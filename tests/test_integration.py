"""
Integration Test - Test full flow dari load ROM sampai export
"""

import unittest
import os
import sys
import tempfile
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rom_loader import ROMLoader, ROMInfo
from core.text_extractor import TextExtractor, TextEntry
from core.text_injector import TextInjector
from core.patch_builder import PatchBuilder

from translators.g4f_translator import G4FTranslator
from translators.ollama_translator import OllamaTranslator
from translators.hf_translator import HFTranslator
from translators.cache import TranslationCache
from translators.queue_manager import QueueManager, TranslationTask

from utils.project_manager import ProjectManager
from utils.file_handler import FileHandler


class TestROMExtractor(unittest.TestCase):
    """Test text extraction dari ROM"""

    def setUp(self):
        self.extractor = TextExtractor()

    def test_extract_ascii_strings(self):
        """Test extract ASCII strings dari binary data"""
        # Buat sample binary data dengan string di dalamnya
        data = b'\x00\x00\x00Hello World\x00\x00Test String\x00\x00'
        
        strings = self.extractor._extract_ascii_strings(data)
        
        # Harus menemukan minimal 2 strings
        self.assertGreaterEqual(len(strings), 2)
        
        # Cek content
        string_values = [s[0] for s in strings]
        self.assertIn('Hello World', string_values)
        self.assertIn('Test String', string_values)

    def test_extract_with_min_length_filter(self):
        """Test filter teks berdasarkan panjang minimum"""
        # Setup sample entries
        self.extractor.extracted_texts = [
            TextEntry("Hi", 0),           # 2 chars, terlalu pendek
            TextEntry("Hello", 10),       # 5 chars, ok
            TextEntry("World Test", 20),  # 11 chars, ok
        ]
        
        # Filter min 3 chars
        self.extractor.filter_texts(min_length=3)
        
        # Harus tersisa 2 entries
        self.assertEqual(len(self.extractor.extracted_texts), 2)

    def test_text_entry_creation(self):
        """Test pembuatan TextEntry"""
        entry = TextEntry("Hello World", 100)
        
        self.assertEqual(entry.original_text, "Hello World")
        self.assertEqual(entry.offset, 100)
        self.assertFalse(entry.is_translated)
        self.assertEqual(entry.translated_text, "")


class TestTranslationCache(unittest.TestCase):
    """Test cache system"""

    def setUp(self):
        # Buat temporary file untuk cache
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()
        self.cache = TranslationCache(
            cache_file=self.temp_file.name,
            max_size=100,
            ttl=86400  # 1 hari
        )

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_cache_set_and_get(self):
        """Test set dan get cache"""
        self.cache.set("Hello", "Halo", "auto", "Indonesian")
        
        result = self.cache.get("Hello", "auto", "Indonesian")
        self.assertEqual(result, "Halo")

    def test_cache_miss(self):
        """Test cache miss"""
        result = self.cache.get("NonExistent", "auto", "Indonesian")
        self.assertIsNone(result)

    def test_cache_has(self):
        """Test cache has method"""
        self.cache.set("Test", "Tes", "auto", "Indonesian")
        
        self.assertTrue(self.cache.has("Test", "auto", "Indonesian"))
        self.assertFalse(self.cache.has("Other", "auto", "Indonesian"))

    def test_cache_clear(self):
        """Test clear cache"""
        self.cache.set("A", "B")
        self.cache.clear()
        
        self.assertEqual(len(self.cache), 0)

    def test_cache_persistence(self):
        """Test cache save dan load dari file"""
        self.cache.set("Hello", "Halo")
        self.cache.flush()
        
        # Buat cache baru dari file yang sama
        cache2 = TranslationCache(cache_file=self.temp_file.name)
        
        result = cache2.get("Hello")
        self.assertEqual(result, "Halo")


class TestQueueManager(unittest.TestCase):
    """Test queue manager"""

    def setUp(self):
        # Buat mock translator untuk test
        class MockTranslator:
            def __init__(self, name):
                self.name = name
            def is_available(self):
                return True
            def translate(self, text, source_lang, target_lang):
                return f"[{target_lang}] {text}"

        self.translators = {
            "mock": MockTranslator("mock")
        }
        self.cache = TranslationCache(enabled=False)
        
        self.queue_manager = QueueManager(
            translators=self.translators,
            cache=self.cache,
            primary_provider="mock",
            fallback_providers=[]
        )

    def test_add_texts(self):
        """Test add texts ke queue"""
        self.queue_manager.add_texts(["Hello", "World"])
        
        self.assertEqual(self.queue_manager.total_count, 2)
        self.assertEqual(len(self.queue_manager.tasks), 2)

    def test_clear_queue(self):
        """Test clear queue"""
        self.queue_manager.add_texts(["A", "B", "C"])
        self.queue_manager.clear_queue()
        
        self.assertEqual(self.queue_manager.total_count, 0)
        self.assertEqual(len(self.queue_manager.tasks), 0)

    def test_get_progress(self):
        """Test get progress"""
        self.queue_manager.add_texts(["A", "B"])
        progress = self.queue_manager.get_progress()
        
        self.assertIn('total', progress)
        self.assertIn('processed', progress)
        self.assertIn('progress', progress)


class TestProjectManager(unittest.TestCase):
    """Test save/load project"""

    def setUp(self):
        self.pm = ProjectManager()
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.temp_file.close()

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_create_and_save_project(self):
        """Test create dan save project"""
        # Buat sample ROM info
        class MockROMInfo:
            file_path = "/test/rom.3ds"
            game_title = "Test Game"
            emulator_type = "3ds"
            region = "JP"
            file_size = 1234567

        texts = [
            TextEntry("Hello", 100),
            TextEntry("World", 200),
        ]

        self.pm.create_project(MockROMInfo(), texts)
        result = self.pm.save_project(self.temp_file.name)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.temp_file.name))

    def test_load_project(self):
        """Test load project"""
        # Save dulu
        class MockROMInfo:
            file_path = "/test/rom.3ds"
            game_title = "Test Game"
            emulator_type = "3ds"
            region = "JP"
            file_size = 1234567

        texts = [TextEntry("Hello", 100)]
        self.pm.create_project(MockROMInfo(), texts)
        self.pm.save_project(self.temp_file.name)

        # Load
        pm2 = ProjectManager()
        data = pm2.load_project(self.temp_file.name)
        
        self.assertIsNotNone(data)
        self.assertEqual(data['rom_info']['game_title'], "Test Game")
        self.assertEqual(len(data['texts']), 1)

    def test_get_stats(self):
        """Test get project stats"""
        class MockROMInfo:
            file_path = "/test/rom.3ds"
            game_title = "Test"
            emulator_type = "3ds"
            region = "JP"
            file_size = 1000

        texts = [
            TextEntry("A", 0),
            TextEntry("B", 1),
        ]
        texts[0].is_translated = True
        
        self.pm.create_project(MockROMInfo(), texts)
        stats = self.pm.get_stats()
        
        self.assertEqual(stats['total_texts'], 2)
        self.assertEqual(stats['translated'], 1)
        self.assertEqual(stats['pending'], 1)


class TestPatchBuilder(unittest.TestCase):
    """Test patch builder"""

    def setUp(self):
        self.builder = PatchBuilder()
        self.temp_dir = tempfile.mkdtemp()

    def test_create_json_patch(self):
        """Test create JSON patch"""
        entries = [
            TextEntry("Hello", 100),
            TextEntry("World", 200),
        ]
        entries[0].is_translated = True
        entries[0].translated_text = "Halo"
        
        output_path = os.path.join(self.temp_dir, "test_patch.json")
        result = self.builder.create_json_patch(entries, output_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(output_path))
        
        # Validate JSON content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['version'], '1.0')
        self.assertEqual(len(data['texts']), 1)  # Hanya yang translated


class TestFileHandler(unittest.TestCase):
    """Test file handler utility"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def test_write_and_read_json(self):
        """Test write dan read JSON"""
        data = {"key": "value", "number": 123}
        path = os.path.join(self.temp_dir, "test.json")
        
        result = FileHandler.write_json(path, data)
        self.assertTrue(result)
        
        loaded = FileHandler.read_json(path)
        self.assertEqual(loaded, data)

    def test_write_and_read_text(self):
        """Test write dan read text"""
        content = "Hello World\nTest"
        path = os.path.join(self.temp_dir, "test.txt")
        
        result = FileHandler.write_text(path, content)
        self.assertTrue(result)
        
        loaded = FileHandler.read_text(path)
        self.assertEqual(loaded, content)

    def test_ensure_directory(self):
        """Test ensure directory exists"""
        dir_path = os.path.join(self.temp_dir, "subdir", "nested")
        result = FileHandler.ensure_directory(dir_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(dir_path))


if __name__ == '__main__':
    unittest.main()
