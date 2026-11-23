# BUILD-REPORT-R2 — The Sunday Ledger v2 (news-image-20261122 R2)

**Bounty:** news-image-20261122 ($100, 50 places) — R2 revision of "The Sunday Ledger".
**Deadline:** 24 Nov 00:00 UTC.
**Build session:** 38c6b1b1-4386-4e12-869c-47b592bd8531 (this session).
**Plan session:** 384266bb (verified content plan, `~/workspace/makefun/news-image-20261122-R2-PLAN.md`).
**Repo:** emasinves0-commits/news-image-20261122-r2 (NEW — R1's dir and repo untouched).
**Remote HEAD (at time of writing):** `6337543f4259e9c073064beba8c1b5a9874747b4`
("Add entry.png (Sunday Ledger v2, R2)", 2026-11-23T02:31:52Z).
**Push verification:** all 8 files pushed via PAT (all 201); contents API
lists all 8 with sizes matching local exactly; local `git hash-object`
matches the remote blob sha for all 7 root files (0 mismatches); entry.png
re-downloaded from raw.githubusercontent at the HEAD commit — sha256
identical to local (`95c41003…`, 268,878 bytes); `.makefun/owner.json`
re-downloaded — wallet Aoq99… correct. About: homepage
`https://make.fun/bounty/news-image-20261122` + topic `makefun` (both 200).
(The final HEAD after this report's own push is one commit later; the parent
records it at submit time.)

## Entry

- `entry.png`: 1024×1024, **268,878 bytes**
- **sha256: `95c4100314f66102d57c21d525adf4972a4175e74f5648062022ac94693cb7d8`**
- Deterministic: two consecutive `python3 draw.py` renders byte-identical
  (sha256 matched; verified twice — once before and once after the map fix).

## What R2 changes vs R1 (content swap on R1's geometry)

- Lead: COP31 **collapses with no deal in Antalya** (R1's "reaches a deal" was
  factually wrong — the error behind R1's 1 dev loss). KPI 1: "17 — YEARS
  SINCE A COP LAST COLLAPSED (COPENHAGEN 2009)".
- New panels: #8 Bahrain (Iran hits US bases; 2 hurt), #9 Dymer (Russian
  drone flattens Kyiv flats; 15 missing), #13 Seoul (minister quits over
  exam AI-cheating chaos). New art: art_bahrain, art_dymer, art_seoul;
  art_cop31 rewritten as a collapse scene (dark clouds, empty hall, fallen
  gavel). Deleted: art_kryvyi, art_nepal, art_vaccine.
- New briefs: #20 Libya warship sunk at Benghazi, #24 Indonesia factory
  fire, #25 Nigeria Fulani reprisals, #27 Somalia–UAE deadline,
  #28 Lebanon explosives seizure, #29 Trump 17-nation anti-cartel coalition.
- Results updated to full Sunday: F1 Verstappen wins (0.639s, 35 lead
  changes, 75th win), cricket NZ 119/2 trailing by 233, Liverpool 4–0,
  Barcelona 3–2, Rising Stars result, Nigeria boat toll 29.
- Region balance: Europe 8, Asia 8, Americas 8, Middle East 6, Africa 5,
  Oceania 3, Global 2 (= 40). STILL_DEV fully resolved (7 items).
- COMPILE_TIME "23:30". DATE_CHECK reworked (330 chars, Kryvyi Rih added).

## Verification — fit checks (programmatic, from pixels/fonts)

- Panel headlines: all ≤ 2 lines. Panel bodies: all ≤ 3 lines, **0 ellipses**
  (after fixing #04, #05, #13 — see below).
- Art heights: min 23px (#02), most 29px — all ≥ 20px threshold. No overlaps
  (bottom-up layout, vertical slack ≥ 3px by construction).
- Briefs 14–40: **no truncation** — including #20 ("Russian warship sunk at
  Libya port in drone strike", 49 chars), which the plan flagged as a risk.
- DATE_CHECK: 2 lines (314 chars). STILL_DEV: all 7 items ≤ 325px (limit 504).
- Region bar: ALL 7 labels in full (even GLOBAL 2: 39px label vs 47px segment).
- KPI labels: all 6 fit 2 lines. Standfirst: 1 line.

## Verification — eye-check (crops, read from pixels)

Read every art panel at 2×, the region bar, the data strip, and both map
insets at 2× (R5 lesson: sub-labels inside panel art + bar names from pixels).

- **Top:** masthead, standfirst, KPI strip, region bar — all clean.
- **Heroes 1–3:** COP31 (dark collapse scene — somber, reads; gavel/chairs
  faint, nit only), cartel, F1 — all clean, headlines/bodies/chips/sources
  complete.
- **Smalls 4–13:** all 10 verified individually at 2× — cricket, ship,
  Mercury, FBI, Bahrain, Dymer, South Africa, Kyiv, trade, Seoul. All clean.
- **Map:** world map + Western-Europe inset (pins 12, 35, 39) + Middle-East
  inset (pins 1, 8, 15, 21, 28, 31, 36, 38) — all pins verified by
  projection computation AND by reading the 2× inset crops. Brief 36's pin
  is Doha (51.5, 25.3), correctly inside the ME inset.
- **Bottom:** briefs 14–40 all present, STILL_DEV 7/7, DATE_CHECK 2 lines,
  UTC clock with NOW 23:30 marker at the far right, footer complete.
- **Full poster:** final render re-read end-to-end — clean.

## Fixes made during this build

1. **Body ellipses (3).** #04 cut "by 233", #05 cut "towed it away",
   #13 cut "the college exam". Shortened all three bodies; re-verified
   0 ellipses. #05's headline also changed: "Burning Russian ship" →
   "Russian ship" — the flames were out on Sunday, so "Burning" was wrong.
2. **Map land bleed (real defect, inherited from R1).** The Greenland blob,
   projected into the Western-Europe inset (lon range −4..18), landed at
   (137, 581) with radius 123px and painted a LAND-coloured smear over the
   bottom of panels 9–10 (x 14–259, y 565–587), covering the SUN/CONFIRMED
   chips and the "AP" source. Root cause: `draw_land` drew every global
   blob into every box without clipping. Fix: `draw_land` now draws onto a
   temp layer and pastes through a mask, clipping every blob to its own box.
   Verified: 0 LAND pixels above the map (was a 246×23px smear); 37,877 LAND
   pixels remain inside the map. R1 has the same defect (its renderer is
   identical); R2 does not inherit it.
3. **Misread corrected (no change).** On first reading the 2× inset crops I
   thought the EU inset showed overlapping pins ("35" twice) and the ME
   inset showed impossible numbers. Reading the actual `render()` code and
   the BRIEFS lon/lat proved the insets are correct: they pin explicit
   number sets (EU {12, 35, 39}, ME {1, 8, 15, 21, 28, 31, 36, 38}) and
   every pin projects inside its box. The "35" at the EU inset's bottom is
   "39" (Barcelona) — 7px "9" vs "5" at crop scale. No geometry change made.

## Nits left alone (not blockers)

- Hero 1 (COP31) art is very dark; the fallen gavel and empty chairs are
  faint at poster scale. It reads as a somber collapse scene; the headline
  and body carry the story.
- Panel 5's ship art still shows a small flame on the deck while the body
  says "Flames out" — the flame depicts the drone strike (the event), not
  the current state, as with the other event illustrations.

## Files in the repo

`README.md` (3 live make.fun badges + bounty link, 40-story table),
`main.ts`, `draw.py`, `build.py`, `entry.png`, `LICENSE` (MIT, SPDX),
`.makefun/owner.json` (wallet Aoq99k3QzdPr3RbaqTTWZG3U8j6YENcDojoyhL8cfa92),
`BUILD-REPORT-R2.md` (this file).
