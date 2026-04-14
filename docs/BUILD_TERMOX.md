# 📱 Panduan Build APK di Termux

Panduan lengkap untuk build Emulator Game Translator APK langsung di Android menggunakan Termux.

---

## ⚡ Quick Start (TL;DR)

```bash
# 1. Install Termux dari F-Droid
# https://f-droid.org/packages/com.termux/

# 2. Buka Termux dan run:
pkg update && pkg upgrade
pkg install python rust clang make cmake git wget
pip install buildozer cython

# 3. Setup storage
termux-setup-storage

# 4. Copy project
cp -r /storage/emulated/0/projek/translator-game-emulator ~
cd ~/translator-game-emulator/build

# 5. Build APK!
buildozer android debug

# 6. APK akan ada di:
ls -lh bin/*.apk
```

---

## 📋 Langkah Detail

### Step 1: Install Termux

**PENTING:** Install dari F-Droid, BUKAN dari Play Store (versi Play Store sudah outdated)

1. Buka https://f-droid.org/packages/com.termux/
2. Download dan install APK Termux
3. Buka aplikasi Termux

### Step 2: Install Dependencies

```bash
# Update package list
pkg update && pkg upgrade -y

# Install build tools
pkg install -y \
    python \
    rust \
    clang \
    make \
    cmake \
    git \
    wget \
    lld \
    pkg-config \
    jpeg-turbo \
    libffi \
    openssl \
    freetype \
    libpng \
    sdl2 \
    sdl2-image \
    sdl2-mixer \
    sdl2-ttf

# Install Python packages
pip install buildozer cython
```

### Step 3: Setup Storage Access

```bash
# Berikan akses ke storage Android
termux-setup-storage

# Klik "Allow" saat muncul prompt permission
```

### Step 4: Copy Project

```bash
# Copy project dari internal storage ke home Termux
cp -r /storage/emulated/0/projek/translator-game-emulator ~

# Masuk ke folder build
cd ~/translator-game-emulator/build
```

### Step 5: Build APK

```bash
# Jalankan build (pertama kali butuh waktu 20-40 menit)
buildozer android debug

# Atau dengan verbose logging
buildozer android debug --verbose
```

### Step 6: Install APK

Setelah build selesai:

```bash
# Cek APK
ls -lh bin/*.apk

# Install langsung via adb (jika sudah setup)
adb install bin/emulator_translator-*-debug.apk

# Atau copy ke Downloads dan install manual
cp bin/*.apk /storage/emulated/0/Download/
```

---

## ⚠️ Troubleshooting

### Error: `sdkmanager not found`

```bash
# Buildozer akan auto-download SDK, tapi jika error:
export ANDROID_SDK_ROOT=$HOME/.buildozer/android/platform/android-sdk
```

### Error: `aidl not found`

```bash
# AIDL sudah termasuk dalam Android SDK yang didownload buildozer
# Pastikan build tools terinstall
ls $HOME/.buildozer/android/platform/android-sdk/build-tools/
```

### Error: `java not found`

```bash
# Install OpenJDK di Termux
pkg install openjdk-17
```

### Build gagal di tengah jalan

```bash
# Clean dan build ulang
cd ~/translator-game-emulator/build
rm -rf .buildozer
buildozer android debug
```

### APK terlalu besar (>50MB)

```bash
# Edit buildozer.spec, ubah requirements
# Hapus yang tidak perlu:
requirements = python3,kivy,requests,Pillow
```

---

## 📊 Estimasi Waktu Build

| Tahap | Waktu | Data |
|-------|-------|------|
| Download SDK/NDK | 5-10 menit | ~1 GB |
| Download recipes | 3-5 menit | ~100 MB |
| Compile native libs | 10-15 menit | - |
| Build APK | 3-5 menit | - |
| **TOTAL** | **~25-35 menit** | **~1.1 GB** |

---

## ✅ Checklist Sebelum Build

- [ ] Termux install dari F-Droid
- [ ] Semua dependencies terinstall
- [ ] `termux-setup-storage` sudah dijalankan
- [ ] Project sudah di-copy ke home Termux
- [ ] Koneksi internet stabil (untuk download SDK)
- [ ] Baterai cukup / sambil charge (build butuh 30+ menit)
- [ ] Storage cukup (minimal 3GB free)

---

## 🎯 Setelah Build Berhasil

1. **Test APK di device:**
   ```bash
   # Install
   adb install bin/emulator_translator-*-debug.apk
   
   # Atau install manual:
   # 1. Buka File Manager
   # 2. Ke folder Download
   # 3. Tap APK file
   # 4. Install (allow unknown sources jika diminta)
   ```

2. **Test ROM:**
   - Buka app
   - Load ROM game (.3ds)
   - Lihat auto-translate berjalan
   - Export patch atau inject ke ROM

3. **Share ke teman:**
   - Copy APK ke device lain
   - Atau upload ke cloud storage

---

## 💡 Tips

### Build Lebih Cepat
- Close semua app lain saat build
- Pastikan device tidak panas
- Build di malam hari (internet lebih cepat)

### Hemat Data
- SDK/NDK hanya didownload sekali
- Build berikutnya lebih cepat (cache)
- Pakai WiFi, bukan data seluler

### Debug Build
```bash
# Lihat log lengkap
cat ~/.buildozer/android/platform/build-*/logs/*.log

# Build dengan debug symbols
buildozer android debug --verbose
```

---

## 📞 Support

Jika ada masalah:
1. Cek log: `~/.buildozer/android/platform/build-*/logs/`
2. Cek issue di GitHub project
3. Report bug dengan log lengkap

---

**Happy Building! 🚀**
