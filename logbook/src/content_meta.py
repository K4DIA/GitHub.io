# -*- coding: utf-8 -*-
"""FIELD RECORD - book metadata and front matter."""

TITLE = "FIELD RECORD"
SUBTITLE = "The Portable Operator's Deployment Log"
SERIES_MARK = "SIGNVM  EX  CAMPO"
AUTHOR = 'Tony "K4DIA" Pelfanio'
AUTHOR_CALL = "K4DIA"
EDITION = "First Edition"
YEAR = "2026"
IMPRINT = "Ground Plane Press"

COPYRIGHT = """FIELD RECORD: The Portable Operator's Deployment Log

Compiled and designed by {author}.

Copyright © {year} {author}. All rights reserved.
{edition}. Published {year} by {imprint}.

Interior design, reference tables, and log architecture are original
to this work. The blank record forms in Part Two and Part Three may be
completed and reproduced for the personal station use of the owner of
this copy.

Frequency allocations, award-program requirements, and regulatory
notes in Part One were compiled and verified in {year} from the
sources listed in the Colophon. Rules change. The operator, not the
book, is responsible for lawful operation. Before you transmit,
check 47 CFR Part 97 and the current rules of any award program you
are chasing.

Nothing in this book is legal advice, engineering certification, or a
substitute for your own RF exposure evaluation.

LICENSE. This work is released under Creative Commons Attribution,
NonCommercial, ShareAlike 4.0 International (CC BY-NC-SA 4.0). You may
copy it, print it, and adapt it for your own station, provided you
credit the author, do not sell it or use it commercially, and release
any adaptation under the same terms. The author retains all commercial
rights. Full terms: creativecommons.org/licenses/by-nc-sa/4.0

TRADEMARKS. ICOM and IC-706 are trademarks of Icom Inc. ARRL is a
trademark of the American Radio Relay League. Parks on the Air and
Summits on the Air are trademarks of their respective programs. This
book is an independent work, is not published or endorsed by any of
them, and names them only to say what it is about.

FACTS AND SOURCES. Frequency allocations, repeater listings, tone
codes and program rules are facts and belong to nobody. The
selection, arrangement, drawings and wording here are original to this
work. Sources are named on the page that uses them and in the
Colophon.

Set in IBM Plex, under the SIL Open Font License.
"""

HALF_TITLE_NOTE = "A logbook built around the outing, not the contact."

HOW_TO_USE = [
    ("lead",
     "A conventional logbook records the contact and assumes the station. For "
     "a fixed station that assumption holds. For a portable one it does not: "
     "the antenna, the support, the power source, the noise floor and the "
     "weather change with every outing, and they are the variables that "
     "determine what the log shows."),

    ("p",
     "A contact with Colorado on 20 meters at 40 watts is not a complete "
     "record. The same contact made from a wire at 22 feet, on a battery two "
     "hours into its discharge, at a site 60 feet from a power line, with the "
     "K index at 4, is. Without the second set of facts the first cannot be "
     "interpreted later, and interpretation is the reason to keep a log at "
     "all."),

    ("h3", "The unit of record is the deployment"),

    ("p",
     "Part Two is organized into deployments. Each occupies four pages, laid "
     "out as two facing spreads, and is completed over the course of a single "
     "outing:"),

    ("bul", [
        "<b>Site Record</b>, left page of the first spread. Location, "
        "conditions, station, antenna and power. Complete it before the first "
        "call, while the details are in front of you.",
        "<b>QSO Log A</b>, right page of the first spread. Contacts, in "
        "columns chosen for portable operating.",
        "<b>QSO Log B</b>, left page of the second spread. Continuation. If "
        "both sheets fill, continue on the overflow pages in Part Three and note "
        "the deployment number.",
        "<b>Debrief</b>, right page of the second spread. Totals by band and "
        "mode, power consumed, faults, and the change to make before the next "
        "outing. Complete it at the site.",
    ]),

    ("h3", "Scope of the written record"),

    ("p",
     "Record what cannot be reconstructed afterwards: coordinates, feedpoint "
     "height, wire configuration, measured SWR, noise floor, and the point at "
     "which the supply voltage fell. Where an electronic log is in use it "
     "holds the contact list; these pages hold the context around it and serve "
     "as the running record during operation."),

    ("h3", "Times are UTC"),

    ("p",
     "Every date and time field in this book is Coordinated Universal Time. "
     "Award programs, contest logs and net schedules are all keyed to it, and "
     "the UTC day boundary falls during the evening in North America. A "
     "conversion table is given in Part One."),

    ("h3", "Part One, reference"),

    ("p",
     "Band edges, calling frequencies, wire lengths, feedline loss, power "
     "budgets, exposure limits and activation requirements. Read once, then "
     "consulted. Each section carries a marker at a distinct height in the "
     "outer margin, so the sections can be located from the fore edge."),

    ("h3", "Part Three, station records"),

    ("p",
     "Equipment register, modification and repair log, antenna build sheets "
     "with SWR sweep grids, battery cycle records and award trackers. These "
     "carry forward from one volume to the next."),

    ("note",
     "Number every deployment, including unsuccessful ones. An outing that "
     "produced three contacts because a feedpoint connector failed carries "
     "more diagnostic value than one that produced a hundred without "
     "incident, and only the debrief preserves it."),
]

COLOPHON = [
    ("h3", "Colophon"),
    ("p",
     "The interior is set in IBM Plex: Plex Serif for reading matter, Plex "
     "Sans and Plex Sans Condensed for labels and rules, Plex Mono for tabular "
     "matter. Log grids are ruled at 0.4 point, a weight that carries pencil, "
     "ballpoint and fine-line ink without competing with the entry. Row heights "
     "are set for handwriting done in the field rather than at a desk."),
    ("p",
     "Section markers are printed rather than die cut, so the book can be "
     "produced by any printer without specialist finishing."),
    ("h3", "Sources for Part One"),
    ("bul", [
        "47 CFR Part 97, Amateur Radio Service, US Federal Communications Commission.",
        "ARRL frequency allocations and band plan charts, and ARRL/RAC contest section list.",
        "FCC Report and Order on 60 meters, new 5351.5 to 5366.5 kHz subband effective 13 February 2026.",
        "FCC Report and Order eliminating HF symbol rate limits in favor of a 2.8 kHz bandwidth limit, effective 2024.",
        "Parks on the Air program rules and activator documentation.",
        "Summits on the Air general rules.",
        "FCC Office of Engineering and Technology Bulletin 65 on RF exposure, and the amateur exposure evaluation requirement in effect since 3 May 2023.",
    ]),
    ("p",
     "Coax loss, velocity factor, and conductor ampacity figures are nominal "
     "values for typical cable and wire of each type at room temperature. Use "
     "them for planning. Measure for anything that matters."),
    ("mark", SERIES_MARK),
]

# Inside back cover. Kept to what the book is and who made it; anything about
# the compiler beyond name and callsign is the compiler's to approve.
ABOUT = [
    "This book was compiled because the record a portable operator most needs "
    "is the one a conventional logbook does not ask for. Callsigns survive in "
    "an electronic log. Antenna configuration, feedpoint height, site noise "
    "and the conditions that made a site work do not.",
    "Its unit of record is therefore the deployment rather than the contact, "
    "and each outing closes with a debrief written at the site.",
]
