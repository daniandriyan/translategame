# Arsitektur Teknis - Emulator Game Translator

Dokumen ini menjelaskan arsitektur teknis aplikasi untuk developer.

---

## 🏗️ Overview

Aplikasi ini terdiri dari beberapa modul utama:

```
┌─────────────────────────────────────────────────────────┐
│                      User Interface                     │
│                 (CustomTkinter Desktop)                 │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Core Engine │ │  Translation │ │  Utilities   │
│              │ │   Engine     │ │              │
│ • ROM Loader │ │ • G4F        │ │ • Cache      │
│ • Extractor  │ │ • Ollama     │ │ • Queue Mgr  │
│ • Injector   │ │ • HuggingFace│ │ • Logger     │
│ • Patch      │ │              │ │ • Project    │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 📦 Modul Detail

### 1. Core Engine

#### ROM Loader (`core/rom_loader.py`)

**Tanggung Jawab:**
- Validasi file ROM
- Detect emulator type dari ekstensi
- Baca header untuk extract info game
- Return `ROMInfo` object

**Class: ROMInfo**
```python
class ROMInfo:
    file_path: str       # Path ke file
    file_size: int       # Size dalam bytes
    file_name: str       # Nama file
    extension: str       # .3ds, .nds, dll
    emulator_type: str   # 3ds, nds, gba, psp
    region: str          # JP, US, EU
    game_title: str      # Judul game
    is_valid: bool       # Valid atau tidak
    error_message: str   # Error jika ada
```

**Class: ROMLoader**
```python
class ROMLoader:
    def load_rom(file_path: str) -> ROMInfo
    def read_rom_data() -> bytes
    def get_rom_size() -> int
    
    # Internal methods
    def _detect_emulator_type() -> str
    def _read_3ds_header()
    def _read_nds_header()
    def _read_gba_header()
    def _read_psp_header()
```

**Support Format:**
- `.3ds`, `.cci` → Nintendo 3DS
- `.nds` → Nintendo DS
- `.gba` → Game Boy Advance
- `.iso`, `.cso` → PSP

---

#### Text Extractor (`core/text_extractor.py`)

**Tanggung Jawab:**
- Scan ROM binary untuk text patterns
- Extract printable strings
- Detect encoding (ASCII, Shift-JIS, UTF-8)
- Return list of `TextEntry`

**Class: TextEntry**
```python
class TextEntry:
    original_text: str    # Teks asli dari ROM
    translated_text: str  # Hasil terjemahan
    offset: int           # Offset dalam ROM binary
    is_translated: bool   # Sudah translate atau belum
    needs_review: bool    # Perlu review manual
```

**Class: TextExtractor**
```python
class TextExtractor:
    def extract_from_rom(rom_data: bytes, emulator_type: str) -> List[TextEntry]
    def filter_texts(min_length: int)
    def get_stats() -> Dict
    def export_to_dict() -> List[Dict]
    
    # Internal methods
    def _extract_ascii_strings(data: bytes) -> List[Tuple[str, int]]
    def _extract_encoded_strings(data: bytes, encoding: str)
    def _is_valid_text(text: str) -> bool
```

**Extract Strategy:**
1. Scan binary untuk printable ASCII (0x20-0x7E)
2. Scan untuk Shift-JIS encoded strings
3. Scan untuk UTF-8 strings
4. Filter berdasarkan min/max length
5. Deduplicate dan sort

---

#### Text Injector (`core/text_injector.py`)

**Tanggung Jawab:**
- Inject teks terjemahan kembali ke ROM
- Handle encoding & padding
- Manage offset & length differences

**Class: TextInjector**
```python
class TextInjector:
    def inject_to_rom(
        rom_data: bytearray,
        texts: List[TextEntry],
        emulator_type: str,
        encoding: str = None
    ) -> bytearray
    
    def inject_with_pointers(
        rom_data: bytearray,
        texts: List[TextEntry],
        pointer_table_offset: int,
        encoding: str
    ) -> bytearray
    
    def create_backup(rom_path: str) -> str
    def save_modified_rom(rom_data: bytearray, output_path: str)
    def get_stats() -> Dict
```

**Inject Strategy:**
1. Match teks asli dengan offset
2. Encode teks terjemahan (Shift-JIS/UTF-8)
3. Handle length differences:
   - Lebih pendek → pad dengan null bytes
   - Lebih panjang → truncate (atau expand dengan pointer table)
4. Write ke ROM di offset yang benar

---

#### Patch Builder (`core/patch_builder.py`)

**Tanggung Jawab:**
- Generate patch files untuk distribute
- Support format: XDelta, IPS, JSON

**Class: PatchBuilder**
```python
class PatchBuilder:
    def create_xdelta_patch(
        original_rom: str,
        modified_rom: str,
        output_path: str
    ) -> bool
    
    def create_ips_patch(
        original_rom: str,
        modified_rom: str,
        output_path: str
    ) -> bool
    
    def create_json_patch(
        texts: list,
        output_path: str
    ) -> bool
    
    def apply_patch(
        original_rom: str,
        patch_file: str,
        output_rom: str
    ) -> bool
```

**Patch Formats:**

| Format | Size | Support ROM Size Change | Complexity |
|--------|------|-------------------------|------------|
| XDelta | Kecil | ✅ Ya | Medium |
| IPS | Sedang | ❌ Tidak | Simple |
| JSON | Besar | N/A (text only) | Very Simple |

---

### 2. Translation Engine

#### Base Translator (`translators/base_translator.py`)

**Interface untuk semua translation providers:**

```python
class BaseTranslator(ABC):
    @abstractmethod
    def translate(text, source_lang, target_lang) -> str
    
    @abstractmethod
    def translate_batch(texts, source_lang, target_lang) -> List[str]
    
    @abstractmethod
    def initialize() -> bool
    
    @abstractmethod
    def is_available() -> bool
    
    # Utility methods
    def translate_safe(text, source_lang, target_lang) -> str
    def get_stats() -> Dict
```

---

#### G4F Translator (`translators/g4f_translator.py`)

**ChatGPT gratis tanpa API key:**

```python
class G4FTranslator(BaseTranslator):
    def __init__(model="gpt-3.5-turbo"):
        self.model = model
        self.max_retries = 3
        self.timeout = 30
        self.batch_size = 50
    
    def translate(text, source_lang, target_lang):
        # Build prompt
        prompt = f"Translate {source_lang} to {target_lang}: {text}"
        
        # Call G4F dengan retry
        for attempt in range(max_retries):
            response = g4f.ChatCompletion.create(...)
            if response: return response
```

**Batch Translation:**
- Join semua teks dengan delimiter
- Translate sekali request
- Parse response ke list

---

#### Ollama Translator (`translators/ollama_translator.py`)

**Local LLM - 100% offline:**

```python
class OllamaTranslator(BaseTranslator):
    def __init__(model="llama3.2:1b", host="http://localhost:11434"):
        self.model = model
        self.host = host
    
    def translate(text, source_lang, target_lang):
        # Call Ollama API
        response = requests.post(f"{host}/api/generate", json={
            "model": model,
            "prompt": f"Translate to {target_lang}: {text}",
            "stream": False
        })
        return response.json()["response"]
```

**Setup Ollama:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:1b
```

---

#### HuggingFace Translator (`translators/hf_translator.py`)

**Free API - 30k tokens/hari:**

```python
class HFTranslator(BaseTranslator):
    def __init__(model="Helsinki-NLP/opus-mt-ja-id"):
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    def translate(text, source_lang, target_lang):
        response = requests.post(api_url, json={
            "inputs": text,
            "parameters": {"src_lang": "ja", "trg_lang": "id"}
        })
        return response.json()[0]["translation_text"]
```

---

#### Cache System (`translators/cache.py`)

**JSON-based persistent cache dengan TTL:**

```python
class TranslationCache:
    def __init__(cache_file, max_size, ttl, enabled):
        self._cache: Dict[str, dict] = {}  # hash -> {text, translation, timestamp}
    
    def get(text, source_lang, target_lang) -> Optional[str]
    def set(text, translation, source_lang, target_lang)
    def has(text, source_lang, target_lang) -> bool
    def clear()
    def get_stats() -> Dict
    def flush()  # Save ke disk
```

**Cache Key:**
```python
key = md5(f"{source_lang}:{target_lang}:{text}")
```

**TTL (Time To Live):**
- Default: 7 hari
- Entry expired = auto-delete
- Max size: 10,000 entries

---

#### Queue Manager (`translators/queue_manager.py`)

**Auto-queue translation dengan fallback:**

```python
class QueueManager:
    def __init__(translators, cache, primary_provider, fallback_providers):
        self.queue: Queue = Queue()
        self.tasks: List[TranslationTask] = []
        self.is_running = False
        
        # Callbacks
        self.on_progress: Callable  # callback(progress, processed, total)
        self.on_complete: Callable  # callback(results)
        self.on_error: Callable     # callback(error)
    
    def add_texts(texts: List[str])
    def start()  # Start background thread
    def cancel()
    def get_progress() -> Dict
    def get_results() -> List[str]
```

**Flow:**
```
1. User add texts ke queue
2. QueueManager.start() → background thread
3. Untuk setiap text:
   a. Cek cache → hit? return cached
   b. Cache miss → translate dengan primary provider
   c. Primary gagal? → fallback providers
   d. Save result ke cache
   e. Callback on_progress
4. Semua selesai? → Callback on_complete
```

**Fallback Chain:**
```
G4F (primary)
  ↓ gagal
Ollama (fallback 1)
  ↓ gagal
HuggingFace (fallback 2)
  ↓ gagal
Return original text
```

---

### 3. GUI Components

#### Main Window (`gui/main_window.py`)

**Controller utama yang menghubungkan semua komponen:**

```python
class MainWindow(ctk.CTk):
    def __init__():
        # Core components
        self.rom_loader = ROMLoader()
        self.text_extractor = TextExtractor()
        self.text_injector = TextInjector()
        self.patch_builder = PatchBuilder()
        
        # Translation components
        self.cache = TranslationCache()
        self.translators = {...}
        self.queue_manager = QueueManager(...)
        
        # UI components
        self.rom_panel = ROMPanel(on_rom_loaded=...)
        self.text_panel = TextPanel(on_edit=...)
        self.progress_bar = ProgressBarWidget(...)
```

**Callbacks:**
- `on_rom_loaded` → Start auto-translate
- `on_translation_progress` → Update progress bar
- `on_translation_complete` → Update text table
- `on_text_edited` → Save edit ke memory

---

#### ROM Panel (`gui/rom_panel.py`)

**Panel untuk load ROM:**

```python
class ROMPanel(ctk.CTkFrame):
    def __init__(on_rom_loaded):
        self.on_rom_loaded = on_rom_loaded
        self.rom_loader = ROMLoader()
        self.text_extractor = TextExtractor()
    
    def _load_rom():
        # 1. File dialog
        # 2. Load ROM (background thread)
        # 3. Extract teks
        # 4. Callback on_rom_loaded(rom_info, texts)
```

**Threading:**
- ROM load di background thread (non-blocking)
- `after()` untuk update UI dari thread

---

#### Text Panel (`gui/text_panel.py`)

**Panel untuk tabel teks:**

```python
class TextPanel(ctk.CTkFrame):
    def __init__(on_edit, on_translate):
        self.text_table = TextTableWidget(on_edit=...)
        self.translate_btn = Button(command=on_translate)
```

---

#### Text Table Widget (`gui/widgets/text_table.py`)

**Tabel side-by-side:**

```python
class TextTableWidget(ctk.CTkFrame):
    def __init__(on_edit):
        self.search_box = Entry()  # Search
        self.filter_buttons = [...]  # All/Done/Pending
        self.scrollable_frame = ScrollableFrame()
    
    def load_entries(entries: List[TextEntry]):
        # Render tabel
        # Kolom kiri: Original text
        # Kolom kanan: Editable translation
    
    def _on_search():
        # Filter entries by search text
    
    def _set_filter(status):
        # Filter by status (all/translated/pending)
```

---

#### Progress Bar Widget (`gui/widgets/progress_bar.py`)

**Progress bar realtime:**

```python
class ProgressBarWidget(ctk.CTkFrame):
    def update_progress(progress, processed, total, status):
        # Update progress bar (0-100%)
        # Update percentage label
        # Update count label (processed/total)
        # Update status text
    
    def set_complete(success, failed, cached):
        # Set to 100%
        # Show summary
    
    def set_idle():
        # Reset to 0%
```

---

### 4. Utilities

#### Project Manager (`utils/project_manager.py`)

**Save/Load project:**

```python
class ProjectManager:
    def create_project(rom_info, texts, settings) -> Dict
    def save_project(file_path: str) -> bool
    def load_project(file_path: str) -> Optional[Dict]
    def update_texts(texts: List[TextEntry])
    def get_stats() -> Dict
    def merge_translated_texts(translated_texts: Dict[str, str])
```

**Project JSON Format:**
```json
{
  "version": "1.0",
  "app_version": "1.0.0",
  "created_at": "2026-04-13T...",
  "updated_at": "2026-04-13T...",
  "rom_info": {
    "file_path": "/path/to/rom.3ds",
    "game_title": "Game Title",
    "emulator_type": "3ds",
    "region": "JP"
  },
  "texts": [...],
  "settings": {...}
}
```

---

## 🔄 Data Flow

### Full Translation Flow

```
User clicks "Load ROM"
    ↓
ROMPanel._load_rom()
    ├─ File dialog → file_path
    ├─ ROMLoader.load_rom(file_path)
    │   └─ Return ROMInfo
    ├─ ROMLoader.read_rom_data()
    │   └─ Return bytes
    ├─ TextExtractor.extract_from_rom(rom_data, emulator_type)
    │   └─ Return List[TextEntry]
    └─ Callback: on_rom_loaded(rom_info, texts)
         ↓
MainWindow._on_rom_loaded()
    ├─ Update UI (ROM info, stats)
    ├─ Load texts ke TextPanel
    └─ If pending texts → _start_translation()
         ↓
_start_translation()
    ├─ QueueManager(translators, cache)
    ├─ Add pending texts ke queue
    ├─ Setup callbacks:
    │   ├─ on_progress → update progress bar
    │   ├─ on_complete → update text table
    │   └─ on_error → show error dialog
    └─ QueueManager.start()
         ↓
QueueManager._process_queue() [background thread]
    For each text:
    ├─ Cek cache → hit? use cached
    ├─ Cache miss → _translate_with_fallback()
    │   ├─ Try G4F
    │   ├─ G4F fail? Try Ollama
    │   ├─ Ollama fail? Try HuggingFace
    │   └─ All fail? Return original
    ├─ Save to cache
    ├─ Callback on_progress()
    └─ Callback on_complete()
         ↓
Main thread update UI
    ├─ Progress bar → 100%
    ├─ Text table → update all entries
    └─ Status label → "Translation complete"
```

---

## 📊 Concurrency Model

### Threading

```
Main Thread (GUI)
    ├─ Handle user input
    ├─ Update UI
    └─ Callbacks
    
Background Thread (Translation)
    ├─ Process queue
    ├─ Call translation APIs
    └─ Update shared state (thread-safe)
    
Shared State (with locks)
    ├─ Translation tasks
    ├─ Progress counters
    └─ Cache (auto thread-safe)
```

### Thread Safety

```python
class QueueManager:
    def __init__():
        self._lock = threading.Lock()
    
    def add_texts():
        with self._lock:
            # Thread-safe operations
```

---

## 🎨 Design Patterns

### Patterns yang Digunakan

| Pattern | Lokasi | Tujuan |
|---------|--------|--------|
| **Abstract Factory** | translators/base_translator.py | Interface untuk semua providers |
| **Strategy** | QueueManager fallback | Dynamic provider selection |
| **Observer** | Callbacks | Event-driven UI updates |
| **Singleton** | Cache, Logger | Shared instances |
| **Facade** | MainWindow | Simplify complex subsystem |
| **Template Method** | BaseTranslator | Define translation flow |

---

## 📈 Performance Optimization

### Cache

- **Hit Rate**: Target > 60% (teks sering ulang)
- **TTL**: 7 hari (balance freshness vs speed)
- **Max Size**: 10,000 entries (memory limit)

### Batch Translation

- **G4F**: 50 texts/request
- **Ollama**: 30 texts/request
- **HuggingFace**: 100 texts/request

### UI Responsiveness

- ROM load di background thread
- Translation di background thread
- UI update via `after()` (thread-safe)

---

## 🐛 Debugging

### Enable Verbose Logging

```python
# config.py
LOG_CONFIG = {
    "level": "DEBUG",  # Change from INFO
    ...
}
```

### Log Locations

- `data/logs/app.log` - Main log file
- Console output - Real-time logs

### Common Issues

| Issue | Log Pattern | Solution |
|-------|-------------|----------|
| ROM invalid | "File tidak ditemukan" | Check path |
| G4F error | "G4F translation attempt failed" | Fallback active |
| Cache error | "Error loading cache" | Clear cache |
| Thread error | "Exception in thread" | Check callbacks |

---

**End of Architecture Document**
