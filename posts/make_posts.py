# -*- coding: utf-8 -*-
"""
Картинки для постов NG Hive (Instagram / Facebook, 1080×1080).

    python posts/make_posts.py

Кладёт три PNG рядом с собой. Всё рисуется кодом — правится здесь же,
никаких внешних редакторов не нужно.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SIZE = 1080

HONEY = (242, 177, 52)
HONEY_DEEP = (224, 154, 21)
INK = (47, 48, 51)
STEEL = (169, 174, 181)

F_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
F_SEMI = "C:/Windows/Fonts/seguisb.ttf"
F_REG = "C:/Windows/Fonts/segoeui.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ─────────────────────────── фон ───────────────────────────

def vertical_gradient(top, bottom):
    img = Image.new("RGB", (SIZE, SIZE), top)
    d = ImageDraw.Draw(img)
    for y in range(SIZE):
        t = y / (SIZE - 1)
        d.line([(0, y), (SIZE, y)],
               fill=tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def hexagon(cx, cy, r):
    return [(cx + r * math.cos(math.radians(60 * i - 30)),
             cy + r * math.sin(math.radians(60 * i - 30))) for i in range(6)]


def honeycomb(img, color, width=2, r=78, alpha=38):
    """Сетка сот поверх фона — фирменный узор с логотипа."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = math.sqrt(3) * r, r * 1.5
    row = -1
    y = -r
    while y < SIZE + r:
        x = -w if row % 2 == 0 else -w / 2
        while x < SIZE + w:
            d.polygon(hexagon(x, y, r), outline=color + (alpha,), width=width)
            x += w
        y += h
        row += 1
    return Image.alpha_composite(img.convert("RGBA"), layer)


def glow(img, cx, cy, radius, color, alpha=150):
    """Мягкое медовое свечение за макетом."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 26
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        a = int(alpha * (1 - i / steps) ** 1.7)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(40))
    return Image.alpha_composite(img.convert("RGBA"), layer)


# ─────────────────────────── текст ───────────────────────────

def text(d, xy, s, f, fill, anchor="la", tracking=0):
    if not tracking:
        d.text(xy, s, font=f, fill=fill, anchor=anchor)
        return
    widths = [d.textlength(ch, font=f) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    for ch, w in zip(s, widths):
        d.text((x, y), ch, font=f, fill=fill, anchor="l" + anchor[1])
        x += w + tracking


def pill(d, cx, y, label, f, bg, fg, pad=(46, 24)):
    w = d.textlength(label, font=f) + pad[0] * 2
    h = f.size + pad[1] * 2
    box = [cx - w / 2, y, cx + w / 2, y + h]
    d.rounded_rectangle(box, radius=h / 2, fill=bg)
    d.text((cx, y + h / 2), label, font=f, fill=fg, anchor="mm")
    return h


# ─────────────────────────── макеты устройств ───────────────────────────

def body_gradient(w, h, radius, c_top=(226, 230, 235), c_bot=(138, 145, 153)):
    """Металлический корпус устройства."""
    grad = Image.new("RGB", (w, h))
    dg = ImageDraw.Draw(grad)
    for y in range(h):
        t = y / max(h - 1, 1)
        dg.line([(0, y), (w, y)],
                fill=tuple(round(c_top[i] + (c_bot[i] - c_top[i]) * t) for i in range(3)))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
    grad.putalpha(mask)
    return grad


def shadow(img, box, radius, blur=30, alpha=90, offset=(0, 18)):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]],
                        radius=radius, fill=(20, 22, 26, alpha))
    return Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(blur)))


def watch(img, cx, cy):
    cx, cy = int(cx), int(cy)
    """Apple Watch с экраном будильника."""
    w, h, r = 300, 364, 84
    x0, y0 = cx - w // 2, cy - h // 2
    # ремешок
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    db = ImageDraw.Draw(band)
    db.rounded_rectangle([cx - 104, y0 - 150, cx + 104, y0 + 60], radius=40, fill=(48, 52, 58, 255))
    db.rounded_rectangle([cx - 104, y0 + h - 60, cx + 104, y0 + h + 118], radius=40, fill=(40, 44, 50, 255))
    img = Image.alpha_composite(img, band)

    img = shadow(img, [x0, y0, x0 + w, y0 + h], r, blur=34, alpha=105)
    img.alpha_composite(body_gradient(w, h, r), (x0, y0))

    # колёсико
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0 + w - 4, cy - 44, x0 + w + 8, cy + 6], radius=6, fill=(198, 204, 211, 255))

    scr = Image.new("RGBA", (w - 44, h - 44), (0, 0, 0, 0))
    ds = ImageDraw.Draw(scr)
    ds.rounded_rectangle([0, 0, scr.width - 1, scr.height - 1], radius=r - 20, fill=(15, 17, 20, 255))
    m = scr.width // 2
    text(ds, (m, 70), "Alarm", font(F_SEMI, 25), (150, 157, 167, 255), anchor="mm")
    text(ds, (m, 148), "06:40", font(F_BOLD, 92), HONEY + (255,), anchor="mm")
    text(ds, (m, 214), "30 min window", font(F_REG, 24), (130, 137, 147, 255), anchor="mm")
    pts = [(28, 268), (70, 268), (86, 236), (104, 296), (122, 268), (166, 268),
           (182, 244), (198, 288), (214, 268), (scr.width - 28, 268)]
    ds.line(pts, fill=HONEY + (255,), width=7, joint="curve")
    img.alpha_composite(scr, (x0 + 22, y0 + 22))
    return img


def phone_frame(img, cx, cy, w=346, h=624):
    cx, cy = int(cx), int(cy)
    x0, y0 = cx - w // 2, cy - h // 2
    img = shadow(img, [x0, y0, x0 + w, y0 + h], 62, blur=38, alpha=100)
    img.alpha_composite(body_gradient(w, h, 62), (x0, y0))
    return img, (x0 + 17, y0 + 17, w - 34, h - 34)


def phone_shopping(img, cx, cy):
    img, (sx, sy, sw, sh) = phone_frame(img, cx, cy)
    scr = Image.new("RGBA", (sw, sh), (255, 255, 255, 255))
    d = ImageDraw.Draw(scr)
    d.rounded_rectangle([sw / 2 - 48, 20, sw / 2 + 48, 44], radius=12, fill=(22, 24, 28, 255))

    text(d, (28, 74), "Costco", font(F_BOLD, 36), INK + (255,))
    d.polygon(hexagon(sw - 44, 92, 14), fill=HONEY + (255,))

    rows = [("Milk 2%", False), ("Coffee beans", False),
            ("Paper towels", True), ("AA batteries", False)]
    f_row = font(F_SEMI, 25)
    y = 140
    for label, done in rows:
        d.rounded_rectangle([22, y, sw - 22, y + 60], radius=18, fill=(243, 244, 246, 255))
        box = [40, y + 19, 62, y + 41]
        if done:
            d.rounded_rectangle(box, radius=7, outline=(46, 158, 87, 255), width=3)
            d.line([(45, y + 30), (51, y + 36), (58, y + 24)], fill=(46, 158, 87, 255), width=4)
        else:
            d.rounded_rectangle(box, radius=7, outline=(178, 184, 192, 255), width=3)
        col = (168, 174, 182, 255) if done else INK + (255,)
        text(d, (78, y + 30), label, font(F_SEMI, 25), col, anchor="lm")
        if done:
            tw = d.textlength(label, font=f_row)
            d.line([(78, y + 31), (78 + tw, y + 31)], fill=col, width=3)
        y += 72

    toast = [22, sh - 132, sw - 22, sh - 32]
    d.rounded_rectangle([toast[0], toast[1] + 6, toast[2], toast[3]], radius=22, fill=HONEY_DEEP + (255,))
    d.rounded_rectangle([toast[0], toast[1], toast[2], toast[3] - 6], radius=22, fill=HONEY + (255,))
    text(d, (44, sh - 98), "You're near Costco", font(F_BOLD, 26), INK + (255,), anchor="lm")
    text(d, (44, sh - 64), "4 items on your list", font(F_REG, 22), (96, 80, 44, 255), anchor="lm")

    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=44, fill=255)
    img.paste(scr, (sx, sy), mask)
    return img


def phone_collage(img, cx, cy):
    img, (sx, sy, sw, sh) = phone_frame(img, cx, cy)
    scr = Image.new("RGBA", (sw, sh), (255, 255, 255, 255))
    d = ImageDraw.Draw(scr)
    d.rounded_rectangle([sw / 2 - 48, 20, sw / 2 + 48, 44], radius=12, fill=(22, 24, 28, 255))

    pad, gap = 22, 10
    top, bottom = 76, sh - 116
    gw, gh = sw - pad * 2, bottom - top
    half = (gh - gap) / 2
    third = (gw - gap * 2) / 3
    cells = [
        (pad, top, gw / 2 - gap / 2, half, ((242, 177, 52), (224, 123, 57))),
        (pad + gw / 2 + gap / 2, top, gw / 2 - gap / 2, half, ((127, 178, 229), (63, 111, 168))),
        (pad, top + half + gap, third, half, ((168, 213, 162), (79, 143, 99))),
        (pad + third + gap, top + half + gap, third, half, ((229, 162, 182), (168, 86, 111))),
        (pad + (third + gap) * 2, top + half + gap, third, half, ((201, 205, 211), (125, 131, 140))),
    ]
    for x, y, w, h, (c1, c2) in cells:
        tile = Image.new("RGB", (max(int(w), 1), max(int(h), 1)))
        dt = ImageDraw.Draw(tile)
        for i in range(tile.height):
            t = i / max(tile.height - 1, 1)
            dt.line([(0, i), (tile.width, i)],
                    fill=tuple(round(c1[k] + (c2[k] - c1[k]) * t) for k in range(3)))
        m = Image.new("L", tile.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, tile.width - 1, tile.height - 1], radius=15, fill=255)
        scr.paste(tile, (int(x), int(y)), m)

    d.rounded_rectangle([pad, sh - 98, sw - pad, sh - 36], radius=22, fill=HONEY + (255,))
    text(d, (sw / 2, sh - 67), "Save", font(F_BOLD, 27), INK + (255,), anchor="mm")

    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=44, fill=255)
    img.paste(scr, (sx, sy), mask)
    return img


# ─────────────────────────── общая обвязка ───────────────────────────

def brand_mark(img, dark):
    logo = Image.open(os.path.join(ROOT, "assets", "logo-200.jpg")).convert("RGB").resize((104, 104), Image.LANCZOS)
    if dark:
        card = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
        card.paste(logo, (12, 12))
        m = Image.new("L", (128, 128), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, 127, 127], radius=30, fill=255)
        img.paste(card, (66, 60), m)
        x = 214
    else:
        from PIL import ImageChops
        back = img.convert("RGB").crop((72, 70, 176, 174))
        img.paste(ImageChops.multiply(back, logo), (72, 70))
        x = 190
    d = ImageDraw.Draw(img)
    col = (255, 255, 255, 255) if dark else INK + (255,)
    text(d, (x, 122), "NG HIVE", font(F_BOLD, 34), col, anchor="lm", tracking=5)
    return img


def compose(name, tagline, device, dark=False, accent_note=None):
    if dark:
        img = vertical_gradient((28, 31, 36), (17, 19, 23))
        img = honeycomb(img, HONEY, width=2, alpha=30)
        img = glow(img, SIZE / 2, 430, 430, HONEY, alpha=115)
        title_col, sub_col = (255, 255, 255, 255), (172, 178, 187, 255)
        pill_bg, pill_fg = HONEY + (255,), INK + (255,)
    else:
        img = vertical_gradient((255, 255, 255), (232, 235, 239))
        img = honeycomb(img, (150, 156, 164), width=2, alpha=42)
        img = glow(img, SIZE / 2, 430, 430, HONEY, alpha=95)
        title_col, sub_col = INK + (255,), (104, 110, 118, 255)
        pill_bg, pill_fg = INK + (255,), (255, 255, 255, 255)

    img = img.convert("RGBA")
    img = brand_mark(img, dark)
    img = device(img, SIZE // 2, 430)

    d = ImageDraw.Draw(img)
    text(d, (SIZE / 2, 830), name, font(F_BOLD, 80), title_col, anchor="mm")
    text(d, (SIZE / 2, 900), tagline, font(F_REG, 37), sub_col, anchor="mm")
    if accent_note:
        text(d, (SIZE / 2, 947), accent_note, font(F_SEMI, 29), HONEY + (255,), anchor="mm")
        pill(d, SIZE / 2, 985, "Now on the App Store", font(F_SEMI, 28), pill_bg, pill_fg, pad=(40, 18))
    else:
        pill(d, SIZE / 2, 955, "Now on the App Store", font(F_SEMI, 30), pill_bg, pill_fg, pad=(44, 22))

    out = os.path.join(HERE, "%s.png" % name.lower().replace(".", "").replace(" ", "-"))
    img.convert("RGB").save(out, quality=95)
    print("saved", out)


if __name__ == "__main__":
    compose("WhatchAlarm", "Wakes you at the lightest moment of sleep", watch, dark=True)
    compose("ShopPing", "Your list reminds you right at the store", phone_shopping)
    compose("H.Collage", "A collage of 2–10 photos in a minute",
            phone_collage, accent_note="…and a second layer only you know about")
