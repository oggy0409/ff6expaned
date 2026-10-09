# TECH v0.6.1 — enemy-graphics routing comparison report ($182 / $183 vs vanilla Dark Wind $028)

Machine-readable: `GFX_COMPARE_REPORT_v0.6.1.json` (= `out/gfx_compare_v061/GFX_COMPARE_REPORT.json`, 8 scenarios, every slot).
Tool: `tools/gfx_compare_report.py` (snes9x via stable-retro; same start RAM for every ROM; battle injected with event
`4D FE 3F FE` + `$11E0` = formation). Screen check: each slot's expected sprite is rendered from its ROM tiles + palette and
compared pixel-by-pixel **at its formation position** every 10 frames for 900 frames (91 samples; birds fly in during the
first 60–90 frames, so 81–85/91 exact = fully exact after arrival). Status of this evidence: **EMULATOR**, not user runtime.

## Answer (E): what caused the v0.6 QA failure
**None of the listed routing defects.** Not wrong graphics record, not wrong stencil, not wrong expanded-bank fetch, not
off-by-one, not size metadata, not 3bpp/4bpp. Cause = **"another defect" in the QA formation choice**:

v0.6 isolation formations `$242/$243` were copies of vanilla formation `$008` (VRAM map 1) with the test bird in **slot 5**.
In the opening the party rides **Magitek armor**. The Magitek party graphics occupy VRAM that overlaps the VRAM map 1
**slot 5** box (tile origin 12,8). The bird's tiles are correct in the WRAM tile buffer (7E:AE3F), but on screen slot 5 shows
Magitek-armor tiles → "different / corrupted sprite". This happens **identically in unmodified vanilla Rev 1** (S1: the
vanilla Dark Wind in slot 5 is 0/91 exact, 502/563 pixels wrong) and disappears when Magitek status is cleared (S2).
`$008` is a normal World of Balance field encounter (party on foot), so vanilla play never shows this combination. Both the exact clone and the Vulture-palette
variant were in that slot, so both "failed" for the same reason; the vanilla Dark Wind beside them (slot 4) was fine.

Why v0.6 emulator evidence said "pixel-identical to vanilla `$008`": it compared against vanilla `$008` with the same
Magitek party — which is corrupted in exactly the same way. The comparison was correct but the reference was itself broken.

## A. $182 exact clone vs vanilla Dark Wind (same battle, v0.6.1 `$242`, Magitek party, S6)
| Field | `$028` Dark Wind (slot 0) | `$182` DW CLONE (slot 2) | `$183` DW VULPAL (slot 3) |
|---|---|---|---|
| gfx-prop slot read (router: id<$180 → id, else id+$20) | `$028` | `$1A2` | `$1A3` |
| gfx-prop table | F8:8000 (PC 388000), relocated v0.5 | same | same |
| MonsterGfxProp record (5 B) | `1B 17 00 46 1F` | `1B 17 00 46 1F` | `1B 17 00 4A 1F` |
| graphics index (word0 & $7FFF) | `$171B` | `$171B` | `$171B` |
| bpp (word0 bit15) | 4 | 4 | 4 |
| large stencil (byte2 bit7) | no | no | no |
| expansion flag (byte2 bit5) | 0 | 0 | 0 |
| router-selected graphics base | E9:7000 (vanilla) | E9:7000 | E9:7000 |
| tile source = base + index×8 | **EA:28D8** (PC 2A28D8) | **EA:28D8** | **EA:28D8** |
| tiles / bytes | 14 / 448 | 14 / 448 | 14 / 448 |
| stencil index (byte4 + byte2 bit6) | `$01F` | `$01F` | `$01F` |
| stencil bytes (FB:4000 small table) | `E0 70 F0 F0 00 00 00 00` | same | same |
| resolved size cols×rows (stencil; RAM `$812F`) | 4×4 / 4×4 | 4×4 / 4×4 | 4×4 / 4×4 |
| palette index (RAM `$8117`) | `$046` / `0046` | `$046` / `0046` | **`$04A` / `004A`** |
| palette bytes (FB:0000 + 32×pal) | `00 00 22 00 B7 46 F1 35 6D 29 0A 21 C7 14 85 0C D6 5A E7 7E BE 73 DC 0E B2 0D EA 04 91 20 4B 18` | identical | `29 25 84 0C BD 73 3A 53 76 3E D0 35 BC 3E 8E 29 2B 21 C7 14 FA 21 11 19 4A 10 15 7A 4E 65 CA 44` |
| WRAM tile buffer == ROM source | yes | yes | yes |
| buffer box SHA-1 | `e9dd90a413b9…` | `e9dd90a413b9…` | `e9dd90a413b9…` |
| formation position byte → screen x,y | `13` → 8,24 | `4B` → 32,88 | `87` → 64,56 |
| VRAM map 8 box origin / size | 0,0 / 8×8 | 8,0 / 4×8 | 8,8 / 4×8 |
| on-screen pixel-exact (563 opaque px) | 83/91, final 0 bad | 83/91, final 0 bad | 83/91, final 0 bad |

The same fields are identical in the v0.6.0 `$242`/`$243` (S3–S5): records, tile source, stencil, buffer SHA-1 — only the
screen result of slot 5 depends on the party.

## B. $183 vs $182: every field except palette identical
Record differs only in byte 3 (`46` → `4A`, palette low byte); graphics index, bpp, large flag, expansion flag, base, tile
source, tile count, stencil index/bytes, size, buffer SHA-1 identical (table above, all scenarios). The Vulture palette on
Dark Wind pixels is therefore a pure recolour (the v0.5 TESTMOB B look); shape is preserved (S5, S6 screenshots).

## Scenarios (D, raw in JSON)
| Tag | ROM | Formation (VRAM map) | Party | Result |
|---|---|---|---|---|
| S1 | vanilla Rev 1 | `$008` (map 1), DW in slots 4,5 | Magitek | slot 4 exact 83/91; **slot 5 0/91 (502 px wrong) — vanilla engine** |
| S2 | vanilla Rev 1 | `$008` | Magitek cleared (poke) | all slots exact |
| S3 | v0.6.0 QA | `$242` (map 1), `$182` slot 5 | Magitek | **slot 5 0/91** = user's failure, identical to S1 |
| S4 | v0.6.0 QA | `$242` | Magitek cleared | all exact |
| S5 | v0.6.0 QA | `$243`, `$183` slot 5 | Magitek cleared | all exact (Vulture-coloured DW shape) |
| S6 | **v0.6.1 QA** | `$242` (map 8): `$028`/`$182`/`$183` slots 0/2/3 | Magitek | **all exact** |
| S7 | **v0.6.1 QA** | `$243` (map 8): 3× `$028` | Magitek | all exact (reference) |
| S8 | vanilla Rev 1 | `$002` (map 8, opening Guards) | Magitek | all exact (template layout is Magitek-safe in vanilla) |

Screenshots: `out/gfx_compare_v061/<tag>_f600.png`, `_f900.png`; contact sheet `TECH_v0.6.1_gfx_routing_contact_sheet.png`
(S1/S3 show Magitek-armor tiles in place of the slot-5 bird).

## Hotfix decision
No engine/router/data change is justified by the evidence. v0.6.1 changes only the two QA isolation formations
(template `$002`, VRAM map 8, all three birds in one battle + a 3× vanilla reference battle) and the QA menu text.
Production / celes-tech ROMs are byte-identical to v0.6.0.

Open item for production content (not a hotfix): formations that can appear while the party uses Magitek armor
(or other large party graphics) must not use VRAM boxes overlapping that VRAM region. Proven safe so far: VRAM map 8
slots 0/2/3 (and vanilla's own Magitek formations). Which other map/slot boxes conflict has not been fully mapped
(KNOWN_RISKS R13).
