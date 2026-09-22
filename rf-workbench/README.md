# Sideband RF Workbench

A single-page suite of **114 live calculators** for radio, RF propagation, transmission lines, PCB design and general electronics. It includes charts, schematics, cross-sections and a Smith chart. Everything runs in the visitor's browser: there is no server code, no build step to deploy, no tracking and no external requests.

## What's in this folder

```
rf-workbench/
├── index.html           ← the complete app (HTML + CSS + JS in one file)
├── fonts/               ← self-hosted web fonts used by index.html
│   ├── fonts.css
│   ├── *.woff2          (Barlow Semi Condensed, IBM Plex Sans, IBM Plex Mono)
│   └── OFL-*.txt        (font licences, keep these with the fonts)
├── embed-example.html   ← copy-paste example for putting it inside an existing page
├── src/                 ← editable source the page is built from
│   ├── 00-head.html     (page shell, colours, layout CSS)
│   ├── 10-core.js       (units, formatting, charts, schematic drawing, card engine)
│   ├── 20-prop.js … 70-amp-phys-conv.js   (the calculators, grouped by category)
│   ├── 90-boot.js       (navigation, search, pinning)
│   └── build.py         (rebuilds ../index.html from the parts)
└── README.md
```

## Put it on your website

**The page needs only `index.html` and the `fonts/` folder.** Keep them side by side.

### Option 1: its own page (recommended)
Upload the whole `rf-workbench` folder to your web host, for example with FTP, cPanel File Manager or your host's upload tool. It will then be live at:

```
https://your-site.com/rf-workbench/
```

Link to it from your menu. Individual calculators can be linked directly with a `#` anchor:

| Link | Opens |
|---|---|
| `/rf-workbench/#linkbudget` | Link Budget |
| `/rf-workbench/#fresnel` | Fresnel Zone & Path Clearance |
| `/rf-workbench/#hata` | Okumura–Hata / COST-231 |
| `/rf-workbench/#vswr` | VSWR / Return Loss |
| `/rf-workbench/#microstrip` | Microstrip Impedance |
| `/rf-workbench/#rescolor` | Resistor Colour Code |
| `/rf-workbench/#bench-tline` | a whole category (`prop`, `rf`, `ant`, `match`, `atten`, `tline`, `ind`, `circ`, `amp`, `phys`, `conv`) |

Every card's anchor is its `id:` in the `src/*.js` files.

### Option 2: inside an existing page (iframe)
After uploading as in Option 1, paste this where you want it to appear:

```html
<iframe src="/rf-workbench/index.html" title="RF and circuit calculators"
        style="display:block;width:100%;height:100vh;border:0" loading="lazy"></iframe>
```

A fixed `height:100vh` keeps the workbench's sticky search bar and category menu working. If you would rather the frame grow to the full length of the page, see the optional script in `embed-example.html`. The page reports its height to the parent page for exactly this purpose.

### Site builders
- **WordPress:** upload the folder to your site root with your host's File Manager or SFTP (next to `wp-content`), then link to it or use a *Custom HTML* block with the iframe above.
- **Squarespace, Wix, Webflow, Shopify:** these don't let you upload a folder of files. Host the folder somewhere free and static, then add the iframe in a *Code* / *Embed* block with `src` set to that full URL. Options include GitHub Pages, Netlify Drop (drag the folder onto app.netlify.com/drop) and Cloudflare Pages.
- **GitHub Pages:** push this folder to a repository, enable Pages, and it is served as-is.

No server-side language, database or special MIME configuration is needed. Any static host works, and the page also runs straight from your computer by double-clicking `index.html`.

## Customise it

Edit the files in `src/`, then rebuild:

```bash
cd src
python3 build.py                 # writes ../index.html with the self-hosted fonts
python3 build.py --google-fonts  # optional: load fonts from Google instead of fonts/
```

- **Colours:** change the tokens at the top of `src/00-head.html`. The first `:root { … }` block is the light theme and the two blocks after it are dark mode. `--accent` is the orange highlight and `--trace` is the chart blue.
- **Name and intro text:** the `<title>`, the brand in `<header class="top">` and the `<section class="intro">` are all in `src/00-head.html`.
- **Default values:** each input is written as `N('id','Label','unit',defaultValue,'defaultUnit')` in the calculator files.
- **Add a calculator:** copy an existing `def({...})` block. `inputs`, `outputs` and `calc(v)` are required. `viz`, `fx` (formulas) and `notes` are optional. Inputs arrive in `calc` already converted to SI units.

Python 3.8 or newer is the only requirement for rebuilding, and it's not needed to host the site.

## Features
- Results recalculate as you type. Each field has its own unit selector, and values accept SI shorthand such as `4k7`, `2.2n`, `150M` or `1e-6`.
- "Solve for" buttons on calculators like Friis, LC resonance, RC, Snell's law and C = Q/V let you pick the unknown.
- Charts, schematics with component values, PCB and coax cross-sections, a Smith chart, a spectrum band map and a clickable resistor colour chart.
- Search (press `/`), a category menu, and ☆ pinning of favourites (stored only in the visitor's own browser).
- Light and dark themes follow the visitor's system setting. The layout works from phones to wide monitors.
- Each card has a "Formula & notes" panel showing the equations and their validity limits.

## Calculators

**Propagation & Links** (17): Spectrum Locator · Link Budget · Free Space Path Loss · Friis Transmission Equation · EIRP & ERP · Power Density & RF Exposure · Fresnel Zone & Path Clearance · Radio Horizon & Line of Sight · Two-Ray Ground Reflection · Okumura–Hata / COST-231 Path Loss · Knife-Edge Diffraction · Receiver Sensitivity & Noise Floor · Fade Margin & Availability · Rain Fade · HF Skywave MUF · Doppler Shift · Radar Maximum Range

**RF Power & Signal** (14): RF Power Conversion · Decibel Calculator · RF Power Ratio Conversion · VSWR / Return Loss · Noise Figure & Noise Temperature · Cascaded Noise Figure · Power Added Efficiency · N-Way Power Divider · Wavelength (TEM) · Peak, Peak-to-Peak, RMS & Average Voltage · Skin Depth · Mixer Image & IF Frequency · Two-Tone IP3 & Intermod · Coax Cable Loss

**Antennas** (7): Dipole & Vertical Lengths · Parabolic Dish Gain · Antenna Gain, Aperture & Antenna Factor · Microstrip Patch Antenna · Antenna Downtilt & Coverage · Near-Field / Far-Field Boundary · Polarisation Mismatch Loss

**Matching & Filters** (8): Smith Chart Load · L-Match Network · Pi-Match Network · T-Match Network · Quarter-Wave Transformer · LC Resonant Frequency · LC Tank Circuit · Butterworth LC Filter (Low-, High- & Band-pass)

**Attenuators** (5): T-Pad Attenuator · Pi Attenuator · Bridged-Tee Attenuator · Balanced Attenuator (H & O pad) · Reflection Attenuator

**Transmission Lines & PCB** (18): Microstrip Impedance · Embedded Microstrip Impedance · Symmetric Stripline Impedance · Asymmetric Stripline Impedance · Edge-Coupled Microstrip Impedance · Edge-Coupled Stripline Impedance · Broadside-Coupled Stripline Impedance · Wire Microstrip Impedance · Wire Stripline Impedance · Coax Impedance · Twisted-Pair Impedance · Microstrip Wavelength · PCB Trace Current & Width (IPC-2221) · Trace Resistance · Rectangular Waveguide · Circular Waveguide · Microstrip Crosstalk · Stripline Crosstalk

**Inductance** (10): Coil Inductance · Wire Self-Inductance · Parallel Wire Inductance · Wire Loop Inductance · Rectangle Loop Inductance · Wire-Over-Plane Inductance · Coax Inductance · Microstrip Inductance · Edge-Coupled Trace Inductance · Broadside-Coupled Trace Inductance

**Circuits & Passives** (15): Resistor Colour Code (4, 5 & 6 Band) · Ohm’s Law · Parallel Resistors · Voltage Divider · Wheatstone Bridge · RC Time Constant · Capacitor Charge & Energy · Capacitance (C = Q/V) · Capacitive Reactance & Admittance · Capacitor Impedance · Inductive Reactance & Admittance · Resistivity · Series LED Resistor · MCD to Lumens · Electrical Energy

**Op-Amps, Timers & Power** (11): Inverting Op-Amp Resistors · Non-Inverting Op-Amp Resistors · Op-Amp Voltage & Gain · Instrumentation Amplifier Gain · Comparator with Hysteresis (Schmitt Trigger) · 555 Timer: Monostable · 555 Timer: Astable Oscillator · Stepper Motor Speed & Power · Flyback Converter Design · Heat Sink · Battery Life

**Physics & Optics** (4): Lorentz Force · Faraday’s & Lenz’s Law · Snell’s Law · Speed, Distance & Time

**Unit Converters & Math** (5): Pressure Unit Converter · Torque Converter · Temperature Converter · Unit Conversion · Square, Cube & Nth Root
## Licences and credits
- **Fonts:** Barlow Semi Condensed (© The Barlow Project Authors) and IBM Plex Sans / Mono (© IBM Corp.), both under the SIL Open Font License 1.1. The licence texts are in `fonts/` and must stay with the font files.
- **Formulas:** standard published engineering relations, including IPC-2141 and IPC-2221, Hammerstad–Jensen, Wheeler, Okumura–Hata / COST-231, ITU-R P.526 and P.838-3, Barnett–Vigants, FCC OET-65 and Friis. Each card cites its equations.
- **Disclaimer:** the results are engineering approximations for design and education. Verify critical designs against a field solver, the relevant standard or a measurement.
