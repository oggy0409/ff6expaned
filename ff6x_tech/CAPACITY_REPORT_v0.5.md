# TECH v0.5 — Monster / formation capacity report (production build)

| Item | Capacity after v0.5 | Used by production v0.5 | Free for project content |
|---|---|---|---|
| Max valid monster ID | **$1FE** ($1FF = engine null / empty formation slot) | — | — |
| New monster IDs | $180–$1FE = **127** | 0 (QA build: $180, $181) | 127 |
| Stats (MonsterProp, 32 B) | 512 records, F8:0000–F8:3FFF (16 384 B) | 384 vanilla | 127 |
| Names (10 chars) | 512, F8:4000–F8:53FF | 384 | 127 |
| Special-attack names (10 chars) | 512, F8:5400–F8:67FF | 384 | 127 |
| AI script pointers | 512, F9:0000–F9:03FF | 384 (+ new ids → default empty script) | 127 |
| AI script space | F9:0400–F9:FFFF = **64 512 B** (16-bit offsets, one bank) | 14 674 B (vanilla 14 672 + 2 B default) | **49 838 B** (vanilla average ≈ 38 B/monster) |
| Graphics metadata (MonsterGfxProp, 5 B) | 543 slots: $000–$19F vanilla (monsters + espers/Imp), $1A0–$21E = one slot per new id | 416 | 127 (1:1 with new ids) |
| Palettes | vanilla MonsterPal 768 × 16 B units, referenced by index | highest used index $28F | new monsters can **reuse** any vanilla palette; **new custom palettes not available yet** (needs relocation or audited free units) |
| Graphics tile data | vanilla window E9:7000–ED:6FF8 | — | final art needs a graphics allocation (FB–FE reserved) — next architecture step |
| Loot (steal rare/common, drop rare/common) | 512 × 4 B, F8:6800 | 384 | 127 (item ids 8-bit, ≤ $FE) |
| Control (4 attacks) | 512 × 4 B, F8:7000 | 384 | 127 |
| Sketch (2 attacks) | 512 × 2 B, F8:7800 | 384 | 127 |
| Special animation / sprite overlap | 512 × 1 B each | 384 | 127 |
| Formations | 1024: $000–$23F vanilla, **$240–$3FF = 448 new** (F8:9000 aux, F8:A000 monsters) | 576 | 448 (QA build uses $240) |
| Event battle groups | 256; $9A–$FF unreferenced (`00 00 00 00`) | — | ~102 groups (audit before production use) |
| Rage / Veldt | 256 rage ids (8-bit, SRAM bits) | vanilla | **0 new Rages** (policy: new monsters excluded); new formations never on the Veldt |
| Magic points | battle ids < $200 only | — | formations ≥ $240 award 0 magic points (extension needed for production random encounters) |

## F0–FF bytes (monster module)

| Region | Range | Size | Used | Free |
|---|---|---|---|---|
| Monster/formation tables | F8:0000–F8:DFFF, 11 active sub-regions | 56 320 | 54 955 (QA build: same) | 1 365 inside regions (gfx-prop 357, formation-monsters 1 008) |
| MONX_SPARE_1 / MONX_SPARE_2 | F8:8C00–F8:8FFF, F8:E000–F8:FFFF | 9 216 | 0 (reserved) | 9 216 |
| AI pointers + scripts | F9:0000–F9:FFFF | 65 536 | 15 698 (QA: 15 710) | 49 838 (QA: 49 826) |
| Engine router | F0:1200–F0:1230 (in ENGINE_CODE) | 49 | 49 | — |

## Does the planned roster fit?
**Yes, with comfortable reserve.** 35 new normal mobs + e.g. 15–25 boss/phase IDs = 50–60 of 127 IDs
(≈ 67–77 spare). Formations: 448 new slots. AI: ~49 KB ≈ 390 B for every one of the 127 new IDs, even if every
new monster had a large script. Per-ID tables (stats, names, loot, Control, Sketch, gfx metadata) are
1:1 with IDs, so they never run out before IDs do.

The real remaining constraints are **assets, not IDs**: new palettes and new graphics tile data
(both need their own allocation/loader work before final art), and **magic points** for new
random-encounter formations.
