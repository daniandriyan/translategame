"""
G4F Translator - ChatGPT gratis tanpa API key
Menggunakan library g4f (gpt4free)
"""

import logging
from typing import List
from translators.base_translator import BaseTranslator
from config import TRANSLATION_CONFIG

logger = logging.getLogger(__name__)


class G4FTranslator(BaseTranslator):
    """
    Translator menggunakan G4F (gpt4free)
    Akses ChatGPT gratis tanpa API key
    
    Install: pip install g4f
    """
    
    def __init__(self, model: str = None):
        super().__init__("G4F (ChatGPT Free)")
        
        if model is None:
            model = TRANSLATION_CONFIG["g4f"]["model"]
        
        self.model = model
        self.max_retries = TRANSLATION_CONFIG["g4f"]["max_retries"]
        self.timeout = TRANSLATION_CONFIG["g4f"]["timeout"]
        self.batch_size = TRANSLATION_CONFIG["g4f"]["batch_size"]
        
        self.g4f = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize G4F library"""
        if self.is_initialized:
            return True
        
        try:
            import g4f
            self.g4f = g4f
            self.is_initialized = True
            logger.info("G4F library initialized successfully")
            return True
        except ImportError:
            logger.error("G4F library not installed. Run: pip install g4f")
            return False
        except Exception as e:
            logger.error(f"Error initializing G4F: {e}")
            return False
    
    def is_available(self) -> bool:
        """Cek apakah G4F tersedia"""
        if not self.is_initialized:
            self.initialize()
        
        return self.g4f is not None
    
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> str:
        """
        Translate text menggunakan G4F ChatGPT
        
        Args:
            text: Text yang akan di-translate
            source_lang: Bahasa sumber
            target_lang: Bahasa target
            
        Returns:
            Translated text
        """
        if not self.is_available():
            logger.error("G4F translator not available")
            return text
        
        # Build prompt
        if source_lang == "auto":
            prompt = f"Translate the following text to {target_lang}. Only return the translated text, nothing else:\n\n{text}"
        else:
            prompt = f"Translate the following {source_lang} text to {target_lang}. Only return the translated text, nothing else:\n\n{text}"
        
        # Translate dengan retry
        for attempt in range(self.max_retries):
            try:
                response = self.g4f.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=self.timeout
                )
                
                if response and hasattr(response, 'choices'):
                    translated = response.choices[0].message.content.strip()
                elif isinstance(response, dict) and 'choices' in response:
                    translated = response['choices'][0]['message']['content'].strip()
                elif isinstance(response, str):
                    translated = response.strip()
                else:
                    # Response format tidak dikenali
                    logger.warning(f"Unexpected G4F response type: {type(response)}")
                    return text
                
                # Validasi hasil
                if translated and len(translated) > 0:
                    return translated
                else:
                    logger.warning(f"Empty translation for: {text[:30]}")
                    return text
            
            except Exception as e:
                logger.warning(f"G4F translation attempt {attempt + 1} failed: {e}")
                
                if attempt == self.max_retries - 1:
                    logger.error(f"G4F translation failed after {self.max_retries} attempts")
                    return text
                
                # Wait sebelum retry (simplified, no sleep untuk non-blocking)
                continue
        
        return text
    
    def translate_batch(self, texts: List[str], source_lang: str = "auto", target_lang: str = "Indonesian") -> List[str]:
        """
        Translate batch teks
        
        Strategy: Join semua teks dengan delimiter, translate sekali, split lagi
        """
        if not texts:
            return []
        
        if not self.is_available():
            return texts
        
        # Batch processing: translate beberapa teks sekaligus
        batch_size = self.batch_size
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Build batch prompt
            prompt = f"Translate the following texts to {target_lang}. Return translations in the same format, numbered 1 to {len(batch)}.\nOnly return the numbered translations, nothing else:\n\n"
            
            for j, text in enumerate(batch, 1):
                if text and not text.isspace():
                    prompt += f"{j}. {text}\n"
                else:
                    prompt += f"{j}. \n"
            
            prompt += "\nTranslations:\n"
            
            try:
                response = self.g4f.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    timeout=self.timeout * 2  # Lebih lama untuk batch
                )
                
                # Parse response
                translated_batch = self._parse_batch_response(response, len(batch))
                results.extend(translated_batch)
            
            except Exception as e:
                logger.error(f"Batch translation failed: {e}")
                # Fallback: translate satu per satu
                for text in batch:
                    results.append(self.translate_safe(text, source_lang, target_lang))
        
        return results
    
    def _parse_batch_response(self, response, expected_count: int) -> List[str]:
        """Parse batch translation response"""
        results = []
        
        try:
            if isinstance(response, str):
                lines = response.strip().split('\n')
                
                for line in lines:
                    # Remove numbering (1. , 2. , dll)
                    if '. ' in line:
                        parts = line.split('. ', 1)
                        if len(parts) == 2:
                            results.append(parts[1].strip())
                    elif line.strip():
                        results.append(line.strip())
            
            # Ensure we have expected count
            while len(results) < expected_count:
                results.append("")
            
            return results[:expected_count]
        
        except Exception as e:
            logger.error(f"Error parsing batch response: {e}")
            return [""] * expected_count
