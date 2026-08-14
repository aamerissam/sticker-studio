# qr_generator.py
import qrcode
from PIL import Image, ImageDraw, ImageChops
from reportlab.lib.colors import HexColor


def generate_qr_pil(url, accent_hex, target_px=300):
    c = HexColor(accent_hex)
    accent = (int(c.red * 255), int(c.green * 255), int(c.blue * 255))
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="white", back_color=(0, 0, 0, 0)).convert("RGBA")
    logo_ratio = 0.22
    logo_size = int(min(qr_img.size) * logo_ratio)
    logo = Image.new("RGBA", (logo_size, logo_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(logo)
    draw.ellipse([0, 0, logo_size - 1, logo_size - 1], fill=(255, 255, 255, 255))
    pad = int(logo_size * 0.18)
    inner = logo_size - 2 * pad
    radius = max(3, inner // 5)
    draw.rounded_rectangle([pad, pad, pad + inner, pad + inner],
                           radius=radius, fill=accent + (255,), outline=accent + (255,))
    obj = int(inner * 0.50)
    ox = (logo_size - obj) // 2
    oy = (logo_size - obj) // 2
    draw.ellipse([ox, oy, ox + obj, oy + obj], fill=(255, 255, 255, 255))
    obj_in = int(obj * 0.45)
    oix = (logo_size - obj_in) // 2
    oiy = (logo_size - obj_in) // 2
    draw.ellipse([oix, oiy, oix + obj_in, oiy + obj_in], fill=accent + (255,))
    flash = max(2, int(inner * 0.12))
    fx = pad + inner - flash - max(2, int(inner * 0.08))
    fy = pad + max(2, int(inner * 0.08))
    draw.ellipse([fx, fy, fx + flash, fy + flash], fill=(255, 255, 255, 255))
    pos = ((qr_img.size[0] - logo_size) // 2, (qr_img.size[1] - logo_size) // 2)
    qr_img.paste(logo, pos, logo)
    corner_radius = int(min(qr_img.size) * 0.08)
    mask = Image.new("L", qr_img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([0, 0, qr_img.size[0] - 1, qr_img.size[1] - 1],
                                radius=corner_radius, fill=255)
    r, g, b, a = qr_img.split()
    a = ImageChops.multiply(a, mask)
    qr_img = Image.merge("RGBA", (r, g, b, a))
    return qr_img.resize((target_px, target_px), Image.LANCZOS)


def generate_qr_file(url, accent_hex, out_path, target_px=300):
    generate_qr_pil(url, accent_hex, target_px).save(out_path)
    return out_path