# -*- coding: utf-8 -*-
"""FIELD RECORD - Part One reference sections, group B: technical and field."""

UTC_ROWS = [
    ["00", "20", "19", "18", "17", "16", "15"],
    ["01", "21", "20", "19", "18", "17", "16"],
    ["02", "22", "21", "20", "19", "18", "17"],
    ["03", "23", "22", "21", "20", "19", "18"],
    ["04", "00*", "23", "22", "21", "20", "19"],
    ["05", "01*", "00*", "23", "22", "21", "20"],
    ["06", "02*", "01*", "00*", "23", "22", "21"],
    ["12", "08", "07", "06", "05", "04", "03"],
    ["18", "14", "13", "12", "11", "10", "09"],
    ["21", "17", "16", "15", "14", "13", "12"],
    ["22", "18", "17", "16", "15", "14", "13"],
    ["23", "19", "18", "17", "16", "15", "14"],
]

SEC_TIME = dict(
    tag="TIME",
    title="Time and the Zulu Day",
    blocks=[
        ("lead",
         "Amateur radio is keyed to Coordinated Universal Time. A net at 0100Z "
         "meets at the same instant everywhere; one operator's Tuesday evening "
         "is another's Wednesday morning, and both log the same time."),
        ("h3", "North American conversion, UTC to local clock"),
        ("p",
         "An asterisk indicates that the local date is one day earlier than the "
         "UTC date. This is where activation counts are most often lost."),
        ("table", dict(head=["UTC", "EDT (-4)", "CDT (-5)", "MDT (-6)", "PDT (-7)", "AKDT (-8)", "HST (-10)"],
                       rows=UTC_ROWS, w=[1.0 / 7] * 7,
                       align=['c'] * 7, mono=list(range(7)), size=8.0)),
        ("p",
         "Standard time in winter shifts each column one hour further back: EST "
         "is UTC minus 5, CST is UTC minus 6, and so on. Hawaii does not observe "
         "daylight saving time and stays at UTC minus 10 year round. Arizona, "
         "excepting the Navajo Nation, stays at UTC minus 7 year round."),
        ("h3", "Logging practice"),
        ("bul", [
            "Set the transceiver clock to UTC and leave it. Conversion in the "
            "field is a source of error.",
            "Enter the UTC date at the head of every sheet before the first "
            "contact, and rule a heavy line across the grid at the rollover with "
            "the new date beside it.",
        ]),
        ("h3", "Spoken form"),
        ("p",
         "Say 0100Z as \"zero one hundred Zulu\" and 1430Z as \"fourteen thirty "
         "Zulu.\" On CW, times are usually sent as four digits with no punctuation."),
    ])

GRID_ROWS = [
    ["Field", "2 letters, A to R", "20 deg longitude by 10 deg latitude", "FN, EM, DM"],
    ["Square", "2 digits, 0 to 9", "2 deg longitude by 1 deg latitude", "FN31, EM73"],
    ["Subsquare", "2 letters, a to x", "5 min longitude by 2.5 min latitude", "FN31pr"],
    ["Extended", "2 digits", "30 sec longitude by 15 sec latitude", "FN31pr55"],
]

SEC_GRID = dict(
    tag="GRID",
    title="Maidenhead Grid Squares",
    blocks=[
        ("lead",
         "The Maidenhead locator is a compressed coordinate. Six characters "
         "resolve to a few miles, which is sufficient for a VHF contact and "
         "short enough to send on CW."),
        ("h3", "How the locator is built"),
        ("table", dict(head=["Level", "Characters", "Size", "Example"],
                       rows=GRID_ROWS, w=[0.16, 0.20, 0.40, 0.24],
                       align=['l', 'l', 'l', 'l'], mono=[3])),
        ("h3", "Deriving a locator"),
        ("p",
         "You will not usually need to. Any handheld GPS, phone app, or modern "
         "radio will report it. But the arithmetic is worth understanding once, "
         "because it tells you what the letters mean."),
        ("num", [
            "Take longitude, add 180 so the numbering starts at the antimeridian. "
            "Divide by 20. The whole part indexes the first field letter, A through R.",
            "Take latitude, add 90. Divide by 10. The whole part indexes the second "
            "field letter.",
            "Divide the longitude remainder by 2 for the first digit, and take the "
            "whole latitude remainder for the second digit.",
            "Divide what is left of longitude by 5 minutes for the first subsquare "
            "letter and what is left of latitude by 2.5 minutes for the second, "
            "a through x.",
        ]),
        ("note",
         "Longitude is always given first. FN31 and 31FN are not the same "
         "place, and the second character of the field carries latitude. A "
         "locator that resolves to open ocean usually indicates a transposed "
         "pair."),
        ("h3", "Estimating distance"),
        ("p",
         "At mid latitudes in North America, one full grid square is roughly 100 "
         "miles north to south and roughly 100 miles east to west. Counting "
         "squares on a map is accurate enough for deciding whether a 2 meter "
         "SSB contact was worth writing home about."),
        ("h3", "Sites and locators"),
        ("fill_grid", dict(rows=6, cols=3,
                           labels=["Site name", "Grid (6 char)", "Coordinates"])),
    ])

PROP_ROWS = [
    ["SFI, solar flux index", "65 to 300", "Higher is better for the high bands. Below 75 the "
     "bands above 20 meters are usually dead. Above 150, 10 and 15 meters open widely."],
    ["A index", "0 to 400, daily", "Geomagnetic disturbance averaged over a day. Below 10 is "
     "quiet. Above 20 expect degraded polar and high latitude paths."],
    ["K index", "0 to 9, every 3 hours", "The number to watch. 0 to 2 is quiet, 3 is unsettled, "
     "4 is active, 5 and above is a storm and your high band DX is finished for a while."],
    ["MUF", "Varies by path and hour", "Maximum usable frequency for a given path. Work just "
     "below it for the strongest signals."],
    ["LUF", "Varies by path and hour", "Lowest usable frequency. Absorption below it eats you alive, "
     "which is why 80 meters is useless at noon."],
]

BANDCLOCK_ROWS = [
    ["160 m", "Dead", "Dead", "Opening", "Best", "Best", "Closing", "Winter nights only. Very quiet sites required."],
    ["80/75 m", "Local", "Local", "Regional", "Regional to DX", "DX", "Regional", "Reliable 300 mile band after dark."],
    ["60 m", "Local", "Local", "Regional", "Regional", "Regional", "Regional", "Excellent NVIS. Very stable."],
    ["40 m", "Regional", "Regional", "Regional to DX", "DX", "DX", "Regional", "The one band that works nearly all day."],
    ["30 m", "Regional", "Regional", "DX", "DX", "DX", "Regional", "CW and data only. Quiet and underused."],
    ["20 m", "Opening", "Best", "Best", "Best", "Closing", "Dead", "The workhorse for daytime portable operating."],
    ["17 m", "Opening", "Good", "Good", "Good", "Closing", "Dead", "Less crowded than 20. Try it first."],
    ["15 m", "Opening", "Good", "Best", "Good", "Closing", "Dead", "Needs SFI above about 110 to be useful."],
    ["12 m", "Marginal", "Good", "Good", "Marginal", "Dead", "Dead", "Feast or famine. Check it when 15 is open."],
    ["10 m", "Marginal", "Good", "Best", "Marginal", "Dead", "Dead", "Sporadic E in May to August regardless of the sun."],
    ["6 m", "Sporadic E", "Sporadic E", "Sporadic E", "Sporadic E", "Dead", "Dead", "June and July. Watch 50.125 constantly."],
]

SEC_PROP = dict(
    tag="PROP",
    title="Propagation for the Field Operator",
    blocks=[
        ("lead",
         "Practical propagation planning reduces to two decisions: which band "
         "to work, and whether a given site is worth operating from."),
        ("h3", "Indices"),
        ("table", dict(head=["Index", "Range", "What it tells you"],
                       rows=PROP_ROWS, w=[0.19, 0.18, 0.63],
                       align=['l', 'l', 'l'], size=7.4)),
        ("h3", "Band by band, by time of day"),
        ("p",
         "A rough guide for a mid latitude North American station at moderate "
         "solar activity. Local means under 100 miles, regional means roughly "
         "100 to 1000 miles, DX means beyond that."),
        ("table", dict(head=["Band", "Dawn", "Morning", "Midday", "Afternoon", "Dusk", "Night", "Notes"],
                       rows=BANDCLOCK_ROWS,
                       w=[0.075, 0.095, 0.095, 0.095, 0.10, 0.09, 0.09, 0.36],
                       align=['l', 'c', 'c', 'c', 'c', 'c', 'c', 'l'], size=6.8)),
        ("h3", "Grayline"),
        ("p",
         "For roughly 30 to 60 minutes at your local sunrise and sunset, the "
         "band of twilight sweeping the earth carries low band signals far better "
         "than either full day or full night. The D layer, which absorbs, has "
         "decayed; the F layer, which refracts, has not. Paths along that line "
         "open dramatically. If you are chasing distance on 40 or 80 meters from "
         "a park, arrive early enough to catch your own sunset."),
        ("h3", "Near vertical incidence skywave"),
        ("p",
         "Near vertical incidence skywave fills the gap between ground wave and "
         "the first skip zone, roughly 0 to 300 miles. Put a dipole low, a tenth "
         "of a wavelength up or less, on 80, 60, or 40 meters, and the pattern "
         "fires almost straight up. It comes back down over a wide circle with no "
         "dead zone. This is the correct configuration for regional emergency "
         "traffic and for working your own state, and it is the one time in "
         "amateur radio when a low antenna is the right antenna."),
        ("note",
         "Site noise is a propagation factor. A site three decibels quieter "
         "than the usual noise floor yields more than doubling transmitter "
         "power. Record the measured noise floor on every Site Record; sites "
         "reading S1 on 40 meters are worth the travel."),
    ])

WIRE_ROWS = [
    ["160", "1.900", "246.3", "123.2", "492.6", "Full size is rarely portable. Consider a loaded vertical."],
    ["80", "3.650", "128.2", "64.1", "256.4", "A sloped or inverted V fits most parks."],
    ["60", "5.360", "87.3", "43.7", "174.6", "Excellent NVIS at 15 to 25 feet."],
    ["40", "7.150", "65.5", "32.7", "130.9", "The standard portable dipole."],
    ["30", "10.125", "46.2", "23.1", "92.4", "Fits between the trees almost anywhere."],
    ["20", "14.200", "33.0", "16.5", "65.9", "The one to build first."],
    ["17", "18.118", "25.8", "12.9", "51.7", ""],
    ["15", "21.300", "22.0", "11.0", "43.9", ""],
    ["12", "24.940", "18.8", "9.4", "37.5", ""],
    ["10", "28.400", "16.5", "8.2", "33.0", "A full wave EFHW here is only 33 feet."],
    ["6", "50.150", "9.3", "4.7", "18.7", "Short enough to hold up on a painter's pole."],
]

VF_ROWS = [
    ["RG-58 solid PE", "0.66", "50", "1.8", "2.6", "3.3", "6.2", "11.5"],
    ["RG-8X foam PE", "0.82", "50", "1.2", "1.7", "2.3", "4.0", "7.4"],
    ["RG-213 solid PE", "0.66", "50", "0.6", "0.9", "1.2", "2.2", "4.2"],
    ["LMR-400 type", "0.85", "50", "0.4", "0.6", "0.8", "1.5", "2.7"],
    ["RG-174 thin", "0.66", "50", "5.5", "7.5", "9.5", "17.0", "31.0"],
    ["450 ohm window", "0.91", "450", "0.05", "0.08", "0.10", "0.25", "0.55"],
]

SWR_ROWS = [
    ["1.0 : 1", "0.000", "0.0 %", "Infinite", "0.00"],
    ["1.2 : 1", "0.091", "0.8 %", "20.8 dB", "0.04"],
    ["1.5 : 1", "0.200", "4.0 %", "14.0 dB", "0.18"],
    ["2.0 : 1", "0.333", "11.1 %", "9.5 dB", "0.51"],
    ["2.5 : 1", "0.429", "18.4 %", "7.4 dB", "0.88"],
    ["3.0 : 1", "0.500", "25.0 %", "6.0 dB", "1.25"],
    ["4.0 : 1", "0.600", "36.0 %", "4.4 dB", "1.94"],
    ["5.0 : 1", "0.667", "44.4 %", "3.5 dB", "2.55"],
    ["10.0 : 1", "0.818", "66.9 %", "1.7 dB", "4.81"],
]

SEC_ANT = dict(
    tag="ANT",
    title="Antenna Math for the Field",
    blocks=[
        ("lead",
         "Wire is the portable station's principal advantage: light, cheap, "
         "and, at a half wavelength in a tree, consistently better than a "
         "shortened whip at vehicle height."),
        ("h3", "Wire lengths, in feet"),
        ("p",
         "Half wave uses 468 divided by frequency in megahertz. Quarter wave uses "
         "234. Full wave, for end fed half wave transformers used on their "
         "harmonic bands and for loops, uses 936. These are rules of thumb that "
         "already include an end effect correction. Cut long by three percent, "
         "measure, then trim."),
        ("table", dict(head=["Band", "Design f (MHz)", "Half wave (ft)", "Quarter wave (ft)", "Full wave (ft)", "Field notes"],
                       rows=WIRE_ROWS, w=[0.08, 0.13, 0.14, 0.15, 0.13, 0.37],
                       align=['l', 'r', 'r', 'r', 'r', 'l'], mono=[1, 2, 3, 4], size=7.4)),
        ("h3", "Height and pattern"),
        ("bul", [
            "A horizontal dipole at a quarter wavelength or lower fires most of "
            "its energy up. That is NVIS, and it is the right choice for regional work.",
            "The same dipole at a half wavelength drops the main lobe to roughly "
            "30 degrees and starts to work DX.",
            "Above one wavelength, gains are real but small and the rigging cost "
            "rises fast. In a park, spend your effort on getting the feedpoint "
            "clear of the ground rather than on the last five feet of height.",
            "A quarter wave vertical needs radials. Four elevated radials cut for "
            "the band beat sixteen random wires on the dirt. With no radials at "
            "all, your coax shield becomes the counterpoise and the pattern is "
            "whatever the coax feels like.",
            "An end fed half wave with a 49 to 1 transformer still needs a "
            "counterpoise, usually a length of wire around 0.05 wavelength, or the "
            "feedline does the job badly.",
        ]),
        ("h3", "SWR, return loss and mismatch loss"),
        ("p",
         "The reflected power figure is the fraction of forward power that comes "
         "back from the mismatch. In a low loss line, most of it is re-reflected "
         "by the transmitter and eventually radiated, so a 2 to 1 match is not "
         "wasting eleven percent of your signal. What high SWR really costs you "
         "is transmitter power foldback and extra loss in lossy coax."),
        ("table", dict(head=["SWR", "Reflection coeff", "Reflected power", "Return loss", "Mismatch loss (dB)"],
                       rows=SWR_ROWS, w=[0.16, 0.21, 0.21, 0.20, 0.22],
                       align=['l', 'r', 'r', 'r', 'r'], mono=[0, 1, 2, 3, 4])),
        ("h3", "Feedline, nominal loss per 100 feet, matched"),
        ("table", dict(head=["Cable", "VF", "Z0", "14 MHz", "28 MHz", "50 MHz", "146 MHz", "440 MHz"],
                       rows=VF_ROWS, w=[0.22, 0.09, 0.08, 0.122, 0.122, 0.122, 0.122, 0.12],
                       align=['l', 'c', 'c', 'r', 'r', 'r', 'r', 'r'], mono=[1, 2, 3, 4, 5, 6, 7], size=7.4)),
        ("note",
         "Losses accumulate without being obvious. Fifty feet of RG-174 at "
         "146 MHz dissipates more than half the transmitter output before the "
         "antenna. For a low power field station a short run of RG-8X is "
         "generally the best compromise between weight and loss. Velocity "
         "factor applies when cutting a matching stub or a quarter wave "
         "transformer: multiply the free space length by VF."),
    ])

POWER_ROWS = [
    ["Receive, headphones", "0.5 - 1.0 A", "Most of a long day is spent here."],
    ["Receive, internal speaker", "0.8 - 1.5 A", "Headphones save real amp-hours."],
    ["Transmit, 5 W SSB", "1.5 - 2.5 A", "Average on voice is far below peak."],
    ["Transmit, 10 W SSB", "2.5 - 4 A", ""],
    ["Transmit, 100 W SSB", "18 - 22 A peak", "Voice duty cycle keeps the average near a third of this."],
    ["Transmit, 100 W CW", "15 - 20 A key down", "Key down is continuous. Budget for it."],
    ["Transmit, 100 W digital", "18 - 22 A continuous", "Worst case. Full duty cycle, and it heats the finals."],
    ["Tablet or logging device", "0.5 - 1.5 A", "Charge it from the same battery and it is part of the budget."],
]

WIRE_GAUGE_ROWS = [
    ["18 AWG", "10 A", "0.0064", "Accessory leads, control lines"],
    ["16 AWG", "13 A", "0.0040", "Light accessory runs"],
    ["14 AWG", "17 A", "0.0025", "QRP main feed, short runs"],
    ["12 AWG", "23 A", "0.0016", "100 W radio main feed, under 6 feet"],
    ["10 AWG", "33 A", "0.0010", "100 W radio, longer runs, battery to panel"],
    ["8 AWG", "46 A", "0.00063", "Battery main and disconnect"],
]

SEC_POWER = dict(
    tag="POWER",
    title="Power Budget, Battery, and Wiring",
    blocks=[
        ("lead",
         "A field station is limited by its supply more often than by "
         "propagation or equipment. Both the capacity and the wiring have to be "
         "sized to the actual load."),
        ("h3", "Typical current draw at 13.8 V"),
        ("table", dict(head=["State", "Current", "Notes"],
                       rows=POWER_ROWS, w=[0.28, 0.18, 0.54],
                       align=['l', 'l', 'l'], size=7.4)),
        ("h3", "Runtime"),
        ("p",
         "Estimate an average current, not a peak. For a normal operating "
         "session, assume you transmit about one third of the time on phone and "
         "about half the time on CW. Then:"),
        ("formula", "Average A  =  (RX amps x RX fraction)  +  (TX amps x TX fraction)"),
        ("formula", "Runtime h  =  (Battery Ah x usable fraction)  /  Average A"),
        ("p",
         "Usable fraction depends on chemistry. Lithium iron phosphate will give "
         "you roughly 90 percent of rated capacity with a flat voltage curve "
         "almost to the end. Sealed lead acid should be treated as 50 percent "
         "usable if you want the battery to survive the year, and its voltage "
         "sags under transmit load in a way that will make a radio unhappy long "
         "before the amp-hours run out."),
        ("h3", "Runtime worksheet"),
        ("fill_grid", dict(rows=5, cols=4,
                           labels=["Configuration", "Avg current (A)", "Battery (Ah usable)", "Predicted hours"])),
        ("h3", "Wire gauge and fusing for 12 volt DC"),
        ("p",
         "Fuse to protect the wire, not the radio. The fuse should open before "
         "the smallest conductor in the branch reaches its rating. Fuse the "
         "positive lead as close to the battery terminal as physically possible: "
         "everything downstream of that point is unprotected."),
        ("table", dict(head=["Gauge", "Practical DC limit", "Ohms per foot", "Typical use in a field station"],
                       rows=WIRE_GAUGE_ROWS, w=[0.13, 0.19, 0.16, 0.52],
                       align=['l', 'l', 'r', 'l'], mono=[2])),
        ("h3", "Lithium iron phosphate"),
        ("bul", [
            "Do not charge below freezing. LiFePO4 will accept charge at low "
            "temperature and plate lithium doing it, which permanently destroys "
            "capacity. Discharging cold is fine.",
            "The internal battery management system is a protection device, not a "
            "charge controller and not a substitute for a fuse. When it trips, it "
            "disconnects the whole pack, usually in the middle of your best contact.",
            "A LiFePO4 pack holds near 13.2 volts across most of its discharge and "
            "then falls off a cliff. Voltage is a poor fuel gauge. Track amp-hours "
            "or carry a coulomb counter.",
            "Charge to storage voltage, not full, if the pack will sit for months.",
            "Carry the pack in a hard case with the terminals covered. A wrench "
            "across a 20 amp-hour pack will weld itself to the terminals.",
        ]),
    ])

MPE_ROWS = [
    ["0.3 - 1.34 MHz", "100", "180 / f squared", "f in MHz"],
    ["1.34 - 3.0 MHz", "900 / f squared", "180 / f squared", ""],
    ["3.0 - 30 MHz", "900 / f squared", "180 / f squared", "At 14 MHz: 4.59 controlled, 0.92 uncontrolled"],
    ["30 - 300 MHz", "1.0", "0.2", "The most restrictive range"],
    ["300 - 1500 MHz", "f / 300", "f / 1500", ""],
    ["1500 - 100,000 MHz", "5.0", "1.0", ""],
]

SEC_SAFETY = dict(
    tag="SAFE",
    title="RF Exposure and Field Safety",
    blocks=[
        ("lead",
         "Since 3 May 2023 every amateur station in the United States must "
         "have a current RF exposure evaluation, at any power level. The "
         "categorical exemption by power was removed. The evaluation is "
         "retained by the licensee and is not filed with anyone."),
        ("h3", "Maximum permissible exposure, mW per square centimeter"),
        ("p",
         "Controlled means you and people who know the transmitter is there and "
         "can act accordingly. Uncontrolled means everybody else, which in a "
         "public park means everybody else."),
        ("table", dict(head=["Frequency", "Controlled (MPE)", "Uncontrolled (MPE)", "Notes"],
                       rows=MPE_ROWS, w=[0.24, 0.20, 0.22, 0.34],
                       align=['l', 'l', 'l', 'l'], size=7.4)),
        ("h3", "Evaluating a portable station"),
        ("num", [
            "Record your maximum power at the antenna feedpoint, your antenna "
            "gain, your duty cycle, and the lowest frequency you will use.",
            "Compute or look up the minimum safe distance for uncontrolled "
            "exposure at that power and frequency.",
            "Set up so that the nearest point the public can reach exceeds that "
            "distance. In practice this means the feedpoint and the high current "
            "portion of the wire are out of arm's reach of a trail.",
            "Write the result down. The Site Record page in Part Two has a field "
            "for the exclusion distance you used.",
        ]),
        ("note",
         "In a public area the governing hazard is contact with the high "
         "voltage end of an end fed wire, not diffuse field exposure at the "
         "operating position. Keep wire ends above head height and clear of "
         "any path."),
        ("h3", "Weather and lightning"),
        ("bul", [
            "You are erecting a conductor on a mast in an open field. Treat the "
            "first distant thunder as the signal to take it down, not as a "
            "prompt to check the radar.",
            "Thirty minutes after the last thunder before you put anything back up.",
            "A fiberglass mast is not an insulator once it is wet.",
            "Disconnect the feedline from the radio when you break for lunch. It "
            "costs nothing.",
        ]),
        ("h3", "Site and personal safety"),
        ("bul", [
            "Look up before you throw a line. Power lines end more amateur careers "
            "than anything else in this book. If a wire could reach a power line "
            "when it falls, the site is wrong.",
            "Mark guy lines and radials with flagging tape. In a public park, "
            "somebody will walk into them.",
            "Water, shade, and a hat outlast enthusiasm. Cold weather operating "
            "fails through hands, not through gear.",
            "Leave no trace. Pack out the wire ties, the electrical tape, and the "
            "little plastic caps off the connectors. Amateur radio's access to "
            "public land is a courtesy, and it is revocable.",
            "Tell somebody where you are going and when you will be back, "
            "particularly for summits. A handheld on 146.520 is not a rescue plan.",
        ]),
    ])

SEC_SECTIONS = dict(
    tag="SECT",
    title="ARRL and RAC Sections",
    blocks=[
        ("lead",
         "The section abbreviation forms the exchange in Field Day, "
         "Sweepstakes and the Simulated Emergency Test. Sections are not "
         "states: several states are divided, and some sections cross state "
         "lines."),
        ("sections_table", None),
        ("note",
         "Florida holds three sections: Northern, Southern and West Central. "
         "Massachusetts, New York, New Jersey, Pennsylvania, Texas, Washington "
         "and California are also divided. Establish which section a site falls "
         "in before operating near a boundary."),
    ])

PREFIX_ROWS = [
    ["North America", "K, N, W, AA-AL", "United States", "VE, VA, VO, VY", "Canada"],
    ["", "XE, XF", "Mexico", "KP4, NP4, WP4", "Puerto Rico"],
    ["", "KH6, NH6, WH6", "Hawaii", "KL7, AL7, NL7", "Alaska"],
    ["", "CO, CM", "Cuba", "HI", "Dominican Republic"],
    ["South America", "PY, PP-PW", "Brazil", "LU", "Argentina"],
    ["", "CE", "Chile", "HK", "Colombia"],
    ["", "YV", "Venezuela", "OA", "Peru"],
    ["Europe", "G, M, 2E", "England", "GM, MM", "Scotland"],
    ["", "EI", "Ireland", "F", "France"],
    ["", "DL, DA-DR", "Germany", "I", "Italy"],
    ["", "EA", "Spain", "CT", "Portugal"],
    ["", "PA", "Netherlands", "ON", "Belgium"],
    ["", "SM", "Sweden", "LA", "Norway"],
    ["", "OH", "Finland", "OZ", "Denmark"],
    ["", "SP", "Poland", "OK", "Czech Republic"],
    ["", "HA", "Hungary", "YO", "Romania"],
    ["", "UA, R", "Russia", "UR", "Ukraine"],
    ["", "S5", "Slovenia", "9A", "Croatia"],
    ["", "HB9", "Switzerland", "OE", "Austria"],
    ["Africa", "ZS", "South Africa", "CN", "Morocco"],
    ["", "SU", "Egypt", "5N", "Nigeria"],
    ["", "5Z", "Kenya", "EA8", "Canary Islands"],
    ["Asia", "JA-JS", "Japan", "BY, BA-BL", "China"],
    ["", "HL, DS", "South Korea", "VU", "India"],
    ["", "9V", "Singapore", "HS", "Thailand"],
    ["", "4X, 4Z", "Israel", "TA", "Turkey"],
    ["Oceania", "VK", "Australia", "ZL", "New Zealand"],
    ["", "KH2", "Guam", "FK", "New Caledonia"],
    ["", "YB", "Indonesia", "DU", "Philippines"],
]

SEC_PREFIX = dict(
    tag="PFX",
    title="Common Callsign Prefixes",
    blocks=[
        ("lead",
         "A working subset, sufficient to place a signal before checking it "
         "properly. DXCC counts entities rather than countries, and the "
         "official list is longer than this page."),
        ("h3", "US call areas"),
        ("p",
         "The numeral in a US callsign originally indicated the licensee's call "
         "area, and for vanity and older calls it usually still reflects where "
         "the licensee lived when the call was issued. It has not been a "
         "reliable location indicator for decades. Ask for a state."),
        ("table", dict(head=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                       rows=[["CO IA KS MN\nMO ND NE SD", "CT MA ME\nNH RI VT",
                              "NY NJ", "DE PA MD\nDC", "AL FL GA KY\nNC SC TN VA",
                              "AR LA MS NM\nOK TX", "CA", "AK AZ ID MT\nNV OR UT\nWA WY",
                              "MI OH WV", "IL IN WI"]],
                       w=[0.10] * 10, align=['l'] * 10, size=6.6)),
        ("h3", "By region and entity"),
        ("table", dict(head=["Region", "Prefix", "Entity", "Prefix", "Entity"],
                       rows=PREFIX_ROWS, w=[0.16, 0.14, 0.22, 0.16, 0.32],
                       align=['l', 'l', 'l', 'l', 'l'], size=7.2, mono=[1, 3])),
    ])


CHECK_PRE = [
    ("License and identity", [
        "Callsign known and correct for the mode of operation",
        "Any portable indicator decided before you leave",
        "Award program reference number written down, with prefix",
    ]),
    ("Radio and control", [
        "Radio, microphone, key or paddle, and their cables",
        "Clock set to UTC and verified",
        "Power output set to the band and program limits",
        "Spare fuses for every fused device",
    ]),
    ("Antenna", [
        "Wire, transformer or balun, and insulators",
        "Throw line, weight, and a second throw line",
        "Mast, guys, stakes, and something to drive them with",
        "Coax and the adapters you actually need, not all of them",
        "Antenna analyzer or SWR meter",
    ]),
    ("Power", [
        "Battery charged, and the charge state actually verified",
        "Fused leads, Powerpole or equivalent, no bare terminals",
        "Second battery or a charging plan for a long day",
    ]),
    ("Logging", [
        "This book, and two pencils",
        "Electronic log ready and its device charged",
        "Paper backup of the reference number and any schedule",
    ]),
    ("Personal and site", [
        "Water, food, sun and insect protection, layers",
        "Site permission and hours confirmed",
        "Somebody knows where you are and when you will be back",
        "Phone charged, and you know whether it will have coverage",
    ]),
]

CHECK_POST = [
    ("Before closing down", [
        "Contact count meets the program minimum inside one UTC day",
        "Every time in the log is UTC",
        "Park to park and summit to summit contacts flagged",
        "Debrief page started while the details are fresh",
    ]),
    ("Teardown", [
        "Antenna down, wire coiled, nothing left in a tree",
        "All stakes, guys, and flagging recovered",
        "Battery disconnected and terminals covered",
        "Connectors capped, coax coiled without kinks",
        "Site walked once with a light, looking for what you dropped",
    ]),
    ("Within 24 hours", [
        "Log uploaded to the program and to LoTW",
        "Anything that failed written into the Modification and Repair log",
        "Anything that needs replacing added to the go-kit list",
        "Battery on charge",
    ]),
]

SEC_CHECK = dict(
    tag="CHECK",
    title="Pre-Deployment and Teardown Checklists",
    blocks=[
        ("lead",
         "Read aloud and confirmed item by item. A checklist that is skimmed "
         "records only what the operator already assumes."),
        ("h3", "Pre-deployment"),
        ("checklist", CHECK_PRE),
        ("h3", "Teardown and follow-up"),
        ("checklist", CHECK_POST),
    ])

SECTIONS_B = [SEC_TIME, SEC_GRID, SEC_PROP, SEC_ANT, SEC_POWER, SEC_SAFETY,
              SEC_SECTIONS, SEC_PREFIX, SEC_CHECK]

ARRL_SECTIONS = [
    ("Call Area 0", [("CO", "Colorado"), ("IA", "Iowa"), ("KS", "Kansas"), ("MN", "Minnesota"),
                     ("MO", "Missouri"), ("ND", "North Dakota"), ("NE", "Nebraska"), ("SD", "South Dakota")]),
    ("Call Area 1", [("CT", "Connecticut"), ("EMA", "Eastern Massachusetts"), ("ME", "Maine"),
                     ("NH", "New Hampshire"), ("RI", "Rhode Island"), ("VT", "Vermont"),
                     ("WMA", "Western Massachusetts")]),
    ("Call Area 2", [("ENY", "Eastern New York"), ("NLI", "New York City-Long Island"),
                     ("NNJ", "Northern New Jersey"), ("NNY", "Northern New York"),
                     ("SNJ", "Southern New Jersey"), ("WNY", "Western New York")]),
    ("Call Area 3", [("DE", "Delaware"), ("EPA", "Eastern Pennsylvania"), ("MDC", "Maryland-DC"),
                     ("WPA", "Western Pennsylvania")]),
    ("Call Area 4", [("AL", "Alabama"), ("GA", "Georgia"), ("KY", "Kentucky"), ("NC", "North Carolina"),
                     ("NFL", "Northern Florida"), ("PR", "Puerto Rico"), ("SC", "South Carolina"),
                     ("SFL", "Southern Florida"), ("TN", "Tennessee"), ("VA", "Virginia"),
                     ("VI", "US Virgin Islands"), ("WCF", "West Central Florida")]),
    ("Call Area 5", [("AR", "Arkansas"), ("LA", "Louisiana"), ("MS", "Mississippi"), ("NM", "New Mexico"),
                     ("NTX", "North Texas"), ("OK", "Oklahoma"), ("STX", "South Texas"), ("WTX", "West Texas")]),
    ("Call Area 6", [("EB", "East Bay"), ("LAX", "Los Angeles"), ("ORG", "Orange"), ("PAC", "Pacific"),
                     ("SB", "Santa Barbara"), ("SCV", "Santa Clara Valley"), ("SDG", "San Diego"),
                     ("SF", "San Francisco"), ("SJV", "San Joaquin Valley"), ("SV", "Sacramento Valley")]),
    ("Call Area 7", [("AK", "Alaska"), ("AZ", "Arizona"), ("EWA", "Eastern Washington"), ("ID", "Idaho"),
                     ("MT", "Montana"), ("NV", "Nevada"), ("OR", "Oregon"), ("UT", "Utah"),
                     ("WWA", "Western Washington"), ("WY", "Wyoming")]),
    ("Call Area 8", [("MI", "Michigan"), ("OH", "Ohio"), ("WV", "West Virginia")]),
    ("Call Area 9", [("IL", "Illinois"), ("IN", "Indiana"), ("WI", "Wisconsin")]),
    ("Canada (RAC)", [("AB", "Alberta"), ("BC", "British Columbia"), ("GH", "Ontario Golden Horseshoe"),
                      ("MB", "Manitoba"), ("NB", "New Brunswick"), ("NL", "Newfoundland and Labrador"),
                      ("NS", "Nova Scotia"), ("ONE", "Ontario East"), ("ONN", "Ontario North"),
                      ("ONS", "Ontario South"), ("PE", "Prince Edward Island"), ("QC", "Quebec"),
                      ("SK", "Saskatchewan"), ("TER", "Territories")]),
]
