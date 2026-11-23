#!/usr/bin/env python3
"""The Sunday Ledger v2 — make.fun news-image-20261122 (R2 revision).
Draws a 1024x1024 poster summing the world's news of Sunday 22 November 2026.
Content swap on R1's geometry: the lead is corrected (COP31 COLLAPSED, no deal),
Bahrain / Dymer / Seoul join as panels, regions rebalanced to a cap of 8.
Deterministic: fixed compile time, fixed seed, no network, no clock reads.
Run: python3 draw.py  -> writes entry.png in this directory.
"""
import hashlib
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
COMPILE_TIME = "23:30"          # UTC, fixed for determinism (end of Sunday)
COMPILE_HOUR = 23.5             # 23:30 as hours, for the UTC clock marker

FD = "/usr/share/fonts/truetype/dejavu/"
FN = "/usr/share/fonts/truetype/noto/"

def F(path, size):
    return ImageFont.truetype(path, size)

SERIF_B = lambda s: F(FD + "DejaVuSerif-Bold.ttf", s)
SERIF   = lambda s: F(FD + "DejaVuSerif.ttf", s)
SERIF_I = lambda s: F(FN + "NotoSerif-Italic.ttf", s)
SANS    = lambda s: F(FN + "NotoSans-Regular.ttf", s)
SANS_B  = lambda s: F(FN + "NotoSans-Bold.ttf", s)
SANS_DB = lambda s: F(FD + "DejaVuSans-Bold.ttf", s)

# ---------- palette ----------
INK      = (18, 18, 22)
PAPER    = (250, 248, 242)
NAVY     = (16, 32, 64)
NAVY2    = (28, 52, 96)
RULE     = (180, 175, 165)
LIGHT    = (238, 235, 227)
WHITE    = (255, 255, 255)
CHIP_SUN = (16, 120, 70)    # green = Sunday
CHIP_SAT = (176, 96, 0)     # amber = Saturday, still developing
CHIP_FRI = (150, 60, 60)    # rust = Friday, still carried
VERIFY   = (60, 60, 66)
SEA      = (205, 224, 238)
LAND     = (232, 228, 210)
LANDLINE = (170, 162, 140)

CAT_COLORS = {
    "CLIMATE": (16, 120, 70), "AMERICAS": (150, 60, 40), "SPORT": (20, 90, 160),
    "EUROPE": (90, 60, 140), "SCIENCE": (0, 120, 130), "TECH": (60, 60, 70),
    "ASIA": (190, 120, 0), "WAR": (140, 30, 30), "AFRICA": (170, 90, 20),
    "TRADE": (30, 110, 90), "HEALTH": (180, 40, 90),
}

# ---------- the 40 stories ----------
# Panels 1-13: (num, chip, category, verify, place, headline, body, source, lon, lat, art)
# chip: SUN / SAT>SUN / FRI>SUN
PANELS = [
    (1, "SUN", "CLIMATE", "CONFIRMED", "ANTALYA, TURKEY",
     "COP31 collapses with no deal in Antalya",
     "The EU and Britain rejected a text with no mention of fossil fuels. President Kurum conceded there was no consensus; the longest COP ever ends in failure.",
     "Reuters", 30.7, 36.9, "cop31"),
    (2, "FRI>SUN", "AMERICAS", "CONFIRMED", "GUASAVE, MEXICO",
     "Mexico captures FBI's most-wanted cartel boss",
     "Fausto Isidro Meza Flores, 44, was seized Friday night. Eleven died; he was flown to Mexico City Saturday as troops clear roadblocks.",
     "Reuters", -108.5, 25.6, "cartel"),
    (3, "SUN", "SPORT", "OFFICIAL", "LAS VEGAS, USA",
     "Verstappen wins Las Vegas GP thriller",
     "He held off Norris by 0.639s after 35 lead changes \u2014 his 75th career win and third in Las Vegas. Piastri was third.",
     "formula1.com", -115.1, 36.2, "f1"),
    (4, "SUN", "SPORT", "CONFIRMED", "WELLINGTON, NEW ZEALAND",
     "India declare on 720/9, a record in New Zealand",
     "Pant's 128 and Rahul's 136 built a lead of 352. New Zealand were 119/2 at stumps, trailing by 233.",
     "AFP", 174.8, -41.3, "cricket"),
    (5, "SAT>SUN", "EUROPE", "CONFIRMED", "GULF OF FINLAND",
     "Russian ship towed from Finnish waters",
     "Two drones hit the Sparta II; 16 crew rescued. Flames out; a Russian tug towed it away.",
     "Reuters", 26.5, 59.9, "ship"),
    (6, "SAT>SUN", "SCIENCE", "OFFICIAL", "MERCURY ORBIT",
     "BepiColombo reaches Mercury after 8 years",
     "The ESA\u2013JAXA mission entered Mercury orbit on Saturday, only the second craft ever to do so.",
     "ESA", 8.65, 49.87, "mercury"),
    (7, "FRI>SUN", "TECH", "REPORTED", "WASHINGTON, USA",
     "Hackers breached the FBI's crime database",
     "The NCIC \u2014 warrants, fugitives, missing persons \u2014 was breached, CNN reported Friday.",
     "CNN", -77.0, 38.9, "fbi"),
    (8, "SAT>SUN", "WAR", "CONFIRMED", "MANAMA, BAHRAIN",
     "Iran hits US bases in Bahrain; 2 hurt",
     "Missiles and drones struck Al-Riffa and Awali on Saturday; a factory burned on Sitra Island.",
     "Reuters", 50.6, 26.2, "bahrain"),
    (9, "SUN", "WAR", "CONFIRMED", "DYMER, UKRAINE",
     "Russian drone flattens Kyiv flats; 15 missing",
     "A drone hit a five-storey block in Dymer overnight; two dead and up to 15 feared under the rubble.",
     "AP", 30.3, 50.8, "dymer"),
    (10, "FRI>SUN", "AFRICA", "OFFICIAL", "JOHANNESBURG, S. AFRICA",
     "South Africa mourns its first woman deputy president",
     "Phumzile Mlambo-Ngcuka, 71, died Friday. Flags at half-mast from today; state funeral Saturday.",
     "Presidency", 28.0, -26.2, "mlambo"),
    (11, "SAT>SUN", "WAR", "CONFIRMED", "KYIV, UKRAINE",
     "Zelensky: bridge strikes a \u2018fair response\u2019",
     "He cited 109 Russian attacks on Ukrainian bridges. Kyiv and London will build drones in Britain.",
     "BBC", 30.5, 50.45, "drone"),
    (12, "SAT>SUN", "TRADE", "OFFICIAL", "BRUSSELS, BELGIUM",
     "EU and Indonesia sign trade deal after 10 years",
     "Duties vanish on over 90% of goods under the CEPA signed in Brussels. Live in early 2027.",
     "Reuters", 4.35, 50.85, "trade"),
    (13, "SUN", "ASIA", "OFFICIAL", "SEOUL, SOUTH KOREA",
     "Seoul minister quits over exam AI-cheating chaos",
     "Education chief Choi Kyo-jin resigned Sunday over last-minute anti-cheating changes to the exam.",
     "Reuters", 127.0, 37.5, "seoul"),
]

# Briefs 14-40: (num, chip, text, lon, lat)
BRIEFS = [
    (14, "FRI>SUN", "Poland: missiles land; NATO vows defence", 21.0, 53.6),
    (15, "SAT>SUN", "Gaza: food-aid vehicle strike kills 3", 34.5, 31.5),
    (16, "FRI>SUN", "Nigeria: funeral boat toll rises to 29", 6.3, 4.8),
    (17, "FRI>SUN", "Pentagon memo limits US\u2013Canada defence ties", -77.05, 38.9),
    (18, "FRI>SUN", "Trump orders contractors to report Congress", -77.03, 38.9),
    (19, "FRI>SUN", "Haiti: three Salvadoran troops die in blast", -72.3, 18.5),
    (20, "SUN", "Russian warship sunk at Libya port in drone strike", 20.1, 32.1),
    (21, "SAT>SUN", "Basra power-station fire kills 4, injures 35", 47.8, 30.5),
    (22, "SAT>SUN", "MAMA Awards: BTS take artist, album of year", 135.5, 34.7),
    (23, "SAT>SUN", "Delhi sets 15\u201320% pollution cut for 2027", 77.25, 28.6),
    (24, "SAT>SUN", "Indonesia factory fire kills 3; 36 missing", 106.3, -6.2),
    (25, "SAT>SUN", "Nigeria: 35 Fulani killed in reprisal attacks", 4.5, 9.9),
    (26, "SAT>SUN", "Estonia: NATO F-16s scrambled for drone alert", 27.3, 59.3),
    (27, "SUN", "Somalia: UAE envoy deadline expires", 45.3, 2.0),
    (28, "SUN", "Lebanon seizes 264kg of explosives from Syria", 36.4, 34.3),
    (29, "SAT>SUN", "Trump launches 17-nation anti-cartel coalition", -80.35, 25.81),
    (30, "FRI>SUN", "Malaria vaccine hits 87% efficacy in trial", -122.3, 47.6),
    (31, "SAT>SUN", "Saudis down three Houthi missiles over Riyadh", 46.7, 24.7),
    (32, "SAT>SUN", "Fukushima snow isolates about 1,400 people", 140.5, 37.8),
    (33, "SAT>SUN", "Banda Sea M6.8 quake felt in Darwin", 128.5, -6.5),
    (34, "SUN", "Nepal PM lands in Delhi for two-day visit", 77.2, 28.6),
    (35, "SUN", "Liverpool thrash 10-man United 4\u20130", -2.98, 53.4),
    (36, "SUN", "Rising Stars: Pakistan A beat India A by 48 runs", 51.5, 25.3),
    (37, "SUN", "Korean navy chief begins two-day Japan visit", 139.7, 35.3),
    (38, "SUN", "Israel coalition talks resume in Jerusalem", 35.2, 31.8),
    (39, "SUN", "Barcelona fight back to beat Villarreal 3\u20132", 2.17, 41.4),
    (40, "SUN", "Australia rebukes US report on AUKUS subs", 151.2, -33.9),
]

KPIS = [
    ("17", "YEARS SINCE A COP LAST COLLAPSED (COPENHAGEN 2009)"),
    ("35", "LEAD CHANGES IN THE LAS VEGAS GP"),
    ("352", "INDIA'S LEAD AFTER DECLARING 720/9"),
    ("11", "KILLED IN THE CARTEL BOSS CAPTURE"),
    ("16", "CREW RESCUED FROM THE SPARTA II"),
    ("15", "MISSING UNDER THE DYMER RUBBLE"),
]

REGIONS = [("EUROPE", 8, (90, 60, 140)), ("ASIA", 8, (190, 120, 0)),
           ("AMERICAS", 8, (150, 60, 40)), ("MIDDLE EAST", 6, (0, 120, 130)),
           ("AFRICA", 5, (170, 90, 20)), ("OCEANIA", 3, (20, 90, 160)),
           ("GLOBAL", 2, (60, 60, 70))]

STILL_DEV = [
    "Dymer: search goes on for 15 missing under the rubble",
    "Bahrain: Gulf states condemn Iran strikes; tensions high",
    "Indonesia: search resumes Monday for 36 factory workers",
    "IND v NZ, day 5 \u2014 NZ 119/2, need 233 to avoid innings defeat",
    "NATO Council meets Monday over the Poland incursion",
    "Sinaloa: troops still clearing roadblocks after capture",
    "Libya: joint probe into the Benghazi warship strike",
]

DATE_CHECK = ("Left out on purpose \u2014 not Sunday news: Peru M6.7 quake (Fri) \u00b7 Nitish Setu bridge "
    "(Sat) \u00b7 Cyclone Akvan (Fri) \u00b7 Trump\u2013Xi\u2013Putin summit (Fri\u2013Sat) \u00b7 "
    "ICJ Myanmar ruling (Fri) \u00b7 Anthropic IPO (Fri) \u00b7 US\u2013Iran Gulf strikes (17\u201318 Nov) \u00b7 Fiji/Tonga "
    "drought (18\u201319 Nov) \u00b7 Japan\u2013India 2+2 (19 Nov) \u00b7 Kryvyi Rih strike (Fri).")

STANDFIRST = ("COP31 collapses with no deal in Antalya \u00b7 Iran hits US bases in Bahrain \u00b7 "
    "a Russian drone flattens flats near Kyiv \u2014 and 37 more stories from every region.")


# ---------- text helpers ----------
def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_lines(draw, text, font, max_w, max_lines):
    """Wrap to at most max_lines; ellipsize the last line if it overflows."""
    lines = wrap(draw, text, font, max_w)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    last = out[-1]
    while last and draw.textlength(last + "\u2026", font=font) > max_w:
        last = last[:-1].rsplit(" ", 1)[0] if " " in last else last[:-1]
    out[-1] = (last + "\u2026") if last else "\u2026"
    return out

def chip_color(chip):
    return CHIP_SUN if chip == "SUN" else (CHIP_SAT if chip == "SAT>SUN" else CHIP_FRI)

def draw_chip(draw, x, y, text, color, font):
    w = int(draw.textlength(text, font=font)) + 8
    h = 12
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=color)
    draw.text((x + 4, y + 1), text, font=font, fill=WHITE)
    return w

def truncate_to_width(d, text, font, max_w):
    if d.textlength(text, font=font) <= max_w:
        return text
    t = text
    while t and d.textlength(t + "\u2026", font=font) > max_w:
        t = t[:-1]
    return t.rstrip() + "\u2026"

# ---------- illustrations (original flat art, drawn in Pillow) ----------
# Each function paints a w x h scene inside (x, y). Scenes are simple
# geometric compositions; every panel gets its own unique key.

def art_cop31(d, x, y, w, h):
    """Collapse scene: dark clouds over an empty hall, a fallen gavel."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 58, 78))
    # storm clouds, heavy and low
    for cx, cy, r in ((x + 18, y + 10, 14), (x + 44, y + 6, 17), (x + 74, y + 12, 13),
                      (x + w - 34, y + 8, 15), (x + w - 62, y + 5, 12)):
        d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=(28, 32, 48))
    # rain, thin diagonal strokes
    for i in range(9):
        rx = x + 8 + i * ((w - 16) // 8)
        d.line([rx, y + 22, rx - 3, y + 32], fill=(120, 140, 170), width=1)
    # the empty hall: long table, no delegates
    d.rectangle([x + 10, y + h - 22, x + w - 10, y + h - 10], fill=(96, 74, 52))
    d.rectangle([x + 14, y + h - 26, x + w - 14, y + h - 22], fill=(130, 102, 72))
    # empty chairs, pushed back
    for cx in (x + 22, x + w // 2 - 6, x + w - 34):
        d.rectangle([cx, y + h - 34, cx + 12, y + h - 26], fill=(60, 50, 44))
        d.rectangle([cx + 2, y + h - 26, cx + 10, y + h - 22], fill=(80, 68, 58))
    # fallen gavel on the table, handle askew
    gx, gy = x + w // 2 - 4, y + h - 25
    d.line([gx - 10, gy + 4, gx + 12, gy - 2], fill=(40, 28, 18), width=3)
    d.rectangle([gx + 8, gy - 5, gx + 16, gy + 1], fill=(70, 50, 30))
    # a single cold light over the table
    d.polygon([(x + w // 2 - 20, y + h - 26), (x + w // 2 + 20, y + h - 26),
               (x + w // 2 + 8, y + 18), (x + w // 2 - 8, y + 18)], fill=(150, 160, 190))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(30, 34, 48))

def art_cartel(d, x, y, w, h):
    """Desert road, mountains, helicopter, burning roadblock."""
    d.rectangle([x, y, x + w, y + h], fill=(235, 205, 150))
    d.polygon([(x, y + h), (x + 30, y + 18), (x + 60, y + h)], fill=(180, 130, 80))
    d.polygon([(x + 45, y + h), (x + 80, y + 26), (x + 115, y + h)], fill=(165, 115, 70))
    # road sweeping to the right
    d.polygon([(x + w - 60, y + h), (x + w - 20, y + 10), (x + w, y + 10), (x + w, y + h)], fill=(90, 85, 80))
    # helicopter overhead
    hx, hy = x + w // 2 - 10, y + 12
    d.ellipse([hx, hy, hx + 26, hy + 12], fill=(60, 70, 60))
    d.line([hx - 8, hy + 2, hx + 34, hy + 2], fill=(40, 45, 40), width=2)
    d.line([hx + 26, hy + 6, hx + 42, hy + 2], fill=(60, 70, 60), width=3)
    # flames at the roadblock
    bx, by = x + w - 34, y + h - 26
    d.polygon([(bx, by + 12), (bx + 6, by), (bx + 12, by + 12)], fill=(230, 120, 20))
    d.polygon([(bx + 8, by + 12), (bx + 14, by + 2), (bx + 20, by + 12)], fill=(255, 180, 40))
    # cactus and a second small flame
    cx0 = x + w // 2 + 18
    d.rectangle([cx0, y + h - 24, cx0 + 4, y + h - 8], fill=(60, 130, 70))
    d.rectangle([cx0 - 5, y + h - 20, cx0 - 1, y + h - 16], fill=(60, 130, 70))
    d.rectangle([cx0 + 5, y + h - 18, cx0 + 9, y + h - 14], fill=(60, 130, 70))
    d.polygon([(x + 14, y + h - 8), (x + 20, y + h - 20), (x + 26, y + h - 8)], fill=(255, 140, 20))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(140, 100, 60))

def art_f1(d, x, y, w, h):
    """Night race: stars, neon strips, a red open-wheeler."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 25, 55))
    for sx in range(8):
        px = x + 6 + (sx * 37) % (w - 12)
        py = y + 4 + (sx * 13) % 14
        d.ellipse([px, py, px + 2, py + 2], fill=(255, 255, 220))
    # neon strips along the track
    d.rectangle([x, y + h - 22, x + w, y + h - 18], fill=(255, 60, 120))
    d.rectangle([x, y + h - 14, x + w, y + h - 12], fill=(60, 220, 255))
    # the car
    cx, cy = x + w // 2 - 34, y + h - 40
    d.polygon([(cx, cy + 14), (cx + 8, cy + 2), (cx + 34, cy), (cx + 56, cy + 4), (cx + 68, cy + 14)], fill=(220, 30, 40))
    d.rectangle([cx + 26, cy - 4, cx + 40, cy + 4], fill=(30, 30, 40))
    d.ellipse([cx + 8, cy + 10, cx + 22, cy + 24], fill=(15, 15, 20))
    d.ellipse([cx + 46, cy + 10, cx + 60, cy + 24], fill=(15, 15, 20))
    d.ellipse([cx + 12, cy + 14, cx + 18, cy + 20], fill=(200, 200, 210))
    d.ellipse([cx + 50, cy + 14, cx + 56, cy + 20], fill=(200, 200, 210))
    d.line([cx - 12, cy + 8, cx + 2, cy + 8], fill=(255, 220, 80), width=2)

def art_cricket(d, x, y, w, h):
    """Green outfield, pitch, stumps, bat and ball."""
    d.rectangle([x, y, x + w, y + h], fill=(120, 185, 110))
    d.ellipse([x + 8, y + h - 24, x + w - 8, y + h - 2], fill=(90, 160, 85))
    # pitch
    d.rectangle([x + w // 2 - 16, y + 10, x + w // 2 + 16, y + h - 8], fill=(215, 190, 140))
    # stumps
    for i in range(3):
        sx = x + w // 2 - 9 + i * 9
        d.rectangle([sx, y + 14, sx + 3, y + 30], fill=(255, 240, 180))
    # bat and ball
    d.line([x + w // 2 + 24, y + h - 34, x + w // 2 + 34, y + h - 14], fill=(200, 160, 100), width=5)
    d.ellipse([x + w // 2 - 40, y + 22, x + w // 2 - 30, y + 32], fill=(200, 40, 40))
    d.line([x + w // 2 - 34, y + 18, x + w // 2 - 20, y + 30], fill=(255, 255, 255), width=1)

def art_ship(d, x, y, w, h):
    """A cargo ship at sea, smoke and flame from its deck."""
    d.rectangle([x, y, x + w, y + h], fill=(150, 195, 225))
    d.polygon([(x, y + 16), (x + 22, y + 6), (x + 44, y + 16)], fill=(120, 150, 120))
    # hull and superstructure
    d.polygon([(x + 8, y + h - 26), (x + w - 8, y + h - 26), (x + w - 20, y + h - 10), (x + 20, y + h - 10)], fill=(70, 70, 80))
    d.rectangle([x + w // 2 - 18, y + h - 40, x + w // 2 + 14, y + h - 26], fill=(200, 200, 205))
    d.rectangle([x + w // 2 - 18, y + h - 46, x + w // 2 - 4, y + h - 40], fill=(160, 160, 165))
    # smoke and flame
    d.ellipse([x + w // 2 + 18, y + 6, x + w // 2 + 38, y + 22], fill=(90, 90, 95))
    d.ellipse([x + w // 2 + 28, y + 2, x + w // 2 + 46, y + 16], fill=(120, 120, 125))
    d.polygon([(x + w // 2 + 20, y + h - 40), (x + w // 2 + 28, y + h - 52), (x + w // 2 + 36, y + h - 40)], fill=(255, 140, 20))
    # waves
    for i in range(4):
        wx = x + 6 + i * (w // 4)
        d.arc([wx, y + h - 12, wx + 22, y + h - 2], 180, 360, fill=(255, 255, 255), width=2)

def art_mercury(d, x, y, w, h):
    """Deep space, cratered Mercury, two orbiters on its ring."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 14, 30))
    for sx in range(10):
        px = x + 5 + (sx * 29) % (w - 10)
        py = y + 3 + (sx * 17) % (h - 8)
        d.ellipse([px, py, px + 2, py + 2], fill=(255, 255, 230))
    # Mercury
    mx, my, mr = x + w // 2, y + h // 2 + 4, min(w, h) // 2 - 8
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(180, 150, 120))
    d.ellipse([mx - mr + 6, my - mr + 8, mx - mr + 14, my - mr + 16], fill=(150, 120, 95))
    d.ellipse([mx + 4, my + 6, mx + 14, my + 16], fill=(150, 120, 95))
    d.ellipse([mx - 12, my + 2, mx - 4, my + 10], fill=(200, 175, 145))
    # orbiters
    d.ellipse([mx - mr - 12, my - mr - 6, mx - mr - 2, my - mr + 4], fill=(255, 220, 80))
    d.rectangle([mx - mr - 18, my - mr - 3, mx - mr - 12, my - mr + 1], fill=(140, 180, 220))
    d.ellipse([mx + mr - 2, my + mr - 10, mx + mr + 8, my + mr], fill=(120, 200, 255))
    d.ellipse([mx - mr - 2, my - mr - 2, mx + mr + 2, my + mr + 2], outline=(90, 110, 150), width=1)

def art_fbi(d, x, y, w, h):
    """A laptop glowing with database rows and a warning triangle."""
    d.rectangle([x, y, x + w, y + h], fill=(35, 40, 55))
    # laptop
    d.rectangle([x + w // 2 - 30, y + 10, x + w // 2 + 30, y + h - 20], fill=(20, 22, 32))
    d.rectangle([x + w // 2 - 26, y + 14, x + w // 2 + 26, y + h - 26], fill=(90, 200, 160))
    for i, lw in enumerate((34, 26, 40)):
        d.line([x + w // 2 - 20, y + 20 + i * 6, x + w // 2 - 20 + lw, y + 20 + i * 6], fill=(20, 60, 45), width=2)
    d.rectangle([x + w // 2 - 36, y + h - 20, x + w // 2 + 36, y + h - 14], fill=(60, 65, 80))
    # warning triangle
    tx, ty = x + w - 30, y + h - 30
    d.polygon([(tx, ty + 18), (tx + 10, ty), (tx + 20, ty + 18)], fill=(255, 190, 30))
    d.rectangle([tx + 9, ty + 6, tx + 11, ty + 12], fill=(30, 30, 30))
    d.ellipse([tx + 9, ty + 14, tx + 11, ty + 16], fill=(30, 30, 30))

def art_mlambo(d, x, y, w, h):
    """South African flag bands, a dignified silhouette, a half-mast flag."""
    d.rectangle([x, y, x + w, y + h], fill=(40, 70, 110))
    # flag bands
    d.rectangle([x, y, x + w, y + 6], fill=(220, 40, 50))
    d.rectangle([x, y + 6, x + w, y + 10], fill=(255, 255, 255))
    d.rectangle([x, y + 10, x + w, y + 16], fill=(20, 130, 60))
    # dignified silhouette
    cx, cy = x + w // 2, y + h // 2 + 2
    d.ellipse([cx - 9, cy - 20, cx + 9, cy - 2], fill=(30, 25, 35))
    d.ellipse([cx - 7, cy - 18, cx + 7, cy - 4], fill=(120, 85, 60))
    d.polygon([(cx - 16, cy + 22), (cx - 8, cy - 2), (cx + 8, cy - 2), (cx + 16, cy + 22)], fill=(90, 40, 60))
    d.ellipse([cx - 4, cy + 6, cx + 4, cy + 14], fill=(255, 215, 130))
    # half-mast flag
    fx, fy = x + w - 22, y + 20
    d.line([fx, fy, fx, fy + 26], fill=(220, 220, 220), width=2)
    d.rectangle([fx, fy + 8, fx + 12, fy + 14], fill=(20, 130, 60))

def art_drone(d, x, y, w, h):
    """City skyline under a quadcopter, a small Union Jack hint."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 220, 235))
    # skyline
    d.rectangle([x + 4, y + h - 22, x + 18, y + h - 6], fill=(110, 130, 150))
    d.rectangle([x + 22, y + h - 30, x + 38, y + h - 6], fill=(90, 110, 135))
    d.rectangle([x + 42, y + h - 18, x + 58, y + h - 6], fill=(120, 140, 160))
    d.rectangle([x + 28, y + h - 38, x + 32, y + h - 30], fill=(90, 110, 135))
    # drone
    dx, dy = x + w // 2 - 6, y + 10
    d.ellipse([dx, dy, dx + 22, dy + 8], fill=(50, 55, 65))
    d.line([dx - 6, dy + 2, dx + 28, dy + 2], fill=(40, 45, 55), width=2)
    d.ellipse([dx - 4, dy + 8, dx + 2, dy + 14], fill=(40, 45, 55))
    d.ellipse([dx + 20, dy + 8, dx + 26, dy + 14], fill=(40, 45, 55))
    d.line([dx + 11, dy + 8, dx + 11, dy + 16], fill=(40, 45, 55), width=2)
    # UK flag hint
    d.rectangle([x + w - 24, y + h - 16, x + w - 8, y + h - 6], fill=(30, 60, 140))
    d.line([x + w - 24, y + h - 16, x + w - 8, y + h - 6], fill=(255, 255, 255), width=1)
    d.line([x + w - 8, y + h - 16, x + w - 24, y + h - 6], fill=(255, 255, 255), width=1)

def art_trade(d, x, y, w, h):
    """EU circle of stars, the Indonesian flag, a handshake arc."""
    d.rectangle([x, y, x + w, y + h], fill=(210, 230, 220))
    # EU circle of stars
    cx, cy = x + w // 2 - 22, y + h // 2
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(30, 60, 140))
    for i in range(12):
        a = math.radians(i * 30)
        sx, sy = cx + int(12 * math.cos(a)), cy + int(12 * math.sin(a))
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 220, 60))
    # Indonesian flag
    fx, fy = x + w // 2 + 8, y + h // 2 - 14
    d.rectangle([fx, fy, fx + 28, fy + 12], fill=(220, 40, 50))
    d.rectangle([fx, fy + 12, fx + 28, fy + 24], fill=(255, 255, 255))
    d.line([fx, fy, fx, fy + 30], fill=(60, 60, 60), width=2)
    # handshake arc
    d.arc([x + w // 2 - 14, y + h - 18, x + w // 2 + 22, y + h + 6], 200, 340, fill=(30, 110, 90), width=3)

def art_bahrain(d, x, y, w, h):
    """Night sky over the Gulf: missile trails, an intercept burst, a factory fire."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 20, 44))
    # stars
    for sx in range(9):
        px = x + 6 + (sx * 31) % (w - 12)
        py = y + 4 + (sx * 11) % 12
        d.ellipse([px, py, px + 2, py + 2], fill=(230, 230, 255))
    # missile trails arcing down
    for tx in (x + 22, x + w // 2 + 6, x + w - 34):
        d.line([tx, y + 4, tx + 10, y + 26], fill=(255, 190, 90), width=2)
        d.ellipse([tx + 8, y + 24, tx + 14, y + 30], fill=(255, 120, 40))
    # intercept burst, high in the sky
    bx, by = x + w // 2, y + 12
    for a in range(0, 360, 45):
        ex = bx + int(11 * math.cos(math.radians(a)))
        ey = by + int(11 * math.sin(math.radians(a)))
        d.line([bx, by, ex, ey], fill=(255, 230, 140), width=2)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(255, 255, 220))
    # Gulf skyline
    d.rectangle([x + 8, y + h - 24, x + 24, y + h - 6], fill=(60, 70, 100))
    d.rectangle([x + 28, y + h - 30, x + 42, y + h - 6], fill=(70, 80, 110))
    d.rectangle([x + 46, y + h - 20, x + 60, y + h - 6], fill=(55, 65, 95))
    # factory fire on the right
    fx = x + w - 26
    d.rectangle([fx, y + h - 22, fx + 18, y + h - 6], fill=(90, 85, 80))
    d.polygon([(fx + 2, y + h - 22), (fx + 7, y + h - 34), (fx + 12, y + h - 22)], fill=(255, 140, 20))
    d.polygon([(fx + 8, y + h - 22), (fx + 13, y + h - 30), (fx + 18, y + h - 22)], fill=(255, 200, 60))
    d.ellipse([fx + 4, y + h - 40, fx + 14, y + h - 32], fill=(120, 115, 110))
    # sea line
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(30, 60, 95))

def art_dymer(d, x, y, w, h):
    """A collapsed apartment section, a rescue crane, dust in the air.
    Deliberately unlike the Kryvyi Rih scene: daylight, a crane, no ambulance."""
    d.rectangle([x, y, x + w, y + h], fill=(195, 205, 215))
    # the standing block (left)
    d.rectangle([x + 6, y + 14, x + 34, y + h - 8], fill=(120, 110, 100))
    for wy in (y + 20, y + 30, y + 40):
        d.rectangle([x + 10, wy, x + 16, wy + 5], fill=(255, 220, 120))
        d.rectangle([x + 22, wy, x + 28, wy + 5], fill=(200, 205, 210))
    # the collapsed section (right): jagged rubble pile
    d.polygon([(x + 36, y + h - 8), (x + 44, y + 26), (x + 52, y + 34),
               (x + 62, y + 28), (x + 72, y + 38), (x + w - 6, y + h - 8)],
              fill=(90, 82, 76))
    d.polygon([(x + 44, y + 26), (x + 52, y + 18), (x + 58, y + 26)], fill=(140, 130, 120))
    d.rectangle([x + 58, y + 30, x + 66, y + 36], fill=(200, 205, 210))
    # rescue crane reaching over the rubble
    d.line([x + w - 14, y + 6, x + w - 14, y + h - 30], fill=(200, 160, 30), width=3)
    d.line([x + w - 14, y + 8, x + 40, y + 14], fill=(200, 160, 30), width=2)
    d.line([x + 52, y + 14, x + 52, y + 26], fill=(60, 60, 60), width=1)
    d.rectangle([x + 48, y + 26, x + 56, y + 32], fill=(220, 60, 40))
    # dust puffs
    for dx, dy, r in ((x + 40, y + 20, 6), (x + 62, y + 16, 5), (x + w - 24, y + 22, 6)):
        d.ellipse([dx - r, dy - r, dx + r, dy + r], fill=(170, 165, 155))
    d.rectangle([x, y + h - 6, x + w, y + h], fill=(110, 105, 98))

def art_seoul(d, x, y, w, h):
    """An exam hall: rows of desks, a resignation letter, an AI warning."""
    d.rectangle([x, y, x + w, y + h], fill=(225, 230, 240))
    # exam hall desks in two rows
    for row_y in (y + 18, y + 32):
        for dx in (x + 10, x + 34, x + 58, x + w - 26):
            d.rectangle([dx, row_y, dx + 16, row_y + 8], fill=(150, 125, 95))
            d.ellipse([dx + 6, row_y - 5, dx + 10, row_y - 1], fill=(60, 60, 70))
    # the resignation letter, front and centre
    lx, ly = x + w // 2 - 16, y + h - 26
    d.rectangle([lx, ly, lx + 32, ly + 20], fill=(255, 255, 255), outline=(120, 120, 130))
    for i, lw in enumerate((24, 20, 16)):
        d.line([lx + 4, ly + 4 + i * 5, lx + 4 + lw, ly + 4 + i * 5], fill=(40, 40, 50), width=1)
    # red seal stamp on the letter
    d.ellipse([lx + 22, ly + 12, lx + 30, ly + 20], fill=(200, 40, 40))
    # AI warning triangle, top right
    tx, ty = x + w - 26, y + 6
    d.polygon([(tx, ty + 14), (tx + 8, ty), (tx + 16, ty + 14)], fill=(255, 190, 30))
    d.rectangle([tx + 7, ty + 5, tx + 9, ty + 10], fill=(30, 30, 30))
    d.ellipse([tx + 7, ty + 11, tx + 9, ty + 13], fill=(30, 30, 30))
    # chalkboard strip at the top
    d.rectangle([x, y, x + w, y + 4], fill=(50, 80, 70))

ARTS = {"cop31": art_cop31, "cartel": art_cartel, "f1": art_f1, "cricket": art_cricket,
        "ship": art_ship, "mercury": art_mercury, "fbi": art_fbi, "bahrain": art_bahrain,
        "dymer": art_dymer, "mlambo": art_mlambo, "drone": art_drone,
        "trade": art_trade, "seoul": art_seoul}


# ---------- world map (stylised blobs — clean at strip-map scale) ----------
# (centre lon, centre lat, radius-x deg, radius-y deg). Blobs are drawn in
# the same projection as the pins, so every pin sits on or beside its land.
BLOBS = [
    (-100, 48, 32.3, 17.6),   # North America
    (-104, 24, 8.5, 8.1),     # Mexico
    (-85, 18, 11.9, 8.1),     # Central America / Caribbean
    (-42, 73, 8.5, 6.8),      # Greenland
    (-60, -15, 12.8, 25.7),   # South America
    (15, 52, 16.1, 14.9),     # Europe
    (-2, 54, 3.4, 6.8),       # UK
    (20, 4, 16.1, 28.4),      # Africa
    (26, -28, 6.8, 8.1),      # Southern Africa
    (45, 30, 12.8, 13.5),     # Middle East
    (85, 50, 34.0, 17.6),     # Central Asia
    (78, 22, 6.8, 12.2),      # India
    (103, 13, 8.5, 10.8),     # SE Asia
    (118, -2, 13.6, 8.1),     # Indonesia
    (115, 33, 10.2, 12.2),    # East China
    (139, 37, 3.4, 8.1),      # Japan
    (128, 36, 2.5, 5.4),      # Korea
    (134, -25, 15.3, 12.2),   # Australia
    (172, -41, 3.4, 6.8),     # New Zealand
]

def project(lon, lat, box, lon_range=(-180, 180), lat_range=(75, -58)):
    """Equirectangular projection of (lon, lat) into a pixel box."""
    x0, y0, x1, y1 = box
    fx = (lon - lon_range[0]) / (lon_range[1] - lon_range[0])
    fy = (lat_range[0] - lat) / (lat_range[0] - lat_range[1])
    return (x0 + fx * (x1 - x0), y0 + fy * (y1 - y0))

def draw_land(d, box, lon_range, lat_range):
    """Paint the land blobs for a map box, clipped to the box.
    Blobs are projected from a GLOBAL list, so a blob far outside an inset's
    lon/lat range (e.g. Greenland in the Western-Europe inset) would otherwise
    paint a landmass over neighbouring panels. Drawing onto a temp layer and
    pasting through a mask keeps every blob inside its own box."""
    x0, y0, x1, y1 = box
    sx = (x1 - x0) / (lon_range[1] - lon_range[0])
    sy = (y1 - y0) / (lat_range[0] - lat_range[1])
    tmp = Image.new("RGB", (x1 - x0, y1 - y0), (0, 0, 0))
    td = ImageDraw.Draw(tmp)
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    md = ImageDraw.Draw(mask)
    for clon, clat, rx, ry in BLOBS:
        cx, cy = project(clon, clat, box, lon_range, lat_range)
        lx, ly = cx - x0, cy - y0
        td.ellipse([lx - rx * sx, ly - ry * sy, lx + rx * sx, ly + ry * sy],
                   fill=LAND, outline=LANDLINE)
        md.ellipse([lx - rx * sx, ly - ry * sy, lx + rx * sx, ly + ry * sy], fill=255)
    d._image.paste(tmp, (x0, y0), mask)

def repel(points, box, min_dist=15, passes=14):
    """Deterministic repulsion so numbered pins never overlap.
    Returns list of (display_x, display_y, true_x, true_y)."""
    pts = [[x, y, x, y] for (x, y) in points]
    x0, y0, x1, y1 = box
    for _ in range(passes):
        moved = False
        for i in range(len(pts)):
            for j in range(i):
                dx = pts[i][0] - pts[j][0]
                dy = pts[i][1] - pts[j][1]
                dist = math.hypot(dx, dy)
                if dist < min_dist and dist > 0.01:
                    push = (min_dist - dist) / 2 + 0.5
                    ux, uy = dx / dist, dy / dist
                    pts[i][0] += ux * push
                    pts[i][1] += uy * push
                    pts[j][0] -= ux * push
                    pts[j][1] -= uy * push
                    moved = True
                elif dist <= 0.01:
                    pts[i][0] += min_dist / 2
                    pts[j][0] -= min_dist / 2
                    moved = True
        for p in pts:
            p[0] = min(max(p[0], x0 + 8), x1 - 8)
            p[1] = min(max(p[1], y0 + 8), y1 - 8)
        if not moved:
            break
    return [(p[0], p[1], p[2], p[3]) for p in pts]

def draw_pins(d, pins, box, lon_range, lat_range, font_num, radius=7, min_dist=15):
    """pins: list of (num, lon, lat). Draws leader lines + numbered circles."""
    true_xy = [project(lon, lat, box, lon_range, lat_range) for _, lon, lat in pins]
    placed = repel(true_xy, box, min_dist=min_dist)
    for (num, _, _), (dx, dy, tx, ty) in zip(pins, placed):
        if math.hypot(dx - tx, dy - ty) > 3:
            d.line([dx, dy, tx, ty], fill=(120, 110, 100), width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(120, 110, 100))
        r = radius
        d.ellipse([dx - r, dy - r, dx + r, dy + r], fill=NAVY, outline=WHITE, width=1)
        t = str(num)
        tw = d.textlength(t, font=font_num)
        d.text((dx - tw / 2, dy - 5), t, font=font_num, fill=WHITE)

# ---------- panel (bottom-up: chips, body, headline, illustration fills the rest) ----------
def draw_panel(d, x, y, w, h, num, chip, cat, verify, place, headline, body, source, art_key, hero=False):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=RULE, width=1)
    cc = CAT_COLORS.get(cat, NAVY)
    bh = 16 if hero else 14
    d.rectangle([x, y, x + w, y + bh], fill=cc)
    bf = SANS_B(10 if hero else 9)
    d.text((x + 6, y + 2), f"{num:02d}  {cat}", font=bf, fill=WHITE)
    d.text((x + w - 6 - d.textlength(place, font=SANS_B(8)), y + 3), place, font=SANS_B(8), fill=(235, 235, 235))
    # chips at the bottom; drop the verify chip if it would collide with the source
    cy = y + h - 16
    chip_f = SANS_DB(8)
    sf = SANS(10)
    sw = d.textlength(source, font=sf)
    w_ver = int(d.textlength(verify, font=chip_f)) + 8
    cw = draw_chip(d, x + 6, cy, chip, chip_color(chip), chip_f)
    if x + 10 + cw + w_ver + 6 < x + w - 6 - sw:
        draw_chip(d, x + 10 + cw, cy, verify, VERIFY, chip_f)
    d.text((x + w - 6 - sw, cy + 1), source, font=sf, fill=(110, 105, 100))
    # body: up to 3 lines, ending just above the chips
    bfl = fit_lines(d, body, SANS(11), w - 12, 3)
    body_top = cy - 2 - len(bfl) * 13
    for i, ln in enumerate(bfl):
        d.text((x + 6, body_top + i * 13), ln, font=SANS(11), fill=(40, 40, 46))
    # headline: up to 2 lines, ending just above the body
    hf = SERIF_B(14 if hero else 11)
    lh = 16 if hero else 13
    hl = fit_lines(d, headline, hf, w - 12, 2)
    head_top = body_top - 1 - len(hl) * lh
    for i, ln in enumerate(hl):
        d.text((x + 6, head_top + i * lh), ln, font=hf, fill=INK)
    # illustration: drawn at canonical 50px height, then rescaled to fit.
    # (Keeps every art function safe whatever space the text leaves.)
    ih = head_top - (y + bh + 1)
    if ih >= 20:
        tmp = Image.new("RGB", (w - 2, 50), WHITE)
        td = ImageDraw.Draw(tmp)
        ARTS[art_key](td, 0, 0, w - 2, 50)
        if ih != 50:
            tmp = tmp.resize((w - 2, ih), Image.LANCZOS)
        d._image.paste(tmp, (x + 1, y + bh + 1))


# ---------- main layout ----------
M = 8  # page margin

def section_bar(d, y, h, title, right=None):
    d.rectangle([M, y, W - M, y + h], fill=NAVY)
    d.text((M + 8, y + 2), title, font=SANS_B(10), fill=WHITE)
    if right:
        rf = SANS_B(9)
        d.text((W - M - 8 - d.textlength(right, font=rf), y + 3), right, font=rf, fill=(200, 210, 230))

def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- top bar 0-22 ---
    d.rectangle([0, 0, W, 22], fill=NAVY)
    tb = "THE WORLD IN ONE DAY  \u00b7  40 STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    tf = SANS_B(11)
    d.text(((W - d.textlength(tb, font=tf)) / 2, 4), tb, font=tf, fill=WHITE)

    # --- masthead 22-84 ---
    d.text((M, 22), "THE SUNDAY LEDGER", font=SERIF_B(38), fill=INK)
    d.text((M, 60), "The world in one day \u2014 Sunday 22 November 2026", font=SERIF_I(13), fill=(80, 75, 70))
    rt = "Sunday 22 November 2026"
    d.text((W - M - d.textlength(rt, font=SERIF_B(16)), 26), rt, font=SERIF_B(16), fill=NAVY)
    rt2 = "40 stories \u00b7 7 regions \u00b7 every one dated"
    d.text((W - M - d.textlength(rt2, font=SANS(11)), 50), rt2, font=SANS(11), fill=(80, 75, 70))
    d.line([M, 84, W - M, 84], fill=RULE, width=1)

    # --- standfirst 88-118 ---
    sf = wrap(d, STANDFIRST, SERIF_I(12), W - 2 * M)
    for i, ln in enumerate(sf[:2]):
        d.text((M, 88 + i * 16), ln, font=SERIF_I(12), fill=(50, 48, 44))

    # --- KPI strip 122-158 ---
    ky = 122
    kw = (W - 2 * M) // 6
    for i, (num, label) in enumerate(KPIS):
        x0 = M + i * kw
        d.rectangle([x0, ky, x0 + kw - 2, ky + 36], fill=LIGHT, outline=RULE, width=1)
        d.text((x0 + 8, ky + 2), num, font=SANS_DB(18), fill=NAVY)
        ll = wrap(d, label, SANS_B(9), kw - 16)
        for j, ln in enumerate(ll[:2]):
            d.text((x0 + 8, ky + 21 + j * 10), ln, font=SANS_B(9), fill=(70, 66, 60))

    # --- region bar 164-178 ---
    ry = 164
    d.text((M, ry + 1), "REGIONS", font=SANS_B(10), fill=INK)
    bx0, bw = M + 62, W - 2 * M - 62
    x = bx0
    total = sum(c for _, c, _ in REGIONS)
    for name, count, color in REGIONS:
        seg = int(bw * count / total)
        d.rectangle([x, ry, x + seg - 1, ry + 14], fill=color)
        lab = f"{name} {count}"
        lf = SANS_B(8)
        if d.textlength(lab, font=lf) <= seg - 4:
            d.text((x + 3, ry + 3), lab, font=lf, fill=WHITE)
        else:
            d.text((x + 3, ry + 3), str(count), font=lf, fill=WHITE)
        x += seg

    # --- hero row 184-314 ---
    hy = 184
    hw = (W - 2 * M - 2 * 6) // 3
    for i, p in enumerate(PANELS[:3]):
        num, chip, cat, verify, place, headline, body, source, lon, lat, art = p
        draw_panel(d, M + i * (hw + 6), hy, hw, 130, num, chip, cat, verify, place,
                   headline, body, source, art, hero=True)

    # --- small rows 320-448, 454-582 ---
    sw = (W - 2 * M - 4 * 6) // 5
    for row, y0 in enumerate((320, 454)):
        for i, p in enumerate(PANELS[3 + row * 5: 8 + row * 5]):
            num, chip, cat, verify, place, headline, body, source, lon, lat, art = p
            draw_panel(d, M + i * (sw + 6), y0, sw, 128, num, chip, cat, verify, place,
                       headline, body, source, art, hero=False)

    # --- map 588-742 ---
    my, mh = 588, 154
    d.rectangle([M, my, W - M, my + mh], fill=SEA, outline=RULE, width=1)
    world_box = (M + 4, my + 18, 680, my + mh - 4)
    draw_land(d, world_box, (-180, 180), (72, -50))
    all_pins = [(p[0], p[8], p[9]) for p in PANELS] + [(b[0], b[3], b[4]) for b in BRIEFS]
    draw_pins(d, all_pins, world_box, (-180, 180), (72, -50), SANS_DB(7), radius=6, min_dist=13)
    d.rectangle([M + 4, my + 2, M + 268, my + 16], fill=SEA)
    d.text((M + 8, my + 3), "WHERE IT HAPPENED \u2014 EVERY STORY PINNED", font=SANS_B(10), fill=NAVY)
    d.text((M + 8, my + mh - 12), "Pin 6 = ESA control, Darmstadt (BepiColombo is in Mercury orbit).",
           font=SANS(9), fill=(50, 65, 90))
    # Western Europe inset (the crowded half; eastern pins read on the main map)
    ex0, ey0, ex1, ey1 = 688, my + 18, W - M - 4, my + 84
    d.rectangle([ex0, ey0, ex1, ey1], fill=(215, 230, 240), outline=NAVY, width=1)
    eu_box = (ex0 + 2, ey0 + 12, ex1 - 2, ey1 - 2)
    draw_land(d, eu_box, (-4, 18), (58, 37))
    eu_nums = {12, 35, 39}
    draw_pins(d, [p for p in all_pins if p[0] in eu_nums], eu_box, (-4, 18), (58, 37),
              SANS_DB(7), radius=6, min_dist=13)
    d.rectangle([ex0 + 2, ey0 + 1, ex0 + 158, ey0 + 12], fill=(215, 230, 240))
    d.text((ex0 + 4, ey0 + 1), "WESTERN EUROPE \u2014 DETAIL", font=SANS_B(9), fill=NAVY)
    # Middle East inset
    mx0, my0, mx1, my1 = 688, my + 88, W - M - 4, my + mh - 4
    d.rectangle([mx0, my0, mx1, my1], fill=(215, 230, 240), outline=NAVY, width=1)
    me_box = (mx0 + 2, my0 + 12, mx1 - 2, my1 - 2)
    draw_land(d, me_box, (25, 62), (42, 12))
    me_nums = {1, 8, 15, 21, 28, 31, 36, 38}
    draw_pins(d, [p for p in all_pins if p[0] in me_nums], me_box, (25, 62), (42, 12),
              SANS_DB(7), radius=6, min_dist=13)
    d.rectangle([mx0 + 2, my0 + 1, mx0 + 96, my0 + 12], fill=(215, 230, 240))
    d.text((mx0 + 4, my0 + 1), "MIDDLE EAST", font=SANS_B(9), fill=NAVY)

    # --- briefs bar 748-764, rows 768-876 ---
    section_bar(d, 748, 16, "ALSO ON SUNDAY 22 NOVEMBER \u2014 27 MORE STORIES",
                "Chips: SUN = Sunday \u00b7 SAT>SUN = Sat, still developing \u00b7 FRI>SUN = Fri, still carried")
    bw3 = (W - 2 * M - 2 * 10) // 3
    for col in range(3):
        x0 = M + col * (bw3 + 10)
        for r in range(9):
            num, chip, text, lon, lat = BRIEFS[col * 9 + r]
            y0 = 768 + r * 12
            nf = SANS_B(11)
            d.text((x0, y0), f"{num}.", font=nf, fill=NAVY)
            nx = x0 + d.textlength(f"{num}. ", font=nf)
            cf = SANS_B(10)
            d.text((nx, y0 + 1), chip, font=cf, fill=chip_color(chip))
            tx = nx + d.textlength(chip + " ", font=cf)
            t = truncate_to_width(d, text, SANS(11), x0 + bw3 - tx)
            d.text((tx, y0), t, font=SANS(11), fill=INK)

    # --- still developing bar 882-896, rows 900-948 ---
    section_bar(d, 882, 14, "STILL DEVELOPING")
    for i, item in enumerate(STILL_DEV):
        col, r = (0, i) if i < 4 else (1, i - 4)
        x0 = M + col * 504
        y0 = 900 + r * 12
        d.text((x0, y0), "\u2022 " + item, font=SANS(11), fill=INK)

    # --- date check bar 954-966, text 970-994 ---
    section_bar(d, 954, 12, "DATE CHECK \u2014 OLD NEWS, DELIBERATELY LEFT OUT")
    dc = wrap(d, DATE_CHECK, SANS(11), W - 2 * M)
    for i, ln in enumerate(dc[:2]):
        d.text((M, 970 + i * 12), ln, font=SANS(11), fill=(70, 66, 60))

    # --- footer 996-1024 ---
    foot = "Every story here happened, or was first reported, on Sunday 22 November 2026. Officials' counts and claims are attributed."
    d.text((M, 996), foot, font=SANS(11), fill=INK)
    d.text((M, 1009), "UTC", font=SANS_B(9), fill=NAVY)
    cx0, cx1, cy = M + 26, M + 326, 1012
    d.line([cx0, cy, cx1, cy], fill=NAVY, width=2)
    for h24 in range(0, 25, 6):
        tx = cx0 + (cx1 - cx0) * h24 / 24
        d.line([tx, cy - 3, tx, cy + 3], fill=NAVY, width=1)
        lab = f"{h24:02d}"
        d.text((tx - d.textlength(lab, font=SANS(7)) / 2, cy + 4), lab, font=SANS(7), fill=(90, 85, 80))
    mx = cx0 + (cx1 - cx0) * COMPILE_HOUR / 24
    d.polygon([(mx, cy + 2), (mx - 4, cy + 8), (mx + 4, cy + 8)], fill=(200, 40, 40))
    d.text((cx1 + 8, 1009), f"NOW {COMPILE_TIME}", font=SANS_B(9), fill=(200, 40, 40))
    comp = f"Compiled {COMPILE_TIME} UTC \u00b7 THE SUNDAY LEDGER"
    d.text((W - M - d.textlength(comp, font=SANS_B(10)), 1008), comp, font=SANS_B(10), fill=NAVY)

    return img

if __name__ == "__main__":
    im = render()
    im.save("entry.png", optimize=True)
    data = open("entry.png", "rb").read()
    print(f"entry.png: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    print(f"size: {im.size}")
