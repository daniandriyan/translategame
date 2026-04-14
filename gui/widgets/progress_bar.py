"""
Progress Bar Widget - Custom progress bar dengan label dan percentage
Menampilkan progress translation secara realtime
"""

import customtkinter as ctk
from typing import Optional, Callable


class ProgressBarWidget(ctk.CTkFrame):
    """
    Custom progress bar widget dengan fitur:
    - Progress bar visual
    - Percentage label
    - Status text (Translating..., Completed, dll)
    - Detail count (e.g., "800/1000 texts")
    - Cancel button
    """

    def __init__(
        self,
        master,
        title: str = "Progress",
        show_cancel: bool = True,
        on_cancel: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.show_cancel = show_cancel
        self.on_cancel = on_cancel

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Menunggu...",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=20,
            corner_radius=10,
            progress_color="#2b8ada"
        )
        self.progress_bar.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # Detail frame (percentage + count)
        detail_frame = ctk.CTkFrame(self, fg_color="transparent")
        detail_frame.grid_columnconfigure(0, weight=1)
        detail_frame.grid_columnconfigure(1, weight=0)
        detail_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Percentage label
        self.percentage_label = ctk.CTkLabel(
            detail_frame,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.percentage_label.grid(row=0, column=0, sticky="w")

        # Count label
        self.count_label = ctk.CTkLabel(
            detail_frame,
            text="0/0 texts",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.count_label.grid(row=0, column=1, sticky="e")

        # Cancel button
        if self.show_cancel:
            self.cancel_button = ctk.CTkButton(
                self,
                text="⏹️ Cancel",
                command=self._on_cancel,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                width=100,
                height=30
            )
            self.cancel_button.grid(row=4, column=0, padx=10, pady=(5, 10), sticky="e")
            self.cancel_button.grid_remove()  # Hide by default

    def update_progress(self, progress: float, processed: int, total: int, status: str = None):
        """
        Update progress bar

        Args:
            progress: Progress percentage (0-100)
            processed: Jumlah yang sudah diproses
            total: Jumlah total
            status: Optional status text
        """
        # Update progress bar (0-1)
        self.progress_bar.set(progress / 100)

        # Update labels
        self.percentage_label.configure(text=f"{progress:.1f}%")
        self.count_label.configure(text=f"{processed}/{total} texts")

        # Update status
        if status:
            self.status_label.configure(text=status)

        # Show cancel button when running
        if self.show_cancel and progress < 100:
            self.cancel_button.grid()

    def set_status(self, status: str):
        """Set status text"""
        self.status_label.configure(text=status)

    def set_complete(self, success: int, failed: int, cached: int):
        """Set progress ke completed state"""
        self.progress_bar.set(1.0)
        self.percentage_label.configure(text="100%")
        self.count_label.configure(text=f"{success + failed} texts")
        self.status_label.configure(
            text=f"✓ Selesai! {success} success, {failed} failed, {cached} dari cache"
        )

        # Hide cancel button
        if self.show_cancel:
            self.cancel_button.grid_remove()

    def set_idle(self):
        """Set progress ke idle state"""
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        self.count_label.configure(text="0/0 texts")
        self.status_label.configure(text="Menunggu...", text_color="gray")

        if self.show_cancel:
            self.cancel_button.grid_remove()

    def _on_cancel(self):
        """Handle cancel button click"""
        if self.on_cancel:
            self.on_cancel()

    def reset(self):
        """Reset progress ke awal"""
        self.set_idle()
