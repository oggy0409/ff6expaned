# TECH v0.8 — engine finding and fix: extended-id high bit leaking through the B accumulator

**Found by the v0.8 emulator stress test (Optimum with all 39 items + strong vanilla gear). Fixed in the v0.8 targets.
Frozen accepted baselines (production / celes-tech v0.7.2, QA v0.7.3) are unchanged and still byte-exact.**

## Symptom
With several extended items in the inventory, the Equip menu's item list and **Optimum** could rank items wrongly:
Locke's Optimum took Leo's Blade (218) while Ragnarok (255) was available; Edgar took Sandpiercer (210) over Gale Lance
(218); Terra took a Buckler while Genji Shld / Concord Shield were available. No item was lost, duplicated or truncated
(stress L1 passed before the fix); only the choice / list order was wrong.

## Root cause
The C3 hooks that read a 9-bit id return the low byte in A and the extended bit in **B** (the high accumulator byte) for
the following extended-aware lookup (`XC3_LdaInvY` → `XC3_PropPtrB`). The vanilla code after those hooks had B = 0
(`TDC` / `CLR_A` earlier), but the hooks left B = 1 after an extended item.

`SortValidEquip` (C3:A150) builds its sort keys in a loop that does `LDA $7E9D8A,X` (8-bit) then **`TAY`** with 16-bit
index registers, i.e. Y = B:A. After an extended item, Y became `$0100 + slot`, so the next entry's key was read from
`$1869 + $100 + slot` = the **quantity** array and the extension bitmap of an unrelated bit. Measured in the emulator
(Locke's weapon list, before the fix): keys `205, 205, 205, 205, 188, 30, 26` for items whose powers are
`218, 198, 202, 54, 188, 255, 26` (Ragnarok keyed 30 = Mithril Knife's power). After the fix: `255, 218, 202, 198, 188,
54, 26`.

## Fix (asm/item_v08/c3.s; hook sites unchanged)
The routines that end an id chain now return with **B = 0**, exactly as the vanilla path (A low byte and flags as vanilla):
`XC3_PropPtrB`, `XC3_HiM7A`, `XC3_IncQtyB`, `XC3_DecQtyB`, `XC3_EqpName` (+ helper `XC3_ClrB`). No consumer needs the
producer's B after these routines (every later use starts with a new producer — checked hook by hook).

Engine source versioning: `asm/item_v071` (accepted, used by the frozen v0.7.x targets) and `asm/item_v08` (v0.8
targets; identical except these exits in `c3.s`, 15 changed code lines — selftest 43d). Production v0.8 vs v0.7.2
differs only in the FA tables, metadata, checksum, 917 bytes inside the claimed XC3 stub area (the routines after the
first change move) and 70 operand bytes of C3 hook sites re-pointed to them (selftest 43b). C0 / C1 / C2 engine code
and every hook opcode are unchanged.

## Static audit of every B-producing hook (`devtools/b_leak_audit_v08.py`)
Walks the code after each hook that can leave the extended bit in B (both branch paths, into called routines, back into
the real callers), until B is overwritten, and reports every instruction that would consume it (16-bit `TAX/TAY`,
`TCD/TCS`, `XBA` other than the vanilla `XBA/LDA #0/XBA` clear idiom, 16-bit accumulator ops, `PHA` 16-bit).

| Engine | Findings |
|---|---|
| v0.7.1 (accepted v0.7.2 production) | 14: **I402 `SortValidEquip` TAY (the bug above)**; GetValidEquip-family returns reaching a `TAX` at C3:1173 (needs an extended item in the last scanned slot); equipment-name / Optimum tails returning B = 1 |
| v0.8 | 1, unreachable: I304 (Item menu "use") returns through the Megalixir test `CMP #$EF`; an extended id's low byte is `$00-$3F`, never `$EF` |

## Verification
* Emulator: sorted list keys dumped before / after (above); stress **L3** (new): Optimum picks, for every slot, the
  highest attack / defense power among the items the character can equip, extended and vanilla alike; **L2**:
  Terra / Locke take Illumina / Ragnarok over the signature swords.
* All v0.7.1-v0.7.3 item regressions rerun on the fixed engine (`REGRESSION_REPORT_v0.8.md`).

## Impact on the accepted v0.7.2 baseline
The defect exists in the accepted v0.7.2 engine, but production v0.7.2 defines no extended item, so it cannot occur
there. In the v0.7.x QA ROM (one QA item per slot type) an extended entry could mis-key the list entry that followed
it; the v0.7.1 Optimum checks tested duplication / loss, not ranking, so it was not seen. The key computation only
reads memory: nothing is written or corrupted, and saves made with v0.7.2 / v0.7.3 are unaffected.
