# TECH v0.7.1 — save compatibility

## Design (NEXT_TASK §2)

* The SRAM slot size and layout are **unchanged** (`$1600-$1FFF` copy + vanilla checksum). The extension metadata
  lives inside the slot at `$1CF8-$1D27` (see `SAVED_RAM_AUDIT_v0.7.1.md`), so it is saved, checksummed and loaded
  by the vanilla code with no change.
* Signature/version `58 49 01 FE` at `$1D24-$1D27`.
* Every load path runs `XSanitize` (FA, `asm/item_v071/core.s`) after the vanilla copy has been accepted:
  title → Continue (I222, C3:29EB) and game-over restart (I221, C3:150E, after the checksum passed).
* New Game writes zero metadata + signature (I220).

## `XSanitize` rules

| Case | Detection | Action |
|---|---|---|
| Legacy save (vanilla Rev 1 or any pre-v0.7.1 FF6X build) | `$1D24-$1D27` ≠ `58 49 01 FE` (a vanilla save holds `A5 9A A6 FF`, the Bushido-name copy) | clear all 44 metadata bytes, write the signature. **Vanilla bytes untouched**: every inventory/equipment byte keeps its vanilla meaning, so `$3D` stays Chocobo Brsh. Zero phantom extended items. |
| Synthetic garbage without signature | same | same: zero extended items/equipment |
| Valid signature, inventory bit set on an empty slot (`$FF`) | per bit | stale bit cleared |
| Valid signature, inventory bit set on an id whose `XExtFlags` bit 0 is 0 (not defined in this ROM) | per bit | item **removed** (`$FF`, qty 0) and bit cleared — never truncated to the vanilla id with the same low byte |
| Valid signature, equipment bit set on `$FF` | per bit | bit cleared |
| Valid signature, equipment bit on an undefined id | per bit | slot := `$FF`, bit cleared |
| Valid signature, defined ids | — | loaded as saved |

The undefined-id rule is what makes a QA save safe in the production ROM (production defines no extended ids).

## Emulator evidence (Claude-side, snes9x via stable-retro — not user runtime)

`tools/emu_item_qa.py` → `ITEM_QA_EMULATOR_REPORT.json` (33/33 PASS) on the final build:

| Check | Result |
|---|---|
| A0 New Game writes signature, metadata zero | PASS |
| J- / J0 pre-save state: `$13D` equipped **and** `$13D/$13F` in the inventory; saved slot carries signature and bits | PASS |
| J1 save → new emulator process (power cycle) → title Continue → slot 1: inventory (9-bit ids + qty), equipment and bits identical | PASS |
| L1 the same slot with `$1CF8-$1D27` replaced by deterministic non-zero garbage and no signature (checksum recomputed): **zero** extended items/equipment, signature written | PASS |
| L2 every other vanilla byte of that slot preserved (excluding the character records / volatile event area that gameplay changes after load) | PASS |
| L3 a save made by the **clean Rev 1 ROM** holds the Bushido-name bytes (`…FE 92 A5 9A A6 FF`) | PASS |
| L4 that vanilla Rev 1 save loaded in v0.7.1: zero phantom items; Chocobo/DaVinci/Magical Brsh (`$3D/$3E/$3F`) stay vanilla | PASS |
| P1 the v0.7.1 QA save loaded in the **production** ROM: extended items/equipment removed (not truncated to `$3D-$3F`), vanilla inventory exactly the pre-save vanilla part, metadata zero | PASS |

## Downgrade (v0.7.1 save → older ROM)

An older ROM ignores `$1CF8-$1D27`; extended items would appear as their low-byte vanilla aliases
(e.g. QA Blade13D → Chocobo Brsh). This is a one-way upgrade: see `KNOWN_RISKS_v0.7.1.md` R1.

## Status

STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING (steps J and L in `USER_QA_TECH_v0.7.1_VI.md`).
