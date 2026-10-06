# FFVI Expanded Edition — TECH v0.9.1 (Item Data Alignment) + TECH v0.9.2 (Celes Enablers) — QA package

**Status: STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING.**
Baseline: TECH v0.9 (USER RUNTIME PASS / ACCEPTED). The v0.9 targets are frozen and rebuilt byte-exact by this source
(`production-v0.9`, `celes-tech-v0.9`, `item-tech-v0.9`, SHA-1s asserted by `build.py`).
Approved decisions: `docs/design/DESIGN_DECISIONS_v1.0.md` (G1 closed, D-01 .. D-25). Work order: D-15 (one cycle, one QA
package, two logically separate milestones).

| target | file | SHA-1 | CRC32 | content |
|---|---|---|---|---|
| `production` | `FF6X_Rev1_TECH_v0.9.1_PRODUCTION` | `2dc73bfbbcf4657eb59eec93bd614181ecdc817c` | `01AE6F84` | v0.9 + item data alignment (v0.9.1) |
| `celes-tech` | `FF6X_Rev1_TECH_v0.9.1_CELES_TECH` | `e2192311a997ee49315807508d71ca202d4a8d09` | `EA66714A` | production v0.9.1 + accepted Annex slice |
| `item-tech` | `FF6X_Rev1_TECH_v0.9.2_ITEM_ALIGNMENT_CELES_ENABLERS_QA` | `697a25e886e843ad356d98cdfb078fcba7c8615f` | `7EA0481F` | v0.9.1 + Celes enablers E1-E9 + QA hub (**the user QA ROM**) |

The Celes enablers exist **only in the QA target** (D-15: proved in QA targets; the Celes ROM Script Pass / CONTENT v1.0
decide what production carries). Full hashes: `HASHES_v0.9.2.txt`. Byte-level changes: `PATCH_TABLE_v0.9.2.md`,
`out/DELTA_v0.9_to_v0.9.2.csv`.

## Build
`python3 build.py "<Final Fantasy III (USA) (Rev 1).sfc>" --target all --out out` (27 targets, every frozen hash asserted;
clean ROM SHA-1 `057ada1c…` CRC32 `C0FA0464`). Static self-tests: `python3 tools/selftest.py <clean>` (148 guards).
Emulator regression: `tools/run_regression_v092.sh` (see `REGRESSION_REPORT_v0.9.2.md`: every new and accepted suite
PASS; two test-method updates - the v0.6.1 suite menu path / AI observation and the equipment-battle J1 / O1 monster-ATB
hold - are documented there with the evidence, `KNOWN_RISKS_v0.9.2.md` R66 / R67). Evidence: `out/emulator_v092/`,
contact sheets `out/ITEM_ALIGNMENT_V091_SHEET.png`, `out/CELES_ENABLERS_V092_SHEET.png`.

## A. TECH v0.9.1 — item data alignment (production + QA)
Per-item table: `ITEM_ALIGNMENT_v0.9.1.md` (generated). Sources: `items/production_v091/` (authored by
`items/production_v091/author_v091.py` from the accepted v0.9 data; every change cites its decision / cross-check row).

| item | locked (source) | v0.9.1 |
|---|---|---|
| Gaia Tonic `$127` | one ally, 1,500 HP + Regen (MB §18, D-16) | one ally, **exactly 1500 HP** (battle and field) + **Regen set** (battle) |
| Aether Flask `$128` | 100 MP | **exactly 100 MP** |
| Phoenix Ash `$129` | (keep) | unchanged |
| Null Dust `$12A` | Dispel one target (D-17) | battle, one target, **exact vanilla Dispel set** (Vanish, Image, Berserk, Regen, Slow, Haste, Stop, Shell, Safe, Reflect, Life 3, Float); not sold |
| Iron Ration `$12B` | 600 HP (D-16) | **exactly 600 HP** (the unlocked Poison cure removed); Rebuilt Mobliz, 300 GP |
| Remedy+ `$12C` | normal status + Zombie | vanilla Remedy set (Blind / Poison / Imp / Petrify / Mute / Sap) **+ Zombie**; rare, not sold |
| Beacon Flare `$12D` | Fire to all + reveals the invisible (D-17) | Fire damage to all **and removes Vanish** in the same action (Image kept) |
| Magitek Cell `$12E` | Lightning + non-elemental hybrid, limited, Foundry after Celes (D-17) | one enemy; **800 total = 400 Lightning-reactive + 400 non-elemental** (weak 1200, null 400, absorb 0); Item command (no MP, not a spell); Bolt Beam animation; Figaro Foundry only once `EXP_CELES_DONE`; **hold/buy at most 3** (owned + bought ≤ 3, re-entry cannot bypass); 1500 GP |
| shops `$80-$84` | Bible §19 (D-18) | `$80` Rebuilt Mobliz (Iron Ration, Remedy, Fenix Down, Gaia Tonic, Gaia Gear) · `$81` Reopened Narshe Forge (3 elemental blades + Gold / Diamond Shld; **no Tempered Edge**) · `$82` Rebuilt Doma (Forged / Tempest / Murasame, Ninja Gear, Head Band, 3 scrolls; **no Doma Edge**) · `$83` Figaro Foundry (canonical tools) · `$84` = Foundry after `EXP_CELES_DONE` (tools + Magitek Cell) |
| Darill's Coin `$11E` | Spd +5, **Mag +2**, M.Evade +20% (D-19) | Mag +2 added; description updated |
| sources (metadata) | D-03/DA-01, D-20, X0223, X0599-X0636 | Leo's Blade = Records Vault concealed locker (DA-01) · Tempered Edge = Empty Forge reward, never sold · Doma Edge = Cyan/Doma reward, no second copy · Sandpiercer = one-time Foundry chest · Magister Robe → Forgotten Age · Triune Sigil = its own sigil (Triune Sentinel), description fixed · key-item sources / arcs |

DERIVED values (conservative, documented in the item `derived` lists): Gaia Tonic 2000 GP, Iron Ration 300 GP, Magitek
Cell 800 total damage and 1500 GP (Figaro price modifier 6 = half price when Edgar leads), the shop gear choices.

**Engine (D-16 "smallest safe path", extended consumables only)** — `asm/item_v091/v091.s`, hooks `patches/item_v091_hooks.py`:
* `XFixAmt` (FA:7E00) fixed amount per extended consumable: battle — CalcTargetDmg C2:0BD3 replaces the heal amount
  when `$11A4` bit 0 (restore) is set; field — `_c38ccd` C3:8CD1 replaces the power byte. Vanilla items never have a
  context (the table is indexed by the extended low byte, the context is cleared for every id < $100).
* `XHybrid` (FA:7E80) hybrid split at the same hook (vanilla element order on the Lightning half; the vanilla element
  block is skipped for the hybrid action). `$11A1` stays Lightning (AI element tests see a Lightning item).
* `XShopCap` (FA:7EC0) purchase cap at `_c3b82f` / `_b83e` (C3:B836 / C3:B83E), from the owned count.
* `XCtxFlags` (FA:7F00) Vanish removal kept for Null Dust / Beacon Flare at MagicStatusEffect C2:4418 (the vanilla Item
  command clears zb3 bit 7, which cancels any Vanish removal by an item; unchanged for every other item).
* The item-action context (`XFIXAMT/XHYBEL/XVANOK`, saved-RAM bytes $1E23-$1E26, transient) is cleared before **every**
  battle command at ExecCmd C2:13FA (Regen / Poison ticks, counters and monster actions included — measured: a Gaia
  Tonic's Regen ticks heal 76-84, never 1500), at the AI dispatch (v0.9 hook) and at New Game / load.
* Hooks: `V9101` C2:13FA, `V9102` C2:0BD3, `V9103` C3:8CD1, `V9104` C3:B836, `V9105` C3:B83E, `V9106` C2:4418 (no overlap
  with any v0.7.1 / v0.9 hook — asserted by the builder).

## B. TECH v0.9.2 — Celes enablers (QA target only)
Details: `CELES_ENABLERS_v0.9.2.md`.

| | enabler | proof (emulator suite `tools/emu_enablers_v092.py`) |
|---|---|---|
| E1 | WoR landing → new map → Falcon | world short entrance (map $001 (146,202), SET_PARENT) → map **$1A2** Vector Outer Ward (QA); south exit = parent map → world map beside the parked airship; board with A |
| E2 | Praetor solo, Bits at 70% | formation `$244` (template Dadaluma `$1B6`): Bits in **hidden** slots, shown by the Praetor AI (`entry` = AI $F5) when HP ≤ 70% (new AI condition `HP_PCT_LE`, exact integer %) |
| E3 | Overload at 40% | new AI effect `OVERLOAD`: Defense 165 → 80 (DERIVED), Haste (vanilla set_status), overload palette written to the battle palette buffer (placeholder, D-14); HP untouched (no monster swap) |
| E4 | Grounding Field | new AI condition `LIGHTNING_COUNT` (calls the vanilla IF_ELEMENT): every 3rd qualifying Lightning hit → Lightning null + not weak for 3 Praetor turns (`GROUNDING_TICK`), then weak again; per-battle vars 0-2 only (vars 4-23 are SRAM-saved and untouched) |
| E5 | party-conditional event + speaker fallback | vanilla event cmd `$DE` (party case word → bits $1A0+char, read-only refs `CASE_CHAR_*`); survivor reaction Locke → Edgar → Sabin → line dropped (D-11) |
| E6 | Imperial Ruins palette / tile variants | MapPal relocated (ED:C480 → F7:A000, 48 vanilla palettes byte-exact) + palette **$30** derived from the Magitek-lab palette (PAL-01 ash / iron / ivory); map $1A2 uses vanilla tiles |
| E7 | Vale / NPC palette variant | MapSpritePal relocated (E6:8000 → F7:E000, 32 vanilla byte-exact) + sprite palette **$20**; the map startup event loads it into sprite slot 7 (event cmd `$60`) for Vale |
| E8 | persistent outer-map states | event bits (D-21) → map startup event redraws the memorial wall / archive door: none · temporary tag wall (arc done, both branches) · Preserve = archive retained · Burn = archive burned · stone memorial (Graves Without Names); survives save → power cycle → load |
| E9 | front-only formations; Praetor + Bits safe | formation flag `front_only` (aux bits = side/pincer/back disabled); `$244` / `$245` 0 formation-safety errors with the hidden slots checked (the checker now also checks hidden-at-start members) |

The Praetor (`monsters/qa92_praetor`, id `$184`) carries the **locked stats** (Lv 36, HP 47,800, MP 9,000, Spd 45, BP 34,
Def 165, MDef 150, Mag 13, weak Lightning, null Poison, immune Doom / Petrify / Confuse) and the locked AI rules; the
Suppressor Bit (`$185`) the locked MOB-03 stats (Reflect support: one Reflect on the Praetor per Bit). Graphics are
vanilla placeholders (Guardian / Spit Fire, D-14). For **hand QA only**, the twin formation `$245` uses `PraetorQA`
(`$186`) / `Bit QA` (`$187`): byte-identical AI scripts, 1/10 HP and attack / magic 1, so an early-game QA party can reach
the 70% / 40% / Grounding Field rules (asserted identical by the self-test; the locked battle is `$244`).

Event bits (D-21, all FREE_CANDIDATE in the Rev 1 audit, reserved permanently): `EXP_HOPE_EMPIRE $0E0`,
`EXP_CELES_STARTED $0E8`, `EXP_CELES_DONE $0E9`, `EXP_CELES_RECORDS_PRESERVED $0EA`, `EXP_CELES_RECORDS_CHOSEN $0EB`,
`EXP_GRAVES_DONE $0EC`, NPC `NPC_CELES_VALE_OUTER $6F0`. QA only: vanilla `$1B9` (airship available) may be written by
the QA hub (`vanilla_qa_write_refs`, never available to production packages).

## QA hub (item-tech)
New Game → Narshe QA tile (up 6, left 4) → **TECH v0.9.2 QA ACCESS**: `Items v0.9.1` · `Celes enablers v0.9.2` · `Older QA
(v0.9 tree)` (the accepted v0.9 menus, unchanged). Manual checklist (~25 min, Vietnamese): `USER_QA_TECH_v0.9.2_VI.md`.

## Not done (by instruction)
No story rewards placed, no Celes ROM Script Pass, no CONTENT v1.0 maps / text, no final art. Narrative amendment v1.3
(D-12) has no text yet. Known risks: `KNOWN_RISKS_v0.9.2.md`.
