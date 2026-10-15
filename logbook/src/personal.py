# -*- coding: utf-8 -*-
"""FIELD RECORD, personal edition. The three sections added for full color.

Nothing here is copied from any other publication. The frequency and repeater
data are facts, compiled from the sources named on each page; the arrangement,
wording and drawing are original to this book.
"""
from reportlab.lib.units import inch
from reportlab.lib.colors import white, Color
from engine import (INK, G25, G50, G70, W_HAIR, W_RULE, W_MED,
                    SERIF, SERIF_I, COND, COND_B, MONO,
                    fit_text, fit_tracked, wrap_lines,
                    CLR, SLATE, SLATE_MID, SLATE_PALE, AMBER,
                    BAND_COLORS, band_color,
                    head_fill, zebra_fill)
from forms import page_header, blockhead

# =====================================================================
#  1. THE BAND PLAN CHART
# =====================================================================
# (label, low MHz, high MHz, [(seg_low, seg_high, classes, modes)])
# classes: E, A, G, T, N. Drawn darkest for Extra, palest for Tech/Novice.
CHART = [
    ("160", 1.800, 2.000, [(1.800, 2.000, "EAG", "CW, phone, data")]),
    ("80",  3.500, 4.000, [(3.500, 3.525, "E", "CW, data"),
                           (3.525, 3.600, "EAGTN", "CW, data"),
                           (3.600, 3.700, "E", "phone"),
                           (3.700, 3.800, "EA", "phone"),
                           (3.800, 4.000, "EAG", "phone")]),
    ("60",  5.3515, 5.3665, [(5.3515, 5.3665, "EAG", "2.8 kHz, 9.15 W ERP")]),
    ("40",  7.000, 7.300, [(7.000, 7.025, "E", "CW, data"),
                           (7.025, 7.125, "EAGTN", "CW, data"),
                           (7.125, 7.175, "EA", "phone"),
                           (7.175, 7.300, "EAG", "phone")]),
    ("30",  10.100, 10.150, [(10.100, 10.150, "EAG", "CW and data only, 200 W")]),
    ("20",  14.000, 14.350, [(14.000, 14.025, "E", "CW"),
                             (14.025, 14.150, "EAG", "CW, data"),
                             (14.150, 14.175, "E", "phone"),
                             (14.175, 14.225, "EA", "phone"),
                             (14.225, 14.350, "EAG", "phone")]),
    ("17",  18.068, 18.168, [(18.068, 18.110, "EAG", "CW, data"),
                             (18.110, 18.168, "EAG", "phone")]),
    ("15",  21.000, 21.450, [(21.000, 21.025, "E", "CW"),
                             (21.025, 21.200, "EAGTN", "CW, data"),
                             (21.200, 21.225, "E", "phone"),
                             (21.225, 21.275, "EA", "phone"),
                             (21.275, 21.450, "EAG", "phone")]),
    ("12",  24.890, 24.990, [(24.890, 24.930, "EAG", "CW, data"),
                             (24.930, 24.990, "EAG", "phone")]),
    ("10",  28.000, 29.700, [(28.000, 28.300, "EAGTN", "CW, data"),
                             (28.300, 28.500, "EAGTN", "CW, phone"),
                             (28.500, 29.700, "EAG", "phone, FM above 29.5")]),
    ("6",   50.0, 54.0, [(50.0, 50.1, "EAGT", "CW"),
                         (50.1, 54.0, "EAGT", "all modes")]),
    ("2",   144.0, 148.0, [(144.0, 144.1, "EAGT", "CW"),
                           (144.1, 148.0, "EAGT", "all modes")]),
    ("1.25", 222.0, 225.0, [(222.0, 225.0, "EAGTN", "all modes")]),
    ("70cm", 420.0, 450.0, [(420.0, 450.0, "EAGT", "all modes")]),
]

BAND_LABEL = {"70cm": "70 cm", "1.25": "1.25 m", "33cm": "33 cm",
              "23cm": "23 cm"}

BAND_TITLE = {"2": "2 meters", "70cm": "70 centimeters", "6": "6 meters",
              "1.25": "1.25 meters", "10": "10 meters", "33cm": "33 centimeters",
              "23cm": "23 centimeters"}


class Operator(object):
    """What the current build knows about the person the book is for.

    Set once by make_book. When `letter` is set the band chart greys out the
    segments this licence class may not transmit on, which is the difference
    between a chart you read and a chart you use.
    """
    letter = ""          # N, T, G, A or E
    name = ""            # Novice, Technician, ...
    place = ""           # South Carolina, Sacramento Valley, ...
    repeaters = {}       # {band: [(out, sh, tone, call, location, system)]}
    nets = []
    attribution = ""


OP = Operator()


def set_operator(letter="", name="", place=""):
    OP.letter, OP.name, OP.place = letter or "", name or "", place or ""


def set_rf_data(repeaters=None, nets=None, attribution=""):
    OP.repeaters = repeaters or {}
    OP.nets = list(nets or [])
    OP.attribution = attribution or ""


def usable(classes):
    """Can the operator this book is for transmit on a segment?"""
    return (not OP.letter) or (OP.letter in classes)

CLASS_SHADE = {"E": 1.00, "EA": 0.84, "EAG": 0.68, "EAGT": 0.68,
               "EAGTN": 0.42}


def _shade(base, k):
    """Lighten a band color toward paper by factor k (1.0 = full strength)."""
    return Color(base.red + (1 - base.red) * (1 - k),
                 base.green + (1 - base.green) * (1 - k),
                 base.blue + (1 - base.blue) * (1 - k))


def band_chart(bk):
    """A full page color band plan. One row per band, each on its own scale."""
    c = bk.c
    x, y0, w, h0 = bk.body()
    excluded = any(not usable(cls)
                   for (_n, _lo, _hi, segs) in CHART
                   for (_a, _b, cls, _m) in segs)
    if OP.letter and excluded:
        y = page_header(bk, "US Band Plan", big="%s privileges" % OP.name)
        sub = ("SOLID BARS ARE YOURS TO TRANSMIT ON AS A %s. OUTLINED BARS "
               "BELONG TO A HIGHER CLASS. EACH BAND IS ON ITS OWN SCALE, "
               "FREQUENCIES IN MHZ." % OP.name.upper())
        legend = [("Yours to use", None), ("Higher class only", None)]
    elif OP.letter:
        y = page_header(bk, "US Band Plan", big="%s privileges" % OP.name)
        sub = ("EVERY ALLOCATION BELOW IS YOURS. EACH BAND IS ON ITS OWN "
               "SCALE, FREQUENCIES IN MHZ.")
        legend = []
    else:
        y = page_header(bk, "US Band Plan", big="Technician through Extra")
        sub = ("EACH BAR IS ONE BAND ON ITS OWN SCALE. DARKER SHADING "
               "INDICATES FEWER LICENSE CLASSES. FREQUENCIES IN MHZ.")
        legend = [("Extra only", 1.00), ("Extra, Advanced", 0.84),
                  ("General and up", 0.68), ("Technician, Novice", 0.42)]
    fit_tracked(c, x, y - 8, sub, COND, 6.2, w, 0.9, SLATE_MID)
    y -= 18

    # legend
    lw = w / 5.0
    ref = BAND_COLORS["20"] if CLR.on else G50
    for i, (lab, k) in enumerate(legend):
        cx = x + i * lw
        if k is None:
            if i == 0:
                c.setFillColor(ref)
                c.rect(cx, y - 7, 13, 8, stroke=0, fill=1)
            else:
                c.setFillColor(white)
                c.rect(cx, y - 7, 13, 8, stroke=0, fill=1)
        else:
            c.setFillColor(_shade(ref, k))
            c.rect(cx, y - 7, 13, 8, stroke=0, fill=1)
        c.setStrokeColor(SLATE_MID)
        c.setLineWidth(0.4)
        c.rect(cx, y - 7, 13, 8, stroke=1, fill=0)
        fit_tracked(c, cx + 17, y - 5.5, lab.upper(), COND_B, 6.0, lw - 22, 0.8, SLATE)
    y -= 20

    rows = len(CHART)
    foot = 0.62 * inch
    avail = y - y0 - foot
    rh = avail / float(rows)
    barh = min(19.0, rh * 0.52)
    labw = 0.42 * inch

    for i, (name, lo, hi, segs) in enumerate(CHART):
        ry = y - (i + 1) * rh + (rh - barh) / 2.0 + 4
        base = band_color(name)
        any_mine = any(usable(cls) for (_a, _b, cls, _m) in segs)
        # band label chip
        c.setFillColor(base if any_mine else _shade(base, 0.22))
        c.rect(x, ry, labw - 5, barh, stroke=0, fill=1)
        fit_tracked(c, x + (labw - 5) / 2.0, ry + barh / 2.0 - 2.6,
                    BAND_LABEL.get(name, name + " m"),
                    COND_B, 7.2, labw - 10, 0.5, white, align="c")
        bx = x + labw
        bw = w - labw
        span = float(hi - lo)
        for (s0, s1, cls, modes) in segs:
            f0 = (s0 - lo) / span
            f1 = (s1 - lo) / span
            sx, sw = bx + bw * f0, bw * (f1 - f0)
            mine = usable(cls)
            if OP.letter and not mine:
                # not this operator's to use: leave it open, so the eye skips it
                c.setFillColor(SLATE_PALE if CLR.on else white)
                c.rect(sx, ry, sw, barh, stroke=0, fill=1)
            else:
                k = 1.00 if OP.letter else CLASS_SHADE.get(cls, 0.68)
                c.setFillColor(_shade(base, k))
                c.rect(sx, ry, sw, barh, stroke=0, fill=1)
            c.setStrokeColor(white)
            c.setLineWidth(0.7)
            c.rect(sx, ry, sw, barh, stroke=1, fill=0)
            if sw > 34:
                m = modes.lower()
                if "all modes" in m:
                    lab = "all modes"
                elif "only" in m:
                    lab = modes
                elif "phone" in m and "cw" in m:
                    lab = "CW, phone, data"
                elif "phone" in m:
                    lab = "phone"
                elif "kHz" in modes:
                    lab = modes
                else:
                    lab = "CW, data"
                if OP.letter:
                    ink = white if mine else SLATE_MID
                else:
                    ink = white if CLASS_SHADE.get(cls, 0.68) > 0.6 else SLATE
                fit_text(c, sx + sw / 2.0, ry + barh / 2.0 - 2.4, lab.upper(),
                         COND_B, 5.8, sw - 6, ink, align="c")
        c.setStrokeColor(SLATE_MID)
        c.setLineWidth(0.6)
        c.rect(bx, ry, bw, barh, stroke=1, fill=0)
        # edge frequencies
        fit_text(c, bx, ry - 8.0, ("%.4f" % lo).rstrip("0").rstrip("."),
                 MONO, 5.8, 46, SLATE_MID)
        fit_text(c, bx + bw, ry - 8.0, ("%.4f" % hi).rstrip("0").rstrip("."),
                 MONO, 5.8, 46, SLATE_MID, align="r")
        # interior boundaries
        last_f = -1.0
        for (s0, s1, cls, modes) in segs[:-1]:
            f1 = (s1 - lo) / span
            if 0.06 < f1 < 0.94 and (f1 - last_f) > 0.085:
                last_f = f1
                fit_text(c, bx + bw * f1, ry - 8.0,
                         ("%.3f" % s1).rstrip("0").rstrip("."),
                         MONO, 5.4, 40, SLATE_MID, align="c")


    note = (
        "1500 W PEP unless marked. 30 m is 200 W and carries no phone. 60 m is "
        "secondary: 9.15 W ERP referenced to a dipole, 2.8 kHz bandwidth, "
        "General and above, and the four legacy channels either side of the "
        "subband survive at 100 W ERP. Technician and Novice are 200 W PEP on "
        "the HF slices shown, and 25 W PEP on 1.25 m. Compiled from 47 CFR "
        "Part 97 and ARRL allocation data, current 2026. " +
        ("Your class carries its own power limits; the outlined segments are "
         "not yours until you upgrade. " if (OP.letter and excluded) else "") +
        "Verify before you transmit.")
    size, lead = 7.6, 9.6
    lines = wrap_lines(note, SERIF, size, w)
    # Set the block up from the foot so the last line never crosses the trim,
    # shrinking the type if a narrow measure makes it run long.
    while len(lines) * lead > 0.62 * inch - 8 and size > 5.8:
        size -= 0.2
        lead = size * 1.26
        lines = wrap_lines(note, SERIF, size, w)
    top = y0 + 6 + (len(lines) - 1) * lead
    c.setStrokeColor(AMBER if CLR.on else G70)
    c.setLineWidth(1.2)
    c.line(x, top + lead * 0.9, x + w, top + lead * 0.9)
    c.setFont(SERIF, size)
    c.setFillColor(SLATE if CLR.on else INK)
    yy = top
    for ln in lines:
        c.drawString(x, yy, ln)
        yy -= lead


# =====================================================================
#  2. REPEATERS AND NETS
# =====================================================================
# No repeater data lives in this file. It comes from the CSV named in the
# station config, is loaded by rfdata, and is handed here by set_rf_data.
# Anyone's state works, and nobody redistributes anybody's database.


def _blank_rows(bk, x, y, w, cols, fracs, floor, rh=14.5, size=6.0):
    """A ruled continuation of a table, headings only, for the operator."""
    c = bk.c
    ws = [q * w for q in fracs]
    hh = 12.0
    cx = x
    for i, hd in enumerate(cols):
        fit_tracked(c, cx + 3, y - 8.4, hd.upper(), COND_B, size, ws[i] - 6, 0.6,
                    SLATE_MID if CLR.on else G70)
        cx += ws[i]
    c.setStrokeColor(AMBER if CLR.on else G70)
    c.setLineWidth(1.0)
    c.line(x, y - hh, x + w, y - hh)
    top = y - hh
    n = max(3, int((top - floor) // rh))
    zf = zebra_fill()
    for r in range(n):
        ry = top - (r + 1) * rh
        if zf is not None and r % 2 == 1:
            c.setFillColor(zf)
            c.rect(x, ry, w, rh, stroke=0, fill=1)
        c.setStrokeColor(G25)
        c.setLineWidth(W_HAIR)
        c.line(x, ry, x + w, ry)
    cx = x
    for f in ws[:-1]:
        cx += f
        c.setStrokeColor(G25)
        c.setLineWidth(W_HAIR)
        c.line(cx, top, cx, top - n * rh)
    c.setStrokeColor(SLATE_MID if CLR.on else G70)
    c.setLineWidth(W_RULE)
    c.rect(x, top - n * rh, w, n * rh, stroke=1, fill=0)
    return top - n * rh


def _rep_table(bk, x, y, w, rows, size=6.6, rh=None, floor=None,
               colors=None):
    c = bk.c
    cols = ["Output", "Sh", "Tone", "Call", "Location", "System"]
    ws = [.115, .045, .075, .105, .43, .23]
    ws = [q * w for q in ws]
    hh = 13.0
    n = len(rows)
    if rh is None:
        room = y - (floor or 0) - hh
        rh = min(MAX_ROW_H, room / float(n) if n else MAX_ROW_H)
        # Never draw below the floor. If the caller handed over more rows than
        # fit, the table is clipped to what fits rather than run off the sheet.
        if rh < MIN_ROW_H:
            rh = MIN_ROW_H
            keep = max(1, int(room // rh))
            rows = rows[:keep]
            n = len(rows)
    top = y
    hf = head_fill()
    if hf is not None:
        c.setFillColor(hf)
        c.rect(x, top - hh, w, hh, stroke=0, fill=1)
    cx = x
    for i, hd in enumerate(cols):
        fit_tracked(c, cx + 3, top - 9.0, hd.upper(), COND_B, size - 0.6,
                    ws[i] - 6, 0.6, SLATE if CLR.on else INK)
        cx += ws[i]
    c.setStrokeColor(AMBER if CLR.on else G70)
    c.setLineWidth(1.1)
    c.line(x, top - hh, x + w, top - hh)
    zf = zebra_fill()
    for r, row in enumerate(rows):
        ry = top - hh - (r + 1) * rh
        if zf is not None and r % 2 == 1:
            c.setFillColor(zf)
            c.rect(x, ry, w, rh, stroke=0, fill=1)
        cx = x
        for i, v in enumerate(row):
            if i == 5:
                if v:
                    key = (colors or {}).get(v, "70cm")
                    col = band_color(key)
                    c.setFillColor(col)
                    c.rect(cx + 3, ry + rh * 0.22, 7, rh * 0.52, stroke=0, fill=1)
                    fit_text(c, cx + 14, ry + rh * 0.36, v, COND_B, size - 0.4,
                             ws[i] - 18, SLATE if CLR.on else INK)
            else:
                fnt = MONO if i in (0, 2) else (COND_B if i == 3 else SERIF)
                fit_text(c, cx + 3, ry + rh * 0.36, str(v), fnt,
                         size if i != 1 else size, ws[i] - 6,
                         SLATE if CLR.on else INK)
            cx += ws[i]
        c.setStrokeColor(G25)
        c.setLineWidth(W_HAIR)
        c.line(x, ry, x + w, ry)
    c.setStrokeColor(G70)
    c.setLineWidth(W_MED)
    c.rect(x, top - hh - n * rh, w, hh + n * rh, stroke=1, fill=0)
    return top - hh - n * rh


SYS_PALETTE = ["20", "40", "17", "15", "80", "12", "160", "30", "10", "6"]


def _sys_colors(rows):
    """Colour chip per linked system, assigned in order of first appearance."""
    seen = []
    for r in rows:
        v = r[5] if len(r) > 5 else ""
        if v and v not in seen:
            seen.append(v)
    return {v: SYS_PALETTE[i % len(SYS_PALETTE)] for i, v in enumerate(seen)}


def repeater_pages(bk, bands=None):
    """One page per band that has data, in the order given.

    Returns a list of (band, title) for the contents. A band with more rows
    than a page holds continues onto a second page rather than being cut.
    """
    prefer = bands or ["2", "70cm", "6", "1.25", "10", "33cm", "23cm"]
    have = [b for b in OP.repeaters if OP.repeaters.get(b)]
    order = [b for b in prefer if b in have] + \
            [b for b in have if b not in prefer]
    made = []
    if not order and not OP.nets:
        made.append(("blank", "Repeaters and Nets"))
        _blank_page(bk)
        return made
    for band in order:
        rows = OP.repeaters.get(band) or []
        if not rows:
            continue
        made.extend(_repeater_band(bk, band, rows))
    if OP.nets:
        made.append(("nets", "Nets and Schedules"))
        _nets_page(bk)
    return made


def _blank_page(bk):
    """No data file: rule the grids and let the operator fill them in.

    This is not a lesser page. A list you verified on the air beats a list you
    downloaded, and it will not go stale without telling you.
    """
    c = bk.c
    x, y0, w, h0 = bk.body()
    place = OP.place or "Local"
    y = page_header(bk, "%s Repeaters and Nets" % place, big="Your list")
    fit_tracked(c, x, y - 8, "NOTHING HERE UNTIL YOU PUT IT HERE. WRITE DOWN "
                "WHAT YOU HAVE ACTUALLY WORKED, AND THE DATE YOU CHECKED IT.",
                COND, 6.2, w, 0.9, SLATE_MID)
    y -= 18
    mid = y0 + (y - y0) * 0.42
    y = blockhead(bk, x, y, w, "Repeaters", right="output, shift, tone")
    _blank_rows(bk, x, y + 2, w,
                ["Output", "Sh", "Tone", "Call", "Location", "Checked"],
                (.115, .045, .075, .105, .43, .23), mid + 26)
    y = mid + 12
    y = blockhead(bk, x, y, w, "Nets and schedules",
                  right="times as the net announces them")
    _blank_rows(bk, x, y + 2, w,
                ["Net", "Day", "Time", "Where", "Notes"],
                (.205, .09, .075, .175, .455), y0 + 6)
    bk.end_page(kind="ref", part="Part One  Field Reference",
                label="Repeaters")


MIN_ROW_H = 10.5          # a repeater line, at the smallest that stays legible
MAX_ROW_H = 15.0


def rows_per_page(bk, floor_pad):
    """How many table rows fit on this trim above the reserved foot."""
    x, y0, w, h0 = bk.body()
    top = y0 + h0 - 0.62 * inch          # header plus the note under it
    avail = top - (y0 + floor_pad) - 13.0
    return max(4, int(avail // MIN_ROW_H))


def _repeater_band(bk, band, rows):
    c = bk.c
    made = []
    place = OP.place or "Local"
    band_title = BAND_TITLE.get(band, BAND_LABEL.get(band, band + " m"))
    # Reserve more room on the last page: it carries the source note and the
    # ruled block for machines the operator adds later.
    per_last = rows_per_page(bk, 150)
    per_full = rows_per_page(bk, 20)
    chunks = []
    rest = list(rows)
    while rest:
        take = per_last if len(rest) <= per_last else per_full
        chunks.append(rest[:take])
        rest = rest[take:]
    colors = _sys_colors(rows)
    for n, chunk in enumerate(chunks):
        x, y0, w, h0 = bk.body()
        title = "%s Repeaters" % place
        big = band_title if n == 0 else "%s, continued" % band_title
        y = page_header(bk, title, big=big)
        note = ("SH IS THE INPUT SHIFT. TONE IS THE ENCODE TONE THE REPEATER "
                "WANTS. THE COLOR CHIP GROUPS LINKED SYSTEMS.")
        fit_tracked(c, x, y - 8, note, COND, 6.2, w, 0.9, SLATE_MID)
        y -= 18
        last = (n == len(chunks) - 1)
        floor = y0 + (150 if last else 20)
        y = _rep_table(bk, x, y, w, chunk, floor=floor, colors=colors)
        if last:
            y -= 14
            if OP.attribution:
                c.setFont(SERIF_I, 7.4)
                c.setFillColor(SLATE_MID if CLR.on else G70)
                for ln in wrap_lines(
                        OP.attribution + " Repeaters move, retune and go "
                        "silent. Confirm before you rely on one, and wait a "
                        "beat after keying on a linked system so every node "
                        "has time to come up.", SERIF_I, 7.4, w):
                    c.drawString(x, y, ln)
                    y -= 9.8
            y -= 14
            y = blockhead(bk, x, y, w, "Repeaters to add",
                          right="verified on the air, with the date")
            _blank_rows(bk, x, y + 2, w,
                        ["Output", "Sh", "Tone", "Call", "Location", "Checked"],
                        (.115, .045, .075, .105, .43, .23), y0 + 6)
        made.append((band, "%s Repeaters, %s" % (place, band_title)
                     if n == 0 else
                     "%s Repeaters, %s continued" % (place, band_title)))
        bk.end_page(kind="ref", part="Part One  Field Reference",
                    label="Repeaters")
    return made


def _nets_page(bk):
    c = bk.c
    x, y0, w, h0 = bk.body()
    place = OP.place or "Local"
    y = page_header(bk, "Nets and Schedules", big=place)
    fit_tracked(c, x, y - 8, "TIMES AS THE NET ANNOUNCES THEM, WHICH IS USUALLY "
                "LOCAL AND NOT UTC.", COND, 6.2, w, 0.9, SLATE_MID)
    y -= 18

    cols = ["Net", "Day", "Time", "Where", "Notes"]
    ws = [q * w for q in (.205, .09, .075, .175, .455)]
    hh = 13.0
    rh = 15.0
    top = y
    hf = head_fill()
    if hf is not None:
        c.setFillColor(hf)
        c.rect(x, top - hh, w, hh, stroke=0, fill=1)
    cx = x
    for i, hd in enumerate(cols):
        fit_tracked(c, cx + 3, top - 9.0, hd.upper(), COND_B, 6.0, ws[i] - 6,
                    0.6, SLATE if CLR.on else INK)
        cx += ws[i]
    c.setStrokeColor(AMBER if CLR.on else G70)
    c.setLineWidth(1.1)
    c.line(x, top - hh, x + w, top - hh)
    zf = zebra_fill()
    nets = OP.nets
    for r, row in enumerate(nets):
        ry = top - hh - (r + 1) * rh
        if zf is not None and r % 2 == 1:
            c.setFillColor(zf)
            c.rect(x, ry, w, rh, stroke=0, fill=1)
        cx = x
        for i, v in enumerate(row[:5]):
            fnt = MONO if i == 2 else (COND_B if i == 0 else SERIF)
            fit_text(c, cx + 3, ry + rh * 0.34, str(v), fnt, 6.6, ws[i] - 6,
                     SLATE if CLR.on else INK)
            cx += ws[i]
        c.setStrokeColor(G25)
        c.setLineWidth(W_HAIR)
        c.line(x, ry, x + w, ry)
    c.setStrokeColor(G70)
    c.setLineWidth(W_MED)
    c.rect(x, top - hh - len(nets) * rh, w, hh + len(nets) * rh,
           stroke=1, fill=0)
    y = top - hh - len(nets) * rh - 12

    y -= 8
    y = blockhead(bk, x, y, w, "Nets and schedules to add",
                  right="times as the net announces them")
    _blank_rows(bk, x, y + 2, w,
                ["Net", "Day", "Time", "Where", "Notes"],
                (.205, .09, .075, .175, .455), y0 + 6)
    bk.end_page(kind="ref", part="Part One  Field Reference", label="Nets")
