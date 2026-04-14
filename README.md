# Emulator Game Translator

**Auto-translate game ROM untuk emulator Android dengan ChatGPT gratis**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Status](https://img.shields.io/badge/status-Building%20APK-orange)

---

## 🎯 Fitur Utama

- ✅ **Auto Extract & Translate** - Load ROM, langsung extract & translate otomatis
- ✅ **ChatGPT Gratis (G4F)** - Tanpa API key berbayar
- ✅ **Fallback Otomatis** - G4F error? Auto switch ke Ollama/HuggingFace
- ✅ **Cache System** - Teks sama tidak perlu translate ulang
- ✅ **Batch Processing** - Translate 50-100 teks per request
- ✅ **Manual Edit** - Review & koreksi hasil terjemahan
- ✅ **Export Patch** - Generate patch file (JSON/XDelta/IPS) untuk ROM
- ✅ **GUI Modern** - CustomTkinter, dark/light mode
- ✅ **Android APK** - Bisa di-build jadi APK Android

---

## 📸 Preview GUI Desktop

```
┌──────────────────────────────────────────────────────────┐
│  🎮 Emulator Game Translator           v1.0.0    [⚙️]   │
├──────────────────────────────────────────────────────────┤
│  [📂 Load ROM]                                           │
│  File: Story of Seasons - Trio of Towns (USA).3ds       │
│  Game: Story of Seasons     [3DS] [US]    1,234.56 MB   │
│  ✓ ROM loaded: 1,234 teks diekstrak                      │
├──────────────────────────────────────────────────────────┤
│  Translation Progress                                     │
│  🔄 Translating... 800/1234                             │
│  ████████████████████░░░░░░░ 64.8%                      │
│  800/1234 texts                            [⏹️ Cancel]   │
├──────────────────────────────────────────────────────────┤
│  📝 Teks & Terjemahan    [🔄 Translate] [🗑️ Clear]       │
│  ┌─────────────────────┬───────────────────────────────┐ │
│  │ Teks Asli           │ Terjemahan                    │ │
│  ├─────────────────────┼───────────────────────────────┤ │
│  │ ✓ こんにちは        │ [Halo                         ]│ │
│  │ ✓ 村へようこそ      │ [Selamat datang di desa       ]│ │
│  │ ○ まだ翻訳されていない │ Belum diterjemahkan...       │ │
│  └─────────────────────┴───────────────────────────────┘ │
├──────────────────────────────────────────────────────────┤
│  💡 Load ROM untuk memulai    [💾 Export] [🔧 Inject]    │
│                              [📁 Save Project]            │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Desktop (Linux/Debian Chroot)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan aplikasi
python main.py
```

### Android APK

APK sedang dalam proses build. Setelah selesai:
```bash
# Install via adb
adb install build/bin/emulator_translator-*-debug.apk

# Atau install manual di device Android
```

---

## 📖 Panduan Penggunaan

### 1. Load ROM Game

1. Klik tombol **"📂 Load ROM"**
2. Pilih file ROM (`.3ds`, `.nds`, `.gba`, `.iso`, `.cso`)
3. Aplikasi akan:
   - Validasi format ROM
   - Baca header untuk info game (judul, region, emulator)
   - **Auto-extract semua teks dari ROM**
   - Menampilkan jumlah teks yang diekstrak

### 2. Auto-Translate

Setelah ROM di-load dan teks diekstrak:
- Aplikasi **otomatis memulai translation**
- Progress bar menampilkan progress realtime
- Teks yang sudah di-cache akan dilewati (hemat API call)
- Jika primary provider (G4F) error, auto fallback ke Ollama/HuggingFace

### 3. Review & Edit Manual

Setelah translate selesai:
- Lihat hasil di tabel side-by-side (Original | Translation)
- **Edit manual** terjemahan yang kurang pas
- **Search** teks yang ingin dicari
- **Filter** berdasarkan status (All / Translated / Pending)

### 4. Export Hasil

Ada 3 opsi export:

#### A. Export Patch (JSON/XDelta/IPS)
- Klik **"💾 Export Patch"**
- Pilih format:
  - **JSON** - Untuk debugging/manual review
  - **XDelta** - Patch binary (perlu ROM asli + ROM modified)
  - **IPS** - Patch format lama (simple)
- Patch bisa di-share ke komunitas

#### B. Inject to ROM
- Klik **"🔧 Inject to ROM"**
- Pilih lokasi save ROM baru
- Aplikasi akan inject teks terjemahan langsung ke ROM
- Hasil: ROM baru dengan teks sudah Bahasa Indonesia

#### C. Save Project
- Klik **"📁 Save Project"**
- Save progress ke file JSON
- Bisa di-load lagi nanti untuk lanjut translate

### 5. Main Game!

Setelah ROM modified:
- Load ROM baru di emulator (Citra, Citroid, dll)
- Teks game sudah dalam Bahasa Indonesia! 🎉

---

## 🏗️ Struktur Project

```
translator-game-emulator/
│
├── main.py                     # Entry point aplikasi
├── config.py                   # Konfigurasi (API, path, settings)
├── requirements.txt            # Dependencies
├── README.md                   # Dokumentasi ini
├── prd.md                      # Product Requirements Document
├── STATUS.md                   # Status tracking development
├── .gitignore                  # Git ignore rules
│
├── core/                       # Core Engine
│   ├── rom_loader.py           # Load & validasi ROM files
│   ├── text_extractor.py       # Extract teks dari ROM binary
│   ├── text_injector.py        # Inject teks terjemahan ke ROM
│   └── patch_builder.py        # Build patch files (XDelta/IPS/JSON)
│
├── translators/                # Translation Engine
│   ├── base_translator.py      # Abstract base class untuk translators
│   ├── g4f_translator.py       # ChatGPT gratis via G4F
│   ├── ollama_translator.py    # Local LLM (Ollama) - 100% offline
│   ├── hf_translator.py        # HuggingFace API - free tier
│   ├── cache.py                # Cache system dengan TTL
│   └── queue_manager.py        # Auto-queue translation dengan fallback
│
├── gui/                        # GUI Desktop (CustomTkinter)
│   ├── main_window.py          # Window utama aplikasi
│   ├── rom_panel.py            # Panel load ROM & info
│   ├── text_panel.py           # Panel teks & terjemahan
│   ├── settings_panel.py       # Dialog pengaturan
│   └── widgets/
│       ├── progress_bar.py     # Progress bar widget realtime
│       └── text_table.py       # Tabel side-by-side dengan search/filter
│
├── utils/                      # Utilities
│   ├── file_handler.py         # File operations (read/write JSON, text)
│   ├── logger.py               # Logging dengan rotasi file
│   └── project_manager.py      # Save/Load project
│
├── data/                       # Data folder
│   ├── dictionaries/           # Custom dictionaries per game
│   ├── cache/                  # Translation cache (JSON)
│   └── logs/                   # Log files
│
├── build/                      # Android Build
│   ├── buildozer.spec          # Konfigurasi build APK
│   ├── main_kivy.py            # Kivy app untuk Android
│   └── bin/                    # Output APK (setelah build)
│
└── tests/                      # Testing
    └── test_integration.py     # Integration tests (18 tests)
```

---

## 🔧 Konfigurasi

Edit file `config.py` untuk kustomisasi:

### Translation Provider

```python
TRANSLATION_CONFIG = {
    # Provider utama (REKOMENDASI: g4f)
    "primary_provider": "g4f",
    
    # Fallback providers (urutan prioritas)
    "fallback_providers": ["ollama", "huggingface"],
    
    # G4F Settings
    "g4f": {
        "model": "gpt-3.5-turbo",      # Model ChatGPT
        "max_retries": 3,               # Retry jika gagal
        "timeout": 30,                  # Timeout (seconds)
        "batch_size": 50,               # Teks per request
    },
    
    # Ollama Settings (Local LLM)
    "ollama": {
        "model": "llama3.2:1b",         # Model ringan
        "host": "http://localhost:11434",
        "timeout": 60,
        "batch_size": 30,
    },
    
    # HuggingFace Settings
    "huggingface": {
        "model": "Helsinki-NLP/opus-mt-ja-id",  # JP → ID
        "timeout": 30,
        "batch_size": 100,
    },
}
```

### Target Bahasa

```python
TRANSLATION_LANGUAGE = {
    "source": "auto",        # Auto-detect
    "target": "Indonesian",  # Target bahasa
    "target_code": "id",
}
```

### GUI Settings

```python
GUI_CONFIG = {
    "theme": "dark",            # "dark" atau "light"
    "color_theme": "blue",      # "blue", "green", "dark-blue"
    "window_size": (1200, 800), # Width, Height
    "auto_translate": True,     # Auto-translate saat load ROM
}
```

### Cache Settings

```python
CACHE_CONFIG = {
    "enabled": True,
    "max_size": 10000,          # Max entries
    "ttl": 86400 * 7,           # 7 hari (seconds)
    "file": "data/cache/translation_cache.json",
}
```

---

## 🤖 Translation Providers

| Provider | API Key | Internet | Status | Keterangan |
|----------|---------|----------|--------|------------|
| **G4F (ChatGPT)** | ❌ No | ✅ Yes | ✅ Recommended | Gratis, no API key |
| **Ollama (Local)** | ❌ No | ❌ No | ✅ Alternative | 100% offline, butuh device kuat |
| **HuggingFace** | ❌ No | ✅ Yes | ✅ Fallback | Free tier 30k tokens/hari |

### Setup Ollama (Offline Translation)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull model ringan (1-2GB)
ollama pull llama3.2:1b

# Edit config.py
TRANSLATION_CONFIG["primary_provider"] = "ollama"
```

---

## ☁️ Build APK di Google Colab (Gratis!)

Tidak punya komputer kuat? Build APK langsung di cloud dengan Google Colab!

### Quick Start

1. **Upload project ke Google Drive**
   - Buat folder `translator-game-emulator` di Google Drive
   - Upload seluruh project

2. **Buka Google Colab**
   - Kunjungi [colab.research.google.com](https://colab.research.google.com/)
   - Klik **"New Notebook"**

3. **Install Dependencies**
   ```python
   !pip install buildozer cython==0.29.33
   !apt-get update
   !apt-get install -y python3-pip build-essential git python3-dev \
       libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
       openjdk-17-jdk autoconf automake libtool libffi-dev libssl-dev
   ```

4. **Mount Drive & Copy Project**
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   !cp -r /content/drive/MyDrive/translator-game-emulator /content/
   %cd /content/translator-game-emulator/build
   ```

5. **Build APK!**
   ```python
   !buildozer android debug
   ```

6. **Download APK**
   ```python
   !cp /content/translator-game-emulator/build/bin/*.apk /content/drive/MyDrive/
   ```

### Estimasi Waktu
- **Pertama kali:** ~20-35 menit (download SDK/NDK)
- **Build berikutnya:** ~8-15 menit (cached)

### 📖 Panduan Lengkap
Lihat dokumentasi lengkap di: [docs/BUILD_COLAB.md](docs/BUILD_COLAB.md)

---

## 📦 Build APK Android

### Prerequisites

```bash
# Install buildozer & cython
pip install buildozer cython

# Install system dependencies (Debian/Ubuntu)
sudo apt install -y build-essential git python3-dev \
    ffmpeg libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
    openjdk-17-jdk-headless aidl
```

### Build

```bash
cd build
buildozer android debug
```

### Output

APK akan ada di folder `bin/`:
```
build/bin/emulator_translator-*-debug.apk
```

### Install ke Device

```bash
# Via ADB
adb install build/bin/emulator_translator-*-debug.apk

# Atau copy ke device dan install manual
```

---

## 📝 Supported ROM Formats

| Emulator | Format | Metode Ekstraksi | Status |
|----------|--------|------------------|--------|
| **Citra (3DS)** | `.3ds`, `.cci` | Pattern matching text bytes | ✅ Supported |
| **Citroid (3DS)** | `.3ds`, `.cci` | Sama seperti Citra | ✅ Supported |
| **DraStic (DS)** | `.nds` | Nintendo DS text tables | ✅ Supported |
| **VisualBoy (GBA)** | `.gba` | GBA text pointers | ✅ Supported |
| **PPSSPP (PSP)** | `.iso`, `.cso` | PSP text encoding (Shift-JIS) | ✅ Supported |
| **JJSP (PSP)** | `.iso`, `.cso` | Sama seperti PPSSPP | ⏳ Planned |

---

## 🛠️ Development

### Run Tests

```bash
# Integration tests
python -m unittest tests.test_integration -v

# Hasil: 18 tests, semua pass ✅
```

### Code Style

```bash
# Install linter & formatter
pip install flake8 black

# Check code quality
flake8 .

# Auto-format code
black .
```

### Run Desktop App

```bash
# Development mode
python main.py

# Dengan logging verbose
export LOG_LEVEL=DEBUG && python main.py
```

---

## 🐛 Troubleshooting

### G4F Error / Rate Limit
- Aplikasi akan **auto-fallback** ke Ollama atau HuggingFace
- Atau install Ollama untuk translation offline

### ROM Tidak Terbaca
- Pastikan format ROM didukung (`.3ds`, `.nds`, `.gba`, `.iso`)
- ROM tidak boleh encrypted
- Cek log di `data/logs/app.log` untuk detail error

### Text Tidak Terekstrak
- Beberapa game punya format text khusus
- Coba adjust `min_text_length` di `config.py`
- Report issue dengan sample ROM

### Build APK Gagal
- Pastikan semua dependencies terinstall
- Build di filesystem native (ext4), bukan exFAT/FUSE
- Cek log build di `build/.buildozer/android/platform/`

### Translation Lambat
- Enable cache di `config.py`
- Gunakan batch_size lebih besar
- Install Ollama untuk offline translation (lebih cepat)

---

## 📊 Arsitektur Aplikasi

### Flow Aplikasi

```
[User buka app]
    ↓
[User load ROM file]
    ↓
[Auto-detect tipe game/emulator]
    ↓
[🔄 AUTO EXTRACT: Scan & ekstrak SEMUA teks dari ROM]
    ↓
[🔄 AUTO TRANSLATE: Queue semua teks → G4F API (background)]
    │    ├─ Batch 50-100 teks per request
    │    ├─ Cek cache dulu (skip jika sudah ada)
    │    ├─ Progress bar realtime
    │    └─ Fallback otomatis jika G4F error
    ↓
[Tampilkan hasil di tabel: kiri=asli, kanan=terjemahan]
    ↓
[User review & edit manual (opsional)]
    ↓
[User klik "Export" → Patch/Overlay/Save Project]
    ↓
[User main game di emulator → teks sudah Indonesia!]
```

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│                  GUI (CustomTkinter)            │
│  ┌─────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ROM Panel│  │Text Panel│  │Settings Panel │  │
│  └────┬────┘  └────┬─────┘  └───────────────┘  │
│       │             │                            │
│  ┌────▼─────────────▼────────────────────────┐  │
│  │         Main Window Controller            │  │
│  └────────────────────┬──────────────────────┘  │
└───────────────────────┼─────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌───────────┐ ┌──────────────┐
│  Core Engine  │ │Translators│ │   Utilities   │
│ ┌───────────┐ │ │ ┌───────┐ │ │ ┌──────────┐ │
│ │ROM Loader │ │ │ │ G4F   │ │ │ │  Cache   │ │
│ │Extractor  │ │ │ │Ollama │ │ │ │  Queue   │ │
│ │Injector   │ │ │ │   HF  │ │ │ │  Project │ │
│ │Patch      │ │ │ └───────┘ │ │ │  Logger  │ │
│ └───────────┘ │ └───────────┘ │ └──────────┘ │
└───────────────┴───────────────┴──────────────┘
```

---

## 📄 License

MIT License - lihat [LICENSE](LICENSE) untuk detail

---

## 🙏 Credits

- **G4F** - [g4f library](https://github.com/xtekky/gpt4free)
- **CustomTkinter** - [Tom Schimansky](https://github.com/TomSchimansky/CustomTkinter)
- **Kivy** - [Kivy.org](https://kivy.org/)
- **Buildozer** - [Kivy Buildozer](https://github.com/kivy/buildozer)
- **Python-for-Android** - [p4a](https://github.com/kivy/python-for-android)

---

## 📞 Support

Ada masalah atau pertanyaan?
- Buka [Issues](https://github.com/username/emulator-game-translator/issues)
- Baca dokumentasi di `docs/` folder
- Cek status development di `STATUS.md`

---

**Made with ❤️ by Qwen Code**