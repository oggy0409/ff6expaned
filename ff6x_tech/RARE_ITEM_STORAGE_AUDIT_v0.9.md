# RARE ITEM STORAGE AUDIT — TECH v0.9

## 1. Vanilla storage (read-only reference)

The vanilla Rare Items list (`GetRareItemList` C3:8394) is built from event bits `$1D0-$1EB` (`$1EBA-$1EBD`, 28 bits;
names for 20 entries at CE:FBA0, 13 bytes each). Rare ids 0-19 are the 20 vanilla rare items (Cider … Pendant). Bits
`$1E4-$1EB` are read by the EN list but have no name / description and no Rev 1 script sets them; they are **not**
used for FF6X rare items (no assumption that they are free).

Observation: the opening sets `$1E3` (Pendant, rare id 19) for Terra — a New Game already owns one vanilla rare item.

## 2. FF6X storage (new, audited free saved RAM)

| bytes | name | content |
|---|---|---|
| `$1E1D-$1E20` | `XRARE` | FF6X rare ids 20-51: bit (id - 20) |
| `$1E21-$1E22` | `XRSIG` | `$52` ('R'), `XRARE0 ^ XRARE1 ^ XRARE2 ^ XRARE3 ^ $A5` |

`$1E1D-$1E3F` was audited free in TECH v0.7.1 (`SAVED_RAM_AUDIT_v0.7.1.md` §2: zero direct accesses, every indexed
table that could reach it ends below `$1E1D`); it lies inside the saved block `$1600-$1FFF`, so it is saved and loaded
with the game. Allocations are recorded in `data/allocations.json` → `saved_ram_allocations` (selftest 51: inside the
audited bytes, no overlap). `$1E23-$1E35` stay free.

Capacity: 20 vanilla + **32 FF6X** = 52 logical rare ids (requirement ≥ 32 FF6X entries). Production defines 5 (20-24),
`XRareDef` (FA:5080) masks the rest; the QA build defines all 32 (fillers 25-51) and proves the capacity at runtime
(emulator R2a / R4c / R5).

## 3. Initialisation, load, migration

| case | result |
|---|---|
| New Game (`XNewGame` → `ClearAll`) | XRARE = 0, XRSIG valid, transient bytes 0 (emulator R1) |
| load, item-bank signature valid (v0.7.1 … v0.9 save) | `RareCheck`: XRSIG valid → XRARE &= XRareDef (undefined ids dropped); XRSIG invalid → XRARE = 0 |
| load, legacy save (Rev 1 / pre-v0.7.1, no item-bank signature) | `ClearAll` → XRARE = 0 |
| v0.7.x / v0.8 save (signature valid, rare block never written) | XRSIG does not match the bytes left there → XRARE = 0 (no phantom; emulator R6b with key-item bits POKEd) |
| Rev 1 save with garbage in `$1E1D-$1E22` | legacy path → cleared (emulator R6a) |
| QA save in the production ROM | QA fillers 25-51 dropped, key items 20-24 kept (emulator R7a) |

The item-bank signature (`XSIG`, `$1D24`, version 1) is **unchanged** by v0.9: a v0.9 save loads in v0.8 (downgrade:
the consumables are undefined there and removed cleanly, the rare block is ignored and survives an upgrade back).

## 4. Event bits

Vanilla rare items 0-19 keep their vanilla bits (`GIVE_RARE 3` = set `$1D3`, emulator R2d). No other event bit changes
(emulator R2b over the full `$1E80-$1EFF` range). One QA-only result switch `$152 QA_V09_HAS_RARE` is allocated for the
QA hub (item-tech only).
