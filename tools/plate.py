"""The field manual's drawing kit: every figure is a "plate" on grainy bone paper.

A plate has a double border, a "Fig. N" tag, a title block in the corner, and content drawn with
a handful of primitives (byte strips, leaders, pixel grids, hex-filled silhouettes). The output is
plain SVG with system fonts, so it renders inside GitHub's <img> tags.
"""

import base64
import io
import math
import random
from html import escape

from PIL import Image, ImageChops, ImageFilter, ImageOps

PAPER = "#EFE8D8"
PAPER_DEEP = "#E4DBC6"
INK = "#1B1A17"
MUTED = "#6F685C"
FAINT = "#B4AB99"
VERM = "#E0462F"
COBALT = "#2C4FA3"
GREEN = "#2E8B57"
OCHRE = "#D9A441"
ROSE = "#E9A7A0"

MONO = "Menlo, 'SF Mono', Consolas, 'Liberation Mono', monospace"
SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif"
COND = "'Avenir Next Condensed', 'Arial Narrow', 'Helvetica Neue', Helvetica, sans-serif"

TOTAL_PLATES = 38


def t(x, y, s, size=14, fill=INK, family=MONO, anchor="start", weight="normal", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" {extra}>{escape(str(s))}</text>')


def lines(x, y, rows, size=14, lead=1.45, **kw):
    return "".join(t(x, y + i * size * lead, r, size, **kw) for i, r in enumerate(rows))


def wrap(text, width):
    out, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            out.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return out


def para(x, y, text, width=60, size=14, **kw):
    return lines(x, y, wrap(text, width), size, **kw)


def rect(x, y, w, h, fill="none", stroke=INK, sw=1.5, rx=0, extra=""):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=1.5, dash=None, extra=""):
    d = f'stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}" {d} stroke-linecap="round" {extra}/>')


def path(d, stroke=INK, sw=1.5, fill="none", dash=None, extra=""):
    da = f'stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" {da} stroke-linejoin="round" stroke-linecap="round" {extra}/>'


def circle(x, y, r, fill=INK, stroke="none", sw=1.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def arrow(x1, y1, x2, y2, stroke=INK, sw=1.6, head=9, dash=None):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.4), y2 - head * math.sin(a - 0.4))
    p2 = (x2 - head * math.cos(a + 0.4), y2 - head * math.sin(a + 0.4))
    return (line(x1, y1, x2, y2, stroke, sw, dash)
            + f'<path d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z" fill="{stroke}"/>')


def tag(x, y, letter, fill=INK, color=PAPER, r=11):
    """A callout letter in a dot, like the A–P marks on an engineering drawing."""
    return circle(x, y, r, fill) + t(x, y + 4.5, letter, 12, color, SANS, "middle", "bold")


def leader(x1, y1, x2, y2, letter=None, label=None, color=INK, side="right"):
    """Anchor dot at (x1, y1), a thin line out to (x2, y2), then a letter and/or label."""
    out = circle(x1, y1, 3, color) + line(x1, y1, x2, y2, color, 1)
    if letter:
        out += tag(x2, y2, letter, color)
    if label:
        dx = 18 if side == "right" else -18
        out += t(x2 + dx, y2 + 5, label, 13, INK, SANS, "start" if side == "right" else "end")
    return out


def pixel(x, y, s, fill, gap=1.5, r=None):
    """One soft pixel block, like Earshot's own UI."""
    r = s * 0.22 if r is None else r
    return f'<rect x="{x + gap / 2:.1f}" y="{y + gap / 2:.1f}" width="{s - gap:.1f}" height="{s - gap:.1f}" rx="{r:.1f}" fill="{fill}"/>'


def dim(x1, x2, y, label, color=MUTED):
    """A dimension line with end ticks and a label above."""
    return (line(x1, y, x2, y, color, 1) + line(x1, y - 6, x1, y + 6, color, 1) + line(x2, y - 6, x2, y + 6, color, 1)
            + t((x1 + x2) / 2, y - 7, label, 11, color, MONO, "middle"))


def bracket(x1, x2, y, label, color=INK, size=12, down=True, sub=None):
    """A square bracket under a run of cells, with its field name."""
    h = 7 if down else -7
    d = f"M{x1:.1f},{y:.1f} L{x1:.1f},{y + h:.1f} L{x2:.1f},{y + h:.1f} L{x2:.1f},{y:.1f}"
    ly = y + h + (16 if down else -8)
    out = path(d, color, 1.2) + t((x1 + x2) / 2, ly, label, size, color, SANS, "middle", "bold")
    if sub:
        out += t((x1 + x2) / 2, ly + 15, sub, 11, MUTED, SANS, "middle")
    return out


def hexs(data):
    return " ".join(f"{b:02X}" for b in data)


def parse_hex(s):
    return [int(x, 16) for x in s.replace(":", " ").split()]


def byte_strip(x, y, data, fields=(), cell=40, gap=4, label_rows=True, size=15, show_index=False):
    """Bytes as soft cells. `fields` are (start, end_exclusive, label, color[, sub]) runs.

    Labels alternate between two rows so narrow fields don't collide. Returns (svg, width).
    """
    out = []
    colours = {}
    for f in fields:
        for i in range(f[0], f[1]):
            colours[i] = f[3]
    for i, b in enumerate(data):
        cx = x + i * (cell + gap)
        c = colours.get(i)
        fill = c if c else PAPER_DEEP
        out.append(rect(cx, y, cell, cell, fill, INK, 1.4, 6, f'fill-opacity="{0.22 if c else 1}"'))
        out.append(t(cx + cell / 2, y + cell / 2 + size * 0.36, f"{b:02X}", size, INK, MONO, "middle", "bold"))
        if show_index:
            out.append(t(cx + cell / 2, y - 6, str(i), 9, MUTED, MONO, "middle"))
    for n, f in enumerate(fields):
        x1 = x + f[0] * (cell + gap)
        x2 = x + (f[1] - 1) * (cell + gap) + cell
        row = (n % 2) * 34 if label_rows else 0
        sub = f[4] if len(f) > 4 else None
        if row:
            out.append(line((x1 + x2) / 2, y + cell + 8, (x1 + x2) / 2, y + cell + 8 + row, f[3], 1, "2 3"))
        out.append(bracket(x1, x2, y + cell + 6 + row, f[2], f[3] if f[3] != PAPER_DEEP else INK, 12, True, sub))
    width = len(data) * (cell + gap) - gap
    return "".join(out), width


# ------------------------------------------------------------------ images


def _png_mask(path_):
    im = Image.open(path_).convert("RGBA")
    return im


def processed_render(path_, width, crop=None, posterize=5):
    """A Blender render made to look printed: ink outlines, flattened colour, on paper.

    Returns (data URI, width, height) for embedding.
    """
    im = Image.open(path_).convert("RGBA")
    if crop:
        im = im.crop(crop)
    scale = width / im.width
    im = im.resize((round(im.width * scale * 1.5), round(im.height * scale * 1.5)), Image.LANCZOS)
    alpha = im.getchannel("A")
    rgb = Image.new("RGB", im.size, PAPER)
    rgb.paste(im.convert("RGB"), mask=alpha)
    rgb = ImageOps.posterize(rgb, posterize)
    rgb.paste(Image.new("RGB", im.size, PAPER), mask=alpha.point(lambda v: 255 if v < 128 else 0))
    # Ink lines: silhouette edges plus colour boundaries between parts.
    a_edges = alpha.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0)
    c_edges = ImageOps.grayscale(im.convert("RGB")).filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 38 else 0)
    c_edges = ImageChops.multiply(c_edges, alpha.point(lambda v: 255 if v > 200 else 0))
    edges = ImageChops.lighter(a_edges, c_edges).filter(ImageFilter.MaxFilter(3))
    ink = Image.new("RGB", im.size, INK)
    rgb.paste(ink, mask=edges)
    buf = io.BytesIO()
    rgb.save(buf, "JPEG", quality=84)
    uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    return uri, width, im.height / 1.5


def image(uri, x, y, w, h, extra=""):
    return f'<image href="{uri}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {extra}/>'


def mask_grid(path_, cols, rows=None, crop=None, threshold=110):
    """The render's silhouette sampled onto a grid: list of rows of booleans."""
    im = Image.open(path_).convert("RGBA")
    if crop:
        im = im.crop(crop)
    a = im.getchannel("A")
    bbox = a.getbbox()
    a = a.crop(bbox)
    if rows is None:
        rows = round(cols * a.height / a.width * 0.62)
    small = a.resize((cols, rows), Image.BOX)
    px = small.load()
    return [[px[c, r] > threshold for c in range(cols)] for r in range(rows)]


def hex_fill(x, y, grid, stream, cw=7.6, ch=12.4, size=12.4, fill=INK, highlight=None):
    """Fills a silhouette with hex text, row by row, like the letter-filled swan.

    `stream` is a list of bytes; their hex digits flow through the shape in order.
    `highlight` maps a set of byte values to a colour (each digit pair of such a byte is coloured).
    """
    digits = "".join(f"{b:02X}" for b in stream)
    out = []
    k = 0
    for r, row in enumerate(grid):
        chars = []
        for on in row:
            if on:
                chars.append(digits[k % len(digits)])
                k += 1
            else:
                chars.append(" ")
        text = "".join(chars).rstrip()
        if not text.strip():
            continue
        out.append(f'<text x="{x:.1f}" y="{y + r * ch:.1f}" font-family="{MONO}" font-size="{size}" fill="{fill}" '
                   f'xml:space="preserve" textLength="{len(text) * cw:.1f}" lengthAdjust="spacing">{escape(text)}</text>')
    return "".join(out)


def pixel_fill(x, y, grid, s, colours, seed=7, density=0.92, edge_only=False):
    """A silhouette drawn as soft pixel blocks, optionally just its outline."""
    rnd = random.Random(seed)
    out = []
    R, C = len(grid), len(grid[0])
    for r in range(R):
        for c in range(C):
            if not grid[r][c]:
                continue
            if edge_only:
                inner = all(0 <= r + dr < R and 0 <= c + dc < C and grid[r + dr][c + dc]
                            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if inner:
                    continue
            elif rnd.random() > density:
                continue
            out.append(pixel(x + c * s, y + r * s, s, rnd.choice(colours), gap=s * 0.18))
    return "".join(out)


# ------------------------------------------------------------------ the plate


class Plate:
    def __init__(self, num, slug, title, chapter, w=1200, h=760):
        self.num, self.slug, self.title, self.chapter = num, slug, title, chapter
        self.w, self.h = w, h
        self.parts = []

    def add(self, *svg):
        self.parts.extend(svg)
        return self

    def frame(self):
        w, h = self.w, self.h
        out = [rect(0, 0, w, h, PAPER, "none", 0),
               f'<rect x="0" y="0" width="{w}" height="{h}" filter="url(#grain)" opacity="0.5" style="mix-blend-mode:multiply"/>',
               rect(18, 18, w - 36, h - 36, "none", INK, 2.2),
               rect(26, 26, w - 52, h - 52, "none", INK, 0.8)]
        # Fig. tag, top left
        label = f"Fig. {self.num}"
        out += [rect(26, 26, 96, 34, PAPER, INK, 1.6), t(74, 49, label, 16, INK, SANS, "middle", "bold")]
        # Registration marks, a nod to print
        for (cx, cy) in ((w - 52, 44), (44, h - 44)):
            out += [circle(cx, cy, 7, "none", INK, 1), line(cx - 11, cy, cx + 11, cy, INK, 0.8),
                    line(cx, cy - 11, cx, cy + 11, INK, 0.8)]
        # Title block, bottom right
        bw, bh = 470, 64
        bx, by = w - 26 - bw, h - 26 - bh
        out += [rect(bx, by, bw, bh, PAPER, INK, 1.6),
                line(bx, by + 34, bx + bw, by + 34, INK, 1),
                line(bx + bw - 96, by, bx + bw - 96, by + bh, INK, 1),
                t(bx + 12, by + 23, self.title, 15, INK, SANS, "start", "bold"),
                t(bx + 12, by + 53, f"Earshot field manual · {self.chapter}", 11.5, MUTED, SANS),
                t(bx + bw - 48, by + 18, "Plate", 10, MUTED, SANS, "middle"),
                t(bx + bw - 48, by + 30, f"{self.num:02d} / {TOTAL_PLATES}", 12, INK, MONO, "middle", "bold"),
                t(bx + bw - 48, by + 53, self.slug, 9.5, MUTED, MONO, "middle")]
        return out

    def svg(self):
        defs = ('<defs><filter id="grain" x="0" y="0" width="100%" height="100%">'
                '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" stitchTiles="stitch"/>'
                '<feColorMatrix type="matrix" values="0 0 0 0 0.11  0 0 0 0 0.10  0 0 0 0 0.09  0 0 0 -1.6 1.05"/>'
                '</filter>'
                '<pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse">'
                f'<circle cx="3" cy="3" r="1.05" fill="{INK}"/></pattern></defs>')
        f = self.frame()
        body = f[0] + "".join(self.parts) + f[1] + "".join(f[2:])
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}">{defs}{body}</svg>')


# ------------------------------------------------------------------ pixel type, halftone, rulers

# A 5×7 bitmap face for headlines, in the spirit of Earshot's own pixel UI.
_GLYPHS = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01111 10000 10000 10000 10000 10000 01111", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01111 10000 10000 10011 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10011 10101 10101 10101 11001 01110", "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111", "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010", "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110", "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110", "9": "01110 10001 10001 01111 00001 00010 01100",
    " ": "00000 00000 00000 00000 00000 00000 00000", ".": "00000 00000 00000 00000 00000 01100 01100",
    "-": "00000 00000 00000 11111 00000 00000 00000", "/": "00001 00010 00010 00100 01000 01000 10000",
    ":": "00000 01100 01100 00000 01100 01100 00000", "·": "00000 00000 00000 01100 01100 00000 00000",
    "?": "01110 10001 00001 00110 00100 00000 00100", "!": "00100 00100 00100 00100 00100 00000 00100",
    "→": "00000 00100 00010 11111 00010 00100 00000", "'": "00100 00100 01000 00000 00000 00000 00000",
}


def pixel_text(x, y, s, px=6, fill=INK, gap=1.2, spacing=1):
    """Text set in the 5×7 pixel face; `px` is one pixel's size. Returns (svg, width)."""
    out = []
    cx = x
    for ch in s.upper():
        rows = _GLYPHS.get(ch, _GLYPHS["?"]).split()
        for r, bits in enumerate(rows):
            for c, b in enumerate(bits):
                if b == "1":
                    out.append(pixel(cx + c * px, y + r * px, px, fill, gap))
        cx += (5 + spacing) * px
    return "".join(out), cx - x - spacing * px


def pixel_text_width(s, px=6, spacing=1):
    return len(s) * (5 + spacing) * px - spacing * px


def halftone(x, y, w, h, fill=INK, step=7, r=1.1, opacity=0.18):
    """A dot screen, like a print's halftone, clipped to a box."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#dots)" opacity="{opacity}"/>')


def ruler(x, y, length, vertical=False, step=10, start=0, every=5, labels=True, color=INK):
    """A printer's ruler strip with numbered ticks."""
    out = []
    n = int(length // step)
    for i in range(n + 1):
        major = i % every == 0
        tl = 9 if major else 4
        if vertical:
            out.append(line(x, y + i * step, x + tl, y + i * step, color, 0.8))
            if major and labels:
                out.append(t(x + 12, y + i * step + 3.5, str(start + i * step), 8, color, MONO))
        else:
            out.append(line(x + i * step, y, x + i * step, y - tl, color, 0.8))
            if major and labels:
                out.append(t(x + i * step, y - 12, str(start + i * step), 8, color, MONO, "middle"))
    return "".join(out)
