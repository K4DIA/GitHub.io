# -*- coding: utf-8 -*-
"""Station configuration for FIELD RECORD.

One YAML file describes the operator, the volume and the data sources. Every
field has a default, so a config that omits half of it still builds a book.
Nothing here touches the layout engine; it only supplies values the page
builders ask for.
"""
import os
import datetime

try:
    from zoneinfo import ZoneInfo
except ImportError:                                   # pragma: no cover
    ZoneInfo = None

# Standard and daylight offsets for the zones this book uses, so the UTC
# rollover note still prints where the tz database is unavailable.
FALLBACK_OFFSETS = {
    "America/New_York": (-5, -4), "America/Chicago": (-6, -5),
    "America/Denver": (-7, -6), "America/Phoenix": (-7, -7),
    "America/Los_Angeles": (-8, -7), "America/Anchorage": (-9, -8),
    "America/Boise": (-7, -6), "America/Detroit": (-5, -4),
    "America/Indiana/Indianapolis": (-5, -4), "America/Puerto_Rico": (-4, -4),
    "Pacific/Honolulu": (-10, -10), "Pacific/Guam": (10, 10),
    "Pacific/Pago_Pago": (-11, -11), "Pacific/Saipan": (10, 10),
    "UTC": (0, 0),
}


class _FixedZone(datetime.tzinfo):
    """A plain fixed-offset zone, used when the tz database is missing."""

    def __init__(self, name, std, dst):
        self._name, self._std, self._dst = name, std, dst

    def utcoffset(self, dt):
        # Second Sunday in March to the first Sunday in November, US rule.
        if dt is None or self._std == self._dst:
            return datetime.timedelta(hours=self._std)
        summer = 3 < dt.month < 11 or (dt.month == 3 and dt.day > 14) \
            or (dt.month == 11 and dt.day < 2)
        return datetime.timedelta(hours=self._dst if summer else self._std)

    def dst(self, dt):
        return datetime.timedelta(
            hours=(self._dst - self._std)) if self.utcoffset(dt) == \
            datetime.timedelta(hours=self._dst) else datetime.timedelta(0)

    def tzname(self, dt):
        return self._name


def zone(name):
    """The named zone, or a fixed-offset stand-in where zoneinfo is absent."""
    if ZoneInfo is not None:
        try:
            return ZoneInfo(name)
        except Exception:
            pass
    if name not in FALLBACK_OFFSETS:
        raise KeyError(name)
    std, dst = FALLBACK_OFFSETS[name]
    return _FixedZone(name, std, dst)

try:
    import yaml
except ImportError:                                   # pragma: no cover
    yaml = None


# --------------------------------------------------------------------------
# License classes, in the order the band chart shades them
# --------------------------------------------------------------------------
CLASSES = ["novice", "technician", "general", "advanced", "extra"]
CLASS_LETTER = {"novice": "N", "technician": "T", "general": "G",
                "advanced": "A", "extra": "E"}
CLASS_NAME = {"novice": "Novice", "technician": "Technician",
              "general": "General", "advanced": "Advanced", "extra": "Extra"}


# --------------------------------------------------------------------------
# State to ARRL section. A state with exactly one section fills the field in
# automatically. A state with several leaves it blank unless the config names
# one. A wrong section gets copied onto a contest exchange.
# --------------------------------------------------------------------------
STATE_SECTIONS = {
    "AK": ["AK"], "AL": ["AL"], "AR": ["AR"], "AZ": ["AZ"],
    "CA": ["SV", "EB", "LAX", "ORG", "SB", "SCV", "SDG", "SF", "SJV"],
    "CO": ["CO"], "CT": ["CT"], "DC": ["MDC"], "DE": ["DE"],
    "FL": ["NFL", "SFL", "WCF"], "GA": ["GA"], "HI": ["PAC"], "IA": ["IA"],
    "ID": ["ID"], "IL": ["IL"], "IN": ["IN"], "KS": ["KS"], "KY": ["KY"],
    "LA": ["LA"], "MA": ["EMA", "WMA"], "MD": ["MDC"], "ME": ["ME"],
    "MI": ["MI"], "MN": ["MN"], "MO": ["MO"], "MS": ["MS"], "MT": ["MT"],
    "NC": ["NC"], "ND": ["ND"], "NE": ["NE"], "NH": ["NH"],
    "NJ": ["NNJ", "SNJ"], "NM": ["NM"], "NV": ["NV"],
    "NY": ["WNY", "ENY", "NLI", "NNY"], "OH": ["OH"], "OK": ["OK"],
    "OR": ["OR"], "PA": ["EPA", "WPA"], "PR": ["PR"], "RI": ["RI"],
    "SC": ["SC"], "SD": ["SD"], "TN": ["TN"],
    "TX": ["NTX", "STX", "WTX"], "UT": ["UT"], "VA": ["VA"],
    "VI": ["VI"], "VT": ["VT"], "WA": ["EWA", "WWA"], "WI": ["WI"],
    "GU": ["PAC"], "AS": ["PAC"], "MP": ["PAC"],
    "WV": ["WV"], "WY": ["WY"],
}

SECTION_NAMES = {
    "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "EB": "East Bay", "EMA": "Eastern Massachusetts",
    "ENY": "Eastern New York", "EPA": "Eastern Pennsylvania",
    "EWA": "Eastern Washington", "GA": "Georgia", "IA": "Iowa",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "LAX": "Los Angeles",
    "MDC": "Maryland-DC", "ME": "Maine", "MI": "Michigan",
    "MN": "Minnesota", "MO": "Missouri", "MS": "Mississippi",
    "MT": "Montana", "NC": "North Carolina", "ND": "North Dakota",
    "NE": "Nebraska", "NFL": "Northern Florida", "NH": "New Hampshire",
    "NLI": "New York City-Long Island", "NM": "New Mexico",
    "NNJ": "Northern New Jersey", "NNY": "Northern New York",
    "NTX": "North Texas", "NV": "Nevada", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "ORG": "Orange", "PAC": "Pacific", "PR": "Puerto Rico",
    "RI": "Rhode Island", "SB": "Santa Barbara", "SC": "South Carolina",
    "SCV": "Santa Clara Valley", "SD": "South Dakota", "SDG": "San Diego",
    "SF": "San Francisco", "SFL": "Southern Florida",
    "SJV": "San Joaquin Valley", "SNJ": "Southern New Jersey",
    "STX": "South Texas", "SV": "Sacramento Valley", "TN": "Tennessee",
    "UT": "Utah", "VA": "Virginia", "VI": "US Virgin Islands", "VT": "Vermont",
    "WCF": "West Central Florida", "WI": "Wisconsin", "WMA":
    "Western Massachusetts", "WNY": "Western New York",
    "WPA": "Western Pennsylvania", "WTX": "West Texas",
    "WV": "West Virginia", "WWA": "Western Washington", "WY": "Wyoming",
}

STATE_NAMES = {
    "AK": "Alaska", "AL": "Alabama", "AR": "Arkansas", "AZ": "Arizona",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DC": "District of Columbia", "DE": "Delaware", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "IA": "Iowa", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "MA": "Massachusetts", "MD": "Maryland",
    "ME": "Maine", "MI": "Michigan", "MN": "Minnesota", "MO": "Missouri",
    "MS": "Mississippi", "MT": "Montana", "NC": "North Carolina",
    "ND": "North Dakota", "NE": "Nebraska", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NV": "Nevada",
    "NY": "New York", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon",
    "PA": "Pennsylvania", "PR": "Puerto Rico", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VA": "Virginia", "VI": "US Virgin Islands",
    "VT": "Vermont", "WA": "Washington", "WI": "Wisconsin",
    "GU": "Guam", "AS": "American Samoa",
    "MP": "Northern Mariana Islands",
    "WV": "West Virginia", "WY": "Wyoming",
}

# Default IANA zone per state. States that straddle a boundary get the zone
# most of their population lives in; the config can name another.
STATE_TZ = {
    "AK": "America/Anchorage", "AL": "America/Chicago",
    "AR": "America/Chicago", "AZ": "America/Phoenix",
    "CA": "America/Los_Angeles", "CO": "America/Denver",
    "CT": "America/New_York", "DC": "America/New_York",
    "DE": "America/New_York", "FL": "America/New_York",
    "GA": "America/New_York", "HI": "Pacific/Honolulu",
    "IA": "America/Chicago", "ID": "America/Boise",
    "IL": "America/Chicago", "IN": "America/Indiana/Indianapolis",
    "KS": "America/Chicago", "KY": "America/New_York",
    "LA": "America/Chicago", "MA": "America/New_York",
    "MD": "America/New_York", "ME": "America/New_York",
    "MI": "America/Detroit", "MN": "America/Chicago",
    "MO": "America/Chicago", "MS": "America/Chicago",
    "MT": "America/Denver", "NC": "America/New_York",
    "ND": "America/Chicago", "NE": "America/Chicago",
    "NH": "America/New_York", "NJ": "America/New_York",
    "NM": "America/Denver", "NV": "America/Los_Angeles",
    "NY": "America/New_York", "OH": "America/New_York",
    "OK": "America/Chicago", "OR": "America/Los_Angeles",
    "PA": "America/New_York", "PR": "America/Puerto_Rico",
    "RI": "America/New_York", "SC": "America/New_York",
    "SD": "America/Chicago", "TN": "America/Chicago",
    "TX": "America/Chicago", "UT": "America/Denver",
    "VA": "America/New_York", "VI": "America/Puerto_Rico",
    "VT": "America/New_York", "WA": "America/Los_Angeles",
    "WI": "America/Chicago", "WV": "America/New_York",
    "GU": "Pacific/Guam", "AS": "Pacific/Pago_Pago",
    "MP": "Pacific/Saipan",
    "WY": "America/Denver",
}

# FIPS codes, for the RepeaterBook query
STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08",
    "CT": "09", "DE": "10", "DC": "11", "FL": "12", "GA": "13", "HI": "15",
    "ID": "16", "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21",
    "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27",
    "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
    "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46",
    "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
    "WV": "54", "WI": "55", "WY": "56", "AS": "60", "GU": "66",
    "MP": "69", "PR": "72", "VI": "78",
}


# ---------------------------------------------------------------------------
# What can be turned on and off. Everything is on unless a station file says
# otherwise, so an operator who wants the whole book writes nothing.
# ---------------------------------------------------------------------------
PARTS = [
    ("cover", "Front and back covers"),
    ("half_title", "Half title page"),
    ("title", "Title page"),
    ("copyright", "Copyright, licence and build date"),
    ("contents", "Contents"),
    ("how_to_use", "How to use this book"),
    ("this_station", "This Station, your own details"),
    ("go_kit", "Go-Kit manifest"),
    ("part_one", "Part One, the whole field reference"),
    ("band_plan", "The band plan drawn for your licence"),
    ("repeaters", "Repeater and net pages"),
    ("radios", "Radio quick reference cards"),
    ("part_two", "Part Two, the deployment log"),
    ("deployment_howto", "How a deployment is recorded"),
    ("deployment_index", "Deployment index"),
    ("part_three", "Part Three, station records"),
    ("colophon", "Colophon and sources"),
]
PART_KEYS = [k for k, _d in PARTS]

# Ready-made selections, for people who would rather not tick boxes.
PRESETS = {
    "full": {},
    "log-only": {k: False for k in
                 ("how_to_use", "this_station", "go_kit", "part_one",
                  "band_plan", "repeaters", "radios", "part_three",
                  "deployment_howto")},
    "field": {"how_to_use": False, "go_kit": False, "part_three": False,
              "reference": ["BANDS", "FREQS", "OPS", "PHON", "AWARDS", "TIME",
                            "CHECK"]},
    "reference-only": {k: False for k in
                       ("part_two", "deployment_howto", "deployment_index",
                        "part_three")},
}


class Sections(object):
    """Which parts of the book this operator asked for."""

    def __init__(self, raw, ref_tags, record_keys):
        raw = dict(raw or {})
        preset = str(raw.pop("preset", "") or "").strip().lower()
        if preset:
            if preset not in PRESETS:
                raise ConfigError("preset must be one of %s, not %r"
                                  % (", ".join(sorted(PRESETS)), preset))
            merged = dict(PRESETS[preset])
            merged.update(raw)
            raw = merged
        self.preset = preset or "full"

        self.flags = {k: True for k in PART_KEYS}
        self.reference = list(ref_tags)
        self.records = list(record_keys)

        for k, v in raw.items():
            if k == "reference":
                self.reference = _pick(v, ref_tags, "reference")
            elif k == "station_records":
                self.records = _pick(v, record_keys, "station_records")
            elif k in self.flags:
                self.flags[k] = bool(v)
            else:
                raise ConfigError(
                    "include: %r is not something that can be switched. "
                    "Try: %s, reference, station_records, preset"
                    % (k, ", ".join(PART_KEYS)))

        # A part switched off takes its children with it.
        if not self.flags["part_one"]:
            for k in ("band_plan", "repeaters", "radios"):
                self.flags[k] = False
            self.reference = []
        if not self.flags["part_two"]:
            for k in ("deployment_howto", "deployment_index"):
                self.flags[k] = False
        if not self.flags["part_three"]:
            self.records = []
        if not self.reference and not self.flags["band_plan"] \
                and not self.flags["repeaters"] and not self.flags["radios"]:
            self.flags["part_one"] = False
        if not self.records:
            self.flags["part_three"] = False

    def on(self, key):
        return self.flags.get(key, True)


def _pick(v, allowed, what):
    """Read a section list: all, none, or a list of names."""
    if v is None or v is False:
        return []
    if v is True:
        return list(allowed)
    if isinstance(v, str):
        t = v.strip().lower()
        if t in ("all", "everything"):
            return list(allowed)
        if t in ("none", "nothing"):
            return []
        v = [v]
    if not isinstance(v, (list, tuple)):
        raise ConfigError("%s should be all, none, or a list of names" % what)
    want, seen = [], set()
    for item in v:
        name = str(item).strip()
        match = None
        for a in allowed:
            if a.lower() == name.lower():
                match = a
                break
        if match is None:
            raise ConfigError("%s: %r is not one of %s"
                              % (what, name, ", ".join(allowed)))
        if match not in seen:
            want.append(match)
            seen.add(match)
    return [a for a in allowed if a in seen]


DEFAULTS = {
    "station": {
        "name": "",
        "callsign": "",
        "byline": "",
        "license_class": "general",
        "grid": "",
        "state": "",
        "arrl_section": "",
        "time_zone": "",
        "club": "",
    },
    "book": {
        "title": "FIELD RECORD",
        "subtitle": "The Portable Operator's Deployment Log",
        "deployments": 26,
        "trim": "personal",
        "color": True,
        "imprint": "",
        "edition": "First Edition",
        "volume": "",
        "series_mark": "",
    },
    "radios": [],
    "data": {
        "repeaters": "",
        "nets": "",
        "attribution": "",
    },
    "include": {},
}


# Trim names the layout engine knows. Kept here so a bad value is caught while
# reading the station file rather than part way through a build.
TRIM_KEYS = {"personal", "6x9", "8.5x11", "field", "L8x55", "L9x6",
             "P55x8", "P6x9"}


class ConfigError(ValueError):
    pass


def _merge(base, over):
    """Overlay a config on the defaults.

    A section whose keys are all commented out parses as None, which must not
    wipe the defaults for that section.
    """
    out = dict(base)
    for k, v in (over or {}).items():
        if v is None and isinstance(out.get(k), (dict, list)):
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


class Station(object):
    """Everything the page builders need to know about one operator."""

    def __init__(self, raw, root="."):
        d = _merge(DEFAULTS, raw or {})
        s, b = d["station"], d["book"]
        self.root = root

        self.name = (s.get("name") or "").strip()
        self.callsign = (s.get("callsign") or "").strip().upper()
        self.club = (s.get("club") or "").strip()

        cls = (s.get("license_class") or "general").strip().lower()
        if cls not in CLASSES:
            raise ConfigError(
                "license_class must be one of %s, not %r"
                % (", ".join(CLASSES), cls))
        self.license_class = cls
        self.class_letter = CLASS_LETTER[cls]
        self.class_name = CLASS_NAME[cls]

        self.grid = (s.get("grid") or "").strip().upper()
        st = (s.get("state") or "").strip().upper()
        if st and st not in STATE_NAMES:
            raise ConfigError("state must be a two letter US code, not %r" % st)
        self.state = st
        self.state_name = STATE_NAMES.get(st, "")

        sec = (s.get("arrl_section") or "").strip().upper()
        self.section_choices = STATE_SECTIONS.get(st, [])
        self.section_ambiguous = False
        if not sec and st:
            # Only fill it in when the state holds exactly one section.
            if len(self.section_choices) == 1:
                sec = self.section_choices[0]
            elif self.section_choices:
                self.section_ambiguous = True
        if sec and sec not in SECTION_NAMES:
            choices = ", ".join(STATE_SECTIONS.get(st, [])) or "see the ARRL list"
            raise ConfigError("arrl_section %r is not an ARRL section. For %s: %s"
                              % (sec, st or "your state", choices))
        self.section = sec
        self.section_name = SECTION_NAMES.get(sec, "")

        tz = (s.get("time_zone") or "").strip()
        if not tz:
            tz = STATE_TZ.get(st, "UTC")
        try:
            self.tz = zone(tz)
        except Exception:
            raise ConfigError("time_zone %r is not an IANA zone name. Try "
                              "America/New_York, America/Chicago, "
                              "America/Denver or America/Los_Angeles." % tz)
        self.tz_name = tz

        # byline: what appears under the title and on the cover. Set it
        # explicitly to control the form; otherwise the callsign sits between
        # the given name and the surname, which is how most operators sign.
        self.byline = (s.get("byline") or "").strip() or self._default_byline()

        self.title = b.get("title") or "FIELD RECORD"
        self.subtitle = b.get("subtitle") or ""
        nd = b.get("deployments", 26)
        if nd is None or nd == "":
            nd = 26
        try:
            self.ndep = int(nd)
        except (TypeError, ValueError):
            raise ConfigError("deployments must be a whole number, not %r" % nd)
        if not 1 <= self.ndep <= 60:
            raise ConfigError("deployments must be between 1 and 60, not %d"
                              % self.ndep)
        self.trim = b.get("trim") or "personal"
        if self.trim not in TRIM_KEYS:
            raise ConfigError("trim must be one of %s, not %r"
                              % (", ".join(sorted(TRIM_KEYS)), self.trim))
        self.color = bool(b.get("color", True))
        self.imprint = (b.get("imprint") or "").strip()
        self.edition = b.get("edition") or "First Edition"
        self.volume = str(b.get("volume") or "").strip()
        self.series_mark = b.get("series_mark") or ""

        radios = d.get("radios") or []
        if isinstance(radios, str):
            radios = [radios]
        if not isinstance(radios, (list, tuple)):
            raise ConfigError("radios should be a list of card names, not a %s"
                              % type(radios).__name__)
        self.radios = [str(r).strip() for r in radios if r]

        dd = d["data"]
        self.repeaters_path = self._path(dd.get("repeaters"))
        self.nets_path = self._path(dd.get("nets"))
        self.attribution = (dd.get("attribution") or "").strip()

        self.built = datetime.date.today()
        # Filled in by make_book, which knows the section and record names.
        self.sections = None
        self._raw_include = d.get("include") or {}

    def choose(self, ref_tags, record_keys):
        """Resolve the include block once the available names are known."""
        self.sections = Sections(self._raw_include, ref_tags, record_keys)
        return self.sections

    # -- helpers ---------------------------------------------------------
    def _default_byline(self):
        parts = self.name.split()
        if self.name and self.callsign and len(parts) >= 2:
            return '%s "%s" %s' % (parts[0], self.callsign, " ".join(parts[1:]))
        if self.name and self.callsign:
            return "%s, %s" % (self.name, self.callsign)
        return self.name or self.callsign or "The Operator"

    def _path(self, p):
        if not p:
            return ""
        p = str(p)
        return p if os.path.isabs(p) else os.path.join(self.root, p)

    @property
    def state_fips(self):
        """Used by fetch_repeaters when the state comes from a station file."""
        return STATE_FIPS.get(self.state, "")

    def place(self):
        """A short line naming where the book is keyed to."""
        if self.section and self.section_name:
            return self.section_name
        return self.state_name or ""

    def utc_rollover(self):
        """The local clock time at which the UTC day rolls over, in summer."""
        u = datetime.datetime(self.built.year, 7, 1, 0, tzinfo=zone("UTC"))
        return u.astimezone(self.tz).strftime("%H%M")


def load(path):
    """Read a station YAML file. Returns a Station."""
    if yaml is None:
        raise ConfigError("PyYAML is not installed. Run: pip install pyyaml")
    if not os.path.exists(path):
        raise ConfigError("no config at %s" % path)
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    if not isinstance(raw, dict):
        raise ConfigError("%s should be a mapping of sections" % path)
    return Station(raw, root=os.path.dirname(os.path.abspath(path)) or ".")
