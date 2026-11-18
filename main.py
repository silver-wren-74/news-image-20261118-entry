#!/usr/bin/env python3
"""One image that sums up the world news of Wednesday 18 November 2026.

The picture is a night-desk front page: a lead story across the top and
four more beneath it, painted pixel by pixel with the Python 3 standard
library only, and saved as /output/entry.png (PNG, 1024 x 1024).
Deterministic: the same bytes come out of every run.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

NIGHT = (23, 34, 46)
CARD = (250, 246, 236)
INKC = (24, 30, 44)
CRIMSON = (178, 34, 44)
AMBER = (232, 168, 32)
PINE = (26, 110, 96)
WAVE = (70, 120, 165)
MIST = (150, 158, 168)
SNOW = (240, 244, 248)


def png_bytes(width, height, buf):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data +
                struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    stride = width * 3
    raw = b"".join(b"\x00" + bytes(buf[y * stride:(y + 1) * stride])
                   for y in range(height))
    head = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head) +
            chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


class Pic:
    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.buf = bytearray(bytes(colour) * (width * height))

    def put(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(colour)

    def box(self, x, y, w, h, colour):
        for yy in range(max(y, 0), min(y + h, self.h)):
            base = (yy * self.w + max(x, 0)) * 3
            run = bytes(colour) * max(0, min(x + w, self.w) - max(x, 0))
            self.buf[base:base + len(run)] = run

    def frame(self, x, y, w, h, colour, thick=3):
        self.box(x, y, w, thick, colour)
        self.box(x, y + h - thick, w, thick, colour)
        self.box(x, y, thick, h, colour)
        self.box(x + w - thick, y, thick, h, colour)

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.put(xx, yy, colour)

    def ring(self, cx, cy, r, colour, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = math.hypot(xx - cx, yy - cy)
                if r - thick <= d <= r:
                    self.put(xx, yy, colour)

    def line(self, x0, y0, x1, y1, colour, thick=3):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = max(thick // 2, 1)
        for i in range(steps + 1):
            self.disc(x0 + (x1 - x0) * i // steps,
                      y0 + (y1 - y0) * i // steps, r, colour)

    def tri(self, ax, ay, bx, by, cx, cy, colour):
        det = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if det == 0:
            return
        for yy in range(min(ay, by, cy), max(ay, by, cy) + 1):
            for xx in range(min(ax, bx, cx), max(ax, bx, cx) + 1):
                w0 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / det
                w1 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / det
                if w0 >= 0 and w1 >= 0 and 1 - w0 - w1 >= 0:
                    self.put(xx, yy, colour)


# 5x7 glyphs, one int per row, bit 16 = leftmost pixel
GLYPHS = {
    "A": (14, 17, 17, 31, 17, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (15, 16, 16, 16, 16, 16, 15), "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31), "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (15, 16, 16, 23, 17, 17, 14), "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (31, 4, 4, 4, 4, 4, 31), "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17), "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 17, 25, 21, 19, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14), "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13), "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14), "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17), "X": (17, 10, 4, 4, 4, 10, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 19, 21, 25, 17, 17, 14), "1": (4, 12, 20, 4, 4, 4, 31),
    "2": (14, 17, 1, 6, 8, 16, 31), "3": (30, 1, 1, 14, 1, 1, 30),
    "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (14, 16, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 4, 4, 4),
    "8": (14, 17, 17, 14, 17, 17, 14), "9": (14, 17, 17, 15, 1, 1, 14),
    " ": (0, 0, 0, 0, 0, 0, 0), ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 12, 8), ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 12, 8), "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 2, 4, 0, 4), "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 31, 0, 0, 0), "+": (0, 4, 4, 31, 4, 4, 0),
    "/": (1, 1, 2, 4, 8, 16, 16), "(": (3, 4, 8, 8, 8, 4, 3),
    ")": (24, 4, 2, 2, 2, 4, 24), "&": (12, 18, 20, 8, 21, 18, 13),
    "%": (25, 26, 1, 2, 4, 8, 19), "$": (4, 15, 20, 14, 5, 30, 4),
}


def measure(text, scale):
    return len(text) * 6 * scale - scale


def stamp(pic, x, y, text, colour, scale=3):
    cx = x
    for ch in text.upper():
        rows = GLYPHS.get(ch, GLYPHS[" "])
        for ri, bits in enumerate(rows):
            for ci in range(5):
                if bits & (16 >> ci):
                    pic.box(cx + ci * scale, y + ri * scale,
                            scale, scale, colour)
        cx += 6 * scale
    return cx


def stamp_c(pic, cx, y, text, colour, scale=3):
    return stamp(pic, cx - measure(text, scale) // 2, y, text, colour, scale)


def wrap_lines(text, scale, max_width):
    out, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if measure(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


# ------------------------------------------------------------------ icons
def icon_tanker(p, x, y):
    p.tri(x + 6, y + 78, x + 26, y + 104, x + 6, y + 104, INKC)
    p.box(x + 24, y + 78, 150, 26, INKC)
    p.tri(x + 174, y + 78, x + 196, y + 104, x + 174, y + 104, INKC)
    p.box(x + 36, y + 58, 30, 20, CRIMSON)
    p.box(x + 70, y + 58, 30, 20, AMBER)
    p.box(x + 104, y + 58, 30, 20, PINE)
    p.box(x + 146, y + 44, 16, 34, INKC)
    p.box(x + 150, y + 36, 8, 8, INKC)
    # flames over the middle tank
    p.tri(x + 76, y + 58, x + 86, y + 26, x + 96, y + 58, CRIMSON)
    p.tri(x + 82, y + 58, x + 87, y + 40, x + 92, y + 58, AMBER)
    p.disc(x + 60, y + 22, 7, MIST)
    p.disc(x + 48, y + 14, 5, MIST)
    for i in range(5):
        wx = x + 8 + i * 38
        p.line(wx, y + 122, wx + 9, y + 116, WAVE, 3)
        p.line(wx + 9, y + 116, wx + 18, y + 122, WAVE, 3)


def icon_bridge_night(p, x, y):
    p.disc(x + 96, y + 18, 11, AMBER)
    p.box(x + 10, y + 30, 9, 66, INKC)
    p.box(x + 99, y + 30, 9, 66, INKC)
    p.box(x + 2, y + 24, 114, 6, INKC)
    p.line(x + 14, y + 26, x + 50, y + 58, INKC, 2)
    p.line(x + 104, y + 26, x + 68, y + 58, INKC, 2)
    p.box(x + 2, y + 58, 42, 7, INKC)
    p.line(x + 44, y + 61, x + 58, y + 80, CRIMSON, 5)
    p.box(x + 74, y + 58, 42, 7, INKC)
    p.line(x + 52, y + 100, x + 70, y + 94, CRIMSON, 4)
    for i in range(4):
        wx = x + 4 + i * 29
        p.line(wx, y + 110, wx + 7, y + 105, WAVE, 3)
        p.line(wx + 7, y + 105, wx + 14, y + 110, WAVE, 3)


def icon_flags(p, x, y):
    p.line(x + 22, y + 6, x + 22, y + 112, INKC, 4)
    p.line(x + 84, y + 6, x + 84, y + 112, INKC, 4)
    p.box(x + 22, y + 8, 48, 28, CRIMSON)
    p.tri(x + 70, y + 8, x + 70, y + 36, x + 57, y + 22, CARD)
    p.disc(x + 40, y + 22, 6, SNOW)
    p.box(x + 84, y + 8, 48, 28, PINE)
    p.tri(x + 132, y + 8, x + 132, y + 36, x + 119, y + 22, CARD)
    p.disc(x + 102, y + 22, 6, AMBER)
    p.disc(x + 22, y + 4, 4, AMBER)
    p.disc(x + 84, y + 4, 4, AMBER)


def icon_missile(p, x, y):
    for t in range(0, 60, 10):
        p.disc(x + 16 + t // 3, y + 100 - t // 3, 2, MIST)
    p.line(x + 44, y + 76, x + 84, y + 36, INKC, 13)
    p.tri(x + 84, y + 36, x + 104, y + 16, x + 74, y + 26, CRIMSON)
    p.tri(x + 50, y + 82, x + 34, y + 84, x + 44, y + 66, INKC)
    p.tri(x + 76, y + 48, x + 78, y + 32, x + 62, y + 42, INKC)
    p.tri(x + 44, y + 76, x + 30, y + 88, x + 48, y + 90, AMBER)
    p.tri(x + 42, y + 78, x + 34, y + 84, x + 46, y + 84, CRIMSON)


def icon_thermo(p, x, y):
    p.disc(x + 92, y + 24, 13, AMBER)
    for ang in range(0, 360, 60):
        dx = int(19 * math.cos(math.radians(ang)))
        dy = int(19 * math.sin(math.radians(ang)))
        p.line(x + 92, y + 24, x + 92 + dx, y + 24 + dy, AMBER, 3)
    p.box(x + 44, y + 14, 14, 74, INKC)
    p.box(x + 48, y + 44, 6, 40, CRIMSON)
    p.disc(x + 51, y + 96, 15, INKC)
    p.disc(x + 51, y + 96, 9, CRIMSON)
    for dx, dy in ((-12, -12), (0, -15), (12, -12), (-12, 12), (0, 15),
                   (12, 12), (-15, 0), (15, 0)):
        p.line(x + 18, y + 96, x + 18 + dx, y + 96 + dy, WAVE, 2)


# ------------------------------------------------------------------ layout
def card(p, x, y, w, h, kicker, headline, body, icon, hscale=3):
    p.box(x, y, w, h, CARD)
    p.frame(x, y, w, h, INKC, 3)
    icon(p, x + 14, y + 56)
    tx = x + 146
    tw = w - 162
    stamp(p, tx, y + 14, kicker, CRIMSON, 2)
    p.box(tx, y + 32, 54, 3, AMBER)
    ly = y + 44
    for ln in wrap_lines(headline, hscale, tw):
        stamp(p, tx, ly, ln, INKC, hscale)
        ly += 9 * hscale
    ly += 6
    for ln in wrap_lines(body, 2, tw):
        stamp(p, tx, ly, ln, INKC, 2)
        ly += 20


def compose():
    p = Pic(W, H, NIGHT)
    p.box(0, 0, W, 8, CRIMSON)
    stamp_c(p, W // 2, 26, "ONE DAY IN THE WORLD", SNOW, 6)
    p.box(88, 84, W - 176, 3, SNOW)
    stamp_c(p, W // 2, 96, "WEDNESDAY 18 NOVEMBER 2026", AMBER, 4)
    p.box(88, 132, W - 176, 3, SNOW)

    # lead story, full width
    lx, ly0, lw, lh = 28, 152, 968, 246
    p.box(lx, ly0, lw, lh, CARD)
    p.frame(lx, ly0, lw, lh, INKC, 3)
    icon_tanker(p, lx + 36, ly0 + 62)
    tx = lx + 262
    tw = lw - 262 - 24
    stamp(p, tx, ly0 + 22, "MIDDLE EAST - WAR AT SEA", CRIMSON, 2)
    p.box(tx, ly0 + 40, 54, 3, AMBER)
    yy = ly0 + 54
    for ln in wrap_lines("US SINKS FIVE IRANIAN TANKERS", 4, tw):
        stamp(p, tx, yy, ln, INKC, 4)
        yy += 36
    yy += 8
    for ln in wrap_lines(
            "Iran hits back at ships near Hormuz and a US base in "
            "Jordan, while Bahrain and Kuwait intercept drones "
            "overhead: the sharpest night yet of the Gulf war.", 2, tw):
        stamp(p, tx, yy, ln, INKC, 2)
        yy += 20

    stories = [
        ("UKRAINE - PEACE TALKS", "KERCH BRIDGE HIT FOR SECOND NIGHT",
         "Kyiv strikes the Crimea link again as US envoys talk "
         "peace; Washington scolds Ukraine over deep strikes.",
         icon_bridge_night),
        ("ASIA - SUMMITS", "TRUMP IN MANILA FOR QUAD TALKS",
         "Xi meets Canada's Carney and trade deals extend ahead "
         "of the APEC summit in Shenzhen.", icon_flags),
        ("KOREA", "NORTH KOREA FIRES BALLISTIC MISSILE",
         "Pyongyang launches toward the Sea of Japan hours after "
         "US, South Korean and Japanese drills end.", icon_missile),
        ("CLIMATE - COP31", "CLIMATE TALKS ENTER DECISIVE PHASE",
         "Negotiators in Antalya wrestle with 144 disputed items "
         "before Friday's closing deadline.", icon_thermo),
    ]
    pw, ph, gap, mx, top = 474, 238, 20, 28, 418
    for i, (kicker, head, body, icon) in enumerate(stories):
        card(p, mx + (i % 2) * (pw + gap), top + (i // 2) * (ph + gap),
             pw, ph, kicker, head, body, icon)

    fy = top + 2 * ph + gap + 16
    p.box(88, fy, W - 176, 3, SNOW)
    stamp_c(p, W // 2, fy + 12,
            "ALSO: UN WARNS OF COLD DEATHS IN GAZA AS WINTER SETS IN",
            SNOW, 2)
    stamp_c(p, W // 2, fy + 36,
            "ROMANIA QUAKE 5.3 - PRAGUE MARCHES - PATTINSON IS BOND",
            MIST, 2)
    return png_bytes(W, H, p.buf)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = compose()
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)
    print("wrote entry.png:", len(data), "bytes")


if __name__ == "__main__":
    main()
