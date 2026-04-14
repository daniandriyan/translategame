"""
Base Translator - Interface untuk semua translation providers
Abstract class yang harus diimplementasi oleh semua translator
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseTranslator(ABC):
    """
    Abstract base class untuk translation providers
    
    Semua translator (G4F, Ollama, HuggingFace) harus implementasi class ini
    """
    
    def __init__(self, name: str):
        self.name = name
        self.is_initialized = False
        self.error_count = 0
        self.success_count = 0
    
    @abstractmethod
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> str:
        """
        Translate single text
        
        Args:
            text: Text yang akan di-translate
            source_lang: Bahasa sumber (auto untuk auto-detect)
            target_lang: Bahasa target
            
        Returns:
            Text yang sudah di-translate
        """
        pass
    
    @abstractmethod
    def translate_batch(self, texts: List[str], source_lang: str = "auto", target_lang: str = "Indonesian") -> List[str]:
        """
        Translate batch teks sekaligus (lebih efisien)
        
        Args:
            texts: List of texts yang akan di-translate
            source_lang: Bahasa sumber
            target_lang: Bahasa target
            
        Returns:
            List of translated texts
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize translator (load model, connect to API, dll)
        
        Returns:
            True jika berhasil
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Cek apakah translator tersedia dan bisa digunakan
        
        Returns:
            True jika translator ready
        """
        pass
    
    def translate_safe(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> str:
        """
        Translate dengan error handling
        
        Returns original text jika gagal
        """
        try:
            if not text or text.isspace():
                return text
            
            result = self.translate(text, source_lang, target_lang)
            
            if result and not result.isspace():
                self.success_count += 1
                return result
            else:
                # Translation gagal/empty
                self.error_count += 1
                logger.warning(f"Empty translation result for: {text[:30]}")
                return text
        
        except Exception as e:
            self.error_count += 1
            logger.error(f"Translation error ({self.name}): {e}")
            return text  # Fallback ke original
    
    def get_stats(self) -> dict:
        """Dapatkan statistik translation"""
        total = self.success_count + self.error_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        return {
            'provider': self.name,
            'success': self.success_count,
            'errors': self.error_count,
            'total': total,
            'success_rate': f"{success_rate:.1f}%",
            'is_available': self.is_available(),
        }
    
    def reset_stats(self):
        """Reset statistik"""
        self.success_count = 0
        self.error_count = 0
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, available={self.is_available()})"
