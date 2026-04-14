"""
Translation Queue Manager - Auto-queue dan manage translation tasks
Handle batch translation dengan progress tracking dan fallback otomatis
"""

import logging
import threading
import time
from typing import List, Callable, Optional, Dict
from queue import Queue, Empty
from translators.base_translator import BaseTranslator
from translators.cache import TranslationCache
from config import TRANSLATION_CONFIG, TRANSLATION_LANGUAGE

logger = logging.getLogger(__name__)


class TranslationTask:
    """Container untuk satu translation task"""

    def __init__(self, text: str, source_lang: str = "auto", target_lang: str = "Indonesian"):
        self.text = text
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.result: Optional[str] = None
        self.is_completed = False
        self.is_failed = False
        self.error_message: Optional[str] = None


class QueueManager:
    """
    Manage translation queue dengan fitur:
    - Auto-queue: langsung translate tanpa user interaction
    - Batch processing: translate 50-100 teks per request
    - Progress tracking: realtime progress
    - Fallback otomatis: jika primary provider gagal, switch ke fallback
    - Cancel support: bisa cancel di tengah proses
    - Thread-safe: jalan di background thread
    """

    def __init__(
        self,
        translators: Dict[str, BaseTranslator],
        cache: TranslationCache,
        primary_provider: str = None,
        fallback_providers: List[str] = None
    ):
        self.translators = translators
        self.cache = cache

        # Set providers
        if primary_provider is None:
            primary_provider = TRANSLATION_CONFIG["primary_provider"]

        if fallback_providers is None:
            fallback_providers = TRANSLATION_CONFIG["fallback_providers"]

        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers

        # Queue & state
        self.queue: Queue = Queue()
        self.tasks: List[TranslationTask] = []
        self.is_running = False
        self.is_cancelled = False
        self.is_completed = False

        # Progress tracking
        self.total_count = 0
        self.processed_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.cached_count = 0

        # Callbacks
        self.on_progress: Optional[Callable] = None  # callback(progress: float, processed: int, total: int)
        self.on_complete: Optional[Callable] = None  # callback(results: List[str])
        self.on_error: Optional[Callable] = None  # callback(error: str)

        # Thread
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Target language
        self.target_lang = TRANSLATION_LANGUAGE["target"]
        self.source_lang = TRANSLATION_LANGUAGE["source"]

    def add_texts(self, texts: List[str]):
        """
        Tambahkan teks ke queue

        Args:
            texts: List of texts untuk di-translate
        """
        with self._lock:
            for text in texts:
                task = TranslationTask(
                    text=text,
                    source_lang=self.source_lang,
                    target_lang=self.target_lang
                )
                self.tasks.append(task)
                self.queue.put(task)

            self.total_count = len(self.tasks)
            logger.info(f"Added {len(texts)} texts to queue (total: {self.total_count})")

    def clear_queue(self):
        """Hapus semua teks dari queue"""
        with self._lock:
            self.queue = Queue()
            self.tasks = []
            self.total_count = 0
            self.processed_count = 0
            self.success_count = 0
            self.failed_count = 0
            self.cached_count = 0
            self.is_completed = False
            self.is_cancelled = False

    def start(self):
        """Start translation di background thread"""
        if self.is_running:
            logger.warning("QueueManager sudah running")
            return

        if self.queue.empty():
            logger.warning("Queue kosong, tidak ada yang perlu di-translate")
            return

        self.is_running = True
        self.is_cancelled = False
        self.is_completed = False

        # Start background thread
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()

        logger.info(f"QueueManager started with {self.total_count} texts")

    def cancel(self):
        """Cancel translation yang sedang berjalan"""
        self.is_cancelled = True
        self.is_running = False
        logger.info("Translation cancelled")

    def _process_queue(self):
        """Process semua task di queue (background thread)"""
        try:
            while not self.is_cancelled and not self.queue.empty():
                # Get next task
                try:
                    task = self.queue.get_nowait()
                except Empty:
                    break

                # Check cache dulu
                cached = self.cache.get(task.text, task.source_lang, task.target_lang)

                if cached is not None:
                    # Cache hit!
                    task.result = cached
                    task.is_completed = True
                    self.cached_count += 1
                    self.success_count += 1
                else:
                    # Cache miss, translate
                    result = self._translate_with_fallback(task.text, task.source_lang, task.target_lang)

                    if result:
                        task.result = result
                        task.is_completed = True
                        self.success_count += 1

                        # Save to cache
                        self.cache.set(task.text, result, task.source_lang, task.target_lang)
                    else:
                        task.is_failed = True
                        task.error_message = "All translation providers failed"
                        task.result = task.text  # Fallback ke original
                        self.failed_count += 1

                self.processed_count += 1

                # Callback progress
                if self.on_progress:
                    progress = self.processed_count / self.total_count
                    self.on_progress(progress, self.processed_count, self.total_count)

                # Small delay untuk hindari rate limit
                time.sleep(0.1)

            # Selesai
            self.is_running = False
            self.is_completed = not self.is_cancelled

            # Flush cache
            self.cache.flush()

            # Callback complete
            if self.on_complete and not self.is_cancelled:
                results = [task.result or task.text for task in self.tasks]
                self.on_complete(results)

            status = "cancelled" if self.is_cancelled else "completed"
            logger.info(
                f"Translation {status}: "
                f"{self.success_count} success, "
                f"{self.failed_count} failed, "
                f"{self.cached_count} from cache"
            )

        except Exception as e:
            self.is_running = False
            logger.error(f"QueueManager error: {e}", exc_info=True)

            if self.on_error:
                self.on_error(str(e))

    def _translate_with_fallback(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translate dengan fallback chain
        Coba primary dulu, kalau gagal coba fallback providers
        """
        # Coba primary provider
        primary_translator = self.translators.get(self.primary_provider)

        if primary_translator and primary_translator.is_available():
            try:
                result = primary_translator.translate(text, source_lang, target_lang)
                if result and not result.isspace():
                    return result
            except Exception as e:
                logger.warning(f"Primary translator ({self.primary_provider}) failed: {e}")

        # Fallback ke providers lain
        for provider_name in self.fallback_providers:
            translator = self.translators.get(provider_name)

            if translator and translator.is_available():
                try:
                    logger.info(f"Fallback to {provider_name}")
                    result = translator.translate(text, source_lang, target_lang)

                    if result and not result.isspace():
                        return result
                except Exception as e:
                    logger.warning(f"Fallback {provider_name} failed: {e}")
                    continue

        logger.error("All translation providers failed")
        return None

    def get_progress(self) -> Dict:
        """Dapatkan progress saat ini"""
        progress = 0.0

        if self.total_count > 0:
            progress = self.processed_count / self.total_count

        return {
            "is_running": self.is_running,
            "is_completed": self.is_completed,
            "is_cancelled": self.is_cancelled,
            "total": self.total_count,
            "processed": self.processed_count,
            "success": self.success_count,
            "failed": self.failed_count,
            "cached": self.cached_count,
            "progress": round(progress * 100, 2),  # percentage
        }

    def get_results(self) -> List[str]:
        """Get semua hasil terjemahan"""
        return [task.result or task.text for task in self.tasks]

    def get_results_with_original(self) -> List[Dict]:
        """Get hasil beserta teks asli"""
        return [
            {
                "original": task.text,
                "translated": task.result or task.text,
                "is_completed": task.is_completed,
                "is_failed": task.is_failed,
            }
            for task in self.tasks
        ]

    def is_idle(self) -> bool:
        """Cek apakah queue manager sedang idle"""
        return not self.is_running and not self.is_completed

    def __repr__(self):
        progress = self.get_progress()
        return f"QueueManager({progress['processed']}/{progress['total']}, running={self.is_running})"
