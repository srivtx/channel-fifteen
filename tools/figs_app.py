"""Plates for chapters 10 (the app), 11 (shipping) and the back cover."""

import base64
import io
import os

from PIL import Image

from plate import *
from figs_story import CAPTURED, R, crop_box

SCREENS = os.path.expanduser("~/Desktop/new/earshot/docs/screens")
NAVY = "#1D2B45"
GOLD = "#D4A84A"
GOLD_DIM = "#8F7536"


def png_uri(path_, width):
    im = Image.open(path_).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), im.height


def board_chip(x, y, w, h, title, items, accent=GOLD):
    out = rect(x, y, w, h, "#121B2C", accent, 1.6, 6)
    for k in range(int(w // 22)):
        px = x + 14 + k * 22
        out += rect(px, y - 6, 8, 6, "#B9BDC4", "none", 0) + rect(px, y + h, 8, 6, "#B9BDC4", "none", 0)
    out += t(x + 16, y + 28, title, 15, accent, MONO, "start", "bold")
    for i, it in enumerate(items):
        out += t(x + 16, y + 52 + i * 19, it, 12, "#E9E2D2", MONO)
    return out


def trace(pts, label=None, color=GOLD, lanes=3, gap=5):
    """A bus: several parallel gold traces along the same route, like the PCB-trace cat."""
    out = ""
    for k in range(lanes):
        off = (k - (lanes - 1) / 2) * gap
        d = "M" + " L".join(f"{x + (off if i % 2 else 0):.1f},{y + (0 if i % 2 else off):.1f}" for i, (x, y) in enumerate(pts))
        out += path(d, color, 1.6)
    if label:
        (x1, y1), (x2, y2) = pts[0], pts[1]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        out += rect(mx - len(label) * 3.7 - 8, my - 11, len(label) * 7.4 + 16, 22, NAVY, GOLD, 1, 11)
        out += t(mx, my + 4, label, 11, GOLD, MONO, "middle", "bold")
    return out


def architecture(n):
    p = Plate(n, "architecture", "Earshot's architecture as a circuit board", "10 · the app", 1500, 1100)
    BX, BY, BW, BH = 70, 110, 1360, 830
    p.add(rect(BX, BY, BW, BH, NAVY, INK, 2, 26))
    for k in range(34):
        p.add(circle(BX + 40 + k * 38, BY + 24, 5, "none", GOLD_DIM, 1.4))
    p.add(trace([(500, 300), (640, 300)], "Intent", GOLD), trace([(870, 300), (990, 300)], "Outgoing", GOLD),
          trace([(990, 520), (870, 520)], "Inbound", GOLD), trace([(640, 520), (500, 520)], "Event", GOLD),
          trace([(1110, 640), (1110, 760)], "bytes", GOLD), trace([(330, 640), (330, 760)], "@Observable", GOLD),
          trace([(760, 640), (760, 760)], "Capabilities", GOLD_DIM, 2))
    p.add(board_chip(160, 200, 340, 440, "UI  (SwiftUI)", ["PopoverView", "  header · battery", "Tabs", "  Buds · Sound · Taps",
                                                           "Components", "  pixel buttons, rows", "PixelArt", "  sprites from bitmaps",
                                                           "Theme", "  White · Dark · System", "", "never talks Bluetooth"]))
    p.add(board_chip(640, 200, 230, 440, "BudsStore", ["@MainActor", "@Observable", "", "battery, placement", "noise, level",
                                                       "toggles, eq, touch", "pending…", "", "optimistic UI", "rollback", "notice"], VERM))
    p.add(board_chip(990, 200, 330, 440, "BudsLink", ["IOBluetooth", "find paired buds", "SDP → channel", "open RFCOMM, retry",
                                                      "one message in flight", "reply timeout 2.5 s", "supersede", "poll every 90 s",
                                                      "", "Journal (600 lines)"], GOLD))
    p.add(board_chip(160, 760, 1160, 150, "EarshotCore  (pure Swift, no Bluetooth, fully tested)",
                     ["Model · Driver protocol · Profiles · Checksums",
                      "OPODriver · GalaxyDriver · SonyDriver · NothingDriver · SoundcoreDriver"], "#7FB6A0"))
    p.add(t(1340, 280, "→ macOS", 12, GOLD, MONO, "end"), t(1340, 300, "IOBluetooth", 12, GOLD, MONO, "end"),
          t(BX + BW - 30, BY + BH - 24, "EARSHOT · MAIN BOARD · v1.1.0", 11, GOLD_DIM, MONO, "end", "bold"))
    p.add(para(70, 990, "Data only flows one way around the loop. The UI calls the store; the store turns a tap into an "
                        "Intent for the link; the link asks the brand's Driver to encode it, writes the bytes, feeds "
                        "replies back to the driver, and passes the resulting Events to the store, which updates "
                        "what SwiftUI draws.", 190, 14, family=SANS))
    return p


def states(n):
    p = Plate(n, "states", "BudsLink's four states", "10 · the app", 1400, 960)
    nodes = {"noBuds": (220, 250), "away": (700, 250), "linking": (700, 620), "linked": (1180, 620)}
    notes = {"noBuds": "no supported buds paired", "away": "paired, not connected", "linking": "connected for audio,\nopening channel",
             "linked": "control channel open"}
    for name, (x, y) in nodes.items():
        col = GREEN if name == "linked" else (VERM if name == "linking" else INK)
        p.add(rect(x - 120, y - 52, 240, 104, PAPER, col, 2.6, 16), rect(x - 112, y - 44, 224, 88, "none", col, 0.8, 12),
              t(x, y - 6, name, 20, col, MONO, "middle", "bold"))
        for i, r in enumerate(notes[name].split("\n")):
            p.add(t(x, y + 18 + i * 16, r, 11.5, MUTED, SANS, "middle"))
    edges = [
        ((340, 235), (580, 235), "buds paired (refresh)"), ((580, 270), (340, 270), "unpaired"),
        ((690, 302), (690, 568), "connect notification → open after 1 s"), ((720, 568), (720, 302), "disconnect"),
        ((820, 600), (1060, 600), "rfcommChannelOpenComplete ✓"), ((1060, 640), (820, 640), "channel closed while connected"),
        ((1180, 568), (820, 270), "disconnect"),
    ]
    for (a, b, lab) in edges:
        p.add(arrow(*a, *b, INK, 1.6))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if abs(a[0] - b[0]) < 40:
            left = a[0] < 705
            p.add(t(mx + (-16 if left else 16), my + 4, lab, 11.5, INK, SANS, "end" if left else "start"))
        else:
            p.add(rect(mx - len(lab) * 3.4 - 6, my - 11, len(lab) * 6.8 + 12, 20, PAPER, "none", 0, 4),
                  t(mx, my + 4, lab, 11.5, INK, SANS, "middle"))
    p.add(path("M610,690 C560,780 640,800 660,690", VERM, 1.6), t(560, 800, "open refused → retry with backoff, reset after 4", 11.5, VERM, SANS),
          path("M1240,680 C1300,780 1180,790 1200,680", GREEN, 1.6), t(1100, 800, "poll battery every 90 s", 11.5, GREEN, SANS))
    p.add(t(110, 880, "Mac wakes from sleep → tear down, re-scan after 2 s. The header subtitle shows the state; the menu-bar icon the lowest bud.", 13, INK, SANS))
    return p


def queue(n):
    p = Plate(n, "queue", "One message in flight", "10 · the app", 1500, 1000)
    y0 = 200
    p.add(t(80, 150, "THE QUEUE  (BudsLink.queue)", 13, INK, MONO, "start", "bold"))
    items = [("0106", "battery?", INK, "reply 8106"), ("0109", "status?", INK, "reply 8109"),
             ("0404 01 01 08", "ANC deep", COBALT, "superseded"), ("0406 02", "EQ Serenade", COBALT, "reply 8406")]
    for i, (code, name, col, note) in enumerate(items):
        x = 80 + i * 230
        dead = note == "superseded"
        p.add(rect(x, y0, 210, 90, PAPER_DEEP, col, 1.8, 10, 'stroke-dasharray="5 4"' if dead else ""),
              t(x + 16, y0 + 34, code, 15, FAINT if dead else col, MONO, "start", "bold"), t(x + 16, y0 + 58, name, 13, FAINT if dead else INK, SANS),
              t(x + 16, y0 + 78, note, 11, VERM if dead else MUTED, MONO))
        if dead:
            p.add(line(x + 10, y0 + 10, x + 200, y0 + 80, VERM, 2))
    p.add(rect(80 + 4 * 230, y0, 210, 90, PAPER, VERM, 2.2, 10), t(80 + 4 * 230 + 16, y0 + 34, "0404 01 01 04", 15, VERM, MONO, "start", "bold"),
          t(80 + 4 * 230 + 16, y0 + 58, "ANC mild (newer)", 13, INK, SANS), t(80 + 4 * 230 + 16, y0 + 78, "same key → replaces", 11, VERM, MONO))
    p.add(arrow(80 + 4 * 230 + 100, y0 + 110, 80 + 2 * 230 + 120, y0 + 110, VERM, 1.4, dash="4 4"))
    p.add(t(80, 400, "IN FLIGHT", 13, INK, MONO, "start", "bold"), rect(80, 420, 260, 90, INK, "none", 0, 10),
          t(100, 456, "0106 battery?", 16, PAPER, MONO, "start", "bold"), t(100, 484, "waiting for 8106…", 12, "#CFC7BF", MONO))
    rules = [("reply arrives", "clear the slot, send the next", GREEN), ("no reply in 2.5 s", "report the setting failed, re-read it, move on", VERM),
             ("message expects no reply", "wait 0.15 s, then the next (subscribe, Galaxy writes)", OCHRE),
             ("newer request, same key", "drop the queued one (key = command + payload minus its last byte)", COBALT),
             ("every 90 s", "driver.poll(): battery and wear status", INK)]
    for i, (when, what, col) in enumerate(rules):
        y = 580 + i * 44
        p.add(pixel(80, y - 16, 22, col, 2, 5), t(116, y, when, 14, INK, SANS, "start", "bold"), t(380, y, what, 14, MUTED, SANS))
    p.add(para(80, 830, "Earbuds are small computers with small buffers: two commands back to back and the second is often "
                        "silently dropped. So BudsLink sends one message, waits for its answer, then sends the next. Tapping "
                        "through ANC strengths quickly would queue a pile of stale requests; the supersede key keeps only "
                        "the newest one per setting.", 190, 14, family=SANS))
    return p


def optimistic(n):
    p = Plate(n, "optimistic", "Showing the change before the buds confirm it", "10 · the app", 1500, 980)
    lanes = [("APPLIED", GREEN, ["tap ANC", "control shows ANC (pending)", "0404 sent", "8404 00", "settled"]),
             ("REFUSED", VERM, ["tap ANC", "control shows ANC (pending)", "0404 sent", "8404 0E", "rolled back + notice"]),
             ("NO ANSWER", OCHRE, ["tap ANC", "control shows ANC (pending)", "0404 sent", "… 2.5 s …", "rolled back, re-read"])]
    for i, (name, col, steps) in enumerate(lanes):
        y = 190 + i * 210
        p.add(t(80, y + 6, name, 15, col, MONO, "start", "bold"), line(240, y, 1420, y, FAINT, 1, "2 4"))
        for k, s in enumerate(steps):
            x = 300 + k * 270
            last = k == len(steps) - 1
            p.add(pixel(x - 13, y - 13, 26, col if last else (INK if k else PAPER_DEEP), 0, 5))
            p.add(t(x, y + 40, s, 13, INK, SANS, "middle", "bold" if last else "normal"))
            if k:
                p.add(arrow(x - 250, y, x - 20, y, MUTED, 1))
    p.add(rect(240, 790, 880, 46, INK, "none", 0, 10), t(262, 819, "realme Buds Air7 · Buds report no bud in an ear. Seat them and retry.", 14, "#F3A0A0", SANS),
          t(1140, 819, "← the only place errors appear", 13, MUTED, SANS))
    p.add(para(80, 880, "BudsStore keeps pendingNoiseMode / pendingAncLevel / pendingEq next to the confirmed values and "
                        "shows the pending one, so taps feel instant. The driver reports .applied, .refused(code) or the "
                        "link reports a failure; the store then settles or rolls back. No pop-ups, no toasts.", 190, 14, family=SANS))
    return p


def ui(n):
    p = Plate(n, "ui", "The three screens", "10 · the app", 1500, 1120)
    names = [("buds-dark", "BUDS"), ("sound-dark", "SOUND"), ("taps-dark", "TAPS")]
    for i, (f, label) in enumerate(names):
        uri, h = png_uri(os.path.join(SCREENS, f + ".png"), 330)
        x = 110 + i * 460
        p.add(rect(x + 8, 168, 330, h, INK, "none", 0, 14), image(uri, x, 160, 330, h, 'style="border-radius:12px"'),
              t(x, 145, f"{label} TAB", 13, INK, MONO, "start", "bold"))
    notes = [
        (110 + 340, 300, "battery per bud + case, IN EAR / OUT / CASE tags"),
        (110 + 340, 460, "Off · Ambient · ANC, then strength"),
        (570 + 340, 360, "EQ presets in a grid, switches below"),
        (1030 + 340, 330, "pick a side, then each gesture's action"),
    ]
    for x, y, lab in notes:
        p.add(circle(x - 4, y, 4, VERM), line(x - 4, y, x + 30, y, VERM, 1))
    p.add(t(110, 900, "Fixed popover size (no jumping, no flicker) · soft pixel blocks · White / Dark / System themes, no blur ·", 14, INK, SANS),
          t(110, 924, "settings behind the gear · errors only in the header subtitle · a control appears only if the buds have it.", 14, INK, SANS),
          t(110, 960, "Live renders from the app's own DevShots hook (EARSHOT_SHOTS) with real data from the Buds Air 7.", 12, MUTED, SANS))
    for i, (_, _, lab) in enumerate(notes):
        p.add(t(110 + i * 345, 1010, f"{chr(65 + i)} · {lab}", 12, INK, SANS))
        x, y = notes[i][0], notes[i][1]
        p.add(tag(x + 42, y, chr(65 + i), VERM, PAPER, 10))
    return p


def journal(n):
    """Earshot's traffic journal, printed like a bank passbook."""
    p = Plate(n, "journal", "The journal: a passbook of bytes", "10 · the app", 1400, 1180)
    BX, BY, BW = 90, 120, 1220
    rows = [
        ("note", "begin · realme Buds Air7 · realme (tested)", ""),
        ("note", "open channel 15 attempt 0: 0", ""),
        ("→", "AA 0A 00 00 05 02 00 06 00 09 01 02 03 05 06", "subscribe"),
        ("→", "AA 07 00 00 06 01 01 00 00", "battery?"),
        ("←", "AA 0D 00 00 06 81 01 06 00 00 02 01 0A 03 00", "left 10 %"),
        ("→", "AA 07 00 00 09 01 02 00 00", "where?"),
        ("←", "AA 0F 00 00 09 81 02 08 00 00 03 01 03 02 00 03 04", "L ear · R case"),
        ("→", "AA 09 00 00 0C 01 03 02 00 01 01", "mode?"),
        ("←", "AA 0B 00 00 0C 81 03 04 00 00 01 01 08", "ANC deep"),
        ("→", "AA 0A 00 00 04 04 04 03 00 01 01 02", "set ambient"),
        ("←", "AA 08 00 00 04 84 04 01 00 00", "applied"),
        ("←", "AA 0D 00 00 04 02 8A 06 00 01 02 01 0A 03 00", "push battery"),
        ("→", "AA 0A 00 00 04 04 05 03 00 01 01 08", "set ANC"),
        ("←", "AA 08 00 00 04 84 05 01 00 0E", "refused 0E"),
        ("note", "no reply", ""),
    ]
    rh = 46
    H = 120 + len(rows) * rh + 90
    p.add(rect(BX, BY, BW, H, "#F4E6D9", "#C9826C", 1.6, 18))
    hdr = [("#", 30), ("時 time", 90), ("dir", 210), ("bytes", 300), ("meaning", 1010)]
    p.add(rect(BX, BY, BW, 70, "none", "#C9826C", 0, 18), t(BX + 30, BY + 44, "EARSHOT REPORT", 22, "#B2553C", SANS, "start", "bold"),
          t(BX + BW - 30, BY + 44, "15", 34, "#B2553C", SANS, "end", "bold"))
    for k in range(18):
        p.add(rect(BX + 360 + k * 6, BY + 22, 3 if k % 3 else 1.5, 30, INK, "none", 0))
    y = BY + 100
    for c, x in hdr:
        p.add(t(BX + x, y, c, 11, "#B2553C", MONO, "start", "bold"))
    for i, (d, b, m) in enumerate(rows):
        yy = y + 14 + i * rh
        if i % 2 == 0:
            p.add(rect(BX + 6, yy, BW - 12, rh, "#EBC9BC", "none", 0, 0, 'opacity="0.55"'))
        p.add(line(BX + 6, yy + rh, BX + BW - 6, yy + rh, "#D7A493", 0.8))
        for x in (80, 200, 290, 1000):
            p.add(line(BX + x, yy, BX + x, yy + rh, "#D7A493", 0.8))
        tt = f"0.{i * 13 % 97:02d}" if i else "0.00"
        col = VERM if d == "←" else (COBALT if d == "→" else MUTED)
        p.add(t(BX + 30, yy + 30, f"{i + 1:02d}", 13, "#B2553C", MONO), t(BX + 90, yy + 30, f"+{i * 0.17:.2f}s", 13, INK, MONO),
              t(BX + 230, yy + 30, d, 15 if d != "note" else 11, col, MONO, "start", "bold"),
              t(BX + 300, yy + 30, b, 14 if d != "note" else 13, INK if d != "note" else MUTED, MONO, "start", "bold" if d != "note" else "normal"),
              t(BX + 1010, yy + 30, m, 13, col, SANS))
    fy = y + 14 + len(rows) * rh + 40
    p.add(t(BX + BW - 30, fy, "*BYTES", 22, INK, MONO, "end", "bold"),
          t(BX + 30, fy, "No addresses are written. Saved to Downloads by Settings → Report → Save.", 12, MUTED, SANS))
    p.add(para(90, BY + H + 50, "BudsLink records every frame it writes and receives in a 600-entry ring, plus notes such as "
                                "channel opens and timeouts. The report turns that into plain text for owners of “beta” buds "
                                "to attach to a GitHub issue – the fastest way to confirm a protocol nobody here owns.", 170, 14, family=SANS))
    return p


def pipeline(n):
    p = Plate(n, "pipeline", "From source to a download", "11 · shipping", 1500, 940)
    steps = [("Sources/", "Swift files", INK), ("swift build", "-c release --arch arm64", COBALT),
             ("Earshot.app", "MacOS/ · Info.plist · Fonts · icon", OCHRE), ("codesign", "--sign - (ad-hoc)", VERM),
             ("ditto -c -k", "Earshot.zip", GREEN), ("gh release", "v1.1.0 + notes", INK)]
    for i, (name, sub, col) in enumerate(steps):
        x = 80 + i * 230
        p.add(rect(x + 8, 208, 200, 120, INK, "none", 0, 12), rect(x, 200, 200, 120, PAPER, col, 2.2, 12),
              t(x + 100, 252, name, 17, col, MONO, "middle", "bold"), t(x + 100, 280, sub, 11.5, MUTED, SANS, "middle"))
        if i:
            p.add(arrow(x - 26, 260, x - 4, 260, INK, 2))
    p.add(t(80, 160, "scripts/build.sh  –  run on the Mac", 14, INK, MONO, "start", "bold"))
    p.add(t(80, 420, "ON EVERY PUSH  –  .github/workflows/ci.yml", 14, INK, MONO, "start", "bold"))
    ci = [("git push", INK), ("GitHub Actions · macos-15", COBALT), ("swift test", GREEN), ("swift build -c release", OCHRE), ("✓ green", GREEN)]
    for i, (name, col) in enumerate(ci):
        x = 80 + i * 280
        p.add(rect(x, 450, 250, 64, PAPER_DEEP, col, 2, 32), t(x + 125, 488, name, 14, col, MONO, "middle", "bold"))
        if i:
            p.add(arrow(x - 26, 482, x - 4, 482, INK, 2))
    p.add(t(80, 580, "THE PIECES", 14, INK, MONO, "start", "bold"))
    pieces = ["Package.swift: three targets – EarshotCore (pure), Earshot (app), EarshotCoreTests",
              "scripts/test.sh: points SwiftPM at Testing.framework when only Command Line Tools are installed",
              "Info.plist: LSUIElement (menu-bar only, no Dock icon) · NSBluetoothAlwaysUsageDescription · version 1.1.0",
              "scripts/make-icon.swift draws the pixel icon; sips + iconutil turn it into AppIcon.icns",
              "Ad-hoc signed, so first launch needs right-click → Open (or System Settings → Privacy & Security)"]
    for i, r in enumerate(pieces):
        p.add(pixel(80, 600 + i * 34, 16, [INK, COBALT, OCHRE, GREEN, VERM][i], 2, 4), t(108, 613 + i * 34, r, 13.5, INK, SANS))
    return p


def back_cover(n):
    """The bud drawn in concentric copper traces on a navy board, like the trace cat."""
    p = Plate(n, "back-cover", "Thank you", "12 · credits", 1300, 1500)
    p.add(rect(26, 26, 1248, 1448, NAVY, "none", 0, 0))
    path_ = os.path.join(R, "assembled.png")
    box = crop_box(path_)
    ratio = (box[3] - box[1]) / (box[2] - box[0])
    cols = 120
    rows = round(cols * ratio)
    s = 6.2
    gx, gy = 650 - cols * s / 2, 150
    im = Image.open(path_).getchannel("A").crop(box).resize((cols, rows), Image.BOX).point(lambda v: 255 if v > 110 else 0)
    from PIL import ImageFilter
    for k, col in enumerate([GOLD, GOLD, GOLD_DIM, GOLD, GOLD_DIM, GOLD, GOLD_DIM]):
        level = im if k == 0 else im.filter(ImageFilter.MinFilter(1 + 4 * k))
        grid = [[level.getpixel((c, r)) > 0 for c in range(cols)] for r in range(rows)]
        p.add(pixel_fill(gx, gy, grid, s, [col], edge_only=True))
    inner = im.filter(ImageFilter.MinFilter(29))
    pts = [(c, r) for r in range(rows) for c in range(cols) if inner.getpixel((c, r))]
    for j, (c, r) in enumerate(pts[:: max(1, len(pts) // 5)][:5]):
        p.add(rect(gx + c * s - 22, gy + r * s - 16, 44, 32, "#0E1524", GOLD, 1.2, 3),
              *[rect(gx + c * s - 18 + q * 9, gy + r * s - 21, 4, 5, "#B9BDC4", "none", 0) for q in range(5)])
    by = gy + rows * s + 70
    title, w = pixel_text(0, 0, "THANK YOU", 9, GOLD)
    p.add(f'<g transform="translate({650 - w / 2:.0f},{by})">{title}</g>')
    credits = ["Gadgetbridge – the open Android app whose protocol work made the OPO, Sony, Nothing and soundcore drivers possible",
               "GalaxyBudsClient – Samsung's message layouts and captured status frames",
               "Aasheesh's OnePlus Buds write-up – proof that the OPO family could be spoken from a computer",
               "and the realme Buds Air 7 that patiently answered every question"]
    for i, r in enumerate(credits):
        p.add(t(650, by + 100 + i * 26, r, 13, "#E9E2D2", SANS, "middle"))
    return p


PLATES = [architecture, states, queue, optimistic, ui, journal, pipeline, back_cover]
