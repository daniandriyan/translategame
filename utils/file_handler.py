"""
File Handler - Utility untuk operasi file
JSON, text, backup, dll
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class FileHandler:
    """Utility untuk handle file operations"""
    
    @staticmethod
    def read_json(file_path: str) -> Optional[Dict[str, Any]]:
        """Baca file JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
        """Tulis data ke file JSON"""
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            logger.info(f"JSON file saved: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}")
            return False
    
    @staticmethod
    def read_text(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """Baca file text"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return None
    
    @staticmethod
    def write_text(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """Tulis content ke file text"""
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"Text file saved: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing text file {file_path}: {e}")
            return False
    
    @staticmethod
    def create_backup(file_path: str) -> Optional[str]:
        """Buat backup file"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.warning(f"File tidak ditemukan untuk backup: {file_path}")
                return None
            
            backup_path = path.with_suffix(path.suffix + '.backup')
            
            # Copy file
            import shutil
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    @staticmethod
    def get_file_size_human(file_path: str) -> str:
        """Dapatkan ukuran file dalam format human-readable"""
        try:
            size_bytes = os.path.getsize(file_path)
            return FileHandler._format_bytes(size_bytes)
        except:
            return "Unknown"
    
    @staticmethod
    def _format_bytes(size_bytes: int) -> str:
        """Format bytes ke human-readable string"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 ** 2:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 ** 3:
            return f"{size_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{size_bytes / (1024 ** 3):.2f} GB"
    
    @staticmethod
    def ensure_directory(dir_path: str) -> bool:
        """Pastikan direktori ada, buat jika belum"""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except:
            return False
    
    @staticmethod
    def list_files(directory: str, extension: str = None) -> list:
        """List semua file dalam direktori"""
        try:
            path = Path(directory)
            
            if not path.exists():
                return []
            
            files = [str(f) for f in path.iterdir() if f.is_file()]
            
            if extension:
                files = [f for f in files if f.endswith(extension)]
            
            return files
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """Hapus file"""
        try:
            path = Path(file_path)
            
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Cek apakah file ada"""
        return os.path.exists(file_path) and os.path.isfile(file_path)
