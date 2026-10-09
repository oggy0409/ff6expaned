# FF6 Expanded Edition — TECH v0.8: COMPLETE SIGNATURE EQUIPMENT POPULATION

**STATIC PASS · EMULATOR PASS · USER RUNTIME PASS** — accepted baseline (user runtime QA: all 39 items, equip restrictions / stats, battle / boss graphics, Optimum / Empty / Arrange, save / load, Sell / Colosseum exclusion, smith: PASS). The builder pins the three v0.8 SHA-1s.
Baseline: v0.7.2 production item/equipment engine and v0.7.3 QA harness (both user-runtime accepted).

## Result
All **39 locked signature equipment concepts** are real equipment at ids **`$100-$126`** in the production ROM:
13 weapons (`$100-$10C`), 7 body armor (`$10D-$113`), 4 helmets (`$114-$117`), 2 shields (`$118-$119`), 13 relics
(`$11A-$126`). `$127-$13C` stay reserved; `$13D-$13F` stay QA-only (item-tech ROM only, not moved).

* **Content = data.** Production v0.8 differs from accepted production v0.7.2 in 3453 bytes: the bank-FA extended
  item tables (records, names, flags, descriptions, weapon/Jump animation entries), version byte, checksum, and one
  **engine fix** (below). `PATCH_TABLE_v0.8.md`, `out/DELTA_v0.7.x_to_v0.8.csv`.
* **Engine fix found by the v0.8 stress test** (`ENGINE_FIX_v0.8_B_ACCUMULATOR.md`): with several extended items, the
  Equip list order and **Optimum** could rank items wrongly (Locke's Optimum took Leo's Blade over Ragnarok) because a
  C3 hook left the id high bit in the B accumulator and `SortValidEquip`'s `TAY` used it. Fixed by B := 0 exits in five
  C3 routines (`asm/item_v08`); a static audit of every B-producing hook now reports no reachable leak. No item was
  ever lost or duplicated; frozen v0.7.2/v0.7.3 ROMs keep the accepted engine byte-exact.
* **Single source of truth:** `items/production_v08/equipment.json` (locked name/code/users/stat line verbatim,
  plus every derived value marked in `derived`). The builder composes each 30-byte ItemProp record explicitly from it
  (a vanilla template supplies only icon, block graphic, weapon targeting and animation) and refuses the build on any
  rule violation (`patches/equipment_v08.py`; selftest 46: 13 fail-closed cases).
* **No locked concept invented, renamed, merged, deleted or turned into a key item / consumable; no vanilla id reused.**
  18 locked names longer than the game's 12-character name field use a documented 12-char display form; the locked
  name is kept in the source/tables and shown in the description (`KNOWN_RISKS_v0.8.md` R21).
* **Graphics / animation:** each weapon uses a deliberate vanilla template of the same family (Excalibur, ThiefKnife,
  Partisan, Sky Render, …); never the low-byte alias (no Dirk / Brush alias, no unarmed fallback)
  (`EQUIPMENT_ANIMATION_MAP_v0.8.md`).
* **Relics:** 7 locked optional-ASM effects ship with their BAL-18 stat fallback; no new relic ASM
  (`FALLBACK_EFFECTS_v0.8.md`). Vanilla relic bits are used where the effect exists in vanilla (MP +1/8, +1/4,
  Sketch rate, status immunities, ThiefKnife steal).
* **Acquisition:** one one-time binding per item (`reward_id`, `future_event_symbol`, conditions, GP for the 3 smith
  items). Excluded from shops, Sell, Steal, Drop, Metamorph, Colosseum wager and Throw (Option C engine)
  (`EQUIPMENT_ACQUISITION_MAP_v0.8.md/.json`). Story events that give them are future work.
* **Balance:** every item compared with all vanilla equipment of its slot (`EQUIPMENT_BALANCE_AUDIT_v0.8.md`);
  weapons inside the locked 184-222 envelope; none dominates Illumina / Ragnarok / Paladin Shld / Minerva; Optimum
  keeps Illumina/Ragnarok (emulator L2). No locked value changed; review items listed.

## Outputs
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.8_PRODUCTION.sfc` | `1091d0779c5278f40c6e74648dbfb8cb2ce6818b` | `2F5FB45A` | `942C` | production |
| `FF6X_Rev1_TECH_v0.8_CELES_TECH.sfc` | `e8a96146507f4587f75344f5cea2781ed02e6b72` | `332238AF` | `A757` | production + Celes Annex tech |
| `FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc` | `498d62c47477a91d6df7b4619f76bb03e7a1fbb5` | `4A8A7533` | `F37D` | **user QA ROM** |
| `…PRODUCTION.bps` / `.ips` | `c8fd0d8f…` / `71d13c7f…` | | | patches vs clean Rev 1 |
| `…CELES_TECH.bps` / `.ips` | `a5002e4e…` / `fa5ee5ae…` | | | |
| `…EQUIPMENT_QA.bps` / `.ips` | `39d48bf0…` / `f81949bc…` | | | |

Full list: `HASHES_v0.8.txt`. Frozen accepted baselines are rebuilt byte-exact and asserted by SHA-1:
production v0.7.2 `f8f92c81…`, celes-tech v0.7.2 `2789edb5…`, item-bank QA v0.7.3 `3a784e0d…` (and all older ones).

## Documents
| File | Content |
|---|---|
| `EQUIPMENT_MASTER_TABLE_v0.8.csv/.json/.md` | canonical table: id, symbol, code, locked + display name, category, icon, description, users / equip mask, all stats, elements, status, flags, template / animation, compatibilities, acquisition, uniqueness, fallback, derivations |
| `EQUIP_MATRIX_v0.8.csv` | item × 14 permanent characters (emulator E1 = the game's own lists) |
| `EQUIPMENT_BALANCE_AUDIT_v0.8.md` | vanilla comparison, dominant / dominated, stacking maxima, dangerous combinations |
| `EQUIPMENT_ACQUISITION_MAP_v0.8.md/.json` | reward bindings, smith purchase rules, exclusions |
| `EQUIPMENT_ANIMATION_MAP_v0.8.md` | weapon template, Jump, Runic, two-hand, Bushido, dual-wield |
| `FALLBACK_EFFECTS_v0.8.md` | BAL-18 relic fallbacks |
| `REGRESSION_REPORT_v0.8.md` | static + emulator results |
| `KNOWN_RISKS_v0.8.md` | R1-R32 |
| `ENGINE_FIX_v0.8_B_ACCUMULATOR.md` | engine finding, root cause, fix, static audit (`devtools/b_leak_audit_v08.py`) |
| `PATCH_TABLE_v0.8.md` | delta header + exact patch tables of the three ROMs |
| `USER_QA_TECH_v0.8_VI.md` | the single consolidated user QA guide (~20-30 min) |

## QA harness (item-tech ROM only)
QA tile (Narshe, up 6 / left 4) → `TECH v0.8 QA ACCESS` → `Equipment v0.8 (39 items)`: Grant all 39, 5 party presets
(Terra leads, out of Magitek; presets never re-run `$40` on an initialized character), grant by type, Remove all 39,
test battle, boss battle (Whelk), smith purchase demo (GP check, HAS check, refund when the inventory is full) and
QA GP. Older v0.7/v0.6 tests stay under `Older tests`.

## Build / test
```
python3 build.py "<clean Rev 1>.sfc" --target all --out out
python3 tools/selftest.py "<clean Rev 1>.sfc"
python3 tools/equipment_docs_v08.py "<clean Rev 1>.sfc" .
python3 tools/emu_equip_v08.py        out/FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc out/…EQUIPMENT_QA.manifest.json "<clean Rev 1>.sfc" <dir>
python3 tools/emu_equip_battle_v08.py out/FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc out/…EQUIPMENT_QA.manifest.json <dir>
python3 tools/emu_equip_stress_v08.py out/FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc out/…EQUIPMENT_QA.manifest.json \
        out/FF6X_Rev1_TECH_v0.8_PRODUCTION.sfc "<clean Rev 1>.sfc" <dir>
```

Not implemented (hard stop): the 8 consumables, key item expansion, final Celes quest, enemy art, new relic ASM,
story events placing the items.
