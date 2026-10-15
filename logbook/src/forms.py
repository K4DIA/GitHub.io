# -*- coding: utf-8 -*-
"""FIELD RECORD - fixed-layout record pages."""
from reportlab.lib.units import inch
from reportlab.lib.colors import white
from engine import (INK, G25, G35, G50, G70,
                    W_HAIR, W_RULE, W_MED, W_HEAVY, SERIF_I,
                    COND, COND_SB, COND_B, MONO,
                    tracked, fit_tracked, wrap_lines,
                    INKM, head_fill, zebra_fill, CLR, band_ink,
                    rule_ink, SLATE, AMBER, SLATE_MID)

BANDS_SHORT = ["80", "60", "40", "30", "20", "17", "15", "12", "10", "6/2"]


# ------------------------------------------------------------------ header
def page_header(bk, kind, right_label=None, big=None, sub=None):
    """Standard record-page header band. Returns y of the top of the work area."""
    c = bk.c
    x, y, w, h = bk.body()
    top = y + h
    bh = 0.30 * inch
    if INKM.weatherproof:
        # rules plus one small anchor square instead of a solid reversed band
        c.setFillColor(INK)
        c.rect(x, top - bh + 0.088 * inch, 0.115 * inch, 0.115 * inch,
               stroke=0, fill=1)
        bk.rule(x, top, w, W_HEAVY, INK)
        bk.rule(x, top - bh, w, W_MED, INK)
        fg, x_text = INK, x + 0.185 * inch
    else:
        c.setFillColor(band_ink())
        c.rect(x, top - bh, w, bh, stroke=0, fill=1)
        if CLR.on:
            c.setFillColor(AMBER)
            c.rect(x, top - bh - 1.8, w, 1.8, stroke=0, fill=1)
        fg, x_text = white, x + 6
    kw = fit_tracked(c, x_text, top - 0.205 * inch, kind.upper(), COND_B,
                     9.4, w * 0.44, 1.5, fg)
    if big:
        fit_tracked(c, x + w - 6, top - 0.205 * inch, big.upper(), COND_B,
                    9.4, w - kw - 34, 1.5, fg, align="r")
    yy = top - 0.30 * inch
    if right_label:
        bk.rule(x, yy - 0.16 * inch, w, W_HAIR, G35)
        tracked(c, x + w - 2, yy - 0.135 * inch, right_label.upper(), COND, 6.0,
                0.8, G50, align="r")
        yy -= 0.16 * inch
    return yy - 3.0


def blockhead(bk, x, y, w, text, right=None):
    """Small caps block heading with a rule beneath. Returns new y."""
    c = bk.c
    tw = fit_tracked(c, x, y - 6.4, text.upper(), COND_B, 6.9, w * 0.62, 1.25,
                     SLATE if CLR.on else INK)
    if right:
        fit_tracked(c, x + w, y - 6.4, right.upper(), COND, 6.0,
                    max(24.0, w - tw - 10), 0.7,
                    SLATE_MID if CLR.on else G50, align="r")
    bk.rule(x, y - 9.6, w, W_MED, rule_ink())
    if CLR.on:
        bk.rule(x, y - 9.6, min(w, tw + 8), 1.6, AMBER)
    return y - 18.0


def fields_row(bk, x, y, w, specs, gap=7.0, lh=None):
    """Draw one row of write-on fields.

    specs: list of (label, weight) or (label, weight, value). A value is
    printed on the rule in mono, which is how a filled book reads back: the
    machine-set entries are visibly machine-set and anything still blank is
    still yours to write. Two-element specs behave exactly as before, so every
    existing caller is untouched.
    """
    total = sum(sp[1] for sp in specs)
    n = len(specs)
    avail = w - gap * (n - 1)
    cx = x
    for sp in specs:
        label, wt = sp[0], sp[1]
        val = sp[2] if len(sp) > 2 else getattr(bk, "values", {}).get(label)
        fw = avail * wt / total
        fit_tracked(bk.c, cx, y + 2.4, label.upper(), COND_SB, 5.5, fw - 1.0,
                    0.85, G70)
        bk.rule(cx, y - 6.2, fw, W_RULE, G35)
        if val not in (None, ""):
            fit_tracked(bk.c, cx + 1.5, y - 4.6, str(val), MONO, 6.4,
                        fw - 3.0, 0.0, INK)
        cx += fw + gap
    return y - 6.2


def minitable(bk, x, y, w, cols, row_labels, cell_h, head_h=10.5,
              first_col_w=0.16, size=5.9, zebra=False, values=None):
    """A small pre-labeled write-in matrix. Returns bottom y.

    values, when given, is {row_label: {col_label: text}}. Cells it does not
    name are left blank for pen, so a partly known matrix still prints.
    """
    c = bk.c
    ncol = len(cols)
    fc = w * first_col_w if row_labels else 0
    cw = (w - fc) / float(ncol)
    top = y
    nrow = len(row_labels) if row_labels else 1
    hgt = head_h + nrow * cell_h
    hf = head_fill()
    if hf is not None:
        c.setFillColor(hf)
        c.rect(x, top - head_h, w, head_h, stroke=0, fill=1)
    zf = zebra_fill()
    if zebra and zf is not None:
        c.setFillColor(zf)
        for i in range(nrow):
            if i % 2 == 1:
                c.rect(x, top - head_h - (i + 1) * cell_h, w, cell_h, stroke=0, fill=1)
    for i, cl in enumerate(cols):
        fit_tracked(c, x + fc + cw * (i + 0.5), top - head_h + 3.2, str(cl).upper(),
                    COND_B, size, cw - 3.0, 0.45, INK, align="c")
    for j, rl in enumerate(row_labels or []):
        fit_tracked(c, x + 3.5, top - head_h - cell_h * (j + 1) + cell_h / 2 - 2.0,
                    str(rl).upper(), COND_B, size, max(10.0, fc - 6.0), 0.45, G70)
        row_vals = (values or {}).get(rl) or {}
        bkv = getattr(bk, "values", {}) or {}
        for i, cl in enumerate(cols):
            cell = row_vals.get(cl)
            if cell in (None, ""):
                cell = bkv.get("%s|%s" % (rl, cl))
            if cell in (None, ""):
                continue
            fit_tracked(c, x + fc + cw * (i + 0.5),
                        top - head_h - cell_h * (j + 1) + cell_h / 2 - 2.0,
                        str(cell), MONO, size + 0.3, cw - 3.0, 0.0, INK,
                        align="c")
    bk.rule(x, top, w, W_MED, G70)
    bk.rule(x, top - head_h, w, W_RULE, G70)
    for i in range(1, nrow + 1):
        bk.rule(x, top - head_h - i * cell_h, w,
                W_HAIR if i < nrow else W_MED, G35 if i < nrow else G70)
    bk.vrule(x, top - hgt, hgt, W_MED, G70)
    if fc:
        bk.vrule(x + fc, top - hgt, hgt, W_RULE, G50)
    for i in range(ncol):
        cx = x + fc + cw * (i + 1)
        bk.vrule(cx, top - hgt, hgt, W_MED if i == ncol - 1 else W_HAIR,
                 G70 if i == ncol - 1 else G35)
    return top - hgt


def ruled_area(bk, x, y, w, h, title, rows=None, pitch=0.19 * inch):
    y2 = blockhead(bk, x, y, w, title)
    inner_h = h - (y - y2)
    n = rows or max(1, int(inner_h // pitch))
    rh = inner_h / float(n)
    for i in range(n):
        bk.rule(x, y2 - (i + 1) * rh + 2.0, w, W_HAIR, G25)
    return y - h


# ------------------------------------------------------------------ site record
def site_record(bk, num):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = page_header(bk, "Site Record", big="Deployment %02d" % num)
    bottom = y0
    avail = y - bottom

    # -- 1 LOCATION
    y = blockhead(bk, x, y, w, "Location", right="all times UTC")
    y = fields_row(bk, x, y - 2, w, [("Site name", 3), ("Program reference", 2),
                                     ("Date (UTC)", 1.15)])
    y = fields_row(bk, x, y - 13, w, [("Grid (6)", 1.05), ("Latitude", 1.35),
                                      ("Longitude", 1.35), ("Elevation", 0.85),
                                      ("ARRL section", 0.9)])
    y = fields_row(bk, x, y - 13, w, [("Access, permit, hours, hazards", 1)])
    y -= 11

    # -- 2 CONDITIONS
    y = blockhead(bk, x, y, w, "Conditions")
    y = fields_row(bk, x, y - 2, w, [("Sky", 1.5), ("Temp", 0.75), ("Wind", 1.1),
                                     ("SFI", 0.6), ("A", 0.45), ("K", 0.45),
                                     ("Sunrise Z", 0.85), ("Sunset Z", 0.85)])
    y -= 9
    y = minitable(bk, x, y, w, BANDS_SHORT, ["S-units"], cell_h=0.185 * inch * bk.t.fs,
                  head_h=10.0 * bk.t.fs, first_col_w=0.135, size=5.8 * bk.t.fs)
    tracked(c, x, y - 7.0, "MEASURED NOISE FLOOR, ANTENNA CONNECTED, PREAMP OFF",
            COND, 5.3, 0.6, G50)
    y -= 15

    # -- 3 STATION
    y = blockhead(bk, x, y, w, "Station")
    y = fields_row(bk, x, y - 2, w, [("Radio", 2.0), ("Output power", 1.0),
                                     ("Key / mic", 1.2), ("Logging device", 1.4)])
    y = fields_row(bk, x, y - 13, w, [("Battery / pack", 2.0), ("Start volts", 0.8),
                                      ("Fuse", 0.7), ("Other loads on the pack", 2.0)])
    y -= 11

    # -- 4 ANTENNA
    y = blockhead(bk, x, y, w, "Antenna")
    y = fields_row(bk, x, y - 2, w, [("Type", 2.0), ("Bands", 1.0),
                                     ("Feedpoint height", 1.0), ("Support", 1.4)])
    y = fields_row(bk, x, y - 13, w, [("Orientation / ends toward", 1.7),
                                      ("Feedline and length", 1.5),
                                      ("Matching / counterpoise", 1.6)])
    y -= 9
    y = minitable(bk, x, y, w, BANDS_SHORT, ["SWR", "Tuner"], cell_h=0.185 * inch * bk.t.fs,
                  head_h=10.0 * bk.t.fs, first_col_w=0.135, size=5.8 * bk.t.fs)
    y -= 13

    # -- 5 EXPOSURE + TIMELINE (two columns)
    colw = (w - 12) / 2.0
    ytop = y
    ya = blockhead(bk, x, ytop, colw, "RF exposure")
    ya = fields_row(bk, x, ya - 2, colw, [("Exclusion distance", 1),
                                          ("Public separation", 1)])
    ya = fields_row(bk, x, ya - 13, colw, [("Evaluation basis / notes", 1)])
    xb = x + colw + 12
    yb = blockhead(bk, xb, ytop, colw, "Timeline (UTC)")
    yb = fields_row(bk, xb, yb - 2, colw, [("On site", 1), ("Antenna up", 1),
                                           ("First call", 1)])
    yb = fields_row(bk, xb, yb - 13, colw, [("Off air", 1), ("Packed", 1),
                                            ("Departed", 1)])
    y = min(ya, yb) - 11

    # -- 6 SKETCH fills the rest
    sk_h = y - bottom - 2
    if sk_h > 0.7 * inch:
        y2 = blockhead(bk, x, y, w, "Site sketch",
                       right="orientation, supports, hazards")
        bk.dotgrid(x, bottom + 2, w, y2 - bottom - 4)
        c.setStrokeColor(G35)
        c.setLineWidth(W_RULE)
        c.rect(x, bottom + 2, w, y2 - bottom - 4, stroke=1, fill=0)
        # north arrow in the corner
        cx0, cy0 = x + w - 20, y2 - 20
        c.setStrokeColor(G50)
        c.setLineWidth(W_MED)
        c.line(cx0, cy0 - 9, cx0, cy0 + 7)
        c.line(cx0, cy0 + 7, cx0 - 3.2, cy0 + 1.8)
        c.line(cx0, cy0 + 7, cx0 + 3.2, cy0 + 1.8)
        tracked(c, cx0, cy0 - 17, "N", COND_B, 6.0, 0, G50, align="c")


# ------------------------------------------------------------------ qso log
def qso_log(bk, num, sheet, letter):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = page_header(bk, "QSO Log", big="Deployment %02d  /  Sheet %s" % (num, letter))

    # date strip
    y = fields_row(bk, x, y - 6, w, [("Date (UTC)", 1.1), ("Callsign used", 1.2),
                                     ("Program reference", 1.6), ("Sheet", 0.5)])
    y -= 10

    six = bk.t.key == "6x9"
    if six:
        heads = ["UTC", "Callsign", "Band", "Mode", "W", "Sent", "Rcvd",
                 "QTH / Reference", "Notes"]
        widths = [.088, .175, .072, .072, .052, .062, .062, .200, .217]
        num_col = False
        size = 5.9
    else:
        heads = ["#", "UTC", "Callsign", "Band", "Mode", "W", "Sent", "Rcvd",
                 "State / Park / Summit / Grid", "Notes"]
        widths = [.032, .076, .148, .062, .062, .046, .052, .052, .190, .280]
        num_col = True
        size = 6.2

    rows = bk.t.log_rows
    row_h = bk.t.log_row_h
    foot_h = 0.44 * inch
    grid_top = y
    grid_h = rows * row_h + 13.0
    while grid_top - grid_h < y0 + foot_h:
        rows -= 1
        grid_h = rows * row_h + 13.0

    bottom = bk.formgrid(x, grid_top - grid_h, w, grid_h, heads, widths, rows,
                         row_h=row_h, head_h=13.0, zebra=True, num_col=num_col,
                         size=size)

    # RST bracket over the two report columns
    total = sum(widths)
    acc = x
    idx = heads.index("Sent")
    for i in range(idx):
        acc += widths[i] / total * w
    rst_w = (widths[idx] + widths[idx + 1]) / total * w
    tracked(c, acc + rst_w / 2.0, grid_top + 2.4, "RST", COND, 5.4, 0.9, G50,
            align="c")
    bk.rule(acc, grid_top + 1.0, rst_w, W_HAIR, G50)

    # footer tally strip
    fy = bottom - 12
    if six:
        specs = [("QSOs this sheet", 1.1), ("P2P / S2S", 0.8), ("New states", 0.9),
                 ("New entities", 0.95), ("Running total", 1.05)]
    else:
        specs = [("QSOs this sheet", 1.0), ("Park to park / summit to summit", 1.5),
                 ("New states", 0.9), ("New entities", 0.9), ("Running total", 1.0)]
    fields_row(bk, x, fy, w, specs)


# ------------------------------------------------------------------ debrief
def debrief(bk, num):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = page_header(bk, "Debrief", big="Deployment %02d" % num)
    bottom = y0

    # -- tally matrix
    y = blockhead(bk, x, y - 2, w, "Tally", right="contacts by band and mode")
    modes = ["CW", "SSB", "FM", "AM", "Digital", "Total"]
    y = minitable(bk, x, y - 2, w, modes,
                  ["160", "80/75", "60", "40", "30", "20", "17", "15", "12", "10",
                   "6", "2 / 70", "TOTAL"],
                  cell_h=0.165 * inch * bk.t.fs, head_h=10.5 * bk.t.fs,
                  first_col_w=0.155, size=5.8 * bk.t.fs,
                  zebra=True)
    y -= 12

    # -- summary
    y = blockhead(bk, x, y, w, "Summary")
    y = fields_row(bk, x, y - 2, w, [("Total QSOs", 0.8), ("P2P / S2S", 0.8),
                                     ("States", 0.6), ("Entities", 0.7),
                                     ("Activation valid", 0.9),
                                     ("Log uploaded", 0.9)])
    y = fields_row(bk, x, y - 13, w, [("Best DX, callsign", 1.2), ("Grid", 0.7),
                                      ("Approx miles", 0.8), ("Band and mode", 1.0),
                                      ("Their power", 0.7)])
    y -= 11

    # -- power
    y = blockhead(bk, x, y, w, "Power")
    y = fields_row(bk, x, y - 2, w, [("Start volts", 0.8), ("End volts", 0.8),
                                     ("Amp hours used", 1.0), ("Hours on air", 0.9),
                                     ("Average current", 1.0), ("Recharge by", 1.0)])
    y -= 12

    # -- three prose blocks share what is left
    remain = y - bottom - 6
    each = remain / 3.0
    for title, hint in [("What worked", ""),
                        ("What failed", "gear, site, technique, weather"),
                        ("Action before the next deployment", "")]:
        yb = blockhead(bk, x, y, w, title, right=hint)
        inner = each - (y - yb) - 4
        n = max(2, int(inner // (0.185 * inch)))
        rh = inner / float(n)
        for i in range(n):
            bk.rule(x, yb - (i + 1) * rh + 2.0, w, W_HAIR, G25)
        y -= each


# ------------------------------------------------------------------ generic form page
MIN_ROW_H = 0.245 * inch          # a hand-written line, at the smallest useful


def form_page(bk, title, subtitle, headers, widths, rows=None, row_h=None,
              num_col=False, intro=None, big=None, part=None, sec=None,
              footer_fields=None, size=6.2, stretch=False,
              max_row_h=0.40 * inch):
    """Draw a ruled form. Sets form_page.drawn to the number of rows placed."""
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = page_header(bk, title, big=big)
    if subtitle:
        tracked(c, x, y - 8.0, subtitle.upper(), COND, 5.8, 0.85, G50)
        y -= 14
    if intro:
        c.setFillColor(G70)
        c.setFont(SERIF_I, bk.t.base - 1.2)
        for ln in wrap_lines(intro, SERIF_I, bk.t.base - 1.2, w):
            y -= (bk.t.base - 1.2) * 1.25
            c.drawString(x, y, ln)
        y -= 8
    foot = 0.0
    if footer_fields:
        foot = 0.42 * inch
    avail = y - y0 - foot
    rh = row_h or MIN_ROW_H
    # How many rows this page can actually hold at that height. A caller that
    # asks for more gets what fits and is told how many were drawn, so a long
    # table can be continued rather than run off the sheet.
    fit = max(1, int((avail - 13.0) // rh))
    n = fit if rows is None else min(rows, fit)
    if stretch and rows is not None and n == rows:
        rh = min(max_row_h, max(rh, (avail - 13.0) / float(n)))
    gh = n * rh + 13.0
    bottom = bk.formgrid(x, y - gh, w, gh, headers, widths, n, row_h=rh,
                         head_h=13.0, zebra=True, num_col=num_col, size=size)
    if footer_fields:
        fields_row(bk, x, bottom - 12, w, footer_fields)
    form_page.drawn = n
    return bottom


# ------------------------------------------------------------------ antenna build sheet
def swr_chart(bk, x, y, w, h, label):
    """A blank SWR sweep grid: frequency across, SWR 1 to 3 up."""
    c = bk.c
    pad_l, pad_b = 20.0, 34.0
    gx, gy = x + pad_l, y + pad_b
    gw, gh = w - pad_l - 2, h - pad_b - 12
    # y axis: SWR 1.0 to 3.0 in 0.25 steps
    steps = 8
    for i in range(steps + 1):
        yy = gy + gh * i / float(steps)
        heavy = (i % 4 == 0)
        bk.rule(gx, yy, gw, W_RULE if heavy else W_HAIR, G50 if heavy else G25)
        if i % 2 == 0:
            tracked(c, gx - 3, yy - 2.0, "%.1f" % (1.0 + i * 0.25), MONO, 5.2, 0,
                    G50, align="r")
    for i in range(11):
        xx = gx + gw * i / 10.0
        heavy = (i % 5 == 0)
        bk.vrule(xx, gy, gh, W_RULE if heavy else W_HAIR, G50 if heavy else G25)
    tracked(c, x, y + h - 6.0, label.upper(), COND_B, 6.2, 1.0, INK)
    tracked(c, gx, gy - 8.5, "F LOW", COND, 5.2, 0.5, G50)
    tracked(c, gx + gw, gy - 8.5, "F HIGH", COND, 5.2, 0.5, G50, align="r")
    tracked(c, gx + gw / 2, gy - 8.5, "FREQUENCY", COND, 5.2, 0.7, G50, align="c")
    tracked(c, x + 1, y + h - 5.5, "SWR", COND, 5.2, 0.7, G50)
    bk.rule(gx, gy, gw, W_MED, G70)
    bk.vrule(gx, gy, gh, W_MED, G70)
    # write-in band + edges
    fields_row(bk, gx, gy - 25, gw, [("Band", 1), ("F low", 1), ("F min SWR", 1.2),
                                     ("F high", 1)])


def antenna_build_page(bk, n):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = page_header(bk, "Antenna Build Sheet", big="No. %02d" % n)
    y = blockhead(bk, x, y - 2, w, "Design")
    y = fields_row(bk, x, y - 2, w, [("Antenna name", 2.0), ("Type", 1.4),
                                     ("Design frequency", 1.0), ("Built on", 0.9)])
    y = fields_row(bk, x, y - 13, w, [("Wire gauge and type", 1.4),
                                      ("Cut length, each leg", 1.2),
                                      ("Insulators", 1.0), ("Transformer / balun", 1.2)])
    y = fields_row(bk, x, y - 13, w, [("Feedline", 1.2), ("Counterpoise / radials", 1.4),
                                      ("Support and height", 1.3), ("Mass", 0.6)])
    y -= 13
    y = blockhead(bk, x, y, w, "Trim log", right="measured")
    y = minitable(bk, x, y - 2, w, ["Cut 1", "Cut 2", "Cut 3", "Cut 4", "Final"],
                  ["Length", "F res", "SWR"], cell_h=0.185 * inch * bk.t.fs,
                  head_h=10.5 * bk.t.fs, first_col_w=0.16, size=5.8 * bk.t.fs)
    y -= 14
    y = blockhead(bk, x, y, w, "Sweep", right="measured SWR against frequency")
    ch = (y - y0 - 4) / 2.0
    swr_chart(bk, x, y - ch + 4, w, ch - 8, "Sweep A")
    swr_chart(bk, x, y0 + 2, w, ch - 8, "Sweep B")
