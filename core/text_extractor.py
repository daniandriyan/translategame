"""
Text Extractor - Extract readable text from ROM files
Support: Shift-JIS, UTF-8, EUC-JP encodings
Auto-detect text patterns in ROM binary
"""

import logging
from typing import List, Dict, Tuple
from config import ROM_CONFIG

logger = logging.getLogger(__name__)


class TextEntry:
    """Container untuk satu entry teks"""
    
    def __init__(self, text: str, offset: int = 0):
        self.original_text = text
        self.translated_text = ""
        self.offset = offset  # Offset dalam ROM
        self.is_translated = False
        self.needs_review = False
    
    def __str__(self):
        status = "✓" if self.is_translated else "○"
        return f"[{status}] {self.original_text[:50]}"


class TextExtractor:
    """
    Ekstrak teks dari ROM binary
    
    Strategy:
    1. Scan ROM untuk text patterns (printable strings)
    2. Filter berdasarkan min/max length
    3. Detect encoding (Shift-JIS untuk JP games)
    4. Extract text dengan offset untuk inject balik
    """
    
    def __init__(self):
        self.min_length = ROM_CONFIG["min_text_length"]
        self.max_length = ROM_CONFIG["max_text_length"]
        self.extracted_texts: List[TextEntry] = []
    
    def extract_from_rom(self, rom_data: bytes, emulator_type: str = "3ds") -> List[TextEntry]:
        """
        Ekstrak semua teks dari ROM data
        
        Args:
            rom_data: Binary data dari ROM
            emulator_type: Tipe emulator (3ds, nds, gba, psp)
            
        Returns:
            List of TextEntry objects
        """
        logger.info(f"Extracting text from ROM (emulator: {emulator_type})")
        
        self.extracted_texts = []
        
        if emulator_type == "3ds":
            self._extract_3ds_text(rom_data)
        elif emulator_type == "nds":
            self._extract_nds_text(rom_data)
        elif emulator_type == "gba":
            self._extract_gba_text(rom_data)
        elif emulator_type == "psp":
            self._extract_psp_text(rom_data)
        else:
            # Fallback: generic string extraction
            self._extract_generic_text(rom_data)
        
        logger.info(f"Extracted {len(self.extracted_texts)} text entries")
        return self.extracted_texts
    
    def _extract_3ds_text(self, rom_data: bytes):
        """Extract text dari 3DS ROM"""
        # 3DS games biasanya pakai UTF-8 atau Shift-JIS
        # Text bisa ada di berbagai tempat (ExeFS, RomFS)
        
        # Strategy 1: Extract printable ASCII strings
        ascii_strings = self._extract_ascii_strings(rom_data)
        
        # Strategy 2: Extract Shift-JIS strings
        sjis_strings = self._extract_encoded_strings(rom_data, 'shift-jis')
        
        # Strategy 3: Extract UTF-8 strings
        utf8_strings = self._extract_encoded_strings(rom_data, 'utf-8')
        
        # Combine dan deduplicate
        all_strings = ascii_strings + sjis_strings + utf8_strings
        self._add_unique_texts(all_strings)
    
    def _extract_nds_text(self, rom_data: bytes):
        """Extract text dari NDS ROM"""
        # NDS games biasanya pakai Shift-JIS
        # Text sering ada di ARM9 overlay atau file system
        
        # Extract Shift-JIS strings
        sjis_strings = self._extract_encoded_strings(rom_data, 'shift-jis')
        
        # Extract ASCII strings
        ascii_strings = self._extract_ascii_strings(rom_data)
        
        all_strings = sjis_strings + ascii_strings
        self._add_unique_texts(all_strings)
    
    def _extract_gba_text(self, rom_data: bytes):
        """Extract text dari GBA ROM"""
        # GBA games biasanya pakai Shift-JIS atau custom encoding
        # Text sering ada di fixed locations
        
        # Extract Shift-JIS
        sjis_strings = self._extract_encoded_strings(rom_data, 'shift-jis')
        
        # Extract ASCII
        ascii_strings = self._extract_ascii_strings(rom_data)
        
        all_strings = sjis_strings + ascii_strings
        self._add_unique_texts(all_strings)
    
    def _extract_psp_text(self, rom_data: bytes):
        """Extract text dari PSP ISO"""
        # PSP games biasanya UTF-8 atau Shift-JIS
        # Text ada dalam module files
        
        utf8_strings = self._extract_encoded_strings(rom_data, 'utf-8')
        sjis_strings = self._extract_encoded_strings(rom_data, 'shift-jis')
        
        all_strings = utf8_strings + sjis_strings
        self._add_unique_texts(all_strings)
    
    def _extract_generic_text(self, rom_data: bytes):
        """Fallback: extract semua printable strings"""
        ascii_strings = self._extract_ascii_strings(rom_data)
        self._add_unique_texts(ascii_strings)
    
    def _extract_ascii_strings(self, data: bytes) -> List[Tuple[str, int]]:
        """
        Extract printable ASCII strings dari binary data
        
        Returns:
            List of (string, offset) tuples
        """
        strings = []
        current_string = []
        current_offset = 0
        
        for i, byte in enumerate(data):
            # Printable ASCII: 0x20-0x7E (space tilde)
            if 0x20 <= byte <= 0x7E:
                if not current_string:
                    current_offset = i
                current_string.append(byte)
            else:
                if len(current_string) >= self.min_length:
                    try:
                        text = bytes(current_string).decode('ascii')
                        if len(text) <= self.max_length:
                            strings.append((text, current_offset))
                    except:
                        pass
                current_string = []
        
        # Handle string di akhir file
        if len(current_string) >= self.min_length:
            try:
                text = bytes(current_string).decode('ascii')
                if len(text) <= self.max_length:
                    strings.append((text, current_offset))
            except:
                pass
        
        return strings
    
    def _extract_encoded_strings(self, data: bytes, encoding: str = 'shift-jis') -> List[Tuple[str, int]]:
        """
        Extract strings dengan encoding tertentu dari binary data
        
        Args:
            data: Binary ROM data
            encoding: Encoding (shift-jis, utf-8, euc-jp)
            
        Returns:
            List of (string, offset) tuples
        """
        strings = []
        
        # Scan dengan sliding window
        # Coba decode dari setiap posisi
        step = 1
        max_attempts = min(len(data) * 0.1, 1000000)  # Limit untuk performa
        
        for i in range(0, min(len(data) - 2, int(max_attempts)), step):
            # Coba decode string dari posisi ini
            for length in range(self.min_length, self.max_length + 1):
                if i + length > len(data):
                    break
                
                try:
                    chunk = data[i:i+length]
                    text = chunk.decode(encoding)
                    
                    # Validasi: harus ada karakter yang meaningful
                    if self._is_valid_text(text):
                        # Cek jika ini string terpanjang dari posisi ini
                        next_length = length + 1
                        if i + next_length <= len(data):
                            try:
                                next_chunk = data[i:i+next_length]
                                next_text = next_chunk.decode(encoding)
                                if self._is_valid_text(next_text):
                                    continue  # Ada string yang lebih panjang
                            except:
                                pass
                        
                        strings.append((text, i))
                except:
                    continue
        
        return strings
    
    def _is_valid_text(self, text: str) -> bool:
        """Cek apakah text adalah string yang valid (bukan random bytes)"""
        if not text or len(text) < self.min_length:
            return False
        
        # Harus ada minimal 1 huruf/karakter yang meaningful
        letter_count = sum(1 for c in text if c.isalnum() or ord(c) > 127)
        
        # Minimal 30% harus huruf/karakter meaningful
        return (letter_count / len(text)) >= 0.3
    
    def _add_unique_texts(self, texts_with_offsets: List[Tuple[str, int]]):
        """Tambahkan teks unik ke extracted_texts"""
        seen_texts = set()
        
        for text, offset in texts_with_offsets:
            # Skip duplicates
            if text in seen_texts:
                continue
            
            # Skip text yang terlalu pendek atau terlalu panjang
            if len(text) < self.min_length or len(text) > self.max_length:
                continue
            
            # Skip text yang cuma angka/simbol
            if not any(c.isalpha() or ord(c) > 127 for c in text):
                continue
            
            seen_texts.add(text)
            entry = TextEntry(text=text, offset=offset)
            self.extracted_texts.append(entry)
    
    def filter_texts(self, min_length: int = None):
        """Filter teks berdasarkan panjang"""
        if min_length is None:
            min_length = self.min_length
        
        self.extracted_texts = [
            entry for entry in self.extracted_texts
            if len(entry.original_text) >= min_length
        ]
    
    def get_texts_by_length(self, min_len: int, max_len: int) -> List[TextEntry]:
        """Get teks dalam range panjang tertentu"""
        return [
            entry for entry in self.extracted_texts
            if min_len <= len(entry.original_text) <= max_len
        ]
    
    def export_to_dict(self) -> List[Dict]:
        """Export extracted texts ke list of dict"""
        return [
            {
                'original': entry.original_text,
                'translated': entry.translated_text,
                'offset': entry.offset,
                'is_translated': entry.is_translated,
                'needs_review': entry.needs_review,
            }
            for entry in self.extracted_texts
        ]
    
    def import_from_dict(self, data: List[Dict]):
        """Import extracted texts dari list of dict"""
        self.extracted_texts = []
        for item in data:
            entry = TextEntry(
                text=item.get('original', ''),
                offset=item.get('offset', 0)
            )
            entry.translated_text = item.get('translated', '')
            entry.is_translated = item.get('is_translated', False)
            entry.needs_review = item.get('needs_review', False)
            self.extracted_texts.append(entry)
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik teks yang diekstrak"""
        total = len(self.extracted_texts)
        translated = sum(1 for e in self.extracted_texts if e.is_translated)
        needs_review = sum(1 for e in self.extracted_texts if e.needs_review)
        
        avg_length = 0
        if total > 0:
            avg_length = sum(len(e.original_text) for e in self.extracted_texts) / total
        
        return {
            'total_texts': total,
            'translated': translated,
            'needs_review': needs_review,
            'not_translated': total - translated,
            'average_length': round(avg_length, 2),
        }
