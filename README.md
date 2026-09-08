# K4DIA

The site at [k4dia.com](https://k4dia.com). Static files, served by GitHub
Pages, no build step.

```
index.html          the front page
styles.css          the whole design
site.js             the menu and the dial
fonts/              IBM Plex, self-hosted, SIL Open Font License
logbook/            the Field Record generator, runs in the visitor's browser
CNAME               k4dia.com
```

Nothing here calls out to a third party. The fonts are served from this
domain rather than from Google, and the logbook generator builds its PDF
inside the visitor's own browser, so no callsign or repeater list is ever
sent anywhere.

## Editing

Open the files and change them. There is nothing to compile and nothing to
install. Pushing to `main` publishes.

Photographs go in the three project cards, replacing the ruled placeholder
blocks marked `Photo to come`.

## The logbook

`logbook/` is generated from the FIELD RECORD project. To update it, rebuild
the payload there and copy the folder across:

```
python3 measure_pages.py > pagesizes.json
python3 web/build_payload.py
```
