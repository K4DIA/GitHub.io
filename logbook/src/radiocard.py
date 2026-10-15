# -*- coding: utf-8 -*-
"""Radio quick reference pages, built from a data file.

One YAML file per radio in radios/. Every block is optional except the name,
so a card can be nothing but specifications and a place to write settings down,
which is the honest floor for a radio the author has never had on the bench.

The layout is a two column packer: blocks are measured, then dealt into
columns, then onto further pages if they do not fit.

Block kinds, in the order a card normally uses them:

    keys      (group, key, description)      front panel and menu keys
    quick     (code, name, note)             a quick set or function menu
    filters   (name, note)                   what is fitted and what it is for
    specs     (label, value)                 the radio itself
    tasks     (name, steps)                  common operations
    trouble   (symptom, what to check)       fault finding, in order
    notes     [string]                       operating notes
    control   (label, value)                 computer control, CI-V or CAT
    settings  [label]                        ruled lines to fill in
    memory    -                              a ruled memory plan table
"""
import json
import os


from engine import (INK, G25, G35, G50, G70, W_HAIR, W_RULE,
                    SERIF, SERIF_I, COND, COND_SB, COND_B,
                    fit_text, fit_tracked, wrap_lines,
                    CLR, SLATE, SLATE_MID, SLATE_PALE, AMBER,
                    band_color)
from forms import page_header, blockhead

try:
    import yaml
except ImportError:                                   # pragma: no cover
    yaml = None

RADIO_DIR = "radios"

BODY = 7.1
LEAD = 9.5
HEAD_H = 18.0            # blockhead consumes this much before the first row
GAP = 9.0                # between blocks


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))


def search_dirs(root="."):
    """A station file may sit anywhere; the shipped cards live beside the code.

    The operator's own radios/ directory wins, so a local card can override or
    extend what the project ships.
    """
    out, seen = [], set()
    for d in (os.path.join(root, RADIO_DIR), os.path.join(HERE, RADIO_DIR)):
        d = os.path.abspath(d)
        if d not in seen and os.path.isdir(d):
            out.append(d)
            seen.add(d)
    return out


def _find(stem, root="."):
    """The card file, whichever form it is in.

    Cards are written as YAML because that is what a person can edit. The
    browser build carries the same cards converted to JSON, so a runtime with
    no YAML parser can still read them, and a card written by hand still wins
    over one that was converted.
    """
    for d in search_dirs(root):
        for ext in (".yml", ".json"):
            p = os.path.join(d, stem + ext)
            if os.path.exists(p):
                return p
    return ""


def _read(path):
    with open(path, "r", encoding="utf-8") as fh:
        if path.endswith(".json"):
            d = json.load(fh)
        elif yaml is None:
            raise RuntimeError("PyYAML is not installed. Run: "
                               "pip install pyyaml")
        else:
            d = yaml.safe_load(fh)
    if d is None:
        d = {}
    if not isinstance(d, dict):
        raise ValueError("%s should be a mapping of blocks, not a %s. See "
                         "docs/RADIOS.md." % (path, type(d).__name__))
    return d


def load(name, root="."):
    """Read radios/<name>.yml. Accepts the name with or without extension."""
    stem = name
    for ext in (".yml", ".json"):
        if stem.endswith(ext):
            stem = stem[:-len(ext)]
    path = _find(stem, root)
    if not path:
        raise FileNotFoundError(
            "no radio card named %r. Available: %s"
            % (stem, ", ".join(available(root)) or "none"))
    d = _read(path)
    # `include:` pulls in shared blocks, so one description of Icom CI-V or the
    # Yaesu menu serves the whole family and a correction is made once. The
    # card's own keys always win.
    inc = d.pop("include", None) or []
    if isinstance(inc, str):
        inc = [inc]
    for other in inc:
        ip = _find(str(other), root)
        if not ip:
            raise ValueError("%s includes %r, which is not in radios/"
                             % (path, other))
        base = _read(ip)
        base.pop("include", None)
        base.pop("name", None)
        for k, v in base.items():
            d.setdefault(k, v)
    d.setdefault("name", stem)
    return d


SHARED_PREFIX = "_"


def available(root="."):
    """Card names a station file can ask for. Shared blocks start with _."""
    names = set()
    for d in search_dirs(root):
        for f in os.listdir(d):
            if f.startswith(SHARED_PREFIX):
                continue
            for ext in (".yml", ".json"):
                if f.endswith(ext):
                    names.add(f[:-len(ext)])
    return sorted(names)


# --------------------------------------------------------------------------
# measuring, so a block is never drawn past the foot of a column
# --------------------------------------------------------------------------
def _rows(v):
    """Normalise whatever the YAML held into tuples of strings.

    A block given as a single string is one row, not one row per character,
    and a number is a string once it reaches the page.
    """
    if v is None:
        return []
    if isinstance(v, (str, int, float)):
        return [(str(v),)]
    out = []
    for r in v:
        if isinstance(r, (str, int, float)) or r is None:
            out.append((("" if r is None else str(r)),))
        else:
            out.append(tuple("" if c is None else str(c) for c in r))
    return out


def _lines(text, font, size, width):
    return max(1, len(wrap_lines(str(text), font, size, max(width, 12))))


def measure(block, w):
    kind, rows = block["kind"], block["rows"]
    h = HEAD_H if block.get("head") else 0.0
    if kind == "keys":
        for r in rows:
            h += _lines(r[2] if len(r) > 2 else "", SERIF, 6.9, w - 72) * 9.0
            h += 3.4
    elif kind == "quick":
        for r in rows:
            h += 9.2 + _lines(r[2] if len(r) > 2 else "", SERIF, 6.9,
                              w - 22) * 9.0 + 3.0
    elif kind in ("filters", "tasks", "trouble"):
        lead = 9.4 if kind != "tasks" else 10.0
        for r in rows:
            h += lead + _lines(r[1] if len(r) > 1 else "", SERIF, BODY,
                               w - (8 if kind != "tasks" else 0)) * LEAD
            h += 3.6 if kind != "tasks" else 5.0
    elif kind in ("specs", "control"):
        for r in rows:
            if kind == "specs":
                h += _lines(r[1] if len(r) > 1 else "", SERIF, 7.0,
                            w * 0.56) * 9.2 + 2.4
            else:
                h += 9.6 + _lines(r[1] if len(r) > 1 else "", SERIF, BODY,
                                  w) * LEAD + 4.0
    elif kind == "notes":
        for r in rows:
            h += _lines(r[0], SERIF, BODY, w - 10) * LEAD + 3.6
    elif kind == "settings":
        h += 17.0 * len(rows)
    elif kind == "memory":
        h += 17.0 + 13.2 * int(block.get("min_rows", 12))
    return h


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------
def draw(bk, block, x, y, w, floor):
    c = bk.c
    kind, rows = block["kind"], block["rows"]
    ink = SLATE if CLR.on else INK
    dim = SLATE_MID if CLR.on else G70
    hot = AMBER if CLR.on else INK

    if block.get("head"):
        y = blockhead(bk, x, y, w, block["head"], right=block.get("right", ""))

    if kind == "keys":
        chip = band_color("20") if CLR.on else G50
        for r in rows:
            grp, key, desc = (list(r) + ["", "", ""])[:3]
            if grp:
                c.setFillColor(chip)
                c.rect(x, y - 1.5, 15, 8.5, stroke=0, fill=1)
                fit_text(c, x + 7.5, y + 0.6, grp, COND_B, 5.8, 13,
                         SLATE_PALE if CLR.on else INK, align="c")
            fit_tracked(c, x + 19, y + 0.6, key, COND_B, 6.8, 48, 0.6, ink)
            c.setFillColor(ink)
            c.setFont(SERIF, 6.9)
            yy = y + 0.6
            for ln in wrap_lines(desc, SERIF, 6.9, w - 72):
                c.drawString(x + 71, yy, ln)
                yy -= 9.0
            y = yy - 3.4

    elif kind == "quick":
        for r in rows:
            code, name, note = (list(r) + ["", "", ""])[:3]
            fit_tracked(c, x, y, code, COND_B, 6.8, 20, 0.6, hot)
            fit_tracked(c, x + 22, y, name.upper(), COND_B, 6.4, w - 24, 0.6, ink)
            y -= 9.2
            c.setFillColor(dim)
            c.setFont(SERIF, 6.9)
            for ln in wrap_lines(note, SERIF, 6.9, w - 22):
                c.drawString(x + 22, y, ln)
                y -= 9.0
            y -= 3.0

    elif kind in ("filters", "trouble"):
        for r in rows:
            name, note = (list(r) + ["", ""])[:2]
            fit_tracked(c, x, y, name.upper(), COND_B, 6.6, w, 0.7,
                        hot if kind == "trouble" else ink)
            y -= 9.4
            c.setFillColor(dim if kind == "filters" else ink)
            c.setFont(SERIF, 7.0)
            for ln in wrap_lines(note, SERIF, 7.0, w - 8):
                c.drawString(x + 8, y, ln)
                y -= 9.4
            y -= 3.6

    elif kind == "tasks":
        for r in rows:
            name, steps = (list(r) + ["", ""])[:2]
            fit_tracked(c, x, y, name.upper(), COND_B, 7.0, w, 0.8, ink)
            y -= 10.0
            c.setFillColor(ink)
            c.setFont(SERIF, BODY)
            for ln in wrap_lines(steps, SERIF, BODY, w):
                c.drawString(x, y, ln)
                y -= LEAD
            y -= 5.0

    elif kind == "specs":
        for r in rows:
            k, v = (list(r) + ["", ""])[:2]
            fit_tracked(c, x, y, k.upper(), COND_B, 6.2, w * 0.42, 0.7, dim)
            c.setFillColor(ink)
            c.setFont(SERIF, 7.0)
            yy = y
            for ln in wrap_lines(v, SERIF, 7.0, w * 0.56):
                c.drawString(x + w * 0.44, yy, ln)
                yy -= 9.2
            y = yy - 2.4

    elif kind == "control":
        for r in rows:
            k, v = (list(r) + ["", ""])[:2]
            fit_tracked(c, x, y, k.upper(), COND_B, 6.6, w, 0.8, hot)
            y -= 9.6
            c.setFillColor(ink)
            c.setFont(SERIF, BODY)
            for ln in wrap_lines(v, SERIF, BODY, w):
                c.drawString(x, y, ln)
                y -= LEAD
            y -= 4.0

    elif kind == "notes":
        for r in rows:
            c.setFillColor(hot if CLR.on else G50)
            c.circle(x + 2, y + 2.4, 1.5, stroke=0, fill=1)
            c.setFillColor(ink)
            c.setFont(SERIF, BODY)
            for ln in wrap_lines(r[0], SERIF, BODY, w - 10):
                c.drawString(x + 9, y, ln)
                y -= LEAD
            y -= 3.6

    elif kind == "settings":
        for r in rows:
            fit_tracked(c, x, y + 2.6, r[0].upper(), COND_SB, 6.0, w * 0.5,
                        0.85, dim)
            c.setStrokeColor(G35)
            c.setLineWidth(W_RULE)
            c.line(x + w * 0.52, y, x + w, y)
            y -= 17.0

    elif kind == "memory":
        y = _memory_grid(bk, x, y, w, floor)

    return y


def _lined(bk, x, y, w, floor, head):
    """Ruled writing lines filling the rest of a column."""
    c = bk.c
    y = blockhead(bk, x, y, w, head)
    rh = 13.2
    n = max(3, int((y - floor) // rh))
    c.setStrokeColor(G25)
    c.setLineWidth(W_HAIR)
    for i in range(n):
        yy = y - (i + 1) * rh + 3
        c.line(x, yy, x + w, yy)
    return y - n * rh


def _memory_grid(bk, x, y, w, floor):
    c = bk.c
    heads = ["CH", "FREQUENCY", "MODE", "SHIFT / TONE", "WHAT IT IS"]
    fr = [0.09, 0.24, 0.10, 0.20, 0.37]
    hx = x
    for hd, f in zip(heads, fr):
        fit_tracked(c, hx, y, hd, COND_B, 5.8, w * f - 3, 0.7,
                    SLATE_MID if CLR.on else G70)
        hx += w * f
    y -= 4
    c.setStrokeColor(AMBER if CLR.on else G70)
    c.setLineWidth(1.0)
    c.line(x, y, x + w, y)
    rh = 13.2
    n = max(6, int((y - floor) // rh))
    for i in range(n):
        ry = y - (i + 1) * rh
        if CLR.on and i % 2 == 1:
            c.setFillColor(SLATE_PALE)
            c.rect(x, ry, w, rh, stroke=0, fill=1)
        c.setStrokeColor(G25)
        c.setLineWidth(W_HAIR)
        c.line(x, ry, x + w, ry)
    cx = x
    for f in fr[:-1]:
        cx += w * f
        c.setStrokeColor(G25)
        c.setLineWidth(W_HAIR)
        c.line(cx, y, cx, y - n * rh)
    c.setStrokeColor(SLATE_MID if CLR.on else G70)
    c.setLineWidth(W_RULE)
    c.rect(x, y - n * rh, w, n * rh, stroke=1, fill=0)
    return y - n * rh


# --------------------------------------------------------------------------
# assembling a card
# --------------------------------------------------------------------------
ORDER = [
    ("keys", "Menu and panel keys", "what the buttons do"),
    ("quick", "Quick set", ""),
    ("filters", "Filters", ""),
    ("specs", "Specifications", ""),
    ("tasks", "Common operations", ""),
    ("trouble", "Fault finding", "in this order"),
    ("notes", "Operating notes", ""),
    ("control", "Computer control", ""),
]


def blocks_for(card):
    out = []
    for key, head, right in ORDER:
        rows = _rows(card.get(key))
        if not rows:
            continue
        b = {"kind": key, "rows": rows,
             "head": card.get(key + "_head", head),
             "right": card.get(key + "_right", right)}
        out.append(b)
    settings = _rows(card.get("settings")) or _rows(DEFAULT_SETTINGS)
    out.append({"kind": "settings", "rows": settings,
                "head": "Station settings", "right": "fill this in once"})
    out.append({"kind": "memory", "rows": [], "head": "Memory plan",
                "right": "write it down before you need it", "min_rows": 12})
    return out


DEFAULT_SETTINGS = [
    "Serial or CAT address", "Serial or CAT baud", "Filters fitted",
    "CW pitch", "Mic gain", "SSB power, field", "CW power, field",
    "Break-in setting", "Tuner fitted", "Memory bank scheme",
    "Reset key sequence", "Firmware or model variant",
]


def render(bk, card, part="Part One  Field Reference"):
    """Lay the card out over as many pages as it needs. Returns page count.

    The memory grid is elastic and takes the tail of whatever column it lands
    in.
    """
    name = str(card.get("name") or "Radio")
    subtitle = str(card.get("subtitle") or "Quick reference")
    disclaimer = (card.get("disclaimer") or "").strip()
    sources = card.get("sources") or []
    blocks = blocks_for(card)

    verified = (card.get("verified") or "").strip()
    foot_text = disclaimer
    if verified:
        foot_text = (verified.rstrip(".") + ". " + foot_text).strip()
    if sources:
        joined = "Compiled from: " + "; ".join(str(s) for s in sources) + "."
        foot_text = (foot_text.rstrip() + "  " + joined).strip()

    pages, idx = 0, 0
    oversized = []
    while idx < len(blocks):
        c = bk.c
        x, y0, w, h0 = bk.body()
        big = subtitle if pages == 0 else "%s, continued" % subtitle
        y = page_header(bk, name, big=big)
        if pages == 0 and card.get("kicker"):
            fit_tracked(c, x, y - 8, str(card["kicker"]).upper(), COND, 6.2, w,
                        0.9, SLATE_MID)
            y -= 18
        else:
            y -= 4

        colw = (w - 20) / 2.0
        xs = [x, x + colw + 20]
        floor = y0 + 6

        # room for the footer, measured rather than guessed
        foot = 0.0
        foot_lines = []
        if foot_text:
            foot_lines = wrap_lines(foot_text, SERIF_I, 7.0, w)
            foot = 22.0 + 9.0 * len(foot_lines) + 8.0

        room = y - (floor + foot)
        rest = blocks[idx:]

        # How many blocks fit on this page, and where to break the columns.
        # The split is chosen to minimise the taller column, so a page never
        # ends with one column full and the other empty.
        heights = [measure(b, colw) + GAP for b in rest]

        def best_split_for(n):
            """The split of the first n blocks that leaves the taller column
            shortest, or None when no split of n blocks fits the page."""
            best, best_k = None, None
            for k in range(1, n + 1):
                a, b2 = sum(heights[:k]), sum(heights[k:n])
                if a > room or b2 > room:
                    continue
                worst = max(a, b2)
                if best is None or worst < best:
                    best, best_k = worst, k
            return best_k

        # Take as many blocks as can actually be split across two columns.
        # Asking whether a workable split exists, rather than whether the
        # running total is under two columns, fits another block onto most
        # pages and stops a card ending with two half empty columns.
        m, split = 0, None
        while m < len(rest):
            k = best_split_for(m + 1)
            if k is None:
                break
            m, split = m + 1, k
        if split is None:
            # Nothing splits cleanly. Give the first remaining block the whole
            # of column one on its own; if it is taller than a column even
            # then, it is drawn here and reported, because silently running it
            # off the sheet is the one outcome that must not happen.
            split, m = 1, 1
            if measure(blocks[idx], colw) > room:
                oversized.append((name, blocks[idx]["kind"]))

        col, cy = 0, y
        ends = [y, y]
        for j in range(m):
            if j == split and col == 0:
                col, cy = 1, y
            b = blocks[idx]
            cy = draw(bk, b, xs[col], cy, colw, floor + foot)
            cy -= GAP
            ends[col] = cy
            idx += 1

        # A column with real depth left over gets ruled lines rather than
        # white space. The operator will fill them; the page will not look
        # unfinished either way.
        if idx >= len(blocks):
            for ci in (0, 1):
                depth = ends[ci] - (floor + foot)
                if depth > 105:
                    _lined(bk, xs[ci], ends[ci], colw, floor + foot,
                           "Notes on this radio")

        if idx >= len(blocks) and foot_lines:
            base = floor + 4
            top_of_note = base + 9.0 * len(foot_lines)
            c.setStrokeColor(AMBER if CLR.on else G70)
            c.setLineWidth(1.0)
            c.line(x, top_of_note + 7, x + w, top_of_note + 7)
            c.setFont(SERIF_I, 7.0)
            c.setFillColor(SLATE_MID if CLR.on else G70)
            yy = top_of_note - 7.0
            for ln in foot_lines:
                c.drawString(x, yy, ln)
                yy -= 9.0
        bk.end_page(kind="ref", part=part, label=name)
        pages += 1
    if oversized:
        raise ValueError(
            "radio card %s: the %s block is taller than a column. Split it "
            "into two blocks, or shorten the entries."
            % (name, ", ".join(k for _n, k in oversized)))
    return pages
