# pdf_controller.py
import os
import math
import tempfile
import datetime
from tkinter import messagebox, filedialog
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from config import SLOTS_PER_PAGE, COLS, ROWS, PALETTES
from qr_generator import generate_qr_file
from pdf_renderer import draw_single_sticker_pdf


class PDFControllerMixin:
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
            self.set_status("Génération annulée")
            return
        self.set_status("Génération du PDF en cours...")
        self.root.update_idletasks()
        try:
            PAGE_W, PAGE_H = landscape(A4)
            # FIX #4: margins reduced by 80%
            MARGIN = 2 * mm       # was 10 mm
            GAP = 0.4 * mm        # was 2 mm
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
            msg = "PDF généré avec succès :\n" + file_path + "\n\n" + str(total) + " stickers · " + str(pages) + " page(s)"
            if vacant > 0:
                msg = msg + "\n" + str(vacant) + " places vacantes sur la dernière page"
            self.stats_alert.config(text="OK PDF généré !", fg="#2ECC71")
            self.set_status("PDF généré avec succès")
            messagebox.showinfo("Succès", msg)
        except Exception as e:
            self.set_status("Erreur : " + str(e), error=True)
            messagebox.showerror("Erreur", "La génération a échoué :\n" + str(e))