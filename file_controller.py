# file_controller.py
import os
import json
import datetime
from tkinter import messagebox, filedialog
from config import AUTOSAVE_PATH


class FileControllerMixin:
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
                self.set_status("Lot sauvegardé")
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
                        self.set_status("Lot chargé")
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