# preview_controller.py
from PIL import Image, ImageTk, ImageFont
from config import PALETTES
from preview_renderer import render_preview
from qr_generator import generate_qr_pil


class PreviewControllerMixin:
    def get_font(self, name, size):
        key = (name, size)
        if key not in self._font_cache:
            candidates = [
                "C:/Windows/Fonts/" + name,
                "/usr/share/fonts/truetype/dejavu/" + name,
                "/usr/share/fonts/truetype/liberation/" + name,
                "/usr/share/fonts/truetype/freefont/" + name,
                "/System/Library/Fonts/" + name,
                "/Library/Fonts/" + name,
                name,
            ]
            for path in candidates:
                try:
                    self._font_cache[key] = ImageFont.truetype(path, size)
                    break
                except Exception:
                    continue
            else:
                self._font_cache[key] = ImageFont.load_default()
        return self._font_cache[key]

    def _qr_cache_wrapper(self, insta, accent_hex, qr_size):
        cache_key = (insta, accent_hex, qr_size)
        if self._last_qr_params != cache_key:
            self._qr_cache_pil = generate_qr_pil(insta, accent_hex, qr_size)
            self._last_qr_params = cache_key
        return self._qr_cache_pil.copy()

    def update_preview(self):
        is_male = self.gender_var.get() == "male"
        pattern = self.pattern_var.get()
        pal = PALETTES["male"] if is_male else PALETTES["female"]
        brand = self.brand_var.get().upper() or "KARIM"
        parfum = self.parfum_var.get().upper() or "PARFUM"
        phone = (self.phone_var.get() or "0000000000") + "  "
        insta = self.insta_var.get().strip()

        cfg = {
            "gender": self.gender_var.get(),
            "pattern": pattern,
            "phone_text_color": self.phone_color_var.get(),
            "phone_bg_type": self.phone_bg_var.get(),
        }

        framed = render_preview(
            cfg, brand, parfum, phone, insta,
            self.get_font, self._qr_cache_wrapper
        )
        self.preview_tk = ImageTk.PhotoImage(framed)
        self.preview_label.config(image=self.preview_tk, bg="#0E0E1A")