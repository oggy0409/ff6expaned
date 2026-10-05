# Claude Start — TECH v0.6 Enemy Asset + Magic Point Foundation

TECH v0.5 has been gameplay-tested by the user and is ACCEPTED.

One visual issue was observed:
TESTMOB B's bird placeholder looks visually garbled/poor in battle.
Functional monster behavior is otherwise correct.

Do NOT dismiss this as cosmetic without isolating the cause.

## Primary goals

1. Prove a clean scalable enemy graphics/palette asset pipeline for monster IDs above `0x17F`.
2. Fix/extend Magic Point handling for new formations `0x240–0x3FF`.
3. Preserve every accepted v0.1–v0.5 behavior.

---

# Phase A — isolate the TESTMOB B visual issue first

Before adding custom art, build controlled A/B tests.

A1. Reproduce TESTMOB B using:
- exact vanilla Dark Wind graphics resource,
- exact vanilla Dark Wind palette,
- exact vanilla Dark Wind graphics metadata,
- exact width/height/tile arrangement/positioning data.

This should visually match vanilla Dark Wind as closely as possible.

If it does NOT:
- treat this as a graphics router/metadata bug,
- stop custom asset work,
- fix the routing first.

A2. Then change ONLY the palette to the Vulture palette.
This isolates whether the ugly appearance is caused by palette-index mismatch rather than graphics data.

A3. Document:
- graphics index,
- tile-data source,
- tile count,
- tile arrangement,
- width/height metadata,
- horizontal/vertical positioning,
- palette index,
- palette byte data,
- all monster-ID-indexed graphics consumers involved.

Do not call the issue resolved merely because the battle does not crash.

---

# Phase B — custom enemy graphics storage

Create a dedicated production allocation for new enemy graphics and palettes in unused expansion banks
(prefer FB–FE if compatible with the existing allocation plan).

Requirements:
- explicit allocator entries,
- no overlap with F0–F9 modules,
- source-controlled assets,
- deterministic compression/packing if the game format requires it,
- reproducible import from indexed source graphics,
- no editor-only hidden state.

New asset source should separate:
- monster definition,
- graphics data,
- graphics metadata,
- palette data,
- battle dimensions/position.

Do not import final project monster art yet.

---

# Phase C — two QA custom enemy assets

Create two deliberately simple QA graphics assets from source files.

They may be simple geometric/pixel test creatures, but they must be:
- newly stored in expansion space,
- not aliases of vanilla graphics,
- visibly distinct,
- using distinct palettes,
- rendered with correct silhouette and no tile garbage.

Use monster IDs:
- `0x180`
- `0x181`

The QA battle must prove both custom assets load simultaneously.

Required checks:
- correct tile arrangement,
- correct palette,
- no neighboring-ROM data bleed,
- no flicker/corruption when one monster dies,
- no corruption when targeting,
- no corruption after battle,
- no vanilla enemy graphics regression.

---

# Phase D — Magic Point foundation

Current known limitation:
formations >= `0x200` receive 0 Magic Points due vanilla battle-ID logic.

Audit the exact Rev 1 code path and implement a safe production solution for formations
`0x240–0x3FF`.

Requirements:
- vanilla formations retain byte-for-byte equivalent MP behavior,
- new formations can define nonzero Magic Points,
- MP reward must be source-controlled per formation or per battle definition,
- no SRAM/save-format change,
- no Esper-learning regression,
- no accidental MP awards for formations configured as zero.

Create QA proof:
- one new formation with a small nonzero MP reward,
- win battle with an Esper equipped if practical,
- verify MP is actually credited,
- verify a zero-MP new formation still gives zero.

If early-game QA cannot equip an Esper naturally, provide a separate safe QA harness or emulator-side
proof, but user-facing runtime QA should include a practical path if possible.

---

# Phase E — vanilla regression

At minimum:
- compare graphics metadata outputs for all vanilla monster IDs,
- compare palette mapping for all vanilla monster IDs,
- boot/opening battles,
- several different vanilla enemy graphics sizes,
- multi-enemy formations,
- boss/event battle if practical,
- Sketch/Control graphics path regression,
- v0.5 QA battle,
- Celes Annex regression,
- v0.4 map regression,
- save/reset/load.

---

# Capacity report

Return:
- custom enemy graphics capacity in bytes and practical monster count,
- palette capacity,
- graphics metadata capacity,
- max supported graphics size,
- any per-battle VRAM constraints,
- whether large bosses need separate handling,
- remaining free bytes in allocated graphics banks,
- Magic Point capacity for new formations.

State clearly whether the planned roster of 35 normal mobs + all bosses fits comfortably.

---

# Deliverables

Package:
1. `README_TECH_v0.6.md`
2. `USER_QA_TECH_v0.6_VI.md`
3. `ENEMY_GRAPHICS_AUDIT_v0.6.md`
4. `MAGIC_POINT_AUDIT_v0.6.md`
5. updated allocation manifest
6. deterministic builder source
7. source graphics/palette assets for QA monsters
8. monster definitions for `0x180` / `0x181`
9. QA ROM
10. PRODUCTION ROM without QA-only assets/triggers
11. BPS
12. diff manifest
13. exact PC/SNES patch table
14. emulator regression report
15. known risks
16. capacity report
17. hashes

Status must remain separated:
- STATIC PASS / FAIL
- EMULATOR PASS / FAIL
- USER RUNTIME QA PENDING

---

# Do NOT do yet

Do not:
- import final Rust Hound / Annex Guard / Magitek Praetor art,
- rebalance vanilla enemies,
- start final Celes story,
- start item/equipment architecture,
- expand Rage/Veldt,
- change SRAM format.

Stop after packaging TECH v0.6 for review and user QA.
