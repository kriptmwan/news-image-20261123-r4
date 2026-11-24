#!/usr/bin/env python3
"""Round-4 entry for make.fun news-image-20261123.

Draws one 1024x1024 PNG newspaper front page summing up the world news of
Monday 23 November 2026, using Pillow only. No network, no clock, no
randomness: the same run always writes the same bytes.

Layout (all sizes in pixels, canvas 1024x1024):
  masthead  + dateline rule          (y 24-158)
  lead story: Nvidia / Huang         (y 170-438, art panel right)
  four horizontal bands, one story each:
    COP31 collapse / Poland drone / Dymer strike / Hormuz mines
  bottom ticker strip with four one-liners (y 906-992)

Every headline and deck is set large enough to stay legible when the page is
shown about 300 pixels across: smallest body text is 27 px, headlines 40-54 px.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 26
INK = (20, 20, 20)
PAPER = (246, 241, 229)
RED = (178, 32, 44)
GREY = (90, 86, 76)
GREEN = (20, 83, 45)
NAVY = (28, 47, 87)
TEAL = (16, 92, 96)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_rule(d, x0, x1, y, width=2, fill=INK):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


def art_lead(d, x0, y0, x1, y1):
    """Nvidia lead art: dark green panel, chip, rising line with a gap."""
    d.rectangle([x0, y0, x1, y1], fill=GREEN)
    d.rectangle([x0, y0, x1, y0 + 10], fill=(255, 255, 255))
    # chip outline, left of panel
    cx0, cy0, cx1, cy1 = x0 + 26, y0 + 34, x0 + 150, y0 + 158
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=10,
                        outline=(255, 255, 255), width=5)
    for px in (cx0 + 34, cx0 + 62, cx0 + 90):
        d.line([(px, cy0 - 12), (px, cy0)], fill=(255, 255, 255), width=4)
        d.line([(px, cy1), (px, cy1 + 12)], fill=(255, 255, 255), width=4)
    for py in (cy0 + 34, cy0 + 62, cy0 + 90):
        d.line([(cx0 - 12, py), (cx0, py)], fill=(255, 255, 255), width=4)
        d.line([(cx1, py), (cx1 + 12, py)], fill=(255, 255, 255), width=4)
    d.rounded_rectangle([cx0 + 28, cy0 + 28, cx1 - 28, cy1 - 28], radius=6,
                        outline=(255, 255, 255), width=4)
    # rising chart line across the panel, with a dip (the 11-day gap)
    pts = [(x0 + 170, y1 - 78), (x0 + 215, y1 - 96), (x0 + 250, y1 - 88),
           (x0 + 285, y1 - 130), (x0 + 308, y1 - 150), (x0 + 326, y1 - 178)]
    d.line(pts, fill=(255, 255, 255), width=6, joint="curve")
    for (px, py) in pts:
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(255, 255, 255))
    # gap marker: dashed drop between the second and third point
    d.line([(x0 + 215, y1 - 96), (x0 + 215, y1 - 66)],
           fill=(255, 214, 64), width=3)
    d.line([(x0 + 250, y1 - 88), (x0 + 250, y1 - 66)],
           fill=(255, 214, 64), width=3)
    f_small = font(SANS_B, 22)
    d.text((x0 + 168, y1 - 128), "11 DAYS", font=f_small, fill=(255, 214, 64))
    f_big = font(SANS_B, 62)
    d.text((x0 + 26, y1 - 72), "+31%", font=f_big, fill=(255, 255, 255))


def art_cop31(d, x0, y0, x1, y1):
    """COP31: pale sky, sun, cracked dry earth."""
    d.rectangle([x0, y0, x1, y1], fill=(232, 217, 160))
    d.rectangle([x0, y0 + 46, x1, y1], fill=(196, 164, 110))
    d.ellipse([x0 + 118, y0 + 8, x0 + 152, y0 + 42], fill=(214, 122, 44))
    # cracks in the earth
    crack = (122, 84, 52)
    d.line([(x0 + 30, y0 + 62), (x0 + 52, y0 + 78), (x0 + 44, y0 + 96)],
           fill=crack, width=4, joint="curve")
    d.line([(x0 + 52, y0 + 78), (x0 + 78, y0 + 84)], fill=crack, width=4)
    d.line([(x0 + 110, y0 + 58), (x0 + 96, y0 + 80), (x0 + 118, y0 + 98)],
           fill=crack, width=4, joint="curve")
    d.line([(x0 + 96, y0 + 80), (x0 + 70, y0 + 88)], fill=crack, width=4)
    d.line([(x0 + 140, y0 + 70), (x0 + 150, y0 + 92)], fill=crack, width=4)


def art_poland(d, x0, y0, x1, y1):
    """Poland: radar screen, sweep, one red blip crossing a border line."""
    d.rectangle([x0, y0, x1, y1], fill=NAVY)
    cx, cy = x0 + 85, y0 + 54
    for r in (22, 38, 52):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=(96, 196, 110), width=3)
    d.line([(cx, cy), (cx + 40, cy - 34)], fill=(96, 196, 110), width=3)
    # dashed border crossing the screen
    for i in range(0, 170, 14):
        d.line([(x0 + i, y0 + 18), (x0 + i + 8, y0 + 18)],
               fill=(255, 255, 255), width=3)
    d.ellipse([cx + 34, cy - 40, cx + 46, cy - 28], fill=(235, 64, 52))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(96, 196, 110))


def art_dymer(d, x0, y0, x1, y1):
    """Dymer: dusk skyline, one lit window, a rescue beam."""
    d.rectangle([x0, y0, x1, y1], fill=(64, 74, 96))
    d.rectangle([x0 + 14, y0 + 44, x0 + 58, y1], fill=(32, 34, 44))
    d.rectangle([x0 + 66, y0 + 28, x0 + 118, y1], fill=(32, 34, 44))
    d.rectangle([x0 + 126, y0 + 56, x0 + 156, y1], fill=(32, 34, 44))
    # one warm lit window in the left block (clear of the beam)
    d.rectangle([x0 + 30, y0 + 60, x0 + 44, y0 + 74], fill=(255, 196, 64))
    # rescue beam from the top corner
    d.polygon([(x0 + 150, y0), (x0 + 170, y0), (x0 + 96, y0 + 62),
               (x0 + 84, y0 + 62)], fill=(255, 226, 130))
    d.ellipse([x0 + 8, y0 + 10, x0 + 26, y0 + 28], fill=(226, 226, 214))


def art_hormuz(d, x0, y0, x1, y1):
    """Hormuz: teal sea, tanker silhouette, two spiked mines, waves."""
    d.rectangle([x0, y0, x1, y1], fill=TEAL)
    # waves
    for wy in (y0 + 78, y0 + 92):
        d.arc([x0 + 8, wy - 8, x0 + 52, wy + 8], 180, 360,
              fill=(255, 255, 255), width=3)
        d.arc([x0 + 62, wy - 8, x0 + 106, wy + 8], 180, 360,
              fill=(255, 255, 255), width=3)
        d.arc([x0 + 116, wy - 8, x0 + 160, wy + 8], 180, 360,
              fill=(255, 255, 255), width=3)
    # tanker
    d.polygon([(x0 + 34, y0 + 62), (x0 + 132, y0 + 62), (x0 + 122, y0 + 78),
               (x0 + 44, y0 + 78)], fill=(24, 28, 36))
    d.rectangle([x0 + 96, y0 + 44, x0 + 118, y0 + 62], fill=(24, 28, 36))
    d.rectangle([x0 + 102, y0 + 34, x0 + 108, y0 + 44], fill=(24, 28, 36))
    # spiked mines
    for mx, my in ((x0 + 22, y0 + 30), (x0 + 146, y0 + 24)):
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (1, -1), (-1, 1), (1, 1)):
            d.line([(mx, my), (mx + dx * 12, my + dy * 12)],
                   fill=(20, 20, 20), width=3)
        d.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=(20, 20, 20))


def band(d, y0, h, art_fn, kicker, headline, deck):
    """One horizontal story band: art left, text right."""
    x0, x1 = MARGIN, W - MARGIN
    art_w = 170
    d.rectangle([x0, y0, x0 + art_w, y0 + h], fill=(255, 255, 255))
    art_fn(d, x0, y0, x0 + art_w, y0 + h)
    d.rectangle([x0, y0, x0 + art_w, y0 + h], outline=INK, width=2)
    tx = x0 + art_w + 18
    tw = x1 - tx
    f_kick = font(SANS_B, 22)
    f_head = font(SERIF_B, 38)
    f_dek = font(SANS, 30)
    d.text((tx, y0 + 6), kicker, font=f_kick, fill=RED)
    d.text((tx, y0 + 32), headline, font=f_head, fill=INK)
    d.text((tx, y0 + 74), deck, font=f_dek, fill=(52, 50, 44))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN

    # --- masthead ---
    f_name = font(SERIF_B, 62)
    name = "THE WORLD IN ONE PAGE"
    d.text(((W - text_w(d, name, f_name)) / 2, 30), name, font=f_name, fill=INK)
    draw_rule(d, x0, x1, 112, width=3)
    # --- dateline rule ---
    f_date = font(SANS_B, 36)
    f_tag = font(SANS_B, 26)
    d.text((x0, 124), "MONDAY 23 NOVEMBER 2026", font=f_date, fill=INK)
    tag = "ONE DAY  ·  ONE PAGE"
    d.text((x1 - text_w(d, tag, f_tag), 130), tag, font=f_tag, fill=RED)
    draw_rule(d, x0, x1, 164, width=5)

    # --- lead story: Nvidia ---
    ly0, ly1 = 176, 438
    tx = x0
    tw = 606  # text column stops 20 px short of the art panel at x=652
    f_kick = font(SANS_B, 26)
    f_head = font(SERIF_B, 42)
    f_dek = font(SANS, 32)
    d.text((tx, ly0 + 6), "TECHNOLOGY — SANTA CLARA", font=f_kick, fill=RED)
    head_lines = wrap(d, "Huang returns as Nvidia chief; shares jump 31%",
                      f_head, tw)
    d.multiline_text((tx, ly0 + 38), "\n".join(head_lines), font=f_head,
                     fill=INK, spacing=4)
    dek = ("Board reinstates its founder 11 days after his exit. "
           "Trump says he pressed for it.")
    lines = wrap(d, dek, f_dek, tw)
    dek_y = ly0 + 38 + len(head_lines) * 46 + 16
    d.multiline_text((tx, dek_y), "\n".join(lines), font=f_dek,
                     fill=(52, 50, 44), spacing=6)
    art_lead(d, 652, ly0, x1, ly1)
    d.rectangle([652, ly0, x1, ly1], outline=INK, width=2)

    # --- story bands ---
    y = 450
    band_h = 104
    gap = 10
    band(d, y, band_h, art_cop31, "CLIMATE — ANTALYA, TURKEY",
         "COP31 ends with no deal",
         "Fossil-fuel deadlock sinks the talks in Antalya.")
    y += band_h + gap
    band(d, y, band_h, art_poland, "WAR — POLAND",
         "Russian drone crosses into Poland",
         "NATO meets in emergency session in Brussels.")
    y += band_h + gap
    band(d, y, band_h, art_dymer, "WAR — UKRAINE",
         "Strike on Dymer kills 11",
         "Boy, 7, pulled alive after 14 hours in rubble.")
    y += band_h + gap
    band(d, y, band_h, art_hormuz, "MIDDLE EAST — STRAIT OF HORMUZ",
         "Three tankers hit mines in Hormuz",
         "Trump warns of a \u201cvery traumatic\u201d outcome.")
    y += band_h + gap  # y == 906

    # --- ticker strip ---
    ty0, ty1 = y, 992
    d.rectangle([x0, ty0, x1, ty1], fill=(20, 20, 20))
    f_tick = font(SANS_B, 26)
    d.text((x0 + 14, ty0 + 8),
           "ALSO: Thai–Cambodia truce holds • Nigeria boat sinks, 24 dead",
           font=f_tick, fill=(255, 255, 255))
    d.text((x0 + 14, ty0 + 44),
           "GTA VI: $3.8bn day one • Pakistan astronaut to Tiangong",
           font=f_tick, fill=(255, 255, 255))
    draw_rule(d, x0, x1, 1000, width=2, fill=GREY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), format="PNG", optimize=True)


if __name__ == "__main__":
    main()
