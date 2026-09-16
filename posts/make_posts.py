# -*- coding: utf-8 -*-
"""
Картинки для постов NG Hive.

    python posts/make_posts.py

Для каждого приложения кладёт рядом два файла:
    <app>-facebook.png   2048×2048 — Facebook пережимает всё, что меньше,
                         и мелкий текст на макетах расплывается
    <app>-instagram.png  1080×1080 — родной размер Instagram

Макет описан в «логических» координатах квадрата 1080×1080, а рисуется
сразу в двойном размере (SCALE) и только потом уменьшается — поэтому
буквы и края остаются чёткими, а не растянутыми.
"""

import math
import os
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BASE = 1080          # логический размер макета
SCALE = 2            # во сколько раз крупнее рисуем на самом деле
OUTPUTS = {"facebook": 2048, "instagram": 1080}

HONEY = (242, 177, 52)
HONEY_DEEP = (224, 154, 21)
INK = (47, 48, 51)

F_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
F_SEMI = "C:/Windows/Fonts/seguisb.ttf"
F_REG = "C:/Windows/Fonts/segoeui.ttf"


def P(v):
    """Логические пиксели → настоящие."""
    return int(round(v * SCALE))


def font(path, size):
    return ImageFont.truetype(path, P(size))


def new(mode, w, h, color=0):
    return Image.new(mode, (P(w), P(h)), color)


class Canvas:
    """ImageDraw, который принимает логические координаты."""

    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    @staticmethod
    def _pts(pts):
        return [(P(x), P(y)) for x, y in pts]

    @staticmethod
    def _box(box):
        return [P(v) for v in box]

    def rrect(self, box, r, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(self._box(box), radius=P(r), fill=fill,
                                 outline=outline, width=P(width) if outline else 0)

    def line(self, pts, fill, width=1, joint=None):
        self.d.line(self._pts(pts), fill=fill, width=P(width), joint=joint)

    def polygon(self, pts, fill=None, outline=None, width=1):
        self.d.polygon(self._pts(pts), fill=fill, outline=outline, width=P(width))

    def ellipse(self, box, fill):
        self.d.ellipse(self._box(box), fill=fill)

    def length(self, s, f):
        return self.d.textlength(s, font=f) / SCALE

    def text(self, xy, s, f, fill, anchor="la", tracking=0):
        x, y = xy
        if not tracking:
            self.d.text((P(x), P(y)), s, font=f, fill=fill, anchor=anchor)
            return
        widths = [self.length(ch, f) for ch in s]
        total = sum(widths) + tracking * (len(s) - 1)
        if anchor[0] == "m":
            x -= total / 2
        for ch, w in zip(s, widths):
            self.d.text((P(x), P(y)), ch, font=f, fill=fill, anchor="l" + anchor[1])
            x += w + tracking


# ─────────────────────────── фон ───────────────────────────

def gradient(w, h, top, bottom, mode="RGB"):
    img = new(mode, w, h)
    d = ImageDraw.Draw(img)
    rows = img.height
    for y in range(rows):
        t = y / max(rows - 1, 1)
        d.line([(0, y), (img.width, y)],
               fill=tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img


def hexagon(cx, cy, r):
    return [(cx + r * math.cos(math.radians(60 * i - 30)),
             cy + r * math.sin(math.radians(60 * i - 30))) for i in range(6)]


def honeycomb(img, color, width=2, r=78, alpha=38):
    """Сетка сот поверх фона — фирменный узор с логотипа."""
    layer = new("RGBA", BASE, BASE, (0, 0, 0, 0))
    c = Canvas(layer)
    w, h = math.sqrt(3) * r, r * 1.5
    row, y = -1, -r
    while y < BASE + r:
        x = -w if row % 2 == 0 else -w / 2
        while x < BASE + w:
            c.polygon(hexagon(x, y, r), outline=color + (alpha,), width=width)
            x += w
        y += h
        row += 1
    return Image.alpha_composite(img.convert("RGBA"), layer)


def glow(img, cx, cy, radius, color, alpha=150):
    """Мягкое медовое свечение за макетом."""
    layer = new("RGBA", BASE, BASE, (0, 0, 0, 0))
    c = Canvas(layer)
    steps = 26
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        a = int(alpha * (1 - i / steps) ** 1.7)
        c.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(P(40)))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def pill(c, cx, y, label, f, bg, fg, pad=(46, 24)):
    w = c.length(label, f) + pad[0] * 2
    h = f.size / SCALE + pad[1] * 2
    c.rrect([cx - w / 2, y, cx + w / 2, y + h], h / 2, fill=bg)
    c.text((cx, y + h / 2), label, f, fg, anchor="mm")


# ─────────────────────────── макеты устройств ───────────────────────────

def rounded_mask(w, h, r):
    m = new("L", w, h, 0)
    Canvas(m).rrect([0, 0, w - 0.5, h - 0.5], r, fill=255)
    return m


def body(w, h, r, top=(226, 230, 235), bottom=(138, 145, 153)):
    """Металлический корпус устройства."""
    g = gradient(w, h, top, bottom)
    g.putalpha(rounded_mask(w, h, r))
    return g


def shadow(img, box, r, blur=30, alpha=90, dy=18):
    layer = new("RGBA", BASE, BASE, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    Canvas(layer).rrect([x0, y0 + dy, x1, y1 + dy], r, fill=(20, 22, 26, alpha))
    return Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(P(blur))))


def watch(img, cx, cy):
    """Apple Watch с экраном будильника."""
    w, h, r = 300, 364, 84
    x0, y0 = cx - w / 2, cy - h / 2

    band = new("RGBA", BASE, BASE, (0, 0, 0, 0))
    cb = Canvas(band)
    cb.rrect([cx - 104, y0 - 150, cx + 104, y0 + 60], 40, fill=(48, 52, 58, 255))
    cb.rrect([cx - 104, y0 + h - 60, cx + 104, y0 + h + 118], 40, fill=(40, 44, 50, 255))
    img = Image.alpha_composite(img, band)

    img = shadow(img, [x0, y0, x0 + w, y0 + h], r, blur=34, alpha=105)
    img.alpha_composite(body(w, h, r), (P(x0), P(y0)))
    Canvas(img).rrect([x0 + w - 4, cy - 44, x0 + w + 8, cy + 6], 6, fill=(198, 204, 211, 255))

    sw, sh = w - 44, h - 44
    scr = new("RGBA", sw, sh, (0, 0, 0, 0))
    c = Canvas(scr)
    c.rrect([0, 0, sw - 0.5, sh - 0.5], r - 20, fill=(15, 17, 20, 255))
    m = sw / 2
    c.text((m, 70), "Alarm", font(F_SEMI, 25), (150, 157, 167, 255), anchor="mm")
    c.text((m, 148), "06:40", font(F_BOLD, 92), HONEY + (255,), anchor="mm")
    c.text((m, 214), "30 min window", font(F_REG, 24), (130, 137, 147, 255), anchor="mm")
    c.line([(28, 268), (70, 268), (86, 236), (104, 296), (122, 268), (166, 268),
            (182, 244), (198, 288), (214, 268), (sw - 28, 268)],
           fill=HONEY + (255,), width=7, joint="curve")
    img.alpha_composite(scr, (P(x0 + 22), P(y0 + 22)))
    return img


def phone_frame(img, cx, cy, w=346, h=624):
    x0, y0 = cx - w / 2, cy - h / 2
    img = shadow(img, [x0, y0, x0 + w, y0 + h], 62, blur=38, alpha=100)
    img.alpha_composite(body(w, h, 62), (P(x0), P(y0)))
    return img, (x0 + 17, y0 + 17, w - 34, h - 34)


def phone_screen(img, frame, draw_content):
    sx, sy, sw, sh = frame
    scr = new("RGBA", sw, sh, (255, 255, 255, 255))
    c = Canvas(scr)
    c.rrect([sw / 2 - 48, 20, sw / 2 + 48, 44], 12, fill=(22, 24, 28, 255))
    draw_content(scr, c, sw, sh)
    img.paste(scr, (P(sx), P(sy)), rounded_mask(sw, sh, 44))
    return img


def shopping_screen(scr, c, sw, sh):
    c.text((28, 74), "Costco", font(F_BOLD, 36), INK + (255,))
    c.polygon(hexagon(sw - 44, 92, 14), fill=HONEY + (255,))

    f_row = font(F_SEMI, 25)
    y = 140
    for label, done in [("Milk 2%", False), ("Coffee beans", False),
                        ("Paper towels", True), ("AA batteries", False)]:
        c.rrect([22, y, sw - 22, y + 60], 18, fill=(243, 244, 246, 255))
        box = [40, y + 19, 62, y + 41]
        green = (46, 158, 87, 255)
        if done:
            c.rrect(box, 7, outline=green, width=3)
            c.line([(45, y + 30), (51, y + 36), (58, y + 24)], fill=green, width=4)
        else:
            c.rrect(box, 7, outline=(178, 184, 192, 255), width=3)
        col = (168, 174, 182, 255) if done else INK + (255,)
        c.text((78, y + 30), label, f_row, col, anchor="lm")
        if done:
            c.line([(78, y + 28), (78 + c.length(label, f_row), y + 28)], fill=col, width=3)
        y += 72

    c.rrect([22, sh - 126, sw - 22, sh - 32], 22, fill=HONEY_DEEP + (255,))
    c.rrect([22, sh - 132, sw - 22, sh - 38], 22, fill=HONEY + (255,))
    c.text((44, sh - 98), "You're near Costco", font(F_BOLD, 26), INK + (255,), anchor="lm")
    c.text((44, sh - 64), "4 items on your list", font(F_REG, 22), (96, 80, 44, 255), anchor="lm")


def collage_screen(scr, c, sw, sh):
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
        tile = gradient(w, h, c1, c2)
        scr.paste(tile, (P(x), P(y)), rounded_mask(w, h, 15).resize(tile.size))

    c.rrect([pad, sh - 98, sw - pad, sh - 36], 22, fill=HONEY + (255,))
    c.text((sw / 2, sh - 67), "Save", font(F_BOLD, 27), INK + (255,), anchor="mm")


def phone_shopping(img, cx, cy):
    img, frame = phone_frame(img, cx, cy)
    return phone_screen(img, frame, shopping_screen)


def phone_collage(img, cx, cy):
    img, frame = phone_frame(img, cx, cy)
    return phone_screen(img, frame, collage_screen)


# ─────────────────────────── общая обвязка ───────────────────────────

def brand_mark(img, dark):
    logo = Image.open(os.path.join(ROOT, "assets", "logo-200.jpg")).convert("RGB")
    c = Canvas(img)
    if dark:
        card = new("RGBA", 128, 128, (255, 255, 255, 255))
        card.paste(logo.resize((P(104), P(104)), Image.LANCZOS), (P(12), P(12)))
        img.paste(card, (P(66), P(60)), rounded_mask(128, 128, 30))
        x = 214
    else:
        logo = logo.resize((P(104), P(104)), Image.LANCZOS)
        box = (P(72), P(70), P(72) + logo.width, P(70) + logo.height)
        img.paste(ImageChops.multiply(img.convert("RGB").crop(box), logo), box[:2])
        x = 190
    col = (255, 255, 255, 255) if dark else INK + (255,)
    c.text((x, 122), "NG HIVE", font(F_BOLD, 34), col, anchor="lm", tracking=5)
    return img


def compose(name, tagline, device, dark=False, accent_note=None):
    if dark:
        img = gradient(BASE, BASE, (28, 31, 36), (17, 19, 23))
        img = honeycomb(img, HONEY, width=2, alpha=30)
        img = glow(img, BASE / 2, 430, 430, HONEY, alpha=115)
        title_col, sub_col = (255, 255, 255, 255), (172, 178, 187, 255)
        pill_bg, pill_fg = HONEY + (255,), INK + (255,)
    else:
        img = gradient(BASE, BASE, (255, 255, 255), (232, 235, 239))
        img = honeycomb(img, (150, 156, 164), width=2, alpha=42)
        img = glow(img, BASE / 2, 430, 430, HONEY, alpha=95)
        title_col, sub_col = INK + (255,), (104, 110, 118, 255)
        pill_bg, pill_fg = INK + (255,), (255, 255, 255, 255)

    img = img.convert("RGBA")
    img = brand_mark(img, dark)
    img = device(img, BASE / 2, 430)

    c = Canvas(img)
    c.text((BASE / 2, 830), name, font(F_BOLD, 80), title_col, anchor="mm")
    c.text((BASE / 2, 900), tagline, font(F_REG, 37), sub_col, anchor="mm")
    if accent_note:
        c.text((BASE / 2, 947), accent_note, font(F_SEMI, 29), HONEY + (255,), anchor="mm")
        pill(c, BASE / 2, 985, "Now on the App Store", font(F_SEMI, 28), pill_bg, pill_fg, pad=(40, 18))
    else:
        pill(c, BASE / 2, 955, "Now on the App Store", font(F_SEMI, 30), pill_bg, pill_fg, pad=(44, 22))

    img = img.convert("RGB")
    slug = name.lower().replace(".", "").replace(" ", "-")
    for target, size in OUTPUTS.items():
        out = os.path.join(HERE, "%s-%s.png" % (slug, target))
        img.resize((size, size), Image.LANCZOS).save(out, optimize=True)
        print("saved", out, "%d KB" % (os.path.getsize(out) // 1024))


if __name__ == "__main__":
    compose("WhatchAlarm", "Wakes you at the lightest moment of sleep", watch, dark=True)
    compose("ShopPing", "Your list reminds you right at the store", phone_shopping)
    compose("H.Collage", "A collage of 2–10 photos in a minute",
            phone_collage, accent_note="…and a second layer only you know about")
