# Claude Start — TECH v0.5 MONSTER EXPANSION FOUNDATION

TECH v0.4 has been gameplay-tested by the user and is now ACCEPTED.

Do not begin final monster art or full Celes production monsters yet.

The goal of TECH v0.5 is to make the monster system safely scalable for all planned FFVI Expanded Edition mobs and bosses.

---

# Baseline rules

Use ONLY:
- Final Fantasy III (USA) (Rev 1) / FFVI US v1.1
- unheadered clean ROM
- SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`
- CRC32 `C0FA0464`

Preserve all accepted TECH v0.1–v0.4 production infrastructure.

Build from clean ROM every time.

Do not apply US v1.0 patches by raw offset unless explicitly ported and verified for Rev 1.

---

# Design capacity target

Vanilla monster-stat count:
- base stats table `CF:0000`
- record size `0x20`
- count `0x180` = 384

The project needs:
- 35 new normal mobs
- multiple new bosses / boss phases

Target the production monster-ID space:

- keep all vanilla IDs `0x000–0x17F`
- add production IDs beginning at `0x180`
- support through at least `0x1FE`
- reserve `0x1FF` as null/invalid if the engine architecture requires it

This gives enough capacity for the full planned project without another monster-count migration.

Do not permanently replace dozens of vanilla monster IDs.

---

# Phase 1 — complete monster-ID dependency audit

Before implementing the expansion, produce a machine-readable inventory of EVERY structure and code path indexed directly or indirectly by monster ID.

At minimum investigate:

- monster stats
- monster names
- AI/script pointer tables
- graphics index / graphics metadata
- palettes
- sprite dimensions / positioning / vertical offsets
- formations
- encounter packs
- steals
- drops
- Control commands
- Sketch commands
- Rage-related tables and Veldt eligibility
- Metamorph data if monster-indexed
- special animation / formation flags
- boss-death / event-battle assumptions
- hard-coded monster-count loops/bounds
- editor/tool assumptions
- save/SRAM assumptions, if any

For each dependency report:
- vanilla address/table
- record size
- vanilla count
- whether 9-bit monster IDs already work
- whether relocation is needed
- whether widening is needed
- code consumers
- exact Rev 1 patch points
- expected original bytes
- chosen production solution

Do not infer safety from table shape alone.

---

# Rage / Veldt policy

The previous audit found at least some monster-related tables are only 256 entries, including Rage-related data and a vertical-positioning-style table.

Do NOT silently corrupt or alias IDs above 255.

For TECH v0.5:

1. Determine exactly how Rage and Veldt eligibility are indexed.
2. Determine whether expanding Rage above 256 would require:
   - new Rage storage,
   - menu/list changes,
   - Gau learning logic changes,
   - save/SRAM changes,
   - battle command changes.

Unless a clean expansion is trivial, use this initial production policy:

**New Expanded Edition monsters above vanilla range do not create new Gau Rages and do not appear on the Veldt.**

Implement an explicit safe exclusion/fallback rather than relying on accidental truncation.

Document this as a technical policy, not a creative retcon.

Do not change Gau's existing vanilla Rages.

If you find a low-risk clean Rage expansion with no save-format migration, report it separately; do not implement it without approval.

---

# Phase 2 — relocate/expand monster-indexed tables

Relocate affected production tables into the existing F0–FF allocation framework.

Use one authoritative allocation manifest.

Requirements:
- preserve every vanilla entry byte-identically where possible,
- patch known consumers with expected-byte assertions,
- no unclassified global search/replace,
- no overlapping allocations,
- no hidden dependence on old table slack,
- production build must remain deterministic.

All vanilla monsters must continue to behave identically unless explicitly affected by a required engine fix.

---

# Phase 3 — new monster source format

Start source-controlled monster definitions now.

Create a reproducible source structure such as:

`monsters/tech_0180/`
- `monster.json`
- `stats.json`
- `ai.*`
- `graphics.json`
- `palette.json`
- `loot.json`
- `control.json`
- `sketch.json`
- `README.md`

and similarly for `0x181`.

Exact file names may differ, but the builder project—not an editor-modified ROM—must remain the source of truth.

---

# Phase 4 — two real >383 proof monsters

Create TWO QA-only test monsters:

- monster ID `0x180`
- monster ID `0x181`

Requirements:

## Monster 0x180
- unique test name
- distinct stats
- placeholder vanilla graphic reused safely
- explicit palette mapping
- simple custom AI stored in expansion space
- defined steal/drop
- defined Control/Sketch fallback or valid entries
- explicit Veldt/Rage exclusion

## Monster 0x181
- different unique test name
- different stats
- different placeholder graphic OR palette
- different simple custom AI
- defined steal/drop
- defined Control/Sketch fallback or valid entries
- explicit Veldt/Rage exclusion

The two must coexist in the SAME battle formation at least once so the formation loader proves 9-bit monster IDs work independently.

Do not use final Rust Hound / Annex Guard / Magitek Praetor art or balance yet.

Names can be obvious QA labels, e.g.:
- `TESTMOB A`
- `TESTMOB B`

---

# Formation / battle proof

Create a QA-only event battle reachable from the existing QA harness or another clean early-game QA trigger.

The battle must prove:

1. both new IDs > `0x17F` load,
2. both names render correctly,
3. correct graphics/palette are used,
4. stats differ as defined,
5. AI differs as defined,
6. targeting works,
7. victory works,
8. battle return works,
9. steal/drop paths do not corrupt data,
10. Control/Sketch path is safe if those commands can reasonably be tested,
11. save/reset/load after the event does not corrupt state,
12. vanilla battles remain unaffected.

If early-game party strength is an issue, tune QA stats low.
Do not modify production difficulty for the test.

---

# Graphics policy for TECH v0.5

Reuse vanilla enemy graphics.

Do not create final custom pixel art yet.

The goal is engine capacity, not asset production.

However, the source definition must already separate:
- monster ID
- graphics resource
- palette resource
- battle position/dimensions

so final custom graphics can replace placeholders later without changing monster IDs.

---

# AI policy

Store new QA AI scripts in expansion space.

Prove that new monsters can point to new AI without overwriting vanilla AI.

Use deliberately obvious behaviors, for example:
- TESTMOB A: basic physical attack + occasional Fire
- TESTMOB B: basic physical attack + occasional Slow

Do not make the QA battle dangerous.

---

# Vanilla regression

Run a broad emulator regression after the monster-table relocation.

At minimum:
- opening Narshe battles,
- several different vanilla formations,
- boss/event battle if practical,
- enemy names,
- steals/drops,
- Sketch/Control code paths if practical,
- menu and save/load,
- Celes Annex v0.4 regression,
- new map pipeline regression.

Where automation allows, compare vanilla monster table outputs before/after for ALL vanilla IDs.

A strong goal:
all vanilla monster definitions `0x000–0x17F` deserialize identically from the new production tables.

---

# Capacity report

Return exact practical production capacity after v0.5:

- max valid monster ID
- number of new usable monster IDs
- monster-stat capacity
- name capacity
- AI capacity
- graphics metadata capacity
- palette capacity
- loot capacity
- Control capacity
- Sketch capacity
- formation capacity implications
- Rage/Veldt policy/capacity
- remaining F0–FF bytes used/free by monster module

Also state whether the current creative roster of 35 normal mobs + planned bosses fits with comfortable reserve.

---

# Deliverables

Package:

1. `README_TECH_v0.5.md`
2. `USER_QA_TECH_v0.5_VI.md`
3. `MONSTER_DEPENDENCY_AUDIT_v0.5.md`
4. machine-readable monster dependency table
5. updated allocation manifest
6. deterministic builder source
7. monster source definitions for `0x180` and `0x181`
8. formation source
9. QA-access ROM
10. PRODUCTION ROM without QA content
11. BPS (and IPS if practical)
12. diff manifest
13. exact PC/SNES patch table
14. emulator regression report
15. known risks
16. capacity report
17. hashes

State separately:
- STATIC PASS / FAIL
- EMULATOR PASS / FAIL
- USER RUNTIME QA PENDING

Do not claim runtime acceptance until the user tests it.

---

# Do NOT do in TECH v0.5

Do not:
- import final monster art,
- implement Rust Hound / Annex Guard / Magitek Praetor as final production content,
- rebalance vanilla monsters,
- add new Gau Rages unless explicitly approved,
- change save/SRAM format just for Rage,
- start final item architecture,
- import full Celes story,
- start another character arc.

Stop after packaging TECH v0.5 for review and user QA.
