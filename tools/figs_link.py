"""Plates for chapters 04 (the Bluetooth stack), 05 (macOS) and 06 (method)."""

from plate import *


def stack(n):
    p = Plate(n, "stack", "The Bluetooth stack, bottom to top", "04 · the stack", 1300, 1000)
    layers = [
        ("Radio", "GFSK / DPSK on 79 channels at 2.4 GHz", INK, "controller"),
        ("Baseband", "hopping, slots, packets, ACL & SCO links, CRC, retries", INK, "controller"),
        ("LMP", "link manager: pairing, encryption keys, power modes", INK, "controller"),
        ("HCI", "the seam between the Bluetooth chip and the OS", VERM, "boundary"),
        ("L2CAP", "logical channels, multiplexing, segmentation", COBALT, "host"),
        ("SDP  ·  RFCOMM  ·  AVDTP", "service lookup · serial ports · audio streams", COBALT, "host"),
        ("A2DP · AVRCP · HFP · vendor", "music · remote control · calls · settings", GREEN, "profiles"),
    ]
    x, w, h = 330, 640, 92
    base = 860
    for i, (name, note, col, kind) in enumerate(layers):
        y = base - (i + 1) * (h + 10)
        p.add(rect(x + 12, y + 12, w, h, INK, "none", 0, 12),
              rect(x, y, w, h, PAPER, INK, 2, 12),
              rect(x, y, 16, h, col, "none", 0, 4),
              t(x + 40, y + 40, name, 22, INK, SANS, "start", "bold"),
              t(x + 40, y + 66, note, 13, MUTED, SANS))
    p.add(bracket(300, 300 - 0.001, 0, "", INK))
    p.add(path(f"M300,{base - 3 * (h + 10) + 6} L285,{base - 3 * (h + 10) + 6} L285,{base - 6} L300,{base - 6}", INK, 1.4),
          t(270, base - 1.5 * (h + 10), "IN THE CHIP", 12, INK, MONO, "end", "bold"),
          t(270, base - 1.5 * (h + 10) + 18, "(firmware in silicon)", 11, MUTED, SANS, "end"))
    top = base - 7 * (h + 10)
    p.add(path(f"M300,{top + 6} L285,{top + 6} L285,{base - 4 * (h + 10) - 6} L300,{base - 4 * (h + 10) - 6}", INK, 1.4),
          t(270, top + 1.6 * (h + 10), "IN THE OS", 12, INK, MONO, "end", "bold"),
          t(270, top + 1.6 * (h + 10) + 18, "macOS: IOBluetooth", 11, MUTED, SANS, "end"))
    ey = base - 6 * (h + 10) + 46
    p.add(arrow(1180, ey, 990, ey, VERM, 2), t(1190, ey - 8, "EARSHOT", 14, VERM, MONO, "start", "bold"),
          t(1190, ey + 12, "opens an RFCOMM", 12, INK, SANS), t(1190, ey + 28, "channel and speaks", 12, INK, SANS),
          t(1190, ey + 44, "the vendor protocol", 12, INK, SANS))
    p.add(para(330, 900, "Each layer only talks to the one below it and pretends the rest doesn't exist – the same idea "
                         "as envelopes inside envelopes.", 90, 14, family=SANS))
    return p


def _fcs(data):
    """RFCOMM's frame check: CRC-8 (poly 0x07, reflected), init 0xFF, complemented."""
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xE0 if crc & 1 else crc >> 1
    return 0xFF - crc


def encapsulation(n):
    p = Plate(n, "encapsulation", "Envelopes inside envelopes", "04 · the stack", 1500, 1060)
    msg = parse_hex("AA 07 00 00 06 01 00 00 00")
    addr, ctrl, ln = 0x7B, 0xEF, (len(msg) << 1) | 1
    rf = [addr, ctrl, ln] + msg + [_fcs([addr, ctrl])]
    l2 = [len(rf) & 0xFF, 0x00, 0x41, 0x00] + rf
    acl = [0x0B, 0x20, len(l2) & 0xFF, 0x00] + l2
    rows = [
        ("1 · OPO MESSAGE", "what Earshot writes", msg, [(0, 9, "battery request", VERM)]),
        ("2 · RFCOMM UIH FRAME", "a serial-port byte stream", rf,
         [(0, 1, "addr", COBALT, "DLCI·ch 15"), (1, 2, "UIH", COBALT), (2, 3, "len", COBALT, "9<<1|1"),
          (3, 12, "our 9 bytes", VERM), (12, 13, "FCS", COBALT, "CRC-8")]),
        ("3 · L2CAP BASIC FRAME", "a logical channel", l2,
         [(0, 2, "length", GREEN), (2, 4, "CID", GREEN, "channel"), (4, 17, "RFCOMM frame", COBALT)]),
        ("4 · HCI ACL PACKET", "macOS → the Bluetooth chip", acl,
         [(0, 2, "handle+flags", OCHRE), (2, 4, "length", OCHRE), (4, 21, "L2CAP frame", GREEN)]),
    ]
    y = 140
    for title, sub, data, fields in rows:
        p.add(t(70, y - 14, title, 13, INK, MONO, "start", "bold"), t(70 + len(title) * 8.4 + 16, y - 14, sub, 12, MUTED, SANS))
        svg, w = byte_strip(70, y, data, fields, 54, 9, True, 14)
        p.add(svg)
        y += 190
    # Over the air: proportional, in bits.
    p.add(t(70, y - 14, "5 · OVER THE AIR (baseband packet, bits)", 13, INK, MONO, "start", "bold"))
    segs = [("access code", 72, INK), ("header", 54, OCHRE), ("payload hdr", 16, OCHRE), ("ACL payload", 8 * 21, GREEN), ("CRC-16", 16, VERM)]
    total = sum(b for _, b, _ in segs)
    x = 70
    for name, bits, col in segs:
        w = bits / total * 1350
        p.add(rect(x, y, w - 4, 40, col, INK, 1.4, 5, 'fill-opacity="0.3"'),
              t(x + w / 2, y + 25, f"{name} · {bits}", 12, INK, SANS, "middle", "bold"))
        x += w
    p.add(t(70, y + 70, "…then whitened, sent as GFSK on one hop, and acknowledged by the other side in the next slot.", 13, MUTED, SANS),
          t(70, y + 96, "Handles, CIDs and the address byte vary per connection; these are representative values. Only row 1 is ours.", 12, MUTED, SANS))
    return p


def profiles(n):
    p = Plate(n, "profiles", "Why a Mac plays music but can't change settings", "04 · the stack", 1400, 920)

    def card(x, y, w, title, items, col, foot):
        h = 92 + len(items) * 56
        out = rect(x + 10, y + 10, w, h, INK, "none", 0, 12) + rect(x, y, w, h, PAPER, INK, 2, 12)
        out += rect(x, y, w, 46, col, "none", 0, 12) + rect(x, y + 30, w, 16, col, "none", 0, 0)
        out += t(x + 20, y + 30, title, 16, PAPER, SANS, "start", "bold")
        for i, (name, sub) in enumerate(items):
            out += t(x + 20, y + 84 + i * 56, name, 16, INK, SANS, "start", "bold") + t(x + 20, y + 104 + i * 56, sub, 12, MUTED, SANS)
        out += t(x + 20, y + h - 18, foot, 12, col, MONO, "start", "bold")
        return out

    p.add(card(80, 140, 560, "macOS KNOWS THESE PROFILES", [
        ("A2DP", "music, one way, compressed: SBC or AAC on a Mac"),
        ("AVRCP", "play / pause / skip and volume"),
        ("HFP", "calls: the mic, at low quality (mSBC / CVSD)"),
        ("SPP", "a plain serial port – exists, but nothing uses it here")], COBALT, "→ connects these automatically"))
    p.add(card(760, 140, 560, "macOS HAS NO IDEA ABOUT THIS ONE", [
        ("oppointeraction", "realme's control service, RFCOMM channel 15"),
        ("UUID 0000079A-D102-…", "a 128-bit name no Apple code recognises"),
        ("settings protocol", "battery, ANC, EQ, taps, find-my-buds"),
        ("nobody listening", "…until Earshot opens it")], VERM, "→ Earshot's whole reason to exist"))
    p.add(t(80, 560, "AUDIO CODECS – HOW MUSIC IS SQUEEZED FOR THE AIR", 13, INK, MONO, "start", "bold"))
    codecs = [("SBC", "mandatory · ≈ 345 kbit/s", INK, True), ("AAC", "Apple's choice · ≈ 256 kbit/s", INK, True),
              ("LDAC", "Sony · up to 990 kbit/s", FAINT, False), ("LHDC 5.0", "realme's Hi-Res · up to ≈ 1 Mbit/s", FAINT, False)]
    for i, (name, sub, col, mac) in enumerate(codecs):
        x = 80 + i * 310
        p.add(rect(x, 580, 290, 92, PAPER_DEEP, INK, 1.4, 10), t(x + 18, 614, name, 20, INK, SANS, "start", "bold"),
              t(x + 18, 638, sub, 12, MUTED, SANS), t(x + 18, 660, "on a Mac ✓" if mac else "not on a Mac", 12, GREEN if mac else VERM, MONO, "start", "bold"))
    p.add(para(80, 730, "When you pick the buds in the Bluetooth menu, macOS connects the profiles it understands – audio "
                        "and remote control – and stops there. The settings live behind a vendor service that no Mac "
                        "software asks for. Earshot's “Hi-Res audio” switch still works: it tells the buds to offer LHDC "
                        "to phones that support it. The Mac itself stays on AAC.", 170, 14, family=SANS))
    return p


def sdp(n):
    p = Plate(n, "sdp", "Reading the buds' service records", "05 · macOS", 1400, 960)
    x, y, w = 80, 140, 760
    p.add(rect(x + 10, y + 10, w, 520, INK, "none", 0, 10), rect(x, y, w, 520, PAPER, INK, 2, 10))
    p.add(line(x + 44, y, x + 44, y + 520, VERM, 1), t(x + 64, y + 40, "SDP SERVICE RECORD", 16, INK, MONO, "start", "bold"),
          t(x + w - 20, y + 40, "card 7 of 9", 11, MUTED, MONO, "end"))
    rows = [
        ("0x0000", "ServiceRecordHandle", "0x0001000B  (any number; per device)", INK),
        ("0x0001", "ServiceClassIDList", "UUID-128  0000079A-D102-11E1-9B23-00025B00A5A5", VERM),
        ("0x0004", "ProtocolDescriptorList", "L2CAP (0x0100)  →  RFCOMM (0x0003), channel 15", COBALT),
        ("0x0005", "BrowseGroupList", "public browse root (0x1002)", INK),
        ("0x0100", "ServiceName", "\"oppointeraction\"", GREEN),
    ]
    for i, (attr, name, val, col) in enumerate(rows):
        yy = y + 100 + i * 82
        p.add(line(x + 44, yy + 30, x + w, yy + 30, FAINT, 0.8), t(x + 64, yy, attr, 13, MUTED, MONO),
              t(x + 150, yy, name, 15, INK, SANS, "start", "bold"), t(x + 150, yy + 22, val, 13, col, MONO, "start", "bold"))
    p.add(t(900, 160, "WHAT EARSHOT DOES", 13, INK, MONO, "start", "bold"))
    code = ["for record in device.services {",
            "  let classes = record",
            "    .getAttributeDataElement(0x0001)",
            "  if classes contain the brand's UUID {",
            "    record.getRFCOMMChannelID(&id)",
            "    return id          // 15",
            "  }",
            "}",
            "// not cached yet? performSDPQuery,",
            "// then fall back to 15 for realme"]
    p.add(rect(900, 180, 440, 290, INK, "none", 0, 10))
    p.add(lines(920, 214, code, 13, 1.75, fill=PAPER))
    p.add(t(900, 520, "SHORT UUIDS GROW TO 128 BITS", 13, INK, MONO, "start", "bold"),
          t(900, 548, "0x1101  (Serial Port)", 13, INK, MONO),
          t(900, 570, "→ 00001101-0000-1000-8000-00805F9B34FB", 12, COBALT, MONO),
          t(900, 596, "Earshot compares all of them at 16 bytes.", 12, MUTED, SANS))
    p.add(para(80, 720, "SDP – the Service Discovery Protocol – is the buds' table of contents. Each record says what a "
                        "service is (a UUID) and how to reach it (protocol stack and channel number). macOS caches these "
                        "records when you pair, and IOBluetooth hands them to any app. The realme Buds Air 7 advertise "
                        "their control service on RFCOMM channel 15 under the name “oppointeraction”; Samsung, Sony, "
                        "Nothing and soundcore each use their own UUID, listed in Earshot's Profiles.swift.", 170, 14, family=SANS))
    return p


def open_retry(n):
    p = Plate(n, "open-retry", "Opening the door, politely and persistently", "05 · macOS", 1500, 900)
    x0, x1, y = 90, 1410, 360
    scale = (x1 - x0) / 12.0
    X = lambda s: x0 + s * scale
    p.add(line(x0, y, x1, y, INK, 2))
    for s in range(0, 13):
        p.add(line(X(s), y, X(s), y + (12 if s % 2 == 0 else 6), INK, 1))
        if s % 2 == 0:
            p.add(t(X(s), y + 30, f"{s} s", 11, MUTED, MONO, "middle"))
    events = [(0, "connect", "audio connected", INK)]
    tcur = 1.0
    events.append((tcur, "open #0", "refused", VERM))
    for k, d in enumerate([0.4, 0.8, 1.5, 3.0]):
        tcur += d
        events.append((tcur, f"open #{k + 1}" if k < 3 else "reset link", "refused" if k < 3 else "close + reconnect", VERM if k < 3 else OCHRE))
    tcur += 2
    events.append((tcur, "reconnect", "connect note", INK))
    tcur += 1
    events.append((tcur, "open", "channel 15 ✓", GREEN))
    for i, (ts, name, note, col) in enumerate(events):
        up = i % 2 == 0
        yy = y - 70 if up else y + 70
        p.add(pixel(X(ts) - 10, y - 10, 20, col, 0, 4), line(X(ts), y + (-10 if up else 10), X(ts), yy + (8 if up else -22), col, 1),
              t(X(ts), yy - (0 if up else -10), name, 13, INK, SANS, "middle", "bold"), t(X(ts), yy + (16 if up else 26), note, 11, col, MONO, "middle"))
    for a, b, lab in ((1.0, 1.4, "0.4"), (1.4, 2.2, "0.8"), (2.2, 3.7, "1.5"), (3.7, 6.7, "3")):
        p.add(path(f"M{X(a):.1f},{y - 24} Q{(X(a) + X(b)) / 2:.1f},{y - 60} {X(b):.1f},{y - 24}", MUTED, 1, dash="3 3"),
              t((X(a) + X(b)) / 2, y - 48, lab, 10, MUTED, MONO, "middle"))
    p.add(t(x0, 140, "BACKOFF  0.4 · 0.8 · 1.5 · 3 · 5 · 8 · 15 s  →  then every 30 s", 15, INK, MONO, "start", "bold"),
          t(x0, 166, "after 4 failed opens: close the Bluetooth link and reconnect, which clears a half-open channel", 13, OCHRE, SANS),
          t(x0, 188, "every open has a 6 s watchdog – if macOS never answers, start over rather than hang in “linking”", 13, MUTED, SANS))
    p.add(para(x0, 560, "Right after the buds connect for audio, they often refuse the first request for the control "
                        "channel – they are still busy setting up. A copy of Earshot that was force-quit can also leave "
                        "the channel half-open, and the buds then turn every newcomer away. BudsLink handles both: it "
                        "waits a second after the connect notification, retries with growing gaps, resets the link if "
                        "that clearly isn't working, and closes the channel cleanly on quit (even on SIGTERM). In "
                        "testing, kill-and-reopen cycles linked in about 0.15 s.", 190, 14, family=SANS))
    p.add(t(x0, 760, "macOS also asks once: “Earshot would like to use Bluetooth” – the NSBluetoothAlwaysUsageDescription", 13, INK, SANS),
          t(x0, 782, "string in Info.plist is what that dialog shows. Without a yes, IOBluetooth returns nothing at all.", 13, INK, SANS))
    return p


def watcher(n):
    p = Plate(n, "watcher", "The watcher: learning by watching", "06 · method", 1500, 980)
    x0, x1 = 300, 1420
    lanes = [("PHONE · realme Link", 190), ("BUDS · what changed", 400), ("CONCLUSION", 540)]
    for name, y in lanes:
        p.add(t(70, y + 5, name, 13, INK, MONO, "start", "bold"), line(x0 - 20, y, x1, y, FAINT, 1, "2 4"))
    steps = [
        ("enhancer off", "0110 → 00", "volume boost = cmd 0x0110 (not switch 0x09)", COBALT),
        ("enhancer on", "0110 → 01", "", COBALT),
        ("spatial on", "misc 1B → 01", "spatial audio = misc 0x1B (+ 0x041E type)", GREEN),
        ("spatial off", "misc 1B → 00", "", GREEN),
        ("Serenade", "EQ → 02", "EQ ids:", VERM),
        ("Original", "EQ → 00", "00 Original · 01 Deep bass", VERM),
        ("Clear bass", "EQ → 03", "02 Serenade · 03 Clear bass", VERM),
        ("Deep bass", "EQ → 01", "", VERM),
    ]
    k = len(steps)
    for i, (tap, seen, concl, col) in enumerate(steps):
        x = x0 + (i + 0.5) * (x1 - x0) / k
        p.add(pixel(x - 14, 176, 28, INK, 0, 5), t(x, 236, tap, 13, INK, SANS, "middle", "bold"),
              arrow(x, 250, x, 380, col, 1.6), pixel(x - 14, 386, 28, col, 0, 5), t(x, 446, seen, 13, col, MONO, "middle", "bold"))
    step = (x1 - x0) / k
    for a, b, text, col in ((0, 2, "volume enhancer = command 0x0110 (switch 0x09 is vocal boost)", COBALT),
                            (2, 4, "spatial audio = misc switch 0x1B, plus type 0x041E", GREEN),
                            (4, 8, "EQ ids: 00 Original · 01 Deep bass · 02 Serenade · 03 Clear bass", VERM)):
        xa, xb = x0 + a * step + 10, x0 + b * step - 10
        p.add(bracket(xa, xb, 520, "", col))
        for j, row in enumerate(wrap(text, int((xb - xa) / 7.4))):
            p.add(t((xa + xb) / 2, 560 + j * 18, row, 12.5, INK, SANS, "middle", "bold" if j == 0 else "normal"))
    p.add(t(x0 - 20, 150, "≈ 10 s apart · watcher only READS: it polls every setting and prints what moved", 12, MUTED, MONO))
    p.add(para(70, 730, "realme Link has settings nobody had documented. Guessing could flip the wrong one, so we watched "
                        "instead. With dual-device (multipoint) on, the phone and the Mac were connected at once. A small "
                        "read-only program on the Mac asked the buds for every setting over and over while the user "
                        "changed one thing at a time on the phone and noted the order. Every change on the phone showed "
                        "up as exactly one changed value on the Mac – a perfect key. Starting state: enhancer on, spatial "
                        "off, EQ Deep bass.", 190, 14, family=SANS))
    return p


def touch_bug(n):
    p = Plate(n, "touch-bug", "Change, read back, revert: catching a bug", "06 · method", 1400, 1000)
    p.add(t(80, 140, "SET “LEFT DOUBLE TAP → NEXT”  (command 0x0401)", 14, INK, MONO, "start", "bold"))
    s1, w = byte_strip(80, 190, [0x01, 0x01, 0x02, 0x01, 0x06],
                       [(0, 1, "count", INK), (1, 2, "left", COBALT), (2, 4, "gesture ⇄ swapped", VERM), (4, 5, "next", GREEN)], 66, 10, True, 18)
    p.add(t(80, 178, "FIRST GUESS", 12, VERM, MONO, "start", "bold"), s1)
    p.add(t(500, 230, "→ buds read gesture 01 = single tap: the wrong gesture changes", 13, VERM, SANS))
    s2, w = byte_strip(80, 400, [0x01, 0x01, 0x01, 0x02, 0x06],
                       [(0, 1, "count", INK), (1, 2, "left", COBALT), (2, 4, "01 · double (02)", GREEN), (4, 5, "next", GREEN)], 66, 10, True, 18)
    p.add(t(80, 388, "WHAT THE BUDS USE  (gesture is the u16 0x0201, little-endian)", 12, GREEN, MONO, "start", "bold"), s2)
    # The loop.
    cx, cy, r = 1110, 400, 140
    steps = [("change", "send a set command", -90), ("read back", "ask for all bindings", 0), ("compare", "only that entry moved?", 90), ("revert", "put it back as it was", 180)]
    p.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{INK}" stroke-width="1.4" stroke-dasharray="4 5"/>')
    for name, sub, a in steps:
        import math
        x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
        p.add(circle(x, y, 34, PAPER, INK, 1.8), t(x, y + 5, name, 12, INK, SANS, "middle", "bold"),
              t(x, y + (52 if a >= 0 and a != 180 else -44) if a != 0 else y + 52, sub, 11, MUTED, SANS, "middle"))
    p.add(para(80, 640, "The tap layout came from Gadgetbridge's code, but the byte order was easy to misread. Instead of "
                        "trusting it, every write was tested on the real buds with the same loop: change one thing, read "
                        "the whole table back, check that exactly that entry moved, then revert. The loop caught that the "
                        "first encoder would have set the wrong gesture for double, triple and hold. With the fix, "
                        "“left triple tap: Next → Previous” came back as 03 05 in the reply, nothing else moved, and the "
                        "revert restored 03 06. Earshot keeps doing a light version forever: after any tap change it "
                        "reads the bindings back, so the screen always shows what the buds really hold.", 170, 14, family=SANS))
    return p


PLATES = [stack, encapsulation, profiles, sdp, open_retry, watcher, touch_bug]
