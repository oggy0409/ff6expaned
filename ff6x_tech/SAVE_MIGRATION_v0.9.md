# SAVE MIGRATION — TECH v0.9

## 1. Save format

| block | bytes | since | v0.9 change |
|---|---|---|---|
| vanilla item ids / quantities | `$1869-$1A68` | Rev 1 | none |
| extended item high bits `XBITS` | `$1CF8-$1D23` | v0.7.1 | none (consumables use the same bits) |
| item-bank signature `XSIG` | `$1D24-$1D27` = `58 49 01 FE` | v0.7.1 | **none (format version 1 kept)** |
| FF6X rare items `XRARE` + `XRSIG` | `$1E1D-$1E22` | **v0.9** | new block with its own signature |
| transient context bytes | `$1E36-$1E3F` | v0.7.1 / v0.9 | cleared at load |

Keeping the item-bank format version means **no migration step rewrites or clears any existing metadata**: a v0.7.x or
v0.8 save is a valid v0.9 save. Load sanitisation (`XSanitize`, unchanged rules) only drops an extended id that the ROM
does not define (never truncating it to its vanilla alias) and stale bits on empty slots. The rare block is validated
separately (signature / defined ids).

## 2. Paths (emulator evidence, `tools/emu_stress_v09.py`, `tools/emu_rare_v09.py`)

| from | to | result | test |
|---|---|---|---|
| genuine Rev 1 save (katanas $27-$2E + Potions) | v0.9 QA | inventory unchanged; katanas stay katanas; no phantom consumable / rare item | J1 |
| Rev 1 save with garbage in `$1E1D-$1E22` | v0.9 QA | no phantom rare item (legacy path clears the extended metadata) | R6a |
| TECH v0.7.3 QA save (QA equipment `$13D-$13F`) | v0.9 QA | kept | K1 |
| TECH v0.8 QA save (20 equipment in the inventory, 19 worn) | v0.9 QA and v0.9 PRODUCTION | every item and every worn slot kept — **FF6X metadata not cleared** | L1 |
| v0.8 save with rare bits but no valid rare signature | v0.9 QA | no phantom rare item | R6b |
| v0.9 save (equipment + consumables + rare) | v0.9 QA after power cycle | identical inventory, worn gear, rare items, bitmaps | H1, R5 |
| v0.9 QA save | v0.9 PRODUCTION | everything defined in production kept (QA fillers dropped) | I1, R7a |
| v0.9 save | accepted **v0.8** PRODUCTION (downgrade, informative) | consumables removed cleanly (undefined in v0.8, never shown as katanas), equipment kept, rare block ignored | M1 |

## 3. Notes

* New Game in v0.9: item bank cleared + signed, rare block cleared + signed, transient bytes 0.
* The accepted v0.7.2 / v0.7.3 / v0.8 ROMs are unchanged (frozen targets, SHA-1 asserted by the builder).
* Downgrading loses the consumables (the older ROM has no definition for them); upgrading again does not restore
  them. Not a supported path; listed for completeness.
