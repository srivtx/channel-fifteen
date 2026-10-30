"""Plates for chapters 02 (signals to bits) and 03 (radio)."""

import math
import random

from plate import *


def sampling(n):
    p = Plate(n, "sampling", "From air pressure to numbers", "02 · signals to bits", 1300, 840)
    x0, x1, yc, amp = 110, 1180, 330, 150
    levels = 8

    def f(u):
        return 0.8 * math.sin(u * 2 * math.pi * 1.6) + 0.18 * math.sin(u * 2 * math.pi * 5.3 + 0.7)

    for k in range(levels):
        y = yc + amp - k * (2 * amp / (levels - 1))
        p.add(line(x0, y, x1, y, FAINT, 0.7, "2 4"), t(x0 - 12, y + 4, format(k, "03b"), 11, MUTED, MONO, "end"))
    p.add(path("M" + " L".join(f"{x0 + u / 400 * (x1 - x0):.1f},{yc - f(u / 400) * amp:.1f}" for u in range(401)), INK, 2.4))
    N = 24
    codes = []
    stair = []
    for i in range(N + 1):
        u = i / N
        v = f(u)
        q = round((v + 1) / 2 * (levels - 1))
        q = max(0, min(levels - 1, q))
        codes.append(q)
        x = x0 + u * (x1 - x0)
        qy = yc + amp - q * (2 * amp / (levels - 1))
        stair.append((x, qy))
        p.add(line(x, yc - v * amp, x, qy, VERM, 1), circle(x, yc - v * amp, 4, VERM))
    d = "M" + "".join(f" L{x:.1f},{y:.1f} L{x + (x1 - x0) / N:.1f},{y:.1f}" for x, y in stair[:-1])[2:]
    p.add(path(d, COBALT, 2.2))
    p.add(t(x0, 140, "PRESSURE AT THE MIC (continuous)", 12, INK, MONO, "start", "bold"),
          t(x1, 140, "SAMPLES (red) · QUANTISED TO 3 BITS (blue)", 12, COBALT, MONO, "end", "bold"))
    p.add(dim(x0, x0 + (x1 - x0) / N, yc + amp + 34, "1 / sample rate"))
    for i, q in enumerate(codes[:N]):
        x = x0 + i * (x1 - x0) / N
        p.add(rect(x + 2, 560, (x1 - x0) / N - 4, 30, PAPER_DEEP, INK, 1, 4),
              t(x + (x1 - x0) / N / 2, 580, format(q, "03b"), 11, INK, MONO, "middle", "bold"))
    p.add(para(110, 650, "A microphone turns pressure into a voltage. An analogue-to-digital converter (ADC) measures "
                         "that voltage at fixed moments – 48 000 times a second in an earbud – and rounds each "
                         "measurement to the nearest of 2ⁿ levels. Real audio uses 16 or 24 bits; three are drawn "
                         "here. To capture a tone you must sample more than twice as fast as it vibrates (Nyquist), "
                         "which is why 48 kHz comfortably covers the 20 kHz limit of hearing. The speaker runs it "
                         "backwards: a DAC turns numbers into voltages, the voice coil into motion, the diaphragm "
                         "into pressure.", 150, 14, family=SANS))
    return p


def logic(n):
    p = Plate(n, "logic", "A voltage becomes a bit", "02 · signals to bits", 1300, 760)
    x0, x1, ylo, yhi = 160, 1180, 470, 210
    bits = [1, 0, 1, 0, 1, 0, 1, 0]
    rnd = random.Random(2)
    vdd = 1.8
    vy = lambda v: ylo - (v / vdd) * (ylo - yhi)
    p.add(line(x0, vy(0.65 * vdd), x1, vy(0.65 * vdd), GREEN, 1, "6 4"), t(x1 + 8, vy(0.65 * vdd) + 4, "VIH 1.17 V", 11, GREEN, MONO),
          line(x0, vy(0.35 * vdd), x1, vy(0.35 * vdd), VERM, 1, "6 4"), t(x1 + 8, vy(0.35 * vdd) + 4, "VIL 0.63 V", 11, VERM, MONO))
    for v, lab in ((0, "0 V"), (vdd, "1.8 V")):
        p.add(t(x0 - 12, vy(v) + 4, lab, 11, MUTED, MONO, "end"))
    pts = []
    w = (x1 - x0) / len(bits)
    for i, b in enumerate(bits):
        for k in range(30):
            u = k / 29
            prev = bits[i - 1] if i else 0
            edge = min(1, u * 6)
            level = prev + (b - prev) * edge
            v = level * vdd * 0.97 + 0.03 + rnd.uniform(-0.08, 0.08)
            pts.append((x0 + (i + u) * w, vy(v)))
        p.add(rect(x0 + i * w + 6, 140, w - 12, 44, VERM if b else PAPER_DEEP, INK, 1.4, 6, 'fill-opacity="0.85"' if b else ""),
              t(x0 + (i + 0.5) * w, 170, str(b), 20, PAPER if b else INK, MONO, "middle", "bold"))
    p.add(path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), INK, 2))
    p.add(t(x0, 520, "1 0 1 0 1 0 1 0  =  0xAA  =  170", 18, INK, MONO, "start", "bold"),
          t(x0, 548, "– the very first byte of every message a realme bud sends or receives", 13, MUTED, SANS))
    p.add(para(x0, 600, "Inside a chip a bit is a wire held near the supply voltage (1) or near ground (0). Anything above "
                        "VIH reads as 1, anything below VIL as 0; the gap in between absorbs noise, which is what makes "
                        "digital robust. A clock decides when to look. Eight of these make a byte, and everything in "
                        "this manual – sound, radio packets, commands – is bytes in the end.", 130, 14, family=SANS))
    return p


def byte_plate(n):
    p = Plate(n, "byte", "One byte, four ways", "02 · signals to bits", 1300, 860)
    value = 0xD5
    x0, y0, s = 150, 170, 96
    total = []
    for i in range(8):
        bit = (value >> (7 - i)) & 1
        weight = 1 << (7 - i)
        x = x0 + i * (s + 8)
        p.add(pixel(x, y0, s, VERM if i == 0 else (INK if bit else PAPER_DEEP), 0, 10))
        p.add(t(x + s / 2, y0 + s / 2 + 12, str(bit), 34, PAPER if bit else INK, MONO, "middle", "bold"),
              t(x + s / 2, y0 - 14, str(weight), 13, MUTED, MONO, "middle"), t(x + s / 2, y0 + s + 22, f"bit {7 - i}", 11, MUTED, MONO, "middle"))
        if bit:
            total.append(str(weight))
    p.add(bracket(x0, x0 + 4 * (s + 8) - 8, y0 + s + 34, "high nibble  D", INK, 13),
          bracket(x0 + 4 * (s + 8), x0 + 8 * (s + 8) - 8, y0 + s + 34, "low nibble  5", INK, 13))
    p.add(t(x0, 410, f"binary 11010101  ·  hex D5  ·  decimal {' + '.join(total)} = {value}", 17, INK, MONO, "start", "bold"))
    p.add(t(x0, 446, "As a realme battery byte it means: top bit 1 = charging, the other seven = 0x55 = 85 %.", 14, VERM, SANS))
    # The sixteen hex digits as 4-pixel strips.
    gx, gy = 150, 510
    p.add(t(gx, gy - 14, "HEX: ONE DIGIT PER FOUR BITS", 12, INK, MONO, "start", "bold"))
    for d in range(16):
        col, row = d % 8, d // 8
        x, y = gx + col * 130, gy + row * 64
        p.add(t(x, y + 22, f"{d:X}", 20, COBALT, MONO, "start", "bold"))
        for k in range(4):
            on = (d >> (3 - k)) & 1
            p.add(pixel(x + 26 + k * 22, y + 4, 22, INK if on else PAPER_DEEP, 2, 4))
    p.add(para(150, 680, "A byte is eight bits, so it holds 0–255. Writing it in base 16 (hexadecimal) gives exactly two "
                         "digits, each standing for four bits – that is why every byte in this manual is two characters "
                         "like D5 or AA. Programmers write 0xD5 to say “this number is hex”.", 130, 14, family=SANS))
    return p


def endian(n):
    p = Plate(n, "endian", "Byte order: which end comes first", "02 · signals to bits", 1300, 800)
    p.add(t(120, 150, "THE NUMBER 0x0106  (= 262, realme's “battery” command)", 15, INK, MONO, "start", "bold"))
    s1, w = byte_strip(160, 200, [0x06, 0x01], [(0, 1, "low byte first", VERM), (1, 2, "then high", COBALT)], 64, 8, False, 20)
    p.add(t(120, 300, "", 10), s1, t(330, 240, "LITTLE-ENDIAN – OPO, Samsung, Nothing, soundcore", 14, INK, SANS, "start", "bold"))
    s2, w = byte_strip(160, 360, [0x01, 0x06], [(0, 1, "high byte first", COBALT), (1, 2, "then low", VERM)], 64, 8, False, 20)
    p.add(s2, t(330, 400, "BIG-ENDIAN – “network order”; Sony's length field", 14, INK, SANS, "start", "bold"))
    p.add(t(120, 530, "A REPLY SETS THE TOP BIT", 15, INK, MONO, "start", "bold"),
          t(120, 562, "0x0106  |  0x8000  =  0x8106    →  sent as  06 81", 17, VERM, MONO, "start", "bold"))
    p.add(para(120, 610, "A number bigger than 255 needs more than one byte, and someone has to decide the order. Most "
                         "chips, including the ARM cores in earbuds and Macs, store the low byte first (little-endian), so "
                         "most of these protocols send it that way too. Read a capture wrong-way-round and 0x0106 becomes "
                         "0x0601 – a command that does not exist. Earshot spells it out with helpers like "
                         "u16(lo, hi) and littleEndianBytes.", 140, 14, family=SANS))
    return p


def bitmask(n):
    p = Plate(n, "bitmask", "Bit masks: many switches in one byte", "02 · signals to bits", 1300, 900)

    def row(y, value, labels, title, note):
        out = [t(120, y - 20, title, 14, INK, MONO, "start", "bold")]
        for i in range(8):
            b = 7 - i
            on = (value >> b) & 1
            x = 120 + i * 84
            lab = labels.get(b)
            fill = (VERM if lab and on else INK) if on else PAPER_DEEP
            out.append(pixel(x, y, 76, fill, 0, 8))
            out.append(t(x + 38, y + 47, str(on), 26, PAPER if on else INK, MONO, "middle", "bold"))
            out.append(t(x + 38, y + 96, f"bit {b}", 10, MUTED, MONO, "middle"))
            if lab:
                out.append(t(x + 38, y + 114, lab, 11, INK, SANS, "middle", "bold"))
        out.append(t(820, y + 32, f"= 0x{value:02X}", 24, INK, MONO, "start", "bold"))
        out += [t(820, y + 60 + k * 18, r, 12.5, MUTED, SANS) for k, r in enumerate(wrap(note, 52))]
        return "".join(out)

    p.add(row(170, 0x0A, {0: "off 01", 1: "ambient 02", 3: "ANC 08"}, "HOLD-CYCLE MASK (realme)",
              "Which modes touch-and-hold steps through. 0x0A = 0x02 | 0x08: ambient and ANC, not off."))
    p.add(row(420, 0xD5, {7: "charging", 6: "64", 5: "32", 4: "16", 3: "8", 2: "4", 1: "2", 0: "1"}, "BATTERY BYTE (realme)",
              "Top bit: charging flag. Low seven bits: level. 0xD5 & 0x7F = 85 %, 0xD5 & 0x80 ≠ 0 → charging."))
    p.add(t(120, 690, "value & mask  → test     value | mask  → set     value & ~mask  → clear", 16, COBALT, MONO, "start", "bold"))
    p.add(para(120, 730, "Protocols squeeze several yes/no answers into one byte by giving each its own bit. Reading them is "
                         "arithmetic with AND (&) and OR (|). Earshot does exactly this: modes.reduce(0) { $0 | code } "
                         "builds the hold-cycle byte, and level & 0x7F / level & 0x80 split a battery byte.", 140, 14, family=SANS))
    return p


def leb128(n):
    p = Plate(n, "leb128", "LEB128: a length that grows when it must", "02 · signals to bits", 1300, 960)
    p.add(t(120, 150, "FRAME LENGTH 207  =  0b 1 1001111", 16, INK, MONO, "start", "bold"))
    bits = format(207, "014b")
    x = 120
    for i, ch in enumerate(bits):
        grp = 0 if i < 7 else 1
        p.add(pixel(x + i * 44 + grp * 26, 180, 40, (COBALT if grp == 0 else VERM) if ch == "1" else PAPER_DEEP, 0, 6),
              t(x + i * 44 + grp * 26 + 20, 207, ch, 16, PAPER if ch == "1" else INK, MONO, "middle", "bold"))
    p.add(bracket(120, 120 + 7 * 44 - 4, 230, "high 7 bits → 0000001", COBALT, 12),
          bracket(120 + 7 * 44 + 26, 120 + 14 * 44 + 22, 230, "low 7 bits → 1001111", VERM, 12))
    p.add(t(120, 340, "1. take the low 7 bits; if more remain, set bit 7 (“more follows”)", 14, INK, SANS),
          t(120, 366, "2. repeat with what's left", 14, INK, SANS))
    s1, w = byte_strip(120, 400, [0xCF, 0x01], [(0, 1, "1|1001111 = CF", VERM, "more follows"), (1, 2, "0|0000001 = 01", COBALT, "last byte")], 130, 30, False, 22)
    p.add(s1)
    p.add(t(120, 650, "ON THE WIRE", 13, INK, MONO, "start", "bold"))
    s2, w = byte_strip(120, 670, [0xAA, 0xCF, 0x01, 0x00, 0x00, 0x05, 0x01, 0x00, 0xC8, 0x00],
                       [(0, 1, "AA", INK), (1, 3, "len 207", VERM), (3, 10, "rest of the frame…", COBALT)], 46, 6, False, 15)
    p.add(s2)
    p.add(para(120, 790, "realme/OPPO frames say how long they are with LEB128 (“little-endian base 128”), the same "
                         "scheme WebAssembly and protobuf use. Short frames – almost all of them – spend one byte on "
                         "the length; long ones grow a second. Earshot's test encodesLongFrameLengthAsLEB128 checks "
                         "exactly this case: a 200-byte payload makes a 207-byte frame, written AA CF 01.", 140, 14, family=SANS))
    return p


# ------------------------------------------------------------------ 03 · radio

def spectrum(n):
    p = Plate(n, "spectrum", "The crowded 2.4 GHz band", "03 · radio", 1400, 860)
    x0, x1 = 120, 1300
    fx = lambda mhz: x0 + (mhz - 2400) / 84 * (x1 - x0)
    p.add(line(x0, 620, x1, 620, INK, 1.5))
    for m in range(2400, 2485, 10):
        p.add(line(fx(m), 620, fx(m), 630, INK, 1), t(fx(m), 648, str(m), 11, INK, MONO, "middle"))
    p.add(t(x1, 672, "MHz", 11, MUTED, MONO, "end"))
    # Wi-Fi 1, 6, 11 as humps.
    for ch, c in ((1, 2412), (6, 2437), (11, 2462)):
        d = f"M{fx(c - 11):.1f},600 C{fx(c - 8):.1f},400 {fx(c + 8):.1f},400 {fx(c + 11):.1f},600"
        p.add(path(d, OCHRE, 2, OCHRE, extra='fill-opacity="0.25"'), t(fx(c), 440, f"Wi-Fi {ch}", 13, INK, SANS, "middle", "bold"))
    # Classic: 79 × 1 MHz.
    for k in range(79):
        x = fx(2402 + k)
        p.add(pixel(x - 6, 560, 12, COBALT, 2, 2))
    p.add(t(x0, 548, "BLUETOOTH CLASSIC – 79 channels × 1 MHz, 2402–2480", 12, COBALT, MONO, "start", "bold"))
    for k in range(40):
        f = 2402 + 2 * k
        adv = k in (0, 12, 39)
        p.add(pixel(fx(f) - 8, 600, 16, VERM if adv else GREEN, 3, 3))
    p.add(t(x0, 716, "BLUETOOTH LOW ENERGY – 40 channels × 2 MHz · red: advertising 37, 38, 39", 12, GREEN, MONO, "start", "bold"))
    p.add(rect(fx(2445), 330, fx(2460) - fx(2445), 250, "url(#dots)", "none", 0, 0, 'opacity="0.35"'),
          t(fx(2452), 320, "microwave ovens", 11, MUTED, SANS, "middle"))
    p.add(para(120, 140, "Radio is electromagnetic waves: electric and magnetic fields swinging back and forth, travelling at "
                         "the speed of light. At 2.4 GHz they swing 2.4 billion times a second and each wave is about "
                         "12.5 cm long – short enough for a millimetre-scale antenna in a stem to work. This band is free "
                         "for anyone to use without a licence (ISM), so Bluetooth shares it with Wi-Fi, baby monitors "
                         "and microwave ovens.", 150, 14, family=SANS))
    p.add(t(120, 790, "Your audio and Earshot's commands travel on the blue channels: the buds speak Bluetooth Classic.", 13, INK, SANS))
    return p


def gfsk(n):
    p = Plate(n, "gfsk", "GFSK: bits as small shifts in frequency", "03 · radio", 1300, 820)
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    x0, x1 = 120, 1180
    w = (x1 - x0) / len(bits)
    for i, b in enumerate(bits):
        p.add(pixel(x0 + i * w + 4, 130, w - 8, VERM if b else PAPER_DEEP, 0, 6),
              t(x0 + (i + 0.5) * w, 162, str(b), 20, PAPER if b else INK, MONO, "middle", "bold"))
    # Square, then Gaussian-smoothed.
    sq = []
    for i, b in enumerate(bits):
        y = 230 if b else 290
        sq += [(x0 + i * w, y), (x0 + (i + 1) * w, y)]
    p.add(path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in sq), FAINT, 1.4, dash="4 4"))
    N = 800
    raw = [bits[min(len(bits) - 1, int(k / N * len(bits)))] * 2 - 1 for k in range(N)]
    sigma = N / len(bits) * 0.22
    ker = [math.exp(-(j / sigma) ** 2 / 2) for j in range(-60, 61)]
    ks = sum(ker)
    smooth = [sum(raw[min(N - 1, max(0, k + j - 60))] * ker[j] for j in range(len(ker))) / ks for k in range(N)]
    p.add(path("M" + " L".join(f"{x0 + k / N * (x1 - x0):.1f},{260 - smooth[k] * 30:.1f}" for k in range(N)), COBALT, 2.4))
    p.add(t(x1 + 8, 234, "+f", 12, COBALT, MONO), t(x1 + 8, 294, "−f", 12, COBALT, MONO),
          t(x0, 330, "GAUSSIAN FILTER rounds the corners so the signal doesn't splatter into neighbouring channels", 12, COBALT, MONO))
    phase, pts = 0.0, []
    for k in range(N):
        phase += 0.25 + 0.09 * smooth[k]
        pts.append(f"{x0 + k / N * (x1 - x0):.1f},{470 - math.sin(phase) * 60:.1f}")
    p.add(path("M" + " L".join(pts), INK, 1.6))
    p.add(t(x0, 380, "THE CARRIER: a little faster for 1, a little slower for 0 (drawn hugely slowed down)", 12, INK, MONO, "start", "bold"))
    p.add(dim(x0, x0 + w, 560, "1 µs per bit (1 Mbit/s)"))
    p.add(para(120, 620, "To send a bit, the radio nudges its frequency a little up (±≈160 kHz around the channel centre) "
                         "for a 1 and down for a 0: frequency-shift keying. Smoothing the switch with a Gaussian curve "
                         "keeps the energy inside the 1 MHz channel. Faster “EDR” modes (2–3 Mbit/s) also shift the "
                         "wave's phase, which is how earbuds fit high-quality audio through the air.", 140, 14, family=SANS))
    return p


def hopping(n):
    p = Plate(n, "hopping", "Frequency hopping, 1600 times a second", "03 · radio", 1400, 960)
    rows, cols = 79, 112
    cw, ch_ = 7.4, 7
    gx, gy = 130, 140
    rnd = random.Random(11)
    wifi = range(24, 47)  # 2426–2448 MHz: Wi-Fi channel 6
    p.add(rect(gx, gy, cols * cw, rows * ch_, PAPER_DEEP, INK, 1))
    afh_at = 52
    p.add(f'<rect x="{gx}" y="{gy + (78 - 46) * ch_}" width="{afh_at * cw}" height="{23 * ch_}" fill="{OCHRE}" opacity="0.14"/>',
          f'<rect x="{gx + afh_at * cw}" y="{gy + (78 - 46) * ch_}" width="{(cols - afh_at) * cw}" height="{23 * ch_}" fill="{OCHRE}" opacity="0.32"/>')
    c = 0
    while c < cols:
        allowed = [k for k in range(79) if c < afh_at or k not in wifi]
        ch = rnd.choice(allowed)
        span = rnd.choice([1, 1, 1, 3, 5]) if c > 6 else 1
        hit = c < afh_at and ch in wifi
        colr = VERM if hit else (COBALT if span > 1 else INK)
        p.add(f'<rect x="{gx + c * cw + 0.6:.1f}" y="{gy + (78 - ch) * ch_ + 0.6:.1f}" width="{min(span, cols - c) * cw - 1.2:.1f}" '
              f'height="{ch_ - 1.2:.1f}" rx="1.6" fill="{colr}"/>')
        c += span
    s = cw
    p.add(line(gx + afh_at * cw, gy - 16, gx + afh_at * cw, gy + rows * ch_ + 10, VERM, 1.4, "6 4"),
          t(gx + afh_at * cw + 8, gy - 4, "AFH on: Wi-Fi channels struck from the hop list", 12, VERM, SANS, "start", "bold"))
    for chn in (0, 39, 78):
        p.add(t(gx - 10, gy + (78 - chn) * ch_ + 6, f"{2402 + chn}", 10, MUTED, MONO, "end"))
    p.add(t(gx, gy + rows * ch_ + 50, "each column is one 625 µs slot · each row one 1 MHz channel", 11, MUTED, MONO),
          dim(gx, gx + cw * 3, gy + rows * ch_ + 22, "3 slots"))
    cols_w = cols * cw / s
    p.add(t(gx + cols * cw + 30, 190, "LEGEND", 12, INK, MONO, "start", "bold"))
    for i, (col, lab) in enumerate(((INK, "1-slot packet (commands, acks)"), (COBALT, "3/5-slot packet (audio)"),
                                    (VERM, "landed on Wi-Fi – likely lost"), (OCHRE, "Wi-Fi channel 6"))):
        p.add(pixel(gx + cols * cw + 30, 210 + i * 30, 18, col, 2, 3), t(gx + cols * cw + 58, 224 + i * 30, lab, 12, INK, SANS))
    p.add(*[t(gx + cols * cw + 30, 380 + i * 20, r, 13, INK, SANS) for i, r in enumerate(wrap(
        "Classic Bluetooth never sits still. The phone (the central) and the buds hop to a new 1 MHz channel every "
        "625 µs slot – 1600 times a second – in a pseudo-random order both sides compute from the central's address "
        "and clock. Interference only ever spoils a slot or two, and the lost packet is simply sent again on the "
        "next hop. Adaptive hopping (AFH) goes further and drops channels that keep failing. Earshot's bytes ride "
        "this whole dance without knowing it.", 32))])
    return p


def tws(n):
    p = Plate(n, "tws", "Piconets and how two buds share one phone", "03 · radio", 1400, 900)

    def node(x, y, label, sub, fill=PAPER_DEEP):
        return rect(x - 90, y - 34, 180, 68, fill, INK, 1.6, 10) + t(x, y - 4, label, 15, INK, SANS, "middle", "bold") + t(x, y + 16, sub, 11, MUTED, MONO, "middle")

    p.add(t(110, 130, "A · RELAY (older TWS)", 14, INK, MONO, "start", "bold"))
    p.add(node(250, 230, "Mac / phone", "central"), node(250, 420, "Primary bud", "peripheral"), node(250, 610, "Secondary bud", "relayed"))
    p.add(arrow(250, 266, 250, 384, COBALT, 2.2), t(262, 330, "audio + control", 12, COBALT, SANS),
          arrow(250, 456, 250, 574, VERM, 2.2), t(262, 520, "forwarded bud-to-bud", 12, VERM, SANS))
    p.add(t(560, 130, "B · SNOOPING / MIRRORING (most buds today)", 14, INK, MONO, "start", "bold"))
    p.add(node(820, 230, "Mac / phone", "sees one device"), node(680, 450, "Primary bud", "owns the link"), node(960, 450, "Secondary bud", "listens in"))
    p.add(arrow(800, 266, 700, 414, COBALT, 2.2), path("M840,266 L940,414", VERM, 2, dash="6 5"),
          t(900, 330, "eavesdrops on the same hops", 12, VERM, SANS), path("M770,470 L870,470", INK, 1.4, dash="3 4"),
          t(820, 494, "sync + acks", 11, MUTED, SANS, "middle"))
    p.add(t(1150, 130, "A PICONET", 14, INK, MONO, "start", "bold"))
    for i in range(7):
        a = i / 7 * 2 * math.pi
        x, y = 1240 + 90 * math.cos(a), 300 + 90 * math.sin(a)
        p.add(line(1240, 300, x, y, FAINT, 1), circle(x, y, 9, COBALT if i < 2 else PAPER_DEEP, INK, 1.2))
    p.add(circle(1240, 300, 16, VERM, INK, 1.4), t(1240, 425, "1 central, ≤ 7 active peripherals", 11, INK, SANS, "middle"),
          t(1240, 445, "all hopping on the central's clock", 11, MUTED, SANS, "middle"))
    p.add(t(1150, 520, "EVERY RADIO HAS A BD_ADDR", 12, INK, MONO, "start", "bold"),
          t(1150, 546, "xx:xx:xx:xx:xx:xx", 16, VERM, MONO, "start", "bold"),
          t(1150, 568, "48 bits; top 24 name the maker", 11, MUTED, SANS))
    p.add(para(110, 720, "Your Mac only ever talks to one bud – the primary. When Earshot changes the noise mode, the "
                         "primary applies it and passes it to its twin over their own link. That is also why the buds "
                         "can refuse a command (status 0x0E) when neither is in an ear, and why a reply can lack the "
                         "right bud's battery: it is asleep, not lost.", 160, 14, family=SANS))
    return p


PLATES = [sampling, logic, byte_plate, endian, bitmask, leb128, spectrum, gfsk, hopping, tws]
