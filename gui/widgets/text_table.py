"""
Text Table Widget - Tabel untuk menampilkan teks asli dan terjemahan
Side-by-side view dengan fitur edit, search, dan filter
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import List, Dict, Optional, Callable
from core.text_extractor import TextEntry


class TextTableWidget(ctk.CTkFrame):
    """
    Tabel untuk menampilkan teks asli dan terjemahan dengan fitur:
    - Side-by-side view (Original | Translation)
    - Editable translation cells
    - Search & filter
    - Status indicators (translated, pending, needs review)
    - Scrollable
    """

    def __init__(
        self,
        master,
        on_edit: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.on_edit = on_edit
        self.entries: List[TextEntry] = []
        self.filtered_entries: List[TextEntry] = []
        self.filter_text = ""
        self.filter_status = "all"  # all, translated, pending, needs_review

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === Header/Search Bar ===
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Search box
        self.search_box = ctk.CTkEntry(
            header_frame,
            placeholder_text="🔍 Search teks asli...",
            width=300,
            height=30
        )
        self.search_box.grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.search_box.bind("<KeyRelease>", self._on_search)

        # Filter dropdown (simplified with buttons)
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=1, sticky="e")

        self.filter_btn_all = ctk.CTkButton(
            filter_frame, text="All", width=60, height=28,
            fg_color="#2b8ada", command=lambda: self._set_filter("all")
        )
        self.filter_btn_all.grid(row=0, column=0, padx=2)

        self.filter_btn_translated = ctk.CTkButton(
            filter_frame, text="✓ Done", width=70, height=28,
            fg_color="gray", command=lambda: self._set_filter("translated")
        )
        self.filter_btn_translated.grid(row=0, column=1, padx=2)

        self.filter_btn_pending = ctk.CTkButton(
            filter_frame, text="○ Pending", width=75, height=28,
            fg_color="gray", command=lambda: self._set_filter("pending")
        )
        self.filter_btn_pending.grid(row=0, column=2, padx=2)

        # Stats label
        self.stats_label = ctk.CTkLabel(
            header_frame,
            text="0 texts",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.stats_label.grid(row=0, column=2, padx=(10, 0), sticky="e")

        # === Scrollable Table ===
        self.scrollable_frame = ctk.CTkScrollableFrame(self, height=500)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.scrollable_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # Table header
        header_original = ctk.CTkLabel(
            self.scrollable_frame,
            text="Teks Asli",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        header_original.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        header_translated = ctk.CTkLabel(
            self.scrollable_frame,
            text="Terjemahan",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        header_translated.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Separator line
        separator = ctk.CTkFrame(self.scrollable_frame, height=2, fg_color="#2b8ada")
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Table content (start at row 2)
        self.table_start_row = 2

    def load_entries(self, entries: List[TextEntry]):
        """Load teks entries ke tabel"""
        self.entries = entries
        self._apply_filters()

    def _apply_filters(self):
        """Apply filter dan render tabel"""
        # Filter entries
        self.filtered_entries = []

        for entry in self.entries:
            # Filter by status
            if self.filter_status == "translated" and not entry.is_translated:
                continue
            if self.filter_status == "pending" and entry.is_translated:
                continue

            # Filter by search text
            if self.filter_text:
                search_lower = self.filter_text.lower()
                if search_lower not in entry.original_text.lower():
                    if entry.translated_text and search_lower not in entry.translated_text.lower():
                        continue

            self.filtered_entries.append(entry)

        # Render
        self._render_table()

        # Update stats
        total = len(self.entries)
        shown = len(self.filtered_entries)
        translated = sum(1 for e in self.entries if e.is_translated)

        if self.filter_text or self.filter_status != "all":
            self.stats_label.configure(text=f"Showing {shown}/{total} ({translated} translated)")
        else:
            self.stats_label.configure(text=f"{total} texts ({translated} translated)")

    def _render_table(self):
        """Render tabel dari filtered_entries"""
        # Clear existing rows
        for widget in self.scrollable_frame.winfo_children():
            grid_info = widget.grid_info()
            if grid_info.get("row", 0) >= self.table_start_row:
                widget.destroy()

        # Render entries
        for idx, entry in enumerate(self.filtered_entries):
            row = self.table_start_row + idx

            # Status indicator + original text
            status_icon = "✓" if entry.is_translated else "○"
            status_color = "#27ae60" if entry.is_translated else "#95a5a6"

            status_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=status_icon,
                text_color=status_color,
                width=20,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            status_label.grid(row=row, column=0, padx=(5, 0), pady=3, sticky="w")

            original_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=entry.original_text,
                font=ctk.CTkFont(size=12),
                wraplength=400,
                anchor="w"
            )
            original_label.grid(row=row, column=0, padx=(25, 5), pady=3, sticky="w")

            # Translation entry (editable)
            if entry.is_translated and entry.translated_text:
                trans_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
                trans_frame.grid_columnconfigure(0, weight=1)
                trans_frame.grid(row=row, column=1, padx=5, pady=3, sticky="ew")

                trans_entry = ctk.CTkEntry(
                    trans_frame,
                    height=30,
                    corner_radius=6
                )
                trans_entry.insert(0, entry.translated_text)
                trans_entry.pack(fill="x", expand=True)

                # Bind edit event
                if self.on_edit:
                    trans_entry.bind("<FocusOut>", lambda e, ent=entry, w=trans_entry: self._on_edit_complete(ent, w.get()))

                if entry.needs_review:
                    trans_entry.configure(border_color="#f39c12", border_width=2)
            else:
                pending_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text="Belum diterjemahkan...",
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                    anchor="w"
                )
                pending_label.grid(row=row, column=1, padx=5, pady=3, sticky="w")

    def _on_search(self, event=None):
        """Handle search input"""
        self.filter_text = self.search_box.get()
        self._apply_filters()

    def _set_filter(self, status: str):
        """Set filter status"""
        self.filter_status = status

        # Update button colors
        colors = {
            "all": self.filter_btn_all,
            "translated": self.filter_btn_translated,
            "pending": self.filter_btn_pending,
        }

        for key, btn in colors.items():
            if key == status:
                btn.configure(fg_color="#2b8ada")
            else:
                btn.configure(fg_color="gray")

        self._apply_filters()

    def _on_edit_complete(self, entry: TextEntry, new_text: str):
        """Handle saat user selesai edit terjemahan"""
        old_text = entry.translated_text
        entry.translated_text = new_text
        entry.needs_review = True

        if self.on_edit:
            self.on_edit(entry, old_text, new_text)

    def update_entry(self, entry: TextEntry):
        """Update satu entry di tabel"""
        entry.is_translated = True
        self._apply_filters()

    def get_all_entries(self) -> List[TextEntry]:
        """Get semua entries"""
        return self.entries

    def get_translated_entries(self) -> List[TextEntry]:
        """Get entries yang sudah diterjemahkan"""
        return [e for e in self.entries if e.is_translated]

    def get_pending_entries(self) -> List[TextEntry]:
        """Get entries yang belum diterjemahkan"""
        return [e for e in self.entries if not e.is_translated]

    def get_stats(self) -> Dict:
        """Get statistik tabel"""
        total = len(self.entries)
        translated = sum(1 for e in self.entries if e.is_translated)
        pending = total - translated
        needs_review = sum(1 for e in self.entries if e.needs_review)

        return {
            "total": total,
            "translated": translated,
            "pending": pending,
            "needs_review": needs_review,
        }
