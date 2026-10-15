# -*- coding: utf-8 -*-
"""Bind a Station to the book's text.

The page builders read module level names out of content_meta. Rather than
thread a config object through forty call sites, this module rebinds those
names once at the start of a build and adds the two notes that only make sense
when the operator's state and time zone are known.

Call apply(station) before building. Call it again for a different station and
the text follows.
"""
import copy

import content_meta as M
import content_ref_b as B

_ORIGINALS = {}


def _save():
    if _ORIGINALS:
        return
    for k in ("TITLE", "SUBTITLE", "SERIES_MARK", "AUTHOR", "AUTHOR_CALL",
              "EDITION", "YEAR", "IMPRINT", "COPYRIGHT", "HALF_TITLE_NOTE",
              "COLOPHON", "ABOUT"):
        _ORIGINALS[k] = copy.deepcopy(getattr(M, k))
    _ORIGINALS["SEC_TIME"] = copy.deepcopy(B.SEC_TIME)
    _ORIGINALS["SEC_SECTIONS"] = copy.deepcopy(_find_sections())


def _find_sections():
    for s in B.SECTIONS_B:
        if s.get("tag") == "SECT" or "Section" in s.get("title", ""):
            return s
    return None


RIGHTS = """{title}: {subtitle}

Compiled and designed by {author}.

Copyright © {year} {author}. All rights reserved.
{edition}.{imprint_line}{owner_line}

Interior design, reference tables, and log architecture are original to this
work. The blank record forms in Part Two and Part Three may be completed and
reproduced for the personal station use of the owner of this copy.

Frequency allocations, award-program requirements, and regulatory notes in
Part One were compiled from the sources listed in the Colophon. Rules change.
The operator, not the book, is responsible for lawful operation. Before you
transmit, check 47 CFR Part 97 and the current rules of any award program you
are chasing.

Nothing in this book is legal advice, engineering certification, or a
substitute for your own RF exposure evaluation.

LICENSE. This work is released under Creative Commons Attribution,
NonCommercial, ShareAlike 4.0 International (CC BY-NC-SA 4.0). You may copy it,
print it, and adapt it for your own station, provided you credit the author, do
not sell it or use it commercially, and release any adaptation under the same
terms. Full terms: creativecommons.org/licenses/by-nc-sa/4.0

TRADEMARKS. Icom, Yaesu, Kenwood and Elecraft are trademarks of their
respective companies. ARRL is a trademark of the American Radio Relay League.
Parks on the Air and Summits on the Air are trademarks of their respective
programs. This book is an independent work, is not published or endorsed by any
of them, and names them only to say what it is about.

FACTS AND SOURCES. Frequency allocations, repeater listings, tone codes and
program rules are facts and belong to nobody. The selection, arrangement,
drawings and wording here are original to this work. Sources are named on the
page that uses them and in the Colophon.{data_line}

BUILD. This copy was generated on {built}. Regulatory figures were current when
the sources in the Colophon were compiled. A copy printed long after that date
should be checked against the rules before it is trusted.

Set in IBM Plex, under the SIL Open Font License.
"""


def _brace(s):
    """Protect user text from the second format() pass on the rights block."""
    return str(s).replace("{", "{{").replace("}", "}}")


def apply(st):
    """Rebind the book's text to this station. Returns the station."""
    _save()

    M.TITLE = st.title or _ORIGINALS["TITLE"]
    M.SUBTITLE = st.subtitle or _ORIGINALS["SUBTITLE"]
    M.SERIES_MARK = st.series_mark or ""
    # The author of FIELD RECORD does not change when a copy is personalized.
    # Rebinding AUTHOR to the operator put their name on the copyright page as
    # the designer and holder of copyright, erased the real author, and left a
    # CC BY licence demanding an attribution the book no longer carried.
    # OWNER is whose copy this is; AUTHOR is who wrote it.
    M.OWNER = st.byline
    M.OWNER_CALL = st.callsign
    M.EDITION = st.edition
    M.YEAR = str(st.built.year)
    M.IMPRINT = st.imprint

    imprint_line = (" Published %s by %s." % (M.YEAR, st.imprint)
                    if st.imprint else " Published %s." % M.YEAR)
    data_line = ("\n\n" + st.attribution) if st.attribution else ""
    # The copyright page runs format() over this string once more, for author,
    # year and edition. Anything the operator typed has to survive that pass,
    # so braces in a name, a club or an attribution are doubled here.
    M.COPYRIGHT = RIGHTS.format(
        title=_brace(M.TITLE), subtitle=_brace(M.SUBTITLE), author="{author}",
        year="{year}", edition="{edition}", imprint_line=_brace(imprint_line),
        data_line=_brace(data_line), built=st.built.strftime("%d %B %Y"),
        owner_line=_brace("\n\nThis copy prepared for %s." % st.byline
                          if st.byline else ""))

    M.HALF_TITLE_NOTE = _ORIGINALS["HALF_TITLE_NOTE"]

    # COLOPHON holds a copy of the series mark taken when the module was
    # imported. Rebuild it, and drop the block entirely when there is no mark.
    colophon = []
    for block in _ORIGINALS["COLOPHON"]:
        if block[0] == "mark":
            if M.SERIES_MARK:
                colophon.append(("mark", M.SERIES_MARK))
        else:
            colophon.append(block)
    M.COLOPHON = colophon

    _time_note(st)
    _section_note(st)
    return st


def _time_note(st):
    """Name the operator's own zone in the Zulu day section."""
    sec = copy.deepcopy(_ORIGINALS["SEC_TIME"])
    if st.tz_name:
        roll = st.utc_rollover()
        where = st.state_name or "your location"
        sec["blocks"] = list(sec["blocks"]) + [(
            "note",
            "This copy is keyed to %s. In summer the UTC day rolls over at "
            "%s local time in %s, which is the middle of an evening "
            "activation. Write the new UTC date on the sheet at that moment "
            "or the contacts either side of it will be filed against the "
            "wrong day."
            % (st.tz_name, roll, where))]
    # SECTIONS_B holds these same dicts, so mutating in place is enough.
    B.SEC_TIME.clear()
    B.SEC_TIME.update(sec)


def _section_note(st):
    """Name the operator's own ARRL section in the sections list."""
    src = _ORIGINALS.get("SEC_SECTIONS")
    if not src:
        return
    live = _find_sections()
    if live is None:
        return
    sec = copy.deepcopy(src)
    if st.section and st.section_name:
        sec["blocks"] = list(sec["blocks"]) + [(
            "note",
            "Your section is %s, %s. Contest and traffic exchanges ask for "
            "the section abbreviation, not the state." % (st.section,
                                                          st.section_name))]
    elif st.section_ambiguous:
        sec["blocks"] = list(sec["blocks"]) + [(
            "note",
            "%s holds more than one ARRL section: %s. Find yours in the list "
            "above and write it on the Site Record. Set arrl_section in your "
            "station file and it will be filled in for you."
            % (st.state_name, ", ".join(st.section_choices)))]
    live.clear()
    live.update(sec)

