# FIELD RECORD generator: source

This is the source for `fieldrecord.zip`, the package the browser loads into
Pyodide at `k4dia.com/logbook/`.

Edit here, then rebuild:

```bash
./build.sh          # from logbook/, rebuilds fieldrecord.zip from src/
```

Commit both `src/` and the rebuilt zip. The zip is what the site serves; src/
is what you and anyone else can actually read and diff.

Before October 2026 the only copy of this code lived inside the zip, which
meant a change to the book was an opaque binary diff and nobody could review
it. That is why this directory exists.

## Layout

The zip is flat, because Pyodide unpacks it straight into the working
directory. Modules sit at the root with `radios/` and `assets/` beside them,
and `src/` mirrors that exactly.

| File | What it does |
|---|---|
| `webapi.py` | What the page calls: `catalogue`, `estimate`, `build` |
| `make_book.py` | Lays out one book, two passes for the contents page numbers |
| `build.py` | Page furniture: covers, part titles, the deployment index |
| `forms.py` | The record pages: Site Record, QSO Log, Debrief |
| `engine.py` | `Book`, fonts, rules, tables, the drawing primitives |
| `config.py` | Reads a station config, validates it, picks the parts |
| `personalize.py` | Rebinds the book's text to one station |
| `cover.py` | Cover artwork |
| `content_*.py`, `personal.py`, `radiocard.py`, `rfdata.py` | Reference content |

## Two things the record pages support beyond a blank book

RF Pi's `rfpi-fieldrecord` prints a finished activation onto these pages, so
the form functions take values as well as drawing the rules:

- `fields_row` specs may be `(label, weight)` as before, or
  `(label, weight, value)`. A `Book` may also carry `values`, a dict keyed by
  the field's own label, which `fill_for` swaps per page.
- `minitable` takes `values`, and falls back to `bk.values["<row>|<col>"]`.
- `Book.formgrid` takes `data`, a list of row sequences, or reads
  `bk.grid_data`.
- `st.bare` drops the Part Two divider, for an export that is four pages
  rather than a book.

All of it is additive. A two-element spec and a Book with no values behave
exactly as they always did, and a blank book built with these changes is byte
identical to one built without them.

## Authorship versus ownership

`personalize.apply` used to do `M.AUTHOR = st.byline`, which put the operator's
name on the copyright page as the author and holder of copyright, erased the
real author, and left a CC BY licence demanding credit the book no longer
carried.

Now `M.AUTHOR` is the author and `M.OWNER` is whose copy it is. The cover and
title page carry the owner; the copyright page carries the author and adds
"This copy prepared for ...". If you touch either, keep that split.
