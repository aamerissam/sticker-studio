# app.py
import tkinter as tk
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image, ImageTk, ImageFont
import os
import datetime
import math
import json
import tempfile

from config import SLOTS_PER_PAGE, COLS, ROWS, PALETTES, PATTERNS, AUTOSAVE_PATH
from qr_generator import generate_qr_pil, generate_qr_file
from pdf_renderer import draw_single_sticker_pdf
from preview_renderer import render_preview
from ui_components import ScrollableFrame


class StickerStudio:
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

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0B0B14", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="◈  KARIM STICKER STUDIO", font=("Helvetica", 18, "bold"),
                 bg="#0B0B14", fg="#FFFFFF").pack(side="left", padx=25, pady=14)
        hdr_actions = tk.Frame(header, bg="#0B0B14")
        hdr_actions.pack(side="right", padx=20)
        tk.Button(hdr_actions, text="Charger", font=("Helvetica", 9),
                  bg="#1A1A2E", fg="#888", bd=0, padx=12, pady=6,
                  cursor="hand2", command=self.load_lot).pack(side="left", padx=4)
        tk.Button(hdr_actions, text="Sauvegarder", font=("Helvetica", 9),
                  bg="#1A1A2E", fg="#888", bd=0, padx=12, pady=6,
                  cursor="hand2", command=self.save_lot).pack(side="left", padx=4)
        tk.Button(hdr_actions, text="Vider le lot", font=("Helvetica", 9),
                  bg="#2C0B0E", fg="#E74C3C", bd=0, padx=12, pady=6,
                  cursor="hand2", command=self.clear_lot).pack(side="left", padx=4)

        # Main container
        container = tk.Frame(self.root, bg="#0B0B14")
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # === PANEL 1: GALLERY (Left) ===
        gallery_container = tk.Frame(container, bg="#12121F", width=260)
        gallery_container.pack(side="left", fill="y", padx=(0, 12))
        gallery_container.pack_propagate(False)
        g_hdr = tk.Frame(gallery_container, bg="#12121F")
        g_hdr.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(g_hdr, text="MON LOT", font=("Helvetica", 11, "bold"),
                 bg="#12121F", fg="#666").pack(side="left")
        self.gallery_count = tk.Label(g_hdr, text="(0)", font=("Helvetica", 10),
                                      bg="#12121F", fg="#444")
        self.gallery_count.pack(side="left", padx=(6, 0))

        # Scrollable gallery list
        self.gallery_scroll = ScrollableFrame(gallery_container, bg="#12121F")
        self.gallery_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.gallery_inner = self.gallery_scroll.inner

        # New card button
        new_card_btn = tk.Frame(gallery_container, bg="#12121F")
        new_card_btn.pack(fill="x", padx=12, pady=10)
        self.btn_new_card = tk.Button(new_card_btn, text="+  NOUVELLE CARTE",
                                      font=("Helvetica", 10, "bold"),
                                      bg="#2ECC71", fg="white",
                                      activebackground="#27AE60",
                                      bd=0, pady=12, cursor="hand2",
                                      command=self.new_card)
        self.btn_new_card.pack(fill="x")

        # === PANEL 2: PREVIEW (Center) ===
        center_panel = tk.Frame(container, bg="#0E0E1A")
        center_panel.pack(side="left", fill="both", expand=True)
        tk.Label(center_panel, text="APERÇU EN TEMPS REEL", font=("Helvetica", 11, "bold"),
                 bg="#0E0E1A", fg="#555").pack(anchor="w", padx=20, pady=(18, 5))

        # Bottom controls stay visible; preview scroll fills remaining space above.
        btn_box = tk.Frame(center_panel, bg="#0E0E1A")
        btn_box.pack(side="bottom", fill="x", padx=20, pady=(12, 0))
        self.btn_add_update = tk.Button(btn_box, text="+  AJOUTER AU LOT",
                                        font=("Helvetica", 12, "bold"),
                                        bg="#2ECC71", fg="white",
                                        activebackground="#27AE60",
                                        bd=0, pady=16, cursor="hand2",
                                        command=self.add_or_update)
        self.btn_add_update.pack(fill="x", pady=(0, 10))

        self.btn_complete = tk.Button(btn_box, text="Completer la derniere page",
                                      font=("Helvetica", 10),
                                      bg="#1A1A2E", fg="#888",
                                      activebackground="#222",
                                      bd=0, pady=10, cursor="hand2",
                                      command=self.complete_page)
        self.btn_complete.pack(fill="x", pady=(0, 10))

        self.btn_final = tk.Button(
            btn_box,
            text="⬇  GENERER PDF FINAL",
            font=("Helvetica", 13, "bold"),
            bg="#2A2A40",
            fg="#555",
            activebackground="#2A2A40",
            bd=0,
            pady=18,
            cursor="arrow",
            command=self.generate_final_pdf,
            state="disabled"
        )
        self.btn_final.pack(fill="x")

        stats_box = tk.Frame(center_panel, bg="#16162A", bd=1, relief="solid",
                             highlightbackground="#222", highlightthickness=1)
        stats_box.pack(side="bottom", fill="x", padx=20, pady=10, ipady=14)
        self.stats_total = tk.Label(stats_box, text="0 sticker", font=("Helvetica", 11),
                                    bg="#16162A", fg="#666")
        self.stats_total.pack(anchor="w", padx=18)
        self.stats_pages = tk.Label(stats_box, text="0 page", font=("Helvetica", 10),
                                    bg="#16162A", fg="#555")
        self.stats_pages.pack(anchor="w", padx=18, pady=(4, 0))
        self.stats_alert = tk.Label(stats_box, text="Creez votre premiere carte pour commencer",
                                    font=("Helvetica", 11, "bold"),
                                    bg="#16162A", fg="#555")
        self.stats_alert.pack(anchor="w", padx=18, pady=(8, 0))

        self.mini_page = tk.Label(center_panel, text="", font=("Helvetica", 9),
                                  bg="#0E0E1A", fg="#444")
        self.mini_page.pack(side="bottom", pady=(0, 5))

        self.preview_scroll = ScrollableFrame(center_panel, bg="#0E0E1A")
        self.preview_scroll.pack(fill="both", expand=True, padx=20, pady=8)
        preview_frame = tk.Frame(self.preview_scroll.inner, bg="#2A2A40", bd=0)
        preview_frame.pack(pady=0)
        self.preview_label = tk.Label(preview_frame, bg="#0E0E1A")
        self.preview_label.pack(padx=1, pady=1)

        # === PANEL 3: EDITOR (Right) ===
        editor_container = tk.Frame(container, bg="#12121F", width=400)
        editor_container.pack(side="left", fill="y", padx=(12, 0))
        editor_container.pack_propagate(False)

        # Fixed editor header
        self.editor_title_frame = tk.Frame(editor_container, bg="#12121F")
        self.editor_title_frame.pack(fill="x", padx=15, pady=(15, 0))
        self.editor_title = tk.Label(self.editor_title_frame,
                                     text="NOUVELLE CARTE",
                                     font=("Helvetica", 13, "bold"),
                                     bg="#12121F", fg="#FFFFFF")
        self.editor_title.pack(anchor="w")
        self.editor_subtitle = tk.Label(self.editor_title_frame,
                                        text="Configurez un nouveau sticker",
                                        font=("Helvetica", 9),
                                        bg="#12121F", fg="#555")
        self.editor_subtitle.pack(anchor="w", pady=(2, 0))

        # Scrollable editor content
        self.editor_scroll = ScrollableFrame(editor_container, bg="#12121F")
        self.editor_scroll.pack(fill="both", expand=True, padx=0, pady=(12, 0))
        self.scroll_e = self.editor_scroll.inner

        # --- Editor widgets packed into self.scroll_e ---
        self._section(self.scroll_e, "IDENTITE")
        self._input_field(self.scroll_e, "Marque", self.brand_var, placeholder="KARIM")
        self._input_field(self.scroll_e, "Nom du parfum", self.parfum_var, placeholder="Fahrenheit")

        self._section(self.scroll_e, "APPARENCE")
        g_frame = tk.Frame(self.scroll_e, bg="#12121F")
        g_frame.pack(fill="x", pady=(0, 14))
        self.btn_male = tk.Button(g_frame, text="HOMME", font=("Helvetica", 10, "bold"),
                                  bg="#1F5EFF", fg="white", bd=0,
                                  padx=15, pady=12, cursor="hand2",
                                  command=lambda: self.set_gender("male"))
        self.btn_male.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.btn_female = tk.Button(g_frame, text="FEMME", font=("Helvetica", 10, "bold"),
                                    bg="#252540", fg="#777", bd=0,
                                    padx=15, pady=12, cursor="hand2",
                                    command=lambda: self.set_gender("female"))
        self.btn_female.pack(side="left", expand=True, fill="x", padx=(5, 0))

        p_frame = tk.Frame(self.scroll_e, bg="#12121F")
        p_frame.pack(fill="x", pady=(0, 10))
        p_frame.columnconfigure(0, weight=1)
        p_frame.columnconfigure(1, weight=1)
        p_frame.columnconfigure(2, weight=1)
        p_frame.columnconfigure(3, weight=1)

        self._pattern_cells = {}
        for idx, (key, info) in enumerate(PATTERNS.items()):
            cell = tk.Frame(p_frame, bg="#12121F", highlightthickness=0)
            cell.grid(row=idx // 4, column=idx % 4, sticky="nsew", padx=3, pady=3)
            btn = tk.Button(cell, text=info["icon"], font=("Helvetica", 16),
                            bg="#1E1E32", fg="#555", bd=0,
                            padx=2, pady=10, cursor="hand2",
                            command=lambda k=key: self.set_pattern(k))
            btn.pack(fill="x")
            lbl = tk.Label(cell, text=info["label"], font=("Helvetica", 8),
                           bg="#12121F", fg="#444")
            lbl.pack(pady=(2, 0))
            self._pattern_btns[key] = (btn, lbl)
            self._pattern_cells[key] = cell

        self._section(self.scroll_e, "CONTACT")
        self._input_field(self.scroll_e, "Lien Instagram / QR", self.insta_var,
                          placeholder="https://instagram.com/...")
        self._input_field(self.scroll_e, "Telephone", self.phone_var,
                          placeholder="07 75 36 73 51")

        self._section(self.scroll_e, "STYLE DU TELEPHONE")
        tk.Label(self.scroll_e, text="Couleur du texte", font=("Helvetica", 9),
                 bg="#12121F", fg="#666").pack(anchor="w", padx=5, pady=(0, 6))
        c_frame = tk.Frame(self.scroll_e, bg="#12121F")
        c_frame.pack(fill="x", pady=(0, 12))
        self.btn_pc_white = tk.Button(c_frame, text="Blanc", font=("Helvetica", 9),
                                      bg="#333", fg="white", bd=0, pady=10,
                                      cursor="hand2",
                                      command=lambda: self.set_phone_color("white"))
        self.btn_pc_white.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.btn_pc_black = tk.Button(c_frame, text="Noir", font=("Helvetica", 9),
                                      bg="#1E1E32", fg="#777", bd=0, pady=10,
                                      cursor="hand2",
                                      command=lambda: self.set_phone_color("black"))
        self.btn_pc_black.pack(side="left", expand=True, fill="x", padx=(4, 0))

        tk.Label(self.scroll_e, text="Fond du telephone", font=("Helvetica", 9),
                 bg="#12121F", fg="#666").pack(anchor="w", padx=5, pady=(0, 6))
        b_frame = tk.Frame(self.scroll_e, bg="#12121F")
        b_frame.pack(fill="x", pady=(0, 12))
        self.btn_pb_none = tk.Button(b_frame, text="Aucun", font=("Helvetica", 9),
                                     bg="#333", fg="white", bd=0, pady=10,
                                     cursor="hand2",
                                     command=lambda: self.set_phone_bg("none"))
        self.btn_pb_none.pack(side="left", expand=True, fill="x", padx=2)
        self.btn_pb_line = tk.Button(b_frame, text="Contour", font=("Helvetica", 9),
                                     bg="#1E1E32", fg="#777", bd=0, pady=10,
                                     cursor="hand2",
                                     command=lambda: self.set_phone_bg("line_outer"))
        self.btn_pb_line.pack(side="left", expand=True, fill="x", padx=2)
        self.btn_pb_fill = tk.Button(b_frame, text="Rempli", font=("Helvetica", 9),
                                     bg="#1E1E32", fg="#777", bd=0, pady=10,
                                     cursor="hand2",
                                     command=lambda: self.set_phone_bg("bg_outer"))
        self.btn_pb_fill.pack(side="left", expand=True, fill="x", padx=2)

        self._section(self.scroll_e, "QUANTITE")
        q_frame = tk.Frame(self.scroll_e, bg="#12121F")
        q_frame.pack(fill="x", pady=(0, 20))
        self.spin_qty = tk.Spinbox(q_frame, from_=1, to=999,
                                   textvariable=self.quantity_var, width=10,
                                   font=("Helvetica", 12),
                                   bg="#1E1E32", fg="white",
                                   buttonbackground="#333",
                                   insertbackground="white")
        self.spin_qty.pack(side="left")
        tk.Label(q_frame, text="exemplaires", font=("Helvetica", 10),
                 bg="#12121F", fg="#555").pack(side="left", padx=(8, 0))

        # Traces
        for var in [self.brand_var, self.parfum_var, self.insta_var,
                    self.phone_var, self.quantity_var]:
            var.trace_add("write", lambda *args: self.update_preview())
        self.gender_var.trace_add("write", lambda *args: self.update_preview())
        self.pattern_var.trace_add("write", lambda *args: self.update_preview())
        self.phone_color_var.trace_add("write", lambda *args: self.update_preview())
        self.phone_bg_var.trace_add("write", lambda *args: self.update_preview())

        self.update_gender_buttons()
        self.update_pattern_buttons()
        self.update_phone_color_buttons()
        self.update_phone_bg_buttons()

    def _section(self, parent, text):
        sep = tk.Frame(parent, bg="#1E1E32", height=1)
        sep.pack(fill="x", pady=(18, 10), padx=5)
        tk.Label(parent, text=text, font=("Helvetica", 9, "bold"),
                 bg="#12121F", fg="#444").pack(anchor="w", pady=(0, 10), padx=5)

    def _input_field(self, parent, label, var, placeholder=""):
        frame = tk.Frame(parent, bg="#12121F")
        frame.pack(fill="x", pady=(0, 12), padx=5)
        tk.Label(frame, text=label, font=("Helvetica", 9),
                 bg="#12121F", fg="#888").pack(anchor="w")
        entry = tk.Entry(frame, textvariable=var, font=("Helvetica", 11),
                         bg="#1E1E32", fg="white", bd=0,
                         highlightthickness=1,
                         highlightbackground="#2A2A40",
                         highlightcolor="#1F5EFF",
                         insertbackground="white")
        entry.pack(fill="x", pady=(4, 0), ipady=10)
        if placeholder:
            entry.insert(0, placeholder)
            entry.bind("<FocusIn>", lambda e: self._on_entry_focus(entry, var, placeholder))
            entry.bind("<FocusOut>", lambda e: self._on_entry_blur(entry, var, placeholder))

    def _on_entry_focus(self, entry, var, placeholder):
        if var.get() == placeholder:
            var.set("")
            entry.config(fg="white")

    def _on_entry_blur(self, entry, var, placeholder):
        if var.get().strip() == "":
            var.set(placeholder)
            entry.config(fg="#555")

    def set_mode(self, mode, index=None):
        self.mode = mode
        self.selected_index = index
        if mode == "create":
            self.editor_title.config(text="NOUVELLE CARTE", fg="#FFFFFF")
            self.editor_subtitle.config(text="Configurez un nouveau sticker")
            self.btn_add_update.config(text="+  AJOUTER AU LOT", bg="#2ECC71",
                                        activebackground="#27AE60")
            self.btn_new_card.config(state="disabled", bg="#1A3A25")
        else:
            card = self.lot[index]
            self.editor_title.config(text="EDITER : " + card["parfum"].upper(), fg="#FFD700")
            self.editor_subtitle.config(text="Modifiez les parametres de cette carte")
            self.btn_add_update.config(text="◈  METTRE A JOUR", bg="#1F5EFF",
                                        activebackground="#1447CC")
            self.btn_new_card.config(state="normal", bg="#2ECC71")
        self.update_gallery_selection()

    def set_gender(self, gender):
        self.gender_var.set(gender)
        self.update_gender_buttons()
        self.update_preview()

    def set_pattern(self, pattern):
        self.pattern_var.set(pattern)
        self.update_pattern_buttons()
        self.update_preview()

    def set_phone_color(self, color):
        self.phone_color_var.set(color)
        self.update_phone_color_buttons()
        self.update_preview()

    def set_phone_bg(self, bg_type):
        self.phone_bg_var.set(bg_type)
        self.update_phone_bg_buttons()
        self.update_preview()

    def update_gender_buttons(self):
        is_male = self.gender_var.get() == "male"
        self.btn_male.config(bg="#1F5EFF" if is_male else "#1E1E32",
                             fg="white" if is_male else "#555")
        self.btn_female.config(bg="#FF5FA2" if not is_male else "#1E1E32",
                               fg="white" if not is_male else "#555")

    def update_pattern_buttons(self):
        active = self.pattern_var.get()
        for key, (btn, lbl) in self._pattern_btns.items():
            cell = self._pattern_cells[key]
            if key == active:
                btn.config(bg="#2A2A45", fg="white")
                lbl.config(fg="white")
                cell.config(highlightbackground="#1F5EFF", highlightthickness=1)
            else:
                btn.config(bg="#1E1E32", fg="#555")
                lbl.config(fg="#444")
                cell.config(highlightbackground="#12121F", highlightthickness=0)

    def update_phone_color_buttons(self):
        active = self.phone_color_var.get()
        self.btn_pc_white.config(bg="#333" if active == "white" else "#1E1E32",
                                 fg="white" if active == "white" else "#555")
        self.btn_pc_black.config(bg="#333" if active == "black" else "#1E1E32",
                                 fg="white" if active == "black" else "#555")

    def update_phone_bg_buttons(self):
        active = self.phone_bg_var.get()
        mapping = {"none": self.btn_pb_none, "line_outer": self.btn_pb_line, "bg_outer": self.btn_pb_fill}
        for key, btn in mapping.items():
            btn.config(bg="#333" if active == key else "#1E1E32",
                       fg="white" if active == key else "#555")

    def new_card(self):
        self.brand_var.set("KARIM")
        self.parfum_var.set("Fahrenheit")
        self.gender_var.set("male")
        self.pattern_var.set("gradient")
        self.insta_var.set("https://www.instagram.com/karim_parfums/")
        self.phone_var.set("07 75 36 73 51")
        self.phone_color_var.set("white")
        self.phone_bg_var.set("none")
        self.quantity_var.set("32")
        self.set_mode("create")
        self.update_preview()
        self.update_stats()

    def select_card(self, idx):
        card = self.lot[idx]
        self.brand_var.set(card["brand"])
        self.parfum_var.set(card["parfum"])
        self.gender_var.set(card["gender"])
        self.pattern_var.set(card["pattern"])
        self.insta_var.set(card["insta"])
        self.phone_var.set(card["phone"])
        self.phone_color_var.set(card["phone_text_color"])
        self.phone_bg_var.set(card["phone_bg_type"])
        self.quantity_var.set(str(card["quantity"]))
        self.set_mode("edit", idx)
        self.update_preview()

    def update_gallery_selection(self):
        for i, frame in enumerate(self._gallery_cards):
            if i == self.selected_index and self.mode == "edit":
                frame.config(highlightbackground="#FFD700", highlightthickness=2)
            else:
                frame.config(highlightbackground="#12121F", highlightthickness=0)

    def refresh_gallery(self):
        for w in self.gallery_inner.winfo_children():
            w.destroy()
        self._gallery_cards.clear()
        if not self.lot:
            empty = tk.Label(self.gallery_inner, text="Aucune carte dans le lot",
                             font=("Helvetica", 10, "italic"),
                             bg="#12121F", fg="#333")
            empty.pack(pady=30)
            self.gallery_count.config(text="(0)")
            return
        self.gallery_count.config(text="(" + str(len(self.lot)) + ")")
        for idx, card in enumerate(self.lot):
            pal = PALETTES[card["gender"]]
            bg_hex = pal["bg"]
            card_frame = tk.Frame(self.gallery_inner, bg=bg_hex, width=220, height=85,
                                  highlightbackground="#12121F", highlightthickness=0)
            card_frame.pack(pady=5, padx=2)
            card_frame.pack_propagate(False)
            card_frame.bind("<Button-1>", lambda e, i=idx: self.select_card(i))
            content = tk.Frame(card_frame, bg=bg_hex)
            content.pack(fill="both", expand=True, padx=10, pady=8)
            content.bind("<Button-1>", lambda e, i=idx: self.select_card(i))
            init = card["parfum"][:2].upper()
            init_lbl = tk.Label(content, text=init, font=("Helvetica", 18, "bold"),
                                bg=bg_hex, fg="white")
            init_lbl.pack(side="left")
            init_lbl.bind("<Button-1>", lambda e, i=idx: self.select_card(i))
            info = tk.Frame(content, bg=bg_hex)
            info.pack(side="left", fill="y", expand=True, padx=(10, 0))
            info.bind("<Button-1>", lambda e, i=idx: self.select_card(i))
            name_lbl = tk.Label(info, text=card["parfum"].upper(),
                                font=("Helvetica", 10, "bold"),
                                bg=bg_hex, fg="white")
            name_lbl.pack(anchor="w")
            name_lbl.bind("<Button-1>", lambda e, i=idx: self.select_card(i))
            qty_lbl = tk.Label(info, text="x" + str(card["quantity"]) + "  •  " + PATTERNS[card["pattern"]]["label"],
                               font=("Helvetica", 9),
                               bg=bg_hex, fg="#CCCCCC")
            qty_lbl.pack(anchor="w")
            qty_lbl.bind("<Button-1>", lambda e, i=idx: self.select_card(i))
            actions = tk.Frame(content, bg=bg_hex)
            actions.pack(side="right")
            if idx > 0:
                up = tk.Label(actions, text="▲", font=("Helvetica", 9),
                              bg=bg_hex, fg="white", cursor="hand2")
                up.pack(pady=(0, 2))
                up.bind("<Button-1>", lambda e, i=idx: self.move_card(i, -1))
            if idx < len(self.lot) - 1:
                down = tk.Label(actions, text="▼", font=("Helvetica", 9),
                                bg=bg_hex, fg="white", cursor="hand2")
                down.pack(pady=(0, 2))
                down.bind("<Button-1>", lambda e, i=idx: self.move_card(i, 1))
            dup = tk.Label(actions, text="⎘", font=("Helvetica", 11),
                           bg=bg_hex, fg="white", cursor="hand2")
            dup.pack(pady=(0, 2))
            dup.bind("<Button-1>", lambda e, i=idx: self.duplicate_card(i))
            delete = tk.Label(actions, text="✕", font=("Helvetica", 11),
                              bg=bg_hex, fg="#FFAAAA", cursor="hand2")
            delete.pack()
            delete.bind("<Button-1>", lambda e, i=idx: self.delete_card(i))
            self._gallery_cards.append(card_frame)
        self.update_gallery_selection()

    def move_card(self, idx, direction):
        new_idx = idx + direction
        if 0 <= new_idx < len(self.lot):
            self.lot[idx], self.lot[new_idx] = self.lot[new_idx], self.lot[idx]
            if self.selected_index == idx:
                self.selected_index = new_idx
            elif self.selected_index == new_idx:
                self.selected_index = idx
            self.refresh_gallery()
            self.autosave()

    def duplicate_card(self, idx):
        card = self.lot[idx].copy()
        card["quantity"] = 1
        self.lot.insert(idx + 1, card)
        self.refresh_gallery()
        self.update_stats()
        self.autosave()
        self.set_status("Carte dupliquee")

    def delete_card(self, idx):
        if not messagebox.askyesno("Supprimer", "Supprimer '" + self.lot[idx]["parfum"] + "' ?"):
            return
        self.lot.pop(idx)
        if self.selected_index == idx:
            self.new_card()
        elif self.selected_index is not None and self.selected_index > idx:
            self.selected_index -= 1
        self.refresh_gallery()
        self.update_stats()
        self.autosave()

    def add_or_update(self):
        try:
            qty = int(self.quantity_var.get())
            if qty < 1:
                raise ValueError
        except Exception:
            self.set_status("Quantite invalide", error=True)
            return
        insta = self.insta_var.get().strip()
        if not insta.startswith("http"):
            self.set_status("L'URL doit commencer par http://", error=True)
            return
        card = {
            "brand": self.brand_var.get().strip() or "KARIM",
            "parfum": self.parfum_var.get().strip() or "Fahrenheit",
            "gender": self.gender_var.get(),
            "insta": insta,
            "phone": self.phone_var.get().strip(),
            "pattern": self.pattern_var.get(),
            "phone_text_color": self.phone_color_var.get(),
            "phone_bg_type": self.phone_bg_var.get(),
            "quantity": qty
        }
        if self.mode == "edit" and self.selected_index is not None:
            self.lot[self.selected_index] = card
            self.set_status("'" + card["parfum"] + "' mis a jour")
        else:
            self.lot.append(card)
            self.set_status("'" + card["parfum"] + "' ajoute au lot")
        self.refresh_gallery()
        self.update_stats()
        self.autosave()
        if self.mode == "create":
            self.set_mode("create")

    def complete_page(self):
        if not self.lot:
            return
        total = sum(c["quantity"] for c in self.lot)
        vacant = (SLOTS_PER_PAGE - (total % SLOTS_PER_PAGE)) % SLOTS_PER_PAGE
        if vacant == 0:
            self.set_status("La derniere page est deja complete")
            return
        self.lot[-1]["quantity"] += vacant
        self.refresh_gallery()
        self.update_stats()
        self.autosave()
        self.set_status("+" + str(vacant) + " ajoutes pour completer la page")

    def update_stats(self):
        total = sum(c["quantity"] for c in self.lot)
        if total == 0:
            self.stats_total.config(text="0 sticker", fg="#444")
            self.stats_pages.config(text="0 page A4", fg="#333")
            self.stats_alert.config(text="Creez votre premiere carte pour commencer", fg="#444")

            # PDF Button: disabled visual state
            self.btn_final.config(
                state="disabled",
                bg="#2A2A40",
                fg="#555",
                activebackground="#2A2A40",
                cursor="arrow"
            )
            self.mini_page.config(text="")
            return

        pages = math.ceil(total / SLOTS_PER_PAGE)
        vacant = (SLOTS_PER_PAGE - (total % SLOTS_PER_PAGE)) % SLOTS_PER_PAGE
        self.stats_total.config(text=str(total) + " stickers  ·  " + str(len(self.lot)) + " modeles", fg="#AAA")
        self.stats_pages.config(text=str(pages) + " page(s) A4 paysage", fg="#888")
        if vacant > 0:
            self.stats_alert.config(text=str(vacant) + " places libres sur la derniere page",
                                    fg="#F39C12", bg="#16162A")
        else:
            self.stats_alert.config(text="OK  Lot optimal — pret pour l'impression",
                                    fg="#2ECC71", bg="#16162A")
        self.mini_page.config(text="Apercu: 1 sticker = " + str(100 // COLS) + "% de la largeur page")

        # PDF Button: enabled visual state
        self.btn_final.config(
            state="normal",
            bg="#1F5EFF",
            fg="white",
            activebackground="#1447CC",
            cursor="hand2"
        )

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

    def generate_final_pdf(self):
        if not self.lot:
            messagebox.showwarning("Lot vide", "Ajoutez au moins une carte au lot.")
            return
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile="stickers_lot_" + ts + ".pdf",
            title="Enregistrer le PDF"
        )
        if not file_path:
            self.set_status("Generation annulee")
            return
        self.set_status("Generation du PDF en cours...")
        self.root.update_idletasks()
        try:
            PAGE_W, PAGE_H = landscape(A4)
            MARGIN = 2 * mm
            GAP = 0.4 * mm
            sticker_w = (PAGE_W - 2 * MARGIN - (COLS - 1) * GAP) / COLS
            sticker_h = (PAGE_H - 2 * MARGIN - (ROWS - 1) * GAP) / ROWS
            qr_cache = {}
            for card in self.lot:
                key = (card["insta"], card["gender"])
                if key not in qr_cache:
                    tsn = datetime.datetime.now().strftime("%H%M%S")
                    path = os.path.join(tempfile.gettempdir(), "qr_final_" + str(len(qr_cache)) + "_" + tsn + ".png")
                    accent = PALETTES[card["gender"]]["accent_hex"]
                    generate_qr_file(card["insta"], accent, path)
                    qr_cache[key] = path
            c = canvas.Canvas(file_path, pagesize=landscape(A4))
            slot = 0
            for card in self.lot:
                qr_path = qr_cache[(card["insta"], card["gender"])]
                for _ in range(card["quantity"]):
                    col = slot % COLS
                    row = (slot // COLS) % ROWS
                    x = MARGIN + col * (sticker_w + GAP)
                    y = PAGE_H - MARGIN - (row + 1) * sticker_h - row * GAP
                    draw_single_sticker_pdf(c, x, y, sticker_w, sticker_h, card, qr_path)
                    slot += 1
                    if slot % SLOTS_PER_PAGE == 0:
                        c.showPage()
            c.save()
            for path in qr_cache.values():
                if os.path.exists(path):
                    os.remove(path)
            total = sum(c["quantity"] for c in self.lot)
            pages = math.ceil(total / SLOTS_PER_PAGE)
            vacant = (SLOTS_PER_PAGE - (total % SLOTS_PER_PAGE)) % SLOTS_PER_PAGE
            msg = "PDF genere avec succes :\n" + file_path + "\n\n" + str(total) + " stickers · " + str(pages) + " page(s)"
            if vacant > 0:
                msg = msg + "\n" + str(vacant) + " places vacantes sur la derniere page"
            self.stats_alert.config(text="OK PDF genere !", fg="#2ECC71")
            self.set_status("PDF genere avec succes")
            messagebox.showinfo("Succes", msg)
        except Exception as e:
            self.set_status("Erreur : " + str(e), error=True)
            messagebox.showerror("Erreur", "La generation a echoue :\n" + str(e))

    def set_status(self, text, error=False):
        if self._status_after:
            self.root.after_cancel(self._status_after)
        self.stats_alert.config(text=text, fg="#E74C3C" if error else "#2ECC71")
        self._status_after = self.root.after(4000, lambda: self.update_stats())

    def autosave(self):
        try:
            with open(AUTOSAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.lot, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def load_autosave(self):
        try:
            if os.path.exists(AUTOSAVE_PATH):
                with open(AUTOSAVE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.lot = data
                        self.refresh_gallery()
        except Exception:
            pass

    def save_lot(self):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="lot_" + ts + ".json",
            title="Sauvegarder le lot"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.lot, f, ensure_ascii=False, indent=2)
                self.set_status("Lot sauvegarde")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def load_lot(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Charger un lot"
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.lot = data
                        self.new_card()
                        self.refresh_gallery()
                        self.update_stats()
                        self.autosave()
                        self.set_status("Lot charge")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def clear_lot(self):
        if not self.lot:
            return
        if messagebox.askyesno("Confirmer", "Vider tout le lot ?"):
            self.lot = []
            self.new_card()
            self.refresh_gallery()
            self.update_stats()
            self.autosave()