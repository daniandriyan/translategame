"""
Ollama Translator - Local LLM, 100% offline
Menggunakan Ollama untuk run LLM lokal (Llama3, Mistral, dll)
"""

import logging
import requests
from typing import List
from translators.base_translator import BaseTranslator
from config import TRANSLATION_CONFIG

logger = logging.getLogger(__name__)


class OllamaTranslator(BaseTranslator):
    """
    Translator menggunakan Ollama (Local LLM)
    100% offline, no internet required
    
    Install Ollama: https://ollama.ai
    Pull model: ollama pull llama3.2:1b
    """
    
    def __init__(self, model: str = None, host: str = None):
        super().__init__("Ollama (Local LLM)")
        
        if model is None:
            model = TRANSLATION_CONFIG["ollama"]["model"]
        
        if host is None:
            host = TRANSLATION_CONFIG["ollama"]["host"]
        
        self.model = model
        self.host = host
        self.timeout = TRANSLATION_CONFIG["ollama"]["timeout"]
        self.batch_size = TRANSLATION_CONFIG["ollama"]["batch_size"]
        
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Cek apakah Ollama tersedia"""
        if self.is_initialized:
            return True
        
        try:
            # Test connection ke Ollama API
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            
            if response.status_code == 200:
                # Cek apakah model ada
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                if self.model in model_names:
                    self.is_initialized = True
                    logger.info(f"Ollama initialized with model: {self.model}")
                    return True
                else:
                    logger.warning(
                        f"Model {self.model} not found. Available: {model_names}"
                    )
                    # Tetap return True, mungkin user akan pull model nanti
                    self.is_initialized = True
                    return True
            else:
                logger.error(f"Ollama returned status {response.status_code}")
                return False
        
        except requests.exceptions.ConnectionError:
            logger.error(
                "Cannot connect to Ollama. Make sure Ollama is running at "
                f"{self.host}. Download: https://ollama.ai"
            )
            return False
        except Exception as e:
            logger.error(f"Error initializing Ollama: {e}")
            return False
    
    def is_available(self) -> bool:
        """Cek apakah Ollama tersedia"""
        if not self.is_initialized:
            self.initialize()
        
        return self.is_initialized
    
    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> str:
        """Translate text menggunakan Ollama local LLM"""
        if not self.is_available():
            logger.error("Ollama translator not available")
            return text
        
        # Build prompt
        if source_lang == "auto":
            prompt = f"Translate this text to {target_lang}. Only return the translation, nothing else:\n\n{text}"
        else:
            prompt = f"Translate this {source_lang} text to {target_lang}. Only return the translation, nothing else:\n\n{text}"
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Low temp untuk konsistensi
                        "num_predict": 512,
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get("response", "").strip()
                
                if translated:
                    return translated
                else:
                    logger.warning(f"Empty Ollama response for: {text[:30]}")
                    return text
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return text
        
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            return text
        except Exception as e:
            logger.error(f"Ollama translation error: {e}")
            return text
    
    def translate_batch(self, texts: List[str], source_lang: str = "auto", target_lang: str = "Indonesian") -> List[str]:
        """Translate batch teks dengan single request"""
        if not texts:
            return []
        
        if not self.is_available():
            return texts
        
        # Build batch prompt
        prompt = f"Translate the following texts to {target_lang}. Return translations numbered 1 to {len(texts)}:\n\n"
        
        for i, text in enumerate(texts, 1):
            if text and not text.isspace():
                prompt += f"{i}. {text}\n"
            else:
                prompt += f"{i}. \n"
        
        prompt += f"\nReturn only the numbered translations (1 to {len(texts)}), nothing else."
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 2048,
                    }
                },
                timeout=self.timeout * 3
            )
            
            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("response", "")
                
                # Parse response
                return self._parse_batch_response(translated_text, len(texts))
            else:
                logger.error(f"Ollama batch error: {response.status_code}")
                return [self.translate_safe(t, source_lang, target_lang) for t in texts]
        
        except Exception as e:
            logger.error(f"Ollama batch translation error: {e}")
            return [self.translate_safe(t, source_lang, target_lang) for t in texts]
    
    def _parse_batch_response(self, response: str, expected_count: int) -> List[str]:
        """Parse batch response dari Ollama"""
        results = []
        
        try:
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Remove numbering
                if '. ' in line:
                    parts = line.split('. ', 1)
                    if len(parts) == 2 and parts[0].isdigit():
                        results.append(parts[1].strip())
                elif line:
                    results.append(line)
            
            # Pad jika kurang
            while len(results) < expected_count:
                results.append("")
            
            return results[:expected_count]
        
        except Exception as e:
            logger.error(f"Error parsing Ollama batch response: {e}")
            return [""] * expected_count
