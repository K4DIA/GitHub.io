# -*- coding: utf-8 -*-
"""Repeater and net data for FIELD RECORD.

Two CSV files, both optional. Column names are matched loosely, so a Chirp
export, a RepeaterBook export and a list typed by hand all load without
editing. Nothing here reaches the network; fetch_repeaters.py does that, and
writes a file this module reads.

Repeater columns, any casing, any order:

    output      required, MHz
    input       or 'offset' or 'duplex' plus 'offset'
    tone        encode tone in Hz, or 'none'
    call        the licensee
    location    town or landmark
    system      the linked system or club, used for the colour chip
    band        optional, otherwise derived from the output frequency

Net columns:

    net, day, time, where, notes
"""
import csv
import os
import re

ALIASES = {
    "output": ["output", "freq", "frequency", "output freq",
               "output frequency", "rx freq", "receive"],
    "input": ["input", "input freq", "input frequency", "tx freq",
              "transmit"],
    "offset": ["offset", "shift", "duplex offset", "offset freq"],
    "duplex": ["duplex", "sh", "direction", "shift direction"],
    "tone": ["tone", "ctcss", "rtone", "encode", "pl", "ctcss tone",
             "tone freq", "uplink tone"],
    "dtcs": ["dtcs", "dcs", "dtcscode", "dtcs code", "dcs code"],
    "call": ["call", "callsign", "call sign", "licensee", "name"],
    "location": ["location", "nearest city", "city", "landmark", "site",
                 "place", "comment"],
    "system": ["system", "network", "link", "linked system", "affiliate",
               "sponsor", "club", "group"],
    "band": ["band"],
    "notes": ["notes", "note", "remarks", "comments"],
    "mode": ["mode", "fm mode", "operating mode"],
    "state": ["state", "st"],
    "county": ["county"],
}

NET_ALIASES = {
    "net": ["net", "name", "net name", "title"],
    "day": ["day", "days", "when"],
    "time": ["time", "local", "local time", "start", "start time"],
    "where": ["where", "frequency", "freq", "repeater", "system", "channel"],
    "notes": ["notes", "note", "remarks", "description", "comments"],
}

BAND_EDGES = [
    ("160", 1.8, 2.0), ("80", 3.5, 4.0), ("60", 5.3, 5.5), ("40", 7.0, 7.3),
    ("30", 10.1, 10.15), ("20", 14.0, 14.35), ("17", 18.0, 18.2),
    ("15", 21.0, 21.45), ("12", 24.8, 25.0), ("10", 28.0, 29.7),
    ("6", 50.0, 54.0), ("2", 144.0, 148.0), ("1.25", 222.0, 225.0),
    ("70cm", 420.0, 450.0), ("33cm", 902.0, 928.0), ("23cm", 1240.0, 1300.0),
]


def band_of(mhz):
    for name, lo, hi in BAND_EDGES:
        if lo <= mhz <= hi:
            return name
    return ""


def _strip(rows):
    """Drop blank rows and leading comment lines, which carry the source note."""
    out = []
    for r in rows:
        if not any((c or "").strip() for c in r):
            continue
        if (r[0] or "").lstrip().startswith("#"):
            continue
        out.append(r)
    return out


def _key(s):
    return re.sub(r"[^a-z0-9 ]+", "", (s or "").strip().lower())


# Chirp's own column names overlap ours but mean different things: its
# "Location" is the memory channel number and its "Tone" is a mode selector,
# not a frequency. Detect a Chirp export and map it explicitly.
CHIRP_SIGNATURE = ("rtonefreq", "dtcscode")
CHIRP_MAP = {
    "output": "frequency", "duplex": "duplex", "offset": "offset",
    "tone": "rtonefreq", "tone_mode": "tone", "call": "name",
    "location": "comment", "mode": "mode", "dtcs": "dtcscode",
}


def is_chirp(header):
    cols = {_key(h) for h in header}
    return all(s in cols for s in CHIRP_SIGNATURE)


def _index(header, aliases):
    """Map our field names to column positions in this file."""
    cols = {_key(h): i for i, h in enumerate(header)}
    if aliases is ALIASES and is_chirp(header):
        return {f: cols[c] for f, c in CHIRP_MAP.items() if c in cols}
    out = {}
    for field, names in aliases.items():
        for n in names:
            if n in cols:
                out[field] = cols[n]
                break
    return out


def _get(row, idx, field, default=""):
    i = idx.get(field)
    if i is None or i >= len(row):
        return default
    return (row[i] or "").strip()


def _mhz(v):
    """Repeater output, to three places, four only when they carry meaning."""
    t = ("%.4f" % v).rstrip("0")
    whole, _, frac = t.partition(".")
    return "%s.%s" % (whole, frac.ljust(3, "0"))


def _num(s):
    try:
        return float(str(s).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


# Chirp tone modes. Only these actually send a CTCSS tone on transmit; DTCS
# and the cross modes send something else, and the tone column is left at its
# default, so printing it would send an operator to the wrong code.
CTCSS_MODES = ("tone", "tsql")


def _tone(s, mode=None):
    """The encode tone, or a word saying there is not one."""
    if mode is not None:
        m = (mode or "").strip().lower()
        if not m:
            return "none"
        if m.startswith("dtcs") or m.startswith("dcs"):
            return "DTCS"
        if m not in CTCSS_MODES:
            return m.upper()          # Cross, and anything else Chirp adds
    s = (s or "").strip()
    if not s or s.lower() in ("none", "off", "-", "carrier"):
        return "none"
    v = _num(s)
    if v is None:
        return s
    if v <= 0:
        return "none"
    return "%.1f" % v


def _shift(out_mhz, idx, row):
    """Return '+', '-' or '' for the input shift, however the file states it.

    Chirp overloads its columns: with duplex "split" the offset column holds
    the absolute transmit frequency rather than a difference, and duplex "off"
    means the channel does not transmit at all. Reading either as a plain
    offset turns every one of them into a plus.
    """
    dup = _get(row, idx, "duplex").strip().lower()
    if dup in ("+", "-"):
        return dup
    if dup.startswith("plus"):
        return "+"
    if dup.startswith("minus") or dup.startswith("neg"):
        return "-"
    if dup in ("off", "none"):
        return ""                    # receive only
    if dup in ("simplex", "s"):
        return ""

    inp = _num(_get(row, idx, "input"))
    off = _num(_get(row, idx, "offset"))
    if dup == "split" and off is not None and out_mhz is not None:
        # an absolute transmit frequency, not a difference
        d = off - out_mhz
        return "+" if d > 0.0005 else ("-" if d < -0.0005 else "")
    if inp is not None and out_mhz is not None:
        d = inp - out_mhz
        if abs(d) > 0.0005:
            return "+" if d > 0 else "-"
        return ""
    if off is not None and abs(off) > 0.0005:
        return "+" if off > 0 else "-"
    return ""


def load_repeaters(path):
    """Read a repeater CSV. Returns {band: [rows]} where each row is
    (output, shift, tone, call, location, system)."""
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rd = list(csv.reader(fh))
    rd = _strip(rd)
    if len(rd) < 2:
        return {}
    idx = _index(rd[0], ALIASES)
    if "output" not in idx:
        raise ValueError("%s has no output frequency column. Expected one of: "
                         "%s" % (path, ", ".join(ALIASES["output"])))
    out = {}
    for row in rd[1:]:
        mhz = _num(_get(row, idx, "output"))
        if mhz is None:
            continue
        band = _get(row, idx, "band") or band_of(mhz)
        if not band:
            continue
        tone_mode = _get(row, idx, "tone_mode", None) if "tone_mode" in idx \
            else None
        tone = _tone(_get(row, idx, "tone"), tone_mode)
        if tone == "DTCS":
            code = _get(row, idx, "dtcs")
            tone = ("D" + code) if code else "DTCS"
        rec = (
            _mhz(mhz),
            _shift(mhz, idx, row),
            tone,
            _get(row, idx, "call").upper(),
            _get(row, idx, "location"),
            _get(row, idx, "system"),
        )
        out.setdefault(band, []).append(rec)
    for band in out:
        out[band].sort(key=lambda r: float(r[0]))
    return out


def load_nets(path):
    """Read a net CSV. Returns a list of (net, day, time, where, notes)."""
    if not path or not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        rd = list(csv.reader(fh))
    rd = _strip(rd)
    if len(rd) < 2:
        return []
    idx = _index(rd[0], NET_ALIASES)
    out = []
    for row in rd[1:]:
        name = _get(row, idx, "net")
        if not name:
            continue
        out.append((name, _get(row, idx, "day"), _get(row, idx, "time"),
                    _get(row, idx, "where"), _get(row, idx, "notes")))
    return out
