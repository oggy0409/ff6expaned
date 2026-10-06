# FF6 Expanded Edition — TECH v0.9: CONSUMABLE + RARE / KEY ITEM EXPANSION

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING** (one consolidated user pass: `USER_QA_TECH_v0.9_VI.md`).
Baseline: accepted TECH v0.8 (39 signature equipment, user runtime PASS) — its three ROMs are rebuilt byte-exact by the
builder as frozen targets (`production-v0.8`, `celes-tech-v0.8`, `item-tech-v0.8`, SHA-1 asserted).

## 0. Sources

The original Creative Lock / Tech Gate spreadsheets are **not in the project**. Locked and used verbatim
(`ITEM_ARCHITECTURE_DECISION_v0.7.md` §2): the 8 consumable names and "some are sold in rebuilt shops"; the 5 key-item
names. Every other value is **DERIVED** and recorded per item in the source (`derived` lists) — the identity / function
of every item was clear from its name, so nothing blocked; derived values need creative confirmation
(`KNOWN_RISKS_v0.9.md` R33). The 39 v0.8 equipment items are unchanged (records byte-identical, selftest 47).

## 1. Result

**A. 8 consumables `$127-$12E`** (`items/production_v09/consumables.json`, validated by `patches/consumables_v09.py`;
`$12F-$13C` reserve, `$13D-$13F` QA-only, unchanged):

| id | name | use | effect (record, run by the vanilla item code) | shop |
|---|---|---|---|---|
| $127 | Gaia Tonic | battle + field | party HP (power 240: ~120 each in battle; 240 on one member in the field) | 1500 |
| $128 | Aether Flask | battle + field | MP +250 | — |
| $129 | Phoenix Ash | battle + field | revive + 8/16 max HP | — |
| $12A | Null Dust | battle | removes Regen/Haste/Shell/Safe/Reflect/Float from one target | 800 |
| $12B | Iron Ration | battle + field | HP +200, cures Poison | 250 |
| $12C | Remedy+ | battle + field | cures Blind/Zombie/Poison/Imp/Petrify/Condemned/Mute/Berserk/Muddle/Sap/Sleep/Slow/Stop | 3000 |
| $12D | Beacon Flare | battle | Fire damage to all enemies (power 255) | — |
| $12E | Magitek Cell | battle | party MP (power 120: ~60 each) | — |

Real consumables everywhere: field Item menu (name, blank icon, description, quantity, usable colour, use, target,
effect, decrement, unusable state, Arrange), battle Item command (list, targeting, extended name window, animation,
effect, decrement on command, held-item return, battle-end reconciliation), save / load / legacy. **Extended shop
layer** (relocated `XShopProp`, shops `$80` / `$81`, no truncation), **Sell** for the 4 sold consumables (½ price),
never stealable / dropped / Metamorph / Colosseum / Throw / equippable / enemy-used.
→ `CONSUMABLE_MASTER_TABLE_v0.9.{md,csv,json}`, `CONSUMABLE_BALANCE_AUDIT_v0.9.md`,
`CONSUMABLE_ACQUISITION_MAP_v0.9.{md,json}`, `CONSUMABLE_ENGINE_AUDIT_v0.9.md`, `EXTENDED_SHOP_AUDIT_v0.9.md`.

**B. Rare / key items — capacity 52 logical rare ids (20 vanilla + 32 FF6X)**. Source registry
`items/production_v09/rare_items.json`: KI-01 Darill's Token (20), KI-02 Concord Sigil (21), KI-03 Cinder Sigil (22),
KI-04 Triune Sigil (23, prerequisite both sigils), KI-05 Broken Seal (24), each with arc / acquisition / prerequisite /
one-time / consumption / ending dependency / event symbol, no combat stats. Storage `XRARE` `$1E1D-$1E20` + signature
`XRSIG` (audited free saved RAM). Rare Items menu: 20 per page, Down/Up at the edge and R/L turn the page. Event API
`$69 GIVE_RARE` / `$6D TAKE_RARE` / `$6E HAS_RARE` for all 52 ids. QA build fills ids 25-51 to prove the capacity.
→ `RARE_ITEM_MASTER_TABLE_v0.9.{md,json}`, `RARE_ITEM_STORAGE_AUDIT_v0.9.md`, `RARE_ITEM_UI_AUDIT_v0.9.md`,
`RARE_ITEM_EVENT_API_v0.9.md`, `RARE_ITEM_ACQUISITION_MAP_v0.9.{md,json}`.

**C. Saves.** Item-bank format unchanged (version 1): Rev 1 / v0.7.x / v0.8 saves load with nothing cleared; the rare
block has its own signature (no phantom). → `SAVE_MIGRATION_v0.9.md`.

**D. QA hub** (QA ROM only): `Consumables v0.9`, `Rare items v0.9`, `More… → Stress / save`, v0.8 equipment tools,
older tests, Save Point.

## 2. Engine

`asm/item_v09` = the accepted v0.8 engine + `v09.s` and new stubs; 57 new hook sites (`patches/item_v09_hooks.py`, Rev 1
bytes asserted) + 2 replaced Sell routines; all in the existing ITEMX regions / stub claims. Three defects were found
by the emulator suites and fixed before packaging (`CONSUMABLE_ENGINE_AUDIT_v0.9.md` §6). Static B-accumulator audit:
only the known unreachable v0.8 finding. Full byte delta: `PATCH_TABLE_v0.9.md`, `out/DELTA_v0.8_to_v0.9.csv`.

## 3. Outputs

See `HASHES_v0.9.txt` (ROM / BPS / IPS / manifest SHA-1s). QA ROM for the user pass:
`FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc`; production `FF6X_Rev1_TECH_v0.9_PRODUCTION.sfc`; celes-tech
`FF6X_Rev1_TECH_v0.9_CELES_TECH.sfc`.

## 4. Test status

* STATIC: builder (all targets, frozen hashes asserted) + `tools/selftest.py` (all self-tests PASS, incl. v0.9 47-51).
* EMULATOR (snes9x): consumables, battle, rare items, stress / migration + every v0.7.1 / v0.8 / v0.6.1 / Celes /
  Colosseum suite rerun on the v0.9 ROMs → `REGRESSION_REPORT_v0.9.md`.
* USER RUNTIME QA: **pending** (`USER_QA_TECH_v0.9_VI.md`).

## 5. Build / test

```
python3 build.py "<clean Rev 1>.sfc" --target all --out out
python3 tools/selftest.py "<clean Rev 1>.sfc"
python3 tools/consumable_docs_v09.py "<clean Rev 1>.sfc" .
python3 tools/emu_cons_v09.py        out/<QA>.sfc out/<QA>.manifest.json "<clean Rev 1>.sfc" <dir>
python3 tools/emu_cons_battle_v09.py out/<QA>.sfc out/<QA>.manifest.json <dir>
python3 tools/emu_rare_v09.py        out/<QA>.sfc out/<QA>.manifest.json out/<PRODUCTION>.sfc "<clean Rev 1>.sfc" <dir>
python3 tools/emu_stress_v09.py      out "<clean Rev 1>.sfc" <dir>
```

Not implemented (hard stop): final Celes quest, Terra / Cyan / Shadow / Figaro / Setzer arcs, enemy art, map
production, special relic ASM, story events placing the items, post-Kefka content.
