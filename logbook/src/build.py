# -*- coding: utf-8 -*-
"""FIELD RECORD - book assembly. Two-pass so the contents can carry real folios."""
import sys, os
from reportlab.lib.units import inch

from engine import (Book, TRIMS, make_styles, INK, G25, G35, G50, G70,
                    TINT_HEAD, W_HAIR, W_RULE, W_MED, W_HEAVY,
                    SERIF, SERIF_I, COND, COND_SB, COND_B,
                    MONO, MONO_SB, tracked, tw_of, wrap_lines, fit_tracked)
import pages as P
import forms as F
import content_meta as M
import content_ref_a as A
import content_ref_b as B

N_DEPLOY = 30
REF_SECTIONS = A.SECTIONS_A + B.SECTIONS_B
TOC_PAGES = 2


def dial_rule(bk, x, y, w, n=41, h=4.2):
    c = bk.c
    c.setStrokeColor(G50)
    c.setLineWidth(W_HAIR)
    for i in range(n):
        xx = x + w * i / float(n - 1)
        hh = h if i % 5 == 0 else h * 0.5
        c.line(xx, y, xx, y + hh)
    c.setLineWidth(W_RULE)
    c.setStrokeColor(G70)
    c.line(x, y, x + w, y)


# ------------------------------------------------------------------ front matter
def half_title(bk):
    x, y, w, h = bk.body()
    c = bk.c
    tracked(c, x, y + h * 0.60, M.TITLE, COND_B, bk.t.base * 2.0, 4.5, INK)
    bk.rule(x, y + h * 0.60 - 9, w * 0.42, W_MED, G70)
    # Whose book, not who wrote it. The author's credit is on the copyright
    # page below, which is where it belongs and where it stays.
    tracked(c, x, y + h * 0.36,
            (getattr(bk, "byline", None) or M.AUTHOR).upper(), COND,
            bk.t.base - 1.4, 1.7, G50)
    c.setFont(SERIF_I, bk.t.base)
    c.setFillColor(G70)
    yy = y + h * 0.60 - 26
    for ln in wrap_lines(M.HALF_TITLE_NOTE, SERIF_I, bk.t.base, w * 0.72):
        c.drawString(x, yy, ln)
        yy -= bk.t.lead
    bk.end_page(kind="front", folio=False)


def title_page(bk, ndep=30):
    x, y, w, h = bk.body()
    c = bk.c
    top = y + h
    dial_rule(bk, x, top - 0.34 * inch, w)
    size = bk.t.base * 3.05
    tracked(c, x, top - 1.30 * inch, "FIELD", COND_B, size, 6.0, INK)
    tracked(c, x, top - 1.30 * inch - size * 0.95, "RECORD", COND_B, size, 6.0, INK)
    ry = top - 1.30 * inch - size * 0.95 - 20
    bk.rule(x, ry, w, W_HEAVY, INK)
    c.setFont(SERIF_I, bk.t.base + 2.4)
    c.setFillColor(INK)
    c.drawString(x, ry - 20, M.SUBTITLE)
    # Whose copy, not who wrote it. See the copyright page for authorship.
    tracked(c, x, y + 1.42 * inch,
            (getattr(bk, "byline", None) or M.AUTHOR).upper(), COND_B,
            bk.t.base + 0.6, 2.2, INK)
    bk.rule(x, y + 1.42 * inch - 7, w * 0.30, W_MED, G70)
    kick = ["%d DEPLOYMENTS  ·  SITE, SIGNAL, AND DEBRIEF" % ndep,
            "FIELD REFERENCE FOR PORTABLE OPERATION"]
    kyy = ry - 42
    for kl in kick:
        fit_tracked(c, x, kyy, kl, COND, bk.t.base - 2.4, w, 1.0, G70)
        kyy -= (bk.t.base - 2.4) * 1.55
    dial_rule(bk, x, y + 0.95 * inch, w)
    tracked(c, x + w / 2, y + 0.62 * inch, M.SERIES_MARK, COND_B,
            bk.t.base - 1.6, 2.6, G70, align="c")
    tracked(c, x + w / 2, y + 0.40 * inch, M.IMPRINT.upper(), COND,
            bk.t.base - 2.6, 1.6, G50, align="c")
    bk.end_page(kind="front", folio=False)


def copyright_page(bk):
    """Set to the foot of the page, in the usual place for a rights notice.

    Paragraphs that open with a full-capital run-in label get that label set in
    the condensed bold, so the licence and trademark notices can be found
    without reading the whole page.
    """
    x, y, w, h = bk.body()
    c = bk.c
    txt = M.COPYRIGHT.format(edition=M.EDITION, year=M.YEAR,
                             imprint=M.IMPRINT, author=M.AUTHOR)
    size = bk.t.base - 1.6
    meas = w * 0.86

    def split_label(para):
        """Return (label, rest) if the paragraph opens with a CAPS run-in."""
        for sep in (". ", ". "):
            i = para.find(sep)
            if 0 < i < 26:
                head = para[:i]
                if head.isupper() and head.replace(" ", "").isalpha():
                    return head, para[i + len(sep):]
        return None, para

    paras = []
    for para in txt.split("\n\n"):
        para = " ".join(para.split())
        if para:
            paras.append(para)

    def compose(para):
        """(size, font, is_title, label, lines, height) for one paragraph."""
        title = para.startswith("FIELD RECORD:")
        sz = size + (1.0 if title else 0)
        lab, rest = (None, para) if title else split_label(para)
        font = COND_B if title else SERIF
        lines = wrap_lines(rest if lab else para, font, sz, meas)
        hgt = len(lines) * sz * 1.42 + sz * 0.7 + (sz * 1.55 if lab else 0.0)
        return sz, font, title, lab, lines, hgt

    blocks = [compose(p) for p in paras]
    total = sum(b[5] for b in blocks)
    yy = min(y + total - size * 0.7, y + h - 12)

    for sz, font, title, lab, lines, _ in blocks:
        if lab:
            yy -= sz * 0.55
            tracked(c, x, yy, lab, COND_B, sz - 0.6, 1.6, INK)
            yy -= sz * 1.45
        c.setFillColor(INK if title else G70)
        c.setFont(font, sz)
        for ln in lines:
            c.drawString(x, yy, ln)
            yy -= sz * 1.42
        yy -= sz * 0.7
    bk.end_page(kind="front", folio=False)


def toc_layout(t, entries, npages):
    """Deal contents entries onto npages pages. Returns (pages, leftover).

    The same arithmetic drives both the page-count estimate and the drawing,
    so a contents that fits the estimate always fits the page.
    """
    top_h = t.H - t.top
    floor = t.bottom + 6
    out, i = [], 0
    for pi in range(npages):
        yy = top_h - (0.30 * inch + 30 if pi == 0 else 0.16 * inch + 26)
        page = []
        while i < len(entries):
            kind = entries[i][0]
            need = 23 if kind == "part" else t.lead * 1.06
            if yy - need < floor:
                break
            page.append(entries[i])
            i += 1
            yy -= 23 if kind == "part" else (
                t.lead * 1.06 if kind == "sec" else t.lead * 0.92)
        out.append(page)
    return out, len(entries) - i


def toc_pages_needed(t, entries, minimum=2):
    """How many contents pages this book needs. Never fewer than the minimum."""
    n = minimum
    while n < 12:
        _pages, left = toc_layout(t, entries, n)
        if not left:
            return n
        n += 1
    return n


def contents_pages(bk, toc, npages=TOC_PAGES):
    """Draw exactly npages pages of contents."""
    t = bk.t
    entries = list(toc or [])
    pages, leftover = toc_layout(t, entries, npages)
    if leftover:
        # Should not happen: make_book sizes the contents from the entry list
        # before the drawing pass. Say so rather than dropping entries quietly.
        raise ValueError("contents needs more than %d pages; %d entries did "
                         "not fit" % (npages, leftover))
    for pi in range(npages):
        x, y, w, h = bk.body()
        c = bk.c
        top = y + h
        page = pages[pi] if pi < len(pages) else []
        if pi == 0:
            tracked(c, x, top - 0.30 * inch, "CONTENTS", COND_B, bk.t.base + 6.5,
                    3.2, INK)
            bk.rule(x, top - 0.30 * inch - 9, w, W_HEAVY, INK)
            yy = top - 0.30 * inch - 30
        elif page:
            tracked(c, x, top - 0.16 * inch, "CONTENTS, CONTINUED", COND, 6.4,
                    1.2, G50)
            bk.rule(x, top - 0.16 * inch - 6, w, W_RULE, G35)
            yy = top - 0.16 * inch - 26
        else:
            # the contents fitted on fewer pages; leave the rest blank rather
            # than heading an empty page
            bk.end_page(kind="front", folio=False)
            continue
        for kind, label, pg in page:
            if kind == "part":
                yy -= 6
                tracked(c, x, yy, label.upper(), COND_B, bk.t.base + 0.6, 1.5, INK)
                if pg:
                    tracked(c, x + w, yy, str(pg), MONO_SB, bk.t.base - 0.6, 0, INK,
                            align="r")
                bk.rule(x, yy - 4.5, w, W_RULE, G70)
                yy -= 17
            elif kind == "sec":
                c.setFont(SERIF, bk.t.base - 0.8)
                c.setFillColor(INK)
                c.drawString(x + 10, yy, label)
                lw = 10 + c.stringWidth(label, SERIF, bk.t.base - 0.8) + 5
                pw = tw_of(str(pg), MONO, bk.t.base - 1.4)
                c.setStrokeColor(G25)
                c.setLineWidth(W_HAIR)
                c.setDash(0.6, 2.6)
                c.line(x + lw, yy + 1.6, x + w - pw - 5, yy + 1.6)
                c.setDash()
                tracked(c, x + w, yy, str(pg), MONO, bk.t.base - 1.4, 0, G70,
                        align="r")
                yy -= bk.t.lead * 1.06
            elif kind == "sub":
                tracked(c, x + 10, yy, label.upper(), COND, bk.t.base - 2.2, 0.7, G50)
                if pg:
                    tracked(c, x + w, yy, str(pg), MONO, bk.t.base - 1.8, 0, G50,
                            align="r")
                yy -= bk.t.lead * 0.92
        bk.end_page(kind="front", folio=False)


def part_title(bk, numeral, name, blurb, items):
    x, y, w, h = bk.body()
    c = bk.c
    top = y + h
    dial_rule(bk, x, top - 0.30 * inch, w)
    tracked(c, x, top - 1.05 * inch, numeral.upper(), COND, bk.t.base + 3.0, 4.5, G50)
    size = bk.t.base * 2.15
    lines = name.upper().split("|")
    yy = top - 1.05 * inch - size * 1.02
    for ln in lines:
        tracked(c, x, yy, ln.strip(), COND_B, size, 3.6, INK)
        yy -= size * 0.94
    yy -= 6
    bk.rule(x, yy, w, W_HEAVY, INK)
    yy -= 20
    c.setFont(SERIF_I, bk.t.base + 0.6)
    c.setFillColor(G70)
    for ln in wrap_lines(blurb, SERIF_I, bk.t.base + 0.6, w * 0.86):
        c.drawString(x, yy, ln)
        yy -= bk.t.lead * 1.05
    yy -= 16
    for it in items:
        tracked(c, x, yy, it.upper(), COND_SB, bk.t.base - 1.6, 1.0, INK)
        bk.rule(x, yy - 4.5, w, W_HAIR, G25)
        yy -= bk.t.lead * 1.22
        if yy < y + 10:
            break
    bk.end_page(kind="part", folio=False)


def section_opener(bk, sec, idx, nsec):
    """Draw the section head at the top of the current page; return the drop."""
    x, y, w, h = bk.body()
    c = bk.c
    top = y + h
    tracked(c, x, top - 0.16 * inch, "%02d" % (idx + 1), MONO_SB, bk.t.base + 1.2,
            0.8, G50)
    tracked(c, x + 0.36 * inch, top - 0.16 * inch, sec['tag'], COND_B,
            bk.t.base - 1.6, 1.9, G50)
    size = bk.t.base + 5.6
    lines = wrap_lines(sec['title'], COND_B, size, w)
    yy = top - 0.42 * inch
    for ln in lines:
        tracked(c, x, yy, ln, COND_B, size, 0.6, INK)
        yy -= size * 1.06
    bk.rule(x, yy + size * 0.30, w, W_HEAVY, INK)
    return (top - (yy + size * 0.30)) + 12


# ------------------------------------------------------------------ station id
def station_identity(bk):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = F.page_header(bk, "This Station", big="Operator and station")
    y = F.blockhead(bk, x, y - 4, w, "Operator")
    y = F.fields_row(bk, x, y - 2, w, [("Callsign", 1.2), ("Name", 1.8),
                                       ("License class", 1.0), ("Expires", 0.9)])
    y = F.fields_row(bk, x, y - 15, w, [("Home grid", 1.0), ("ARRL section", 1.2),
                                        ("FRN", 1.0), ("Club", 1.6)])
    y = F.fields_row(bk, x, y - 15, w, [("Email", 1.6), ("QSL route", 1.4),
                                        ("LoTW", 0.8), ("Logbook software", 1.4)])
    y -= 16
    y = F.blockhead(bk, x, y, w, "Programs and identifiers")
    y = F.fields_row(bk, x, y - 2, w, [("POTA account", 1.2), ("SOTA account", 1.2),
                                       ("WWFF", 1.0), ("Contest section", 1.0)])
    y -= 16
    y = F.blockhead(bk, x, y, w, "If found")
    c.setFont(SERIF_I, bk.t.base - 1.0)
    c.setFillColor(G70)
    msg = ("This is a working logbook. It has no commercial value and "
           "considerable value to its owner. The operator would be glad to "
           "hear from the finder.")
    for ln in wrap_lines(msg, SERIF_I, bk.t.base - 1.0, w):
        y -= (bk.t.base - 1.0) * 1.3
        c.drawString(x, y, ln)
    y -= 12
    y = F.fields_row(bk, x, y, w, [("Contact", 2.0), ("Phone", 1.0), ("Reward", 1.0)])
    y -= 18
    y = F.blockhead(bk, x, y, w, "Emergency information")
    y = F.fields_row(bk, x, y - 2, w, [("Emergency contact", 1.6), ("Relationship", 1.0),
                                       ("Phone", 1.0)])
    y = F.fields_row(bk, x, y - 15, w, [("Medical notes for first responders", 1.0)])
    y = F.fields_row(bk, x, y - 15, w, [("Vehicle", 1.4), ("Plate", 0.8),
                                        ("Local repeater / net", 1.6)])
    bk.end_page(kind="form", folio=True)


def inventory_page(bk):
    F.form_page(bk, "Go-Kit Manifest", "equipment carried",
                ["Item", "Detail / model", "Qty", "Bag", "Chk"],
                [.30, .40, .07, .13, .10], row_h=0.235 * inch, size=6.0,
                intro="Enter the standing kit once and check it in pencil, or "
                      "reproduce this page for each outing.")
    bk.end_page(kind="form", folio=True)


# ------------------------------------------------------------------ part II
def deployment_index(bk, ndep=N_DEPLOY):
    """One line per deployment, continued over as many pages as it takes."""
    left, page = ndep, 0
    while left > 0:
        F.form_page(bk, "Deployment Index" if page == 0
                    else "Deployment Index, continued",
                    "one line per outing. the fastest way back to a page."
                    if page == 0 else "",
                    ["No.", "Date (UTC)", "Site", "Reference", "QSOs", "Valid",
                     "Page"],
                    [.055, .115, .295, .175, .075, .075, .21],
                    rows=left, size=6.2, stretch=True)
        left -= F.form_page.drawn
        page += 1
        bk.end_page(kind="form", folio=True)


def deployment_howto(bk):
    x, y0, w, h0 = bk.body()
    c = bk.c
    y = F.page_header(bk, "How a Deployment Is Recorded", big="Structure")
    y -= 8
    steps = [
        ("Spread one, left", "Site Record",
         "Location, conditions, station, antenna and power. Completed "
         "before the first call."),
        ("Spread one, right", "QSO Log, sheet A",
         "Contacts as made, in UTC. A heavy line is ruled across the grid "
         "at the day rollover."),
        ("Spread two, left", "QSO Log, sheet B",
         "More of the same. If you fill it, continue on the overflow sheets at "
         "the back of Part Three and write the deployment number at the top."),
        ("Spread two, right", "Debrief",
         "Totals, summary, power consumed, and three entries completed at "
         "the site."),
    ]
    for tag, name, body in steps:
        y = F.blockhead(bk, x, y, w, name, right=tag)
        c.setFont(SERIF, bk.t.base)
        c.setFillColor(INK)
        for ln in wrap_lines(body, SERIF, bk.t.base, w * 0.92):
            y -= bk.t.lead
            c.drawString(x, y, ln)
        y -= 20
    y -= 6
    y = F.blockhead(bk, x, y, w, "Column notes for the QSO log")
    notes = [
        ("UTC", "Time only, four digits. The date goes at the top of the sheet."),
        ("W", "Transmitter output at this station, not the other. The figure "
              "used when comparing sites."),
        ("Sent / Rcvd", "Signal reports. Sent is what you gave them."),
        ("State / Park / Summit / Grid",
         "Whatever the other station would need in return. Park and summit "
         "references belong here rather than in Notes."),
        ("Notes", "The other station\u2019s antenna and power, conditions, and any "
                  "difficulty. The column that gives the log later value."),
    ]
    for k, v in notes:
        tracked(c, x, y - 8, k.upper(), COND_B, bk.t.base - 1.8, 1.0, INK)
        kw = tw_of(k.upper(), COND_B, bk.t.base - 1.8, 1.0) + 10
        c.setFont(SERIF, bk.t.base - 0.8)
        c.setFillColor(G70)
        lines = wrap_lines(v, SERIF, bk.t.base - 0.8, w - kw)
        yy = y - 8
        for ln in lines:
            c.drawString(x + kw, yy, ln)
            yy -= (bk.t.base - 0.8) * 1.28
        y = yy - 6
    bk.end_page(kind="form", folio=True)


# ------------------------------------------------------------------ part III
# Every station record is a named block, so a station file can ask for some of
# them and leave the rest out. The order here is the order they print in.
RECORD_ORDER = ["equipment", "repairs", "antennas", "battery", "qsl",
                "was", "dxcc", "activations", "nets", "overflow", "notes"]

RECORD_TITLES = {
    "equipment": "Equipment Register",
    "repairs": "Modification and Repair Log",
    "antennas": "Antenna Build Sheets",
    "battery": "Battery and Power Log",
    "qsl": "QSL and Confirmation Tracker",
    "was": "Worked All States",
    "dxcc": "Entities and Continents Worked",
    "activations": "Parks and Summits Activated",
    "nets": "Nets, Schedules, and Contacts",
    "overflow": "Overflow QSO Sheets",
    "notes": "Field Notes",
}


def _rec_equipment(bk):
    F.form_page(bk, "Equipment Register", "items held, with serial numbers",
                ["Item", "Manufacturer", "Model", "Serial", "Acquired", "Source", "Notes"],
                [.155, .135, .135, .135, .095, .12, .225], size=6.0,
                intro="Photograph this page. It is the record an insurance "
                      "claim or an estate will ask for.")
    bk.end_page(kind="form", folio=True)


def _rec_repairs(bk):
    for sub in ("work carried out and its result", "continued"):
        F.form_page(bk, "Modification and Repair Log", sub,
                    ["Date", "Equipment", "Work performed", "Result", "By"],
                    [.095, .175, .385, .245, .10], row_h=0.30 * inch, size=6.0)
        bk.end_page(kind="form", folio=True)


def _rec_antennas(bk):
    for i in range(1, 5):
        F.antenna_build_page(bk, i)
        bk.end_page(kind="form", folio=True)


def _rec_battery(bk):
    F.form_page(bk, "Battery and Power Log", "cycle history by pack",
                ["Date", "Pack", "Start V", "End V", "Ah used", "Hours", "Charged to", "Notes"],
                [.09, .155, .075, .075, .085, .075, .095, .35], size=6.0,
                intro="Lithium chemistry gives little warning of decline. The "
                      "cycle history is the only indication available.")
    bk.end_page(kind="form", folio=True)


def _rec_qsl(bk):
    F.form_page(bk, "QSL and Confirmation Tracker", "cards and electronic confirmations",
                ["Callsign", "Date", "Band", "Mode", "Via", "Sent", "Rcvd", "LoTW", "Notes"],
                [.135, .095, .07, .07, .105, .06, .065, .065, .335], size=6.0)
    bk.end_page(kind="form", folio=True)


def _rec_was(bk):
    worked_all_states(bk)
    bk.end_page(kind="form", folio=True)


def _rec_dxcc(bk):
    F.form_page(bk, "Entities Worked", "toward DXCC and Worked All Continents",
                ["Prefix", "Entity", "Date", "Band", "Mode", "Confirmed",
                 "Prefix", "Entity", "Date", "Band", "Mode", "Confirmed"],
                [.06, .155, .06, .045, .045, .07, .06, .155, .06, .045, .045, .07],
                size=5.6, row_h=0.215 * inch)
    bk.end_page(kind="form", folio=True)


def _rec_activations(bk):
    F.form_page(bk, "Parks and Summits Activated", "activation history",
                ["Reference", "Name", "First activated", "Times", "Best count", "Notes"],
                [.13, .295, .12, .07, .085, .30], size=6.0)
    bk.end_page(kind="form", folio=True)


def _rec_nets(bk):
    F.form_page(bk, "Nets and Schedules", "standing schedules",
                ["Net or sked", "Frequency", "Day", "Time (UTC)", "Net control", "Notes"],
                [.20, .12, .09, .10, .14, .35], size=6.0)
    bk.end_page(kind="form", folio=True)
    F.form_page(bk, "Contacts", "operators worked",
                ["Callsign", "Name", "QTH", "Grid", "Where we met", "Notes"],
                [.115, .15, .17, .085, .17, .31], size=6.0)
    bk.end_page(kind="form", folio=True)


def _rec_overflow(bk):
    for _ in range(4):
        overflow_log(bk)
        bk.end_page(kind="log", folio=True)


def _rec_notes(bk):
    for i in range(4):
        notes_page(bk, dot=(i % 2 == 0))
        bk.end_page(kind="form", folio=True)


RECORD_BUILDERS = {
    "equipment": _rec_equipment, "repairs": _rec_repairs,
    "antennas": _rec_antennas, "battery": _rec_battery, "qsl": _rec_qsl,
    "was": _rec_was, "dxcc": _rec_dxcc, "activations": _rec_activations,
    "nets": _rec_nets, "overflow": _rec_overflow, "notes": _rec_notes,
}


def part_three_pages(bk, toc, want=None):
    """Draw the station records named in `want`, in the standard order."""
    keys = RECORD_ORDER if want is None else [k for k in RECORD_ORDER if k in want]
    for k in keys:
        toc.append(("sec", RECORD_TITLES[k], bk.page))
        RECORD_BUILDERS[k](bk)
    return keys


def worked_all_states(bk):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = F.page_header(bk, "Worked All States", big="Confirmed")
    fit_tracked(c, x, y - 8, "DIAGONAL FOR WORKED, FILLED BOX FOR CONFIRMED", COND, 5.6, w, 0.75, G50)
    y -= 18
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
              "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
              "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
              "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
              "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    bands = ["160", "80", "60", "40", "30", "20", "17", "15", "12", "10", "6", "2"]
    ncol = 2
    per = 25
    colw = (w - 14) / float(ncol)
    lblw = colw * 0.115
    cellw = (colw - lblw) / len(bands)
    avail = y - y0 - 6
    cellh = min(0.265 * inch, avail / (per + 1.0))
    for ci in range(ncol):
        cx = x + ci * (colw + 14)
        cy = y
        c.setFillColor(TINT_HEAD)
        c.rect(cx, cy - cellh, colw, cellh, stroke=0, fill=1)
        for bi, bn in enumerate(bands):
            tracked(c, cx + lblw + cellw * (bi + 0.5), cy - cellh + cellh * 0.32,
                    bn, COND_B, 5.2, 0.2, INK, align="c")
        bk.rule(cx, cy, colw, W_MED, G70)
        bk.rule(cx, cy - cellh, colw, W_RULE, G70)
        for si in range(per):
            idx = ci * per + si
            ry = cy - cellh - (si + 1) * cellh
            if idx < len(states):
                tracked(c, cx + 3.5, ry + cellh * 0.30, states[idx], COND_B, 6.0,
                        0.5, INK)
            bk.rule(cx, ry, colw, W_HAIR if si < per - 1 else W_MED,
                    G35 if si < per - 1 else G70)
        htot = cellh * (per + 1)
        bk.vrule(cx, cy - htot, htot, W_MED, G70)
        bk.vrule(cx + lblw, cy - htot, htot, W_RULE, G50)
        for bi in range(len(bands)):
            bk.vrule(cx + lblw + cellw * (bi + 1), cy - htot, htot,
                     W_MED if bi == len(bands) - 1 else W_HAIR,
                     G70 if bi == len(bands) - 1 else G25)


def overflow_log(bk):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = F.page_header(bk, "QSO Log", big="Overflow sheet")
    y = F.fields_row(bk, x, y - 6, w, [("Deployment no.", 0.7), ("Date (UTC)", 1.0),
                                       ("Callsign used", 1.1),
                                       ("Program reference", 1.5), ("Sheet", 0.5)])
    y -= 10
    six = bk.t.key == "6x9"
    if six:
        heads = ["UTC", "Callsign", "Band", "Mode", "W", "Sent", "Rcvd",
                 "QTH / Reference", "Notes"]
        widths = [.088, .175, .072, .072, .052, .062, .062, .200, .217]
        num_col, size = False, 5.9
    else:
        heads = ["#", "UTC", "Callsign", "Band", "Mode", "W", "Sent", "Rcvd",
                 "State / Park / Summit / Grid", "Notes"]
        widths = [.032, .076, .148, .062, .062, .046, .052, .052, .190, .280]
        num_col, size = True, 6.2
    rows = bk.t.log_rows
    row_h = bk.t.log_row_h
    gh = rows * row_h + 13.0
    while y - gh < y0 + 0.30 * inch:
        rows -= 1
        gh = rows * row_h + 13.0
    bottom = bk.formgrid(x, y - gh, w, gh, heads, widths, rows, row_h=row_h,
                         head_h=13.0, zebra=True, num_col=num_col, size=size)
    F.fields_row(bk, x, bottom - 12, w, [("QSOs this sheet", 1.0),
                                         ("Running total", 1.0),
                                         ("Transferred to electronic log", 1.4)])


def notes_page(bk, dot=True):
    c = bk.c
    x, y0, w, h0 = bk.body()
    y = F.page_header(bk, "Field Notes", big="")
    if dot:
        bk.dotgrid(x, y0 + 2, w, y - y0 - 6)
    else:
        n = int((y - y0 - 6) // (0.21 * inch))
        rh = (y - y0 - 6) / float(n)
        for i in range(n):
            bk.rule(x, y0 + 2 + i * rh, w, W_HAIR, G25)
    c.setStrokeColor(G35)
    c.setLineWidth(W_RULE)
    c.rect(x, y0 + 2, w, y - y0 - 6, stroke=1, fill=0)


def colophon(bk):
    S = bk.styles
    x, y, w, h = bk.body()
    c = bk.c
    top = y + h
    tracked(c, x, top - 0.22 * inch, "COLOPHON", COND_B, bk.t.base + 5.0, 2.4, INK)
    bk.rule(x, top - 0.22 * inch - 10, w, W_HEAVY, INK)
    blocks = [b for b in M.COLOPHON if not (b[0] == "h3" and b[1] == "Colophon")]
    story = P.render_blocks(blocks, S, w, bk.t.base)
    P.flow(bk, story, part=None, sec=None,
           first_page_drop=0.22 * inch + 24, folio=False)


# ------------------------------------------------------------------ assembly
def build(trim_key, outpath, toc_in=None):
    t = TRIMS[trim_key]
    bk = Book(t, outpath, M.TITLE, M.SUBTITLE)
    bk.styles = make_styles(t)
    toc = []

    # --- front matter
    half_title(bk)
    bk.blank(kind="front")
    title_page(bk)
    copyright_page(bk)
    contents_pages(bk, toc_in)

    bk.to_recto()
    toc.append(("part", "How to Use This Book", bk.page))
    x, y, w, h = bk.body()
    c = bk.c
    top = y + h
    tracked(c, x, top - 0.22 * inch, "HOW TO USE THIS BOOK", COND_B,
            t.base + 5.0, 2.4, INK)
    bk.rule(x, top - 0.22 * inch - 10, w, W_HEAVY, INK)
    drop = 0.22 * inch + 24
    story = P.render_blocks(M.HOW_TO_USE, bk.styles, w, t.base)
    P.flow(bk, story, part=None, sec=None, first_page_drop=drop, folio=False)

    bk.to_recto()
    toc.append(("sec", "This Station", bk.page))
    station_identity(bk)
    toc.append(("sec", "Go-Kit Manifest", bk.page))
    inventory_page(bk)

    # --- PART ONE
    bk.to_recto()
    toc.append(("part", "Part One: Field Reference", bk.page))
    part_title(bk, "Part One", "FIELD | REFERENCE",
               "The material a portable operator reaches for with cold hands. "
               "Read it once at the kitchen table. After that, use the section "
               "markers in the outer margin.",
               [s['title'] for s in REF_SECTIONS])
    nsec = len(REF_SECTIONS)
    for i, sec in enumerate(REF_SECTIONS):
        toc.append(("sec", sec['title'], bk.page))
        secref = (sec['tag'], sec['title'], i, nsec)
        drop = section_opener(bk, sec, i, nsec)
        story = P.render_blocks(sec['blocks'], bk.styles, w, t.base)
        P.flow(bk, story, part="Part One  Field Reference", sec=secref,
               first_page_drop=drop, folio=True)

    # --- PART TWO
    bk.to_recto()
    toc.append(("part", "Part Two: The Deployment Log", bk.page))
    part_title(bk, "Part Two", "THE | DEPLOYMENT | LOG",
               "Thirty deployments, four pages each. Site Record, two sheets of "
               "contacts, and a debrief completed at the site.",
               ["Deployment index", "How a deployment works",
                "Deployments 01 through %02d" % N_DEPLOY])
    deployment_howto(bk)
    bk.to_recto()
    toc.append(("sec", "Deployment Index", bk.page))
    deployment_index(bk)

    bk.to_verso()
    toc.append(("sec", "Deployments 01 to %02d" % N_DEPLOY, bk.page))
    for n in range(1, N_DEPLOY + 1):
        partname = "Part Two  Deployment Log"
        secref = None
        bk.fill_for(n, "site")
        F.site_record(bk, n)
        bk.end_page(kind="log", part=partname, label="Deployment %02d" % n)
        bk.fill_for(n, "qsoA")
        F.qso_log(bk, n, 1, "A")
        bk.end_page(kind="log", part=partname, label="Deployment %02d" % n)
        bk.fill_for(n, "qsoB")
        F.qso_log(bk, n, 2, "B")
        bk.end_page(kind="log", part=partname, label="Deployment %02d" % n)
        bk.fill_for(n, "debrief")
        F.debrief(bk, n)
        bk.end_page(kind="log", part=partname, label="Deployment %02d" % n)

    # --- PART THREE
    bk.to_recto()
    toc.append(("part", "Part Three: Station Records", bk.page))
    part_title(bk, "Part Three", "STATION | RECORDS",
               "The part that outlives this volume. When the log fills up, "
               "photograph these pages before the book goes on the shelf.",
               ["Equipment register", "Modification and repair log",
                "Antenna build sheets", "Battery and power log",
                "QSL and confirmation tracker", "Worked All States",
                "Entities worked", "Parks and summits activated",
                "Nets, schedules, and contacts", "Overflow QSO sheets",
                "Field notes"])
    part_three_pages(bk, toc)

    # --- colophon
    bk.to_recto()
    toc.append(("part", "Colophon", bk.page))
    colophon(bk)

    n = bk.finish(pad_to_multiple=2)
    return n, toc


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else "out"
    os.makedirs(outdir, exist_ok=True)
    results = {}
    for key in ["6x9", "8.5x11"]:
        tmp = os.path.join(outdir, "_pass1_%s.pdf" % key.replace(".", ""))
        n1, toc = build(key, tmp)
        final = os.path.join(outdir, "FieldRecord_interior_%s.pdf" %
                             key.replace(".", "_"))
        n2, _ = build(key, final, toc_in=toc)
        assert n1 == n2, "page count drift %s: %d vs %d" % (key, n1, n2)
        os.remove(tmp)
        results[key] = (final, n2)
        print("%-8s  %3d pages  ->  %s" % (key, n2, final))
    return results


if __name__ == "__main__":
    main()
