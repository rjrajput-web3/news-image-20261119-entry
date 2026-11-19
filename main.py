#!/usr/bin/env python3
"""news-image-20261119 entry: draw a front page summing up Thursday
19 November 2026 world news, and write it to /output/entry.png.

Pure standard library: a hand-built 5x7 bitmap font, a small raster
canvas, and a minimal PNG encoder. No network, no randomness, no
timestamps, so two runs write byte-identical output.

Layout (1024x1024): navy masthead, a four-number stats strip, a hero
row of three stories (Shenzhen summit, GTA VI, Anthropic listing),
a 2x3 grid of story cards, then a world-map panel beside an
"In Brief" list, and a footer ticker.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# Palette: newspaper paper, ink, navy masthead, red accents, gold rules.
PAPER = (246, 241, 231)
INK = (20, 20, 20)
NAVY = (20, 38, 77)
NAVY_LIGHT = (38, 62, 110)
STEEL = (110, 140, 180)
RED = (179, 32, 44)
GOLD = (184, 148, 60)
GREY = (90, 88, 82)
WHITE = (255, 255, 255)
CREAM = (252, 249, 240)
GREEN = (34, 120, 70)

# 5x7 bitmap font, uppercase only. Each glyph is 7 rows of 5 cells,
# '#' is ink, '.' is blank.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#..##", "#..##"),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}

CHAR_W = 5
CHAR_H = 7


class Canvas:
    """A plain RGB raster canvas, origin top-left."""

    def __init__(self, width, height, color):
        self.w = width
        self.h = height
        self.px = bytearray(color * (width * height))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.set(x, y, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ellipse(self, cx, cy, rx, ry, color):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                dx = (xx - cx) / max(rx, 1)
                dy = (yy - cy) / max(ry, 1)
                if dx * dx + dy * dy <= 1.0:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d <= (r + thick) ** 2:
                    self.set(xx, yy, color)

    def text(self, x, y, s, scale, color):
        """Draw uppercase text; returns the width in pixels."""
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(CHAR_H):
                bits = glyph[row]
                for col in range(CHAR_W):
                    if bits[col] == "#":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += (CHAR_W + 1) * scale
        return cx - x - scale

    def text_width(self, s, scale):
        return len(s) * (CHAR_W + 1) * scale - scale

    def centered(self, cx, y, s, scale, color):
        w = self.text_width(s, scale)
        self.text(cx - w // 2, y, s, scale, color)

    def wrap(self, x, y, text, scale, color, max_w, line_h=None):
        """Word-wrap text inside max_w pixels; returns y after last line."""
        if line_h is None:
            line_h = CHAR_H * scale + 4
        words = text.split(" ")
        line = ""
        for word in words:
            trial = (line + " " + word).strip()
            if self.text_width(trial, scale) <= max_w or not line:
                line = trial
            else:
                self.text(x, y, line, scale, color)
                y += line_h
                line = word
        if line:
            self.text(x, y, line, scale, color)
            y += line_h
        return y


def png_bytes(canvas):
    """Encode the canvas as a whole PNG (RGB, 8-bit, filter 0)."""
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        start = y * canvas.w * 3
        raw += canvas.px[start:start + canvas.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ----------------------------------------------------------------------
# Small drawn icons: flags, a game controller, a rising chart, scales
# of justice, a tanker, a bridge, a flame and a globe.
# ----------------------------------------------------------------------

def draw_us_flag(c, x, y, w, h):
    stripe_h = max(1, h // 13)
    for i in range(13):
        c.rect(x, y + i * stripe_h, w, stripe_h,
               RED if i % 2 == 0 else WHITE)
    cw, ch = int(w * 0.4), stripe_h * 7
    c.rect(x, y, cw, ch, NAVY)
    for r in range(4):
        for col in range(5):
            sx = x + 6 + col * (cw - 12) // 4
            sy = y + 5 + r * (ch - 10) // 3
            c.rect(sx, sy, 3, 3, WHITE)


def draw_russia_flag(c, x, y, w, h):
    third = h // 3
    c.rect(x, y, w, third, WHITE)
    c.rect(x, y + third, w, third, (0, 57, 166))
    c.rect(x, y + 2 * third, w, h - 2 * third, RED)


def draw_china_flag(c, x, y, w, h):
    c.rect(x, y, w, h, (222, 41, 16))
    c.circle(x + int(w * 0.22), y + int(h * 0.28), 9, (255, 222, 0))
    for sx, sy in ((0.62, 0.16), (0.78, 0.30), (0.72, 0.52), (0.55, 0.62)):
        c.circle(x + int(w * sx), y + int(h * sy), 4, (255, 222, 0))


def draw_controller(c, x, y, s):
    c.rect(x, y + 4 * s, 44 * s, 22 * s, INK)
    c.rect(x + 2 * s, y, 40 * s, 6 * s, INK)
    c.rect(x + 2 * s, y + 24 * s, 40 * s, 4 * s, INK)
    c.circle(x + 13 * s, y + 15 * s, 4 * s, WHITE)
    c.circle(x + 31 * s, y + 15 * s, 4 * s, WHITE)
    c.rect(x + 9 * s, y + 11 * s, 3 * s, 9 * s, RED)
    c.rect(x + 6 * s, y + 14 * s, 9 * s, 3 * s, RED)


def draw_chart(c, x, y, w, h):
    # Axes, rising bars and a steep green trend line.
    c.rect(x, y, w, h, (235, 240, 235))
    c.vline(x + 8, y + 6, h - 14, GREY)
    c.hline(x + 8, y + h - 8, w - 16, GREY)
    bars = (0.25, 0.35, 0.30, 0.55, 0.70, 0.95)
    bw = (w - 24) // len(bars)
    for i, frac in enumerate(bars):
        bh = int((h - 22) * frac)
        c.rect(x + 14 + i * bw, y + h - 8 - bh, bw - 4, bh, STEEL)
    pts = [(x + 14 + i * bw + bw // 2, y + h - 10 - int((h - 22) * f))
           for i, f in enumerate(bars)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], GREEN)
        c.line(a[0], a[1] + 1, b[0], b[1] + 1, GREEN)
    c.circle(pts[-1][0], pts[-1][1], 4, RED)


def draw_scales(c, x, y, s):
    # Scales of justice: post, beam, two pans.
    c.rect(x + 14 * s, y, 3 * s, 26 * s, INK)
    c.rect(x + 8 * s, y + 26 * s, 15 * s, 3 * s, INK)
    c.rect(x, y + 4 * s, 31 * s, 3 * s, INK)
    c.circle(x + 15 * s, y + 4 * s, 3 * s, GOLD)
    for cx in (x + 3 * s, x + 27 * s):
        c.line(cx, y + 7 * s, cx - 5 * s, y + 18 * s, INK)
        c.line(cx, y + 7 * s, cx + 5 * s, y + 18 * s, INK)
        c.rect(cx - 6 * s, y + 18 * s, 12 * s, 3 * s, GOLD)


def draw_ship(c, x, y, s):
    # Tanker hull, bridge tower and a flame above the deck.
    c.rect(x, y + 16 * s, 52 * s, 10 * s, INK)
    c.rect(x + 38 * s, y + 6 * s, 10 * s, 10 * s, INK)
    c.rect(x + 4 * s, y + 10 * s, 8 * s, 6 * s, RED)
    c.rect(x + 16 * s, y + 10 * s, 8 * s, 6 * s, RED)
    c.rect(x + 28 * s, y + 10 * s, 8 * s, 6 * s, RED)
    draw_flame(c, x + 18 * s, y - 12 * s, 1)
    c.line(x - 4 * s, y + 28 * s, x + 56 * s, y + 28 * s, STEEL)
    c.line(x - 2 * s, y + 32 * s, x + 54 * s, y + 32 * s, STEEL)


def draw_flame(c, x, y, s):
    c.ellipse(x + 8 * s, y + 10 * s, 8 * s, 11 * s, RED)
    c.ellipse(x + 8 * s, y + 13 * s, 5 * s, 7 * s, (240, 140, 20))
    c.ellipse(x + 8 * s, y + 15 * s, 2 * s, 4 * s, GOLD)


def draw_bridge(c, x, y, s):
    # Suspension bridge: two towers, deck and cables.
    c.rect(x + 4 * s, y + 2 * s, 4 * s, 22 * s, INK)
    c.rect(x + 44 * s, y + 2 * s, 4 * s, 22 * s, INK)
    c.rect(x, y + 22 * s, 52 * s, 4 * s, INK)
    c.line(x + 6 * s, y + 2 * s, x + 26 * s, y + 12 * s, RED)
    c.line(x + 46 * s, y + 2 * s, x + 26 * s, y + 12 * s, RED)
    c.line(x + 6 * s, y + 2 * s, x + 2 * s, y + 12 * s, RED)
    c.line(x + 46 * s, y + 2 * s, x + 50 * s, y + 12 * s, RED)
    for dx in (10, 18, 34, 42):
        c.vline(x + dx * s, y + 12 * s, 10 * s, GREY)


def draw_globe(c, cx, cy, r):
    c.circle(cx, cy, r, NAVY_LIGHT)
    c.ring(cx, cy, r, NAVY, 2)
    c.rect(cx - r, cy - 1, 2 * r, 2, WHITE)
    for dx in (-r // 2, r // 2):
        c.line(cx + dx, cy - r + 4, cx + dx, cy + r - 4, WHITE)
    c.circle(cx - r // 3, cy - r // 3, 5, (120, 200, 120))
    c.circle(cx + r // 3, cy + r // 4, 6, (120, 200, 120))


def draw_map(c, x, y, w, h):
    # Simplified world map: muted continent blobs, red dots for the
    # places in today's news.
    c.rect(x, y, w, h, (228, 236, 228))
    land = STEEL
    c.ellipse(x + 52, y + 30, 40, 20, land)   # North America
    c.ellipse(x + 60, y + 62, 16, 12, land)   # South America
    c.ellipse(x + 132, y + 26, 14, 11, land)  # Europe
    c.ellipse(x + 136, y + 52, 18, 16, land)  # Africa
    c.ellipse(x + 200, y + 30, 44, 20, land)  # Asia
    c.ellipse(x + 228, y + 62, 12, 7, land)   # Australia
    dots = [(238, 34), (130, 22), (168, 44), (150, 38),
            (142, 20), (214, 42), (146, 32)]
    for dx, dy in dots:
        c.circle(x + dx, y + dy, 4, RED)
        c.ring(x + dx, y + dy, 5, RED, 1)


def draw_pin(c, x, y, s):
    # Map pin: a round head over a point.
    c.circle(x + 8 * s, y + 7 * s, 8 * s, RED)
    c.circle(x + 8 * s, y + 7 * s, 3 * s, WHITE)
    c.line(x + 8 * s, y + 14 * s, x + 2 * s, y + 26 * s, RED)
    c.line(x + 8 * s, y + 14 * s, x + 14 * s, y + 26 * s, RED)


def stat_box(c, x, y, w, h, number, label):
    c.rect(x, y, w, h, CREAM)
    c.rect(x, y, w, 3, NAVY)
    c.text(x + 12, y + 8, number, 3, NAVY)
    c.text(x + 12, y + 32, label, 2, INK)


def hero_panel(c, x, y, w, h):
    c.rect(x, y, w, h, CREAM)
    c.rect(x, y, w, 4, RED)
    c.rect(x, y, 4, h, NAVY)


def story_card(c, x, y, w, h, kicker, headline, body, icon):
    c.rect(x, y, w, h, CREAM)
    c.rect(x, y, w, 4, RED)
    c.rect(x, y, 4, h, NAVY)
    pad = 16
    c.text(x + pad, y + 10, kicker, 2, RED)
    c.wrap(x + pad, y + 30, headline, 3, INK, w - 2 * pad - 64)
    c.wrap(x + pad, y + 84, body, 2, INK, w - 2 * pad)
    ix, iy = x + w - 66, y + 10
    if icon == "scales":
        draw_scales(c, ix, iy, 1)
    elif icon == "ship":
        draw_ship(c, ix - 6, iy + 12, 1)
    elif icon == "bridge":
        draw_bridge(c, ix, iy, 1)
    elif icon == "flame":
        draw_flame(c, ix + 16, iy, 2)
    elif icon == "globe":
        draw_globe(c, ix + 26, iy + 22, 20)
    elif icon == "pin":
        draw_pin(c, ix + 10, iy, 1)


def build_image():
    c = Canvas(WIDTH, HEIGHT, PAPER)
    # Outer frame.
    c.rect(0, 0, WIDTH, 8, NAVY)
    c.rect(0, HEIGHT - 8, WIDTH, 8, NAVY)
    c.rect(0, 0, 8, HEIGHT, NAVY)
    c.rect(WIDTH - 8, 0, 8, HEIGHT, NAVY)

    # Masthead.
    c.rect(8, 8, WIDTH - 16, 88, NAVY)
    c.centered(WIDTH // 2, 18, "THE WORLD IN ONE DAY", 5, WHITE)
    c.hline(48, 60, WIDTH - 96, GOLD)
    c.hline(48, 63, WIDTH - 96, GOLD)
    c.centered(WIDTH // 2, 70, "THURSDAY, 19 NOVEMBER 2026", 3,
               (255, 214, 130))

    # Stats strip: four big numbers from the day.
    sy = 102
    stat_box(c, 28, sy, 236, 48, "3", "TANKERS HIT MINES")
    stat_box(c, 272, sy, 236, 48, "$190.4M", "VAN GOGH RECORD")
    stat_box(c, 516, sy, 236, 48, "7 YEARS", "TO AN ICJ VERDICT")
    stat_box(c, 760, sy, 236, 48, "25", "SEAFARERS DEAD")

    # Hero row: three big stories with drawn pictures.
    hy = 158
    hero_panel(c, 28, hy, 312, 180)
    draw_us_flag(c, 44, hy + 12, 88, 48)
    draw_russia_flag(c, 136, hy + 12, 88, 48)
    draw_china_flag(c, 228, hy + 12, 88, 48)
    c.text(70, hy + 64, "USA", 2, GREY)
    c.text(144, hy + 64, "RUSSIA", 2, GREY)
    c.text(242, hy + 64, "CHINA", 2, GREY)
    c.wrap(44, hy + 86, "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
           3, INK, 280)
    c.text(44, hy + 164, "FIRST THREE-WAY SUMMIT", 2, RED)

    hero_panel(c, 356, hy, 312, 180)
    draw_controller(c, 468, hy + 10, 2)
    c.wrap(372, hy + 74, "GTA VI LAUNCHES TONIGHT", 3, INK, 280)
    c.wrap(372, hy + 130, "A 13-year wait ends at midnight tonight.",
           2, INK, 280)

    hero_panel(c, 684, hy, 312, 180)
    draw_chart(c, 700, hy + 10, 280, 64)
    c.wrap(700, hy + 82, "ANTHROPIC LISTS ON NASDAQ AS ANT",
           3, INK, 280)
    c.text(700, hy + 162, "RECORD AI STOCK DEBUT", 2, RED)

    # 2x3 grid of story cards.
    cy = 346
    cw, ch, gap = 478, 138, 8
    story_card(c, 28, cy, cw, ch, "JUSTICE  /  THE HAGUE",
               "WORLD COURT RULES ON ROHINGYA CASE",
               "ICJ judgment in Gambia v Myanmar: killings and "
               "sexual violence cited.",
               "scales")
    story_card(c, 518, cy, cw, ch, "ENERGY  /  HORMUZ",
               "TANKERS ABLAZE AFTER MINE STRIKES",
               "Three tankers catch fire east of the strait; "
               "a supertanker sinks.",
               "ship")
    story_card(c, 28, cy + ch + gap, cw, ch, "WAR  /  UKRAINE",
               "KYIV HITS CRIMEA BRIDGE AGAIN",
               "Ukraine strikes the Crimean Bridge for a third "
               "time in a week.",
               "bridge")
    story_card(c, 518, cy + ch + gap, cw, ch, "ASIA  /  BANGLADESH",
               "BANGLADESH BURNS AS UNREST SPREADS",
               "Yunus ancestral home is set on fire as protests "
               "hit 28 districts.",
               "flame")
    story_card(c, 28, cy + 2 * (ch + gap), cw, ch, "MIDDLE EAST  /  GAZA",
               "ISRAEL PUSHES INTO CENTRAL GAZA",
               "Israeli ground forces move beyond the Yellow "
               "Line; dozens flee.",
               "pin")
    story_card(c, 518, cy + 2 * (ch + gap), cw, ch, "CLIMATE  /  COP31",
               "COP31 MINISTERS RACE FOR A DEAL",
               "Ministers meet into the night in Antalya to "
               "unblock the talks.",
               "globe")

    # Bottom: world map beside the In Brief list.
    by = 784
    c.rect(28, by, 300, 144, CREAM)
    c.rect(28, by, 300, 4, RED)
    c.text(44, by + 10, "WHERE TODAY HAPPENED", 2, RED)
    draw_map(c, 44, by + 28, 268, 78)
    c.text(44, by + 112, "SHENZHEN - HAGUE", 2, INK)
    c.text(44, by + 128, "HORMUZ - GAZA - KYIV", 2, INK)

    c.rect(340, by, 656, 144, CREAM)
    c.rect(340, by, 656, 4, RED)
    c.text(356, by + 10, "IN BRIEF", 2, RED)
    brief = [
        "1. Van Gogh sells for $190.4m, a record.",
        "2. Jeffries set to be first Black Speaker.",
        "3. IAEA: North Korea expanded enrichment.",
        "4. Russian plane crash kills all 19 on board.",
        "5. EU proposes 45bn euro loan for Ukraine.",
        "6. Magnitude 5.7 quake jolts Kumamoto.",
    ]
    yy = by + 32
    for item in brief:
        c.text(356, yy, item, 2, INK)
        yy += 18

    # Footer ticker and credit line.
    c.hline(28, 936, WIDTH - 56, GOLD)
    c.wrap(28, 944,
           "ALSO: Pochettino joins Manchester United. "
           "Ethiopia-Eritrea clashes threaten war. Gold below "
           "$3,800; copper down 5%.",
           2, INK, WIDTH - 56)
    c.centered(WIDTH // 2, 988,
               "COMPILED FROM WIRE REPORTS  -  19 NOVEMBER 2026",
               2, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_image())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
