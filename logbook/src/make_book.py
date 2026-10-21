#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build one operator's FIELD RECORD from a station file.

    python3 make_book.py station.yml

The contents cannot be sized until the entries are counted, and the entries
cannot be given page numbers until the contents has been sized. So the book is
laid out more than once, and the passes have to land on the same page count or
the build stops. A contents pointing at the wrong page sends people to the
wrong page, which is worse than no contents at all.
"""
import argparse
import io
import os
import sys

from reportlab.lib.units import inch

from engine import (Book, TRIMS, make_styles, set_ink, set_color,
                    INK, SLATE, AMBER, COND_B, tracked)
import pages as P
import forms as F
import personal as PZ
import build as BLD
import cover as CV
import config as CFG
import personalize
import radiocard
import rfdata
import content_meta as M
import content_ref_a as A
import content_ref_b as B

BAND_ORDER = ["2", "70cm", "6", "1.25", "10", "33cm", "23cm"]


def load_everything(station, root="."):
    """Read the operator's data files and hand them to the page builders."""
    reps = {}
    if station.repeaters_path:
        reps = rfdata.load_repeaters(station.repeaters_path)
    nets = rfdata.load_nets(station.nets_path) if station.nets_path else []
    attrib = station.attribution
    if not attrib and station.repeaters_path:
        attrib = _attribution_from(station.repeaters_path)
    PZ.set_operator(station.class_letter, station.class_name, station.place())
    PZ.set_rf_data(reps, nets, attrib)
    cards = [radiocard.load(name, root) for name in station.radios]
    return reps, nets, cards


def _attribution_from(path):
    """Comment lines at the head of a CSV are treated as its source note."""
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            notes = []
            for line in fh:
                if not line.startswith("#"):
                    break
                t = line.lstrip("#").strip()
                if t:
                    notes.append(t if t.endswith(".") else t + ".")
        return " ".join(notes)
    except OSError:
        return ""


def build(station, outpath, toc_in=None, pages_in=0, root=".",
          toc_pages=BLD.TOC_PAGES):
    st = station
    sec = st.sections or st.choose([x['tag'] for x in A.SECTIONS_A + B.SECTIONS_B],
                                   BLD.RECORD_ORDER)
    set_color(st.color)
    set_ink(False)
    t = TRIMS[st.trim]
    bk = Book(t, outpath, M.TITLE, M.SUBTITLE)
    bk.styles = make_styles(t)
    # A filled book carries its values on the station; a blank one carries
    # nothing and every page below draws exactly as it always has.
    bk.filled = getattr(st, "filled", None) or {}
    # The operator's own byline, derived from their name and callsign, for the
    # cover and title page. The author's credit is separate and unchanged.
    bk.byline = getattr(st, "byline", None)
    toc = []
    x, y, w, h = bk.body()
    ndep = st.ndep
    reps, nets, cards = load_everything(st, root)
    if not sec.on("radios"):
        cards = []

    # ---- cover
    if sec.on("cover"):
        bk.begin()
        CV.personal_front(bk.c, t.W, t.H, ndep, byline=bk.byline)
        bk.end_page(kind="blind", folio=False)
        bk.blank(kind="blind")

    # ---- front matter
    if sec.on("half_title"):
        BLD.half_title(bk)
        bk.blank(kind="front")
    if sec.on("title"):
        BLD.title_page(bk, ndep)
    if sec.on("copyright"):
        BLD.copyright_page(bk)
    if sec.on("contents"):
        BLD.contents_pages(bk, toc_in, toc_pages)

    if sec.on("how_to_use"):
        bk.to_recto()
        toc.append(("part", "How to Use This Book", bk.page))
        c = bk.c
        x, y, w, h = bk.body()
        top = y + h
        tracked(c, x, top - 0.22 * inch, "HOW TO USE THIS BOOK", COND_B,
                t.base + 5.0, 2.4, SLATE if st.color else INK)
        bk.rule(x, top - 0.22 * inch - 10, w, 2.0, AMBER if st.color else INK)
        story = P.render_blocks(M.HOW_TO_USE, bk.styles, w, t.base)
        P.flow(bk, story, part=None, sec=None,
               first_page_drop=0.22 * inch + 24, folio=False)

    if sec.on("this_station") or sec.on("go_kit"):
        bk.to_recto()
    if sec.on("this_station"):
        toc.append(("sec", "This Station", bk.page))
        BLD.station_identity(bk)
    if sec.on("go_kit"):
        toc.append(("sec", "Go-Kit Manifest", bk.page))
        BLD.inventory_page(bk)

    # ---- Part One
    ref_sections = [x for x in A.SECTIONS_A + B.SECTIONS_B
                    if x['tag'] in sec.reference]
    if sec.on("part_one"):
        contents_list = []
        if sec.on("band_plan"):
            contents_list.append("The band plan for your license")
        contents_list += [x['title'] for x in ref_sections]
        if sec.on("repeaters"):
            contents_list.append("%s repeaters and nets" % (st.place() or "Local"))
        if sec.on("radios"):
            for card in cards:
                contents_list.append("%s quick reference" % card.get("name"))

        bk.to_recto()
        toc.append(("part", "Part One: Field Reference", bk.page))
        BLD.part_title(bk, "Part One", "FIELD | REFERENCE",
                       "The material a portable operator reaches for with cold "
                       "hands. Read it once at the kitchen table. After that, "
                       "use the markers in the outer margin.",
                       contents_list)

        if sec.on("band_plan"):
            toc.append(("sec", "The Band Plan, %s" %
                        ("%s Privileges" % st.class_name if st.class_letter
                         else "in Color"), bk.page))
            PZ.band_chart(bk)
            bk.end_page(kind="ref", part="Part One  Field Reference",
                        label="Band plan")

        nsec = len(ref_sections)
        for i, s_ in enumerate(ref_sections):
            toc.append(("sec", s_['title'], bk.page))
            secref = (s_['tag'], s_['title'], i, nsec)
            drop = BLD.section_opener(bk, s_, i, nsec)
            story = P.render_blocks(s_['blocks'], bk.styles, w, t.base)
            P.flow(bk, story, part="Part One  Field Reference", sec=secref,
                   first_page_drop=drop, folio=True)

        if sec.on("repeaters"):
            start = bk.page
            for _band, title in PZ.repeater_pages(bk, BAND_ORDER):
                toc.append(("sec", title, start))
                start += 1

        if sec.on("radios"):
            for card in cards:
                toc.append(("sec", "%s Quick Reference" % card.get("name"),
                            bk.page))
                radiocard.render(bk, card)

    # ---- Part Two
    if sec.on("part_two"):
        bk.to_recto()
        toc.append(("part", "Part Two: The Deployment Log", bk.page))
        items = []
        if sec.on("deployment_index"):
            items.append("Deployment index")
        if sec.on("deployment_howto"):
            items.append("How a deployment works")
        items.append("Deployments 01 through %02d" % ndep)
        # An export of one activation is not a book and wants no divider. This
        # is an attribute rather than a config key so the website's own part
        # checkboxes are untouched.
        if not getattr(st, "bare", False):
            BLD.part_title(bk, "Part Two", "THE | DEPLOYMENT | LOG",
                           "%d deployments, four pages each. Site Record, two "
                           "sheets of contacts, and a debrief completed at the "
                           "site." % ndep, items)
        if sec.on("deployment_howto"):
            BLD.deployment_howto(bk)
        if sec.on("deployment_index"):
            bk.to_recto()
            toc.append(("sec", "Deployment Index", bk.page))
            BLD.deployment_index(bk, ndep)

        bk.to_verso()
        toc.append(("sec", "Deployments 01 to %02d" % ndep, bk.page))
        for n in range(1, ndep + 1):
            pn = "Part Two  Deployment Log"
            lbl = "Deployment %02d" % n
            bk.fill_for(n, "site")
            F.site_record(bk, n)
            bk.end_page(kind="log", part=pn, label=lbl)
            bk.fill_for(n, "qsoA")
            F.qso_log(bk, n, 1, "A")
            bk.end_page(kind="log", part=pn, label=lbl)
            bk.fill_for(n, "qsoB")
            F.qso_log(bk, n, 2, "B")
            bk.end_page(kind="log", part=pn, label=lbl)
            bk.fill_for(n, "debrief")
            F.debrief(bk, n)
            bk.end_page(kind="log", part=pn, label=lbl)

    # ---- Part Three
    if sec.on("part_three"):
        bk.to_recto()
        toc.append(("part", "Part Three: Station Records", bk.page))
        BLD.part_title(bk, "Part Three", "STATION | RECORDS",
                       "The part that outlives this volume. Photograph these "
                       "pages before the book goes on the shelf.",
                       [BLD.RECORD_TITLES[k] for k in sec.records])
        BLD.part_three_pages(bk, toc, sec.records)

    if sec.on("colophon"):
        bk.to_recto()
        toc.append(("part", "Colophon", bk.page))
        BLD.colophon(bk)

    # ---- back cover on the reverse of the last sheet
    if sec.on("cover"):
        while bk.page % 2 == 1:
            bk.blank(kind="blind")
        bk.begin()
        names = [" ".join(x for x in (cd.get("maker"), cd.get("name")) if x)
                 for cd in cards]
        CV.personal_back(bk.c, t.W, t.H, ndep, pages_in or bk.page,
                         byline=bk.byline,
                         copy=CV.personal_back_copy(
                             ndep, sec=sec, place=st.place(), radios=names,
                             ref_tags=getattr(sec, "reference", ())))
        bk.end_page(kind="blind", folio=False)

    n = bk.finish(pad_to_multiple=2)
    return n, toc


class PageCountMoved(ValueError):
    """The layout did not settle. Raised rather than shipping a wrong contents."""


def render(st, root=".", note=None):
    """Lay a station's book out and return (page count, PDF bytes).

    Pass one counts the contents entries. If the standing allowance was
    already the right size, that pass's page numbers still stand and the next
    pass draws them: two passes, not three. A book with no contents and no
    covers depends on no page numbers at all, so one pass finishes it.
    """
    say = note or (lambda _msg: None)
    sec = st.sections
    if sec is None:
        sec = st.choose([x['tag'] for x in A.SECTIONS_A + B.SECTIONS_B],
                        BLD.RECORD_ORDER)

    say("laying out the pages")
    buf = io.BytesIO()
    npages = BLD.TOC_PAGES
    n, toc = build(st, buf, root=root, toc_pages=npages)

    if sec.on("contents"):
        needed = BLD.toc_pages_needed(TRIMS[st.trim], toc)
        if needed != npages:
            say("sizing the contents")
            npages, buf = needed, io.BytesIO()
            n, toc = build(st, buf, root=root, toc_pages=npages)

    # The only things that read the collected numbers are the contents and the
    # back cover. Without either, the pass just made is the finished book.
    if not sec.on("contents") and not sec.on("cover"):
        return n, buf.getvalue()

    say("setting the page numbers")
    out = io.BytesIO()
    n2, _ = build(st, out, toc_in=toc, pages_in=n, root=root,
                  toc_pages=npages)
    if n2 != n:
        raise PageCountMoved("page count moved between passes: %d then %d"
                             % (n, n2))
    return n2, out.getvalue()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Build a FIELD RECORD logbook from a station file.")
    ap.add_argument("config", nargs="?", default="station.yml")
    ap.add_argument("--out", default="out",
                    help="directory for the finished PDF")
    ap.add_argument("--name", default="",
                    help="output file name, without the extension")
    ap.add_argument("--preset", default="",
                    help="full, log-only, field or reference-only. "
                         "Overrides the station file.")
    ap.add_argument("--only", default="",
                    help="comma separated list of parts to keep, and nothing "
                         "else. For example: cover,part_two")
    ap.add_argument("--without", default="",
                    help="comma separated list of parts to drop. For example: "
                         "part_one,part_three")
    ap.add_argument("--reference", default="",
                    help="comma separated reference sections, or all, or none")
    ap.add_argument("--records", default="",
                    help="comma separated station records, or all, or none")
    ap.add_argument("--deployments", type=int, default=0,
                    help="override the number of deployments")
    ap.add_argument("--list-sections", action="store_true",
                    help="print everything that can be switched, then stop")
    a = ap.parse_args(argv)

    if a.list_sections:
        return list_sections()

    try:
        st = CFG.load(a.config)
    except CFG.ConfigError as e:
        print("station file: %s" % e, file=sys.stderr)
        return 2

    root = os.path.dirname(os.path.abspath(a.config)) or "."
    if a.deployments:
        st.ndep = a.deployments

    ref_tags = [x['tag'] for x in A.SECTIONS_A + B.SECTIONS_B]
    try:
        st.choose(ref_tags, BLD.RECORD_ORDER)
        apply_overrides(st, a, ref_tags)
    except CFG.ConfigError as e:
        print("sections: %s" % e, file=sys.stderr)
        return 2
    personalize.apply(st)

    os.makedirs(a.out, exist_ok=True)
    stem = a.name or ("FieldRecord_%s" % (st.callsign or "book"))
    final = os.path.join(a.out, "%s.pdf" % stem)

    try:
        n2, data = render(st, root=root)
    except PageCountMoved as e:
        print("%s" % e, file=sys.stderr)
        return 1
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as e:
        print("build failed: %s" % e, file=sys.stderr)
        return 2
    with open(final, "wb") as fh:
        fh.write(data)

    print("%s" % final)
    print("  %s, %s" % (st.byline, st.class_name))
    if st.place():
        print("  keyed to %s, %s" % (st.place(), st.tz_name))
    if st.section_ambiguous:
        print("  note: %s holds several ARRL sections (%s). Set arrl_section "
              "to name yours." % (st.state_name, ", ".join(st.section_choices)))
    print("  %d deployments, %d pages, %d sheets duplex"
          % (st.ndep, n2, (n2 + 1) // 2))
    off = [k for k in CFG.PART_KEYS if not st.sections.on(k)]
    if off:
        print("  left out: %s" % ", ".join(off))
    if len(st.sections.reference) < len(ref_tags):
        print("  reference sections: %d of %d"
              % (len(st.sections.reference), len(ref_tags)))
    if len(st.sections.records) < len(BLD.RECORD_ORDER):
        print("  station records: %d of %d"
              % (len(st.sections.records), len(BLD.RECORD_ORDER)))
    return 0


def apply_overrides(st, a, ref_tags):
    """Command line flags win over the station file."""
    sec = st.sections
    if a.preset:
        name = a.preset.strip().lower()
        if name not in CFG.PRESETS:
            raise CFG.ConfigError("preset must be one of %s, not %r"
                                  % (", ".join(sorted(CFG.PRESETS)), a.preset))
        sec = st.sections = CFG.Sections(dict(CFG.PRESETS[name]), ref_tags,
                                         BLD.RECORD_ORDER)
    if a.only:
        keep = {k.strip() for k in a.only.split(",") if k.strip()}
        bad = keep - set(CFG.PART_KEYS)
        if bad:
            raise CFG.ConfigError("--only: %s is not a part. Run "
                                  "--list-sections." % ", ".join(sorted(bad)))
        for k in CFG.PART_KEYS:
            sec.flags[k] = k in keep
    for k in (x.strip() for x in a.without.split(",")):
        if not k:
            continue
        if k not in CFG.PART_KEYS:
            raise CFG.ConfigError("--without: %r is not a part. Run "
                                  "--list-sections." % k)
        sec.flags[k] = False
    if a.reference:
        sec.reference = CFG._pick([x.strip() for x in a.reference.split(",")]
                                  if a.reference.strip().lower() not in
                                  ("all", "none") else a.reference,
                                  ref_tags, "reference")
    if a.records:
        sec.records = CFG._pick([x.strip() for x in a.records.split(",")]
                                if a.records.strip().lower() not in
                                ("all", "none") else a.records,
                                BLD.RECORD_ORDER, "station_records")
    # re-apply the parent rules after any override
    if not sec.on("part_one"):
        for k in ("band_plan", "repeaters", "radios"):
            sec.flags[k] = False
        sec.reference = []
    if not sec.on("part_two"):
        for k in ("deployment_howto", "deployment_index"):
            sec.flags[k] = False
    if not sec.on("part_three"):
        sec.records = []
    if not sec.reference and not sec.on("band_plan") and \
            not sec.on("repeaters") and not sec.on("radios"):
        sec.flags["part_one"] = False
    if not sec.records:
        sec.flags["part_three"] = False


def list_sections():
    """Print everything a station file can switch on or off."""
    print("Parts. Set any of these to false under include: in your station "
          "file,\nor pass --without name1,name2 on the command line.\n")
    for k, d in CFG.PARTS:
        print("  %-18s %s" % (k, d))
    print("\nReference sections. Under include: write "
          "reference: [BANDS, TIME]\nor reference: none, "
          "or pass --reference BANDS,TIME.\n")
    for x in A.SECTIONS_A + B.SECTIONS_B:
        print("  %-8s %s" % (x['tag'], x['title']))
    print("\nStation records. Under include: write "
          "station_records: [equipment, notes]\nor pass --records "
          "equipment,notes.\n")
    for k in BLD.RECORD_ORDER:
        print("  %-14s %s" % (k, BLD.RECORD_TITLES[k]))
    print("\nPresets. Under include: write preset: field, "
          "or pass --preset field.\n")
    print("  full             everything, the default")
    print("  log-only         covers, title, contents and the deployments")
    print("  field            the reference an operator uses on site, no "
          "station records")
    print("  reference-only   Part One and nothing to write in")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
