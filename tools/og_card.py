"""Draw link-preview images (Open Graph cards) for build.py.

LinkedIn, Slack and other apps show a 1200x630 image when someone shares a link.
Each card shows the page title, Jeffrey's name and role, the site address and, when
the page has a cover image, that image on the right. Cards are saved as JPEG, which
every platform accepts (WebP is not reliably supported for previews).
"""
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1200, 630
PAD = 72
BG = (255, 255, 255)
INK = (24, 24, 27)        # --text
MUTED = (82, 82, 91)      # --muted
ACCENT = (47, 75, 201)    # --accent
BORDER = (228, 228, 231)  # --border

FONT = os.path.join(os.path.dirname(__file__), "fonts", "Geist-Variable.ttf")


def _font(size, weight):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_name(weight)
    return f


def _wrap(text, font, width):
    """Split text into lines that fit within width pixels."""
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if font.getlength(trial) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def make_card(out_path, title, eyebrow, image_path=None):
    card = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(card)

    text_w = W - 2 * PAD
    if image_path:
        # Cover image on the right, cropped to fill a rounded panel.
        panel = (700, PAD, W - PAD, H - PAD)
        pw, ph = panel[2] - panel[0], panel[3] - panel[1]
        with Image.open(image_path) as src:
            src = src.convert("RGB")
            if src.width / src.height > 1.3:
                # Wide images (charts, desktop screens): show whole, centered on grey.
                img = Image.new("RGB", (pw, ph), (244, 244, 245))
                fitted = ImageOps.contain(src, (pw - 32, ph - 32), Image.LANCZOS)
                img.paste(fitted, ((pw - fitted.width) // 2, (ph - fitted.height) // 2))
            else:
                img = ImageOps.fit(src, (pw, ph), Image.LANCZOS)
        mask = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), radius=18, fill=255)
        card.paste(img, panel[:2], mask)
        draw.rounded_rectangle(panel, radius=18, outline=BORDER, width=2)
        text_w = panel[0] - PAD - 48

    draw.text((PAD, PAD), eyebrow, font=_font(26, "Medium"), fill=MUTED)

    # Largest title size (down to 44px) that fits in four lines.
    for size in (68, 60, 52, 44):
        title_font = _font(size, "SemiBold")
        lines = _wrap(title, title_font, text_w)
        if len(lines) <= 4:
            break
    y = PAD + 70
    for line in lines[:4]:
        draw.text((PAD, y), line, font=title_font, fill=INK)
        y += int(size * 1.15)

    draw.text((PAD, H - PAD - 30), "jeffsoh.com", font=_font(28, "SemiBold"), fill=ACCENT)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    card.save(out_path, "JPEG", quality=86, optimize=True, progressive=True)
