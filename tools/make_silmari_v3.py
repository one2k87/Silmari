"""Silmari channel art v3: simple vector yarn ball with one thread running out.

All strokes share one colour and one thickness.
Usage: python3 tools/make_silmari_v3.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

from make_channel_art import (BANNER, OUT, PREVIEW, ROW_MAX_WIDTH, SANS_KR, SERIF_KR, SILMARI,
                              font, round_line, save_previews, vertical_gradient)

THREAD = SILMARI["thread"]
PAPER = SILMARI["paper"]


def arc_points(cx, cy, r, a0, a1, steps=200):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / steps), cy + r * math.sin(a0 + (a1 - a0) * i / steps))
            for i in range(steps + 1)]


def yarn_ball(layer, cx, cy, r, width, tail_to_x, color=THREAD):
    """Circle + three wound bands + one crossing band, then the thread leaving along the baseline."""
    size = layer.size
    inner = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(inner)
    for k in (0.62, 1.02, 1.42):  # bands wound one way
        round_line(d, arc_points(cx - 1.05 * r, cy - 1.05 * r, (1.05 * math.sqrt(2) - 1 + k) * r, 0, math.pi / 2), color, width)
    round_line(d, arc_points(cx + 1.25 * r, cy - 0.95 * r, 1.42 * r, math.pi / 2, math.pi * 1.05), color, width)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    layer.paste(inner, (0, 0), Image.composite(inner.getchannel("A"), Image.new("L", size, 0), mask))
    d = ImageDraw.Draw(layer)
    round_line(d, arc_points(cx, cy, r, 0, 2 * math.pi, 360), color, width)
    base_y = cy + r
    tail = [(cx + (tail_to_x - cx) * i / 60, base_y) for i in range(61)]
    round_line(d, tail, color, width)


def draw_symbol(size, bg=None):
    s = size * 2
    img = Image.new("RGBA", (s, s), (bg + (255,)) if bg else (0, 0, 0, 0))
    yarn_ball(img, s * 0.40, s * 0.45, s * 0.215, s * 0.050, s * 0.84)
    return img.resize((size, size), Image.LANCZOS)


def banner():
    w, h = BANNER
    img = vertical_gradient(BANNER, SILMARI["bg2"], SILMARI["bg"]).convert("RGBA")
    yarn_ball(img, 300, 1010, 120, 13, w + 60)
    d = ImageDraw.Draw(img)
    title, tagline = "뉴스 실마리", "엉킨 뉴스, 첫 끝부터 풉니다"
    scale = 1.0
    for _ in range(2):
        sym = round(200 * scale)
        f_title, f_tag = font(SERIF_KR, round(176 * scale)), font(SANS_KR, round(50 * scale))
        gap, div_gap = round(46 * scale), round(48 * scale)
        tw, gw = d.textlength(title, font=f_title), d.textlength(tagline, font=f_tag)
        total = sym + gap + tw + div_gap * 2 + 4 + gw
        if total <= ROW_MAX_WIDTH:
            break
        scale *= ROW_MAX_WIDTH / total
    x, cy = (w - total) / 2, h / 2
    big = draw_symbol(sym * 3)
    symbol = big.crop(big.getbbox())
    symbol.thumbnail((sym, sym), Image.LANCZOS)
    img.alpha_composite(symbol, (round(x + (sym - symbol.width) / 2), round(cy - symbol.height / 2)))
    d = ImageDraw.Draw(img)
    x += sym + gap
    d.text((x, cy), title, font=f_title, fill=PAPER, anchor="lm")
    x += tw + div_gap
    d.line([(x, cy - 70 * scale), (x, cy + 70 * scale)], fill=THREAD, width=4)
    x += 4 + div_gap
    d.text((x, cy + 4), tagline, font=f_tag, fill=(214, 208, 198), anchor="lm")
    return img.convert("RGB")


def main():
    logo = draw_symbol(1024, bg=SILMARI["bg"]).convert("RGB")
    logo.save(OUT / "silmari_logo_C.png")
    logo.resize((300, 300), Image.LANCZOS).save(OUT / "silmari_watermark_C.png")
    bn = banner()
    bn.save(OUT / "silmari_banner_C.png")
    save_previews("silmari_C", bn)
    sheet = Image.new("RGB", (712, 512), (30, 30, 30))
    mask = Image.new("L", (512, 512), 0)
    ImageDraw.Draw(mask).ellipse((6, 6, 506, 506), fill=255)
    sheet.paste(logo.resize((512, 512), Image.LANCZOS), (0, 0), mask)
    small = logo.resize((96, 96), Image.LANCZOS)
    m2 = Image.new("L", (96, 96), 0)
    ImageDraw.Draw(m2).ellipse((0, 0, 95, 95), fill=255)
    sheet.paste(small, (564, 208), m2)
    sheet.save(PREVIEW / "silmari_C_logo_circle.jpg", quality=90)
    print("ok")


if __name__ == "__main__":
    main()
