# TECH v0.7.3 — Colosseum visual / QA-state validation: root cause

**Status:** STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING.
**Verdict:** both visual artifacts are **vanilla Rev 1 behaviour in an invalid QA state** (the opening Narshe party).
They are **not** FF6X engine or item-bank defects. **Production is unchanged** (v0.7.2 production / celes-tech,
byte-identical, now asserted by SHA-1 in the builder). Only the QA ROM changes: its Colosseum entry now normalizes
the party.

## 1. Reported (TECH v0.7.2 user runtime QA)
| Fighter | Symptom |
|---|---|
| Terra | battle works; an extra / corrupted sprite appears beside her |
| Biggs/Vicks, Wedge | battle logic works, attacks and effects render, the fighter sprite itself is invisible |

## 2. Reproduction (`tools/emu_colosseum_visual.py`, report `out/emulator_v073/colosseum_visual/`)
| Run | Terra | Wedge | Vicks |
|---|---|---|---|
| **A** v0.7.2 QA ROM, QA menu Colosseum, opening party | extra armor sprite (Magitek mode `$64BA = 1`) | invisible, empty name box (record pointer `$3010 = $FFFF`) | invisible, empty name box (`$FFFF`) |
| **B** clean Rev 1, same opening state, vanilla receptionist branch CB:78D9 | **same** | **same** | **same** |

A and B have the same fighter state and 30–51 identical rendered battle frames per fighter. The clean, unmodified
game produces exactly what the user saw. Screenshots: `out/COLOSSEUM_VISUAL_v0.7.3_before_after.png` (rows 1–2).

## 3. Exact causes (both inside vanilla Rev 1 code)

### 3.1 Wedge / Vicks invisible: the Colosseum's actor lookup does not fit temporary characters
* The Colosseum menu stores the chosen fighter's **character record number** in `$0208`
  (Terra 0, Wedge **14 = $0E**, Vicks **15 = $0F**).
* Battle init (C2 InitParty, Colosseum branch `@2f75`): `lda $0208 / sta $3ED8` puts that value into battle slot 1 as
  an **actor id**. The party-graphics loop (`@304d`) then searches the 16 records for one whose actor `$1600` equals it.
  It takes the sprite id from `$1601`, the name from `$1602-$1607` and the data pointer into `$3010`.
* In the opening, records 14/15 are temporary actors: **Wedge = actor $20**, **Vicks = actor $21** (graphics $0E,
  soldier). No record has actor `$0E`/`$0F`, so slot 1 gets **no sprite id, no name and no record pointer**
  (`$3010 = $FFFF`, name `FF…`). The fight still runs, so attacks and effects render, but the fighter sprite and name
  box stay empty.
* Permanent characters 0–13 always sit in record n with actor n, so the lookup never fails for them. The World of
  Ruin Colosseum only ever has permanent characters (records 14/15 are not party members there).

### 3.2 Terra extra sprite: Magitek status puts the battle into Magitek mode
* In the opening Terra has status 1 bit `$08` (**Magitek**, `$1614 = $08`).
* Battle graphics init (C1:0FB6) ORs the four characters' status 1 and sets **`wMagitekModeEnabled` ($7E64BA)** from
  bit `$08`. Magitek mode changes how battle graphics draw and animate characters (Magitek armor actions,
  `GetMagitekOffset`). The Colosseum battle ($23F, one fighter, Colosseum layout) never runs with Magitek in the real
  game; in this state an additional armor-like sprite is drawn next to Terra. That is the reported "extra sprite".
* **Isolation (run C, clean Rev 1):** the same opening state with *only* Terra's Magitek bit cleared → `$64BA = 0`,
  Terra renders normally, no extra sprite (sheet row 2, last image).

FF6X code around these paths: the only FF6X bytes are the accepted v0.6.0 patch `N303_FORMATION_COLOSSEUM_RANGE`
at C2:2F75 (`LDX $3ED4 / CPX #$023E` → `JSL ColosseumRangeCheck`, so battles $240+ are not treated as Colosseum).
It only decides *whether* the battle is a Colosseum battle (id $23E/$23F as in vanilla). The record lookup after it
(`lda $0208 / sta $3ED8`, C2:2F80, and the graphics loop at C2:304D) is vanilla. So are the Magitek-mode flag
(C1:0FB6) and the sprite id `$1601`. The v0.7.1 hooks in C2 battle init only read equipment and inventory. The
behaviour is identical on clean Rev 1 (A = B, identical frames).

## 4. QA fix (QA ROM only): normalized QA Colosseum party
QA menu → `Colosseum (full battle)` → **`Fight: Terra/Locke/Celes/Edgar`** (`QaColoFight7`) now does what the vanilla
recruit script does (Locke joins at CC:A621: `char_prop`, `create_obj`, `obj_gfx`, `char_party`, with Terra/Wedge/
Vicks leaving the party), then calls the vanilla receptionist branch, then restores the opening party:

| Step | Event bytes | Effect |
|---|---|---|
| normalize | `88 00 F7 FF` | Terra: clear Magitek (status 1 bit $08) |
| | `3F 0E 00` `3F 0F 00` | Wedge, Vicks leave the party (temporary actors) |
| | `40 01 01` `7F 01 01` `3D 01` `37 01 01` `3F 01 01` | Locke: properties, name, object, graphics, joins party 1 |
| | `40 06 06` `7F 06 06` `3D 06` `37 06 06` `3F 06 01` | Celes, the same |
| | `40 04 04` `7F 04 04` `3D 04` `37 04 04` `3F 04 01` | Edgar, the same |
| Colosseum | `B2 D9 78 01` | call CB:78D9 (vanilla receptionist branch, unchanged) |
| restore | `3F 01 00` `3E 01` · `3F 06 00` `3E 06` · `3F 04 00` `3E 04` | Locke / Celes / Edgar leave, objects deleted |
| | `3F 0E 01` `3F 0F 01` `89 00 08 00` | Wedge / Vicks rejoin, Terra's Magitek status restored |

After every fight the opening party (`$1850`) and Terra's Magitek bit are exactly as before, so the other QA tests
and the opening story still start from the same state. The event assembler gained these vanilla opcodes
(`char_prop`, `obj_gfx`, `char_name`, `create_obj`, `delete_obj`, `char_party`; plain encodings, validated ranges).

## 5. Verification (emulator, snes9x; not user QA)
| Check | Result |
|---|---|
| E v0.7.3 QA menu Fight: Terra (win → prize), Locke (natural), Celes (natural), Edgar (win → prize): own sprite and name, record found, Magitek mode 0, bright battle, return with control, party and Magitek restored | PASS |
| E5 Terra wearing **QA Blade13D / QA Mail 13E / QA Charm13F**: renders normally, wins, all three extended items still equipped | PASS |
| E′ same normalized party on clean Rev 1 (the QA ROM's own normalize/restore bytes): QA renders and ends every fight exactly as Rev 1 (identical frames, same fighter state, same inventory) | PASS |
| F **real Colosseum** (map $19D, receptionist CB:78C3), permanent characters Terra / Locke / Celes, on **production v0.7.2**, v0.7.3 QA and clean Rev 1: fighter visible, no extra sprite, identical to Rev 1, return to $19D | PASS |
| Weapon / attack effects | identical rendered frames to Rev 1 in E′ and F (the comparison covers fighter, opponent and effects); screenshots in the sheet |

Totals and the rerun of all v0.7.1/v0.7.2 regressions: `REGRESSION_REPORT_v0.7.3.md`.

## 6. Classification
| Artifact | Class | Production action |
|---|---|---|
| Wedge / Vicks invisible | vanilla Rev 1 behaviour; invalid QA state (temporary actors 14/15 in the Colosseum) | none |
| Terra extra sprite | vanilla Rev 1 behaviour; invalid QA state (Magitek status in the Colosseum) | none |

Do not use Wedge / Vicks (or Magitek Terra) as Colosseum proof characters.
