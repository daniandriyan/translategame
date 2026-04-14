"""
OpenRouter Translator - ChatGPT & LLM gratis via OpenRouter
Support model gratis: openrouter/free, google/gemma-7b-it:free, dll
"""

import logging
import requests
from typing import List, Optional
from translators.base_translator import BaseTranslator
from config import TRANSLATION_CONFIG

logger = logging.getLogger(__name__)


class OpenRouterTranslator(BaseTranslator):
    """
    Translator menggunakan OpenRouter API
    Support model gratis tanpa API key berbayar
    
    Models gratis tersedia:
    - openrouter/free
    - google/gemma-7b-it:free
    - mistralai/mistral-7b-instruct:free
    - meta-llama/llama-3-8b-instruct:free
    - NousResearch/nous-capybara-7b:free
    
    Daftar: https://openrouter.ai (gratis, dapat $1 credit)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        super().__init__("OpenRouter (Free Models)")
        
        if api_key is None:
            api_key = TRANSLATION_CONFIG.get("openrouter", {}).get("api_key", "")
        
        if model is None:
            model = TRANSLATION_CONFIG.get("openrouter", {}).get(
                "model", "openrouter/free"
            )
        
        self.api_key = api_key
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.timeout = TRANSLATION_CONFIG.get("openrouter", {}).get("timeout", 30)
        self.max_retries = TRANSLATION_CONFIG.get("openrouter", {}).get("max_retries", 3)
        
        self.is_initialized = False

    def initialize(self) -> bool:
        """Initialize OpenRouter connection"""
        if self.is_initialized:
            return True
        
        if not self.api_key:
            logger.warning(
                "OpenRouter API key tidak diset. "
                "Daftar gratis di https://openrouter.ai"
            )
            return False
        
        try:
            # Test connection
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.is_initialized = True
                logger.info(f"OpenRouter initialized with model: {self.model}")
                return True
            else:
                logger.error(f"OpenRouter auth failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing OpenRouter: {e}")
            return False

    def is_available(self) -> bool:
        """Cek apakah OpenRouter tersedia"""
        if not self.is_initialized:
            self.initialize()
        return self.is_initialized and bool(self.api_key)

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> str:
        """
        Translate text menggunakan OpenRouter
        
        Args:
            text: Text yang akan di-translate
            source_lang: Bahasa sumber
            target_lang: Bahasa target
            
        Returns:
            Translated text
        """
        if not self.is_available():
            logger.error("OpenRouter translator not available")
            return text
        
        if not text or text.isspace():
            return text
        
        # Build prompt
        if source_lang == "auto":
            system_prompt = f"You are a professional translator. Translate the following text to {target_lang}. Only return the translated text, nothing else."
        else:
            system_prompt = f"You are a professional translator. Translate the following {source_lang} text to {target_lang}. Only return the translated text, nothing else."
        
        # Build request payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3,  # Low temperature for consistency
            "max_tokens": 1000,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/daniandriyan/translategame",
            "X-Title": "Emulator Game Translator",
        }
        
        # Translate dengan retry
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response
                    if "choices" in data and len(data["choices"]) > 0:
                        translated = data["choices"][0]["message"]["content"].strip()
                        
                        if translated:
                            return translated
                        else:
                            logger.warning(f"Empty translation for: {text[:30]}")
                            return text
                    else:
                        logger.warning(f"Unexpected response format: {data}")
                        return text
                        
                elif response.status_code == 429:
                    # Rate limit
                    logger.warning(f"Rate limited, retrying... (attempt {attempt + 1})")
                    continue
                    
                else:
                    logger.error(f"OpenRouter API error {response.status_code}: {response.text}")
                    return text
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout, retrying... (attempt {attempt + 1})")
                continue
            except Exception as e:
                logger.error(f"Translation error: {e}")
                return text
        
        logger.error(f"Translation failed after {self.max_retries} retries")
        return text

    def translate_batch(self, texts: List[str], source_lang: str = "auto", target_lang: str = "Indonesian") -> List[str]:
        """
        Translate batch teks
        
        Strategy: Join teks dengan delimiter, translate sekali, split lagi
        """
        if not texts:
            return []
        
        if not self.is_available():
            return texts
        
        # Filter empty texts
        valid_texts = [(i, t) for i, t in enumerate(texts) if t and not t.isspace()]
        
        if not valid_texts:
            return texts
        
        # Build batch prompt
        batch_text = "\n---ITEM---\n".join([t for _, t in valid_texts])
        
        system_prompt = f"""You are a professional translator. Translate the following texts to {target_lang}.
Rules:
1. Return translations in the same order, separated by "---ITEM---"
2. Only return the translated texts, nothing else
3. Keep the exact same format

Texts to translate:
{batch_text}"""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate these texts to {target_lang}"}
            ],
            "temperature": 0.3,
            "max_tokens": 4000,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/daniandriyan/translategame",
            "X-Title": "Emulator Game Translator",
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout * 3
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    translated_text = data["choices"][0]["message"]["content"].strip()
                    
                    # Split response by delimiter
                    translated_parts = translated_text.split("---ITEM---")
                    
                    # Build results list
                    results = list(texts)  # Start with originals
                    
                    for idx, (orig_idx, orig_text) in enumerate(valid_texts):
                        if idx < len(translated_parts):
                            results[orig_idx] = translated_parts[idx].strip()
                        else:
                            # Fallback ke single translate
                            results[orig_idx] = self.translate_safe(orig_text, source_lang, target_lang)
                    
                    return results
                else:
                    logger.warning("Unexpected batch response format")
                    return [self.translate_safe(t, source_lang, target_lang) for t in texts]
            else:
                logger.error(f"Batch translation error: {response.status_code}")
                return [self.translate_safe(t, source_lang, target_lang) for t in texts]
                
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            return [self.translate_safe(t, source_lang, target_lang) for t in texts]
