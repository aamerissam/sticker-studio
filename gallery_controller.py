# gallery_controller.py
import tkinter as tk
from tkinter import messagebox
from config import PALETTES, PATTERNS, SLOTS_PER_PAGE, COLS


class GalleryControllerMixin:
    # ── Selection ──
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
        self._scroll_gallery_to(idx)

    def _scroll_gallery_to(self, idx):
        """Scroll gallery so selected card is visible."""
        if 0 <= idx < len(self._gallery_cards):
            card = self._gallery_cards[idx]
            self.gallery_scroll.canvas.update_idletasks()
            inner_h = self.gallery_scroll.inner.winfo_height()
            if inner_h > 0:
                y = card.winfo_y()
                self.gallery_scroll.canvas.yview_moveto(max(0, y - 20) / inner_h)

    def update_gallery_selection(self):
        for i, frame in enumerate(self._gallery_cards):
            if i == self.selected_index and self.mode == "edit":
                frame.config(highlightbackground="#FFD700", highlightthickness=3)
            else:
                frame.config(highlightbackground="#12121F", highlightthickness=0)

    # ── Page / Slot computation ──
    def _compute_pages(self):
        """
        Returns list of pages.
        Each page = {
            'page_num': int,
            'slots': [(slot_idx, card_idx, card), ...],   # all 32 slots
            'unique_cards': {card_idx: card},
            'vacant': int
        }
        """
        pages = []
        current_slots = []
        slot_counter = 0
        for card_idx, card in enumerate(self.lot):
            for _ in range(card["quantity"]):
                current_slots.append((slot_counter % SLOTS_PER_PAGE, card_idx, card))
                slot_counter += 1
                if slot_counter % SLOTS_PER_PAGE == 0:
                    unique = {}
                    for _, ci, c in current_slots:
                        unique[ci] = c
                    pages.append({
                        "page_num": len(pages),
                        "slots": current_slots,
                        "unique_cards": unique,
                        "vacant": 0
                    })
                    current_slots = []
        if current_slots:
            unique = {}
            for _, ci, c in current_slots:
                unique[ci] = c
            pages.append({
                "page_num": len(pages),
                "slots": current_slots,
                "unique_cards": unique,
                "vacant": SLOTS_PER_PAGE - len(current_slots)
            })
        return pages

    def _draw_slot_bar(self, parent, slots, vacant):
        """Draw a visual bar of 32 small squares representing page slots."""
        bar = tk.Frame(parent, bg="#0E0E1A", height=18)
        bar.pack(fill="x", padx=8, pady=(4, 6))
        bar.pack_propagate(False)
        # Create 32 tiny colored squares
        for slot_idx in range(SLOTS_PER_PAGE):
            if slot_idx < len(slots):
                _, card_idx, card = slots[slot_idx]
                color = PALETTES[card["gender"]]["bg"]
            else:
                color = "#1A1A2E"  # empty slot
            sq = tk.Frame(bar, bg=color, width=6, height=12)
            sq.pack(side="left", padx=(0, 1))
            sq.pack_propagate(False)
        if vacant > 0:
            tk.Label(bar, text="  +" + str(vacant) + " libre" + ("s" if vacant > 1 else ""),
                     font=("Helvetica", 7), bg="#0E0E1A", fg="#F39C12").pack(side="left", padx=(4, 0))

    # ── Refresh ──
    def refresh_gallery(self):
        for w in self.gallery_inner.winfo_children():
            w.destroy()
        self._gallery_cards.clear()

        if not self.lot:
            empty = tk.Label(self.gallery_inner, text="Aucune carte dans le lot",
                             font=("Helvetica", 10, "italic"),
                             bg="#12121F", fg="#555")
            empty.pack(pady=30)
            self.gallery_count.config(text="(0)")
            return

        total = sum(c["quantity"] for c in self.lot)
        self.gallery_count.config(
            text="(" + str(len(self.lot)) + " modèles · " + str(total) + " stickers)")

        pages = self._compute_pages()

        for page in pages:
            pn = page["page_num"]
            slots = page["slots"]
            vacant = page["vacant"]
            unique_cards = page["unique_cards"]

            # ── Page Header ──
            hdr = tk.Frame(self.gallery_inner, bg="#0A0A14", height=32)
            hdr.pack(fill="x", pady=(12, 0), padx=2)
            hdr.pack_propagate(False)

            status_text = "COMPLET" if vacant == 0 else str(vacant) + " libre" + ("s" if vacant > 1 else "")
            status_color = "#2ECC71" if vacant == 0 else "#F39C12"

            left = tk.Frame(hdr, bg="#0A0A14")
            left.pack(side="left", padx=8, pady=4)
            tk.Label(left, text="Page " + str(pn + 1),
                     font=("Helvetica", 9, "bold"),
                     bg="#0A0A14", fg="#888").pack(side="left")
            tk.Label(left, text="  ·  " + str(len(slots)) + "/" + str(SLOTS_PER_PAGE) + " stickers",
                     font=("Helvetica", 8),
                     bg="#0A0A14", fg="#555").pack(side="left")

            tk.Label(hdr, text=status_text,
                     font=("Helvetica", 8, "bold"),
                     bg="#0A0A14", fg=status_color).pack(side="right", padx=8, pady=4)

            # ── Visual Slot Bar ──
            self._draw_slot_bar(self.gallery_inner, slots, vacant)

            # ── Cards in this page ──
            for card_idx in sorted(unique_cards.keys()):
                card = unique_cards[card_idx]
                pal = PALETTES[card["gender"]]
                bg_hex = pal["bg"]

                card_frame = tk.Frame(self.gallery_inner, bg="#16162A", width=252, height=68,
                                      highlightbackground="#12121F", highlightthickness=0)
                card_frame.pack(pady=3, padx=4)
                card_frame.pack_propagate(False)
                card_frame.bind("<Button-1>", lambda e, i=card_idx: self.select_card(i))

                # Color indicator strip on left
                strip = tk.Frame(card_frame, bg=bg_hex, width=4)
                strip.pack(side="left", fill="y")

                content = tk.Frame(card_frame, bg="#16162A")
                content.pack(side="left", fill="both", expand=True, padx=(8, 6), pady=5)
                content.bind("<Button-1>", lambda e, i=card_idx: self.select_card(i))

                # Top row: init + name + actions
                top_row = tk.Frame(content, bg="#16162A")
                top_row.pack(fill="x")
                top_row.bind("<Button-1>", lambda e, i=card_idx: self.select_card(i))

                init = card["parfum"][:2].upper()
                init_lbl = tk.Label(top_row, text=init, font=("Helvetica", 14, "bold"),
                                    bg=bg_hex, fg="white", width=3)
                init_lbl.pack(side="left")
                init_lbl.bind("<Button-1>", lambda e, i=card_idx: self.select_card(i))

                name_lbl = tk.Label(top_row, text=card["parfum"].upper(),
                                    font=("Helvetica", 10, "bold"),
                                    bg="#16162A", fg="white")
                name_lbl.pack(side="left", padx=(8, 0))
                name_lbl.bind("<Button-1>", lambda e, i=card_idx: self.select_card(i))

                # Quick actions on right side of top row
                acts = tk.Frame(top_row, bg="#16162A")
                acts.pack(side="right")

                dup_btn = tk.Label(acts, text="⎘", font=("Helvetica", 10),
                                   bg="#16162A", fg="#888", cursor="hand2")
                dup_btn.pack(side="left", padx=(0, 8))
                dup_btn.bind("<Button-1>", lambda e, i=card_idx: self.duplicate_card(i))

                del_btn = tk.Label(acts, text="✕", font=("Helvetica", 10),
                                   bg="#16162A", fg="#E74C3C", cursor="hand2")
                del_btn.pack(side="left")
                del_btn.bind("<Button-1>", lambda e, i=card_idx: self.delete_card(i))

                # Bottom row: quantity controls + pattern + reorder
                bot_row = tk.Frame(content, bg="#16162A")
                bot_row.pack(fill="x", pady=(4, 0))
                bot_row.bind("<Button-1>", lambda e, i=card_idx: self.select_card(i))

                # [-] button
                minus = tk.Label(bot_row, text="−", font=("Helvetica", 10, "bold"),
                                 bg="#1E1E32", fg="white", cursor="hand2",
                                 width=2)
                minus.pack(side="left")
                minus.bind("<Button-1>", lambda e, i=card_idx: self.quick_qty_change(i, -1))

                # Quantity display
                qty_lbl = tk.Label(bot_row, text=str(card["quantity"]),
                                   font=("Helvetica", 10, "bold"),
                                   bg="#16162A", fg="#DDDDDD", width=3)
                qty_lbl.pack(side="left", padx=(4, 4))

                # [+] button
                plus = tk.Label(bot_row, text="+", font=("Helvetica", 10, "bold"),
                                bg="#1E1E32", fg="white", cursor="hand2",
                                width=2)
                plus.pack(side="left")
                plus.bind("<Button-1>", lambda e, i=card_idx: self.quick_qty_change(i, +1))

                # Pattern label
                tk.Label(bot_row, text="·  " + PATTERNS[card["pattern"]]["label"],
                         font=("Helvetica", 8),
                         bg="#16162A", fg="#666").pack(side="left", padx=(6, 0))

                # Reorder arrows
                reorder = tk.Frame(bot_row, bg="#16162A")
                reorder.pack(side="right")
                if card_idx > 0:
                    up = tk.Label(reorder, text="▲", font=("Helvetica", 7),
                                  bg="#16162A", fg="#555", cursor="hand2")
                    up.pack(side="left", padx=(0, 6))
                    up.bind("<Button-1>", lambda e, i=card_idx: self.move_card(i, -1))
                if card_idx < len(self.lot) - 1:
                    down = tk.Label(reorder, text="▼", font=("Helvetica", 7),
                                    bg="#16162A", fg="#555", cursor="hand2")
                    down.pack(side="left")
                    down.bind("<Button-1>", lambda e, i=card_idx: self.move_card(i, 1))

                self._gallery_cards.append(card_frame)

            # Page separator
            if pn < len(pages) - 1:
                sep = tk.Frame(self.gallery_inner, bg="#1E1E32", height=1)
                sep.pack(fill="x", pady=(8, 0), padx=8)

        self.update_gallery_selection()

    # ── Quick quantity change ──
    def quick_qty_change(self, idx, delta):
        new_qty = self.lot[idx]["quantity"] + delta
        if new_qty >= 1:
            self.lot[idx]["quantity"] = new_qty
            self.refresh_gallery()
            self.update_stats()
            self.autosave()
            # If this card is currently being edited, update the editor qty too
            if self.mode == "edit" and self.selected_index == idx:
                self.quantity_var.set(str(new_qty))

    # ── Move / Duplicate / Delete ──
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
        self.set_status("Carte dupliquée")
        self.select_card(idx + 1)

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