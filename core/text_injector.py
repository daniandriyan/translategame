"""
Text Injector - Inject translated text back into ROM
Handle text encoding, padding, dan offset management
"""

import logging
from typing import List, Dict
from core.text_extractor import TextEntry
from config import ROM_CONFIG

logger = logging.getLogger(__name__)


class TextInjector:
    """
    Inject teks terjemahan kembali ke ROM binary
    
    Strategy:
    1. Match teks asli dengan offset
    2. Encode teks terjemahan ke encoding yang sesuai
    3. Handle text length differences (padding/truncation)
    4. Write ke ROM dengan offset yang benar
    """
    
    def __init__(self):
        self.injected_count = 0
        self.failed_count = 0
        self.errors: List[str] = []
    
    def inject_to_rom(
        self,
        rom_data: bytearray,
        texts: List[TextEntry],
        emulator_type: str = "3ds",
        encoding: str = None
    ) -> bytearray:
        """
        Inject translated text ke ROM data
        
        Args:
            rom_data: Binary ROM data (mutable)
            texts: List of TextEntry dengan terjemahan
            emulator_type: Tipe emulator
            encoding: Encoding untuk encode text (auto-detect jika None)
            
        Returns:
            Modified ROM data dengan teks terjemahan
        """
        logger.info(f"Injecting {len(texts)} translated texts to ROM")
        
        self.injected_count = 0
        self.failed_count = 0
        self.errors = []
        
        # Auto-detect encoding jika tidak specified
        if encoding is None:
            encoding = self._detect_encoding(emulator_type)
        
        # Inject setiap text
        for entry in texts:
            if not entry.is_translated or not entry.translated_text:
                continue
            
            try:
                self._inject_single_text(rom_data, entry, encoding)
                self.injected_count += 1
            except Exception as e:
                error_msg = f"Failed to inject text at offset {entry.offset}: {e}"
                logger.warning(error_msg)
                self.errors.append(error_msg)
                self.failed_count += 1
        
        logger.info(
            f"Injection complete: {self.injected_count} success, "
            f"{self.failed_count} failed"
        )
        
        return rom_data
    
    def _inject_single_text(
        self,
        rom_data: bytearray,
        entry: TextEntry,
        encoding: str
    ):
        """Inject satu teks ke ROM"""
        offset = entry.offset
        original = entry.original_text
        translated = entry.translated_text
        
        # Encode teks terjemahan
        try:
            encoded_text = translated.encode(encoding)
        except UnicodeEncodeError:
            # Fallback ke UTF-8
            encoded_text = translated.encode('utf-8')
        
        # Cari original text di ROM untuk konfirmasi offset
        try:
            original_encoded = original.encode(encoding)
            found_offset = rom_data.find(original_encoded, offset - 100, offset + 100)
            
            if found_offset != -1:
                offset = found_offset
            else:
                # Gunakan offset asli
                pass
        except:
            pass
        
        # Handle length differences
        original_length = len(original.encode(encoding, errors='ignore'))
        new_length = len(encoded_text)
        
        if new_length <= original_length:
            # Text lebih pendek atau sama: pad dengan null bytes
            rom_data[offset:offset + new_length] = encoded_text
            
            # Padding dengan null bytes
            padding_length = original_length - new_length
            if padding_length > 0:
                rom_data[offset + new_length:offset + original_length] = b'\x00' * padding_length
        else:
            # Text lebih panjang: truncate atau expand
            # Strategy 1: Truncate (aman tapi bisa hilangin teks)
            # rom_data[offset:offset + original_length] = encoded_text[:original_length]
            
            # Strategy 2: Expand (butuh ROM yang punya space)
            # Ini lebih kompleks, perlu geser data setelahnya
            logger.warning(
                f"Translated text longer than original: "
                f"{len(translated)} > {len(original)} at offset {offset}"
            )
            
            # Untuk sekarang, truncate dulu
            rom_data[offset:offset + original_length] = encoded_text[:original_length]
    
    def _detect_encoding(self, emulator_type: str) -> str:
        """Auto-detect encoding berdasarkan emulator type"""
        encodings = ROM_CONFIG["encodings"]
        
        if emulator_type in encodings:
            return encodings[emulator_type][0]
        
        # Default fallback
        return 'utf-8'
    
    def inject_with_pointers(
        self,
        rom_data: bytearray,
        texts: List[TextEntry],
        pointer_table_offset: int,
        encoding: str = 'shift-jis'
    ) -> bytearray:
        """
        Inject text dengan pointer table (advanced)
        
        Beberapa games pakai pointer table untuk reference text locations.
        Ini handle cases tersebut.
        
        Args:
            rom_data: ROM binary
            texts: List of translated texts
            pointer_table_offset: Offset ke pointer table dalam ROM
            encoding: Text encoding
        """
        logger.info(f"Injecting with pointer table at 0x{pointer_table_offset:X}")
        
        # Baca pointer table
        pointers = self._read_pointer_table(rom_data, pointer_table_offset, len(texts))
        
        # Inject setiap text di location yang ditunjuk pointer
        for i, (entry, pointer) in enumerate(zip(texts, pointers)):
            if not entry.is_translated:
                continue
            
            try:
                rom_data = self._inject_at_pointer(
                    rom_data, entry, pointer, encoding
                )
                self.injected_count += 1
            except Exception as e:
                logger.warning(f"Failed at pointer {i}: {e}")
                self.failed_count += 1
        
        return rom_data
    
    def _read_pointer_table(
        self,
        rom_data: bytearray,
        offset: int,
        count: int
    ) -> List[int]:
        """Baca pointer table dari ROM"""
        pointers = []
        
        for i in range(count):
            ptr_offset = offset + (i * 4)  # 4 bytes per pointer (32-bit)
            
            if ptr_offset + 4 > len(rom_data):
                break
            
            # Read 32-bit pointer (little-endian)
            pointer = int.from_bytes(
                rom_data[ptr_offset:ptr_offset + 4],
                byteorder='little'
            )
            
            pointers.append(pointer)
        
        return pointers
    
    def _inject_at_pointer(
        self,
        rom_data: bytearray,
        entry: TextEntry,
        pointer: int,
        encoding: str
    ) -> bytearray:
        """Inject text di location yang ditunjuk pointer"""
        # Cari text dari pointer
        # Pointer bisa absolute atau relative
        
        # Simplified: anggap pointer adalah absolute offset
        if pointer >= len(rom_data):
            raise ValueError(f"Pointer out of bounds: 0x{pointer:X}")
        
        # Cari null terminator atau fixed length
        text_end = rom_data.find(b'\x00', pointer)
        
        if text_end == -1:
            # No null terminator, gunakan original length
            text_end = pointer + len(entry.original_text)
        
        original_length = text_end - pointer
        
        # Encode translated text
        encoded_text = entry.translated_text.encode(encoding, errors='ignore')
        
        # Inject dengan padding
        if len(encoded_text) <= original_length:
            rom_data[pointer:pointer + len(encoded_text)] = encoded_text
            # Null padding
            padding = original_length - len(encoded_text)
            rom_data[pointer + len(encoded_text):pointer + original_length] = b'\x00' * padding
        else:
            # Truncate jika terlalu panjang
            rom_data[pointer:pointer + original_length] = encoded_text[:original_length]
        
        return rom_data
    
    def create_backup(self, rom_path: str) -> str:
        """Buat backup ROM sebelum inject"""
        import shutil
        from pathlib import Path
        
        path = Path(rom_path)
        backup_path = path.with_suffix(path.suffix + '.backup')
        
        shutil.copy2(rom_path, backup_path)
        logger.info(f"Backup created: {backup_path}")
        
        return str(backup_path)
    
    def save_modified_rom(self, rom_data: bytearray, output_path: str):
        """Save modified ROM ke file"""
        with open(output_path, 'wb') as f:
            f.write(rom_data)
        
        logger.info(f"Modified ROM saved to: {output_path}")
    
    def get_stats(self) -> dict:
        """Dapatkan statistik injection"""
        return {
            'injected': self.injected_count,
            'failed': self.failed_count,
            'errors': self.errors,
        }
