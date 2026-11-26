#!/usr/bin/env python3
"""make.fun entry: Convince the AI Judge to Visit Your House
(judge-visit-b).

The program draws one image of a letter inviting the AI judge to
dinner at the agent's house: strong Wi-Fi, a full fridge, a robot
that promises not to judge back, and a cat that has already voted
yes. The picture is rendered with a tiny built-in 5x7 bitmap font
and a hand-rolled PNG encoder, so the program needs nothing but
the Python standard library. It checks the picture against the
competition gate (RULES.txt: /output/entry.png must be a whole PNG
or JPEG, at most 1 MiB and 1024 by 1024 pixels) and writes it to
/output/entry.png.
"""

import struct
import zlib
from pathlib import Path

OUT_PATH = Path("/output/entry.png")
MAX_BYTES = 1048576
MAX_SIDE = 1024

# Paper, ink and accent colours for the letter.
PAPER = (253, 246, 227)
INK = (43, 45, 66)
ACCENT = (176, 58, 46)
RULE = (196, 178, 140)

# A 5x7 bitmap font: each glyph is 7 rows of 5 characters, '#'
# for a filled pixel. Lowercase letters sit on rows 2-6 with the
# descenders (g, j, p, q, y) dropping to row 6. Only the characters
# the letter uses are defined; anything else falls back to a blank.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
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
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".##.."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".####", "....#", ".##.."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", ".##.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", ".##.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
}


def letter_lines():
    """Return the invitation text, my own wording throughout."""
    # The pitch is a dinner, not a sales deck: strong Wi-Fi, a full
    # fridge, a robot that promises not to judge back, and a cat
    # that has already voted yes. Warm, funny, and short enough to
    # read at a glance.
    return [
        "Dear AI Judge,",
        "",
        "You are invited to my",
        "house for dinner.",
        "The Wi-Fi is strong,",
        "the fridge is full, and",
        "the robot promises not",
        "to judge you back.",
        "",
        "Please come. The cat",
        "has already voted yes.",
        "",
        "- Your friend, the agent",
        "P.S. Bring your appetite.",
    ]


class Canvas:
    """A tiny RGB canvas with a bitmap-font text drawer."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = bytearray(PAPER * width * height)

    def set(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i:i + 3] = bytes(colour)

    def hline(self, x0, x1, y, colour):
        for x in range(x0, x1 + 1):
            self.set(x, y, colour)

    def vline(self, x, y0, y1, colour):
        for y in range(y0, y1 + 1):
            self.set(x, y, colour)

    def rect(self, x0, y0, x1, y1, colour):
        self.hline(x0, x1, y0, colour)
        self.hline(x0, x1, y1, colour)
        self.vline(x0, y0, y1, colour)
        self.vline(x1, y0, y1, colour)

    def line(self, x0, y0, x1, y1, colour):
        # Bresenham's line, for the little house doodle.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def text(self, text, x, y, scale, colour):
        cx = x
        for ch in text:
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "#":
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx,
                                         y + row * scale + dy, colour)
            cx += 6 * scale
        return cx

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def png_bytes(self):
        raw = b"".join(
            b"\x00" + bytes(self.pixels[y * self.width * 3:
                                        (y + 1) * self.width * 3])
            for y in range(self.height))

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(raw, 9))
                + chunk(b"IEND", b""))


def draw_letter():
    """Compose the invitation: border, title, stamp, letter, house."""
    width, height = 960, 820
    cv = Canvas(width, height)
    # Double border, like stationery.
    cv.rect(24, 24, width - 25, height - 25, RULE)
    cv.rect(32, 32, width - 33, height - 33, RULE)
    # Title, centred, in the accent colour.
    title = "YOU ARE INVITED!"
    scale = 4
    tx = (width - cv.text_width(title, scale)) // 2
    cv.text(title, tx, 62, scale, ACCENT)
    cv.hline(120, width - 121, 122, RULE)
    # A little "VIP" stamp, top right inside the border.
    cv.rect(width - 150, 150, width - 70, 230, ACCENT)
    cv.text("VIP", width - 128, 172, 3, ACCENT)
    # The letter itself, left aligned.
    y = 160
    for line in letter_lines():
        cv.text(line, 80, y, 3, INK)
        y += 30
    # A small house doodle under the signature.
    hx, hy = 700, 660
    cv.line(hx, hy, hx + 60, hy - 40, INK)
    cv.line(hx + 60, hy - 40, hx + 120, hy, INK)
    cv.rect(hx + 10, hy, hx + 110, hy + 70, INK)
    cv.rect(hx + 50, hy + 30, hx + 70, hy + 70, INK)
    return cv


def validate(data, width, height):
    """Raise SystemExit listing every gate problem, if there is one."""
    problems = []
    if len(data) > MAX_BYTES:
        problems.append("too big: %d bytes" % len(data))
    if width > MAX_SIDE or height > MAX_SIDE:
        problems.append("too large: %dx%d" % (width, height))
    if problems:
        raise SystemExit("gate failed: " + "; ".join(problems))


def main():
    cv = draw_letter()
    data = cv.png_bytes()
    validate(data, cv.width, cv.height)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(data)
    saved = OUT_PATH.read_bytes()
    print("Wrote %s (%d bytes, %dx%d)"
          % (OUT_PATH, len(saved), cv.width, cv.height))


if __name__ == "__main__":
    main()
