"""
Text Panel - Panel untuk menampilkan teks asli dan terjemahan
Dengan tabel side-by-side dan kontrol translation
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging
from typing import Optional, Callable, List

from gui.widgets.text_table import TextTableWidget
from core.text_extractor import TextEntry


class TextPanel(ctk.CTkFrame):
    """
    Panel untuk menampilkan teks dan terjemahan dengan fitur:
    - Tabel side-by-side (Original | Translation)
    - Tombol translate manual
    - Search & filter
    - Statistik teks
    """

    def __init__(
        self,
        master,
        on_edit: Optional[Callable] = None,
        on_translate: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.on_edit = on_edit
        self.on_translate = on_translate
        self.entries: List[TextEntry] = []

        self.logger = logging.getLogger(__name__)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_table()

    def _create_header(self):
        """Create header dengan tombol aksi"""
        header_frame = ctk.CTkFrame(self, height=45, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Teks & Terjemahan",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Action buttons
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        # Translate button
        self.translate_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Translate All",
            command=self._translate_all,
            width=130,
            height=32,
            fg_color="#8e44ad",
            hover_color="#7d3c98"
        )
        self.translate_btn.grid(row=0, column=0, padx=3)

        # Clear button
        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear",
            command=self._clear_table,
            width=90,
            height=32,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.clear_btn.grid(row=0, column=1, padx=3)

        # Stats label
        self.stats_label = ctk.CTkLabel(
            header_frame,
            text="0 texts",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.stats_label.grid(row=0, column=2, sticky="e", padx=(10, 0))

    def _create_table(self):
        """Create text table widget"""
        self.text_table = TextTableWidget(
            self,
            on_edit=self.on_edit
        )
        self.text_table.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    def load_entries(self, entries: List[TextEntry]):
        """Load entries ke tabel"""
        self.entries = entries
        self.text_table.load_entries(entries)
        self._update_stats()

        self.logger.info(f"Loaded {len(entries)} entries ke text panel")

    def update_entry_translation(self, entry: TextEntry):
        """Update translation untuk satu entry"""
        entry.is_translated = True
        self.text_table.update_entry(entry)
        self._update_stats()

    def _translate_all(self):
        """Translate semua teks yang belum diterjemahkan"""
        pending = self.text_table.get_pending_entries()

        if not pending:
            messagebox.showinfo("Info", "Semua teks sudah diterjemahkan!")
            return

        count = len(pending)
        self.logger.info(f"Translating {count} pending texts")

        # Callback ke main window untuk start translation
        if self.on_translate:
            self.on_translate()
        else:
            messagebox.showinfo(
                "Info",
                f"Akan menerjemahkan {count} teks."
            )

    def _clear_table(self):
        """Clear semua teks dari tabel"""
        if not self.entries:
            return

        if messagebox.askyesno("Konfirmasi", "Hapus semua teks dari tabel?"):
            self.entries = []
            self.text_table.load_entries([])
            self._update_stats()
            self.logger.info("Text table cleared")

    def _update_stats(self):
        """Update statistik teks"""
        stats = self.text_table.get_stats()
        text = f"{stats['total']} teks ({stats['translated']} ✓, {stats['pending']} ○)"
        self.stats_label.configure(text=text)

    def get_all_entries(self) -> List[TextEntry]:
        """Get semua entries"""
        return self.text_table.get_all_entries()

    def get_translated_entries(self) -> List[TextEntry]:
        """Get entries yang sudah diterjemahkan"""
        return self.text_table.get_translated_entries()

    def get_pending_entries(self) -> List[TextEntry]:
        """Get entries yang belum diterjemahkan"""
        return self.text_table.get_pending_entries()
