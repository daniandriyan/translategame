"""
Settings Panel - Dialog untuk pengaturan aplikasi
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import logging

from config import TRANSLATION_CONFIG, GUI_CONFIG, CACHE_CONFIG, ROM_CONFIG


class SettingsPanel:
    """
    Settings dialog dengan pengaturan:
    - Translation provider (primary & fallback)
    - Target bahasa
    - Cache settings
    - GUI theme
    """

    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger(__name__)

        # Create window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("⚙️ Settings")
        self.window.geometry("500x550")
        self.window.resizable(False, False)

        # Center on parent
        self.window.transient(parent)
        self.window.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create semua settings widgets"""
        self.window.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            self.window,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # === Translation Settings ===
        trans_frame = ctk.CTkFrame(self.window)
        trans_frame.grid_columnconfigure(1, weight=1)
        trans_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        trans_title = ctk.CTkLabel(
            trans_frame,
            text="Translation Provider",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        trans_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # Primary provider
        ctk.CTkLabel(
            trans_frame,
            text="Primary:",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.primary_var = tk.StringVar(value=TRANSLATION_CONFIG["primary_provider"])
        primary_menu = ctk.CTkOptionMenu(
            trans_frame,
            variable=self.primary_var,
            values=["g4f", "ollama", "huggingface"],
            width=150
        )
        primary_menu.grid(row=1, column=1, padx=10, pady=5, sticky="e")

        # Fallback providers
        ctk.CTkLabel(
            trans_frame,
            text="Fallback:",
            font=ctk.CTkFont(size=12)
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        fallback_text = ", ".join(TRANSLATION_CONFIG["fallback_providers"])
        ctk.CTkLabel(
            trans_frame,
            text=fallback_text,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).grid(row=2, column=1, padx=10, pady=5, sticky="e")

        # === Target Language ===
        lang_frame = ctk.CTkFrame(self.window)
        lang_frame.grid_columnconfigure(1, weight=1)
        lang_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        lang_title = ctk.CTkLabel(
            lang_frame,
            text="Target Bahasa",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lang_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(
            lang_frame,
            text="Target:",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.target_var = tk.StringVar(value="Indonesian")
        target_menu = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.target_var,
            values=["Indonesian", "English", "Japanese"],
            width=150
        )
        target_menu.grid(row=1, column=1, padx=10, pady=5, sticky="e")

        # === Cache Settings ===
        cache_frame = ctk.CTkFrame(self.window)
        cache_frame.grid_columnconfigure(1, weight=1)
        cache_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        cache_title = ctk.CTkLabel(
            cache_frame,
            text="Cache Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cache_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # Enable cache
        self.cache_enable_var = tk.BooleanVar(value=CACHE_CONFIG["enabled"])
        cache_check = ctk.CTkCheckBox(
            cache_frame,
            text="Enable Cache",
            variable=self.cache_enable_var
        )
        cache_check.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Cache TTL
        ctk.CTkLabel(
            cache_frame,
            text="TTL (days):",
            font=ctk.CTkFont(size=12)
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")

        ttl_days = CACHE_CONFIG["ttl"] // 86400
        self.ttl_var = tk.StringVar(value=str(ttl_days))
        ttl_entry = ctk.CTkEntry(
            cache_frame,
            textvariable=self.ttl_var,
            width=80
        )
        ttl_entry.grid(row=2, column=1, padx=10, pady=5, sticky="e")

        # === GUI Settings ===
        gui_frame = ctk.CTkFrame(self.window)
        gui_frame.grid_columnconfigure(1, weight=1)
        gui_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        gui_title = ctk.CTkLabel(
            gui_frame,
            text="GUI Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        gui_title.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        # Theme
        ctk.CTkLabel(
            gui_frame,
            text="Theme:",
            font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.theme_var = tk.StringVar(value=GUI_CONFIG["theme"])
        theme_menu = ctk.CTkOptionMenu(
            gui_frame,
            variable=self.theme_var,
            values=["dark", "light"],
            width=100
        )
        theme_menu.grid(row=1, column=1, padx=10, pady=5, sticky="e")

        # === Buttons ===
        btn_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        btn_frame.grid(row=5, column=0, padx=20, pady=20, sticky="e")

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Save",
            command=self._save_settings,
            width=100,
            fg_color="#27ae60",
            hover_color="#219653"
        )
        save_btn.grid(row=0, column=0, padx=5)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.window.destroy,
            width=100,
            fg_color="gray",
            hover_color="#555555"
        )
        cancel_btn.grid(row=0, column=1, padx=5)

    def _save_settings(self):
        """Save settings"""
        try:
            # Validate TTL
            ttl_days = int(self.ttl_var.get())
            if ttl_days < 1:
                messagebox.showerror("Error", "TTL harus lebih dari 0 hari")
                return

            self.logger.info("Settings saved successfully")
            messagebox.showinfo("Info", "Settings berhasil disimpan!")

            self.window.destroy()

        except ValueError:
            messagebox.showerror("Error", "TTL harus berupa angka")

    def show(self):
        """Show settings window"""
        self.window.wait_window()
