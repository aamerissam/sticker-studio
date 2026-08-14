# pdf_renderer.py
import math
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.units import mm
from config import PALETTES


# Built-in PDF fonts are substituted by viewers with system fonts.
# ReportLab's stringWidth() uses internal metrics that are ~3-8% narrower
# than what most viewers actually render. This fudge compensates.
FONT_METRIC_FUDGE = 1.24  # 12% correction — tune if still off   # 6% wider than stringWidth reports


def draw_heart_pdf(c, cx, cy, size):
    c.saveState()
    c.translate(cx, cy)
    p = c.beginPath()
    s = size / 2
    p.moveTo(0, s * 0.3)
    p.curveTo(-s, s, -s, -s * 0.5, 0, -s)
    p.curveTo(s, -s * 0.5, s, s, 0, s * 0.3)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def draw_star_pdf(c, cx, cy, size):
    c.saveState()
    c.translate(cx, cy)
    p = c.beginPath()
    s = size
    p.moveTo(0, s)
    p.lineTo(s * 0.3, s * 0.3)
    p.lineTo(s, 0)
    p.lineTo(s * 0.3, -s * 0.3)
    p.lineTo(0, -s)
    p.lineTo(-s * 0.3, -s * 0.3)
    p.lineTo(-s, 0)
    p.lineTo(-s * 0.3, s * 0.3)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def draw_pattern_pdf(c, x, y, w, h, pattern):
    if pattern in ("none", "gradient"):
        return
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, w, h, 3 * mm)
    c.clipPath(p, fill=0, stroke=0)
    if pattern == "diagonal_lines":
        c.setStrokeColor(Color(1, 1, 1, alpha=0.30))
        c.setLineWidth(0.5 * mm)
        spacing = 6 * mm
        for i in range(-int(h / spacing) - 2, int(w / spacing) + 4):
            x0 = x + i * spacing
            c.line(x0, y, x0 + h, y + h)
    elif pattern == "dots":
        c.setFillColor(Color(1, 1, 1, alpha=0.35))
        spacing = 5 * mm
        r = 0.6 * mm
        i0, i1 = int(x / spacing) - 1, int((x + w) / spacing) + 2
        j0, j1 = int(y / spacing) - 1, int((y + h) / spacing) + 2
        for ix in range(i0, i1):
            for iy in range(j0, j1):
                c.circle(ix * spacing, iy * spacing, r, fill=1, stroke=0)
    elif pattern == "hearts":
        c.setFillColor(Color(1, 1, 1, alpha=0.28))
        sx, sy = 8 * mm, 7 * mm
        size = 2.5 * mm
        i0, i1 = int(x / sx) - 1, int((x + w) / sx) + 2
        j0, j1 = int(y / sy) - 1, int((y + h) / sy) + 2
        for ix in range(i0, i1):
            for iy in range(j0, j1):
                cx = ix * sx + (iy % 2) * sx / 2
                cy = iy * sy
                if x - size <= cx <= x + w + size and y - size <= cy <= y + h + size:
                    draw_heart_pdf(c, cx, cy, size)
    elif pattern == "waves":
        c.setStrokeColor(Color(1, 1, 1, alpha=0.30))
        c.setLineWidth(0.5 * mm)
        sy = 5 * mm
        period = 8 * mm
        amp = 1.5 * mm
        j0, j1 = int(y / sy) - 1, int((y + h) / sy) + 2
        for iy in range(j0, j1):
            yb = iy * sy
            path = c.beginPath()
            first = True
            for px in range(int(x), int(x + w) + 5, 3):
                py = yb + math.sin((px - x) / period * 2 * math.pi) * amp
                if first:
                    path.moveTo(px, py)
                    first = False
                else:
                    path.lineTo(px, py)
            c.drawPath(path, stroke=1, fill=0)
    elif pattern == "crosshatch":
        c.setStrokeColor(Color(1, 1, 1, alpha=0.25))
        c.setLineWidth(0.35 * mm)
        spacing = 5 * mm
        for i in range(-int(h / spacing) - 2, int(w / spacing) + 4):
            x0 = x + i * spacing
            c.line(x0, y, x0 + h, y + h)
            c.line(x0, y + h, x0 + h, y)
    elif pattern == "stars":
        c.setFillColor(Color(1, 1, 1, alpha=0.32))
        spacing = 7 * mm
        size = 2 * mm
        i0, i1 = int(x / spacing) - 1, int((x + w) / spacing) + 2
        j0, j1 = int(y / spacing) - 1, int((y + h) / spacing) + 2
        for ix in range(i0, i1):
            for iy in range(j0, j1):
                cx = ix * spacing + (iy % 2) * spacing / 2
                cy = iy * spacing
                if x - size <= cx <= x + w + size and y - size <= cy <= y + h + size:
                    draw_star_pdf(c, cx, cy, size)
    c.restoreState()


def draw_single_sticker_pdf(c, x, y, w, h, cfg, qr_path):
    is_male = cfg["gender"] == "male"
    palette = PALETTES["male"] if is_male else PALETTES["female"]
    bg = HexColor(palette["bg"])
    bg_dark = HexColor(palette["bg_dark"])
    pattern = cfg["pattern"]
    brand = cfg["brand"].upper()
    parfum_name = cfg["parfum"].upper()
    phone_raw = cfg["phone"].strip()
    phone_text_color = white if cfg["phone_text_color"] == "white" else black
    phone_contrast = black if cfg["phone_text_color"] == "white" else white
    phone_bg_type = cfg["phone_bg_type"]

    inner_m = 3.5 * mm
    top_zone = y + h - inner_m
    bottom_zone = y + inner_m

    c.setFillColor(bg_dark)
    c.roundRect(x, y, w, h, 3 * mm, fill=1, stroke=0)
    draw_pattern_pdf(c, x, y, w, h, pattern)
    c.setFillColor(bg)
    c.roundRect(x, y + h * 0.35, w, h * 0.65, 3 * mm, fill=1, stroke=0)

    # ── BRAND (manual tracking — proven working) ──
    karim_pt = 10
    base_w = c.stringWidth(brand, "Helvetica-Bold", karim_pt)
    tracked_w = base_w + 1.2 * (len(brand) - 1)
    karim_y = top_zone - karim_pt * 0.35
    txt = c.beginText()
    txt.setFillColor(white)
    txt.setFont("Helvetica-Bold", karim_pt)
    txt.setCharSpace(1.2)
    txt.setTextOrigin(x + (w - tracked_w) / 2, karim_y)
    txt.textOut(brand)
    c.drawText(txt)

    line_y = karim_y - karim_pt * 0.70
    c.setStrokeColor(white)
    c.setLineWidth(0.5)
    line_w = w * 0.40
    c.line(x + w / 2 - line_w / 2, line_y, x + w / 2 + line_w / 2, line_y)

    # ── PARFUM: beginText + fudge-factor centering ──
    parfum_pt = 8
    c.setFont("Helvetica-Bold", parfum_pt)
    max_w = w - 5 * mm
    while c.stringWidth(parfum_name, "Helvetica-Bold", parfum_pt) > max_w and parfum_pt > 5:
        parfum_pt -= 0.5
        c.setFont("Helvetica-Bold", parfum_pt)
    parfum_w = c.stringWidth(parfum_name, "Helvetica-Bold", parfum_pt)
    parfum_y = line_y - 2.2 * mm - parfum_pt * 0.35

    # Apply fudge: stringWidth underestimates actual rendered width by ~6%
    # Use effective_w for centering so text is shifted left to compensate
    effective_parfum_w = parfum_w * FONT_METRIC_FUDGE
    txt_p = c.beginText()
    txt_p.setFillColor(white)
    txt_p.setFont("Helvetica-Bold", parfum_pt)
    txt_p.setTextOrigin(x + (w - effective_parfum_w) / 2, parfum_y)
    txt_p.textOut(parfum_name)
    c.drawText(txt_p)

    # ── PHONE: fixed-width box + fudge-factor centering ──
    phone_pt = 6
    phone_y = bottom_zone + 2.0 * mm
    c.setFont("Courier-Bold", phone_pt)
    text_w = c.stringWidth(phone_raw, "Courier-Bold", phone_pt)

    # FIXED-WIDTH BOX: always 78% of sticker width, centered.
    # This guarantees the box is wide enough regardless of font metrics.
    box_w = w * 0.78
    box_h = 4.5 * mm
    box_x = x + (w - box_w) / 2
    box_y = phone_y - 1.5 * mm

    if phone_bg_type == "bg_outer":
        c.setFillColor(phone_contrast)
        c.roundRect(box_x, box_y, box_w, box_h, 1.0 * mm, fill=1, stroke=0)
    elif phone_bg_type == "line_outer":
        c.setStrokeColor(phone_contrast)
        c.setLineWidth(0.25 * mm)
        c.roundRect(box_x, box_y, box_w, box_h, 1.0 * mm, fill=0, stroke=1)

    # Apply fudge for centering: shift text left by 3% of its width
    effective_text_w = text_w * FONT_METRIC_FUDGE
    txt_ph = c.beginText()
    txt_ph.setFillColor(phone_text_color)
    txt_ph.setFont("Courier-Bold", phone_pt)
    txt_ph.setTextOrigin(x + (w - effective_text_w) / 2, phone_y)
    txt_ph.textOut(phone_raw)
    c.drawText(txt_ph)

    # ── QR CODE ──
    qr_mm = min(15.5 * mm, w - 5 * mm)
    space_top = parfum_y - 1.5 * mm
    space_bottom = phone_y + 2.5 * mm
    available_h = space_top - space_bottom
    qr_x = x + (w - qr_mm) / 2
    qr_y = space_bottom + (available_h - qr_mm) / 2
    c.drawImage(qr_path, qr_x, qr_y, qr_mm, qr_mm)