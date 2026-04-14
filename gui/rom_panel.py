"""
ROM Panel - Panel untuk load dan menampilkan informasi ROM
Dengan auto-extract teks setelah ROM di-load
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import os

from core.rom_loader import ROMLoader, ROMInfo
from core.text_extractor import TextExtractor
from config import ROM_CONFIG


class ROMPanel(ctk.CTkFrame):
    """
    Panel untuk load ROM dengan fitur:
    - File picker untuk pilih ROM
    - Validasi format ROM
    - Menampilkan info game (judul, region, emulator)
    - Auto-extract teks setelah load
    """

    def __init__(self, master, on_rom_loaded=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_rom_loaded = on_rom_loaded
        self.rom_loader = ROMLoader()
        self.text_extractor = TextExtractor()
        self.current_rom_info: ROMInfo = None
        self.extracted_texts = []

        self.logger = logging.getLogger(__name__)

        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        """Create semua widgets di panel"""
        # Load ROM button
        self.load_btn = ctk.CTkButton(
            self,
            text="📂 Load ROM",
            command=self._load_rom,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2b8ada",
            hover_color="#1e6bb8"
        )
        self.load_btn.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # File path label
        self.file_path_label = ctk.CTkLabel(
            self,
            text="Belum ada ROM yang dipilih",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        self.file_path_label.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # ROM Info frame
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid_columnconfigure(1, weight=1)
        info_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        # Game title
        self.title_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Emulator type badge
        self.emulator_badge = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            width=60,
            height=22,
            corner_radius=11,
            fg_color="#3498db",
            text_color="white"
        )
        self.emulator_badge.grid(row=0, column=1, sticky="w", padx=5)

        # Region badge
        self.region_badge = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            width=50,
            height=22,
            corner_radius=11,
            fg_color="#e74c3c",
            text_color="white"
        )
        self.region_badge.grid(row=0, column=2, sticky="w", padx=5)

        # File size label
        self.size_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="e"
        )
        self.size_label.grid(row=0, column=3, sticky="e", padx=(10, 0))

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#27ae60",
            anchor="w"
        )
        self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="w")

    def _load_rom(self):
        """Open file dialog, load ROM, dan auto-extract teks"""
        # File dialog
        filetypes = []

        for fmt in ROM_CONFIG["supported_formats"]:
            ext = fmt.replace(".", "").upper()
            filetypes.append((f"{ext} ROM", f"*{fmt}"))

        filetypes.append(("All Files", "*.*"))

        file_path = filedialog.askopenfilename(
            title="Pilih ROM File",
            filetypes=filetypes
        )

        if not file_path:
            return

        self.logger.info(f"Loading ROM: {file_path}")

        # Update UI - loading state
        self.file_path_label.configure(text=file_path)
        self.status_label.configure(text="⏳ Loading ROM...", text_color="gray")
        self.load_btn.configure(state="disabled")

        # Load ROM dalam thread untuk avoid blocking UI
        self.after(100, lambda: self._load_rom_thread(file_path))

    def _load_rom_thread(self, file_path):
        """Load ROM di background"""
        try:
            rom_info = self.rom_loader.load_rom(file_path)

            if not rom_info.is_valid:
                self.after(0, lambda: self._load_failed(rom_info.error_message))
                return

            # Success
            self.current_rom_info = rom_info

            # Extract teks
            self.after(0, lambda: self._extract_texts(rom_info))

        except Exception as e:
            self.logger.error(f"Error loading ROM: {e}", exc_info=True)
            self.after(0, lambda: self._load_failed(str(e)))

    def _extract_texts(self, rom_info):
        """Extract teks dari ROM"""
        self.status_label.configure(text="🔍 Extracting teks dari ROM...", text_color="#f39c12")

        try:
            # Baca ROM data
            rom_data = self.rom_loader.read_rom_data()

            # Extract teks
            self.extracted_texts = self.text_extractor.extract_from_rom(
                rom_data,
                rom_info.emulator_type
            )

            # Filter teks yang terlalu pendek
            self.text_extractor.filter_texts(min_length=3)
            self.extracted_texts = self.text_extractor.extracted_texts

            # Update UI
            self.after(0, lambda: self._on_rom_loaded_success(rom_info, self.extracted_texts))

        except Exception as e:
            self.logger.error(f"Error extracting texts: {e}", exc_info=True)
            self.after(0, lambda: self._load_failed(f"Gagal extract teks: {str(e)}"))

    def _on_rom_loaded_success(self, rom_info, extracted_texts):
        """Handle setelah ROM dan teks berhasil di-load"""
        self._display_rom_info(rom_info)

        stats = self.text_extractor.get_stats()
        self.status_label.configure(
            text=f"✓ ROM loaded: {rom_info.game_title} - {stats['total_texts']} teks diekstrak",
            text_color="#27ae60"
        )

        self.load_btn.configure(state="normal")

        self.logger.info(
            f"ROM loaded: {rom_info}, "
            f"{stats['total_texts']} texts extracted"
        )

        # Callback dengan rom_info dan extracted_texts
        if self.on_rom_loaded:
            self.on_rom_loaded(rom_info, extracted_texts)

    def _load_failed(self, error_message):
        """Handle ROM load failed"""
        messagebox.showerror(
            "Error",
            f"Gagal load ROM:\n{error_message}"
        )
        self.status_label.configure(text=f"❌ Error: {error_message}", text_color="#e74c3c")
        self.load_btn.configure(state="normal")

    def _display_rom_info(self, rom_info: ROMInfo):
        """Tampilkan informasi ROM"""
        self.file_path_label.configure(text=rom_info.file_path)
        self.title_label.configure(text=rom_info.game_title)

        emulator_text = rom_info.emulator_type.upper()
        self.emulator_badge.configure(text=emulator_text)

        region_text = rom_info.region if rom_info.region != "unknown" else "?"
        self.region_badge.configure(text=region_text)

        size_mb = rom_info.file_size / (1024 * 1024)
        self.size_label.configure(text=f"{size_mb:.2f} MB")

    def get_extracted_texts(self):
        """Get teks yang sudah diekstrak dari ROM"""
        return self.extracted_texts

    def has_rom(self) -> bool:
        """Cek apakah ada ROM yang di-load"""
        return self.current_rom_info is not None
