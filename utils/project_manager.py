"""
Project Manager - Save dan Load project terjemahan
Menyimpan progress terjemahan agar bisa dilanjutkan nanti
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from core.text_extractor import TextEntry
from config import APP_INFO

logger = logging.getLogger(__name__)


class ProjectManager:
    """
    Manager untuk save/load project terjemahan

    Format file JSON:
    {
        "version": "1.0",
        "app_version": "1.0.0",
        "created_at": "2026-04-13T...",
        "updated_at": "2026-04-13T...",
        "rom_info": {
            "file_path": "/path/to/rom.3ds",
            "game_title": "Game Title",
            "emulator_type": "3ds",
            "region": "JP",
            "file_size": 1234567
        },
        "texts": [
            {
                "original": "こんにちは",
                "translated": "Halo",
                "offset": 12345,
                "is_translated": true,
                "needs_review": false
            }
        ],
        "settings": {
            "source_lang": "auto",
            "target_lang": "Indonesian",
            "translation_provider": "g4f"
        }
    }
    """

    def __init__(self):
        self.project_data: Optional[Dict] = None

    def create_project(
        self,
        rom_info,
        texts: List[TextEntry],
        settings: Dict = None
    ) -> Dict:
        """
        Buat project baru dari ROM info dan teks

        Args:
            rom_info: ROMInfo object dari ROM Loader
            texts: List of TextEntry dari Text Extractor
            settings: Optional settings dict

        Returns:
            Project data dict
        """
        now = datetime.now().isoformat()

        self.project_data = {
            "version": "1.0",
            "app_version": APP_INFO["version"],
            "created_at": now,
            "updated_at": now,
            "rom_info": {
                "file_path": rom_info.file_path,
                "game_title": rom_info.game_title,
                "emulator_type": rom_info.emulator_type,
                "region": rom_info.region,
                "file_size": rom_info.file_size,
            },
            "texts": [
                {
                    "original": entry.original_text,
                    "translated": entry.translated_text,
                    "offset": entry.offset,
                    "is_translated": entry.is_translated,
                    "needs_review": entry.needs_review,
                }
                for entry in texts
            ],
            "settings": settings or {
                "source_lang": "auto",
                "target_lang": "Indonesian",
                "translation_provider": "g4f",
            }
        }

        logger.info(f"Project created: {rom_info.game_title}, {len(texts)} texts")
        return self.project_data

    def save_project(self, file_path: str) -> bool:
        """
        Save project ke file JSON

        Args:
            file_path: Path ke file output

        Returns:
            True jika berhasil
        """
        if not self.project_data:
            logger.error("No project data to save")
            return False

        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            self.project_data["updated_at"] = datetime.now().isoformat()

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Project saved to: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving project: {e}", exc_info=True)
            return False

    def load_project(self, file_path: str) -> Optional[Dict]:
        """
        Load project dari file JSON

        Args:
            file_path: Path ke file project

        Returns:
            Project data dict atau None jika gagal
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.project_data = json.load(f)

            logger.info(f"Project loaded: {file_path}")
            logger.info(f"Game: {self.project_data['rom_info']['game_title']}")
            logger.info(f"Texts: {len(self.project_data['texts'])}")

            return self.project_data

        except Exception as e:
            logger.error(f"Error loading project: {e}", exc_info=True)
            return None

    def update_texts(self, texts: List[TextEntry]):
        """Update teks dalam project data"""
        if not self.project_data:
            logger.error("No project data to update")
            return

        self.project_data["texts"] = [
            {
                "original": entry.original_text,
                "translated": entry.translated_text,
                "offset": entry.offset,
                "is_translated": entry.is_translated,
                "needs_review": entry.needs_review,
            }
            for entry in texts
        ]

        self.project_data["updated_at"] = datetime.now().isoformat()
        logger.info(f"Project texts updated: {len(texts)} entries")

    def get_texts_as_entries(self) -> List[TextEntry]:
        """Convert project texts ke TextEntry objects"""
        if not self.project_data:
            return []

        entries = []
        for item in self.project_data.get("texts", []):
            entry = TextEntry(
                text=item.get("original", ""),
                offset=item.get("offset", 0)
            )
            entry.translated_text = item.get("translated", "")
            entry.is_translated = item.get("is_translated", False)
            entry.needs_review = item.get("needs_review", False)
            entries.append(entry)

        return entries

    def get_rom_info(self) -> Optional[Dict]:
        """Get ROM info dari project"""
        if not self.project_data:
            return None
        return self.project_data.get("rom_info")

    def get_stats(self) -> Dict:
        """Get statistik project"""
        if not self.project_data:
            return {}

        texts = self.project_data.get("texts", [])
        total = len(texts)
        translated = sum(1 for t in texts if t.get("is_translated"))
        needs_review = sum(1 for t in texts if t.get("needs_review"))

        return {
            "total_texts": total,
            "translated": translated,
            "needs_review": needs_review,
            "pending": total - translated,
            "created_at": self.project_data.get("created_at"),
            "updated_at": self.project_data.get("updated_at"),
        }

    def merge_translated_texts(self, translated_texts: Dict[str, str]):
        """
        Merge hasil translate ke project data

        Args:
            translated_texts: Dict {original_text: translated_text}
        """
        if not self.project_data:
            return

        for item in self.project_data.get("texts", []):
            original = item.get("original", "")
            if original in translated_texts:
                item["translated"] = translated_texts[original]
                item["is_translated"] = True

        self.project_data["updated_at"] = datetime.now().isoformat()
        logger.info(f"Merged {len(translated_texts)} translated texts")
