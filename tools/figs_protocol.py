"""Plates for chapters 07 (OPO byte by byte), 08 (integrity) and 09 (other brands)."""

from plate import *


# Checksums exactly as Earshot computes them (EarshotCore/Checksums.swift).
def crc16_xmodem(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def crc16_modbus(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def le16(v):
    return [v & 0xFF, v >> 8]


def samsung(id_, payload=()):
    body = [id_] + list(payload)
    return [0xFD] + le16(len(body) + 2) + body + le16(crc16_xmodem(body)) + [0xDD]


def sony(kind, seq, payload):
    n = len(payload)
    body = [kind, seq, (n >> 24) & 0xFF, (n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF] + list(payload)
    body.append(sum(body) & 0xFF)
    esc = []
    for b in body:
        esc += [0x3D, b & 0xEF] if b in (0x3C, 0x3D, 0x3E) else [b]
    return [0x3E] + esc + [0x3C], body


def nothing(control, command, payload=(), fsn=0):
    out = [0x55] + le16(control) + le16(command) + le16(len(payload)) + [fsn] + list(payload)
    return out + le16(crc16_modbus(out))


def soundcore(command, payload=()):
    out = [0xEE, 0x08, 0x00, 0x00, 0x00] + le16(command) + le16(10 + len(payload)) + list(payload)
    return out + [sum(out) & 0xFF]


# ------------------------------------------------------------------ 07 · OPO

OPO_COMMANDS = [
    ("0105", "firmware", "8105"), ("0106", "battery", "8106"), ("0108", "touch bindings", "8108"),
    ("0109", "in ear / in case", "8109"), ("010C", "noise mode / hold cycle", "810C"), ("010D", "misc switches", "810D"),
    ("010F", "EQ preset", "810F"), ("0110", "volume enhancer", "8110"), ("0205", "subscribe to pushes", "—"),
    ("0400", "find (ring)", "8400"), ("0401", "set touch", "8401"), ("0403", "set misc switch", "8403"),
    ("0404", "set noise mode", "8404"), ("0406", "set EQ", "8406"), ("0407", "set enhancer", "8407"),
    ("041E", "set spatial type", "841E"), ("0204", "PUSH: something changed", "(unsolicited)"), ("0504", "PUSH: EQ changed", "(unsolicited)"),
]


def opo_frame(n):
    p = Plate(n, "opo-frame", "The OPO frame, field by field", "07 · OPO byte by byte", 1500, 1080)
    data = parse_hex("AA 0A 00 00 04 04 05 03 00 01 01 02")
    fields = [(0, 1, "preamble", INK, "always AA"), (1, 2, "length", VERM, "LEB128 · 10"),
              (2, 4, "reserved", FAINT, "00 00"), (4, 6, "command", COBALT, "0x0404 LE"),
              (6, 7, "seq", GREEN, "counter"), (7, 9, "payload len", OCHRE, "3, LE"),
              (9, 12, "payload", VERM, "01 01 02")]
    p.add(t(80, 140, "“SWITCH TO TRANSPARENCY”  –  the message Earshot sends when you tap Ambient", 15, INK, MONO, "start", "bold"))
    svg, w = byte_strip(80, 180, data, fields, 82, 12, True, 22)
    p.add(svg)
    p.add(dim(80 + 2 * 94, 80 + 12 * 94 - 12, 168, "length counts these 10 bytes"))
    p.add(t(80, 380, "PAYLOAD  01 · 01 · 02", 13, INK, MONO, "start", "bold"),
          t(80, 404, "01 = “current mode” (02 would be the hold-cycle mask) · 01 = fixed · 02 = transparency", 13, INK, SANS),
          t(80, 426, "modes: 01 off · 02 transparency · ANC strengths 04 mild · 10 moderate · 08 deep · 20 adaptive", 13, MUTED, SANS))
    p.add(t(80, 486, "THE COMMAND TABLE  (a reply sets bit 15: 0x0106 → 0x8106)", 13, INK, MONO, "start", "bold"))
    for i, (req, name, rep) in enumerate(OPO_COMMANDS):
        col, row = divmod(i, 9)
        x, y = 80 + col * 690, 520 + row * 36
        push = rep.startswith("(")
        p.add(rect(x, y, 70, 26, VERM if push else (COBALT if req.startswith("04") else INK), "none", 0, 5, 'fill-opacity="0.9"'),
              t(x + 35, y + 18, req, 13, PAPER, MONO, "middle", "bold"), t(x + 86, y + 18, name, 13, INK, SANS),
              t(x + 420, y + 18, rep, 12, MUTED, MONO))
    p.add(t(80, 880, "No checksum: RFCOMM already guarantees the bytes arrive intact. seq just counts up; replies echo it.", 13, INK, SANS),
          t(80, 904, "Black: read · blue: write · red: the buds speak first. Codes match Gadgetbridge and were verified on the Buds Air 7.", 13, MUTED, SANS))
    return p


def opo_battery(n):
    p = Plate(n, "opo-battery", "A battery question and its answer", "07 · OPO byte by byte", 1500, 1080)
    q = parse_hex("AA 07 00 00 06 01 00 00 00")
    a = parse_hex("AA 0D 00 00 06 81 00 06 00 00 02 01 0A 03 00")
    p.add(t(80, 140, "MAC → BUDS", 13, COBALT, MONO, "start", "bold"))
    s, w = byte_strip(80, 160, q, [(0, 1, "AA", INK), (1, 2, "len 7", VERM), (2, 4, "00 00", FAINT),
                                  (4, 6, "0x0106 battery", COBALT), (6, 7, "seq 0", GREEN), (7, 9, "no payload", OCHRE)], 66, 10, True, 18)
    p.add(s)
    p.add(t(80, 380, "BUDS → MAC", 13, VERM, MONO, "start", "bold"))
    s, w = byte_strip(80, 400, a, [(0, 1, "AA", INK), (1, 2, "len 13", VERM), (2, 4, "00 00", FAINT),
                                  (4, 6, "0x8106 reply", COBALT), (6, 7, "seq", GREEN), (7, 9, "6 bytes", OCHRE),
                                  (9, 10, "ok", GREEN, "status 00"), (10, 11, "count", INK, "2 entries"),
                                  (11, 13, "left 10 %", VERM, "01 · 0A"), (13, 15, "case 0", FAINT, "03 · 00 → skip")], 66, 10, True, 18)
    p.add(s)
    p.add(t(80, 640, "READ AS:  status ok · two readings · slot 01 (left) = 0x0A = 10 % · slot 03 (case) = 0 → “can't read, lid shut”", 14, INK, SANS, "start", "bold"),
          t(80, 666, "The right bud is missing entirely: it was flat. A missing slot means asleep or empty, so Earshot drops its stale value.", 13, MUTED, SANS))
    p.add(t(80, 730, "ANOTHER DAY, CHARGING:", 13, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 750, parse_hex("00 03 01 D5 02 40 03 37"),
                      [(0, 1, "ok", GREEN), (1, 2, "3", INK), (2, 4, "left D5", VERM, "1·1010101 → 85 %, charging"),
                       (4, 6, "right 40", COBALT, "64 %"), (6, 8, "case 37", OCHRE, "55 %")], 66, 10, True, 18)
    p.add(s)
    p.add(t(80, 960, "These are real bytes from a realme Buds Air 7, kept as test vectors in Earshot's ProtocolTests.swift.", 13, MUTED, SANS))
    return p


def opo_sequence(n):
    p = Plate(n, "opo-sequence", "A conversation, in order", "07 · OPO byte by byte", 1400, 1240)
    L, R = 300, 1100
    p.add(rect(L - 90, 110, 180, 50, INK, "none", 0, 8), t(L, 142, "Earshot (Mac)", 15, PAPER, SANS, "middle", "bold"),
          rect(R - 90, 110, 180, 50, VERM, "none", 0, 8), t(R, 142, "Buds", 15, PAPER, SANS, "middle", "bold"),
          line(L, 160, L, 1120, INK, 1.2, "4 5"), line(R, 160, R, 1120, INK, 1.2, "4 5"))
    msgs = [
        ("→", "0205 subscribe 01 02 03 05 06", "no reply: wait 0.15 s", COBALT),
        ("→", "0106 battery?", "", INK), ("←", "8106 00 02 01 0A 03 00", "left 10 %", VERM),
        ("→", "0109 where are you?", "", INK), ("←", "8109 … 01 03 02 00", "left in ear, right in case", VERM),
        ("→", "010C 01 01  mode?", "", INK), ("←", "810C 00 01 01 08", "ANC, deep", VERM),
        ("→", "… firmware, taps, EQ, switches …", "one at a time", INK),
        ("·", "user taps Ambient", "", INK),
        ("→", "0404 01 01 02  set transparency", "", COBALT), ("←", "8404 00", "status 00: applied", GREEN),
        ("←", "0204 01 …  PUSH battery", "the buds speak first", VERM),
        ("·", "both buds back in the case", "", INK),
        ("→", "0404 01 01 08  set ANC", "", COBALT), ("←", "8404 0E", "refused: not worn → roll back", VERM),
    ]
    y = 200
    for d, text, note, col in msgs:
        if d == "·":
            p.add(rect(L + 120, y - 18, R - L - 240, 30, PAPER_DEEP, INK, 1, 14), t((L + R) / 2, y + 2, text, 13, INK, SANS, "middle", "bold"))
        else:
            a, b = (L, R) if d == "→" else (R, L)
            p.add(arrow(a, y, b, y, col, 1.8), t((L + R) / 2, y - 8, text, 13, col, MONO, "middle", "bold"))
            if note:
                p.add(t(R + 24 if d == "←" else L - 24, y + 4, note, 12, MUTED, SANS, "start" if d == "←" else "end"))
        y += 60
    p.add(t(80, 1170, "Earshot never has two questions in flight: buds drop commands sent back to back. Each one waits for its reply (or 2.5 s).", 13, INK, SANS))
    return p


def opo_payloads(n):
    p = Plate(n, "opo-payloads", "Payload shapes", "07 · OPO byte by byte", 1500, 1200)
    y = 140

    def block(title, note, data, fields, cell=50):
        nonlocal y
        p.add(t(80, y, title, 14, INK, MONO, "start", "bold"), t(80, y + 20, note, 12, MUTED, SANS))
        s, w = byte_strip(80, y + 40, data, fields, cell, 7, True, 15)
        p.add(s)
        y += 210

    block("NOISE MODE  (reply to 010C)", "[status, type, 01, value] — type 01 current mode, 02 hold-cycle mask",
          parse_hex("00 01 01 08"), [(0, 1, "ok", GREEN), (1, 2, "current", INK), (2, 3, "01", FAINT), (3, 4, "08 deep ANC", VERM)], 64)
    block("SWITCHES  (reply to 010D)", "[status, count, (id, value)…] — 09 vocal · 1B spatial · 1D dynamic bass · 1A wind",
          parse_hex("00 04 09 00 1B 00 1D 01 1A 01"),
          [(0, 1, "ok", GREEN), (1, 2, "4", INK), (2, 4, "09 off", FAINT), (4, 6, "1B spatial off", COBALT),
           (6, 8, "1D bass on", VERM), (8, 10, "1A wind on", VERM)], 58)
    block("TOUCH BINDINGS  (reply to 0108), first three of ten", "[status, count, (side, 01, gesture, action)…] — side 01 L, 02 R",
          parse_hex("00 0A 02 01 01 00 02 01 02 01 02 01 03 06"),
          [(0, 1, "ok", GREEN), (1, 2, "10", INK), (2, 6, "R single: off", FAINT), (6, 10, "R double: play/pause", COBALT),
           (10, 14, "R triple: next", VERM)], 50)
    fw = "1,1,111,1,2,1.1.0.62"
    data = [0x00, 0x06] + list(fw.encode())
    block("FIRMWARE  (reply to 0105), the start of it", "[status, count, ASCII “side,kind,value,…”] — kind 2 is the version",
          data, [(0, 2, "ok · 6", GREEN), (2, 2 + len("1,1,111,"), "left: kind 1 = 111", FAINT),
                 (2 + len("1,1,111,"), len(data), "1,2,1.1.0.62 → left firmware", VERM)], 40)
    p.add(t(80, y + 10, "ASCII: 31 = '1'  2C = ','  2E = '.'  — firmware is the one place the buds send text.", 13, INK, SANS))
    return p


# ------------------------------------------------------------------ 08 · integrity

def framing(n):
    p = Plate(n, "framing", "Where does a message end?", "08 · integrity", 1500, 1060)
    p.add(t(80, 140, "A · SAY THE LENGTH FIRST  (OPO, Samsung, Nothing, soundcore)", 14, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 170, parse_hex("AA 08 00 00 06 04 43 01 00 02"),
                      [(0, 1, "start", INK), (1, 2, "8 more", VERM), (2, 10, "exactly 8 bytes", COBALT)], 60, 8, False, 17)
    p.add(s, t(80 + w + 30, 205, "read the count, then read that many", 13, INK, SANS))
    p.add(t(80, 330, "B · MARK BOTH ENDS  (Sony: 3E … 3C)", 14, INK, MONO, "start", "bold"))
    frame, body = sony(0x0C, 0, [0x00, 0x00])
    s, w = byte_strip(80, 360, frame, [(0, 1, "start 3E", VERM), (1, len(frame) - 1, "body", COBALT), (len(frame) - 1, len(frame), "end 3C", VERM)], 60, 8, False, 17)
    p.add(s)
    p.add(t(80, 520, "…BUT WHAT IF THE BODY CONTAINS 3C?  ESCAPE IT (byte stuffing)", 14, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 550, [0x12, 0x3C, 0x34], [(1, 2, "would end the frame!", VERM)], 60, 8, False, 17)
    p.add(s, arrow(80 + w + 20, 580, 80 + w + 120, 580, INK, 2))
    s2, w2 = byte_strip(80 + w + 140, 550, [0x12, 0x3D, 0x2C, 0x34], [(1, 3, "3D + (3C with bit 4 cleared)", GREEN)], 60, 8, False, 17)
    p.add(s2)
    p.add(t(80, 700, "C · AND WHEN BYTES GO MISSING?", 14, INK, MONO, "start", "bold"),
          t(80, 726, "Length-first: a wrong length swallows the next message. Every decoder therefore checks what it can (end byte,", 13, INK, SANS),
          t(80, 748, "checksum, sane length ≤ 4096) and, if anything is off, drops ONE byte and hunts for the next start byte.", 13, INK, SANS))
    p.add(para(80, 820, "A Bluetooth serial channel is a stream, like water in a pipe: it delivers bytes in order but has no "
                        "idea where one message stops and the next begins. Two writes can arrive as one chunk; one write "
                        "can arrive in two. Every protocol in this manual solves that with one of these two tricks.", 190, 14, family=SANS))
    return p


def crc_plate(n):
    p = Plate(n, "crc", "Checksums, from adding to dividing", "08 · integrity", 1500, 1400)
    # 1. Sum.
    sc = soundcore(0x0101)
    p.add(t(80, 140, "1 · SUM  (Sony, soundcore): add every byte, keep the low 8 bits", 14, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 165, sc, [(0, len(sc) - 1, " + ".join(f"{b:02X}" for b in sc[:-1]) + f" = 0x{sum(sc[:-1]):X}", COBALT),
                                   (len(sc) - 1, len(sc), "low byte", VERM)], 52, 7, False, 15)
    p.add(s, t(80, 280, "Cheap, catches most single-byte errors, blind to swapped bytes.", 13, MUTED, SANS))
    # 2. Polynomial division, small enough to read.
    msg, gen, k = "10100000", "1011", 3
    work = list(msg + "0" * k)
    steps = []
    for i in range(len(msg)):
        if work[i] == "1":
            steps.append((i, "".join(work[i:i + len(gen)])))
            for j in range(len(gen)):
                work[i + j] = "0" if work[i + j] == gen[j] else "1"
            steps.append((i, "".join(work)))
    rem = "".join(work[-k:])
    p.add(t(80, 340, "2 · CRC = THE REMAINDER OF A DIVISION  (no carries: subtract is XOR)", 14, INK, MONO, "start", "bold"),
          t(80, 364, f"message 0xA0 = {msg}, divided by 1011 (x³ + x + 1), with three 0s appended", 13, INK, SANS))
    cw = 22
    gx, gy = 120, 410
    p.add(t(gx, gy, " ".join(msg + "0" * k), 18, INK, MONO, "start", "bold"))
    yy = gy
    for idx in range(0, len(steps), 2):
        i, before = steps[idx]
        _, after = steps[idx + 1]
        yy += 30
        p.add(t(gx + i * cw, yy, " ".join(gen), 18, VERM, MONO, "start", "bold"), t(gx - 30, yy, "⊕", 16, VERM, MONO))
        p.add(line(gx + i * cw - 4, yy + 8, gx + (i + len(gen)) * cw - 8, yy + 8, INK, 1))
        yy += 26
        nxt = after.find("1")
        start = i if nxt < 0 else min(i, nxt)
        p.add(t(gx + i * cw, yy, " ".join(after[i:]), 18, MUTED, MONO))
    p.add(t(gx, yy + 40, "remainder " + " ".join(rem) + f"  →  CRC-3 = {rem}", 18, GREEN, MONO, "start", "bold"))
    p.add(t(820, 410, "WHY IT WORKS", 13, INK, MONO, "start", "bold"),
          *[t(820, 436 + i * 20, r, 13, INK, SANS) for i, r in enumerate(wrap(
              "Treat the bits as a long binary number and divide by a fixed pattern. The sender appends the "
              "remainder; the receiver divides message+remainder and must get zero. Flip any bit, any burst "
              "shorter than the CRC, or swap bytes, and the remainder changes. Real CRCs use 16-bit patterns "
              "and run a byte at a time with shifts – exactly the eight-step loop in Checksums.swift.", 70))])
    # 3. The two CRC-16s Earshot uses.
    sam = samsung(0xA0)
    no = nothing(0x5120, 0xC007)
    p.add(t(80, 960, "3 · CRC-16/XMODEM  (Samsung: poly 0x1021, start 0)  — “find my buds, start”", 14, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 985, sam, [(3, 4, "id A0", COBALT), (4, 6, f"CRC {crc16_xmodem([0xA0]):04X}, LE", VERM)], 56, 8, False, 16)
    p.add(s)
    p.add(t(80, 1120, "4 · CRC-16/MODBUS  (Nothing: reflected poly 0xA001, start 0xFFFF)  — “battery?”", 14, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 1145, no, [(0, 9, "header: 55 · control 5120 · command C007 · len 0 · fsn 0", COBALT),
                                   (9, 11, f"CRC {crc16_modbus(no[:9]):04X}, LE", VERM)], 56, 8, False, 16)
    p.add(s)
    p.add(t(80, 1280, "OPO has none: RFCOMM's own checks already protect the bytes; brands add their own anyway for older links.", 13, MUTED, SANS))
    return p


def reassembly(n):
    p = Plate(n, "reassembly", "Rebuilding messages from a stream", "08 · integrity", 1500, 1000)
    whole = parse_hex("AA 0B 00 00 0C 81 02 04 00 00 01 01 08")
    chunks = [[0x13, 0x37] + whole[:5], whole[5:]]
    p.add(t(80, 140, "CHUNK 1 ARRIVES  (noise + the first 5 bytes of a reply)", 13, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 160, chunks[0], [(0, 2, "garbage", FAINT, "no AA: drop"), (2, 7, "AA 0B … – need 11 more", COBALT)], 56, 8, False, 16)
    p.add(s)
    p.add(t(80, 330, "BUFFER AFTER CHUNK 1", 13, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 350, whole[:5], [(0, 5, "waiting…", OCHRE, "length says 11 follow; have 3")], 56, 8, False, 16)
    p.add(s)
    p.add(t(80, 520, "CHUNK 2 ARRIVES", 13, INK, MONO, "start", "bold"))
    s, w = byte_strip(80, 540, chunks[1], [(0, len(chunks[1]), "the rest", COBALT)], 56, 8, False, 16)
    p.add(s)
    p.add(t(80, 710, "OUT COMES ONE PACKET", 13, GREEN, MONO, "start", "bold"))
    s, w = byte_strip(80, 730, whole, [(4, 6, "cmd 810C", COBALT), (6, 7, "seq 2", GREEN), (9, 13, "00 01 01 08 = ANC deep", VERM)], 56, 8, False, 16)
    p.add(s)
    p.add(para(80, 880, "This is Earshot's test reassemblesSplitFramesAndSkipsGarbage, drawn. Each brand's FrameDecoder keeps a "
                        "buffer, appends whatever arrives, and loops: skip to a start byte, check the length is there, cut "
                        "out a frame, repeat. Incomplete? Wait for more. Nonsense? Drop a byte and resync.", 190, 14, family=SANS))
    return p


# ------------------------------------------------------------------ 09 · brands

def brand_frames(n):
    p = Plate(n, "brand-frames", "Five dialects of the same idea", "09 · other brands", 1500, 1260)
    rows = [
        ("realme · OPPO · OnePlus  (OPO)", "battery?", parse_hex("AA 07 00 00 06 01 00 00 00"),
         [(0, 1, "AA", INK), (1, 2, "len", VERM), (2, 4, "00 00", FAINT), (4, 6, "cmd LE", COBALT), (6, 7, "seq", GREEN), (7, 9, "plen", OCHRE)]),
        ("Samsung Galaxy Buds", "find, start", samsung(0xA0),
         [(0, 1, "FD", INK), (1, 3, "size LE", VERM), (3, 4, "id", COBALT), (4, 6, "CRC-16 XMODEM", OCHRE), (6, 7, "DD", INK)]),
        ("Sony  (WH-, WF-, LinkBuds)", "hello (init)", sony(0x0C, 0, [0x00, 0x00])[0],
         [(0, 1, "3E", INK), (1, 2, "type", COBALT), (2, 3, "seq", GREEN), (3, 7, "length u32 BE", VERM), (7, 9, "payload", COBALT), (9, 10, "sum", OCHRE), (10, 11, "3C", INK)]),
        ("Nothing · CMF", "battery?", nothing(0x5120, 0xC007),
         [(0, 1, "55", INK), (1, 3, "control LE", GREEN), (3, 5, "command LE", COBALT), (5, 7, "len LE", VERM), (7, 8, "fsn", GREEN), (8, 10, "CRC MODBUS", OCHRE)]),
        ("Anker soundcore", "device info?", soundcore(0x0101),
         [(0, 5, "EE 08 00 00 00", INK), (5, 7, "cmd LE", COBALT), (7, 9, "total len", VERM), (9, 10, "sum", OCHRE)]),
    ]
    y = 140
    for name, what, data, fields in rows:
        p.add(t(80, y, name, 15, INK, SANS, "start", "bold"), t(80 + len(name) * 8.6 + 20, y, f"— “{what}”", 13, MUTED, SANS))
        s, w = byte_strip(80, y + 20, data, fields, 58, 8, True, 16)
        p.add(s)
        y += 215
    p.add(t(80, 1200, "Every byte above is generated with the same arithmetic as Earshot's drivers (see tools/figs_protocol.py).", 13, MUTED, SANS))
    return p


BRANDS = [
    ("realme · OPPO · OnePlus", "AA", "LEB128", "none", "seq; status in reply", "0000079A-…", [1, 1, 1, 1, 1, 1], True),
    ("Samsung Galaxy Buds", "FD … DD", "u16 (10 bits)", "CRC-16 XMODEM", "none; status pushes", "2E73A4AD-…", [1, 1, 0, 1, 1, 1], False),
    ("Sony", "3E … 3C", "u32 BE", "sum", "ACK every frame", "956C7B26-… / 96CC203E-…", [1, 1, 1, 1, 0, 0], False),
    ("Nothing · CMF", "55", "u16", "CRC-16 MODBUS", "fsn numbering", "AEAC4A03-…", [1, 1, 1, 1, 1, 1], False),
    ("Anker soundcore", "EE / FF", "u16 (whole frame)", "sum", "reply = same cmd", "0CF12D31-… + model", [1, 1, 1, 0, 0, 1], False),
]


def brands(n):
    p = Plate(n, "brands", "Seven brands at a glance", "09 · other brands", 1500, 900)
    cols = [("brand", 80), ("start", 330), ("length", 430), ("check", 570), ("ordering", 730), ("service UUID", 920)]
    feats = ["battery", "noise", "strength", "EQ", "taps", "find"]
    p.add(*[t(x, 150, c.upper(), 11, MUTED, MONO, "start", "bold") for c, x in cols])
    for j, f in enumerate(feats):
        p.add(t(1150 + j * 50, 150, f, 9.5, MUTED, MONO, "middle", "bold", 'transform="rotate(-35 %d 150)"' % (1150 + j * 50)))
    for i, (name, start, length, check, order, uuid, fs, tested) in enumerate(BRANDS):
        y = 200 + i * 92
        p.add(line(80, y + 34, 1440, y + 34, FAINT, 0.8))
        p.add(t(80, y, name, 15, INK, SANS, "start", "bold"),
              t(80, y + 20, "tested on hardware" if tested else "beta – from published work", 11, GREEN if tested else VERM, MONO))
        for (c, x), v in zip(cols[1:], (start, length, check, order, uuid)):
            p.add(t(x, y + 6, v, 12.5, INK, MONO))
        for j, on in enumerate(fs):
            p.add(pixel(1140 + j * 50, y - 12, 22, (GREEN if tested else COBALT) if on else PAPER_DEEP, 2, 5))
    p.add(para(80, 700, "Under the dialects it is one idea: a start marker, a length, a command, a payload, sometimes a "
                        "checksum. Earshot captures that in the Driver protocol – start(), encode(intent), frame(message), "
                        "receive(bytes) – so the app never knows which brand it is talking to. Each brand's layouts come "
                        "from open projects (Gadgetbridge, GalaxyBudsClient) and their captured test messages.", 190, 14, family=SANS))
    return p


PLATES = [opo_frame, opo_battery, opo_sequence, opo_payloads, framing, crc_plate, reassembly, brand_frames, brands]


def dump(n):
    """A raw capture with every frame the decoder found boxed in red, like detection boxes on a photo."""
    p = Plate(n, "dump", "Finding frames in a raw capture", "08 · integrity", 1500, 1020)
    stream = parse_hex(
        "13 37 AA 0D 00 00 06 81 00 06 00 00 02 01 0A 03 00 AA 0B 00 00 0C 81 02 04 00 00 01 01 08 "
        "AA 0D 00 00 04 02 8A 06 00 01 02 01 0A 03 00 AA 0F 00 00 04 02 8B 08 00 02 03 01 03 02 00 03 04 "
        "FF AA 08 00 00 04 84 43 01 00 0E AA 09 00 00 0F 81 44 02 00 00 02 AA 08 00 00 04 05 4F 01 00 01 "
        "AA 11 00 00 0D 81 42 0A 00 00 04 09 00 1B 00 1D 01 1A 01 AA 09 00 00 10 81 41 02 00 00 01 00 00")
    # Walk it exactly as OPOFrameDecoder does.
    frames, i = [], 0
    while i < len(stream):
        if stream[i] != 0xAA:
            i += 1
            continue
        ln = stream[i + 1]
        if i + 2 + ln > len(stream):
            break
        frames.append((i, i + 2 + ln))
        i += 2 + ln
    per, cw, ch, gx, gy = 16, 70, 46, 150, 150
    inside = set()
    for a, b in frames:
        inside.update(range(a, b))
    for k, b in enumerate(stream):
        r, c = divmod(k, per)
        x, y = gx + c * cw, gy + r * ch
        p.add(t(x + cw / 2, y + 28, f"{b:02X}", 17, INK if k in inside else FAINT, MONO, "middle", "bold" if k in inside else "normal"))
    for r in range((len(stream) + per - 1) // per):
        p.add(t(gx - 20, gy + r * ch + 28, f"{r * per:04X}", 12, MUTED, MONO, "end"))
    names = {0x8106: "battery", 0x810C: "noise mode", 0x0204: "push", 0x8404: "refused 0E", 0x810F: "EQ", 0x0504: "EQ push",
             0x810D: "switches", 0x8110: "enhancer"}
    for a, b in frames:
        cmd = stream[a + 4] | stream[a + 5] << 8
        k = a
        first = True
        while k < b:
            r, c = divmod(k, per)
            end = min(b, (r + 1) * per)
            x0 = gx + c * cw + 3
            x1 = gx + ((end - 1) % per + 1) * cw - 3
            y = gy + r * ch + 4
            p.add(rect(x0, y, x1 - x0, ch - 8, "none", VERM, 2.2, 3))
            if first:
                p.add(rect(x0, y - 16, len(names.get(cmd, "?")) * 7.4 + 14, 16, VERM, "none", 0, 2),
                      t(x0 + 7, y - 4, names.get(cmd, "?"), 11, PAPER, MONO, "start", "bold"))
                first = False
            k = end
    rows = (len(stream) + per - 1) // per
    p.add(para(150, gy + rows * ch + 60, f"{len(stream)} bytes as they might arrive, noise included. The decoder finds "
                                          f"{len(frames)} frames: skip anything before an AA, read the length, cut. "
                                          "Grey bytes belong to no frame and are dropped. All frames are real captures "
                                          "from the Buds Air 7.", 150, 14, family=SANS))
    return p


PLATES = [opo_frame, opo_battery, opo_sequence, opo_payloads, framing, crc_plate, reassembly, dump, brand_frames, brands]
