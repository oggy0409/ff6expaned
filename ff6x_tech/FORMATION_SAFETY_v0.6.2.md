# TECH v0.6.2 — formation-safety hardening (tooling only, no ROM change)

**STATIC PASS · EMULATOR PASS (evidence below) · no new user QA needed (no ROM byte changed)**

Accepted baseline **TECH v0.6.1** rebuilt byte-exact and now locked in the builder (`expect_sha1`):
QA `8a55707ff2b4cd1364fdabf75e91422ba90ff8bb` / `289BD3B9`; production `26ebd7d3…` / `C9DB005B`; celes-tech `a7ae5d4c…` / `E2BDA3B1`.
All 15 targets reproduce; 2 full builds, 86 output files, 0 differences; selftests **59/59**.
The v0.6.1 graphics architecture (router F0:1240, hook C1:20FF, relocated tables) is untouched.

## 1. What the builder now checks (`ff6x/formation_safety.py`)
Runs on the **built image** for every Expanded Edition formation of a v0.6-layout target (vanilla formations are never
validated or rewritten). Each slot's sprite is decoded exactly as btlgfx does (MonsterGfxProp → stencil → tiles → palette,
clipped to the VRAM-map box); its **opaque-pixel bounding box** is placed at x = (pos >> 4)·8, y = (pos & 15)·8
(geometry pixel-verified in v0.6.1 and again here, §5).

| Mode | Targets | ERROR → |
|---|---|---|
| `enforce` (default) | production, celes-tech and every future production target | build fails (fail closed) |
| `report` | frozen QA/regression targets (v0.6.1 QA accepted, v0.6.0 QA) | report only, ROM bytes unchanged |

Outputs per target with formations: `out/<rom>.formation_safety.json` and `out/formation_preview/<rom>__F<id>.png`
(separate files: accepted manifests are unchanged).
Preview **before** a ROM build: `python build.py <clean.sfc> --target <t> --preview-only`.

## 2. Safe screen-coordinate ranges (measured in snes9x, 32 battle screenshots, 256×224 output)
| Area | Range | Note |
|---|---|---|
| visible monster field | **x 8–247, y 4–150** | x 0–7 and 248–255 masked black, y 0–3 black |
| battle window | y ≥ 151 | frame line at y = 151 |
| party lane | x ≥ 168 | vanilla never puts a monster pixel beyond x = 167 (1 201 normal sprites) |
| formation position grid | x = 0–120, y = 0–120 in 8-px steps | position byte = (x/8) << 4 \| (y/8) |

## 3. Edge-margin rule (opaque bounding box vs visible field)
| Edge | ERROR | WARNING | Vanilla calibration (normal-size sprites, information only) |
|---|---|---|---|
| left | margin < **8 px** (x0 < 16) | < 16 px (x0 < 24) | 0 errors, 3 warnings — vanilla keeps x0 ≥ 16 |
| top | margin < 8 px (y0 < 12) | < 16 px | 41 below 8 px (fliers at y = 8), stricter than vanilla by design |
| right | margin < 8 px | < 16 px | never reached (party lane first) |
| bottom (window) | sprite crosses into the window (y1 > 150) | margin < 8 px | 46 cross (38 of them by 1 px, hidden), 192 within 8 px: vanilla "stands" monsters on the window, so only crossing is an error |
| party lane | — | right edge x1 > 167 | 0 |
| VRAM box clipping | — | sprite clipped by its box | 5 |

`v0.6.1 $242/$243` slot 0 (Dark Wind at pos `$13`, x0 = 8) → **left margin 0 px = ERROR** in enforce mode (this is the
reported placement); report mode for the frozen QA build. Fix pattern (example ex2): pos `$33` → x0 = 24 (16 px).

**Large-sprite exception** — `"layout_exception": {"slots": [k], "reason": "…"}` downgrades that slot's edge ERRORs to
WARNINGs. Refused (ERROR) unless the sprite is large (> 64 px wide/tall or large 16×16 stencil) and a reason is given.
Magitek conflicts can never be overridden.

## 4. Magitek VRAM conflict (R13 audit) — `data/vram_safety.json`
Monster graphics = 16×16 cells of 8×8 tiles, uploaded linearly to VRAM `$6000 + 32·(row·16 + col)` (verified).
With **any** party member in Magitek armor, VRAM cells **rows 0–11, columns 12–15** (48 cells) are overwritten by armor
graphics ~90–120 frames after the formation loads — for 1, 2 or 3 riders alike, independent of formation/VRAM map,
and MagiTek beam animations overwrite no further sprite cell (5 formations, monsters alive). A slot whose used tiles
reach that area shows armor tiles instead of the monster.

| VRAM map | slots: origin (col,row) box → Magitek | all slots safe |
|---|---|---|
| 0 | 0 (0,0) 8×8 safe · 1 (8,0) 8×8 *sprite-dependent* (≤ 4 cols) · 2 (0,8) 8×8 safe · 3 (8,8) 8×8 *sprite-dependent* (≤ 4 cols) | no |
| 1 | 0 safe · 1 (8,0) *sprite-dependent* · 2 (0,8) safe · 3 (4,8) safe · 4 (8,8) safe · **5 (12,8) 4×4 UNSAFE** | no |
| 2 | 0 (0,0) 12×8 safe · 1 (0,8) 12×8 safe | **yes** |
| 3 | 0 (0,0) 8×16 safe · 1 (8,0) 8×16 *sprite-dependent* | no |
| 4 | 0 (0,0) 12×8 safe · 1 (0,8) 8×8 safe · 2 (8,8) 8×8 *sprite-dependent* | no |
| 5 | 0 (0,0) 8×16 safe · 1 (8,0) *sprite-dependent* · 2 (8,8) *sprite-dependent* | no |
| 6 | 0 (0,0) 16×16 *sprite-dependent* (≤ 12 cols, or wide part only in rows 12–15) | no |
| 7 | 0 (0,0) 12×12 safe · **1 (12,0) 4×12 UNSAFE** · 2–5 (0/4/8/12,12) 4×4 safe | no |
| 8 | 0 (0,0) 8×8 · 1 (0,8) 8×8 · 2 (8,0) 4×8 · 3 (8,8) 4×8 — all safe | **yes** |
| 9 | 0 (0,0) 12×12 safe | **yes** |
| 10 | 0 (0,0) 8×12 · 1 (8,0) 4×8 · 2 (8,8) 4×8 · 3 (0,12) 4×4 · 4 (4,12) 4×4 — all safe | **yes** |
| 11 | 0–2 (0/4/8,0) 4×8 · 3 (8,8) 4×8 · 4 (0,8) 8×8 — all safe | **yes** |
| 12 | 0 safe · 1 (8,0) *sprite-dependent* · 2–4 (0/4/8,8) 4×8 safe · **5 (12,8) 4×8 UNSAFE** | no |

*sprite-dependent* = safe only if no used tile reaches column 12 (the validator checks the exact stencil cells).
Vanilla consistency: every vanilla formation built from the opening's monsters (Guard / Lobo / Vomammoth / Whelk:
`$000 $001 $002 $011 $029 $054 $1B0`) uses map 0 slot 0 or map 8 and is safe; `$004` (Marshal + Lobos, map 12 slot 1, Locke's party) would conflict but is never
fought in Magitek. 253 vanilla slot uses would conflict if a Magitek party could meet them (information only).

**Build rule** — every EE formation must declare `"magitek_possible": true/false` (missing = ERROR in enforce mode).
`true` + any used cell in the area = ERROR, with the list of VRAM maps that hold the same sprites unclipped and
conflict-free. Nothing is changed silently: the author sets `"vram_map": N` (new, optional; writes only formation
byte 0 bits 4–7; other bits from the template). Example ex3 → suggested map 7 → ex4: emulator shows the slot-5 bird
pixel-exact with the Magitek party (was 0/91 exact on map 1).

## 5. Evidence (Claude-side emulator, not user runtime)
| Evidence | Result |
|---|---|
| `out/magitek_vram_v062/` VRAM diff Magitek vs none: `$008` (1/2/3 riders), `$002`, `$004` | identical 48-cell mask in every case |
| `out/magitek_screen_v062/` + `…n/` 12 vanilla formations on screen, Magitek vs no Magitek | every predicted conflict slot corrupted only with Magitek; every predicted-safe slot exact (`$039` slot 1 safe while slot 3 conflicts — sprite-level precision); `$071` slot 5 at (12,12) safe |
| beam runs `$001 $002 $011 $071 $03C` (MagiTek command executed) | no sprite cell of a safe slot overwritten |
| `out/formation_safety_examples/emulator/` examples in a scratch ROM | ex3 slot 5 0/91 exact (Magitek) → ex4 (map 7) 81/91 exact; ex1 geometry exact at x = 8 |
| validator on the v0.6.0 QA ROM | flags `$242/$243` slot 5 `magitek_vram_conflict` (the v0.6 failure would have been caught) |

## 6. Files
`ff6x/formation_safety.py`, `ff6x/formation_preview.py`, `data/vram_safety.json` (+ `devtools/make_vram_safety.py`),
`formations/examples/ex1–ex7`, `tools/formation_safety_examples.py`, `tools/magitek_vram_audit.py`,
`devtools/vanilla_formation_calibration.py` → `audits/vanilla_formation_calibration_v062.json`,
`out/TECH_v0.6.2_formation_safety_examples.png`. `ff6x/monsters.py`: optional `vram_map`. QA formation JSONs: added
`"magitek_possible": true` (documentation; bytes unchanged, verified by hash).

## 7. Limits / risks
| # | Item |
|---|---|
| F1 | Visible field measured in snes9x output. Real TVs/other emulators may crop more overscan; 16 px preferred margin covers this. |
| F2 | Back / pincer / side attacks reposition or mirror monsters; only the normal-attack layout is validated. Recommend production formations disable back/pincer/side unless reviewed (BattleProp byte 0 bits 4–7, inverted into `$2F48`). |
| F3 | Only the Magitek party graphic was audited. Other special party graphics (e.g. Imp, Gau leap states, Moogle/Umaro parties, ghost) not measured — no conflict seen in 12 normal-party formations. |
| F4 | Sprite overlap between monsters is not an error (vanilla overlaps often); preview shows it. |
| F5 | Sprite animation/size changes by special effects (e.g. bosses that change graphics mid-battle) are not modelled. |
