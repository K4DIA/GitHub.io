# -*- coding: utf-8 -*-
"""FIELD RECORD - Part I reference sections, group A: rules and operating."""

# Table helper shape:
#   ("table", dict(head=[...], rows=[[...]], w=[relative widths],
#                  align=['l','c','r',...], size=7.2, mono=[col indices]))

BANDPLAN_NOTE = (
    "Sub-band edges below are US allocations under 47 CFR 97.301 and 97.305, "
    "current as of 2026. E = Amateur Extra, A = Advanced, G = General, "
    "T = Technician, N = Novice. Unless a lower limit is shown, the maximum is "
    "1500 W PEP output, and the standing rule always applies: use the minimum "
    "power necessary."
)

BAND_ROWS_LF_MF = [
    ["2200 m", "135.7 - 137.8 kHz", "CW, data", "T&nbsp;A&nbsp;G&nbsp;E", "1 W EIRP. Advance notice to UTC required."],
    ["630 m", "472 - 479 kHz", "CW, data", "T&nbsp;A&nbsp;G&nbsp;E", "5 W EIRP. Advance notice to UTC required."],
    ["160 m", "1.800 - 2.000 MHz", "CW, phone, image, data", "G&nbsp;A&nbsp;E", "No sub-band split. Regional band plan applies."],
]

BAND_ROWS_80 = [
    ["80 m", "3.500 - 3.525", "CW, data", "E", ""],
    ["", "3.525 - 3.600", "CW, data", "T&nbsp;N&nbsp;A&nbsp;G&nbsp;E", "T and N: CW only, 200 W PEP."],
    ["", "3.600 - 3.700", "CW, phone, image, data", "E", ""],
    ["75 m", "3.700 - 3.800", "CW, phone, image", "A&nbsp;E", ""],
    ["", "3.800 - 4.000", "CW, phone, image", "G&nbsp;A&nbsp;E", ""],
]

BAND_ROWS_60 = [
    ["60 m", "5351.5 - 5366.5 kHz", "Any mode, 2.8 kHz max BW", "G&nbsp;A&nbsp;E", "9.15 W ERP max. Secondary."],
    ["", "5332.0 kHz ctr (5330.5 USB)", "USB, CW, data", "G&nbsp;A&nbsp;E", "100 W ERP. Channel."],
    ["", "5348.0 kHz ctr (5346.5 USB)", "USB, CW, data", "G&nbsp;A&nbsp;E", "100 W ERP. Channel."],
    ["", "5373.0 kHz ctr (5371.5 USB)", "USB, CW, data", "G&nbsp;A&nbsp;E", "100 W ERP. Channel."],
    ["", "5405.0 kHz ctr (5403.5 USB)", "USB, CW, data", "G&nbsp;A&nbsp;E", "100 W ERP. Channel."],
]

BAND_ROWS_40_30 = [
    ["40 m", "7.000 - 7.025", "CW, data", "E", ""],
    ["", "7.025 - 7.125", "CW, data", "T&nbsp;N&nbsp;A&nbsp;G&nbsp;E", "T and N: CW only, 200 W PEP."],
    ["", "7.125 - 7.175", "CW, phone, image", "A&nbsp;E", ""],
    ["", "7.175 - 7.300", "CW, phone, image", "G&nbsp;A&nbsp;E", ""],
    ["30 m", "10.100 - 10.150", "CW, data only", "G&nbsp;A&nbsp;E", "200 W PEP max. No phone, no image."],
]

BAND_ROWS_20_17 = [
    ["20 m", "14.000 - 14.025", "CW", "E", ""],
    ["", "14.025 - 14.150", "CW, data", "G&nbsp;A&nbsp;E", ""],
    ["", "14.150 - 14.175", "Phone, image", "E", ""],
    ["", "14.175 - 14.225", "Phone, image", "A&nbsp;E", ""],
    ["", "14.225 - 14.350", "Phone, image", "G&nbsp;A&nbsp;E", ""],
    ["17 m", "18.068 - 18.110", "CW, data", "G&nbsp;A&nbsp;E", ""],
    ["", "18.110 - 18.168", "CW, phone, image", "G&nbsp;A&nbsp;E", ""],
]

BAND_ROWS_15_12_10 = [
    ["15 m", "21.000 - 21.025", "CW", "E", ""],
    ["", "21.025 - 21.200", "CW, data", "T&nbsp;N&nbsp;A&nbsp;G&nbsp;E", "T and N: CW only, 200 W PEP."],
    ["", "21.200 - 21.225", "Phone, image", "E", ""],
    ["", "21.225 - 21.275", "Phone, image", "A&nbsp;E", ""],
    ["", "21.275 - 21.450", "Phone, image", "G&nbsp;A&nbsp;E", ""],
    ["12 m", "24.890 - 24.930", "CW, data", "G&nbsp;A&nbsp;E", ""],
    ["", "24.930 - 24.990", "CW, phone, image", "G&nbsp;A&nbsp;E", ""],
    ["10 m", "28.000 - 28.300", "CW, data", "T&nbsp;N&nbsp;A&nbsp;G&nbsp;E", "T and N: 200 W PEP."],
    ["", "28.300 - 28.500", "CW, phone", "T&nbsp;N&nbsp;A&nbsp;G&nbsp;E", "T and N: 200 W PEP."],
    ["", "28.500 - 29.700", "CW, phone, image", "G&nbsp;A&nbsp;E", "29.5 - 29.7 FM repeaters and simplex."],
]

BAND_ROWS_VHF = [
    ["6 m", "50.0 - 50.1 MHz", "CW only", "T&nbsp;A&nbsp;G&nbsp;E", "50.090 CW calling. 50.125 SSB calling."],
    ["", "50.1 - 54.0 MHz", "All authorized modes", "T&nbsp;A&nbsp;G&nbsp;E", ""],
    ["2 m", "144.0 - 144.1 MHz", "CW only", "T&nbsp;A&nbsp;G&nbsp;E", "144.200 SSB calling. 146.520 FM national simplex."],
    ["", "144.1 - 148.0 MHz", "All authorized modes", "T&nbsp;A&nbsp;G&nbsp;E", ""],
    ["1.25 m", "219 - 220 MHz", "Fixed digital point to point", "T&nbsp;A&nbsp;G&nbsp;E", "Notification required. Not for general use."],
    ["", "222 - 225 MHz", "All authorized modes", "T&nbsp;N&nbsp;A&nbsp;G&nbsp;E", "N: 222.0 - 225.0, 25 W PEP. 223.500 FM calling."],
    ["70 cm", "420 - 450 MHz", "All authorized modes", "T&nbsp;A&nbsp;G&nbsp;E", "446.000 FM national simplex. Regional coordination applies."],
    ["33 cm", "902 - 928 MHz", "All authorized modes", "T&nbsp;A&nbsp;G&nbsp;E", "Secondary. Shared with Part 15 and ISM."],
    ["23 cm", "1240 - 1300 MHz", "All authorized modes", "T&nbsp;A&nbsp;G&nbsp;E", "Secondary. Coordinate. Segment under study."],
]

TECH_HF_ROWS = [
    ["80 m", "3.525 - 3.600 MHz", "CW only", "200 W PEP"],
    ["40 m", "7.025 - 7.125 MHz", "CW only", "200 W PEP"],
    ["15 m", "21.025 - 21.200 MHz", "CW only", "200 W PEP"],
    ["10 m", "28.000 - 28.300 MHz", "CW and data", "200 W PEP"],
    ["10 m", "28.300 - 28.500 MHz", "CW and SSB phone", "200 W PEP"],
]

MODE_BW_ROWS = [
    ["CW", "~100 - 500 Hz", "Narrowest practical mode, and the most efficient use of a limited supply."],
    ["SSB phone", "~2.4 - 2.8 kHz", "HF emission bandwidth capped at 2.8 kHz below 28 MHz."],
    ["AM", "~6 kHz", "Permitted where phone is permitted. The carrier consumes most of the output."],
    ["FM phone", "~16 kHz", "29.5 MHz and above. Not permitted in the HF phone sub-bands below 29.0 MHz."],
    ["RTTY and data", "2.8 kHz max on HF", "Symbol rate limits were removed in 2024 and replaced by this bandwidth cap."],
    ["Image, SSTV", "~3 kHz", "Occupies a phone allocation. Announce before transmitting."],
]

CALLING_ROWS = [
    ["QRP CW", "1.810", "3.560", "7.030", "10.106", "14.060", "18.096", "21.060", "24.906", "28.060"],
    ["QRP SSB", "-", "3.985", "7.285", "-", "14.285", "18.130", "21.385", "24.950", "28.385"],
    ["POTA CW", "-", "3.550", "7.032", "10.110", "14.032", "18.082", "21.032", "24.892", "28.032"],
    ["POTA SSB", "-", "3.885", "7.185", "-", "14.285", "18.155", "21.285", "24.955", "28.420"],
    ["SOTA CW", "-", "3.557", "7.032", "10.110", "14.062", "18.092", "21.062", "24.902", "28.062"],
    ["SOTA SSB", "-", "3.985", "7.185", "-", "14.285", "18.155", "21.285", "24.955", "28.420"],
]

NET_ROWS = [
    ["2 m FM national simplex", "146.520 MHz", "Calling and travel. Move off after contact."],
    ["70 cm FM national simplex", "446.000 MHz", "Calling. Same courtesy applies."],
    ["6 m SSB calling", "50.125 MHz", "Openings are short. Check it often in June."],
    ["2 m SSB calling", "144.200 MHz", "Horizontal polarization. Point the beam."],
    ["Maritime Mobile Service Net", "14.300 MHz", "Also a recognized informal emergency watch frequency."],
    ["Hurricane Watch Net", "14.325 / 7.268 MHz", "Activates only when a storm warrants it. Listen first."],
    ["SATERN", "14.265 MHz", "Salvation Army emergency net."],
    ["Winlink and digital gateways", "Varies by RMS", "Check the current gateway list before you rely on one."],
]

SEC_BANDPLAN = dict(
    tag="BANDS",
    title="US Band Plan and Privileges",
    blocks=[
        ("lead",
         "Sub-band edges are not marked on the dial. In the field, with cold "
         "hands and a knob that is easy to bump, they have to be known."),
        ("p", BANDPLAN_NOTE),
        ("h3", "Low frequency and 160 meters"),
        ("table", dict(head=["Band", "Frequency", "Modes", "Class", "Notes"],
                       rows=BAND_ROWS_LF_MF,
                       w=[0.085, 0.215, 0.215, 0.135, 0.35],
                       align=['l', 'l', 'l', 'c', 'l'], mono=[1])),
        ("h3", "80 and 75 meters"),
        ("table", dict(head=["Band", "Frequency (MHz)", "Modes", "Class", "Notes"],
                       rows=BAND_ROWS_80,
                       w=[0.085, 0.215, 0.215, 0.135, 0.35],
                       align=['l', 'l', 'l', 'c', 'l'], mono=[1])),
        ("h3", "60 meters, as revised 13 February 2026"),
        ("p",
         "The 60 meter band changed shape in 2026. A contiguous 15 kHz subband "
         "replaced channelized operation in the middle of the old channel group, "
         "and the former 5358.5 kHz channel disappeared because it now falls "
         "inside that subband and would otherwise carry two different power "
         "limits. Four legacy channels survive on either side. Everything on "
         "60 meters is secondary: you accept interference from the primary "
         "government users and you must not cause any."),
        ("table", dict(head=["Band", "Frequency", "Modes", "Class", "Notes"],
                       rows=BAND_ROWS_60,
                       w=[0.085, 0.26, 0.20, 0.125, 0.33],
                       align=['l', 'l', 'l', 'c', 'l'], mono=[1])),
        ("note",
         "ERP on 60 meters is referenced to a half-wave dipole, not to an "
         "isotropic radiator and not to your transmitter output. If your antenna "
         "has gain relative to a dipole, you must reduce transmitter power to "
         "stay inside the limit. A compromised portable wire usually has loss, "
         "not gain, but you are responsible for knowing which."),
        ("h3", "40 and 30 meters"),
        ("table", dict(head=["Band", "Frequency (MHz)", "Modes", "Class", "Notes"],
                       rows=BAND_ROWS_40_30,
                       w=[0.085, 0.215, 0.215, 0.135, 0.35],
                       align=['l', 'l', 'l', 'c', 'l'], mono=[1])),
        ("h3", "20 and 17 meters"),
        ("table", dict(head=["Band", "Frequency (MHz)", "Modes", "Class", "Notes"],
                       rows=BAND_ROWS_20_17,
                       w=[0.085, 0.215, 0.215, 0.135, 0.35],
                       align=['l', 'l', 'l', 'c', 'l'], mono=[1])),
        ("h3", "15, 12, and 10 meters"),
        ("table", dict(head=["Band", "Frequency (MHz)", "Modes", "Class", "Notes"],
                       rows=BAND_ROWS_15_12_10,
                       w=[0.085, 0.215, 0.215, 0.135, 0.35],
                       align=['l', 'l', 'l', 'c', 'l'], mono=[1])),
        ("h3", "VHF and above"),
        ("table", dict(head=["Band", "Frequency", "Modes", "Class", "Notes"],
                       rows=BAND_ROWS_VHF,
                       w=[0.085, 0.215, 0.215, 0.135, 0.35],
                       align=['l', 'l', 'l', 'c', 'l'], mono=[1])),
        ("h3", "Technician HF privileges at a glance"),
        ("p",
         "A Technician licensee has full privileges on every amateur band above "
         "50 MHz and five slices of HF. Those slices are enough to do serious "
         "portable work, particularly on 10 meters near a solar peak and on 40 "
         "meter CW after dark."),
        ("table", dict(head=["Band", "Segment", "Modes permitted", "Power"],
                       rows=TECH_HF_ROWS,
                       w=[0.12, 0.30, 0.36, 0.22],
                       align=['l', 'l', 'l', 'l'], mono=[1])),
        ("h3", "Emission bandwidth and mode selection"),
        ("table", dict(head=["Mode", "Typical bandwidth", "Field notes"],
                       rows=MODE_BW_ROWS,
                       w=[0.16, 0.20, 0.64],
                       align=['l', 'l', 'l'])),
    ])

SEC_FREQS = dict(
    tag="FREQS",
    title="Calling Frequencies and Watering Holes",
    blocks=[
        ("lead",
         "None of these frequencies are reserved in regulation. They are "
         "conventions, and they work because operators expect to find each "
         "other on them."),
        ("h3", "Activity frequencies by band, MHz"),
        ("table", dict(head=["Activity", "160", "80/75", "40", "30", "20", "17", "15", "12", "10"],
                       rows=CALLING_ROWS,
                       w=[0.16] + [0.0933] * 9,
                       align=['l'] + ['c'] * 9, size=7.0, mono=list(range(1, 10)))),
        ("note",
         "Listen long enough to establish that the frequency is clear. A weak "
         "station below your noise floor is still occupying it. Then ask: "
         "\"Is this frequency in use?\" on phone, or QRL? on CW, twice, before "
         "the first call."),
        ("h3", "Calling channels and standing nets"),
        ("table", dict(head=["Purpose", "Frequency", "Notes"],
                       rows=NET_ROWS,
                       w=[0.30, 0.20, 0.50],
                       align=['l', 'l', 'l'], mono=[1])),
        ("h3", "Selecting a run frequency"),
        ("bul", [
            "Work above the calling frequency rather than on it. Calling "
            "frequencies are for establishing contact, not for running.",
            "On CW, choose a clear 200 Hz rather than a familiar part of the "
            "band.",
            "Announce QRP operation in the exchange. It sets the receiving "
            "operator's expectations.",
            "Self-spot where the program supports it, then hold the announced "
            "frequency. Drifting off it costs contacts.",
        ]),
    ])

Q_ROWS = [
    ["QRA", "What is your station name?", "Uncommon on the air, common in print."],
    ["QRG", "What is my exact frequency?", "Useful when you suspect drift."],
    ["QRL", "Is this frequency in use?", "Send it twice before you claim a slot."],
    ["QRM", "Interference from other stations", "Man made. Someone else is on top of you."],
    ["QRN", "Atmospheric noise, static", "Natural. Storms, power lines, a bad site."],
    ["QRO", "Increase power", "Costs amp-hours. Consider band or antenna first."],
    ["QRP", "Reduce power / low power operation", "5 W or less output on CW and data, 10 W PEP on SSB."],
    ["QRQ", "Send faster", "Sent by the receiving station, not the sender."],
    ["QRS", "Send slower", "Always honored by an operator worth working."],
    ["QRT", "Stop sending / closing station", "The polite way to leave."],
    ["QRU", "Do you have anything for me?", "Traffic handling."],
    ["QRV", "I am ready", "Also: are you ready?"],
    ["QRX", "Stand by, wait", "Give a time if you can. QRX 5 means five minutes."],
    ["QRZ", "Who is calling me?", "Not a general call for contacts, though it is used that way."],
    ["QSA", "Signal strength, scale 1 to 5", "Older than the RST system."],
    ["QSB", "Fading", "The condition that most often explains a lost contact."],
    ["QSK", "Full break-in, I can hear between elements", "Ask before you assume the other station has it."],
    ["QSL", "Acknowledge receipt, or a confirmation card", "Both senses are in daily use."],
    ["QSO", "A contact", "Used as both noun and verb."],
    ["QSP", "Relay to another station", "Traffic handling."],
    ["QSY", "Change frequency", "Give the new frequency. QSY 7.185."],
    ["QTC", "I have a message to send", "Traffic handling."],
    ["QTH", "Location", "Give something a hunter can log: state, park, grid."],
    ["QTR", "Correct time", "UTC unless you say otherwise."],
]

PROSIGN_ROWS = [
    ["AR", ".-.-.", "End of transmission or message"],
    ["AS", ".-...", "Wait, stand by briefly"],
    ["BK", "-... -.-", "Break, invite the other station in"],
    ["BT", "-...-", "Separator between paragraphs, written as a dash"],
    ["CL", "-.-. .-..", "Closing station, going off the air"],
    ["KN", "-.--.", "Go ahead, named station only"],
    ["K", "-.-", "Go ahead, anyone"],
    ["SK", "...-.-", "End of contact"],
    ["SN", "...-.", "Understood"],
    ["HH", "........", "Error, disregard and start the word again"],
]

CWABBR_ROWS = [
    ["5NN", "599, sent fast", "GM/GA/GE", "Good morning / afternoon / evening"],
    ["ABT", "About", "HR", "Here"],
    ["AGN", "Again", "HW?", "How do you copy?"],
    ["ANT", "Antenna", "NR", "Number, or near"],
    ["BK", "Break", "OM / YL", "Old man / young lady"],
    ["CQ", "Calling any station", "OP", "Operator's name"],
    ["CUL", "See you later", "PSE", "Please"],
    ["DE", "From, this is", "PWR", "Power"],
    ["DX", "Distance, foreign station", "R", "Roger, received"],
    ["ES", "And", "RIG", "Station equipment"],
    ["FB", "Fine business, excellent", "RST", "Signal report"],
    ["GD", "Good", "TU", "Thank you"],
    ["GL", "Good luck", "UR", "Your, you are"],
    ["GND", "Ground", "WX", "Weather"],
    ["73", "Best regards", "88", "Love and kisses"],
]

SEC_OPERATING = dict(
    tag="OPS",
    title="Signal Reports, Q Signals, and Prosigns",
    blocks=[
        ("lead",
         "The shared vocabulary of an on-air contact: signal reports, the Q "
         "signals in common use, and the prosigns sent as single characters "
         "on CW."),
        ("h3", "The RST system"),
        ("p",
         "Three digits: readability, strength, tone. Tone is sent only on CW and "
         "data. A phone report is two digits. The scale is old, imprecise, and "
         "universally understood, which is exactly what a signal report needs to be."),
        ("table", dict(head=["R, readability", "S, strength", "T, tone (CW only)"],
                       rows=[
                           ["1  Unreadable", "1  Faint, barely perceptible", "1  Extremely rough hissing note"],
                           ["2  Barely readable, occasional words", "2  Very weak", "2  Very rough AC note"],
                           ["3  Readable with difficulty", "3  Weak", "3  Rough low pitched AC note"],
                           ["4  Readable with practically no difficulty", "4  Fair", "4  Rather rough AC note"],
                           ["5  Perfectly readable", "5  Fairly good", "5  Musical, modulated note"],
                           ["", "6  Good", "6  Modulated note, slight trace of whistle"],
                           ["", "7  Moderately strong", "7  Near DC note, smooth ripple"],
                           ["", "8  Strong", "8  Good DC note, trace of ripple"],
                           ["", "9  Extremely strong", "9  Purest DC note"],
                       ],
                       w=[0.36, 0.32, 0.32], align=['l', 'l', 'l'], size=7.4)),
        ("note",
         "S9 on HF is defined as 50 microvolts at a 50 ohm receiver input, with "
         "one S unit nominally 6 dB. Few receivers calibrate to it. Above S9 "
         "the scale reads in decibels above that reference. Report what the "
         "meter shows and note any known optimism of the receiver in the "
         "Debrief."),
        ("h3", "Q signals in daily use"),
        ("table", dict(head=["Signal", "Meaning", "Field notes"],
                       rows=Q_ROWS, w=[0.10, 0.36, 0.54],
                       align=['l', 'l', 'l'], size=7.4, mono=[0])),
        ("h3", "Prosigns"),
        ("p",
         "Sent as a single character with no inter-letter space. The overbar in "
         "print marks the run-together pair."),
        ("table", dict(head=["Prosign", "Code", "Meaning"],
                       rows=PROSIGN_ROWS, w=[0.14, 0.24, 0.62],
                       align=['l', 'l', 'l'], mono=[0, 1])),
        ("h3", "CW abbreviations in common use"),
        ("table", dict(head=["Abbr", "Meaning", "Abbr", "Meaning"],
                       rows=CWABBR_ROWS, w=[0.11, 0.34, 0.13, 0.42],
                       align=['l', 'l', 'l', 'l'], size=7.4, mono=[0, 2])),
    ])

PHON_ROWS = [
    ["A", "Alfa", "AL fah", "N", "November", "no VEM ber"],
    ["B", "Bravo", "BRAH voh", "O", "Oscar", "OSS cah"],
    ["C", "Charlie", "CHAR lee", "P", "Papa", "pah PAH"],
    ["D", "Delta", "DELL tah", "Q", "Quebec", "keh BECK"],
    ["E", "Echo", "ECK oh", "R", "Romeo", "ROW me oh"],
    ["F", "Foxtrot", "FOKS trot", "S", "Sierra", "see AIR rah"],
    ["G", "Golf", "GOLF", "T", "Tango", "TANG go"],
    ["H", "Hotel", "hoh TELL", "U", "Uniform", "YOU nee form"],
    ["I", "India", "IN dee ah", "V", "Victor", "VIK tah"],
    ["J", "Juliett", "JEW lee ETT", "W", "Whiskey", "WISS key"],
    ["K", "Kilo", "KEY loh", "X", "X-ray", "ECKS ray"],
    ["L", "Lima", "LEE mah", "Y", "Yankee", "YANG key"],
    ["M", "Mike", "MIKE", "Z", "Zulu", "ZOO loo"],
]

NUM_ROWS = [
    ["0", "Zero", "ZEE roh", "5", "Five", "FIFE"],
    ["1", "One", "WUN", "6", "Six", "SIX"],
    ["2", "Two", "TOO", "7", "Seven", "SEV en"],
    ["3", "Three", "TREE", "8", "Eight", "AIT"],
    ["4", "Four", "FOW er", "9", "Nine", "NIN er"],
]

SEC_PHONETICS = dict(
    tag="PHON",
    title="Phonetics and Working the Exchange",
    blocks=[
        ("lead",
         "Standard phonetics exist so that a marginal signal resolves into the "
         "correct callsign. Non-standard substitutions are workable on a strong "
         "signal and unhelpful on a weak one."),
        ("h3", "ITU and NATO phonetic alphabet"),
        ("table", dict(head=["", "Word", "Spoken", "", "Word", "Spoken"],
                       rows=PHON_ROWS, w=[0.06, 0.17, 0.27, 0.06, 0.17, 0.27],
                       align=['c', 'l', 'l', 'c', 'l', 'l'], size=7.6, mono=[0, 3])),
        ("h3", "Numbers"),
        ("table", dict(head=["", "Word", "Spoken", "", "Word", "Spoken"],
                       rows=NUM_ROWS, w=[0.06, 0.17, 0.27, 0.06, 0.17, 0.27],
                       align=['c', 'l', 'l', 'c', 'l', 'l'], size=7.6, mono=[0, 3])),
        ("h3", "A minimum field exchange, phone"),
        ("p",
         "Everything a hunter needs, nothing they do not. Repeat your own "
         "callsign at the end of every transmission when you are running."),
        ("script", [
            ("You", "CQ Parks on the Air, CQ POTA, this is W1ABC, Whiskey One Alfa Bravo Charlie, "
                    "Kilo dash one two three four, over."),
            ("Them", "W1ABC, this is K9XYZ, Kilo Nine X-ray Yankee Zulu, you are five nine."),
            ("You", "K9XYZ, thanks, you are five seven in Delaware Water Gap. QSL and 73, W1ABC, QRZ."),
        ]),
        ("h3", "A minimum field exchange, CW"),
        ("script", [
            ("You", "CQ POTA CQ POTA DE W1ABC W1ABC K"),
            ("Them", "W1ABC DE K9XYZ 599 599 BK"),
            ("You", "K9XYZ TU 579 579 W1ABC K"),
            ("Them", "TU 73 EE"),
        ]),
        ("h3", "Running a pileup"),
        ("bul", [
            "Identify on every transmission. A station tuning in mid-run "
            "cannot log an unidentified signal.",
            "Work partial calls: naming the fragment heard resolves a pileup "
            "faster than repeated general calls.",
            "Read the callsign back while writing it, rather than pausing.",
            "Announce band changes before making them, so the pileup follows "
            "rather than disperses.",
            "Log times in UTC as contacts are made. Reconstructed timestamps "
            "are a common cause of rejected submissions.",
        ]),
    ])

AWARD_ROWS = [
    ["Parks on the Air (POTA)",
     "10 QSOs from inside the park, in one UTC day",
     "All equipment and operator inside park boundaries, on public land. Within "
     "30.5 m of the feature for trail and river references. Activator uploads an "
     "ADIF log. Hunters submit nothing."],
    ["Summits on the Air (SOTA)",
     "4 QSOs from inside the activation zone for summit points",
     "Activation zone is within 25 vertical meters of the summit. Station must be "
     "wholly independent of any motor vehicle for both power and antenna support. "
     "Human powered access. Winter bonus points apply in some associations."],
    ["World Wide Flora and Fauna (WWFF)",
     "44 QSOs from inside the reference area",
     "Higher bar than POTA. Many sites hold both a POTA and a WWFF reference, so "
     "one log can serve both if you keep working past ten."],
    ["Worked All States (WAS)",
     "Confirmed contact with all 50 states",
     "Confirmations via LoTW, physical QSL, or an accepted equivalent. Endorsements "
     "exist per band and per mode. A portable station chasing WAS should track by "
     "band from the start."],
    ["DXCC",
     "100 confirmed entities",
     "Entities are not countries. Check the current DXCC list rather than a map. "
     "QRP and portable endorsements exist."],
    ["Worked All Continents (WAC)",
     "6 continents confirmed",
     "The most achievable serious HF award from a wire in a park. Africa is "
     "usually the last one."],
]

SEC_AWARDS = dict(
    tag="AWARDS",
    title="Activation and Award Requirements",
    blocks=[
        ("lead",
         "Minimum requirements for the programs a portable station is most "
         "likely to be working. The figures below are the ones that determine "
         "whether an outing counts."),
        ("table", dict(head=["Program", "Minimum for credit", "The rules that actually catch people"],
                       rows=AWARD_ROWS, w=[0.21, 0.24, 0.55],
                       align=['l', 'l', 'l'], size=7.4)),
        ("note",
         "Contact counts are assessed against a single UTC day, not against a "
         "single outing. An activation beginning at 7 p.m. Eastern in summer "
         "has already crossed the boundary: eight contacts before 0000Z and "
         "eight after produce two incomplete activations rather than one "
         "complete one. See Time and the Zulu Day."),
        ("h3", "Confirm before leaving the site"),
        ("bul", [
            "Contact count meets the program minimum, counted within a single "
            "UTC day, not within your afternoon.",
            "Every logged time is UTC, and your radio or phone clock was actually "
            "correct when you wrote them.",
            "Park or summit reference number is written down exactly, including "
            "the prefix. K-1234 and US-1234 are not interchangeable.",
            "Your own callsign as used on the air matches what you will submit. "
            "Portable indicators matter to some programs and not to others.",
            "Any park-to-park or summit-to-summit contacts are flagged in the "
            "Notes column so you can find them again.",
        ]),
    ])

SECTIONS_A = [SEC_BANDPLAN, SEC_FREQS, SEC_OPERATING, SEC_PHONETICS, SEC_AWARDS]
