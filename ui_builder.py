# ui_builder.py
import tkinter as tk
from ui_components import ScrollableFrame
from config import PALETTES, PATTERNS


class UIBuilderMixin:
    def build_ui(self):
        # ---------- HEADER ----------
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

        # ---------- MAIN ----------
        container = tk.Frame(self.root, bg="#0B0B14")
        container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # === PANEL 1: GALLERY ===
        gallery_container = tk.Frame(container, bg="#12121F", width=280)
        gallery_container.pack(side="left", fill="y", padx=(0, 12))
        gallery_container.pack_propagate(False)
        g_hdr = tk.Frame(gallery_container, bg="#12121F")
        g_hdr.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(g_hdr, text="MON LOT", font=("Helvetica", 11, "bold"),
                 bg="#12121F", fg="#888").pack(side="left")
        self.gallery_count = tk.Label(g_hdr, text="(0)", font=("Helvetica", 10),
                                      bg="#12121F", fg="#555")
        self.gallery_count.pack(side="left", padx=(6, 0))

        self.gallery_scroll = ScrollableFrame(gallery_container, bg="#12121F")
        self.gallery_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        self.gallery_inner = self.gallery_scroll.inner

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

        tk.Label(center_panel, text="APERÇU EN TEMPS RÉEL", font=("Helvetica", 11, "bold"),
                 bg="#0E0E1A", fg="#666").pack(anchor="w", padx=20, pady=(14, 0))

        self.preview_scroll = ScrollableFrame(center_panel, bg="#0E0E1A")
        self.preview_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        preview_frame = tk.Frame(self.preview_scroll.inner, bg="#2A2A40", bd=0)
        preview_frame.pack(pady=0)
        self.preview_label = tk.Label(preview_frame, bg="#0E0E1A")
        self.preview_label.pack(padx=1, pady=1)

        # === BOTTOM CONTROLS ===
        bottom_frame = tk.Frame(center_panel, bg="#0E0E1A")
        bottom_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 15))

        # Stats bar
        stats_bar = tk.Frame(bottom_frame, bg="#16162A", highlightbackground="#222",
                             highlightthickness=1)
        stats_bar.pack(fill="x", pady=(0, 10), ipady=10)

        stats_left = tk.Frame(stats_bar, bg="#16162A")
        stats_left.pack(side="left", padx=14)
        self.stats_total = tk.Label(stats_left, text="0 sticker", font=("Helvetica", 10),
                                    bg="#16162A", fg="#888")
        self.stats_total.pack(side="left")
        tk.Label(stats_left, text="·", font=("Helvetica", 10),
                 bg="#16162A", fg="#444").pack(side="left", padx=6)
        self.stats_pages = tk.Label(stats_left, text="0 page", font=("Helvetica", 10),
                                    bg="#16162A", fg="#888")
        self.stats_pages.pack(side="left")

        self.stats_alert = tk.Label(stats_bar, text="Créez votre première carte pour commencer",
                                    font=("Helvetica", 10, "bold"),
                                    bg="#16162A", fg="#555")
        self.stats_alert.pack(side="right", padx=14)

        # Button row 1
        btn_row1 = tk.Frame(bottom_frame, bg="#0E0E1A")
        btn_row1.pack(fill="x")
        btn_row1.columnconfigure(0, weight=3)
        btn_row1.columnconfigure(1, weight=2)

        self.btn_add_update = tk.Button(btn_row1, text="+  AJOUTER AU LOT",
                                        font=("Helvetica", 11, "bold"),
                                        bg="#2ECC71", fg="white",
                                        activebackground="#27AE60",
                                        bd=0, pady=14, cursor="hand2",
                                        command=self.add_or_update)
        self.btn_add_update.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.btn_final = tk.Button(btn_row1, text="⬇  GÉNÉRER PDF",
                                   font=("Helvetica", 11, "bold"),
                                   bg="#2A2A40", fg="#555",
                                   activebackground="#2A2A40",
                                   bd=0, pady=14, cursor="arrow",
                                   command=self.generate_final_pdf,
                                   state="disabled")
        self.btn_final.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Button row 2
        btn_row2 = tk.Frame(bottom_frame, bg="#0E0E1A")
        btn_row2.pack(fill="x", pady=(8, 0))
        self.btn_complete = tk.Button(btn_row2, text="Compléter la dernière page",
                                      font=("Helvetica", 9),
                                      bg="#151525", fg="#555",
                                      activebackground="#1A1A2E",
                                      bd=0, pady=8, cursor="hand2",
                                      command=self.complete_page)
        self.btn_complete.pack(fill="x")

        # === PANEL 3: EDITOR (Right) ===
        editor_container = tk.Frame(container, bg="#12121F", width=360)
        editor_container.pack(side="left", fill="y", padx=(12, 0))
        editor_container.pack_propagate(False)

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
                                        bg="#12121F", fg="#666")
        self.editor_subtitle.pack(anchor="w", pady=(2, 0))

        self.editor_scroll = ScrollableFrame(editor_container, bg="#12121F")
        self.editor_scroll.pack(fill="both", expand=True, padx=0, pady=(12, 0))
        self.scroll_e = self.editor_scroll.inner

        # --- Editor widgets ---
        self._section(self.scroll_e, "IDENTITÉ")
        self._input_field(self.scroll_e, "Marque", self.brand_var)
        self._input_field(self.scroll_e, "Nom du parfum", self.parfum_var)

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
        for i in range(4):
            p_frame.columnconfigure(i, weight=1)

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
                           bg="#12121F", fg="#555")
            lbl.pack(pady=(2, 0))
            self._pattern_btns[key] = (btn, lbl)
            self._pattern_cells[key] = cell

        self._section(self.scroll_e, "CONTACT")
        self._input_field(self.scroll_e, "Lien Instagram / QR", self.insta_var)
        self._input_field(self.scroll_e, "Téléphone", self.phone_var)

        self._section(self.scroll_e, "STYLE DU TÉLÉPHONE")
        tk.Label(self.scroll_e, text="Couleur du texte", font=("Helvetica", 9),
                 bg="#12121F", fg="#888").pack(anchor="w", padx=5, pady=(0, 6))
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

        tk.Label(self.scroll_e, text="Fond du téléphone", font=("Helvetica", 9),
                 bg="#12121F", fg="#888").pack(anchor="w", padx=5, pady=(0, 6))
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

        self._section(self.scroll_e, "QUANTITÉ")
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
                 bg="#12121F", fg="#666").pack(side="left", padx=(8, 0))

        # Traces — clean, no placeholder interference
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
                 bg="#12121F", fg="#666").pack(anchor="w", pady=(0, 10), padx=5)

    def _input_field(self, parent, label, var):
        """Clean input field — NO placeholder system to avoid text doubling bugs."""
        frame = tk.Frame(parent, bg="#12121F")
        frame.pack(fill="x", pady=(0, 12), padx=5)
        tk.Label(frame, text=label, font=("Helvetica", 9),
                 bg="#12121F", fg="#999").pack(anchor="w")
        entry = tk.Entry(frame, textvariable=var, font=("Helvetica", 11),
                         bg="#1E1E32", fg="white", bd=0,
                         highlightthickness=1,
                         highlightbackground="#2A2A40",
                         highlightcolor="#1F5EFF",
                         insertbackground="white")
        entry.pack(fill="x", pady=(4, 0), ipady=10)