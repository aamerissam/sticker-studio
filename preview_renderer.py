# preview_renderer.py
import math
from PIL import Image, ImageDraw
from config import PALETTES


def draw_heart_pil(draw, cx, cy, size, color):
    s = size
    draw.ellipse([cx - s * 0.5, cy, cx, cy + s * 0.5], fill=color)
    draw.ellipse([cx, cy, cx + s * 0.5, cy + s * 0.5], fill=color)
    draw.polygon([(cx - s * 0.5, cy), (cx + s * 0.5, cy), (cx, cy - s * 0.6)], fill=color)


def draw_star_pil(draw, cx, cy, size, color):
    s = size
    draw.polygon([(cx, cy - s), (cx + s * 0.3, cy - s * 0.3), (cx + s, cy),
                  (cx + s * 0.3, cy + s * 0.3), (cx, cy + s), (cx - s * 0.3, cy + s * 0.3),
                  (cx - s, cy), (cx - s * 0.3, cy - s * 0.3)], fill=color)


def draw_pattern_pil(W, H, pattern, px_per_mm):
    if pattern in ("none", "gradient"):
        return None
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    wt = (255, 255, 255)
    if pattern == "diagonal_lines":
        spacing = 6 * px_per_mm
        for i in range(-int(H / spacing) - 2, int(W / spacing) + 4):
            x0 = i * spacing
            draw.line([(x0, 0), (x0 + H, H)], fill=(*wt, 75), width=2)
    elif pattern == "dots":
        spacing = 5 * px_per_mm
        r = int(0.6 * px_per_mm)
        for ix in range(0, int(W / spacing) + 2):
            for iy in range(0, int(H / spacing) + 2):
                cx, cy = int(ix * spacing), int(iy * spacing)
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*wt, 85))
    elif pattern == "hearts":
        sx, sy = 8 * px_per_mm, 7 * px_per_mm
        size = 2.5 * px_per_mm
        for ix in range(0, int(W / sx) + 2):
            for iy in range(0, int(H / sy) + 2):
                cx = ix * sx + (iy % 2) * sx / 2
                cy = iy * sy
                draw_heart_pil(draw, cx, cy, size, (*wt, 65))
    elif pattern == "waves":
        sy = 5 * px_per_mm
        period = 8 * px_per_mm
        amp = 1.5 * px_per_mm
        for iy in range(0, int(H / sy) + 2):
            yb = iy * sy
            points = [(px, yb + math.sin(px / period * 2 * math.pi) * amp)
                      for px in range(0, int(W) + 5, 3)]
            if len(points) > 1:
                draw.line(points, fill=(*wt, 75), width=2)
    elif pattern == "crosshatch":
        spacing = 5 * px_per_mm
        for i in range(-int(H / spacing) - 2, int(W / spacing) + 4):
            x0 = i * spacing
            draw.line([(x0, 0), (x0 + H, H)], fill=(*wt, 60), width=1)
            draw.line([(x0, H), (x0 + H, 0)], fill=(*wt, 60), width=1)
    elif pattern == "stars":
        spacing = 7 * px_per_mm
        size = 2 * px_per_mm
        for ix in range(0, int(W / spacing) + 2):
            for iy in range(0, int(H / spacing) + 2):
                cx = ix * spacing + (iy % 2) * spacing / 2
                cy = iy * spacing
                draw_star_pil(draw, cx, cy, size, (*wt, 75))
    return layer.transpose(Image.FLIP_TOP_BOTTOM)


def render_preview(cfg, brand, parfum, phone, insta, get_font_func, qr_cache_func):
    """Renders the PIL preview image for the sticker."""
    is_male = cfg["gender"] == "male"
    pattern = cfg["pattern"]
    pal = PALETTES["male"] if is_male else PALETTES["female"]
    bg = hex_to_rgb(pal["bg"])
    bg_dark = hex_to_rgb(pal["bg_dark"])
    phone_text_color = cfg["phone_text_color"]
    phone_bg_type = cfg["phone_bg_type"]
    phone_color_rgb = (255, 255, 255) if phone_text_color == "white" else (0, 0, 0)
    contrast_rgb = (0, 0, 0) if phone_text_color == "white" else (255, 255, 255)
    W, H = 360, 500
    sticker_w_mm = 33.1
    px_per_mm = W / sticker_w_mm
    sticker = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sticker)
    draw.rounded_rectangle([0, 0, W, H], radius=20, fill=bg_dark)
    pattern_layer = draw_pattern_pil(W, H, pattern, px_per_mm)
    if pattern_layer:
        sticker.paste(pattern_layer, (0, 0), pattern_layer)
    overlay_h = int(H * 0.65)
    draw.rounded_rectangle([0, 0, W, overlay_h], radius=20, fill=bg)
    qr_size = 150
    try:
        qr_img = qr_cache_func(insta, pal["accent_hex"], qr_size)
    except Exception:
        qr_img = Image.new("RGBA", (qr_size, qr_size), (255, 255, 255, 128))
    f_title = get_font_func("arialbd.ttf", 34)
    f_name = get_font_func("arialbd.ttf", 24)
    f_phone = get_font_func("courbd.ttf", 20)
    inner_m = 24
    top_zone = inner_m
    bottom_zone = H - inner_m
    karim_y = top_zone + 8
    total_w = 0
    chars = list(brand)
    spacing = 3
    for ch in chars:
        total_w += draw.textbbox((0, 0), ch, font=f_title)[2] + spacing
    total_w -= spacing
    cx = (W - total_w) / 2
    for ch in chars:
        draw.text((cx, karim_y), ch, fill="white", font=f_title)
        cx += draw.textbbox((0, 0), ch, font=f_title)[2] + spacing
    line_y = karim_y + 38
    line_w = W * 0.38
    draw.line([(W/2 - line_w/2, line_y), (W/2 + line_w/2, line_y)], fill="white", width=3)
    parfum_y = line_y + 20
    bbox = draw.textbbox((0, 0), parfum, font=f_name)
    tw = bbox[2] - bbox[0]
    if tw > W - 50:
        f_name = get_font_func("arialbd.ttf", 20)
        bbox = draw.textbbox((0, 0), parfum, font=f_name)
        tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, parfum_y), parfum, fill="white", font=f_name)
    phone_y = bottom_zone - 30
    bbox = draw.textbbox((0, 0), phone, font=f_phone)
    tw_phone = bbox[2] - bbox[0]
    pad_px = 5
    box_h_px = 24
    box_x = (W - tw_phone) / 2 - pad_px
    box_y = phone_y - pad_px
    box_w = tw_phone + 2 * pad_px
    if phone_bg_type == "bg_outer":
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h_px],
                               radius=3, fill=contrast_rgb)
    elif phone_bg_type == "line_outer":
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h_px],
                               radius=3, outline=contrast_rgb, width=2)
    draw.text(((W - tw_phone) / 2, phone_y), phone, fill=phone_color_rgb, font=f_phone)
    parfum_bottom = parfum_y + (bbox[3] - bbox[1]) + 8
    phone_top = phone_y - 8
    available_h = phone_top - parfum_bottom
    qr_y = parfum_bottom + (available_h - qr_size) / 2
    qr_x = (W - qr_size) / 2
    sticker.paste(qr_img, (int(qr_x), int(qr_y)), qr_img)
    preview_w, preview_h = 280, 390
    preview_img = sticker.resize((preview_w, preview_h), Image.LANCZOS)
    framed = Image.new("RGBA", (preview_w + 30, preview_h + 30), (14, 14, 26, 255))
    rim = ImageDraw.Draw(framed)
    rim.rectangle([14, 14, 14 + preview_w + 1, 14 + preview_h + 1], outline=(255, 255, 255, 40))
    framed.paste(preview_img, (15, 15), preview_img)
    return framed


def hex_to_rgb(hx):
    return tuple(int(hx[i:i+2], 16) for i in (1, 3, 5))