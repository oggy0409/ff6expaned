# CELES ENABLERS E1-E9 — TECH v0.9.2 (QA target `item-tech` only)

Status: STATIC PASS · EMULATOR PASS (`tools/emu_enablers_v092.py` 14/14) · USER RUNTIME QA PENDING.
Scope (D-15): prove every engine capability the Celes arc needs, in the QA target only. **No Celes story, no CONTENT v1.0
text, no final art** (D-14: palette-adapted vanilla placeholders). Production v0.9.1 contains none of this.

Source map:

| piece | files |
|---|---|
| AI extension (2 conditions, 2 effects) | `asm/celes_v092/ai_ext.s`, hooks in `patches/celes_enablers_v092.py` (V9201 / V9202 / V9203 / V9204) |
| palette relocation + derived palettes | `patches/celes_enablers_v092.py` (V9210-V9212), `palettes/v092/palettes.json` |
| event compiler additions | `ff6x/eventasm.py`: `load_map ... AIRSHIP / SET_PARENT`, `world_end`, `party_case` ($DE), `load_pal` rows 0-15, `set_tiles` |
| map package additions | `patches/map_v04.py`: short entrance `SET_PARENT`, `init_event` (MapInitEvent, claim `MAP_INIT_EVENTS_NEW`) |
| monster / formation additions | `ff6x/monsters.py` (status / element fields, `compile_ai` ext ops, hidden slots, `front_only`), `ff6x/formation_safety.py` (hidden-at-start members checked) |
| QA content | `monsters/qa92_*`, `formations/qa92_0244`, `qa92_0245`, `formations/qa_v092.json`, `maps/celes_outer_v092` (map `$1A2`), `events/celes_enablers_v092`, `events/qa_access_v092` |
| allocations | `data/allocations.json` (bits D-21, `CASE_CHAR_*` read refs, `vanilla_qa_write_refs`, regions `MAPX_MAP_PAL` / `MAPX_SPRITE_PAL`, claims) |

## E1 — World of Ruin landing → new map → back to the Falcon
* World map `$001` tile (146,202) east of Kefka's Tower gets a **short entrance** with the vanilla `SET_PARENT` flag
  (`$0200` in the entrance word): the engine stores the world map + position as the parent. Map `$1A2` (Vector Outer
  Ward, QA placeholder layout) starts at (16,27) facing up.
* The south exit (15,29) is a long exit to destination `$1FF` = parent map → the world map at (146,203), beside the
  parked Falcon. Stepping onto the airship and pressing A boards and takes off (vanilla airship behaviour).
* Event compiler: `load_map` accepts `AIRSHIP` (flags bit 0, world maps only, followed by a world-script that ends in
  `world_end` = `$FF`) so the QA hub can put the party aboard the Falcon in the WoR.
* QA only: the hub sets vanilla bit `$1B9` (airship available) through `vanilla_qa_write_refs`
  (`QA_VANILLA_AIRSHIP_AVAILABLE`), which production packages cannot use (builder-enforced).
* Proof: E1 — fly, land (B), walk 2 north → `$1A2` (16,27) with parent (1,146,202); south exit → (146,203); board → airborne.

## E2 — Praetor alone at the start, Suppressor Bits at 70 %
* Formation `$244` (template = vanilla Dadaluma formation `$1B6` layout): slot 0 Praetor `$184`; slots 1-2 Suppressor
  Bit `$185` **hidden** (monster id set, not in the "present" mask), loaded with full HP.
* New AI condition `HP_PCT_LE pct` (`$40`): exact integer percentage `HP*100 / MaxHP` through the SNES hardware divider.
* At ≤ 70 % the Praetor counter runs `entry $03 2 $06` (vanilla AI `$F5`: show monsters 2 + 3) once (switch var 2 bit 1).
* Proof: E2 (start: shown mask 1, Bits 2200 HP hidden, opening Barrier Safe + Shell, front attack); E2 (a Fight hit to
  ≤ 70 % → shown mask `$07`).

## E3 — Barrier Overload at 40 %
* New AI effect `OVERLOAD def` (`$42`): Defense := `def` (80, DERIVED; locked base 165), and the overload palette is
  copied into the battle palette buffer `$7E7F00 + slot*32` (uploaded every NMI). Followed in the script by vanilla
  `SET_STATUS 19` (Haste). **HP is untouched** (no monster-record swap); the overload palette is DERIVED from the
  Praetor's own vanilla palette (`$1E1`, warm white/orange tint, placeholder for VFX-02).
* One hit crossing both 70 % and 40 % also launches the Bits (the 40 % block shows them as well).
* Proof: E3 (Defense 80, Haste, palette buffer changed, HP = previous − damage).

## E4 — Grounding Field
* New AI condition `LIGHTNING_COUNT n` (`$41`): runs the vanilla element test (IF_ELEMENT, C2:1C5E) for Lightning on the
  action that hit the Praetor; counts per-battle var 0. On the 3rd qualifying hit: Lightning **null + not weak**, field
  turns var 1 = 3, count reset. It never returns true (the counter section continues normally).
* New AI effect `GROUNDING_TICK elem` (`$43`), placed at the end of every Praetor turn: field turns − 1; at 0 → weak
  Lightning restored, Lightning null cleared (Poison null kept). Hits during the field are not counted.
* **Per-battle vars 0-2 only.** Battle vars 4-23 are global and SRAM-saved (`$1DC9-$1DDC`); an earlier build used them
  and the state leaked across battles — fixed and covered by E4 "nothing persists".
* Proof: E4 (1200 / 1200 / 1200 → field → 400 non-elemental only), E4 expiry (weak again, next hit 1200, count 1),
  E4 persistence (new battle starts clean, global vars untouched).

## E5 — Party-conditional event + speaker fallback
* Vanilla event command `$DE` (party case) sets bits `$1A0 + char` for the characters in the current party; the builder
  exposes them as read-only refs `CASE_CHAR_TERRA .. CASE_CHAR_UMARO` (`$1A0-$1AD`).
* Survivor reaction (D-11): base line + exactly one reaction — Locke → Edgar → Sabin → line dropped.
* Proof: E5 (four parties: P1 Locke / Terra-Celes-Edgar-Sabin Edgar / P2 Sabin / Terra + Celes none).

## E6 — Imperial Ruins palette / tile variants
* The vanilla map palette table (ED:C480, 48 × 96 B) is relocated to **F7:A000** (region `MAPX_MAP_PAL`), byte-exact,
  and the three consumers re-pointed (V9210 C0:266D, V9211 C0:50EE, V9212 C0:AA21). New palette **`$30`** = PAL-01
  Imperial Ruins, DERIVED from vanilla `$18` (Magitek Research Facility) by a documented transform.
* Map `$1A2` uses palette `$30` with vanilla tiles. Tile variants are drawn by event (`set_tiles`, see E8).
* Proof: E6 (field palette buffer = derived palette except the 10 engine-managed colours, which also differ on vanilla
  map `$013`; 48 vanilla palettes byte-identical at F7:A000).

## E7 — Vale / NPC palette variant
* The vanilla map sprite palette table (E6:8000, 32 entries) is relocated to **F7:E000** (`MAPX_SPRITE_PAL`), byte-exact;
  new sprite palette **`$20`** (Vale, DERIVED from vanilla `$01`).
* The map startup event loads it into sprite palette slot 7 (`load_pal 15 $20`, rows 8-15 = sprite slots 0-7). Vale's
  NPC uses palette 7 and the switch `NPC_CELES_VALE_OUTER` (`$6F0`).
* Proof: E7 (slot 7 = palette `$20`; slots 0-6 vanilla; Vale hidden by default, shown when the NPC bit is set).

## E8 — Persistent outer-map states
* Map startup event `EvOuterInit` (MapInitEvent table D1:FA00 entry for `$1A2`, code in the claim
  `MAP_INIT_EVENTS_NEW`) redraws the memorial wall (10-12,10) and archive door (19-20,10) from the D-21 bits:

| state | bits | memorial wall | archive door |
|---|---|---|---|
| none | — | machinery | sealed |
| arc done, Burn | `EXP_CELES_DONE`, `EXP_CELES_RECORDS_CHOSEN` | temporary tag wall | burned |
| arc done, Preserve | + `EXP_CELES_RECORDS_PRESERVED` | temporary tag wall | archive retained |
| Graves Without Names | + `EXP_GRAVES_DONE` | stone memorial | keeps its branch |

* Event bits are ordinary saved event bits, so the state survives save → power cycle → load.
* Proof: E8 (four states), E8 persistence.

## E9 — Front-only formations, Praetor + Bits safe
* Formation flag `front_only`: aux byte 0 high nibble `$E` (side / pincer / back attack disabled).
* `formation_safety` now also checks hidden-at-start members (they are drawn when shown): `$244` / `$245` have 0
  errors (2 margin warnings: Bit top margin 13 px < preferred 16 px).
* Proof: E9 (12 battle starts at different RNG phases → all front; aux `E3 00 00 0E`; 0 safety errors).

## Praetor / Suppressor Bit data
`$184` Magitek Praetor: locked stats (CELES_PRODUCTION_SPEC_v1.0 §7.2) — Lv 36, HP 47,800, MP 9,000, Spd 45, BP 34,
Def 165, MDef 150, Mag 13, weak Lightning, null Poison, immune Doom / Petrify / Confuse; Guardian graphics + palette as
placeholder. `$185` Suppressor Bit: locked MOB-03 stats; Spit Fire graphics; one Reflect on the Praetor per Bit, then
Battle / Tek Laser. QA twins `$186` / `$187` (formation `$245`, group `$F9`): byte-identical AI, 1/10 HP, attack /
magic / level 1 — **hand QA only**; the locked battle is `$244` (group `$FA`).

## Allocations (permanent, D-21)
`EXP_HOPE_EMPIRE $0E0`, `EXP_CELES_STARTED $0E8`, `EXP_CELES_DONE $0E9`, `EXP_CELES_RECORDS_PRESERVED $0EA`,
`EXP_CELES_RECORDS_CHOSEN $0EB`, `EXP_GRAVES_DONE $0EC`, NPC bit `NPC_CELES_VALE_OUTER $6F0`. Map `$1A2`. Monsters
`$184-$187`. Formations `$244/$245`. Map palette `$30`, sprite palette `$20`. QA event battle groups `$FA` / `$F9`.
