"""
Main Window - Window utama aplikasi Emulator Game Translator
CustomTkinter GUI dengan integrasi penuh ke semua komponen
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import threading
import os

from config import GUI_CONFIG, APP_INFO, TRANSLATION_CONFIG
from gui.rom_panel import ROMPanel
from gui.text_panel import TextPanel
from gui.settings_panel import SettingsPanel
from gui.widgets.progress_bar import ProgressBarWidget
from gui.widgets.text_table import TextTableWidget

from core.rom_loader import ROMLoader, ROMInfo
from core.text_extractor import TextExtractor
from core.text_injector import TextInjector
from core.patch_builder import PatchBuilder

from translators.g4f_translator import G4FTranslator
from translators.ollama_translator import OllamaTranslator
from translators.hf_translator import HFTranslator
from translators.cache import TranslationCache
from translators.queue_manager import QueueManager

from utils.project_manager import ProjectManager


class MainWindow(ctk.CTk):
    """
    Main application window dengan integrasi penuh:
    ┌──────────────────────────────────────────────┐
    │  [Header] Emulator Game Translator    [⚙️]   │
    ├──────────────────────────────────────────────┤
    │  [ROM Panel] Load ROM info                   │
    ├──────────────────────────────────────────────┤
    │  [Progress Bar] Status & progress            │
    ├──────────────────────────────────────────────┤
    │  [Text Panel] Tabel teks & terjemahan        │
    ├──────────────────────────────────────────────┤
    │  [Action Buttons] Export, Save, dll          │
    └──────────────────────────────────────────────┘
    """

    def __init__(self):
        super().__init__()

        self.logger = logging.getLogger(__name__)

        # State
        self.rom_loaded = False
        self.translation_running = False
        self.current_rom_info: ROMInfo = None
        self.extracted_texts = []

        # Core components
        self.rom_loader = ROMLoader()
        self.text_extractor = TextExtractor()
        self.text_injector = TextInjector()
        self.patch_builder = PatchBuilder()
        self.project_manager = ProjectManager()

        # Translation components
        self.cache = TranslationCache()
        self.translators = {}
        self.queue_manager = None

        # Setup window
        self._setup_window()

        # Initialize translators
        self._init_translators()

        # Create UI components
        self._create_header()
        self._create_rom_panel()
        self._create_progress_bar()
        self._create_text_panel()
        self._create_action_bar()

        self.logger.info("Main window initialized with all components")

    def _setup_window(self):
        """Setup window properties"""
        width, height = GUI_CONFIG["window_size"]
        self.geometry(f"{width}x{height}")
        self.title(f"{APP_INFO['name']} v{APP_INFO['version']}")

        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Theme
        ctk.set_appearance_mode(GUI_CONFIG["theme"])
        ctk.set_default_color_theme(GUI_CONFIG["color_theme"])

        # Protocol
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_translators(self):
        """Initialize semua translation providers"""
        self.logger.info("Initializing translators...")

        # Primary translator
        primary = TRANSLATION_CONFIG["primary_provider"]

        if primary == "g4f":
            self.translators["g4f"] = G4FTranslator()
        elif primary == "ollama":
            self.translators["ollama"] = OllamaTranslator()
        elif primary == "huggingface":
            self.translators["huggingface"] = HFTranslator()

        # Fallback translators
        for provider in TRANSLATION_CONFIG["fallback_providers"]:
            if provider not in self.translators:
                if provider == "g4f":
                    self.translators["g4f"] = G4FTranslator()
                elif provider == "ollama":
                    self.translators["ollama"] = OllamaTranslator()
                elif provider == "huggingface":
                    self.translators["huggingface"] = HFTranslator()

        self.logger.info(f"Translators initialized: {list(self.translators.keys())}")

    def _create_header(self):
        """Create header bar"""
        header = ctk.CTkFrame(self, height=50, fg_color="#1a1a2e")
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header,
            text=f"🎮 {APP_INFO['name']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(side="left", padx=15, pady=10)

        version_label = ctk.CTkLabel(
            header,
            text=f"v{APP_INFO['version']}",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        version_label.pack(side="left", padx=(0, 10))

        settings_btn = ctk.CTkButton(
            header,
            text="⚙️ Settings",
            command=self._open_settings,
            width=100,
            height=30,
            fg_color="#2b8ada",
            hover_color="#1e6bb8"
        )
        settings_btn.pack(side="right", padx=15, pady=10)

    def _create_rom_panel(self):
        """Create ROM load panel dengan callback"""
        self.rom_panel = ROMPanel(
            self,
            on_rom_loaded=self._on_rom_loaded
        )
        self.rom_panel.pack(fill="x", padx=10, pady=(10, 5))

    def _create_progress_bar(self):
        """Create progress bar widget"""
        self.progress_bar = ProgressBarWidget(
            self,
            title="Translation Progress",
            show_cancel=True,
            on_cancel=self._cancel_translation
        )
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.pack_forget()  # Hide initially

    def _create_text_panel(self):
        """Create text panel untuk tabel teks"""
        self.text_panel = TextPanel(
            self,
            on_edit=self._on_text_edited,
            on_translate=self._start_translation
        )
        self.text_panel.pack(fill="both", expand=True, padx=10, pady=5)
        self.text_panel.pack_forget()  # Hide initially

    def _create_action_bar(self):
        """Create action buttons bar"""
        action_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(5, 10), side="bottom")
        action_frame.pack_propagate(False)

        # Status label
        self.status_label = ctk.CTkLabel(
            action_frame,
            text="💡 Load ROM untuk memulai",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=10)

        # Spacer
        ctk.CTkFrame(action_frame, width=20, height=1, fg_color="transparent").pack(side="left", fill="x", expand=True)

        # Export button
        self.export_btn = ctk.CTkButton(
            action_frame,
            text="💾 Export Patch",
            command=self._export_patch,
            state="disabled",
            width=130,
            height=35,
            fg_color="#27ae60",
            hover_color="#219653"
        )
        self.export_btn.pack(side="right", padx=5)

        # Inject button
        self.inject_btn = ctk.CTkButton(
            action_frame,
            text="🔧 Inject to ROM",
            command=self._inject_to_rom,
            state="disabled",
            width=130,
            height=35,
            fg_color="#e67e22",
            hover_color="#d35400"
        )
        self.inject_btn.pack(side="right", padx=5)

        # Save project button
        self.save_btn = ctk.CTkButton(
            action_frame,
            text="📁 Save Project",
            command=self._save_project,
            state="disabled",
            width=130,
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        self.save_btn.pack(side="right", padx=5)

    def _on_rom_loaded(self, rom_info, extracted_texts):
        """Callback saat ROM berhasil di-load dan teks diekstrak"""
        self.rom_loaded = True
        self.current_rom_info = rom_info
        self.extracted_texts = extracted_texts

        self.logger.info(f"ROM loaded: {rom_info.game_title}, {len(extracted_texts)} texts extracted")

        # Show progress bar and text panel
        self.progress_bar.pack(fill="x", padx=10, pady=5, before=self.text_panel)
        self.text_panel.pack(fill="both", expand=True, padx=10, pady=5)

        # Load texts ke text panel
        self.text_panel.load_entries(extracted_texts)

        # Update status
        self.status_label.configure(
            text=f"📂 ROM: {rom_info.game_title} ({rom_info.emulator_type}) - {len(extracted_texts)} teks"
        )

        # Enable buttons
        self.save_btn.configure(state="normal")
        self.export_btn.configure(state="normal")
        self.inject_btn.configure(state="normal")

        # Auto-translate jika ada teks yang belum diterjemahkan
        pending = [t for t in extracted_texts if not t.is_translated]
        if pending:
            self._start_translation()
        else:
            self.status_label.configure(text="✓ Semua teks sudah diterjemahkan")

    def _start_translation(self):
        """Start auto-translation dengan QueueManager"""
        if not self.rom_loaded:
            messagebox.showwarning("Warning", "Load ROM terlebih dahulu!")
            return

        if self.translation_running:
            return

        # Get pending texts
        pending_entries = self.text_panel.get_pending_entries()

        if not pending_entries:
            messagebox.showinfo("Info", "Semua teks sudah diterjemahkan!")
            return

        self.translation_running = True

        # Initialize QueueManager
        self.queue_manager = QueueManager(
            translators=self.translators,
            cache=self.cache
        )

        # Setup callbacks
        self.queue_manager.on_progress = self._on_translation_progress
        self.queue_manager.on_complete = self._on_translation_complete
        self.queue_manager.on_error = self._on_translation_error

        # Add texts to queue
        texts_to_translate = [entry.original_text for entry in pending_entries]
        self.queue_manager.add_texts(texts_to_translate)

        # Update UI
        self.progress_bar.set_status(f"🔄 Translating {len(texts_to_translate)} texts...")
        self.status_label.configure(text="🔄 Auto-translating semua teks...")

        # Start translation in background
        self.queue_manager.start()

        self.logger.info(f"Translation started: {len(texts_to_translate)} texts")

    def _on_translation_progress(self, progress: float, processed: int, total: int):
        """Callback saat translation progress update"""
        self.progress_bar.update_progress(
            progress=progress,
            processed=processed,
            total=total,
            status=f"🔄 Translating... {processed}/{total}"
        )

        # Update text panel jika ada hasil baru
        if self.queue_manager:
            results = self.queue_manager.get_results_with_original()
            for i, result in enumerate(results):
                if result["is_completed"] and result["translated"] != result["original"]:
                    # Update entry di text panel
                    entries = self.text_panel.get_all_entries()
                    for entry in entries:
                        if entry.original_text == result["original"] and not entry.is_translated:
                            entry.translated_text = result["translated"]
                            entry.is_translated = True
                            self.text_panel.update_entry_translation(entry)
                            break

    def _on_translation_complete(self, results):
        """Callback saat translation selesai"""
        self.translation_running = False

        stats = self.queue_manager.get_progress()
        self.progress_bar.set_complete(
            success=stats["success"],
            failed=stats["failed"],
            cached=stats["cached"]
        )

        self.status_label.configure(
            text=f"✓ Translation selesai! {stats['success']} success, {stats['failed']} failed"
        )

        # Update all entries di text panel
        self._sync_translation_results()

        self.logger.info(f"Translation complete: {stats['success']} success, {stats['failed']} failed")

    def _sync_translation_results(self):
        """Sync hasil translate ke text panel"""
        if not self.queue_manager:
            return

        results = self.queue_manager.get_results_with_original()
        entries = self.text_panel.get_all_entries()

        for result in results:
            for entry in entries:
                if entry.original_text == result["original"]:
                    entry.translated_text = result["translated"]
                    entry.is_translated = result["is_completed"]
                    if result["is_completed"]:
                        self.text_panel.update_entry_translation(entry)
                    break

    def _on_translation_error(self, error: str):
        """Callback saat translation error"""
        self.translation_running = False
        self.progress_bar.set_status(f"❌ Error: {error}")
        self.status_label.configure(text=f"❌ Translation error: {error}")

        self.logger.error(f"Translation error: {error}")
        messagebox.showerror("Error", f"Translation gagal:\n{error}")

    def _cancel_translation(self):
        """Cancel translation yang sedang berjalan"""
        if self.queue_manager:
            self.queue_manager.cancel()

        self.translation_running = False
        self.progress_bar.set_status("⏹️ Translation cancelled")
        self.status_label.configure(text="⏹️ Translation cancelled")

        self.logger.info("Translation cancelled by user")

    def _on_text_edited(self, entry, old_text, new_text):
        """Callback saat user edit teks terjemahan"""
        self.logger.info(f"Text edited: {old_text[:20]}... -> {new_text[:20]}...")

    def _export_patch(self):
        """Export patch file dari hasil terjemahan"""
        if not self.rom_loaded:
            messagebox.showwarning("Warning", "Load ROM terlebih dahulu!")
            return

        # Get translated entries
        translated_entries = self.text_panel.get_translated_entries()

        if not translated_entries:
            messagebox.showwarning("Warning", "Belum ada teks yang diterjemahkan!")
            return

        # Get output path
        output_path = filedialog.asksaveasfilename(
            title="Export Patch",
            filetypes=[
                ("JSON Patch", "*.json"),
                ("XDelta Patch", "*.xdelta"),
                ("IPS Patch", "*.ips"),
                ("All Files", "*.*")
            ],
            defaultextension=".json",
            initialfile=f"{self.current_rom_info.game_title}_translation_patch"
        )

        if not output_path:
            return

        # Export berdasarkan format
        success = False

        if output_path.endswith('.json'):
            success = self.patch_builder.create_json_patch(translated_entries, output_path)
        elif output_path.endswith('.xdelta'):
            messagebox.showinfo("Info", "Untuk export XDelta, lakukan 'Inject to ROM' terlebih dahulu, lalu buat patch dari ROM asli vs ROM terjemahan.")
            return
        elif output_path.endswith('.ips'):
            messagebox.showinfo("Info", "Untuk export IPS, lakukan 'Inject to ROM' terlebih dahulu, lalu buat patch dari ROM asli vs ROM terjemahan.")
            return

        if success:
            messagebox.showinfo("Success", f"Patch berhasil di-export ke:\n{output_path}")
            self.status_label.configure(text=f"✓ Patch exported: {output_path}")
        else:
            messagebox.showerror("Error", "Gagal export patch!")

    def _inject_to_rom(self):
        """Inject teks terjemahan ke ROM dan save sebagai file baru"""
        if not self.rom_loaded:
            messagebox.showwarning("Warning", "Load ROM terlebih dahulu!")
            return

        translated_entries = self.text_panel.get_translated_entries()

        if not translated_entries:
            messagebox.showwarning("Warning", "Belum ada teks yang diterjemahkan!")
            return

        # Pilih output path
        output_path = filedialog.asksaveasfilename(
            title="Save Modified ROM",
            filetypes=[("ROM Files", "*.3ds *.nds *.gba *.iso"), ("All Files", "*.*")],
            defaultextension=".3ds",
            initialfile=f"{self.current_rom_info.game_title}_translated"
        )

        if not output_path:
            return

        try:
            # Baca ROM asli
            rom_data = bytearray(self.rom_loader.read_rom_data())

            # Inject teks
            self.text_injector.inject_to_rom(
                rom_data,
                translated_entries,
                self.current_rom_info.emulator_type
            )

            # Save ROM
            self.text_injector.save_modified_rom(rom_data, output_path)

            stats = self.text_injector.get_stats()
            messagebox.showinfo(
                "Success",
                f"ROM berhasil dimodifikasi!\n\n"
                f"Injected: {stats['injected']}\n"
                f"Failed: {stats['failed']}\n\n"
                f"Saved to:\n{output_path}"
            )

            self.status_label.configure(text=f"✓ ROM modified: {output_path}")

        except Exception as e:
            self.logger.error(f"Error injecting to ROM: {e}", exc_info=True)
            messagebox.showerror("Error", f"Gagal inject ke ROM:\n{str(e)}")

    def _save_project(self):
        """Save project saat ini"""
        if not self.rom_loaded:
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Project",
            filetypes=[("JSON", "*.json")],
            defaultextension=".json",
            initialfile=f"{self.current_rom_info.game_title}_project"
        )

        if not output_path:
            return

        # Get current entries
        entries = self.text_panel.get_all_entries()

        # Create project
        self.project_manager.create_project(
            rom_info=self.current_rom_info,
            texts=entries
        )

        # Save
        success = self.project_manager.save_project(output_path)

        if success:
            messagebox.showinfo("Success", f"Project saved to:\n{output_path}")
            self.status_label.configure(text=f"✓ Project saved: {output_path}")
        else:
            messagebox.showerror("Error", "Gagal save project!")

    def _open_settings(self):
        """Open settings dialog"""
        settings_window = SettingsPanel(self)
        settings_window.show()

    def _on_close(self):
        """Handle window close"""
        if self.translation_running:
            if not messagebox.askyesno(
                "Konfirmasi",
                "Translation masih berjalan. Yakin ingin keluar?"
            ):
                return

        # Cancel translation if running
        if self.queue_manager and self.queue_manager.is_running:
            self.queue_manager.cancel()

        self.logger.info("Application closing")
        self.destroy()
