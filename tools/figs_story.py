"""Plates for the prologue and the anatomy chapter."""

import base64
import io
import json
import math
import os

from PIL import Image, ImageChops, ImageFilter, ImageOps

from plate import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "renders")

# Real bytes from the buds (Earshot's ProtocolTests), used wherever a shape is filled with hex.
CAPTURED = parse_hex(
    "AA 07 00 00 06 01 00 00 00 AA 0D 00 00 06 81 00 06 00 00 02 01 0A 03 00 "
    "AA 0B 00 00 0C 81 02 04 00 00 01 01 08 AA 0A 00 00 04 04 05 03 00 01 01 02 "
    "AA 08 00 00 04 84 43 01 00 0E AA 09 00 00 0F 81 44 02 00 00 02 AA 08 00 00 04 05 4F 01 00 01 "
    "AA 0D 00 00 04 02 8A 06 00 01 02 01 0A 03 00 AA 0F 00 00 04 02 8B 08 00 02 03 01 03 02 00 03 04 "
    "AA 11 00 00 0D 81 42 0A 00 00 04 09 00 1B 00 1D 01 1A 01 AA 09 00 00 10 81 41 02 00 00 01")


def crop_box(path_):
    return Image.open(path_).getchannel("A").getbbox()


# ------------------------------------------------------------------ 00 · cover

def cover(n):
    p = Plate(n, "cover", "Earshot field manual", "cover", 1200, 1560)
    p.add(halftone(26, 26, 1148, 1508, opacity=0.10))
    title, w = pixel_text(0, 0, "EARSHOT", 15, INK)
    p.add(f'<g transform="translate({(1200 - w) / 2:.0f},118)">{title}</g>')
    sub, w2 = pixel_text(0, 0, "FIELD MANUAL", 7, VERM)
    p.add(f'<g transform="translate({(1200 - w2) / 2:.0f},248)">{sub}</g>')
    p.add(t(600, 330, "How a Mac learned to talk to a pair of earbuds — from electrons to a menu-bar app",
            16, INK, SANS, "middle"))
    p.add(t(66, 96, "REF // RFCOMM CH 15 → NOW", 11, MUTED, MONO), t(1134, 96, "REALME BUDS AIR 7 · FW 1.1.0.62", 11, MUTED, MONO, "end"))

    # The bud: left half soft pixels, right half the bytes it actually said.
    path_ = os.path.join(R, "assembled.png")
    box = crop_box(path_)
    ratio = (box[3] - box[1]) / (box[2] - box[0])
    s = 8.8
    cols = int(800 / (s * ratio))
    grid = mask_grid(path_, cols, rows=round(cols * ratio))
    gx, gy = 600 - len(grid[0]) * s / 2, 420
    split = int(len(grid[0]) * 0.47)
    left = [[on and c < split for c, on in enumerate(row)] for row in grid]
    right = [[on and c >= split for c, on in enumerate(row)] for row in grid]
    p.add(pixel_fill(gx, gy, left, s, [INK, INK, COBALT, INK, GREEN], density=0.9))
    p.add(hex_fill(gx, gy + s * 0.85, right, CAPTURED * 6, cw=s, ch=s * 1.0, size=10.5))
    # A few stray pixels drifting off the edge, like a scan still settling.
    import random
    rnd = random.Random(3)
    for _ in range(46):
        r = rnd.randrange(len(grid))
        c = rnd.randrange(split - 30, split - 6)
        if grid[r][c] and not grid[r][max(0, c - 8)]:
            p.add(pixel(gx + (c - rnd.randint(4, 12)) * s, gy + r * s, s, rnd.choice([COBALT, VERM])))
    by = gy + len(grid) * s
    p.add(leader(gx + 0.63 * len(grid[0]) * s, gy + 0.22 * len(grid) * s, 1010, 470, None, None, VERM),
          t(1010, 452, "AA 07 00 00 06 01 00 00 00", 13, VERM, MONO, "middle", "bold"),
          t(1010, 490, "“how full is your battery?”", 12, INK, SANS, "middle"),
          leader(gx + 0.2 * len(grid[0]) * s, gy + 0.36 * len(grid) * s, 200, by - 120, None, None, COBALT),
          t(200, by - 102, "every block a byte", 12, COBALT, MONO, "middle", "bold"),
          t(200, by - 84, "the same data, seen as pixels", 12, INK, SANS, "middle"))
    p.add(ruler(66, by + 60, 1068, step=12, every=5))
    rows = ["Fourteen chapters · thirty-eight plates", "Physics · radio · Bluetooth · bytes · protocols · Swift · shipping"]
    p.add(lines(600, by + 110, rows, 15, 1.6, family=SANS, anchor="middle"))
    return p


# ------------------------------------------------------------------ 00 · the story as a sequence

STORY = [
    ("No Mac app", "realme Link: Android & iPhone only"),
    ("Probe", "ask the buds what services they offer"),
    ("Channel 15", "“oppointeraction” – the hidden door"),
    ("First words", "left bud 10 %, right bud silent"),
    ("Earshot 0.1", "menu bar, pixel UI, live battery"),
    ("Linking fixes", "fixed size, retries, link reset"),
    ("Taps & ANC", "change → read back → revert"),
    ("The watcher", "EQ, enhancer, spatial mapped"),
    ("v1.0.0", "first release"),
    ("Seven brands", "drivers from published work"),
    ("v1.1.0", "shipped · CI green"),
]


def timeline(n):
    p = Plate(n, "timeline", "The story in eleven steps", "00 · prologue", 1500, 980)
    path_ = os.path.join(R, "assembled.png")
    box = crop_box(path_)
    grid = mask_grid(path_, 26, rows=round(26 * (box[3] - box[1]) / (box[2] - box[0])))
    s = 3.6
    k = len(STORY)
    pts = []
    for i in range(k):
        u = i / (k - 1)
        x = 120 + u * 1190
        y = 600 - math.sin(u * math.pi * 0.72) * 330
        pts.append((x, y))
    # The arc and its dotted floor, like a figure walking through time.
    d = "M" + " L".join(f"{x + 54:.1f},{y + len(grid) * s + 6:.1f}" for x, y in pts)
    p.add(path(d, INK, 1.2, dash="1 6"))
    for i, ((x, y), (name, note)) in enumerate(zip(pts, STORY)):
        last = i == k - 1
        p.add(pixel_fill(x, y, grid, s, [VERM] if last else [INK], edge_only=not last))
        up = i % 2 == 0
        lx, ly = x + 54, (y - 40 if up else y + len(grid) * s + 70)
        p.add(line(x + 54, y + (0 if up else len(grid) * s), lx, ly + (10 if up else -22), MUTED, 0.8, "2 3"))
        p.add(t(lx, ly, f"{i + 1:02d} {name}", 14, VERM if last else INK, SANS, "middle", "bold"),
              t(lx, ly + 17, note, 11, MUTED, SANS, "middle"))
    p.add(t(120, 860, "THIS IS WHERE WE STARTED", 12, INK, MONO), arrow(250, 846, 160, 720, INK, 1),
          t(1380, 150, "THIS IS EARSHOT TODAY", 12, VERM, MONO, "end"), arrow(1330, 162, pts[-1][0] + 40, pts[-1][1] - 50, VERM, 1))
    p.add(ruler(66, 920, 1300, step=10, every=10, labels=False))
    return p


# ------------------------------------------------------------------ 01 · anatomy

ASSEMBLED_POINTS = [
    ("ear_tip", "Ear tip – silicone seal"), ("mesh", "Nozzle & acoustic mesh"), ("wear_sensor", "IR wear sensor"),
    ("front_shell", "Front shell – the driver's chamber"), ("ff_mic", "Feed-forward mic"),
    ("back_shell", "Back shell – board and cell inside"), ("touch_pad", "Touch area on the stem"),
    ("antenna", "Antenna in the stem"), ("talk_mic", "Talk mic, near your mouth"), ("pogo", "Pogo charging contacts"),
]


def anatomy(n):
    p = Plate(n, "anatomy", "A true-wireless earbud, assembled", "01 · anatomy", 1200, 980)
    path_ = os.path.join(R, "assembled.png")
    box = crop_box(path_)
    uri, w, h = processed_render(path_, 560, crop=box)
    ox, oy = 90, 150
    sc = 560 / (box[2] - box[0])
    p.add(image(uri, ox, oy, w, h))
    at = json.load(open(os.path.join(R, "assembled.json")))["parts"]
    pts = sorted(ASSEMBLED_POINTS, key=lambda kv: at[kv[0]][1])
    for i, (key, label) in enumerate(pts):
        px, py = at[key]
        ax, ay = ox + (px - box[0]) * sc, oy + (py - box[1]) * sc
        p.add(leader(ax, ay, 760, 150 + i * 62, chr(ord("A") + i), label, INK))
    p.add(dim(ox, ox + w, oy + h + 34, "≈ 22 mm, tip to back"), t(90, 120, "Stylised; real buds pack the same parts tighter.", 12, MUTED, SANS))
    return p


def exploded(n):
    p = Plate(n, "exploded", "Every part, pulled apart along its axis", "01 · anatomy", 1500, 1240)
    path_ = os.path.join(R, "exploded.png")
    meta = json.load(open(os.path.join(R, "exploded.json")))
    box = crop_box(path_)
    W = 1240
    uri, w, h = processed_render(path_, W, crop=box)
    ox, oy = 110, 120
    sc = W / (box[2] - box[0])
    p.add(image(uri, ox, oy, w, h))
    # The assembly axis, drawn like a centre line.
    parts = meta["parts"]

    def at(key):
        x, y = parts[key]
        return ox + (x - box[0]) * sc, oy + (y - box[1]) * sc

    a, b = at("ear_tip"), at("touch_pad")
    p.add(line(a[0] - 40, a[1] - 14, b[0] + 60, b[1] + 6, VERM, 1, "18 5 3 5"))
    names = [
        ("ear_tip", "Ear tip"), ("mesh", "Acoustic mesh"), ("front_shell", "Front shell + nozzle"),
        ("wear_sensor", "IR wear sensor"), ("diaphragm", "Diaphragm"), ("voice_coil", "Voice coil"),
        ("magnet", "Magnet"), ("fb_mic", "Feedback mic"), ("pcb", "PCB"), ("soc", "Bluetooth SoC"),
        ("flash", "Flash (settings live here)"), ("pmic", "PMIC – power"), ("battery", "Li-ion cell"),
        ("back_shell", "Back shell"), ("touch_pad", "Touch area"), ("ff_mic", "Feed-forward mic"),
        ("stem", "Stem"), ("antenna", "Antenna"), ("case_magnet", "Case magnet"), ("talk_mic", "Talk mic"),
        ("pogo", "Pogo contacts"),
    ]
    offsets = {"soc": (30, -150), "flash": (-60, -170), "pmic": (40, 140), "pcb": (-10, 150), "mesh": (0, 120),
               "ear_tip": (0, -150), "front_shell": (-30, 170), "diaphragm": (0, -190), "voice_coil": (0, 170),
               "magnet": (30, -170), "battery": (20, -190), "back_shell": (60, -150), "touch_pad": (90, -20),
               "ff_mic": (40, -70), "wear_sensor": (60, -20), "fb_mic": (60, 30), "stem": (-110, 30),
               "antenna": (70, 0), "case_magnet": (-80, -20), "talk_mic": (-80, 0), "pogo": (80, 0)}
    for i, (key, label) in enumerate(names):
        x, y = at(key)
        dx, dy = offsets.get(key, (0, -120))
        letter = chr(ord("A") + i)
        p.add(leader(x, y, x + dx, y + dy, letter))
    # Legend in three columns.
    lx, ly = 70, oy + h + 50
    for i, (key, label) in enumerate(names):
        col, row = divmod(i, 7)
        x, y = lx + col * 300, ly + row * 24
        p.add(tag(x + 10, y - 4, chr(ord("A") + i), INK, PAPER, 9), t(x + 28, y + 1, label, 13, INK, SANS))
    return p


def outline_icon(path_, accent, px=230):
    """A part render turned into a glowing double outline, like a specimen sheet."""
    im = Image.open(path_).convert("RGBA")
    box = im.getchannel("A").getbbox()
    im = im.crop(box)
    k = px / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
    pad = 16
    canvas = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    canvas.paste(im, (pad, pad))
    a = canvas.getchannel("A").point(lambda v: 255 if v > 90 else 0)
    outer = a.filter(ImageFilter.MaxFilter(9))
    ring = ImageChops.subtract(outer, a.filter(ImageFilter.MinFilter(5)))
    inner = ImageChops.subtract(a, a.filter(ImageFilter.MinFilter(3)))
    out = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    tint = ImageOps.posterize(canvas.convert("RGB"), 3)
    body = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    body.paste(tint, mask=a.point(lambda v: 110 if v else 0))
    out.alpha_composite(body)
    out.paste(Image.new("RGBA", canvas.size, accent), mask=ring)
    out.paste(Image.new("RGBA", canvas.size, INK), mask=inner)
    buf = io.BytesIO()
    out.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), out.width, out.height


CATALOGUE = [
    ("ear-tip", "Ear tip", "seals the canal; bass needs the seal", GREEN),
    ("acoustic-mesh", "Acoustic mesh", "keeps wax out, tunes highs", INK),
    ("front-shell", "Front shell", "the cavity the driver breathes into", OCHRE),
    ("ir-wear-sensor", "IR wear sensor", "light bounces off skin → in ear", VERM),
    ("diaphragm", "Diaphragm", "the moving cone that pushes air", OCHRE),
    ("voice-coil", "Voice coil", "current in a magnetic field = force", VERM),
    ("magnet", "Magnet", "the fixed field the coil pushes on", COBALT),
    ("feedback-mic", "Feedback mic", "hears what reaches your ear", COBALT),
    ("pcb", "PCB", "SoC, flash and PMIC on one board", GREEN),
    ("li-ion-cell", "Li-ion cell", "≈ 3.7 V, tens of mAh", VERM),
    ("back-shell", "Back shell", "outer half, holds the board", OCHRE),
    ("touch-pad", "Touch pad", "capacitance changes under a finger", OCHRE),
    ("feed-forward-mic", "Feed-forward mic", "hears the world outside", COBALT),
    ("stem", "Stem", "puts mic and antenna lower", OCHRE),
    ("antenna", "Antenna", "2.4 GHz in and out", COBALT),
    ("case-magnet", "Case magnet", "snaps the bud into its dock", COBALT),
    ("talk-mic", "Talk mic", "aimed at your mouth for calls", COBALT),
    ("pogo-contacts", "Pogo contacts", "5 V in from the case", OCHRE),
]


def catalogue(n):
    p = Plate(n, "parts", "Parts catalogue", "01 · anatomy", 1400, 1180)
    files = sorted(os.listdir(os.path.join(R, "parts")))
    cols, cw, chh = 6, 212, 300
    for i, (slug, name, role, accent) in enumerate(CATALOGUE):
        f = next(x for x in files if x.endswith(slug + ".png"))
        uri, w, h = outline_icon(os.path.join(R, "parts", f), accent, 150)
        col, row = i % cols, i // cols
        cx, cy = 80 + col * cw + cw / 2, 120 + row * chh
        p.add(image(uri, cx - w / 2, cy + 90 - h / 2, w, h))
        p.add(t(cx, cy + 205, f"PART – {i + 1:03d}", 12, INK, MONO, "middle", "bold"),
              t(cx, cy + 224, name, 13, INK, SANS, "middle", "bold"),
              t(cx, cy + 242, role, 10.5, MUTED, SANS, "middle"))
    return p


CASE_POINTS = [
    ("A", "Lid (magnet keeps it shut)", "lid"),
    ("B", "Buds sit stem-down in wells", "bud"),
    ("C", "Hall sensor: lid open → wake buds", "hall"),
    ("D", "Charge LED", "led"),
    ("E", "Case cell + charger IC (inside)", "body"),
]


def case(n):
    p = Plate(n, "case", "The case is a computer too", "01 · anatomy", 1200, 900)
    path_ = os.path.join(R, "case.png")
    box = crop_box(path_)
    uri, w, h = processed_render(path_, 640, crop=box)
    ox, oy = 70, 130
    sc = 640 / (box[2] - box[0])
    p.add(image(uri, ox, oy, w, h))
    with open(os.path.join(R, "case.json")) as f:
        at = json.load(f)["parts"]
    for i, (letter, label, key) in enumerate(CASE_POINTS):
        px, py = at[key]
        ax, ay = ox + (px - box[0]) * sc, oy + (py - box[1]) * sc
        p.add(leader(ax, ay, 780, 160 + i * 64, letter, label))
    p.add(para(780, 520, "The case has its own battery, a charger and a small controller. It tops the buds up "
                         "through two pogo pins, reports its own level to the buds, and tells them when the lid "
                         "opens so they can wake and reconnect. That is why Earshot can show a case battery at "
                         "all: the buds relay what the case told them.", 46, 13, family=SANS))
    return p


def board(n):
    """The bud's electronics as a silkscreened board, like a dev board's top layer."""
    p = Plate(n, "board", "Inside the board: who talks to whom", "01 · anatomy", 1400, 940)
    BX, BY, BW, BH = 90, 120, 1220, 640
    pcb = "#C8475A"
    silk = "#F6EEE8"
    p.add(rect(BX, BY, BW, BH, pcb, INK, 2, 34))
    for (hx, hy) in ((BX + 40, BY + 40), (BX + BW - 40, BY + 40), (BX + 40, BY + BH - 40), (BX + BW - 40, BY + BH - 40)):
        p.add(circle(hx, hy, 15, PAPER, INK, 1.5))
    # Header pads along the top edge, like a dev board.
    for i in range(22):
        x = BX + 120 + i * 38
        p.add(rect(x - 9, BY + 22, 18, 18, "#D7B24A", INK, 1, 3), t(x, BY + 58, f"P{i:02d}", 8, silk, MONO, "middle"))

    def chip(x, y, w, h, name, sub, pins=8):
        out = rect(x, y, w, h, "#232020", INK, 1.6, 6)
        for k in range(pins):
            px = x + 12 + k * (w - 24) / max(1, pins - 1)
            out += rect(px - 3, y - 7, 6, 7, "#C9CCCF", "none", 0) + rect(px - 3, y + h, 6, 7, "#C9CCCF", "none", 0)
        out += t(x + w / 2, y + h / 2 - 2, name, 16, silk, MONO, "middle", "bold")
        out += t(x + w / 2, y + h / 2 + 18, sub, 10.5, "#CFC7BF", SANS, "middle")
        return out

    def pad(x, y, name):
        return rect(x - 26, y - 14, 52, 28, "none", silk, 1.4, 6) + t(x, y + 4, name, 10, silk, MONO, "middle", "bold")

    def trace(pts, label=None, at=0.5):
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        out = path(d, silk, 2.2)
        if label:
            (x1, y1), (x2, y2) = pts[0], pts[-1]
            mx, my = pts[len(pts) // 2] if len(pts) > 2 else ((x1 + x2) / 2, (y1 + y2) / 2)
            out += rect(mx - len(label) * 3.6 - 6, my - 10, len(label) * 7.2 + 12, 20, pcb, "none", 0) + t(mx, my + 4, label, 10.5, silk, MONO, "middle", "bold")
        return out

    soc = (560, 330, 280, 170)
    p.add(trace([(840, 380), (1000, 380), (1000, 220), (1160, 220)], "RF 2.4 GHz"),
          trace([(700, 330), (700, 230), (560, 230)], "SPI"),
          trace([(560, 450), (420, 450), (420, 560)], "I²C"),
          trace([(840, 460), (980, 460), (980, 560)], "I²S / PDM"),
          trace([(700, 500), (700, 620), (860, 620)], "PWM / DAC"),
          trace([(560, 370), (300, 370), (300, 260)], "GPIO"),
          trace([(560, 410), (240, 410), (240, 520)], "ADC"),
          trace([(420, 640), (420, 700), (1080, 700), (1080, 650)], "VBAT 3.7 V"))
    p.add(chip(*soc, "SoC", "radio · DSP · CPU · RAM", 12),
          chip(440, 190, 180, 76, "FLASH", "firmware + your settings", 6),
          chip(330, 560, 180, 80, "PMIC", "charging · power rails", 6),
          chip(1110, 175, 150, 80, "ANT", "chip antenna", 4))
    p.add(pad(980, 585, "MIC×3"), pad(880, 620, "SPK±"), pad(300, 240, "TOUCH"), pad(240, 545, "IR"),
          pad(1080, 630, "POGO"), pad(200, 300, "LED"))
    p.add(t(BX + BW - 70, BY + BH - 30, "EARSHOT FIELD BOARD · REV 1.1", 11, silk, MONO, "end", "bold"),
          t(BX + 60, BY + BH - 30, "Not a real layout: the parts and buses a TWS bud really has.", 11, silk, SANS))
    p.add(para(90, 800, "Every setting Earshot changes ends up as a few bytes in the flash, written by firmware "
                        "running on the SoC's CPU. The radio part of the same chip carries our bytes in and out; "
                        "the DSP part runs the noise cancelling and EQ we switch between.", 120, 14, family=SANS))
    return p


def anc(n):
    p = Plate(n, "anc", "Noise cancelling: adding the opposite", "01 · anatomy", 1200, 760)
    x0, x1 = 120, 1080

    def wave(y, amp, phase=0, color=INK, sw=2.2, extra=0.0):
        pts = []
        for i in range(241):
            u = i / 240
            v = amp * (math.sin(u * 2 * math.pi * 5 + phase) + 0.45 * math.sin(u * 2 * math.pi * 13 + phase * 1.3))
            v += extra * math.sin(u * 2 * math.pi * 31)
            pts.append(f"{x0 + u * (x1 - x0):.1f},{y - v:.1f}")
        return path("M" + " L".join(pts), color, sw)

    rows = [(190, "noise outside", "the feed-forward mic hears it", wave(190, 36, 0, INK)),
            (330, "anti-noise", "DSP plays it inverted (+180°)", wave(330, 36, math.pi, VERM)),
            (480, "what reaches the ear", "the feedback mic checks the leftover", wave(480, 0, 0, COBALT, 2.2, 4))]
    for y, name, note, w in rows:
        p.add(line(x0, y, x1, y, FAINT, 0.8, "3 4"), w, t(x0, y - 56, name.upper(), 13, INK, MONO, "start", "bold"),
              t(x1, y - 56, note, 12, MUTED, SANS, "end"))
    p.add(t(70, 265, "+", 34, INK, SANS, "middle", "bold"), t(70, 415, "=", 34, INK, SANS, "middle", "bold"))
    p.add(para(120, 580, "Sound is pressure going up and down. Add a copy that goes down exactly when the original "
                         "goes up and the two cancel. Earshot never touches the maths – it picks the mode: "
                         "Off, Transparency (mics pass the outside through on purpose) or ANC, and on realme "
                         "buds an ANC strength: mild 04, moderate 10, deep 08, adaptive 20.", 120, 14, family=SANS))
    return p


PLATES = [cover, timeline, anatomy, exploded, catalogue, case, board, anc]
