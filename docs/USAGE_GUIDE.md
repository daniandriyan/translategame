# Panduan Penggunaan - Emulator Game Translator

Dokumen ini menjelaskan cara menggunakan aplikasi secara detail.

---

## 📱 Desktop App (CustomTkinter)

### Launch Aplikasi

```bash
cd /path/to/translator-game-emulator
python main.py
```

### Langkah 1: Load ROM

1. Klik tombol **"📂 Load ROM"** di panel atas
2. File dialog akan muncul
3. Pilih file ROM game (`.3ds`, `.nds`, `.gba`, `.iso`, `.cso`)
4. Klik **"Open"**

**Setelah ROM di-load:**
- Aplikasi menampilkan:
  - Nama game
  - Tipe emulator (3DS/NDS/GBA/PSP)
  - Region (JP/US/EU)
  - Ukuran file
  - Jumlah teks yang diekstrak

**Contoh:**
```
Game: Story of Seasons - Trio of Towns
Emulator: 3DS
Region: US
Size: 1,234.56 MB
Texts: 1,234 diekstrak
```

### Langkah 2: Auto-Translate

Setelah ROM berhasil di-load:
- Aplikasi **otomatis memulai translation**
- Progress bar menampilkan:
  - Persentase progress (0-100%)
  - Jumlah teks yang sudah diterjemahkan
  - Status (Translating... / Selesai / Error)

**Progress Bar Colors:**
- 🟦 Biru = Sedang_translate
- 🟩 Hijau = Selesai
- 🟥 Merah = Error

**Tombol Cancel:**
- Muncul saat translation berjalan
- Klik untuk cancel di tengah proses

### Langkah 3: Review Hasil

Setelah translate selesai:
- Tabel menampilkan 2 kolom:
  - **Kiri**: Teks asli (Jepang/Inggris)
  - **Kanan**: Terjemahan (Indonesia)

**Status Indicator:**
- ✅ = Sudah diterjemahkan
- ○ = Belum diterjemahkan

**Search & Filter:**
- Ketik di kotak search untuk cari teks
- Klik tombol filter:
  - **All** = Tampilkan semua
  - **✓ Done** = Hanya yang sudah diterjemahkan
  - **○ Pending** = Hanya yang belum diterjemahkan

**Edit Manual:**
- Klik di kolom terjemahan
- Edit teks sesuai keinginan
- Tekan Enter atau klik di luar untuk save

### Langkah 4: Export

#### Opsi A: Export Patch (JSON)

1. Klik **"💾 Export Patch"**
2. Pilih lokasi save
3. Pilih format **JSON**
4. File patch akan berisi:
   - Teks asli
   - Terjemahan
   - Offset di ROM

**Contoh JSON:**
```json
{
  "version": "1.0",
  "type": "translation_patch",
  "texts": [
    {
      "original": "こんにちは",
      "translated": "Halo",
      "offset": 12345
    }
  ]
}
```

#### Opsi B: Inject to ROM

1. Klik **"🔧 Inject to ROM"**
2. Pilih lokasi save ROM baru
3. Aplikasi akan:
   - Baca ROM asli
   - Inject teks terjemahan
   - Save sebagai ROM baru

**Peringatan:**
- ROM asli tidak dimodifikasi
- ROM baru bisa lebih besar/kecil
- Backup ROM asli dulu!

#### Opsi C: Save Project

1. Klik **"📁 Save Project"**
2. Pilih lokasi save (format JSON)
3. File project berisi:
   - Info ROM
   - Semua teks + terjemahan
   - Settings

**Load Project:**
- Buka Settings → Load Project
- Pilih file JSON
- Progress akan dilanjutkan

### Langkah 5: Settings

Klik **"⚙️ Settings"** di kanan atas untuk:
- Ubah translation provider
- Set target bahasa
- Configure cache
- Ubah theme GUI

---

## 📂 Manajemen File

### Folder Structure Setelah Pakai

```
translator-game-emulator/
├── data/
│   ├── cache/
│   │   └── translation_cache.json    # Cache terjemahan
│   ├── logs/
│   │   └── app.log                   # Log aplikasi
│   └── dictionaries/                 # Custom dictionary
└── output/                           # ROM modified & patch
    ├── Story of Seasons_translated.3ds
    └── Story of Seasons_patch.json
```

### Backup & Restore

**Backup Cache:**
```bash
cp data/cache/translation_cache.json backup/
```

**Clear Cache:**
```bash
rm data/cache/translation_cache.json
# Aplikasi akan buat cache baru
```

**Lihat Log:**
```bash
tail -f data/logs/app.log
```

---

## 🎮 Cara Pakai Hasil Terjemahan

### Di Emulator Citra (3DS)

#### Opsi 1: Pakai ROM Modified

1. Buka Citra emulator
2. Load ROM yang sudah di-inject
3. Game langsung dalam Bahasa Indonesia

#### Opsi 2: Pakai Patch

1. Install xdelta patcher
2. Apply patch ke ROM asli:
   ```bash
   xdelta patch game_patch.json game_original.3ds game_translated.3ds
   ```
3. Load `game_translated.3ds` di Citra

### Di Emulator Lain

- **DraStic (DS)**: Sama seperti Citra
- **PPSSPP (PSP)**: Load ROM modified
- **VisualBoy (GBA)**: Load ROM modified

---

## 💡 Tips & Tricks

### 1. Optimize Translation Speed

**Enable Cache:**
- Pastikan cache enabled di `config.py`
- Teks yang sama tidak perlu translate ulang

**Batch Size:**
- Naikkan `batch_size` untuk translate lebih cepat
- Default: 50, bisa dinaikkan ke 100

### 2. Hemat API Calls

**Gunakan Ollama:**
- Install Ollama untuk offline translation
- Tidak ada rate limit
- 100% gratis

**Custom Dictionary:**
- Tambahkan kata-kata sering dipakai ke dictionary
- Skip translate untuk kata khusus

### 3. Quality Terjemahan

**Edit Manual:**
- Selalu review hasil auto-translate
- Edit yang kurang pas konteksnya

**Fallback Provider:**
- Kalau G4F hasilnya kurang bagus, coba Ollama
- Setiap provider punya kekuatan beda

### 4. Performance

**Close Aplikasi Lain:**
- Translation butuh RAM & CPU
- Close browser/app lain saat translate

**ROM Size:**
- ROM besar (>1GB) butuh waktu extract lebih lama
- Sabar, prosesnya otomatis

---

## ❓ FAQ

### Q: ROM saya tidak ter-load. Kenapa?
A: Cek:
- Format ROM didukung? (.3ds, .nds, .gba, .iso)
- ROM tidak encrypted?
- File tidak corrupt?

### Q: Kenapa translation lama?
A: Kemungkinan:
- Koneksi internet lambat
- Rate limit dari G4F provider
- Teks yang banyak (>1000)

**Solusi:** Install Ollama untuk offline translation

### Q: Bisa translate game PS1/PS2?
A: Belum. Saat ini support:
- 3DS (.3ds)
- NDS (.nds)
- GBA (.gba)
- PSP (.iso/.cso)

PS1/PS2 dalam rencana future.

### Q: Hasil translate jelek, bisa improve?
A: Ya:
- Edit manual di tabel
- Coba provider lain (G4F → Ollama → HF)
- Tambahkan custom dictionary

### Q: APK Android kapan ready?
A: APK sedang dalam proses build. Cek `STATUS.md` untuk update.

---

## 📞 Support

Ada masalah?
- Baca log: `data/logs/app.log`
- Cek STATUS.md untuk known issues
- Report bug dengan sample ROM & log

---

**Happy Translating! 🎮🌏**
