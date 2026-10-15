# -*- coding: utf-8 -*-
"""FIELD RECORD - print layout engine.

A small book-composition layer over ReportLab's canvas. Everything is
placed in absolute coordinates so page order, page count, and recto/verso
handedness stay deterministic, which is what print-on-demand requires.
"""
import os
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.path.join(HERE, "assets", "fonts")

SERIF = "PlexSerif"
SERIF_I = "PlexSerif-I"
SERIF_B = "PlexSerif-B"
SANS = "PlexSans"
SANS_SB = "PlexSans-SB"
SANS_B = "PlexSans-B"
COND = "PlexCond"
COND_SB = "PlexCond-SB"
COND_B = "PlexCond-B"
MONO = "PlexMono"
MONO_SB = "PlexMono-SB"

_FONTS = {
    SERIF: "IBMPlexSerif-Regular.ttf",
    SERIF_I: "IBMPlexSerif-Italic.ttf",
    SERIF_B: "IBMPlexSerif-SemiBold.ttf",
    SANS: "IBMPlexSans-Regular.ttf",
    SANS_SB: "IBMPlexSans-SemiBold.ttf",
    SANS_B: "IBMPlexSans-Bold.ttf",
    COND: "IBMPlexSansCondensed-Regular.ttf",
    COND_SB: "IBMPlexSansCondensed-SemiBold.ttf",
    COND_B: "IBMPlexSansCondensed-Bold.ttf",
    MONO: "IBMPlexMono-Regular.ttf",
    MONO_SB: "IBMPlexMono-SemiBold.ttf",
}


def register_fonts():
    for name, fn in _FONTS.items():
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONTDIR, fn)))
    pdfmetrics.registerFontFamily(SERIF, normal=SERIF, bold=SERIF_B, italic=SERIF_I,
                                  boldItalic=SERIF_B)
    pdfmetrics.registerFontFamily(SANS, normal=SANS, bold=SANS_B, italic=SANS,
                                  boldItalic=SANS_B)
    pdfmetrics.registerFontFamily(COND, normal=COND, bold=COND_B, italic=COND,
                                  boldItalic=COND_B)
    pdfmetrics.registerFontFamily(MONO, normal=MONO, bold=MONO_SB, italic=MONO,
                                  boldItalic=MONO_SB)


# ---------------------------------------------------------------- ink values
INK = black
G15 = Color(0.85, 0.85, 0.85)
G25 = Color(0.75, 0.75, 0.75)
G35 = Color(0.65, 0.65, 0.65)
G50 = Color(0.50, 0.50, 0.50)
G70 = Color(0.30, 0.30, 0.30)
TINT_HEAD = Color(0.86, 0.86, 0.86)
TINT_ZEBRA = Color(0.945, 0.945, 0.945)
TINT_BOX = Color(0.925, 0.925, 0.925)

W_HAIR = 0.35
W_RULE = 0.5
W_MED = 0.8
W_HEAVY = 1.4


# ---------------------------------------------------------------- color
SLATE = Color(0.106, 0.165, 0.220)     # header ink, a deep instrument blue
SLATE_MID = Color(0.259, 0.353, 0.427)
SLATE_LT = Color(0.855, 0.886, 0.910)
SLATE_PALE = Color(0.957, 0.969, 0.976)
AMBER = Color(0.780, 0.482, 0.129)     # the accent, a panel lamp
AMBER_LT = Color(0.965, 0.902, 0.804)
RED = Color(0.647, 0.180, 0.180)
GREEN = Color(0.184, 0.451, 0.310)

# One hue per band, ordered by wavelength. Used by the band chart, the
# deployment tally and anywhere a band needs to be picked out at a glance.
BAND_COLORS = {
    "160": Color(0.361, 0.286, 0.545), "80": Color(0.180, 0.353, 0.616),
    "60": Color(0.106, 0.478, 0.549),
    "40": Color(0.145, 0.510, 0.325), "30": Color(0.408, 0.588, 0.208),
    "20": Color(0.741, 0.588, 0.129), "17": Color(0.831, 0.494, 0.125),
    "15": Color(0.741, 0.318, 0.098), "12": Color(0.643, 0.208, 0.208),
    "10": Color(0.588, 0.161, 0.373), "6": Color(0.286, 0.404, 0.686),
    "2": Color(0.153, 0.541, 0.494), "1.25": Color(0.318, 0.478, 0.588),
    "70cm": Color(0.451, 0.361, 0.243),
}


class ColorMode:
    """Full color is a build flag, so the same source makes a color book
    for a desktop printer and a black-only book for a trade press."""
    on = False


CLR = ColorMode()


def set_color(on=True):
    CLR.on = bool(on)


def band_ink():
    """Fill for the solid identification band at the head of a record page."""
    return SLATE if CLR.on else INK


def accent():
    return AMBER if CLR.on else G50


def rule_ink():
    return SLATE_MID if CLR.on else G70


def band_color(key):
    return BAND_COLORS.get(str(key), SLATE_MID) if CLR.on else G50


class InkMode:
    """Toner coverage policy.

    Weatherproof stock (Rite in the Rain and the synthetic equivalents) is a
    coated sheet: toner fuses to the coating rather than soaking into fibre, so
    large solid areas are the first thing to craze when a wet sheet is flexed
    or abraded. Weatherproof mode keeps every structural line and drops the
    solid fills, which also cuts toner cost on a long run.
    """
    weatherproof = False


INKM = InkMode()


def set_ink(weatherproof=False):
    INKM.weatherproof = bool(weatherproof)


def head_fill():
    if INKM.weatherproof:
        return None
    return SLATE_LT if CLR.on else TINT_HEAD


def zebra_fill():
    if INKM.weatherproof:
        return None
    return SLATE_PALE if CLR.on else TINT_ZEBRA


def box_fill():
    if INKM.weatherproof:
        return None
    return AMBER_LT if CLR.on else TINT_BOX


# ---------------------------------------------------------------- geometry
class Trim:
    """A trim size plus its binding behavior.

    bind_top=True describes a wire-o or coil book bound along the top edge.
    Its leaves flip up, so the back of every leaf is printed head to foot
    (short-edge duplex) and carries its binding margin at the foot of the
    reading frame rather than the head.
    """

    def __init__(self, key, w_in, h_in, inside, outside, top, bottom,
                 prose_indent, log_rows, log_row_h, base, lead,
                 bind_top=False, fs=None):
        self.key = key
        self.W = w_in * inch
        self.H = h_in * inch
        self.inside = inside * inch      # side-bound: gutter. top-bound: bind
        self.outside = outside * inch    # side-bound: fore edge. top-bound: sides
        self.top = top * inch
        self.bottom = bottom * inch
        self.prose_indent = prose_indent * inch
        self.log_rows = log_rows
        self.log_row_h = log_row_h * inch
        self.base = base
        self.lead = lead
        self.bind_top = bind_top
        self.fs = fs if fs is not None else (1.0 if key == '6x9' else 1.26)

    @property
    def tw(self):
        return self.W - self.inside - self.outside

    @property
    def th(self):
        return self.H - self.top - self.bottom


TRIMS = {
    "6x9": Trim("6x9", 6.0, 9.0, inside=0.75, outside=0.50, top=0.62, bottom=0.62,
                prose_indent=0.0, log_rows=22, log_row_h=0.300, base=8.9, lead=12.6),
    "8.5x11": Trim("8.5x11", 8.5, 11.0, inside=0.875, outside=0.625, top=0.72, bottom=0.72,
                   prose_indent=1.55, log_rows=26, log_row_h=0.320, base=9.6, lead=14.0),
    # Field edition: half letter landscape, wire-o along the top edge.
    # inside = binding margin at the bound edge, outside = the three free edges.
    "field": Trim("field", 8.5, 5.5, inside=0.58, outside=0.40, top=0.58, bottom=0.40,
                  prose_indent=3.20, log_rows=16, log_row_h=0.225, base=8.2, lead=11.5,
                  bind_top=True, fs=0.92),
    # candidate trims for the print shop, all wire-o along the head
    "L8x55": Trim("L8x55", 8.0, 5.5, inside=0.58, outside=0.40, top=0.58, bottom=0.40,
                  prose_indent=2.90, log_rows=16, log_row_h=0.225, base=8.1, lead=11.4,
                  bind_top=True, fs=0.92),
    "L9x6": Trim("L9x6", 9.0, 6.0, inside=0.60, outside=0.42, top=0.60, bottom=0.42,
                 prose_indent=3.40, log_rows=18, log_row_h=0.240, base=8.5, lead=12.0,
                 bind_top=True, fs=1.00),
    "P55x8": Trim("P55x8", 5.5, 8.0, inside=0.58, outside=0.40, top=0.58, bottom=0.40,
                  prose_indent=0.30, log_rows=22, log_row_h=0.250, base=8.1, lead=11.6,
                  bind_top=True, fs=0.92),
    "P6x9": Trim("P6x9", 6.0, 9.0, inside=0.60, outside=0.42, top=0.60, bottom=0.42,
                 prose_indent=0.40, log_rows=25, log_row_h=0.260, base=8.5, lead=12.2,
                 bind_top=True, fs=1.00),
    # Personal edition: plain letter, duplex long edge, wide inside margin so
    # the block can be three-hole punched for a binder.
    "personal": Trim("personal", 8.5, 11.0, inside=0.90, outside=0.50,
                     top=0.65, bottom=0.65, prose_indent=1.30,
                     log_rows=26, log_row_h=0.315, base=9.4, lead=13.6,
                     fs=1.22),
}


def is_landscape(t):
    return t.W > t.H


# ---------------------------------------------------------------- text utils
def tracked(c, x, y, text, font, size, tracking=0.0, fill=INK, align="l"):
    """Draw letterspaced text. align: l, c, r (x is the reference edge)."""
    w = pdfmetrics.stringWidth(text, font, size) + tracking * max(0, len(text) - 1)
    if align == "c":
        x -= w / 2.0
    elif align == "r":
        x -= w
    c.saveState()
    c.setFillColor(fill)
    to = c.beginText(x, y)
    to.setFont(font, size)
    to.setCharSpace(tracking)
    to.textOut(text)
    c.drawText(to)
    c.restoreState()
    return w


def tw_of(text, font, size, tracking=0.0):
    return pdfmetrics.stringWidth(text, font, size) + tracking * max(0, len(text) - 1)


def fit_text(c, x, y, text, font, size, maxw, fill=INK, align="l"):
    """Shrink until it fits, then draw."""
    s = size
    while s > 4.0 and pdfmetrics.stringWidth(text, font, s) > maxw:
        s -= 0.2
    c.saveState()
    c.setFont(font, s)
    c.setFillColor(fill)
    w = pdfmetrics.stringWidth(text, font, s)
    if align == "c":
        x -= w / 2.0
    elif align == "r":
        x -= w
    c.drawString(x, y, text)
    c.restoreState()
    return s


def fit_tracked(c, x, y, text, font, size, maxw, tracking=0.0, fill=INK, align="l"):
    """Tracked text that shrinks (then loosens tracking away) until it fits."""
    s, tr = size, tracking
    while s > 3.6 and tw_of(text, font, s, tr) > maxw:
        s -= 0.15
        tr = max(0.0, tracking * (s / size))
    return tracked(c, x, y, text, font, s, tr, fill, align)


def wrap_lines(text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if pdfmetrics.stringWidth(t, font, size) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- the book
class Book:
    def __init__(self, trim, path, title, subtitle):
        register_fonts()
        self.t = trim
        self.title = title
        self.subtitle = subtitle
        self.c = rl_canvas.Canvas(path, pagesize=(trim.W, trim.H),
                                  initialFontName=SERIF, initialFontSize=10)
        self.c.setTitle(title)
        self.c.setAuthor("")
        self.c.setSubject(subtitle)
        self.c.setCreator("FIELD RECORD composition engine")
        self.page = 1          # physical page index, 1 = first recto
        self.tabs = []         # list of (tag, title) in tab order
        self.pagemap = []      # (page, kind, label) for the index / verification
        self.outline_seen = set()
        # Values for a filled book. `filled` is {deployment_number: {slot:
        # {...}}} where slot is "site", "qsoA", "qsoB" or "debrief". Empty by
        # default, so a book built without it is the blank book it always was.
        self.filled = {}
        self.values = {}
        self.grid_data = None

    def fill_for(self, n, slot):
        """Select the value set for one deployment page, or clear it."""
        block = (self.filled.get(n) or {}).get(slot) or {}
        self.values = block.get("fields") or {}
        self.grid_data = block.get("rows")

    # -- handedness ------------------------------------------------------
    _begun = False

    @property
    def recto(self):
        """Right-hand page in a side-bound book, front of a leaf in a top-bound one."""
        return self.page % 2 == 1

    @property
    def front(self):
        return self.page % 2 == 1

    def begin(self):
        """Open the drawing frame for this page. Idempotent within a page.

        On the back of a top-bound leaf the frame is rotated 180 degrees, so
        every builder can keep drawing in ordinary reading coordinates and the
        sheet still images head to foot for short-edge duplex.
        """
        if self._begun:
            return
        self.c.saveState()
        if self.t.bind_top and not self.front:
            self.c.translate(self.t.W, self.t.H)
            self.c.rotate(180)
        self._begun = True

    def margins(self):
        """Return (left, right, top, bottom) in reading coordinates."""
        t = self.t
        if t.bind_top:
            # binding is at the head of a front, at the foot of a back
            if self.front:
                return t.outside, t.outside, t.inside, t.outside
            return t.outside, t.outside, t.outside, t.inside
        if self.recto:
            return t.inside, t.outside, t.top, t.bottom
        return t.outside, t.inside, t.top, t.bottom

    def body(self):
        """x, y, w, h of the live area on this page, in reading coordinates."""
        self.begin()
        l, r, tp, bt = self.margins()
        return l, bt, self.t.W - l - r, self.t.H - tp - bt

    def outer_x(self):
        """x of the outer trim edge for tab placement."""
        return self.t.W if self.recto else 0.0

    # -- page flow -------------------------------------------------------
    _label = None

    def end_page(self, kind="body", part=None, sec=None, folio=True, label=None):
        self._label = label
        self.pagemap.append((self.page, kind, label or (sec[1] if sec else (part or ""))))
        if kind != "blind":
            self._decorate(part, sec, folio)
        if self._begun:
            self.c.restoreState()
            self._begun = False
        self.c.showPage()
        self.page += 1

    def blank(self, n=1, kind="blank"):
        for _ in range(n):
            self.begin()
            self.end_page(kind=kind, folio=False)

    def to_recto(self):
        if not self.recto:
            self.blank()

    def to_verso(self):
        if self.recto:
            self.blank()

    def finish(self, pad_to_multiple=2):
        while self.page % pad_to_multiple != 1:
            self.blank()
        self.c.save()
        return self.page - 1

    # -- decoration ------------------------------------------------------
    def _decorate(self, part, sec, folio):
        c, t = self.c, self.t
        l, bt, w, h = self.body()
        top_y = t.H - t.top + 0.20 * inch

        # running head
        if part and not t.bind_top:
            c.setStrokeColor(G35)
            c.setLineWidth(W_HAIR)
            c.line(l, top_y - 3.0, l + w, top_y - 3.0)
            if self.recto:
                right_txt = (sec[1] if sec else (self._label or "")).upper()
                tracked(c, l, top_y, part.upper(), COND, 6.6, 1.15, G50)
                if right_txt:
                    tracked(c, l + w, top_y, right_txt, COND_SB, 6.6, 1.15, G70,
                            align="r")
            else:
                tracked(c, l, top_y, self.title, COND_SB, 6.6, 1.15, G70)
                tracked(c, l + w, top_y, part.upper(), COND, 6.6, 1.15, G50,
                        align="r")

        # folio, always at the free edge
        if folio:
            if t.bind_top:
                # the folio always sits at the free edge, outside the live area
                # but inside the 0.25 in safe margin
                if self.front:
                    fy = 0.300 * inch
                else:
                    fy = t.H - 0.355 * inch
                fx = l + w
                tracked(c, fx, fy, str(self.page), MONO_SB, 7.4, 0.4, G70, align="r")
                c.setStrokeColor(G25)
                c.setLineWidth(W_HAIR)
                c.line(fx - 30, fy + 2.4, fx - 18, fy + 2.4)
            else:
                fy = t.bottom - 0.30 * inch
                fx = (l + w) if self.recto else l
                tracked(c, fx, fy, str(self.page), MONO_SB, 8.2, 0.4, G70,
                        align="r" if self.recto else "l")
                c.setStrokeColor(G25)
                c.setLineWidth(W_HAIR)
                if self.recto:
                    c.line(fx - 34, fy + 2.6, fx - 20, fy + 2.6)
                else:
                    c.line(fx + 20, fy + 2.6, fx + 34, fy + 2.6)

        # fore-edge section marker
        if sec and sec[2] is not None:
            self._tab(sec)

    def _tab(self, sec):
        c, t = self.c, self.t
        tag, title, slot, nslots = sec[0], sec[1], sec[2], sec[3]
        if t.bind_top:
            if self.front:
                self._tab_bottom(sec)
            return
        band_top = t.H - t.top
        band_bot = t.bottom
        usable = band_top - band_bot
        cell = usable / float(nslots)
        gap = min(3.0, cell * 0.16)
        y0 = band_bot + usable - (slot + 1) * cell + gap / 2.0
        hgt = cell - gap
        tabw = 0.215 * inch
        inset = 0.275 * inch
        if self.recto:
            x0 = t.W - inset - tabw
        else:
            x0 = inset
        c.saveState()
        if INKM.weatherproof:
            c.setStrokeColor(INK)
            c.setLineWidth(W_MED)
            c.rect(x0, y0, tabw, hgt, stroke=1, fill=0)
        else:
            c.setFillColor(INK)
            c.rect(x0, y0, tabw, hgt, stroke=0, fill=1)
        # tag, rotated to read up the page
        label = tag[:6]
        lw = tw_of(label, COND_B, 6.0, 0.7)
        c.translate(x0 + tabw / 2.0, y0 + hgt / 2.0)
        c.rotate(90)
        tracked(c, -lw / 2.0, -2.1, label, COND_B, 6.0, 0.7,
                INK if INKM.weatherproof else white)
        c.restoreState()

    def _tab_bottom(self, sec):
        """Section marker along the free (foot) edge of a top-bound leaf."""
        c, t = self.c, self.t
        tag, slot, nslots = sec[0], sec[2], sec[3]
        l, bt, w, h = self.body()
        band = w * 0.86                        # leave the folio its corner
        cell = band / float(nslots)
        gap = min(4.0, cell * 0.14)
        x0 = l + slot * cell + gap / 2.0
        wid = cell - gap
        hgt = 0.125 * inch
        y0 = 0.265 * inch
        c.saveState()
        if INKM.weatherproof:
            c.setStrokeColor(INK)
            c.setLineWidth(W_MED)
            c.rect(x0, y0, wid, hgt, stroke=1, fill=0)
            fit_tracked(c, x0 + wid / 2.0, y0 + hgt / 2.0 - 2.0, tag[:6], COND_B,
                        5.6, wid - 5.0, 0.7, INK, align="c")
        else:
            c.setFillColor(INK)
            c.rect(x0, y0, wid, hgt, stroke=0, fill=1)
            fit_tracked(c, x0 + wid / 2.0, y0 + hgt / 2.0 - 2.0, tag[:6], COND_B,
                        5.6, wid - 4.0, 0.7, white, align="c")
        c.restoreState()

    # -- primitives ------------------------------------------------------
    def rule(self, x, y, w, weight=W_RULE, color=G35):
        c = self.c
        c.setStrokeColor(color)
        c.setLineWidth(weight)
        c.line(x, y, x + w, y)

    def vrule(self, x, y, h, weight=W_HAIR, color=G35):
        c = self.c
        c.setStrokeColor(color)
        c.setLineWidth(weight)
        c.line(x, y, x, y + h)

    def label(self, x, y, text, size=6.1, color=G70, tracking=0.85, font=COND_SB):
        return tracked(self.c, x, y, text.upper(), font, size, tracking, color)

    def kicker(self, x, y, text, size=6.4):
        """Small rule + tracked label, used to open a block."""
        w = tracked(self.c, x, y, text.upper(), COND_B, size, 1.1, INK)
        return w

    def box(self, x, y, w, h, title=None, fill=None, weight=W_RULE, color=G35,
            title_size=6.1):
        c = self.c
        if fill is not None:
            c.setFillColor(fill)
            c.rect(x, y, w, h, stroke=0, fill=1)
        c.setStrokeColor(color)
        c.setLineWidth(weight)
        c.rect(x, y, w, h, stroke=1, fill=0)
        if title:
            c.setFillColor(white)
            tw = tw_of(title.upper(), COND_B, title_size, 1.0) + 8
            c.rect(x + 5, y + h - 3.2, tw, 6.4, stroke=0, fill=1)
            tracked(c, x + 9, y + h - 2.2, title.upper(), COND_B, title_size, 1.0, INK)

    def wfield(self, x, y, w, label, size=5.9, gap=9.5, weight=W_RULE):
        """A labelled write-on line: label above, rule below."""
        self.label(x, y + gap, label, size=size)
        self.rule(x, y, w, weight=weight, color=G35)

    def wbox(self, x, y, w, h, label, size=5.9):
        """A labelled write-on box."""
        self.label(x, y + h + 2.2, label, size=size)
        self.c.setStrokeColor(G35)
        self.c.setLineWidth(W_RULE)
        self.c.rect(x, y, w, h, stroke=1, fill=0)

    def checkline(self, x, y, w, text, size=7.6, boxsize=6.4, font=SERIF):
        c = self.c
        c.setStrokeColor(G50)
        c.setLineWidth(W_RULE)
        c.rect(x, y - 0.6, boxsize, boxsize, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont(font, size)
        lines = wrap_lines(text, font, size, w - boxsize - 6)
        yy = y
        for i, ln in enumerate(lines):
            c.drawString(x + boxsize + 5, yy, ln)
            yy -= size * 1.22
        return len(lines) * size * 1.22

    def dotgrid(self, x, y, w, h, pitch=0.145 * inch, color=G25, r=0.42):
        c = self.c
        c.saveState()
        c.setFillColor(color)
        ny = int(h // pitch)
        nx = int(w // pitch)
        ox = x + (w - nx * pitch) / 2.0
        oy = y + (h - ny * pitch) / 2.0
        for i in range(nx + 1):
            for j in range(ny + 1):
                c.circle(ox + i * pitch, oy + j * pitch, r, stroke=0, fill=1)
        c.restoreState()

    def linegrid(self, x, y, w, h, rows, color=G25, weight=W_HAIR):
        rh = h / float(rows)
        for i in range(rows):
            self.rule(x, y + i * rh, w, weight=weight, color=color)

    # -- table grid (write-on forms) --------------------------------------
    def formgrid(self, x, y, w, h, headers, widths, rows, row_h=None,
                 head_h=13.0, zebra=True, num_col=False, size=6.2,
                 sub_headers=None, data=None):
        """Draw a ruled write-on table. Returns bottom y.

        data, when given, is a list of row sequences aligned to `headers`, and
        is printed in mono inside the ruling. Rows beyond the data stay blank,
        so a sheet that is half filled from the log and half from the field
        still prints as one sheet.
        """
        c = self.c
        total = sum(widths)
        widths = [wd / total * w for wd in widths]
        if row_h is None:
            row_h = (h - head_h) / float(rows)
        top = y + h
        # header band
        hf = head_fill()
        if hf is not None:
            c.setFillColor(hf)
            c.rect(x, top - head_h, w, head_h, stroke=0, fill=1)
        # zebra
        zf = zebra_fill()
        if zebra and zf is not None:
            c.setFillColor(zf)
            for i in range(rows):
                if i % 2 == 1:
                    c.rect(x, top - head_h - (i + 1) * row_h, w, row_h, stroke=0, fill=1)
        # accent rule under the header band
        if CLR.on:
            c.setStrokeColor(AMBER)
            c.setLineWidth(1.1)
            c.line(x, top - head_h, x + w, top - head_h)
        # header text
        cx = x
        for i, hd in enumerate(headers):
            fit_tracked(c, cx + widths[i] / 2.0, top - head_h + 4.2, hd.upper(),
                        COND_B, size, widths[i] - 4.0, 0.55, INK, align="c")
            cx += widths[i]
        # horizontal rules
        self.rule(x, top, w, W_MED, G70)
        self.rule(x, top - head_h, w, W_RULE, G70)
        for i in range(1, rows + 1):
            yy = top - head_h - i * row_h
            self.rule(x, yy, w, W_HAIR if i < rows else W_MED,
                      G35 if i < rows else G70)
        # verticals
        cx = x
        self.vrule(cx, top - head_h - rows * row_h, head_h + rows * row_h, W_MED, G70)
        for i, wd in enumerate(widths):
            cx += wd
            wgt = W_MED if i == len(widths) - 1 else W_HAIR
            col = G70 if i == len(widths) - 1 else G35
            self.vrule(cx, top - head_h - rows * row_h, head_h + rows * row_h, wgt, col)
        # filled cells
        data = data if data is not None else self.grid_data
        if data:
            for ri, row in enumerate(data[:rows]):
                yy = top - head_h - (ri + 1) * row_h + row_h / 2.0 - 2.2
                cx2 = x
                for ci, wd in enumerate(widths):
                    if ci < len(row) and row[ci] not in (None, ""):
                        al = "c" if ci == 0 else "l"
                        tx = cx2 + wd / 2.0 if al == "c" else cx2 + 2.0
                        fit_tracked(self.c, tx, yy, str(row[ci]), MONO,
                                    size + 0.3, wd - 3.0, 0.0, INK, align=al)
                    cx2 += wd
        # row numbers
        if num_col:
            for i in range(rows):
                yy = top - head_h - (i + 1) * row_h + row_h / 2.0 - 2.2
                tracked(c, x + widths[0] / 2.0, yy, str(i + 1), MONO, size + 0.4,
                        0.0, G50, align="c")
        return top - head_h - rows * row_h


# ---------------------------------------------------------------- prose styles
def make_styles(t):
    b, ld = t.base, t.lead
    # A top-bound book has identical left and right margins on every page, so
    # its narrowed prose measure can sit flush left instead of centered.
    li = 0.0 if t.bind_top else t.prose_indent / 2.0
    ri = t.prose_indent if t.bind_top else t.prose_indent / 2.0
    S = {}
    S['lead'] = ParagraphStyle('lead', fontName=SERIF_I, fontSize=b + 1.0,
                               leading=ld + 1.8, spaceAfter=ld * 0.62,
                               textColor=G70, alignment=TA_LEFT,
                               leftIndent=li, rightIndent=ri)
    S['p'] = ParagraphStyle('p', fontName=SERIF, fontSize=b, leading=ld,
                            spaceAfter=ld * 0.42, alignment=TA_JUSTIFY,
                            firstLineIndent=0,
                            leftIndent=li, rightIndent=ri,
                            hyphenationLang='')
    S['h2'] = ParagraphStyle('h2', fontName=COND_B, fontSize=b + 5.5,
                             leading=(b + 5.5) * 1.14, spaceBefore=ld * 1.1,
                             spaceAfter=ld * 0.34, textColor=INK)
    S['h3'] = ParagraphStyle('h3', fontName=COND_B, fontSize=b + 0.4,
                             leading=(b + 0.4) * 1.2, spaceBefore=ld * 0.95,
                             spaceAfter=ld * 0.26, textColor=INK)
    # The bullet font must be named explicitly: platypus otherwise falls back
    # to Helvetica, which would leave one unembedded base-14 face in the file.
    S['bul'] = ParagraphStyle('bul', parent=S['p'],
                              leftIndent=li + 11, bulletIndent=li + 1,
                              bulletFontName=SERIF, bulletFontSize=b,
                              spaceAfter=ld * 0.26, alignment=TA_LEFT)
    S['num'] = ParagraphStyle('num', parent=S['bul'],
                              bulletFontName=SERIF, bulletFontSize=b,
                              leftIndent=li + 15, bulletIndent=li + 1)
    S['note'] = ParagraphStyle('note', fontName=SERIF, fontSize=b - 0.5,
                               leading=ld - 0.9, textColor=INK,
                               leftIndent=9, rightIndent=7,
                               spaceBefore=2, spaceAfter=2, alignment=TA_LEFT)
    S['formula'] = ParagraphStyle('formula', fontName=MONO_SB, fontSize=b - 0.8,
                                  leading=ld, alignment=TA_CENTER,
                                  spaceBefore=ld * 0.3, spaceAfter=ld * 0.3)
    S['script_who'] = ParagraphStyle('sw', fontName=COND_B, fontSize=b - 1.4,
                                     leading=ld - 1.5, textColor=G70)
    S['script_txt'] = ParagraphStyle('st', fontName=MONO, fontSize=b - 1.6,
                                     leading=ld - 1.2,
                                     leftIndent=li + 34, rightIndent=ri,
                                     spaceAfter=ld * 0.22)
    S['cap'] = ParagraphStyle('cap', fontName=COND, fontSize=b - 2.2,
                              leading=ld - 3.0, textColor=G70)
    return S
