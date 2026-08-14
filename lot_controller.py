# lot_controller.py
import math
from tkinter import messagebox
from config import SLOTS_PER_PAGE


class LotControllerMixin:
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

    def add_or_update(self):
        try:
            qty = int(self.quantity_var.get())
            if qty < 1:
                raise ValueError
        except Exception:
            self.set_status("Quantité invalide", error=True)
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
            self.set_status("'" + card["parfum"] + "' mis à jour")
            self.refresh_gallery()
            self.update_stats()
            self.autosave()
            # Stay in edit mode, selection preserved
        else:
            self.lot.append(card)
            self.set_status("'" + card["parfum"] + "' ajouté au lot")
            self.refresh_gallery()
            self.update_stats()
            self.autosave()
            # Auto-select the newly added card so user sees what they created
            self.select_card(len(self.lot) - 1)

    def complete_page(self):
        if not self.lot:
            return
        total = sum(c["quantity"] for c in self.lot)
        vacant = (SLOTS_PER_PAGE - (total % SLOTS_PER_PAGE)) % SLOTS_PER_PAGE
        if vacant == 0:
            self.set_status("La dernière page est déjà complète")
            return
        self.lot[-1]["quantity"] += vacant
        self.refresh_gallery()
        self.update_stats()
        self.autosave()
        self.set_status("+" + str(vacant) + " ajoutés pour compléter la page")

    def update_stats(self):
        total = sum(c["quantity"] for c in self.lot)
        if total == 0:
            self.stats_total.config(text="0 sticker", fg="#555")
            self.stats_pages.config(text="0 page A4", fg="#444")
            self.stats_alert.config(text="Créez votre première carte pour commencer", fg="#555")

            self.btn_final.config(
                state="disabled",
                bg="#2A2A40",
                fg="#555",
                activebackground="#2A2A40",
                cursor="arrow"
            )
            return

        pages = math.ceil(total / SLOTS_PER_PAGE)
        vacant = (SLOTS_PER_PAGE - (total % SLOTS_PER_PAGE)) % SLOTS_PER_PAGE
        self.stats_total.config(text=str(total) + " stickers  ·  " + str(len(self.lot)) + " modèles", fg="#AAA")
        self.stats_pages.config(text=str(pages) + " page(s) A4 paysage", fg="#888")
        if vacant > 0:
            self.stats_alert.config(text=str(vacant) + " places libres sur la dernière page",
                                    fg="#F39C12", bg="#16162A")
        else:
            self.stats_alert.config(text="OK  Lot optimal — prêt pour l'impression",
                                    fg="#2ECC71", bg="#16162A")

        self.btn_final.config(
            state="normal",
            bg="#1F5EFF",
            fg="white",
            activebackground="#1447CC",
            cursor="hand2"
        )