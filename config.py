"""
Configuration file for Emulator Game Translator
Central tempat untuk semua pengaturan & settings
"""

import os
from pathlib import Path

# === PATH CONFIGURATION ===
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DICTIONARIES_DIR = DATA_DIR / "dictionaries"
CACHE_DIR = DATA_DIR / "cache"
LOGS_DIR = DATA_DIR / "logs"

# Auto-create directories
for dir_path in [DATA_DIR, DICTIONARIES_DIR, CACHE_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# === TRANSLATION ENGINE ===
TRANSLATION_CONFIG = {
    # Provider utama (REKOMENDASI)
    "primary_provider": "g4f",
    
    # Provider fallback (jika primary gagal)
    "fallback_providers": ["ollama", "huggingface"],
    
    # G4F Settings
    "g4f": {
        "model": "gpt-3.5-turbo",
        "max_retries": 3,
        "timeout": 30,  # seconds
        "batch_size": 50,  # teks per request
    },
    
    # Ollama Settings (Local LLM)
    "ollama": {
        "model": "llama3.2:1b",
        "host": "http://localhost:11434",
        "timeout": 60,
        "batch_size": 30,
    },
    
    # HuggingFace Settings
    "huggingface": {
        "model": "Helsinki-NLP/opus-mt-ja-id",  # Japanese → Indonesian
        "timeout": 30,
        "batch_size": 100,
    },
}

# === TARGET LANGUAGE ===
TRANSLATION_LANGUAGE = {
    "source": "auto",  # auto-detect
    "target": "Indonesian",  # target bahasa
    "target_code": "id",  # untuk API tertentu
}

# === CACHE SETTINGS ===
CACHE_CONFIG = {
    "enabled": True,
    "max_size": 10000,  # max entries
    "ttl": 86400 * 7,  # 7 hari (seconds)
    "file": CACHE_DIR / "translation_cache.json",
}

# === ROM SETTINGS ===
ROM_CONFIG = {
    # Format ROM yang disupport
    "supported_formats": [".3ds", ".cci", ".nds", ".gba", ".iso", ".cso"],
    
    # Default text encoding per emulator
    "encodings": {
        "3ds": ["utf-8", "shift-jis", "euc-jp"],
        "nds": ["utf-8", "shift-jis"],
        "gba": ["shift-jis", "ascii"],
        "psp": ["shift-jis", "utf-8"],
    },
    
    # Minimum text length untuk diekstrak (filter noise)
    "min_text_length": 2,
    
    # Maximum text length (antisipasi false positive)
    "max_text_length": 500,
}

# === GUI SETTINGS ===
GUI_CONFIG = {
    "theme": "dark",  # "dark" atau "light"
    "color_theme": "blue",  # "blue", "green", "dark-blue"
    "window_size": (1200, 800),  # width, height
    "window_title": "Emulator Game Translator",
    "font_size": 14,
    "auto_translate": True,  # auto-translate saat load ROM
    "show_progress": True,  # tampilkan progress bar
}

# === EXPORT SETTINGS ===
EXPORT_CONFIG = {
    # Default export format
    "default_format": "xdelta",  # "xdelta", "bps", "json", "txt"
    
    # Output directory
    "output_dir": BASE_DIR / "output",
    
    # Auto-create output dir
    "auto_create_dir": True,
}

# Auto-create output dir
if EXPORT_CONFIG["auto_create_dir"]:
    EXPORT_CONFIG["output_dir"].mkdir(parents=True, exist_ok=True)

# === LOGGING ===
LOG_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "file": LOGS_DIR / "app.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 3,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
}

# === APP INFO ===
APP_INFO = {
    "name": "Emulator Game Translator",
    "version": "1.0.0",
    "author": "Qwen Code",
    "description": "Auto-translate game ROM untuk emulator Android",
}
