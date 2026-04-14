# Product Requirements Document (PRD)
## Aplikasi Penerjemah Teks Game Emulator Android

**Versi:** 1.0  
**Tanggal:** 12 April 2026  
**Status:** Draft

---

## 1. Ringkasan Produk

### 1.1 Latar Belakang
Game emulator Android (seperti Citra, Citroid, JJSP, DraStic, dll) sering menjalankan game dengan bahasa asing (Jepang, Inggris, dll). Para gamer Indonesia kesulitan memahami teks/dialog dalam game karena tidak ada terjemahan bahasa Indonesia.

### 1.2 Solusi
Membuat aplikasi desktop berbasis Python dengan GUI ringan yang dapat:
- Mengekstrak teks dari ROM game emulator
- Menerjemahkan teks ke bahasa Indonesia (via API translator)
- Membuat patch terjemahan atau file overlay
- Output berupa file yang bisa langsung digunakan di emulator

### 1.3 Target User
- Gamer emulator Android di Indonesia
- Romhacker/translator komunitas
- Pengguna casual yang ingin translate game cepat

---

## 2. Fitur Utama

### 2.1 MVP (Minimum Viable Product)

#### F1 - Load ROM Game
- User dapat memilih file ROM (.3ds, .nds, .gba, .iso, dll)
- Validasi file ROM dan deteksi otomatis tipe emulator
- Tampilkan info game (judul, region, bahasa)

#### F2 - Ekstrak Teks (OTOMATIS)
- **Auto-detect semua teks dari ROM saat load**
- Ekstraksi teks dari ROM berdasarkan pola emulator
- Support format teks umum: pointer tables, text databases, dialog, menu, item names, dll
- **Langsung queue ke translation engine tanpa user intervention**

#### F3 - Translate OTOMATIS (FULL AUTO)
- **Setelah ekstrak selesai, LANGSUNG auto-translate semua teks via G4F**
- User TIDAK perlu klik tombol translate
- Progress bar realtime: `Translating: ████████░░ 80% (800/1000)`
- Background process - user bisa lihat progress & cancel jika perlu
- **Cache otomatis** - teks yang sama tidak perlu translate ulang
- **Fallback otomatis** - kalau G4F error/rate limit → switch ke Ollama/HuggingFace

#### F4 - Tampilkan Hasil & Manual Edit
- Tampilkan teks asli + terjemahan side-by-side
- User bisa edit manual hasil terjemahan jika ada yang kurang pas
- Search & filter teks
- Highlight teks yang belum sempurna

#### F5 - Export Patch
- Generate patch file (.xdelta, .bps, atau format custom)
- Atau export file teks terjemahan untuk overlay emulator
- Simpan project untuk edit nanti

### 2.2 Future Enhancements (Post-MVP)

| Fitur | Deskripsi | Prioritas |
|-------|-----------|-----------|
| OCR Screenshot | Screenshot game → OCR → translate | Medium |
| Real-time Translation | Overlay translate saat game berjalan | Low |
| kamus Custom | User bisa tambah kamus khusus game | High |
| Collaborative | Share terjemahan ke komunitas | Low |
| Multi-bahasa | Support selain Indonesia | Medium |

---

## 3. Arsitektur Teknis

### 3.1 Tech Stack

| Komponen | Teknologi | Alasan |
|----------|-----------|--------|
| **GUI Framework** | CustomTkinter | Ringan, modern, native Python |
| **Translation API** | **G4F (ChatGPT gratis)** / Ollama / HuggingFace | 100% gratis, no API key berbayar |
| **ROM Parser** | Custom parser per emulator | Fleksibel untuk berbagai format |
| **Build to APK** | **Buildozer + Kivy** ATAU **Flet + Briefcase** | Bisa compile Python → Android APK |
| **Package Manager** | pip | Standar Python |
| **Version Control** | Git | Standar |

### 3.2 Struktur Folder

```
emulator-translator/
├── main.py                 # Entry point aplikasi
├── config.py               # Konfigurasi (API, path, dll)
├── requirements.txt        # Dependencies
│
├── core/
│   ├── __init__.py
│   ├── rom_loader.py       # Load & validasi ROM
│   ├── text_extractor.py   # Ekstrak teks dari ROM
│   ├── text_injector.py    # Inject teks terjemahan ke ROM
│   └── patch_builder.py    # Build patch file
│
├── translators/
│   ├── __init__.py
│   ├── base_translator.py  # Abstract base class
│   ├── libre_translate.py  # LibreTranslate API
│   ├── deep_translator.py  # deep-translator library
│   └── custom_dict.py      # Kamus manual user
│
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Window utama
│   ├── rom_panel.py        # Panel load ROM
│   ├── text_panel.py       # Panel teks asli & terjemahan
│   ├── settings_panel.py   # Pengaturan
│   └── widgets/            # Custom widgets
│       ├── text_table.py
│       └── progress_bar.py
│
├── utils/
│   ├── __init__.py
│   ├── file_handler.py
│   └── logger.py
│
├── data/
│   └── dictionaries/       # kamus per game
│
├── build/
│   └── buildozer.spec      # Konfigurasi build APK
│
└── prd.md                  # Dokumen ini
```

### 3.3 Flow Aplikasi

```
[User buka app]
    ↓
[User load ROM file]
    ↓
[Auto-detect tipe game/emulator]
    ↓
[🔄 AUTO EKSTRAK: Scan & ekstrak SEMUA teks dari ROM]
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

---

## 4. Spesifikasi Teknis Detail

### 4.1 ROM Support (MVP)

| Emulator | Format ROM | Metode Ekstraksi |
|----------|-----------|------------------|
| Citra (3DS) | .3ds, .cci | Pattern matching text bytes |
| Citroid (3DS) | .3ds, .cci | Sama seperti Citra |
| JJSP (PSP) | .iso, .cso | PSP text encoding (Shift-JIS) |
| DraStic (DS) | .nds | Nintendo DS text tables |
| VisualBoy (GBA) | .gba | GBA text pointers |

### 4.2 Translation Engine

#### Opsi Translator Gratis (Tanpa API Key Berbayar)

| Provider | Status | Keterangan |
|----------|--------|------------|
| **G4F (g4f)** | ✅ REKOMENDASI | Wrapper ChatGPT gratis, no API key |
| **HuggingFace API** | ✅ Gratis tier | Model open-source, free 30k tokens/hari |
| **Cohere Free** | ✅ Free tier | 100 calls/min, cukup untuk MVP |
| **Ollama (Local)** | ✅ 100% Offline | Run LLM lokal (Llama3, Mistral), no internet |

**Rekomendasi Utama: G4F (g4f)**
- Wrapper untuk akses ChatGPT gratis tanpa API key
- Support multiple backend (GPT-3.5, GPT-4 via free providers)
- Install: `pip install g4f`
- Rate limit: tergantung provider, tapi cukup untuk translate game

**Fallback: Ollama (Local LLM)**
- Jika user punya device powerful, bisa run LLM lokal
- Model ringan: `llama3.2:1b` atau `phi3:mini` (~1-2GB)
- 100% offline, no rate limit
- Cocok untuk bulk translation tanpa bergantung internet

```python
# Contoh interface translator
class BaseTranslator:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        pass

# Implementasi dengan G4F (ChatGPT gratis)
import g4f

class G4FTranslator(BaseTranslator):
    def __init__(self, model="gpt-3.5-turbo"):
        self.model = model
    
    def translate(self, text, source_lang="auto", target_lang="Indonesian"):
        if not text or text.isspace():
            return text
        
        prompt = f"Translate the following {source_lang} text to {target_lang}. Only return the translated text, nothing else:\n\n{text}"
        
        response = g4f.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.strip() if response else text

# Alternatif: Ollama (Local LLM - 100% offline)
import requests

class OllamaTranslator(BaseTranslator):
    def __init__(self, model="llama3.2:1b", host="http://localhost:11434"):
        self.model = model
        self.host = host
    
    def translate(self, text, source_lang="auto", target_lang="Indonesian"):
        if not text or text.isspace():
            return text
        
        prompt = f"Translate this {source_lang} text to {target_lang}. Only return translation:\n\n{text}"
        
        response = requests.post(f"{self.host}/api/generate", json={
            "model": self.model,
            "prompt": prompt,
            "stream": False
        })
        
        if response.status_code == 200:
            return response.json().get("response", text).strip()
        return text

# Fallback: HuggingFace Free API
from huggingface_hub import InferenceClient

class HFTranslator(BaseTranslator):
    def __init__(self, model="Helsinki-NLP/opus-mt-en-id"):
        # Free tier: 30k tokens/day
        self.client = InferenceClient(model=model)
    
    def translate(self, text, source_lang="auto", target_lang="id"):
        if not text or text.isspace():
            return text
        # Implementation depends on model
        return self.client.translation(text)
```

### 4.3 GUI Layout (CustomTkinter)

```
┌──────────────────────────────────────────────┐
│  [Header] Emulator Game Translator    [⚙️]   │
├──────────────────────────────────────────────┤
│  [Load ROM] 📂  │ Game: Story of Seasons    │
│                 │ Region: JP → Target: ID   │
├──────────────────────────────────────────────┤
│  [STATUS] 🔄 Auto Translating...            │
│           ████████░░ 80% (800/1000 texts)   │
├──────────────────────────────────────────────┤
│  ┌─────────────────┬──────────────────────┐  │
│  │ Teks Asli (JP)  │ Terjemahan (ID)      │  │
│  ├─────────────────┼──────────────────────┤  │
│  │ こんにちは      │ Halo                 │  │
│  │ 村へようこそ    │ Selamat datang di desa│ │
│  │ ...             │ ...                  │  │
│  └─────────────────┴──────────────────────┘  │
├──────────────────────────────────────────────┤
│  [⏹️ Cancel]  [💾 Export]  [📋 Copy]         │
│  ✓ Auto-translate ON  |  Cache: 234 items   │
└──────────────────────────────────────────────┘
```

### 4.4 Dependencies (requirements.txt)

```
customtkinter>=5.2.0
darkdetect>=0.8.0
g4f>=0.3.0.0
requests>=2.31.0
huggingface-hub>=0.20.0
packaging>=23.0
Pillow>=10.0.0
```

---

## 5. Build ke APK Android

### 5.1 Opsi Build

#### Opsi A: Buildozer + Kivy (REKOMENDASI)
```bash
# Install buildozer di Ubuntu chroot
pip install buildozer cython

# Install dependencies Android SDK/NDK
sudo apt install -y python3-pip build-essential git \
    python3-dev ffmpeg-libs libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev

# Build APK
buildozer init
buildozer android debug
```

**Kelebihan:**
- Mature & well-documented
- Support full Android APK
- Bisa akses storage Android

**Kekurangan:**
- GUI Kivy berbeda dari CustomTkinter (perlu rewrite UI)
- Build pertama lama (download SDK/NDK ~2GB)

#### Opsi B: Flet (Modern Alternative)
```bash
pip install flet
flet build apk
```

**Kelebihan:**
- GUI lebih modern (berbasis Flutter)
- Setup lebih simpel

**Kekurangan:**
- Masih experimental untuk Android
- APK size lebih besar (~50MB+)

### 5.2 Rekomendasi Final

**Untuk MVP Desktop (Ubuntu chroot):**
- Pakai **CustomTkinter** → cepat develop
- Output: `.py` atau build ke `.exe` dengan PyInstaller

**Untuk Android APK:**
- Migrate GUI ke **Kivy** (tetap logic core sama)
- Build dengan **Buildozer**
- Target APK size: < 50MB

---

## 6. User Stories

### US-001: Load & Auto Translate ROM
```
Sebagai gamer,
Saya ingin load file ROM dan aplikasi LANGSUNG auto-translate semua teks,
Sehingga saya tidak perlu klik tombol translate manual.
```

### US-002: Manual Edit
```
Sebagai translator,
Saya ingin mengedit manual hasil terjemahan,
Sehingga terjemahan lebih akurat sesuai konteks game.
```

### US-003: Export & Share
```
Sebagai user,
Saya ingin export hasil terjemahan ke file patch,
Sehingga bisa saya share ke komunitas atau langsung saya pakai.
```

### US-004: Save Project
```
Sebagai user,
Saya ingin menyimpan progress terjemahan,
Sehingga bisa saya lanjutkan nanti tanpa mulai dari awal.
```

---

## 7. Acceptance Criteria

| ID | Criteria | Status |
|----|----------|--------|
| AC-01 | Aplikasi bisa load file ROM .3ds | ✅ TODO |
| AC-02 | Aplikasi ekstrak minimal 80% teks game | ✅ TODO |
| **AC-03** | **Auto-translate jalan tanpa user klik tombol** | ✅ TODO |
| AC-04 | Terjemahan via G4F berhasil tanpa error | ✅ TODO |
| AC-05 | User bisa edit manual teks terjemahan | ✅ TODO |
| AC-06 | Export patch file berhasil dibuat | ✅ TODO |
| AC-07 | GUI responsif tanpa lag | ✅ TODO |
| AC-08 | APK Android bisa install & jalan | ✅ TODO |

---

## 8. Timeline Estimasi

| Fase | Duration | Deliverable |
|------|----------|-------------|
| **Fase 1: Setup** | 1-2 hari | Struktur project, dependencies |
| **Fase 2: Core** | 3-5 hari | ROM loader, text extractor |
| **Fase 3: Auto Translator** | 4-5 hari | G4F integration, auto-queue, cache, fallback |
| **Fase 4: GUI** | 3-4 hari | CustomTkinter UI + progress bar realtime |
| **Fase 5: Export** | 2-3 hari | Patch builder, save project |
| **Fase 6: Build APK** | 3-5 hari | Kivy migration, buildozer |
| **TOTAL** | **~16-24 hari** | APK ready to use |

---

## 9. Risk & Mitigasi

| Risk | Impact | Mitigasi |
|------|--------|----------|
| ROM encryption tidak support | High | Dokumentasi format ROM yang disupport |
| **G4F provider down/rate limit** | High | **Fallback ke Ollama local atau HuggingFace** |
| APK size terlalu besar | Medium | Optimize dependencies, strip unused |
| Text encoding kompleks | High | Mulai dari 1 emulator dulu (Citra) |
| Buildozer fail di chroot | Medium | Test di environment yang sama dulu |

---

## 10. Metrik Sukses

- ✅ Aplikasi bisa translate 1 game penuh tanpa crash
- ✅ APK size < 50MB
- ✅ Terjemahan accuracy > 70% (auto) + manual edit
- ✅ User bisa export & apply patch ke ROM
- ✅ UI responsif di device low-end (RAM 2GB)

---

## 11. Referensi

- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)
- [Buildozer GitHub](https://github.com/kivy/buildozer)
- [Kivy Framework](https://kivy.org/)
- [deep-translator PyPI](https://pypi.org/project/deep-translator/)
- [LibreTranslate](https://libretranslate.com/)

---

**Dibuat oleh:** Qwen Code AI Assistant  
**Disetujui oleh:** _Pending_  
**Next Step:** Implementasi Fase 1 (Setup Project)
