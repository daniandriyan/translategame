"""
HuggingFace Translator - Fallback translator menggunakan HuggingFace API
Gratis dengan free tier 30k tokens/hari
"""

import logging
import requests
from typing import List
from translators.base_translator import BaseTranslator
from config import TRANSLATION_CONFIG

logger = logging.getLogger(__name__)


class HFTranslator(BaseTranslator):
    """
    Translator menggunakan HuggingFace Inference API (Gratis)
    Model translation: Helsinki-NLP/opus-mt-ja-id (Japanese → Indonesian)

    Free tier: 30k tokens/hari
    No API key required untuk basic usage
    """

    def __init__(self, model: str = None):
        super().__init__("HuggingFace (Free API)")

        if model is None:
            model = TRANSLATION_CONFIG["huggingface"]["model"]

        self.model = model
        self.timeout = TRANSLATION_CONFIG["huggingface"]["timeout"]
        self.batch_size = TRANSLATION_CONFIG["huggingface"]["batch_size"]

        # HuggingFace Inference API endpoint
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"

        self.is_initialized = False

    def initialize(self) -> bool:
        """Cek apakah HuggingFace API tersedia"""
        if self.is_initialized:
            return True

        try:
            # Test connection dengan request sederhana
            response = requests.get(
                f"https://api-inference.huggingface.co/models/{self.model}",
                timeout=10
            )

            # Model bisa jadi loading (503) tapi tetap valid
            if response.status_code in [200, 503]:
                self.is_initialized = True
                logger.info(f"HuggingFace initialized with model: {self.model}")
                return True
            else:
                logger.warning(f"HuggingFace status: {response.status_code}")
                # Tetap coba initialize, mungkin perlu waktu untuk load model
                self.is_initialized = True
                return True

        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to HuggingFace API. Check internet connection")
            return False
        except Exception as e:
            logger.error(f"Error initializing HuggingFace: {e}")
            # Tetap return True, mungkin transient error
            self.is_initialized = True
            return True

    def is_available(self) -> bool:
        """Cek apakah HuggingFace tersedia"""
        if not self.is_initialized:
            self.initialize()

        return self.is_initialized

    def translate(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> str:
        """
        Translate text menggunakan HuggingFace API

        Args:
            text: Text yang akan di-translate
            source_lang: Bahasa sumber (auto-detect)
            target_lang: Bahasa target

        Returns:
            Translated text
        """
        if not self.is_available():
            logger.error("HuggingFace translator not available")
            return text

        if not text or text.isspace():
            return text

        try:
            # HuggingFace translation model biasanya langsung translate
            # Tanpa prompt, model sudah trained untuk translation
            response = requests.post(
                self.api_url,
                json={
                    "inputs": text,
                    "parameters": {
                        "src_lang": self._map_source_lang(source_lang),
                        "trg_lang": self._map_target_lang(target_lang),
                    }
                },
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()

                # Parse response format
                if isinstance(result, list) and len(result) > 0:
                    translation = result[0].get("translation_text", "")
                elif isinstance(result, dict):
                    translation = result.get("translation_text", "")
                else:
                    logger.warning(f"Unexpected HF response format: {type(result)}")
                    return text

                if translation and translation.strip():
                    return translation.strip()
                else:
                    logger.warning(f"Empty translation for: {text[:30]}")
                    return text

            elif response.status_code == 503:
                # Model sedang loading
                estimated_time = response.json().get("estimated_time", 30)
                logger.warning(f"Model is loading, estimated time: {estimated_time}s")
                return text

            else:
                logger.error(f"HuggingFace API error: {response.status_code} - {response.text}")
                return text

        except requests.exceptions.Timeout:
            logger.error("HuggingFace request timeout")
            return text
        except Exception as e:
            logger.error(f"HuggingFace translation error: {e}")
            return text

    def translate_batch(self, texts: List[str], source_lang: str = "auto", target_lang: str = "Indonesian") -> List[str]:
        """
        Translate batch teks

        HuggingFace API support batch inputs
        """
        if not texts:
            return []

        if not self.is_available():
            return texts

        results = []

        # Process dalam batch kecil
        batch_size = self.batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            # Filter empty texts
            valid_indices = [j for j, t in enumerate(batch) if t and not t.isspace()]
            valid_texts = [batch[j] for j in valid_indices]

            if not valid_texts:
                results.extend(["" for _ in batch])
                continue

            try:
                response = requests.post(
                    self.api_url,
                    json={
                        "inputs": valid_texts,
                        "parameters": {
                            "src_lang": self._map_source_lang(source_lang),
                            "trg_lang": self._map_target_lang(target_lang),
                        }
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout * 2
                )

                if response.status_code == 200:
                    result = response.json()

                    # Parse batch response
                    translated_map = {}
                    if isinstance(result, list):
                        for item in result:
                            original = item.get("translation_text", "")
                            if original:
                                translated_map[original] = original  # Simplified

                    # Build results
                    translated_list = []
                    if isinstance(result, list):
                        for item in result:
                            translated_list.append(item.get("translation_text", ""))

                    # Map back ke posisi asli
                    batch_results = []
                    translated_idx = 0
                    for j, text in enumerate(batch):
                        if j in valid_indices:
                            if translated_idx < len(translated_list):
                                batch_results.append(translated_list[translated_idx])
                                translated_idx += 1
                            else:
                                batch_results.append(text)
                        else:
                            batch_results.append(text)

                    results.extend(batch_results)

                else:
                    # Batch gagal, fallback satu per satu
                    logger.warning(f"Batch translation failed (status {response.status_code}), fallback to single")
                    for text in batch:
                        results.append(self.translate_safe(text, source_lang, target_lang))

            except Exception as e:
                logger.error(f"Batch translation error: {e}")
                for text in batch:
                    results.append(self.translate_safe(text, source_lang, target_lang))

        return results

    def _map_source_lang(self, source_lang: str) -> str:
        """Map source language ke code yang dimengerti model"""
        lang_map = {
            "auto": "ja",  # Default Japanese untuk game
            "japanese": "ja",
            "english": "en",
            "auto": "ja",
        }
        return lang_map.get(source_lang.lower(), "ja")

    def _map_target_lang(self, target_lang: str) -> str:
        """Map target language ke code yang dimengerti model"""
        lang_map = {
            "indonesian": "id",
            "indonesian": "id",
            "bahasa": "id",
        }
        return lang_map.get(target_lang.lower(), "id")
