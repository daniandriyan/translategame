"""
ROM Loader - Load & validate game ROM files
Support: .3ds, .nds, .gba, .iso, .cso
"""

import os
import logging
from pathlib import Path
from config import ROM_CONFIG

logger = logging.getLogger(__name__)


class ROMInfo:
    """Container untuk informasi ROM"""
    
    def __init__(self):
        self.file_path: str = ""
        self.file_size: int = 0
        self.file_name: str = ""
        self.extension: str = ""
        self.emulator_type: str = "unknown"  # 3ds, nds, gba, psp
        self.region: str = "unknown"  # JP, US, EU, etc
        self.game_title: str = "unknown"
        self.is_valid: bool = False
        self.error_message: str = ""
    
    def __str__(self):
        return f"{self.game_title} ({self.region}) [{self.emulator_type}]"


class ROMLoader:
    """Load dan validasi ROM files"""
    
    def __init__(self):
        self.supported_formats = ROM_CONFIG["supported_formats"]
        self.rom_info = ROMInfo()
    
    def load_rom(self, file_path: str) -> ROMInfo:
        """
        Load ROM file dan extract informasi
        
        Args:
            file_path: Path ke file ROM
            
        Returns:
            ROMInfo object dengan informasi ROM
        """
        logger.info(f"Loading ROM: {file_path}")
        
        # Reset ROM info
        self.rom_info = ROMInfo()
        self.rom_info.file_path = file_path
        
        # Validasi file exists
        if not os.path.exists(file_path):
            error_msg = f"File tidak ditemukan: {file_path}"
            logger.error(error_msg)
            self.rom_info.error_message = error_msg
            return self.rom_info
        
        # Validasi ukuran file
        file_size = os.path.getsize(file_path)
        self.rom_info.file_size = file_size
        
        if file_size == 0:
            error_msg = "File ROM kosong"
            logger.error(error_msg)
            self.rom_info.error_message = error_msg
            return self.rom_info
        
        # Extract file info
        path = Path(file_path)
        self.rom_info.file_name = path.name
        self.rom_info.extension = path.suffix.lower()
        
        # Validasi format
        if not self._is_supported_format():
            error_msg = f"Format tidak didukung: {self.rom_info.extension}"
            logger.error(error_msg)
            self.rom_info.error_message = error_msg
            return self.rom_info
        
        # Detect emulator type
        self.rom_info.emulator_type = self._detect_emulator_type()
        
        # Baca header ROM untuk extract info
        try:
            self._read_rom_header()
            self.rom_info.is_valid = True
            logger.info(f"ROM loaded successfully: {self.rom_info}")
        except Exception as e:
            error_msg = f"Error membaca ROM: {str(e)}"
            logger.error(error_msg)
            self.rom_info.error_message = error_msg
        
        return self.rom_info
    
    def _is_supported_format(self) -> bool:
        """Cek apakah format ROM didukung"""
        return self.rom_info.extension in self.supported_formats
    
    def _detect_emulator_type(self) -> str:
        """Detect tipe emulator berdasarkan ekstensi"""
        ext = self.rom_info.extension
        
        if ext in [".3ds", ".cci"]:
            return "3ds"
        elif ext == ".nds":
            return "nds"
        elif ext == ".gba":
            return "gba"
        elif ext in [".iso", ".cso"]:
            return "psp"
        
        return "unknown"
    
    def _read_rom_header(self):
        """
        Baca header ROM untuk extract informasi game
        Implementasi berbeda per tipe emulator
        """
        emulator_type = self.rom_info.emulator_type
        
        if emulator_type == "3ds":
            self._read_3ds_header()
        elif emulator_type == "nds":
            self._read_nds_header()
        elif emulator_type == "gba":
            self._read_gba_header()
        elif emulator_type == "psp":
            self._read_psp_header()
        else:
            self.rom_info.game_title = self.rom_info.file_name
            self.rom_info.region = "unknown"
    
    def _read_3ds_header(self):
        """Baca header Nintendo 3DS ROM"""
        # 3DS NCCH header structure
        # Title offset: 0x200 (offset dalam NCCH partition)
        # Region info: dari Product Code
        
        try:
            with open(self.rom_info.file_path, 'rb') as f:
                # Baca 3DS header (simplified)
                # Magic bytes "NCCH" di offset 0x100
                f.seek(0x100)
                magic = f.read(4)
                
                if magic == b'NCCH':
                    # Baca game title (offset 0x200 dalam partition pertama)
                    # Untuk sekarang, extract dari filename
                    title = self._extract_title_from_filename()
                    self.rom_info.game_title = title
                    
                    # Detect region dari product code
                    region = self._detect_3ds_region()
                    self.rom_info.region = region
                else:
                    # Mungkin format .3ds yang berbeda (legacy)
                    self.rom_info.game_title = self._extract_title_from_filename()
                    self.rom_info.region = "unknown"
        except Exception as e:
            logger.warning(f"Error reading 3DS header: {e}")
            self.rom_info.game_title = self._extract_title_from_filename()
            self.rom_info.region = "unknown"
    
    def _read_nds_header(self):
        """Baca header Nintendo DS ROM"""
        try:
            with open(self.rom_info.file_path, 'rb') as f:
                # NDS header di offset 0
                # Game title: 12 bytes di offset 0
                title_bytes = f.read(12)
                title = title_bytes.decode('ascii', errors='ignore').strip()
                
                if title:
                    self.rom_info.game_title = title
                
                # Region detection dari header
                f.seek(0x0C)  # Game code offset
                game_code = f.read(4).decode('ascii', errors='ignore')
                
                if len(game_code) >= 3:
                    region_char = game_code[2]
                    region_map = {
                        'J': 'JP',
                        'U': 'US',
                        'E': 'EU',
                        'K': 'KR',
                    }
                    self.rom_info.region = region_map.get(region_char, "unknown")
        except Exception as e:
            logger.warning(f"Error reading NDS header: {e}")
            self.rom_info.game_title = self._extract_title_from_filename()
    
    def _read_gba_header(self):
        """Baca header Game Boy Advance ROM"""
        try:
            with open(self.rom_info.file_path, 'rb') as f:
                # GBA game title: 12 bytes di offset 0xA0
                f.seek(0xA0)
                title_bytes = f.read(12)
                title = title_bytes.decode('ascii', errors='ignore').strip()
                
                if title:
                    self.rom_info.game_title = title
                
                # Game code: 4 bytes di offset 0xAC
                f.seek(0xAC)
                game_code = f.read(4).decode('ascii', errors='ignore')
                
                if len(game_code) >= 3:
                    region_char = game_code[2]
                    region_map = {
                        'J': 'JP',
                        'U': 'US',
                        'E': 'EU',
                    }
                    self.rom_info.region = region_map.get(region_char, "unknown")
        except Exception as e:
            logger.warning(f"Error reading GBA header: {e}")
            self.rom_info.game_title = self._extract_title_from_filename()
    
    def _read_psp_header(self):
        """Baca header PSP ISO/CSO"""
        try:
            with open(self.rom_info.file_path, 'rb') as f:
                # PSP ISO: baca PARAM.SFO dari dalam ISO
                # Untuk sekarang, extract dari filename
                self.rom_info.game_title = self._extract_title_from_filename()
                self.rom_info.region = "unknown"
        except Exception as e:
            logger.warning(f"Error reading PSP header: {e}")
            self.rom_info.game_title = self._extract_title_from_filename()
    
    def _extract_title_from_filename(self) -> str:
        """Extract game title dari nama file"""
        filename = self.rom_info.file_name
        
        # Hapus ekstensi
        name = Path(filename).stem
        
        # Hapus tags umum [USA], [JP], (v1.0), dll
        import re
        name = re.sub(r'\[.*?\]', '', name)
        name = re.sub(r'\(.*?\)', '', name)
        name = name.strip()
        
        # Hapus underscores
        name = name.replace('_', ' ')
        
        return name if name else "Unknown Game"
    
    def _detect_3ds_region(self) -> str:
        """Detect region 3DS dari product code"""
        # Simplified region detection
        # Product code format: CTR-XXXX-XXY
        # Y = region (J=JP, U=US, E=EU, dll)
        
        title = self.rom_info.game_title.upper()
        
        if 'JPN' in title or 'JAP' in title:
            return 'JP'
        elif 'USA' in title or 'NTSC' in title:
            return 'US'
        elif 'EUR' in title or 'PAL' in title:
            return 'EU'
        
        return "unknown"
    
    def read_rom_data(self) -> bytes:
        """Baca seluruh isi ROM file"""
        if not self.rom_info.is_valid:
            raise ValueError("ROM belum di-load atau tidak valid")
        
        with open(self.rom_info.file_path, 'rb') as f:
            return f.read()
    
    def get_rom_size(self) -> int:
        """Dapatkan ukuran ROM dalam bytes"""
        return self.rom_info.file_size
