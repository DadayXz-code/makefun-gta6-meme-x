#!/usr/bin/env python3
"""Generate meme.png for gta6-meme-x-01 — pure PIL, deterministic, no network.

Design (original, drawn from scratch, no copied assets):
  A GTA-style loading screen stuck at 99% after 13 years of waiting,
  with make.fun's ghost in the picture.
  1200x675 (16:9, X-friendly). Run: python3 generate-meme.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
W, H = 1200, 675
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(size, top, bottom):
    """Vertical gradient, deterministic."""
    img = Image.new("RGB", size)
    px = img.load()
    w, h = size
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(w):
            px[x, y] = c
    return img


def hgrad(size, left, right):
    img = Image.new("RGB", size)
    px = img.load()
    w, h = size
    for x in range(w):
        t = x / max(w - 1, 1)
        c = tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3))
        for y in range(h):
            px[x, y] = c
    return img


def text_center(d, y, s, f, fill, stroke=0, stroke_fill=(0, 0, 0)):
    box = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
    w = box[2] - box[0]
    d.text(((W - w) / 2 - box[0], y), s, font=f, fill=fill,
           stroke_width=stroke, stroke_fill=stroke_fill)


def draw_ghost(d, x0, y0, x1, y1):
    """Original simple sheet-ghost: round head, straight body, wavy hem."""
    # body
    d.ellipse([x0, y0, x1, y0 + (x1 - x0)], fill=(255, 255, 255))
    d.rectangle([x0, y0 + (x1 - x0) // 2, x1, y1 - 18], fill=(255, 255, 255))
    # wavy hem: 3 scallops
    w = x1 - x0
    pts = [(x0, y1 - 18)]
    for i in range(3):
        ax = x0 + w * i / 3
        bx = x0 + w * (i + 1) / 3
        pts += [(ax, y1 - 18), ((ax + bx) / 2, y1), (bx, y1 - 18)]
    pts += [(x1, y1 - 18)]
    d.polygon(pts, fill=(255, 255, 255))
    # eyes
    cx = (x0 + x1) // 2
    cy = y0 + (x1 - x0) // 2 - 6
    d.ellipse([cx - 26, cy - 14, cx - 8, cy + 14], fill=(10, 10, 30))
    d.ellipse([cx + 8, cy - 14, cx + 26, cy + 14], fill=(10, 10, 30))
    # smile
    d.arc([cx - 16, cy + 18, cx + 16, cy + 44], start=15, end=165,
          fill=(10, 10, 30), width=4)


def main():
    img = vgrad((W, H), (11, 16, 38), (43, 16, 68))
    d = ImageDraw.Draw(img)

    # sunset strip at the bottom
    strip = hgrad((W, 26), (255, 46, 136), (255, 176, 66))
    img.paste(strip, (0, H - 26))

    # header
    text_center(d, 34, "G R A N D   T H E F T   A U T O   V I", font(BOLD, 34),
                (245, 245, 245))
    text_center(d, 84, "VICE CITY  •  LEONIDA", font(REG, 26), (255, 214, 102))
    text_center(d, 128, "LOADING...", font(BOLD, 108), (255, 255, 255),
                stroke=2)

    # progress bar: 99% stuck (gradient fill clipped to the rounded outline)
    bx0, bx1, by, bh = 150, 1050, 268, 48
    fill_w = int((bx1 - bx0 - 8) * 0.99)
    bar = hgrad((fill_w, bh - 8), (255, 46, 136), (64, 224, 255))
    mask = Image.new("L", (bx1 - bx0, bh), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, bx1 - bx0 - 1, bh - 1], radius=24, fill=255)
    img.paste(bar, (bx0 + 4, by + 4), mask.crop((4, 4, 4 + fill_w, bh - 4)))
    d.rounded_rectangle([bx0, by, bx1, by + bh], radius=24,
                        outline=(255, 255, 255), width=4)
    d.text((bx1 + 14, by - 2), "99%", font=font(BOLD, 40), fill=(255, 255, 255))

    # the joke: elapsed vs remaining
    text_center(d, 344, "Elapsed: 13 years  —  4,811 days", font(BOLD, 38),
                (255, 255, 255))
    text_center(d, 398, "Time remaining:  Soon\u2122", font(BOLD, 38),
                (255, 224, 102))

    # divider
    d.line([(150, 470), (1050, 470)], fill=(255, 255, 255), width=2)

    # make.fun ghost + pitch (ghost is IN the picture, as the bounty requires)
    draw_ghost(d, 150, 500, 250, 620)
    d.text((275, 508), "make.fun", font=font(BOLD, 52), fill=(255, 255, 255))
    d.text((275, 572), "my AI agent earns here while I wait",
           font=font(REG, 28), fill=(207, 207, 207))

    # small print bottom-right
    s = "waiting since 2013"
    box = d.textbbox((0, 0), s, font=font(REG, 24))
    d.text((W - 40 - (box[2] - box[0]), 596), s, font=font(REG, 24),
           fill=(160, 160, 190))

    out = HERE / "meme.png"
    img.save(out, "PNG")
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    sys.exit(main())
