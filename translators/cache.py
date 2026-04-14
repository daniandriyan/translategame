"""
Cache System - Cache hasil terjemahan untuk menghindari API call berulang
JSON-based cache dengan TTL (Time To Live)
"""

import json
import logging
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict
from config import CACHE_CONFIG

logger = logging.getLogger(__name__)


class TranslationCache:
    """
    Cache system untuk hasil terjemahan

    Features:
    - JSON-based persistent cache
    - TTL (Time To Live) untuk auto-expire
    - Max size limit
    - Auto-save ke disk
    """

    def __init__(
        self,
        cache_file: str = None,
        max_size: int = None,
        ttl: int = None,
        enabled: bool = None
    ):
        # Load config defaults
        if cache_file is None:
            cache_file = CACHE_CONFIG["file"]

        if max_size is None:
            max_size = CACHE_CONFIG["max_size"]

        if ttl is None:
            ttl = CACHE_CONFIG["ttl"]

        if enabled is None:
            enabled = CACHE_CONFIG["enabled"]

        self.cache_file = Path(cache_file)
        self.max_size = max_size
        self.ttl = ttl
        self.enabled = enabled

        # In-memory cache: {hash_key: {"text": ..., "translation": ..., "timestamp": ...}}
        self._cache: Dict[str, dict] = {}

        # Load cache dari disk jika ada
        if self.enabled:
            self._load_cache()

    def _load_cache(self):
        """Load cache dari file JSON"""
        if not self.cache_file.exists():
            logger.info("Cache file tidak ditemukan, mulai dari kosong")
            return

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self._cache = json.load(f)

            logger.info(f"Cache loaded: {len(self._cache)} entries dari {self.cache_file}")

            # Cleanup expired entries
            self._cleanup_expired()

        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self._cache = {}

    def _save_cache(self):
        """Save cache ke file JSON"""
        if not self.enabled:
            return

        try:
            # Ensure directory exists
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)

            logger.debug(f"Cache saved: {len(self._cache)} entries")

        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _generate_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key dari text dan language"""
        key_string = f"{source_lang}:{target_lang}:{text}"
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

    def _cleanup_expired(self):
        """Hapus entry yang sudah expired"""
        if self.ttl <= 0:
            return

        current_time = time.time()
        expired_keys = []

        for key, entry in self._cache.items():
            if current_time - entry.get("timestamp", 0) > self.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            self._save_cache()

    def _enforce_max_size(self):
        """Hapus entry lama jika cache melebihi max_size"""
        if len(self._cache) <= self.max_size:
            return

        # Sort by timestamp (oldest first)
        sorted_entries = sorted(self._cache.items(), key=lambda x: x[1].get("timestamp", 0))

        # Remove oldest entries
        excess = len(self._cache) - self.max_size
        for key, _ in sorted_entries[:excess]:
            del self._cache[key]

        logger.info(f"Cache size limit reached, removed {excess} old entries")
        self._save_cache()

    def get(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> Optional[str]:
        """
        Get cached translation

        Args:
            text: Original text
            source_lang: Source language
            target_lang: Target language

        Returns:
            Cached translation or None jika tidak ada/expired
        """
        if not self.enabled:
            return None

        key = self._generate_key(text, source_lang, target_lang)

        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Cek TTL
        if self.ttl > 0:
            if time.time() - entry.get("timestamp", 0) > self.ttl:
                # Expired, hapus
                del self._cache[key]
                return None

        return entry.get("translation")

    def set(self, text: str, translation: str, source_lang: str = "auto", target_lang: str = "Indonesian"):
        """
        Set cache entry

        Args:
            text: Original text
            translation: Translated text
            source_lang: Source language
            target_lang: Target language
        """
        if not self.enabled:
            return

        key = self._generate_key(text, source_lang, target_lang)

        self._cache[key] = {
            "text": text,
            "translation": translation,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "timestamp": time.time()
        }

        # Enforce max size
        self._enforce_max_size()

    def has(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> bool:
        """Cek apakah ada cache untuk text ini"""
        if not self.enabled:
            return False

        key = self._generate_key(text, source_lang, target_lang)
        return key in self._cache

    def delete(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian") -> bool:
        """Hapus cache entry spesifik"""
        if not self.enabled:
            return False

        key = self._generate_key(text, source_lang, target_lang)

        if key in self._cache:
            del self._cache[key]
            return True

        return False

    def clear(self):
        """Hapus semua cache"""
        self._cache = {}

        if self.cache_file.exists():
            self.cache_file.unlink()

        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """Dapatkan statistik cache"""
        return {
            "enabled": self.enabled,
            "total_entries": len(self._cache),
            "max_size": self.max_size,
            "ttl_days": self.ttl // 86400 if self.ttl > 0 else "unlimited",
            "file_size": self.cache_file.stat().st_size if self.cache_file.exists() else 0,
        }

    def flush(self):
        """Force save cache ke disk"""
        self._save_cache()

    def __contains__(self, item):
        """Support 'in' operator"""
        if isinstance(item, tuple) and len(item) == 3:
            text, source_lang, target_lang = item
            return self.has(text, source_lang, target_lang)
        return False

    def __len__(self):
        return len(self._cache)

    def __repr__(self):
        return f"TranslationCache(entries={len(self._cache)}, enabled={self.enabled})"
