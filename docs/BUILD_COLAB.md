# 📱 Panduan Build APK di Google Colab

Panduan lengkap untuk build Emulator Game Translator APK menggunakan Google Colab (gratis, cloud-based).

---

## ⚡ Kenapa Google Colab?

| Keuntungan | Keterangan |
|------------|------------|
| ✅ **Gratis** | GPU/CPU cloud, tidak butuh device kuat |
| ✅ **No Setup** | Tidak perlu install SDK/NDK/JDK lokal |
| ✅ **Cepat** | Build ~15-25 menit (tergantung size project) |
| ✅ **Access Anywhere** | Bisa akses dari browser mana saja |
| ✅ **Storage Cloud** | Langsung upload APK ke Google Drive |

---

## 🚀 Quick Start (TL;DR)

### Step 1: Buka Google Colab
1. Buka [Google Colab](https://colab.research.google.com/)
2. Klik **"New Notebook"**

### Step 2: Copy-Paste Semua Command di Bawah

#### Cell 1: Install Dependencies
```python
# Install Buildozer & Cython
!pip install buildozer cython==0.29.33

# Update & install system dependencies
!apt-get update
!apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    openjdk-17-jdk \
    autoconf \
    automake \
    libtool \
    libffi-dev \
    libssl-dev
```

#### Cell 2: Mount Google Drive & Copy Project
```python
# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Copy project dari Drive ke Colab (jika sudah ada di Drive)
# Atau upload langsung via UI Colab
!cp -r /content/drive/MyDrive/translator-game-emulator /content/
%cd /content/translator-game-emulator/build
```

#### Cell 3: Build APK!
```python
# Build APK (first time: ~20-30 minutes)
!buildozer android debug

# Atau dengan verbose
!buildozer android debug --verbose
```

#### Cell 4: Download APK
```python
# Cek APK yang sudah di-build
!ls -lh /content/translator-game-emulator/build/bin/*.apk

# Copy APK ke Google Drive (supaya tidak hilang)
!cp /content/translator-game-emulator/build/bin/*.apk /content/drive/MyDrive/

print("✅ Build selesai! APK sudah ada di Google Drive Anda.")
```

---

## 📋 Langkah Detail

### Step 1: Siapkan Project

**REKOMENDASI: Clone langsung dari GitHub (Paling Mudah!)**

Tidak perlu upload manual ke Google Drive. Cukup clone repository langsung di Colab:

```python
# Di Colab notebook - Clone repository
!git clone https://github.com/daniandriyan/translategame.git
%cd /content/translategame/build
```

**Keuntungan clone dari GitHub:**
- ✅ **Lebih cepat** - tidak perlu upload manual
- ✅ **Selalu update** - dapat versi terbaru
- ✅ **Tidak perlu Google Drive storage**
- ✅ **Siapa saja bisa build** - tinggal buka Colab & run

**Opsi Alternatif: Upload Manual ke Google Drive**

Jika ingin upload sendiri:
1. Buka [Google Drive](https://drive.google.com/)
2. Buat folder `translategame`
3. Upload seluruh folder project dari komputer lokal

> **Note:** Yang perlu di-upload hanya **source code**, bukan folder `build/.buildozer/` atau `build/bin/` (akan di-generate otomatis saat build).

### Step 2: Buka Google Colab

1. Buka [https://colab.research.google.com/](https://colab.research.google.com/)
2. Klik **"New Notebook"**
3. Beri nama: `Build APK - Emulator Translator`

### Step 3: Install Dependencies

Copy-paste command berikut ke **Cell 1**:

```python
# @title Install Dependencies
!pip install buildozer cython==0.29.33

!apt-get update
!apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    openjdk-17-jdk \
    autoconf \
    automake \
    libtool \
    libffi-dev \
    libssl-dev

print("✅ Dependencies installed successfully!")
```

**Jalankan Cell:** Klik tombol ▶️ di sebelah cell atau tekan `Ctrl+Enter`

### Step 4: Clone Project dari GitHub

Copy-paste ke **Cell 2**:

```python
# @title Clone Project dari GitHub
import os

# Clone repository langsung dari GitHub
!git clone https://github.com/daniandriyan/translategame.git

# Masuk ke folder build
%cd /content/translategame/build

# Verifikasi file buildozer.spec ada
!ls -la buildozer.spec
!ls -la main_kivy.py

print("✅ Project siap untuk build!")
```

**Jalankan Cell:** `Ctrl+Enter`

**Keuntungan clone dari GitHub:**
- ✅ Tidak perlu upload manual ke Google Drive
- ✅ Selalu dapat versi terbaru
- ✅ Tidak perlu storage Google Drive
- ✅ Siapapun bisa build tanpa setup ribet

**Opsi Alternatif: Mount Google Drive**

Jika project sudah ada di Drive Anda:

```python
# @title Mount Drive & Setup Project
from google.colab import drive
import os

# Mount Google Drive
drive.mount('/content/drive')

# Cek apakah project sudah ada di Drive
project_path = '/content/drive/MyDrive/translategame'
if os.path.exists(project_path):
    !cp -r $project_path /content/
    %cd /content/translategame/build
    print("✅ Project copied to Colab!")
else:
    print("⚠️ Project not found in Drive. Clone from GitHub instead!")
    print("📁 Path: /content/drive/MyDrive/translategame")

# Verify buildozer.spec exists
!ls -la buildozer.spec
```

**Jalankan Cell:** `Ctrl+Enter`

**Note:** Saat pertama kali, akan muncul link autentikasi Google Drive:
1. Klik link yang muncul
2. Login dengan akun Google Anda
3. Copy authorization code
4. Paste code di input box yang muncul

### Step 5: Build APK

Copy-paste ke **Cell 3**:

```python
# @title Build APK (Debug Mode)
import time

start_time = time.time()

# Pastikan di folder build yang benar
%cd /content/translategame/build

# Build APK
!buildozer android debug

elapsed = time.time() - start_time
print(f"\n✅ Build completed in {elapsed/60:.2f} minutes!")
```

**Jalankan Cell:** `Ctrl+Enter`

**Tunggu proses build selesai:**
- **Pertama kali:** 20-35 menit (download SDK/NDK + compile)
- **Build berikutnya:** 5-10 menit (cache)

**Output yang diharapkan:**
```
# Android packaging done!
# APK available at: bin/emulator_translator-1.0.0-debug.apk
```

### Step 6: Download APK

Copy-paste ke **Cell 4**:

```python
# @title Download APK
import glob
import os

# Find APK files
apk_files = glob.glob('/content/translategame/build/bin/*.apk')

if apk_files:
    print(f"✅ Found {len(apk_files)} APK file(s):\n")
    for apk in apk_files:
        size = os.path.getsize(apk) / (1024 * 1024)  # MB
        print(f"📱 {os.path.basename(apk)} ({size:.2f} MB)")

    # Copy APK to Google Drive (for permanent storage)
    !cp /content/translategame/build/bin/*.apk /content/drive/MyDrive/
    print("\n✅ APK copied to Google Drive!")
    print("📁 Location: /MyDrive/ in your Google Drive")
else:
    print("❌ No APK found. Check build logs for errors.")
```

**Jalankan Cell:** `Ctrl+Enter`

### Step 7: Download ke Device

**Opsi A: Dari Google Drive**
1. Buka Google Drive di HP Android
2. Download file APK
3. Install APK (allow "Unknown sources" jika diminta)

**Opsi B: Direct Download dari Colab**
```python
from google.colab import files
files.download('/content/translategame/build/bin/emulator_translator-1.0.0-debug.apk')
```

---

## 📊 Estimasi Waktu Build di Colab

| Tahap | Waktu | Keterangan |
|-------|-------|------------|
| Install dependencies | 2-3 menit | Pertama kali saja |
| Download SDK/NDK | 5-10 menit | Pertama kali saja |
| Download recipes | 3-5 menit | Pertama kali saja |
| Compile native libs | 5-10 menit | |
| Build APK | 3-5 menit | |
| **TOTAL (first time)** | **~18-33 menit** | |
| **TOTAL (subsequent)** | **~8-15 menit** | Cached |

---

## ⚠️ Troubleshooting

### Error: `ModuleNotFoundError: No module named 'buildozer'`

```python
# Pastikan install di cell pertama
!pip install buildozer cython==0.29.33
```

### Error: `sdkmanager not found`

```python
# Buildozer akan auto-download SDK
# Jika masih error, set environment variable
import os
os.environ['ANDROID_SDK_ROOT'] = '/root/.buildozer/android/platform/android-sdk'
```

### Error: `aidl not found`

```python
# Install build tools
!apt-get install -y android-tools-adb
```

### Error: `java not found`

```python
# Install OpenJDK
!apt-get install -y openjdk-17-jdk
!export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
```

### Build gagal di tengah jalan

```python
# Clean dan build ulang
%cd /content/translategame/build
!rm -rf .buildozer
!buildozer android debug
```

### Error: "Repository not found" atau "Clone failed"

```python
# Pastikan URL GitHub benar
!git clone https://github.com/daniandriyan/translategame.git

# Atau clone dengan verbose untuk lihat detail error
!git clone -v https://github.com/daniandriyan/translategame.git
```

### Colab Runtime Terputus

**Masalah:** Colab akan disconnect setelah 12 jam (free tier)

**Solusi:**
1. Build harus selesai dalam 12 jam
2. Jika terputus, cell yang sudah dijalankan tetap cached
3. Reconnect dan lanjutkan dari cell yang gagal

### APK terlalu besar (>50MB)

Edit `buildozer.spec`:
```python
# Edit requirements, hapus yang tidak perlu
requirements = python3,kivy,requests,Pillow
```

---

## 📝 Complete Notebook Template

Berikut template lengkap yang bisa langsung copy-paste ke Colab:

```python
# =============================================
# CELL 1: Install Dependencies
# =============================================
!pip install buildozer cython==0.29.33

!apt-get update
!apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    openjdk-17-jdk \
    autoconf \
    automake \
    libtool \
    libffi-dev \
    libssl-dev

print("✅ Dependencies installed!")

# =============================================
# CELL 2: Clone Project dari GitHub
# =============================================
import os

# Clone repository langsung dari GitHub (REKOMENDASI)
!git clone https://github.com/daniandriyan/translategame.git
%cd /content/translategame/build

# Verifikasi file penting ada
if os.path.exists('buildozer.spec'):
    print("✅ buildozer.spec found!")
else:
    print("❌ buildozer.spec NOT found!")

if os.path.exists('main_kivy.py'):
    print("✅ main_kivy.py found!")
else:
    print("❌ main_kivy.py NOT found!")

print("✅ Project ready to build!")

# =============================================
# CELL 3: Build APK
# =============================================
import time

start_time = time.time()

!buildozer android debug

elapsed = time.time() - start_time
print(f"\n✅ Build completed in {elapsed/60:.2f} minutes!")

# =============================================
# CELL 4: Download APK
# =============================================
import glob
import os

apk_files = glob.glob('/content/translategame/build/bin/*.apk')
if apk_files:
    for apk in apk_files:
        size = os.path.getsize(apk) / (1024 * 1024)
        print(f"📱 {os.path.basename(apk)} ({size:.2f} MB)")

    # Copy ke Google Drive
    !cp /content/translategame/build/bin/*.apk /content/drive/MyDrive/
    print("\n✅ APK saved to Google Drive!")
else:
    print("❌ Build failed or APK not found")
```

---

## 🎯 Setelah Build Berhasil

### 1. Test APK di Device

```bash
# Install via ADB (jika device terhubung)
adb install emulator_translator-*-debug.apk

# Atau install manual di HP Android:
# 1. Buka File Manager
# 2. Ke folder Download
# 3. Tap APK file
# 4. Install (allow "Unknown sources" jika diminta)
```

### 2. Test ROM

- Buka app
- Load ROM game (.3ds)
- Lihat auto-translate berjalan

### 3. Share APK

- Upload ke Google Drive
- Share link ke teman/komunitas

---

## 💡 Tips

### Optimize Build Time

**Gunakan Colab Pro (jika ada):**
- Runtime lebih lama (24 jam vs 12 jam)
- GPU/CPU lebih cepat
- Prioritas resource lebih tinggi

**Build di Waktu Off-Peak:**
- Pagi hari (2-6 AM WIB) - server lebih sepi
- Hindari jam sibuk (7-10 PM)

### Hemat Resource

**Close Tab Lain:**
- Colab free tier punya limit RAM/CPU
- Close tab browser yang tidak perlu

**Gunakan Fresh Runtime:**
- Jika runtime sudah lama running, restart:
  - Menu: `Runtime` → `Restart runtime`

### Persistent Storage

**Simpan .buildozer folder di Drive (opsional):**
```python
# Supaya build berikutnya lebih cepat (tidak perlu download ulang)
!cp -r /content/translategame/build/.buildozer /content/drive/MyDrive/

# Restore di build selanjutnya
!cp -r /content/drive/MyDrive/.buildozer /content/translategame/build/
```

> **Note:** Tidak wajib karena `.buildozer` tidak ada di repository. Buildozer akan download ulang saat build pertama kali.

---

## ✅ Checklist Sebelum Build

- [ ] Repository GitHub sudah ada ([github.com/daniandriyan/translategame](https://github.com/daniandriyan/translategame))
- [ ] Colab notebook sudah dibuat
- [ ] Cell 1 (Dependencies) sudah di-run
- [ ] Cell 2 (Clone Project) sudah di-run & verifikasi file ada
- [ ] Koneksi internet stabil
- [ ] Waktu cukup (30+ menit untuk pertama kali)

---

## 📂 Apa yang Ada di Repository?

**File yang DI-COMMIT ke GitHub:**
```
📁 translategame/
├── build/
│   ├── buildozer.spec   ✅ Konfigurasi build
│   └── main_kivy.py     ✅ Kivy app untuk Android
├── core/                ✅ ROM Loader, Extractor, Injector
├── translators/         ✅ G4F, Ollama, HuggingFace
├── gui/                 ✅ Desktop GUI
├── utils/               ✅ Utilities
├── docs/                ✅ Dokumentasi lengkap
├── main.py              ✅ Entry point desktop
├── config.py            ✅ Konfigurasi
└── requirements.txt     ✅ Dependencies
```

**File yang TIDAK DI-COMMIT (diabaikan .gitignore):**
```
❌ build/.buildozer/     ❌ Build artifacts (2GB+, di-generate saat build)
❌ build/bin/            ❌ Output APK (hasil build)
❌ build/build.log       ❌ Log file
❌ data/cache/           ❌ Cache files
❌ output/               ❌ Output files
```

> **Note:** Saat user run `buildozer android debug` di Colab, Buildozer akan otomatis generate semua artifacts yang diperlukan.

---

## 📞 Support

Jika ada masalah:
1. Cek log: `~/.buildozer/android/platform/build-*/logs/`
2. Cek issue di GitHub project
3. Report bug dengan log lengkap

---

**Happy Building! 🚀**

*Build APK di cloud, main game di Android!*

---

## 🔗 Links

- **Repository GitHub:** [github.com/daniandriyan/translategame](https://github.com/daniandriyan/translategame)
- **Panduan Termux (Android):** [BUILD_TERMOX.md](BUILD_TERMOX.md)
- **Usage Guide:** [USAGE_GUIDE.md](USAGE_GUIDE.md)
- **Architecture Docs:** [ARCHITECTURE.md](ARCHITECTURE.md)
