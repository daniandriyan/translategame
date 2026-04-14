"""
Patch Builder - Generate patch files (XDelta, BPS, etc)
Create diff patches antara ROM asli dan ROM terjemahan
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PatchBuilder:
    """
    Generate patch files untuk distribute terjemahan
    
    Formats:
    - XDelta (.xdelta) - Paling umum, support ROM size changes
    - BPS (.bps) - Modern, lebih reliable
    - IPS (.ips) - Simple, untuk patch kecil
    - Custom JSON - Untuk debugging
    """
    
    def __init__(self):
        self.patch_format = "xdelta"
    
    def create_xdelta_patch(
        self,
        original_rom: str,
        modified_rom: str,
        output_path: str
    ) -> bool:
        """
        Buat XDelta patch
        
        Args:
            original_rom: Path ke ROM asli
            modified_rom: Path ke ROM yang sudah dimodifikasi
            output_path: Path output patch file
            
        Returns:
            True jika berhasil
        """
        logger.info(f"Creating XDelta patch: {output_path}")
        
        try:
            # Coba pakai library xdelta-python jika ada
            import xdelta3
            
            with open(original_rom, 'rb') as f:
                original_data = f.read()
            
            with open(modified_rom, 'rb') as f:
                modified_data = f.read()
            
            # Create patch
            patch_data = xdelta3.encode(original_data, modified_data)
            
            # Write patch file
            with open(output_path, 'wb') as f:
                f.write(patch_data)
            
            logger.info(f"XDelta patch created: {output_path}")
            return True
            
        except ImportError:
            logger.warning("xdelta3 not installed, using manual patch creation")
            return self._create_manual_patch(original_rom, modified_rom, output_path)
        except Exception as e:
            logger.error(f"Error creating XDelta patch: {e}")
            return False
    
    def _create_manual_patch(
        self,
        original_rom: str,
        modified_rom: str,
        output_path: str
    ) -> bool:
        """
        Buat patch manual (fallback jika xdelta3 tidak ada)
        Format: custom binary diff
        """
        logger.info("Creating manual patch...")
        
        try:
            with open(original_rom, 'rb') as f:
                original = f.read()
            
            with open(modified_rom, 'rb') as f:
                modified = f.read()
            
            # Find differences
            patch_data = self._compute_diff(original, modified)
            
            # Write patch
            with open(output_path, 'wb') as f:
                f.write(patch_data)
            
            logger.info(f"Manual patch created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating manual patch: {e}")
            return False
    
    def _compute_diff(self, original: bytes, modified: bytes) -> bytes:
        """
        Compute binary diff
        
        Format:
        [MAGIC: 4 bytes] [VERSION: 1 byte] [CHUNKS...]
        
        Each chunk:
        [OFFSET: 4 bytes] [LENGTH: 2 bytes] [DATA: LENGTH bytes]
        """
        import struct
        
        # Magic bytes "PAT1" (Patch version 1)
        patch = b'PAT1'
        patch += b'\x01'  # Version
        
        # Find changes
        min_len = min(len(original), len(modified))
        
        # Scan untuk changes
        chunks = []
        current_offset = None
        current_data = bytearray()
        
        for i in range(min_len):
            if original[i] != modified[i]:
                if current_offset is None:
                    current_offset = i
                current_data.append(modified[i])
            else:
                if current_offset is not None:
                    chunks.append((current_offset, bytes(current_data)))
                    current_offset = None
                    current_data = bytearray()
        
        # Handle trailing changes
        if current_offset is not None:
            chunks.append((current_offset, bytes(current_data)))
        
        # Handle jika modified lebih panjang
        if len(modified) > min_len:
            chunks.append((min_len, modified[min_len:]))
        
        # Write chunks
        for offset, data in chunks:
            patch += struct.pack('<I', offset)  # 4-byte offset (little-endian)
            patch += struct.pack('<H', len(data))  # 2-byte length
            patch += data
        
        return patch
    
    def create_ips_patch(
        self,
        original_rom: str,
        modified_rom: str,
        output_path: str
    ) -> bool:
        """
        Buat IPS patch (simple format)
        
        IPS Format:
        [PATCH] [Records...] [EOF]
        
        Record:
        [Offset: 3 bytes] [Length: 2 bytes] [Data...]
        """
        logger.info(f"Creating IPS patch: {output_path}")
        
        try:
            with open(original_rom, 'rb') as f:
                original = f.read()
            
            with open(modified_rom, 'rb') as f:
                modified = f.read()
            
            patch = b'PATCH'
            
            min_len = min(len(original), len(modified))
            
            # Find changes
            i = 0
            while i < min_len:
                if original[i] != modified[i]:
                    # Start of change
                    offset = i
                    
                    # Find end of change
                    while i < min_len and original[i] != modified[i]:
                        i += 1
                    
                    # Write record
                    length = i - offset
                    data = modified[offset:offset + length]
                    
                    # Offset (3 bytes, big-endian)
                    patch += offset.to_bytes(3, byteorder='big')
                    # Length (2 bytes, big-endian)
                    patch += length.to_bytes(2, byteorder='big')
                    # Data
                    patch += data
                else:
                    i += 1
            
            # Handle appended data
            if len(modified) > len(original):
                offset = len(original)
                data = modified[offset:]
                
                patch += offset.to_bytes(3, byteorder='big')
                patch += (0).to_bytes(2, byteorder='big')  # Length 0 = RLE append
                patch += len(data).to_bytes(2, byteorder='big')
                patch += data
            
            # EOF marker
            patch += b'EOF'
            
            with open(output_path, 'wb') as f:
                f.write(patch)
            
            logger.info(f"IPS patch created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating IPS patch: {e}")
            return False
    
    def apply_patch(
        self,
        original_rom: str,
        patch_file: str,
        output_rom: str
    ) -> bool:
        """
        Apply patch ke ROM
        
        Args:
            original_rom: Path ke ROM asli
            patch_file: Path ke patch file
            output_rom: Path output ROM yang sudah di-patch
            
        Returns:
            True jika berhasil
        """
        logger.info(f"Applying patch: {patch_file}")
        
        # Detect patch format dari ekstensi
        patch_ext = Path(patch_file).suffix.lower()
        
        if patch_ext == '.xdelta':
            return self._apply_xdelta_patch(original_rom, patch_file, output_rom)
        elif patch_ext == '.ips':
            return self._apply_ips_patch(original_rom, patch_file, output_rom)
        else:
            logger.error(f"Unsupported patch format: {patch_ext}")
            return False
    
    def _apply_xdelta_patch(
        self,
        original_rom: str,
        patch_file: str,
        output_rom: str
    ) -> bool:
        """Apply XDelta patch"""
        try:
            import xdelta3
            
            with open(original_rom, 'rb') as f:
                original_data = f.read()
            
            with open(patch_file, 'rb') as f:
                patch_data = f.read()
            
            # Decode patch
            modified_data = xdelta3.decode(original_data, patch_data)
            
            with open(output_rom, 'wb') as f:
                f.write(modified_data)
            
            logger.info(f"XDelta patch applied: {output_rom}")
            return True
            
        except ImportError:
            logger.error("xdelta3 not installed")
            return False
        except Exception as e:
            logger.error(f"Error applying XDelta patch: {e}")
            return False
    
    def _apply_ips_patch(
        self,
        original_rom: str,
        patch_file: str,
        output_rom: str
    ) -> bool:
        """Apply IPS patch"""
        try:
            with open(original_rom, 'rb') as f:
                rom_data = bytearray(f.read())
            
            with open(patch_file, 'rb') as f:
                patch_data = f.read()
            
            # Verify IPS header
            if patch_data[:5] != b'PATCH':
                logger.error("Invalid IPS patch")
                return False
            
            # Verify EOF marker
            if patch_data[-3:] != b'EOF':
                logger.error("Invalid IPS patch (missing EOF)")
                return False
            
            # Parse records
            offset = 5  # Skip PATCH header
            
            while offset < len(patch_data) - 3:
                # Read offset (3 bytes)
                rec_offset = int.from_bytes(
                    patch_data[offset:offset+3],
                    byteorder='big'
                )
                offset += 3
                
                # Read length (2 bytes)
                length = int.from_bytes(
                    patch_data[offset:offset+2],
                    byteorder='big'
                )
                offset += 2
                
                if length == 0:
                    # RLE record (skip untuk simplicity)
                    rle_length = int.from_bytes(
                        patch_data[offset:offset+2],
                        byteorder='big'
                    )
                    offset += 2
                    # Skip RLE data
                    offset += 1
                    continue
                
                # Read data
                data = patch_data[offset:offset+length]
                offset += length
                
                # Apply to ROM
                rom_data[rec_offset:rec_offset+length] = data
            
            # Write output
            with open(output_rom, 'wb') as f:
                f.write(rom_data)
            
            logger.info(f"IPS patch applied: {output_rom}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying IPS patch: {e}")
            return False
    
    def create_json_patch(
        self,
        texts: list,
        output_path: str
    ) -> bool:
        """
        Buat patch dalam format JSON (untuk debugging)
        
        Args:
            texts: List of TextEntry objects
            output_path: Path output JSON file
        """
        import json
        
        logger.info(f"Creating JSON patch: {output_path}")
        
        try:
            patch_data = {
                'version': '1.0',
                'type': 'translation_patch',
                'texts': []
            }
            
            for entry in texts:
                if entry.is_translated:
                    patch_data['texts'].append({
                        'original': entry.original_text,
                        'translated': entry.translated_text,
                        'offset': entry.offset,
                    })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(patch_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON patch created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating JSON patch: {e}")
            return False
