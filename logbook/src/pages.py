# -*- coding: utf-8 -*-
"""FIELD RECORD - page builders."""
from reportlab.lib.units import inch
from reportlab.lib.colors import white
from reportlab.platypus import (Frame, Paragraph, Spacer, Table, TableStyle,
                                Flowable)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from engine import (head_fill, zebra_fill, box_fill, CLR, AMBER,
                    INK, G25, G35, G50, G70, W_HAIR, W_RULE, W_MED,
                    SERIF, COND_B, MONO, MONO_SB, wrap_lines)
import content_ref_b as B


# =====================================================================
#  flowables
# =====================================================================
class NoteBox(Flowable):
    """A caution note with a heavy left bar."""

    def __init__(self, para, width):
        Flowable.__init__(self)
        self.para = para
        self.width = width

    def wrap(self, aw, ah):
        w, h = self.para.wrap(self.width - 12, ah)
        self.height = h + 13
        return self.width, self.height

    def draw(self):
        c = self.canv
        h = self.height
        bf = box_fill()
        if bf is not None:
            c.setFillColor(bf)
            c.rect(0, 0, self.width, h, stroke=0, fill=1)
        else:
            c.setStrokeColor(G35)
            c.setLineWidth(W_RULE)
            c.rect(0, 0, self.width, h, stroke=1, fill=0)
        c.setFillColor(AMBER if CLR.on else INK)
        c.rect(0, 0, 2.6, h, stroke=0, fill=1)
        c.saveState()
        c.translate(11, 5.5)
        self.para.drawOn(c, 0, 0)
        c.restoreState()


class CheckRow(Flowable):
    def __init__(self, text, width, size=8.0):
        Flowable.__init__(self)
        self.text, self.width, self.size = text, width, size

    def wrap(self, aw, ah):
        self.lines = wrap_lines(self.text, SERIF, self.size, self.width - 16)
        self.height = len(self.lines) * self.size * 1.24 + 2.5
        return self.width, self.height

    def draw(self):
        c = self.canv
        top = self.height - self.size * 0.98
        c.setStrokeColor(G50)
        c.setLineWidth(W_RULE)
        c.rect(0.5, top - 0.4, 6.6, 6.6, stroke=1, fill=0)
        c.setFillColor(INK)
        c.setFont(SERIF, self.size)
        y = top
        for ln in self.lines:
            c.drawString(14, y, ln)
            y -= self.size * 1.24


class Rule(Flowable):
    def __init__(self, width, weight=W_MED, color=G70, space=3):
        Flowable.__init__(self)
        self.width, self.weight, self.color, self.space = width, weight, color, space

    def wrap(self, aw, ah):
        return self.width, self.weight + self.space * 2

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.weight)
        self.canv.line(0, self.space, self.width, self.space)


def _tbl_style(ncols, nrows, size, mono, align, header=True):
    st = [
        # Named explicitly so the table does not emit a Helvetica selector.
        ('FONT', (0, 0), (-1, -1), MONO if mono else SERIF, size),
        ('GRID', (0, 0), (-1, -1), W_HAIR, G35),
        ('BOX', (0, 0), (-1, -1), W_MED, G70),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2.6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.8),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.4),
    ]
    if header:
        st += [
            ('LINEBELOW', (0, 0), (-1, 0), 1.1, AMBER if CLR.on else G70),
            ('TOPPADDING', (0, 0), (-1, 0), 3.4),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 3.6),
        ]
        hf = head_fill()
        if hf is not None:
            st.append(('BACKGROUND', (0, 0), (-1, 0), hf))
        zf = zebra_fill()
        if zf is not None:
            for r in range(1, nrows):
                if r % 2 == 0:
                    st.append(('BACKGROUND', (0, r), (-1, r), zf))
    return st


def build_table(spec, avail_w, styles, base):
    head = spec.get('head')
    rows = spec['rows']
    size = spec.get('size', base - 1.4)
    mono = spec.get('mono', [])
    align = spec.get('align', ['l'] * len(rows[0]))
    # Column widths are fractions of the measure. A spec that sums to more
    # than one would run the table past the margin, and on a verso that means
    # into the punched edge, so it is scaled back rather than trusted.
    frac = list(spec['w'])
    total = sum(frac)
    if total > 1.0:
        frac = [x / total for x in frac]
    w = [x * avail_w for x in frac]

    cell = ParagraphStyle('cell', fontName=SERIF, fontSize=size,
                          leading=size * 1.22, alignment=TA_LEFT)
    cellm = ParagraphStyle('cellm', parent=cell, fontName=MONO, fontSize=size - 0.5,
                           leading=size * 1.22)
    cellc = ParagraphStyle('cellc', parent=cell, alignment=TA_CENTER)
    cellmc = ParagraphStyle('cellmc', parent=cellm, alignment=TA_CENTER)
    cellr = ParagraphStyle('cellr', parent=cell, alignment=2)
    cellmr = ParagraphStyle('cellmr', parent=cellm, alignment=2)
    headst = ParagraphStyle('hd', fontName=COND_B, fontSize=size - 0.3,
                            leading=size * 1.16, alignment=TA_LEFT)
    headc = ParagraphStyle('hdc', parent=headst, alignment=TA_CENTER)

    data = []
    if head:
        data.append([Paragraph(h.upper(), headc if align[i] in 'cr' else headst)
                     for i, h in enumerate(head)])
    for r in rows:
        out = []
        for i, v in enumerate(r):
            v = "" if v is None else str(v)
            v = v.replace("\n", "<br/>")
            m = i in mono
            a = align[i] if i < len(align) else 'l'
            if a == 'c':
                s = cellmc if m else cellc
            elif a == 'r':
                s = cellmr if m else cellr
            else:
                s = cellm if m else cell
            out.append(Paragraph(v, s))
        data.append(out)
    t = Table(data, colWidths=w, repeatRows=1 if head else 0, hAlign='LEFT')
    t.setStyle(TableStyle(_tbl_style(len(w), len(data), size, mono, align,
                                     header=bool(head))))
    return t


def build_fill_grid(spec, avail_w, base):
    labels = spec['labels']
    nrows = spec['rows']
    cw = avail_w / float(len(labels))
    headst = ParagraphStyle('fh', fontName=COND_B, fontSize=base - 2.0,
                            leading=(base - 2.0) * 1.15)
    data = [[Paragraph(l.upper(), headst) for l in labels]]
    for _ in range(nrows):
        data.append([""] * len(labels))
    t = Table(data, colWidths=[cw] * len(labels),
              rowHeights=[None] + [0.245 * inch] * nrows, hAlign='LEFT')
    _hf = head_fill()
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), SERIF, base - 1.4),
        ('GRID', (0, 0), (-1, -1), W_HAIR, G35),
        ('BOX', (0, 0), (-1, -1), W_MED, G70),
        ('BACKGROUND', (0, 0), (-1, 0), _hf if _hf is not None else white),
        ('LINEBELOW', (0, 0), (-1, 0), W_MED, G70),
        ('TOPPADDING', (0, 0), (-1, -1), 3.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.0),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.4),
    ]))
    return t


def build_sections_table(avail_w, base):
    """ARRL / RAC section list, laid out in three balanced columns."""
    flat = []
    for grp, items in B.ARRL_SECTIONS:
        flat.append(("GRP", grp, ""))
        for ab, nm in items:
            flat.append(("ROW", ab, nm))
    ncol = 3
    per = (len(flat) + ncol - 1) // ncol
    cols = [flat[i * per:(i + 1) * per] for i in range(ncol)]
    while len(cols) < ncol:
        cols.append([])
    maxlen = max(len(c) for c in cols)
    for c in cols:
        c.extend([("PAD", "", "")] * (maxlen - len(c)))

    ab_s = ParagraphStyle('ab', fontName=MONO_SB, fontSize=base - 2.4,
                          leading=(base - 2.4) * 1.28)
    nm_s = ParagraphStyle('nm', fontName=SERIF, fontSize=base - 2.4,
                          leading=(base - 2.4) * 1.28)
    gp_s = ParagraphStyle('gp', fontName=COND_B, fontSize=base - 2.2,
                          leading=(base - 2.2) * 1.34, textColor=INK)

    data, styles = [], []
    colw = avail_w / float(ncol)
    subw = [colw * 0.30, colw * 0.70]
    for r in range(maxlen):
        row = []
        for ci in range(ncol):
            kind, a, n = cols[ci][r]
            if kind == "GRP":
                row.append(Paragraph(a.upper(), gp_s))
                styles.append(('SPAN', (ci * 2, r), (ci * 2 + 1, r)))
                _g = head_fill()
                if _g is not None:
                    styles.append(('BACKGROUND', (ci * 2, r), (ci * 2 + 1, r), _g))
                else:
                    styles.append(('LINEBELOW', (ci * 2, r), (ci * 2 + 1, r), W_RULE, G50))
                row.append("")
            elif kind == "PAD":
                row.append("")
                row.append("")
            else:
                row.append(Paragraph(a, ab_s))
                row.append(Paragraph(n, nm_s))
        data.append(row)
    widths = []
    for _ in range(ncol):
        widths.extend(subw)
    t = Table(data, colWidths=widths, hAlign='LEFT')
    styles += [
        ('FONT', (0, 0), (-1, -1), SERIF, base - 2.0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2.6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2.0),
        ('LINEAFTER', (1, 0), (1, -1), W_HAIR, G25),
        ('LINEAFTER', (3, 0), (3, -1), W_HAIR, G25),
    ]
    t.setStyle(TableStyle(styles))
    return t


# =====================================================================
#  block renderer
# =====================================================================
def render_blocks(blocks, S, avail_w, base):
    out = []
    for kind, val in blocks:
        if kind == 'lead':
            out.append(Paragraph(val, S['lead']))
        elif kind == 'p':
            out.append(Paragraph(val, S['p']))
        elif kind == 'h2':
            out.append(Paragraph(val, S['h2']))
        elif kind == 'h3':
            out.append(Paragraph(val, S['h3']))
        elif kind == 'bul':
            for it in val:
                out.append(Paragraph(it, S['bul'], bulletText='–'))
        elif kind == 'num':
            for i, it in enumerate(val):
                out.append(Paragraph(it, S['num'], bulletText='%d.' % (i + 1)))
        elif kind == 'note':
            out.append(Spacer(1, 4))
            out.append(NoteBox(Paragraph(val, S['note']),
                               avail_w - S['p'].leftIndent - S['p'].rightIndent))
            out.append(Spacer(1, 5))
        elif kind == 'formula':
            out.append(Paragraph(val, S['formula']))
        elif kind == 'script':
            for who, txt in val:
                out.append(Paragraph('<font name="%s">%s</font>&nbsp;&nbsp;%s'
                                     % (COND_B, who.upper(), txt), S['script_txt']))
        elif kind == 'table':
            out.append(Spacer(1, 3))
            out.append(build_table(val, avail_w, S, base))
            out.append(Spacer(1, 6))
        elif kind == 'sections_table':
            out.append(Spacer(1, 3))
            out.append(build_sections_table(avail_w, base))
            out.append(Spacer(1, 6))
        elif kind == 'fill_grid':
            out.append(Spacer(1, 3))
            out.append(build_fill_grid(val, avail_w, base))
            out.append(Spacer(1, 6))
        elif kind == 'checklist':
            for grp, items in val:
                out.append(Paragraph(grp, S['h3']))
                for it in items:
                    out.append(CheckRow(it, avail_w - S['p'].leftIndent
                                        - S['p'].rightIndent, base - 0.6))
                    out.append(Spacer(1, 1.6))
                out.append(Spacer(1, 3))
        elif kind == 'mark':
            out.append(Spacer(1, 14))
            out.append(Paragraph('<font name="%s" size="%.1f">%s</font>'
                                 % (COND_B, base - 1.5, val),
                                 ParagraphStyle('mk', alignment=TA_CENTER,
                                                textColor=G50)))
        elif kind == 'rule':
            out.append(Rule(avail_w))
    return out


def flow(bk, story, part=None, sec=None, first_page_drop=0.0, folio=True):
    """Push a story through pages until exhausted."""
    S = bk.styles
    while story:
        x, y, w, h = bk.body()
        drop = first_page_drop
        f = Frame(x, y, w, h - drop, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0, showBoundary=0)
        before = len(story)
        f.addFromList(story, bk.c)
        if len(story) == before and story:
            # a single flowable taller than the page: force it and move on
            story.pop(0)
        bk.end_page(kind='ref', part=part, sec=sec, folio=folio)
        first_page_drop = 0.0
    return
