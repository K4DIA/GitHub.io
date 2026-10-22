# -*- coding: utf-8 -*-
"""One entry point that turns a plain dictionary into a finished PDF.

The command line reads YAML off a disk and writes a file. A browser has
neither, so everything here works in memory and takes ordinary Python data:

    import webapi
    out = webapi.build({"station": {"callsign": "N0CALL"}})
    out["pdf"]        # bytes, ready to hand to the visitor
    out["pages"]      # how long it came out

The same functions answer the questions a form has to ask before it can draw
itself, so the list of radios, sections and states lives in one place and the
form cannot drift out of step with the generator.

Nothing here reaches the network or keeps anything. Under Pyodide the whole
thing runs inside the visitor's tab.
"""
import os
import tempfile

import build as BLD
import config as CFG
import content_ref_a as A
import content_ref_b as B
import make_book
import personalize
import radiocard
from engine import TRIMS


class BuildError(ValueError):
    """Something the visitor can fix, phrased for the visitor."""


REF_TAGS = [x['tag'] for x in A.SECTIONS_A + B.SECTIONS_B]
REF_TITLES = {x['tag']: x['title'] for x in A.SECTIONS_A + B.SECTIONS_B}

PRESET_NOTES = {
    "full": "Everything.",
    "log-only": "Covers, title, contents and the deployments.",
    "field": "The reference you use on site, without the station records.",
    "reference-only": ("The field reference without the paper log. For operators "
                       "who log on a computer and still want the manual on site."),
}

# What the buttons say. Keys are stable; these are for people.
PRESET_LABELS = {
    "full": "Full book",
    "field": "Field",
    "log-only": "Log only",
    "reference-only": "Reference only",
}


# --------------------------------------------------------------------------
# what the form needs to know
# --------------------------------------------------------------------------
def catalogue(root="."):
    """Every choice the generator will accept, in the order a form should
    show them. The web page builds its controls from this and from nothing
    else, so adding a radio card or a reference section reaches the form
    without anybody editing JavaScript."""
    return {
        "license_classes": [{"key": k, "label": CFG.CLASS_NAME[k]}
                            for k in CFG.CLASSES],
        "states": [{"code": c, "name": n,
                    "fips": CFG.STATE_FIPS.get(c, ""),
                    "sections": CFG.STATE_SECTIONS.get(c, []),
                    "time_zone": CFG.STATE_TZ.get(c, "UTC")}
                   for c, n in sorted(CFG.STATE_NAMES.items(),
                                      key=lambda kv: kv[1])],
        "section_names": dict(CFG.SECTION_NAMES),
        "parts": [{"key": k, "label": d} for k, d in CFG.PARTS],
        "reference": [{"tag": x['tag'], "title": x['title']}
                      for x in A.SECTIONS_A + B.SECTIONS_B],
        "records": [{"key": k, "title": BLD.RECORD_TITLES[k]}
                    for k in BLD.RECORD_ORDER],
        "presets": [{"key": k, "label": PRESET_LABELS.get(k, k),
                     "note": PRESET_NOTES.get(k, ""),
                     "include": _preset_shape(k)}
                    for k in ("full", "field", "log-only", "reference-only")],
        "radios": radios(root),
        "limits": {"deployments": [1, 60], "pages_per_deployment": 4},
        # The counts a form offers. Any value inside the limits still builds.
        "deployment_choices": [1, 3, 5, 10, 15, 20, 25, 30, 40, 50, 60],
        "defaults": {"license_class": "general", "deployments": 25,
                     "trim": "personal", "color": True},
    }


def _preset_shape(name):
    """A preset as the switches a form would have to set."""
    sec = CFG.Sections(dict(CFG.PRESETS[name]), REF_TAGS, BLD.RECORD_ORDER)
    return {"parts": dict(sec.flags), "reference": list(sec.reference),
            "records": list(sec.records)}


def radios(root="."):
    """The shipped cards, each with the line it prints about its own sources.

    Depth is stated because the cards are not equally good: one was written
    from a radio and the rest were restated from manuals, and an operator
    choosing a card deserves to know which is which before it goes in a book
    they will trust in the field.
    """
    out = []
    for name in radiocard.available(root):
        try:
            card = radiocard.load(name, root)
        except (ValueError, OSError, RuntimeError):
            continue
        blocks = [b["head"] for b in radiocard.blocks_for(card)]
        out.append({
            "id": name,
            "name": str(card.get("name") or name),
            "maker": str(card.get("maker") or ""),
            "verified": " ".join(str(card.get("verified") or "").split()),
            "blocks": blocks,
        })
    out.sort(key=lambda r: (r["maker"].lower(), r["name"].lower()))
    return out


# --------------------------------------------------------------------------
# building
# --------------------------------------------------------------------------
def station(config, root=".", repeaters_csv=None, nets_csv=None, tmpdir=None):
    """Turn a config dictionary into a Station, ready to lay out.

    CSV text can be handed in directly, which is what a browser has after
    somebody picks a file. It is written to a scratch file because that is
    what the loader reads, and the scratch file never leaves the process.
    """
    raw = _plain(config)
    if not isinstance(raw, dict):
        raise BuildError("the configuration should be a mapping, not a %s"
                         % type(raw).__name__)
    raw = dict(raw)
    data = dict(raw.get("data") or {})

    keep = []
    if repeaters_csv:
        data["repeaters"] = _scratch(repeaters_csv, "repeaters.csv", tmpdir)
        keep.append(data["repeaters"])
    if nets_csv:
        data["nets"] = _scratch(nets_csv, "nets.csv", tmpdir)
        keep.append(data["nets"])
    if data:
        raw["data"] = data

    try:
        st = CFG.Station(raw, root=root)
        st.choose(REF_TAGS, BLD.RECORD_ORDER)
    except CFG.ConfigError as e:
        _clean(keep)
        raise BuildError(str(e))
    personalize.apply(st)
    st._scratch_files = keep
    return st


def build(config, root=".", progress=None, repeaters_csv=None,
          nets_csv=None, filled=None, bare=False):
    """Build one book. Returns the PDF bytes and what went into it.

    progress, if given, is called with a short line each time the layout
    starts another pass, so a page can show something moving during the wait.
    """
    st = station(config, root=root, repeaters_csv=repeaters_csv,
                 nets_csv=nets_csv)
    # filled is {deployment_number: {slot: {"fields": {...}, "rows": [...]}}}.
    # Absent, the book is the blank book.
    st.filled = filled or {}
    st.bare = bool(bare)
    try:
        pages, pdf = make_book.render(st, root=root, note=progress)
    except make_book.PageCountMoved as e:
        raise BuildError(str(e))
    except CFG.ConfigError as e:
        raise BuildError(str(e))
    except FileNotFoundError as e:
        raise BuildError(str(e))
    finally:
        _clean(getattr(st, "_scratch_files", []))

    sec = st.sections
    return {
        "pdf": pdf,
        "pages": pages,
        "sheets": (pages + 1) // 2,
        "filename": filename(st),
        "byline": st.byline,
        "license_class": st.class_name,
        "place": st.place(),
        "time_zone": st.tz_name,
        "utc_rollover": st.utc_rollover(),
        "section_ambiguous": st.section_ambiguous,
        "section_choices": list(st.section_choices),
        "left_out": [k for k in CFG.PART_KEYS if not sec.on(k)],
        "reference": list(sec.reference),
        "records": list(sec.records),
        "deployments": st.ndep,
    }


PAGE_TABLE = "pagesizes.json"


def estimate(config, root="."):
    """About how long this book will come out, without building it.

    Measured figures, added up. It is close but it is not exact: pages come in
    leaves, so a part that half fills one can look free until its neighbour
    goes too, and the real count lands within a leaf or two of this. The form
    says about, and means it.

    Returns None if the table has not been measured, so a page can leave the
    line out rather than print a made-up number.
    """
    import json
    path = os.path.join(root, PAGE_TABLE)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        tab = json.load(fh)

    st = station(config, root=root)
    _clean(getattr(st, "_scratch_files", []))
    sec = st.sections

    n = 0
    for k, cost in tab["front"].items():
        if sec.on(k):
            n += cost
    if sec.on("cover"):
        n += tab["back"]["cover"]

    for k, cost in tab["parts"].items():
        if k == "deployment_howto":
            continue
        if sec.on(k):
            n += cost
    if sec.on("part_two") and not sec.on("deployment_howto"):
        n -= tab["parts"].get("deployment_howto", 0)

    for tag, cost in tab["reference"].items():
        if tag in sec.reference:
            n += cost
    for key, cost in tab["records"].items():
        if key in sec.records:
            n += cost
    if sec.on("radios"):
        for name in st.radios:
            n += tab["radios"].get(name, 2)
    if sec.on("part_two"):
        n += tab["per_deployment"] * st.ndep

    n = max(2, n)
    return n + (n % 2)


def filename(st):
    """A file name the visitor will recognise in their downloads folder."""
    stem = "".join(ch for ch in (st.callsign or "book")
                   if ch.isalnum() or ch in "-_") or "book"
    return "FieldRecord_%s.pdf" % stem


def check(config, root="."):
    """Read a config without building. Returns a list of complaints, empty if
    it would build."""
    try:
        st = station(config, root=root)
    except BuildError as e:
        return [str(e)]
    problems = []
    for name in st.radios:
        try:
            radiocard.load(name, root)
        except (FileNotFoundError, ValueError) as e:
            problems.append(str(e))
    if st.trim not in TRIMS:
        problems.append("the layout engine has no trim called %r" % st.trim)
    _clean(getattr(st, "_scratch_files", []))
    return problems


# --------------------------------------------------------------------------
def _plain(v):
    """Convert whatever a JavaScript caller handed over into Python data.

    Pyodide passes objects across as proxies. They behave like dictionaries
    for most purposes and then fail somewhere deep in the layout, so they are
    converted once, here, where the error would still make sense.
    """
    if hasattr(v, "to_py"):
        return _plain(v.to_py())
    if isinstance(v, dict):
        return {str(k): _plain(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    return v


def _scratch(text, name, tmpdir=None):
    d = tmpdir or tempfile.mkdtemp(prefix="fieldrecord-")
    path = os.path.join(d, name)
    if isinstance(text, bytes):
        text = text.decode("utf-8-sig", "replace")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _clean(paths):
    for p in paths:
        try:
            os.remove(p)
            os.rmdir(os.path.dirname(p))
        except OSError:
            pass
