# -*- coding: utf-8 -*-
"""FIELD RECORD - print-ready wrap cover and flat front cover."""
import os, math, sys
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, white
from engine import (register_fonts, tracked, tw_of, fit_tracked, fit_text,
                    wrap_lines,
                    SERIF, SERIF_I, COND, COND_SB, COND_B, MONO)
import content_meta as M

BLEED = 0.125 * inch
PPI_WHITE = 0.002252          # KDP black ink on white paper, inches per page
PPI_CREAM = 0.0025

DARK = Color(0.055, 0.065, 0.078)
DARK2 = Color(0.10, 0.115, 0.135)
AMBER = Color(0.914, 0.631, 0.231)
AMBER_D = Color(0.72, 0.47, 0.14)
PAPER = Color(0.965, 0.957, 0.941)
GREY = Color(0.62, 0.64, 0.66)

BLURB = (
    "Most logbooks are built for a station that never moves. Take one to a "
    "picnic table and it starts lying to you."
)

BODY = (
    "FIELD RECORD is organized around the outing rather than the contact. "
    "Thirty deployments, four pages each: a Site Record for where you are and "
    "what you put up, two sheets of contacts in the columns a portable "
    "operator actually needs, and a debrief completed at the site. "
    "Behind them sits a field reference compiled for people operating away "
    "from mains power, and a set of station records that will outlive this "
    "volume."
)

BULLETS = [
    "US band plan and privileges, including the 60 meter allocation as revised in February 2026",
    "Activation rules for POTA, SOTA, WWFF, and the UTC day boundary that ruins them",
    "Antenna field math, coax loss, SWR tables, and power budget worksheets",
    "RF exposure limits and the evaluation every station is now required to keep",
    "Propagation, grid squares, Q signals, prosigns, phonetics, and ARRL sections",
    "Equipment registers, antenna build sheets with SWR sweep grids, and award trackers",
]


def spine_width(pages, paper="white"):
    return pages * (PPI_WHITE if paper == "white" else PPI_CREAM) * inch


def station_mark(c, gx, gy, r):
    """A mast with an inverted-V wire, radiating wavefronts from the apex.

    The feedpoint is at the apex because that is where the current maximum
    of a center-fed half wave actually is.
    """
    mast_h = r * 0.86
    ax, ay = gx, gy + mast_h                     # apex, the feedpoint
    legx, legy = r * 0.60, mast_h * 0.34

    c.saveState()
    arcs = 8
    for i in range(arcs):
        rr = r * 0.42 + (r * 1.02) * i / float(arcs - 1)
        t = i / float(arcs - 1)
        c.setStrokeColor(Color(0.914, 0.631, 0.231,
                               alpha=max(0.12, 0.92 - t * 0.80)))
        c.setLineWidth(max(0.55, 2.4 - i * 0.26))
        p = c.beginPath()
        n = 80
        a0, a1 = -14.0, 194.0
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / float(n))
            px, py = ax + rr * math.cos(a), ay + rr * math.sin(a) * 0.72
            if k == 0:
                p.moveTo(px, py)
            else:
                p.lineTo(px, py)
        c.drawPath(p, stroke=1, fill=0)

    # ground line
    c.setStrokeColor(Color(1, 1, 1, alpha=0.30))
    c.setLineWidth(0.9)
    c.line(gx - r * 1.45, gy, gx + r * 1.45, gy)

    # mast and wire
    c.setStrokeColor(Color(1, 1, 1, alpha=0.72))
    c.setLineWidth(1.3)
    c.line(gx, gy, ax, ay)
    c.setLineWidth(1.0)
    c.line(ax, ay, ax + legx, ay - legy)
    c.line(ax, ay, ax - legx, ay - legy)
    # feedpoint
    c.setFillColor(AMBER)
    c.circle(ax, ay, 3.2, stroke=0, fill=1)
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.0)
    c.circle(ax, ay, 8.0, stroke=1, fill=0)
    c.restoreState()


def grid_field(c, x, y, w, h, pitch, color, lw=0.4):
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    nx = int(w // pitch)
    ny = int(h // pitch)
    for i in range(nx + 1):
        c.line(x + i * pitch, y, x + i * pitch, y + h)
    for j in range(ny + 1):
        c.line(x, y + j * pitch, x + w, y + j * pitch)
    c.restoreState()


def dial(c, x, y, w, n=49, h=5.0, color=None, lw=0.7):
    c.saveState()
    c.setStrokeColor(color or Color(1, 1, 1, alpha=0.55))
    c.setLineWidth(lw)
    for i in range(n):
        xx = x + w * i / float(n - 1)
        hh = h if i % 6 == 0 else h * 0.45
        c.line(xx, y, xx, y + hh)
    c.line(x, y, x + w, y)
    c.restoreState()


def front_panel(c, x, y, w, h, trim_key, bleed_rect=None):
    """Draw the front cover artwork inside the given panel rect.

    bleed_rect extends the background art past the trim so nothing shows a
    seam if the guillotine wanders.
    """
    m = 0.55 * inch if w < 7 * inch else 0.75 * inch
    ix, iy, iw, ih = x + m, y + m, w - 2 * m, h - 2 * m
    bx, by, bw, bh = bleed_rect or (x, y, w, h)

    c.saveState()
    p = c.beginPath()
    p.rect(bx, by, bw, bh)
    c.clipPath(p, stroke=0, fill=0)
    grid_field(c, bx - 20, by - 20, bw + 40, bh + 40, 0.30 * inch,
               Color(1, 1, 1, alpha=0.045))
    grid_field(c, bx - 20, by - 20, bw + 40, bh + 40, 1.50 * inch,
               Color(1, 1, 1, alpha=0.085))
    station_mark(c, x + w * 0.50, y + h * 0.275, min(w, h) * 0.44)
    c.restoreState()

    # top kicker
    top = iy + ih
    dial(c, ix, top - 8, iw)
    fit_tracked(c, ix, top - 26, "PORTABLE OPERATION  ·  SITE, SIGNAL, DEBRIEF",
                COND_SB, w * 0.020, iw, 2.0, AMBER)

    # title
    size = w * 0.145
    ty = top - 26 - size * 1.02
    tracked(c, ix, ty, "FIELD", COND_B, size, size * 0.055, white)
    tracked(c, ix, ty - size * 0.93, "RECORD", COND_B, size, size * 0.055, white)
    ry = ty - size * 0.93 - size * 0.30
    c.setStrokeColor(AMBER)
    c.setLineWidth(2.2)
    c.line(ix, ry, ix + iw, ry)

    # subtitle
    ss = w * 0.036
    c.setFillColor(PAPER)
    c.setFont(SERIF_I, ss)
    c.drawString(ix, ry - ss * 1.45, M.SUBTITLE)

    # bottom band
    by = iy
    dial(c, ix, by + 30, iw)
    fit_tracked(c, ix, by + 12, "THIRTY DEPLOYMENTS  ·  FIELD REFERENCE  ·  "
                                "STATION RECORDS", COND_SB, w * 0.019, iw * 0.78,
                1.7, GREY)
    fit_tracked(c, ix + iw, by + 12, M.IMPRINT.upper(), COND, w * 0.017,
                iw * 0.20, 1.4, GREY, align="r")


def back_panel(c, x, y, w, h, pages, trim_key):
    m = 0.62 * inch if w < 7 * inch else 0.85 * inch
    ix, iy, iw, ih = x + m, y + m, w - 2 * m, h - 2 * m
    top = iy + ih

    # reserved bottom zone: barcode clear area and the imprint block
    bw, bh = 2.0 * inch, 1.2 * inch
    bx = x + w - 0.30 * inch - bw
    by = y + 0.32 * inch
    floor = by + bh + 0.22 * inch

    def measure(bs, bodys):
        t = 0.0
        t += len(wrap_lines(BLURB, SERIF_I, bs, iw)) * bs * 1.40 + bs * 0.75
        t += len(wrap_lines(BODY, SERIF, bodys, iw)) * bodys * 1.52 + bodys * 1.1
        t += bodys * 2.9
        for b in BULLETS:
            t += len(wrap_lines(b, SERIF, bodys, iw - 14)) * bodys * 1.42
            t += bodys * 0.42
        return t

    bs, bodys = w * 0.040, w * 0.0265
    room = (top - 34) - floor
    guard = 0
    while measure(bs, bodys) > room and guard < 80:
        bs *= 0.98
        bodys *= 0.98
        guard += 1

    dial(c, ix, top - 8, iw, color=Color(1, 1, 1, alpha=0.35))
    y2 = top - 34
    c.setFillColor(white)
    c.setFont(SERIF_I, bs)
    for ln in wrap_lines(BLURB, SERIF_I, bs, iw):
        c.drawString(ix, y2, ln)
        y2 -= bs * 1.40
    y2 -= bs * 0.75

    c.setFillColor(Color(0.80, 0.82, 0.84))
    c.setFont(SERIF, bodys)
    for ln in wrap_lines(BODY, SERIF, bodys, iw):
        c.drawString(ix, y2, ln)
        y2 -= bodys * 1.52
    y2 -= bodys * 1.1

    c.setStrokeColor(AMBER)
    c.setLineWidth(1.4)
    c.line(ix, y2 + bodys * 0.6, ix + iw * 0.28, y2 + bodys * 0.6)
    y2 -= bodys * 1.0
    fit_tracked(c, ix, y2, "WHAT IS IN PART ONE", COND_B, w * 0.021, iw, 1.9, AMBER)
    y2 -= bodys * 1.9

    for b in BULLETS:
        c.setFillColor(AMBER)
        c.circle(ix + 2.2, y2 + bodys * 0.32, 1.5, stroke=0, fill=1)
        c.setFillColor(Color(0.86, 0.88, 0.90))
        c.setFont(SERIF, bodys)
        for ln in wrap_lines(b, SERIF, bodys, iw - 14):
            c.drawString(ix + 12, y2, ln)
            y2 -= bodys * 1.42
        y2 -= bodys * 0.42

    # barcode clear area, bottom right of the back panel
    c.setFillColor(white)
    c.rect(bx, by, bw, bh, stroke=0, fill=1)
    tracked(c, bx + bw / 2, by + bh / 2 - 3, "ISBN BARCODE AREA", COND, 6.4, 1.2,
            Color(0.62, 0.62, 0.62), align="c")

    # imprint block, bottom left, inside the reserved zone
    mky = by + bh - 12
    fit_tracked(c, ix, mky, M.SERIES_MARK, COND_B, w * 0.020,
                bx - ix - 18, 2.6, AMBER)
    fit_tracked(c, ix, mky - 15, M.IMPRINT.upper(), COND, w * 0.017,
                bx - ix - 18, 1.4, GREY)
    fit_tracked(c, ix, mky - 28, "%d PAGES  ·  %s" % (pages, M.EDITION.upper()),
                COND, w * 0.016, bx - ix - 18, 1.2, Color(0.45, 0.47, 0.50))


def spine_panel(c, x, y, w, h, pages):
    if w < 0.20 * inch:
        return
    c.saveState()
    c.translate(x + w / 2.0, y + h / 2.0)
    c.rotate(-90)
    # title reads top to bottom when the book lies face up
    size = min(w * 0.52, 15.0)
    tracked(c, -h / 2.0 + 0.62 * inch, -size * 0.34, "FIELD RECORD", COND_B,
            size, size * 0.12, white)
    tracked(c, h / 2.0 - 0.62 * inch, -size * 0.30, M.IMPRINT.upper(), COND,
            size * 0.58, 1.3, Color(0.70, 0.72, 0.74), align="r")
    c.restoreState()
    # amber hairlines top and bottom of the spine
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.0)
    c.line(x + w * 0.30, y + h - 0.30 * inch, x + w * 0.70, y + h - 0.30 * inch)
    c.line(x + w * 0.30, y + 0.30 * inch, x + w * 0.70, y + 0.30 * inch)


def build_wrap(trim_key, trim_w, trim_h, pages, outpath):
    register_fonts()
    sw = spine_width(pages)
    W = 2 * BLEED + 2 * trim_w + sw
    H = 2 * BLEED + trim_h
    c = rl_canvas.Canvas(outpath, pagesize=(W, H),
                         initialFontName=SERIF, initialFontSize=10)
    c.setTitle("FIELD RECORD cover, %s, %d pages" % (trim_key, pages))
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # subtle vertical lift behind the front panel
    c.setFillColor(DARK2)
    c.rect(BLEED + trim_w + sw, 0, trim_w + BLEED, H, stroke=0, fill=1)

    back_panel(c, BLEED, BLEED, trim_w, trim_h, pages, trim_key)
    spine_panel(c, BLEED + trim_w, BLEED, sw, trim_h, pages)
    fx = BLEED + trim_w + sw
    front_panel(c, fx, BLEED, trim_w, trim_h, trim_key,
                bleed_rect=(fx, 0, W - fx, H))
    c.save()
    return W / inch, H / inch, sw / inch


def build_flat_front(trim_key, trim_w, trim_h, outpath):
    register_fonts()
    c = rl_canvas.Canvas(outpath, pagesize=(trim_w, trim_h),
                         initialFontName=SERIF, initialFontSize=10)
    c.setFillColor(DARK2)
    c.rect(0, 0, trim_w, trim_h, stroke=0, fill=1)
    front_panel(c, 0, 0, trim_w, trim_h, trim_key,
                bleed_rect=(0, 0, trim_w, trim_h))
    c.save()


FIELD_BULLETS = [
    "Site Record, two log sheets and a debrief for every outing",
    "Cards A, B and C on the backs, upright when the leaf stands",
    "Band edges current to the February 2026 sixty meter revision",
    "Wire lengths, SWR, power budget and RF exposure distances",
    "POTA and SOTA minimums, and the UTC day that voids them",
]

FIELD_BODY = (
    "Bound along the top so it lies dead flat on a picnic table and folds back "
    "on itself. Turn a leaf and it stands up in front of you, which is why the "
    "reference lives on the backs: a card is facing you on every page you log."
)


def field_front(c, x, y, w, h, ndep, bleed_rect=None):
    """Landscape front cover. The head is left clear for the wire punch."""
    bindclear = 0.62 * inch
    m = 0.42 * inch
    ix, iy = x + m, y + m
    iw, ih = w - 2 * m, h - m - bindclear
    bx, by, bw, bh = bleed_rect or (x, y, w, h)

    c.saveState()
    p = c.beginPath()
    p.rect(bx, by, bw, bh)
    c.clipPath(p, stroke=0, fill=0)
    grid_field(c, bx - 20, by - 20, bw + 40, bh + 40, 0.28 * inch,
               Color(1, 1, 1, alpha=0.045))
    grid_field(c, bx - 20, by - 20, bw + 40, bh + 40, 1.40 * inch,
               Color(1, 1, 1, alpha=0.085))
    station_mark(c, x + w * 0.735, y + h * 0.235, min(w, h) * 0.50)
    c.restoreState()

    top = iy + ih
    dial(c, ix, top - 7, iw)
    fit_tracked(c, ix, top - 23, "FIELD EDITION  \u00b7  %d DEPLOYMENTS  \u00b7  "
                "LIES FLAT" % ndep, COND_SB, w * 0.019, iw * 0.72, 1.9, AMBER)
    size = w * 0.098
    ty = top - 23 - size * 1.05
    tracked(c, ix, ty, "FIELD", COND_B, size, size * 0.055, white)
    tracked(c, ix, ty - size * 0.92, "RECORD", COND_B, size, size * 0.055, white)
    ry = ty - size * 0.92 - size * 0.30
    c.setStrokeColor(AMBER)
    c.setLineWidth(2.0)
    c.line(ix, ry, ix + iw * 0.60, ry)
    ss = w * 0.026
    c.setFillColor(PAPER)
    c.setFont(SERIF_I, ss)
    c.drawString(ix, ry - ss * 1.45, M.SUBTITLE)

    dial(c, ix, iy + 20, iw)
    fit_tracked(c, ix, iy + 6, "SITE  \u00b7  SIGNAL  \u00b7  DEBRIEF",
                COND_SB, w * 0.017, iw * 0.5, 1.7, GREY)
    fit_tracked(c, ix + iw, iy + 6, M.IMPRINT.upper(), COND, w * 0.015,
                iw * 0.3, 1.4, GREY, align="r")


def field_back(c, x, y, w, h, ndep, pages, bleed_rect=None):
    """Landscape back panel. Sizes are driven by panel height, not width."""
    bindclear = 0.62 * inch
    m = 0.42 * inch
    ix, iy = x + m, y + m
    iw, ih = w - 2 * m, h - m - bindclear
    top = iy + ih

    bw, bh = 2.0 * inch, 1.2 * inch
    bxx = x + w - 0.28 * inch - bw
    byy = y + 0.26 * inch

    col1 = iw * 0.505
    xr = ix + col1 + 18
    wr = iw - col1 - 18
    left_floor = iy + 40
    right_floor = byy + bh + 8

    def measure(bs, body):
        a = len(wrap_lines(BLURB, SERIF_I, bs, col1)) * bs * 1.36 + bs * 0.7
        a += len(wrap_lines(FIELD_BODY, SERIF, body, col1)) * body * 1.5
        b = body * 3.0
        for t in FIELD_BULLETS:
            b += len(wrap_lines(t, SERIF, body, wr - 12)) * body * 1.4
            b += body * 0.4
        return a, b

    bs, body = ih * 0.072, ih * 0.049
    for _ in range(90):
        a, b = measure(bs, body)
        if a <= (top - 26) - left_floor and b <= (top - 26) - right_floor:
            break
        bs *= 0.975
        body *= 0.975

    dial(c, ix, top - 7, iw, color=Color(1, 1, 1, alpha=0.35))

    # left: the pitch
    y2 = top - 26
    c.setFillColor(white)
    c.setFont(SERIF_I, bs)
    for ln in wrap_lines(BLURB, SERIF_I, bs, col1):
        c.drawString(ix, y2, ln)
        y2 -= bs * 1.36
    y2 -= bs * 0.7
    c.setFillColor(Color(0.80, 0.82, 0.84))
    c.setFont(SERIF, body)
    for ln in wrap_lines(FIELD_BODY, SERIF, body, col1):
        c.drawString(ix, y2, ln)
        y2 -= body * 1.5

    # right: what is in it
    y3 = top - 26
    c.setStrokeColor(AMBER)
    c.setLineWidth(1.2)
    c.line(xr, y3 + body * 0.9, xr + wr * 0.30, y3 + body * 0.9)
    fit_tracked(c, xr, y3 - body * 0.5, "IN THE BOOK", COND_B, body * 0.92,
                wr, 1.8, AMBER)
    y3 -= body * 2.4
    for t in FIELD_BULLETS:
        c.setFillColor(AMBER)
        c.circle(xr + 1.6, y3 + body * 0.32, 1.2, stroke=0, fill=1)
        c.setFillColor(Color(0.86, 0.88, 0.90))
        c.setFont(SERIF, body)
        for ln in wrap_lines(t, SERIF, body, wr - 12):
            c.drawString(xr + 9, y3, ln)
            y3 -= body * 1.4
        y3 -= body * 0.4

    # barcode clear area
    c.setFillColor(white)
    c.rect(bxx, byy, bw, bh, stroke=0, fill=1)
    tracked(c, bxx + bw / 2, byy + bh / 2 - 3, "ISBN BARCODE AREA", COND, 6.0, 1.1,
            Color(0.62, 0.62, 0.62), align="c")

    # imprint block, bottom left
    fit_tracked(c, ix, iy + 24, M.SERIES_MARK, COND_B, body * 0.95, col1, 2.4, AMBER)
    fit_tracked(c, ix, iy + 12, M.IMPRINT.upper(), COND, body * 0.85, col1, 1.4, GREY)
    fit_tracked(c, ix, iy + 1, "%d DEPLOYMENTS  \u00b7  %d PAGES  \u00b7  WIRE BOUND "
                "TO LIE FLAT" % (ndep, pages), COND, body * 0.80, col1, 1.2,
                Color(0.45, 0.47, 0.50))


PAPERW = Color(0.972, 0.966, 0.953)      # the light ground for weatherproof stock
LINE = Color(0.10, 0.11, 0.12)
LINE2 = Color(0.42, 0.44, 0.46)
LINE3 = Color(0.66, 0.68, 0.70)


def light_station_mark(c, gx, gy, r):
    """Line-art version of the mark for a light, low-toner cover."""
    mast_h = r * 0.86
    ax, ay = gx, gy + mast_h
    legx, legy = r * 0.60, mast_h * 0.34
    c.saveState()
    for i in range(8):
        rr = r * 0.42 + (r * 1.02) * i / 7.0
        t = i / 7.0
        c.setStrokeColor(Color(0.72, 0.47, 0.14, alpha=max(0.20, 0.95 - t * 0.78)))
        c.setLineWidth(max(0.5, 1.9 - i * 0.20))
        p = c.beginPath()
        for k in range(81):
            a = math.radians(-14.0 + 208.0 * k / 80.0)
            px, py = ax + rr * math.cos(a), ay + rr * math.sin(a) * 0.72
            p.moveTo(px, py) if k == 0 else p.lineTo(px, py)
        c.drawPath(p, stroke=1, fill=0)
    c.setStrokeColor(Color(0.10, 0.11, 0.12, alpha=0.28))
    c.setLineWidth(0.8)
    c.line(gx - r * 1.45, gy, gx + r * 1.45, gy)
    c.setStrokeColor(Color(0.10, 0.11, 0.12, alpha=0.80))
    c.setLineWidth(1.2)
    c.line(gx, gy, ax, ay)
    c.setLineWidth(0.95)
    c.line(ax, ay, ax + legx, ay - legy)
    c.line(ax, ay, ax - legx, ay - legy)
    c.setFillColor(AMBER_D)
    c.circle(ax, ay, 3.0, stroke=0, fill=1)
    c.setStrokeColor(AMBER_D)
    c.setLineWidth(1.0)
    c.circle(ax, ay, 7.5, stroke=1, fill=0)
    c.restoreState()


def _panel_geom(x, y, w, h):
    bindclear = 0.62 * inch
    m = 0.42 * inch
    return x + m, y + m, w - 2 * m, h - m - bindclear


def light_front(c, x, y, w, h, ndep, bleed_rect=None):
    ix, iy, iw, ih = _panel_geom(x, y, w, h)
    bx, by, bw, bh = bleed_rect or (x, y, w, h)
    c.saveState()
    p = c.beginPath(); p.rect(bx, by, bw, bh); c.clipPath(p, stroke=0, fill=0)
    grid_field(c, bx - 20, by - 20, bw + 40, bh + 40, 0.28 * inch,
               Color(0.10, 0.11, 0.12, alpha=0.045))
    grid_field(c, bx - 20, by - 20, bw + 40, bh + 40, 1.40 * inch,
               Color(0.10, 0.11, 0.12, alpha=0.10))
    light_station_mark(c, x + w * 0.735, y + h * 0.235, min(w, h) * 0.50)
    c.restoreState()

    top = iy + ih
    dial(c, ix, top - 7, iw, color=Color(0.10, 0.11, 0.12, alpha=0.55))
    fit_tracked(c, ix, top - 23, "FIELD EDITION  \u00b7  %d DEPLOYMENTS  \u00b7  "
                "LIES FLAT" % ndep, COND_SB, w * 0.019, iw * 0.70, 1.9, AMBER_D)
    size = w * 0.098
    ty = top - 23 - size * 1.05
    tracked(c, ix, ty, "FIELD", COND_B, size, size * 0.055, LINE)
    tracked(c, ix, ty - size * 0.92, "RECORD", COND_B, size, size * 0.055, LINE)
    ry = ty - size * 0.92 - size * 0.30
    c.setStrokeColor(AMBER_D); c.setLineWidth(2.0)
    c.line(ix, ry, ix + iw * 0.60, ry)
    ss = w * 0.026
    c.setFillColor(LINE); c.setFont(SERIF_I, ss)
    c.drawString(ix, ry - ss * 1.45, M.SUBTITLE)
    fit_tracked(c, ix, ry - ss * 3.05, M.AUTHOR.upper(), COND_B, w * 0.020,
                iw * 0.62, 2.0, LINE2)

    dial(c, ix, iy + 20, iw, color=Color(0.10, 0.11, 0.12, alpha=0.45))
    fit_tracked(c, ix, iy + 6, "SITE  \u00b7  SIGNAL  \u00b7  DEBRIEF",
                COND_SB, w * 0.017, iw * 0.5, 1.7, LINE2)
    fit_tracked(c, ix + iw, iy + 6, M.IMPRINT.upper(), COND, w * 0.015,
                iw * 0.3, 1.4, LINE2, align="r")


def light_back(c, x, y, w, h, ndep, pages):
    ix, iy, iw, ih = _panel_geom(x, y, w, h)
    top = iy + ih
    bw, bh = 2.0 * inch, 1.2 * inch
    bxx = x + w - 0.28 * inch - bw
    byy = y + 0.26 * inch
    col1 = iw * 0.505
    xr = ix + col1 + 18
    wr = iw - col1 - 18
    left_floor = iy + 40
    right_floor = byy + bh + 8

    def measure(bs, body):
        a = len(wrap_lines(BLURB, SERIF_I, bs, col1)) * bs * 1.36 + bs * 0.7
        a += len(wrap_lines(FIELD_BODY, SERIF, body, col1)) * body * 1.5
        b = body * 3.0
        for t in FIELD_BULLETS:
            b += len(wrap_lines(t, SERIF, body, wr - 12)) * body * 1.4 + body * 0.4
        return a, b

    bs, body = ih * 0.072, ih * 0.049
    for _ in range(90):
        a, b = measure(bs, body)
        if a <= (top - 26) - left_floor and b <= (top - 26) - right_floor:
            break
        bs *= 0.975; body *= 0.975

    dial(c, ix, top - 7, iw, color=Color(0.10, 0.11, 0.12, alpha=0.45))
    y2 = top - 26
    c.setFillColor(LINE); c.setFont(SERIF_I, bs)
    for ln in wrap_lines(BLURB, SERIF_I, bs, col1):
        c.drawString(ix, y2, ln); y2 -= bs * 1.36
    y2 -= bs * 0.7
    c.setFillColor(Color(0.22, 0.24, 0.26)); c.setFont(SERIF, body)
    for ln in wrap_lines(FIELD_BODY, SERIF, body, col1):
        c.drawString(ix, y2, ln); y2 -= body * 1.5

    y3 = top - 26
    c.setStrokeColor(AMBER_D); c.setLineWidth(1.2)
    c.line(xr, y3 + body * 0.9, xr + wr * 0.30, y3 + body * 0.9)
    fit_tracked(c, xr, y3 - body * 0.5, "IN THE BOOK", COND_B, body * 0.92,
                wr, 1.8, AMBER_D)
    y3 -= body * 2.4
    for t in FIELD_BULLETS:
        c.setFillColor(AMBER_D); c.circle(xr + 1.6, y3 + body * 0.32, 1.2, stroke=0, fill=1)
        c.setFillColor(Color(0.18, 0.20, 0.22)); c.setFont(SERIF, body)
        for ln in wrap_lines(t, SERIF, body, wr - 12):
            c.drawString(xr + 9, y3, ln); y3 -= body * 1.4
        y3 -= body * 0.4

    c.setStrokeColor(LINE3); c.setLineWidth(0.6)
    c.rect(bxx, byy, bw, bh, stroke=1, fill=0)
    tracked(c, bxx + bw / 2, byy + bh / 2 - 3, "ISBN BARCODE AREA", COND, 6.0, 1.1,
            LINE3, align="c")

    fit_tracked(c, ix, iy + 26, M.AUTHOR.upper(), COND_B, body * 1.05, col1, 2.0, LINE)
    fit_tracked(c, ix, iy + 14, M.SERIES_MARK, COND_B, body * 0.85, col1, 2.2, AMBER_D)
    fit_tracked(c, ix, iy + 3, "%s  \u00b7  %d DEPLOYMENTS  \u00b7  %d PAGES  "
                "\u00b7  WIRE BOUND" % (M.IMPRINT.upper(), ndep, pages),
                COND, body * 0.76, col1, 1.2, LINE2)


def inside_front(c, x, y, w, h, ndep):
    """Owner block, how the book works, and the calling channels."""
    ix, iy, iw, ih = _panel_geom(x, y, w, h)
    top = iy + ih

    def head(hx, hy, hw, t, right=None):
        tracked(c, hx, hy - 6.5, t.upper(), COND_B, 7.2, 1.2, LINE)
        if right:
            fit_tracked(c, hx + hw, hy - 6.5, right.upper(), COND, 5.8,
                        hw * 0.5, 0.8, LINE2, align="r")
        c.setStrokeColor(LINE); c.setLineWidth(0.9)
        c.line(hx, hy - 9.4, hx + hw, hy - 9.4)
        return hy - 19.0

    def field(fx, fy, fw, label):
        fit_tracked(c, fx, fy + 2.6, label.upper(), COND_SB, 5.6, fw - 2, 0.85, LINE2)
        c.setStrokeColor(LINE3); c.setLineWidth(0.55)
        c.line(fx, fy - 6.4, fx + fw, fy - 6.4)

    def row(fx, fy, fw, labels, gap=8):
        n = len(labels); avail = fw - gap * (n - 1); tot = sum(q[1] for q in labels)
        cx = fx
        for lab, wt in labels:
            ww = avail * wt / tot
            field(cx, fy, ww, lab)
            cx += ww + gap
        return fy - 6.4

    col = iw * 0.52
    xr = ix + col + 20
    wr = iw - col - 20

    ya = head(ix, top, col, "This book belongs to", right="please write it in")
    ya = row(ix, ya, col, [("Name", 1.6), ("Callsign", 1.0)])
    ya = row(ix, ya - 13, col, [("Grid", 0.8), ("Email", 1.8), ("Phone", 1.0)])
    ya = row(ix, ya - 13, col, [("Club or group", 1.4), ("Volume no.", 0.6),
                                ("Started", 0.8), ("Filled", 0.8)])
    ya -= 14
    ya = head(ix, ya, col, "If found", right="")
    c.setFillColor(Color(0.22, 0.24, 0.26)); c.setFont(SERIF_I, 7.4)
    for ln in wrap_lines("This is a working logbook. It has no cash value and "
                         "considerable sentimental value. The operator above "
                         "would be very glad to hear from you.", SERIF_I, 7.4, col):
        c.drawString(ix, ya, ln); ya -= 10.2

    yb = head(xr, top, wr, "How this book works")
    steps = [
        ("Fronts", "You write on them. Site Record, then two log sheets."),
        ("Backs", "Cards A, B and C. Never write on a back."),
        ("The flip", "Turn a leaf and it stands up. The card on its back "
                     "faces you while you work the page below."),
        ("Times", "UTC, every field, every page. Write the date at the top "
                  "of each sheet and rule a line at the rollover."),
        ("Debrief", "Bottom of sheet B. Fill it at the site, not at home."),
    ]
    c.setFont(SERIF, 7.2)
    for k, v in steps:
        tracked(c, xr, yb, k.upper(), COND_B, 6.4, 1.0, AMBER_D)
        kw = tw_of(k.upper(), COND_B, 6.4, 1.0) + 9
        c.setFillColor(Color(0.18, 0.20, 0.22)); c.setFont(SERIF, 7.2)
        yy = yb
        for ln in wrap_lines(v, SERIF, 7.2, wr - kw):
            c.drawString(xr + kw, yy, ln); yy -= 9.6
        yb = yy - 4.5

    yb -= 6
    yb = head(xr, yb, wr, "Calling channels", right="MHz")
    ch = [("2 m FM simplex", "146.520"), ("70 cm FM simplex", "446.000"),
          ("6 m SSB", "50.125"), ("2 m SSB", "144.200"),
          ("POTA SSB, 40 / 20", "7.185 / 14.285"),
          ("POTA CW, 40 / 20", "7.032 / 14.032")]
    for k, v in ch:
        c.setFillColor(Color(0.18, 0.20, 0.22)); c.setFont(SERIF, 7.0)
        c.drawString(xr, yb, k)
        tracked(c, xr + wr, yb, v, MONO, 7.0, 0, LINE, align="r")
        yb -= 10.0

    # ---- lower half: the two things worth having on the stiffest surface
    mid = min(ya, yb) - 16
    c.setStrokeColor(LINE); c.setLineWidth(0.9)
    c.line(ix, mid + 8, ix + iw, mid + 8)

    yc = head(ix, mid, col, "Pre-deployment", right="")
    checks = [
        "Callsign, park or summit reference, and access hours written down",
        "Radio clock set to UTC and verified against a known source",
        "Battery charged, charge state actually checked, fused at the post",
        "Wire, transformer, throw line, weight, and a second throw line",
        "Water, layers, sun and insect protection, and a charged phone",
        "Somebody knows where you are going and when you will be back",
    ]
    c.setFont(SERIF, 7.0)
    for t in checks:
        c.setStrokeColor(LINE2); c.setLineWidth(0.55)
        c.rect(ix + 0.5, yc - 0.8, 6.2, 6.2, stroke=1, fill=0)
        c.setFillColor(Color(0.18, 0.20, 0.22)); c.setFont(SERIF, 7.0)
        lines = wrap_lines(t, SERIF, 7.0, col - 13)
        for ln in lines:
            c.drawString(ix + 13, yc, ln); yc -= 9.4
        yc -= 2.0

    yd = head(xr, mid, wr, "UTC to local", right="* is the day before")
    rows = [("UTC", "00", "02", "12", "16", "18", "20", "22", "23"),
            ("EDT", "20*", "22*", "08", "12", "14", "16", "18", "19"),
            ("CDT", "19*", "21*", "07", "11", "13", "15", "17", "18"),
            ("MDT", "18*", "20*", "06", "10", "12", "14", "16", "17"),
            ("PDT", "17*", "19*", "05", "09", "11", "13", "15", "16")]
    cw = wr / 9.0
    for ri, r in enumerate(rows):
        for ci, v in enumerate(r):
            fnt = COND_B if (ri == 0 or ci == 0) else MONO
            fit_text(c, xr + cw * (ci + 0.5), yd, v, fnt, 6.8, cw - 2,
                     LINE, align="c")
        c.setStrokeColor(LINE3); c.setLineWidth(0.45)
        c.line(xr, yd - 3.2, xr + wr, yd - 3.2)
        yd -= 11.0
    yd -= 4
    c.setFillColor(Color(0.30, 0.32, 0.34)); c.setFont(SERIF_I, 6.6)
    for ln in ["Winter standard time is one hour further back. The Zulu day",
               "rolls over mid evening in North America, which is what voids",
               "more activations than any other rule in the book."]:
        c.drawString(xr, yd, ln); yd -= 8.8


def inside_back(c, x, y, w, h, ndep):
    """About the book, the compiler's credit, and space for volume notes."""
    ix, iy, iw, ih = _panel_geom(x, y, w, h)
    top = iy + ih
    col = iw * 0.52
    xr = ix + col + 20
    wr = iw - col - 20

    def head(hx, hy, hw, t, right=None):
        tracked(c, hx, hy - 6.5, t.upper(), COND_B, 7.2, 1.2, LINE)
        if right:
            fit_tracked(c, hx + hw, hy - 6.5, right.upper(), COND, 5.8,
                        hw * 0.5, 0.8, LINE2, align="r")
        c.setStrokeColor(LINE); c.setLineWidth(0.9)
        c.line(hx, hy - 9.4, hx + hw, hy - 9.4)
        return hy - 19.0

    ya = head(ix, top, col, "About this book")
    c.setFont(SERIF, 7.3)
    for para in M.ABOUT:
        c.setFillColor(Color(0.18, 0.20, 0.22))
        for ln in wrap_lines(para, SERIF, 7.3, col):
            c.drawString(ix, ya, ln); ya -= 10.0
        ya -= 5
    ya -= 6
    c.setStrokeColor(AMBER_D); c.setLineWidth(1.2)
    c.line(ix, ya + 4, ix + col * 0.3, ya + 4)
    ya -= 8
    tracked(c, ix, ya, M.AUTHOR.upper(), COND_B, 8.2, 2.0, LINE)
    ya -= 11
    fit_tracked(c, ix, ya, "COMPILED, WRITTEN AND SET BY THE AUTHOR", COND,
                6.0, col, 1.0, LINE2)
    ya -= 16
    fit_tracked(c, ix, ya, M.SERIES_MARK, COND_B, 6.6, col, 2.4, AMBER_D)
    ya -= 10
    fit_tracked(c, ix, ya, "%s  \u00b7  %s  \u00b7  ISBN 000-0-0000000-0-0"
                % (M.IMPRINT.upper(), M.YEAR), COND, 5.8, col, 1.4, LINE2)
    ya -= 22
    tracked(c, ix, ya, "WHERE PART ONE COMES FROM", COND_B, 6.6, 1.1, LINE)
    ya -= 11
    c.setFillColor(Color(0.30, 0.32, 0.34)); c.setFont(SERIF, 6.6)
    for ln in ["47 CFR Part 97 and ARRL allocation and section data. The FCC",
               "orders on 60 meters, effective 13 February 2026, and on HF",
               "symbol rate limits. POTA and SOTA program rules. FCC OET",
               "Bulletin 65 for RF exposure.",
               "",
               "Rules change. The operator, not the book, is responsible for",
               "lawful operation. Nothing here is legal advice, engineering",
               "certification, or a substitute for your own exposure evaluation."]:
        c.drawString(ix, ya, ln); ya -= 9.0

    yb = head(xr, top, wr, "This volume", right="fill in when it is full")
    for lab in [("Volume number", 0.8), ("First deployment", 1.2),
                ("Last deployment", 1.2)]:
        pass
    def field(fx, fy, fw, label):
        fit_tracked(c, fx, fy + 2.6, label.upper(), COND_SB, 5.6, fw - 2, 0.85, LINE2)
        c.setStrokeColor(LINE3); c.setLineWidth(0.55)
        c.line(fx, fy - 6.4, fx + fw, fy - 6.4)
    half = (wr - 10) / 2.0
    field(xr, yb, half, "Volume number")
    field(xr + half + 10, yb, half, "Callsign used")
    yb -= 20
    field(xr, yb, half, "First deployment, date")
    field(xr + half + 10, yb, half, "Last deployment, date")
    yb -= 20
    field(xr, yb, half, "Total QSOs")
    field(xr + half + 10, yb, half, "Parks and summits")
    yb -= 24
    yb = head(xr, yb, wr, "Notes on this volume")
    n = max(3, int((yb - iy - 6) // 12.5))
    rh = (yb - iy - 6) / float(n)
    c.setStrokeColor(LINE3); c.setLineWidth(0.5)
    for i in range(n):
        yy = yb - (i + 1) * rh + 2
        c.line(xr, yy, xr + wr, yy)


# --------------------------------------------------------------------------
# Personal edition, 8.5 x 11 portrait, printed on the same desktop printer as
# the interior. A desktop printer cannot bleed, so the dark ground is an inset
# panel on a white sheet rather than a full-bleed field.
# --------------------------------------------------------------------------

P_INSET = 0.35 * inch

P_BLURB = (
    "A logbook for a station that is carried in, assembled on site, and taken "
    "down the same day."
)

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
         "eighty", "ninety"]


def _words(n):
    """A small count in words, the way the cover has always said it."""
    n = int(n)
    if 0 <= n < 20:
        return _ONES[n]
    if n < 100:
        t, o = divmod(n, 10)
        return _TENS[t] + ("-" + _ONES[o] if o else "")
    return str(n)


def _list_names(names):
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " and " + names[-1]


def personal_back_copy(ndep, sec=None, place="", radios=(), ref_tags=()):
    """The back cover copy for the book that was actually built.

    The cover must never describe parts the operator left out, and it must
    name their state and their radios, not the author's. sec is the Sections
    object (None means everything), radios is a list of display names such as
    "Icom IC-7100", ref_tags the Part One section tags that are in.
    """
    on = (lambda k: True) if sec is None else sec.on
    tags = set(ref_tags or ())
    if sec is None:
        tags = {"BANDS", "ANT", "POWER", "SAFE", "PROP", "GRID", "PHON",
                "SECT", "AWARDS", "OPS"}
    has_log, has_p1, has_p3 = on("part_two"), on("part_one"), on("part_three")

    body = "FIELD RECORD is organized around the outing rather than the contact. "
    if has_log:
        body += ("%s deployments, four pages each: a Site Record completed "
                 "before the first call, two sheets of contacts in the columns "
                 "portable operation requires, and a debrief written at the "
                 "site. " % _words(ndep).capitalize())
    else:
        body += ("This copy is the field reference on its own, for an operator "
                 "who keeps the log elsewhere. ")
    if has_p1:
        body += ("Part One is a field reference compiled from primary sources "
                 "for operators working away from mains power. ")
    if has_p3:
        body += ("Part Three holds the station records that carry forward from "
                 "one volume to the next.")
    body = body.strip()

    bullets = []
    if has_p1:
        if "BANDS" in tags:
            bullets.append("US band plan and privileges in color, including "
                           "the 60 meter allocation as revised in February 2026")
        local = []
        if on("repeaters") and place:
            local.append("%s repeaters and nets" % place)
        names = _list_names(list(radios))
        if on("radios") and names:
            local.append("%s for the %s" % (
                "a quick reference card" if len(list(radios)) == 1
                else "quick reference cards", names))
        if local:
            bullets.append(", and ".join(local) if len(local) == 2
                           else local[0])
        if "ANT" in tags or "POWER" in tags:
            bullets.append("Antenna field math, coax loss, SWR tables, and "
                           "power budget worksheets")
        if "SAFE" in tags:
            bullets.append("RF exposure limits and the station evaluation "
                           "required of every licensee")
        if tags & {"PROP", "GRID", "PHON", "SECT"}:
            bullets.append("Propagation indices, grid squares, Q signals, "
                           "prosigns, phonetics, and ARRL sections")
        if "AWARDS" in tags:
            bullets.append("Activation requirements for POTA, SOTA and WWFF, "
                           "keyed to the UTC day")

    meta = ("%d DEPLOYMENTS" % ndep) if has_log else "FIELD REFERENCE"
    return dict(blurb=P_BLURB, body=body, bullets=bullets,
                part_one=bool(has_p1 and bullets), meta=meta)


def _p_panel(pw, ph):
    """Inset panel rect for a portrait sheet of pw x ph."""
    return P_INSET, P_INSET, pw - 2 * P_INSET, ph - 2 * P_INSET


def _p_ground(c, x, y, w, h, shade=DARK2):
    c.saveState()
    c.setFillColor(shade)
    c.rect(x, y, w, h, stroke=0, fill=1)
    p = c.beginPath()
    p.rect(x, y, w, h)
    c.clipPath(p, stroke=0, fill=0)
    grid_field(c, x - 20, y - 20, w + 40, h + 40, 0.28 * inch,
               Color(1, 1, 1, alpha=0.045))
    grid_field(c, x - 20, y - 20, w + 40, h + 40, 1.40 * inch,
               Color(1, 1, 1, alpha=0.085))
    return c


def personal_front(c, pw, ph, ndep, byline=None):
    """The front cover. `byline` is whose book this copy is.

    FIELD RECORD is written by one operator and carried by another. The cover
    belongs to whoever is filling it in, so their byline goes here and the
    author's credit stays on the copyright page and in the PDF metadata.
    Without a byline this falls back to the author, which is the right answer
    for the author's own copy and for an unconfigured build.
    """
    x, y, w, h = _p_panel(pw, ph)
    m = 0.62 * inch
    ix, iy, iw, ih = x + m, y + m, w - 2 * m, h - 2 * m

    _p_ground(c, x, y, w, h)
    station_mark(c, x + w * 0.50, y + h * 0.205, w * 0.385)
    c.restoreState()

    # thin amber keyline just inside the panel edge
    c.setStrokeColor(Color(0.914, 0.631, 0.231, alpha=0.55))
    c.setLineWidth(0.8)
    c.rect(x + 8, y + 8, w - 16, h - 16, stroke=1, fill=0)

    top = iy + ih
    dial(c, ix, top - 8, iw)
    fit_tracked(c, ix, top - 26, "PORTABLE OPERATION  ·  SITE, SIGNAL, "
                "DEBRIEF", COND_SB, 10.6, iw, 2.2, AMBER)

    size = w * 0.150
    ty = top - 26 - size * 1.05
    tracked(c, ix, ty, "FIELD", COND_B, size, size * 0.055, white)
    tracked(c, ix, ty - size * 0.93, "RECORD", COND_B, size, size * 0.055, white)
    ry = ty - size * 0.93 - size * 0.30
    c.setStrokeColor(AMBER)
    c.setLineWidth(2.4)
    c.line(ix, ry, ix + iw, ry)

    ss = w * 0.038
    c.setFillColor(PAPER)
    c.setFont(SERIF_I, ss)
    c.drawString(ix, ry - ss * 1.45, M.SUBTITLE)

    # byline sits above the foot rule, clear of the mark
    byy = iy + 62
    fit_tracked(c, ix, byy, (byline or M.AUTHOR).upper(), COND_B, 12.0,
                iw * 0.80, 2.6, white)
    c.setStrokeColor(Color(1, 1, 1, alpha=0.35))
    c.setLineWidth(0.8)
    c.line(ix, byy - 8, ix + iw * 0.26, byy - 8)

    dial(c, ix, iy + 30, iw)
    fit_tracked(c, ix, iy + 12, "%d DEPLOYMENTS  ·  FIELD REFERENCE  ·  "
                "STATION RECORDS" % ndep, COND_SB, 9.6, iw * 0.76, 1.8, GREY)
    fit_tracked(c, ix + iw, iy + 12, M.IMPRINT.upper(), COND, 8.8, iw * 0.22,
                1.4, GREY, align="r")


def personal_back(c, pw, ph, ndep, pages, byline=None, copy=None):
    cp = copy or personal_back_copy(ndep)
    x, y, w, h = _p_panel(pw, ph)
    m = 0.62 * inch
    ix, iy, iw, ih = x + m, y + m, w - 2 * m, h - 2 * m
    top = iy + ih

    _p_ground(c, x, y, w, h, shade=DARK)
    c.restoreState()
    c.setStrokeColor(Color(0.914, 0.631, 0.231, alpha=0.40))
    c.setLineWidth(0.8)
    c.rect(x + 8, y + 8, w - 16, h - 16, stroke=1, fill=0)

    floor = iy + 88
    bs, body = 17.0, 11.4

    def measure(bs, body):
        t = len(wrap_lines(cp['blurb'], SERIF_I, bs, iw)) * bs * 1.38 + bs * 0.85
        t += len(wrap_lines(cp['body'], SERIF, body, iw)) * body * 1.52 + body * 1.3
        t += body * 3.0 if cp['part_one'] else 0
        for b in cp['bullets']:
            t += len(wrap_lines(b, SERIF, body, iw - 14)) * body * 1.42
            t += body * 0.45
        return t

    for _ in range(90):
        if measure(bs, body) <= (top - 34) - floor:
            break
        bs *= 0.98
        body *= 0.98

    dial(c, ix, top - 8, iw, color=Color(1, 1, 1, alpha=0.35))
    y2 = top - 34
    c.setFillColor(white)
    c.setFont(SERIF_I, bs)
    for ln in wrap_lines(cp['blurb'], SERIF_I, bs, iw):
        c.drawString(ix, y2, ln)
        y2 -= bs * 1.38
    y2 -= bs * 0.85

    c.setFillColor(Color(0.80, 0.82, 0.84))
    c.setFont(SERIF, body)
    for ln in wrap_lines(cp['body'], SERIF, body, iw):
        c.drawString(ix, y2, ln)
        y2 -= body * 1.52
    y2 -= body * 1.3

    if cp['part_one']:
        c.setStrokeColor(AMBER)
        c.setLineWidth(1.4)
        c.line(ix, y2 + body * 0.7, ix + iw * 0.26, y2 + body * 0.7)
        y2 -= body * 0.9
        fit_tracked(c, ix, y2, "IN PART ONE", COND_B, body * 0.94, iw, 2.0, AMBER)
        y2 -= body * 2.1

    for b in cp['bullets']:
        c.setFillColor(AMBER)
        c.circle(ix + 2.2, y2 + body * 0.32, 1.5, stroke=0, fill=1)
        c.setFillColor(Color(0.86, 0.88, 0.90))
        c.setFont(SERIF, body)
        for ln in wrap_lines(b, SERIF, body, iw - 14):
            c.drawString(ix + 12, y2, ln)
            y2 -= body * 1.42
        y2 -= body * 0.45

    # the mark again, quietly, in whatever room the copy leaves
    gap = (y2 + body) - (iy + 78)
    if gap > 1.4 * inch:
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        r = min(w * 0.30, gap * 0.46)
        station_mark(c, x + w * 0.50, iy + 78 + gap * 0.22, r)
        c.restoreState()

    # foot: author, license, imprint
    dial(c, ix, iy + 66, iw, color=Color(1, 1, 1, alpha=0.28))
    fit_tracked(c, ix, iy + 48, (byline or M.AUTHOR).upper(), COND_B, 11.0, iw * 0.62,
                2.4, white)
    fit_tracked(c, ix + iw, iy + 48, M.SERIES_MARK, COND_B, 10.0, iw * 0.34,
                2.6, AMBER, align="r")
    c.setFillColor(Color(0.70, 0.72, 0.74))
    c.setFont(SERIF, 8.6)
    lic = ("Released under Creative Commons Attribution, NonCommercial, "
           "ShareAlike 4.0 International. Not for sale.")
    yy = iy + 32
    for ln in wrap_lines(lic, SERIF, 8.6, iw):
        c.drawString(ix, yy, ln)
        yy -= 10.4
    fit_tracked(c, ix, iy + 4, "%s  ·  %s  ·  %s  ·  "
                "%d PAGES" % (M.IMPRINT.upper(), M.EDITION.upper(), cp['meta'], pages),
                COND, 8.4, iw, 1.3, Color(0.45, 0.47, 0.50))


def build_field_cover(ndep, pages, outpath, trim_w=8.5 * inch, trim_h=5.5 * inch,
                      weatherproof=True):
    """Wire-o cover, four panels in printing order and no spine.

    Page 1 outside front, 2 inside front, 3 inside back, 4 outside back.
    Weatherproof mode uses a light ground because a full bleed of solid dark
    toner is the first thing to craze on a coated synthetic sheet.
    """
    register_fonts()
    W = trim_w + 2 * BLEED
    H = trim_h + 2 * BLEED
    c = rl_canvas.Canvas(outpath, pagesize=(W, H),
                         initialFontName=SERIF, initialFontSize=10)
    c.setTitle("FIELD RECORD field edition cover, %d deployments" % ndep)
    c.setAuthor(M.AUTHOR)

    ground = PAPERW if weatherproof else DARK2
    for panel in ("front", "inside_front", "inside_back", "back"):
        c.setFillColor(ground if weatherproof else
                       (DARK2 if panel == "front" else DARK))
        c.rect(0, 0, W, H, stroke=0, fill=1)
        if panel == "front":
            if weatherproof:
                light_front(c, BLEED, BLEED, trim_w, trim_h, ndep,
                            bleed_rect=(0, 0, W, H))
            else:
                field_front(c, BLEED, BLEED, trim_w, trim_h, ndep,
                            bleed_rect=(0, 0, W, H))
        elif panel == "inside_front":
            inside_front(c, BLEED, BLEED, trim_w, trim_h, ndep)
        elif panel == "inside_back":
            inside_back(c, BLEED, BLEED, trim_w, trim_h, ndep)
        else:
            if weatherproof:
                light_back(c, BLEED, BLEED, trim_w, trim_h, ndep, pages)
            else:
                field_back(c, BLEED, BLEED, trim_w, trim_h, ndep, pages)
        c.showPage()
    c.save()
    return W / inch, H / inch


if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else "out"
    specs = [("6x9", 6.0 * inch, 9.0 * inch, int(sys.argv[2])),
             ("8.5x11", 8.5 * inch, 11.0 * inch, int(sys.argv[3]))]
    for key, tw, th, pages in specs:
        k = key.replace(".", "_")
        wrap = os.path.join(outdir, "FieldRecord_cover_%s_%dpp.pdf" % (k, pages))
        W, H, S = build_wrap(key, tw, th, pages, wrap)
        flat = os.path.join(outdir, "FieldRecord_frontcover_%s.pdf" % k)
        build_flat_front(key, tw, th, flat)
        print("%-8s  wrap %.4f x %.4f in   spine %.4f in   -> %s"
              % (key, W, H, S, os.path.basename(wrap)))
