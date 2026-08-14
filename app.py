# app.py
import tkinter as tk

from file_controller import FileControllerMixin
from gallery_controller import GalleryControllerMixin
from lot_controller import LotControllerMixin
from pdf_controller import PDFControllerMixin
from preview_controller import PreviewControllerMixin
from state_controller import StateControllerMixin
from ui_builder import UIBuilderMixin


class StickerStudio(
    FileControllerMixin,
    GalleryControllerMixin,
    LotControllerMixin,
    PDFControllerMixin,
    PreviewControllerMixin,
    StateControllerMixin,
    UIBuilderMixin,
):
    def __init__(self, root):
        self.root = root
        self.root.title("Karim Sticker Studio — Edition Professionnelle")
        self.root.geometry("1400x900")
        self.root.configure(bg="#0B0B14")
        self.root.minsize(1280, 800)

        self.lot = []
        self.selected_index = None
        self.mode = "create"

        self.brand_var = tk.StringVar(value="KARIM")
        self.parfum_var = tk.StringVar(value="Fahrenheit")
        self.gender_var = tk.StringVar(value="male")
        self.pattern_var = tk.StringVar(value="gradient")
        self.insta_var = tk.StringVar(value="https://www.instagram.com/karim_parfums/")
        self.phone_var = tk.StringVar(value="07 75 36 73 51")
        self.phone_color_var = tk.StringVar(value="white")
        self.phone_bg_var = tk.StringVar(value="none")
        self.quantity_var = tk.StringVar(value="32")

        self._font_cache = {}
        self._last_qr_params = None
        self._qr_cache_pil = None
        self._pattern_btns = {}
        self._pattern_cells = {}
        self._gallery_cards = []
        self._status_after = None

        self.build_ui()
        self.load_autosave()
        self.update_preview()
        self.update_stats()
        self.set_mode("create")

    def set_status(self, text, error=False):
        if self._status_after:
            self.root.after_cancel(self._status_after)
        self.stats_alert.config(text=text, fg="#E74C3C" if error else "#2ECC71")
        self._status_after = self.root.after(4000, lambda: self.update_stats())