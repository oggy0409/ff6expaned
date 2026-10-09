# Claude Phase 3 Start — FFVI Expanded Edition
## TECH v0.3 — Celes “Echoes of the Empire” Technical Vertical Slice

TECH v0.2 has now been runtime-tested by the user and is ACCEPTED.

Promote the accepted event/dialogue expansion mechanism into the production branch, but remove all temporary EVTEST content from production.

Do NOT start full story implementation yet.

---

# Baseline

Use ONLY the clean unheadered:

- Final Fantasy III (USA) (Rev 1) / FFVI US v1.1
- SHA-1: `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`
- CRC32: `C0FA0464`

Build from clean ROM every time.

---

# Accepted technical foundations

## TECH v0.1
- 4 MiB ROM expansion accepted at runtime.
- F0-bank runtime data reads accepted.

## TECH v0.2
- expansion-bank dialogue accepted at runtime.
- event bridge/hook accepted at runtime.
- persistent event-bit behavior accepted through save/reset/load.
- return to vanilla control accepted.

Keep the engineering, discard the temporary test presentation.

---

# Phase 3 objective

Build ONE minimal, complete playable pipeline for:

**Celes — Echoes of the Empire**

This is a TECHNICAL vertical slice, not the final arc.

The purpose is to prove:

`vanilla WoR -> new map -> NPC -> expanded dialogue -> persistent production flag -> battle -> reward -> exit -> save/load -> vanilla WoR`

All final artwork, final enemies, final rewards and full dialogue remain deferred.

---

# Map requirement

Prefer physical map ID:

`$0C7`

unless your completed Rev 1 map audit provides a documented technical reason to use another verified-safe map.

For this build, create a small functional Annex test map.

Recommended size:
- approximately 32x32 or 48x32 tiles
- no need for final production dimensions

Minimum layout:

1. entrance
2. short corridor
3. NPC interaction area
4. event-trigger area
5. battle room
6. reward point
7. clean exit

Placeholder/reused vanilla tiles are allowed.

The test map must have:
- correct walkability
- no softlocks
- no out-of-bounds walkable tiles
- working entry/exit coordinates
- stable camera behavior
- correct save/load position behavior if saved inside the map, if the engine permits

Do NOT spend time on final map art yet.

---

# NPC requirement

Add one test NPC representing the future Vale role.

Placeholder vanilla sprite/palette is allowed.

Required:
- production NPC entry
- talk event
- visibility controlled by a newly allocated production flag/state
- no use of TECH_TEST bit `$0FF`

Document:
- map ID
- NPC index
- sprite/palette
- coordinates
- facing
- event pointer
- visibility bit/condition

---

# Dialogue requirement

Use the accepted expanded-dialogue system.

Add a short TECH v0.3 chain, for example:

1. intro line proving expanded-bank dialogue
2. state-dependent follow-up after the event flag is set
3. one vanilla dialogue call afterward if useful for regression proof

Do not import the final Celes script yet.

Document:
- dialogue IDs
- pointer format
- storage bank/address
- hook/trampoline path

---

# Event-bit requirement

Use one REAL production event bit from the audited safe allocation.

Rules:
- `$0FF` is permanently reserved for TECH_TEST and must never be reused.
- allocate the chosen bit in the authoritative allocation manifest
- give it a symbolic name
- document default state
- test set / test / persistence
- verify no vanilla reference conflicts

Suggested semantic name:

`CELES_ANNEX_TECH_COMPLETE`

The exact numeric bit is yours to assign from the approved safe pool.

---

# Battle requirement

Trigger exactly one battle from the new map/event.

For TECH v0.3:
- use a vanilla enemy/formation as placeholder
- do NOT implement Magitek Praetor yet
- do NOT modify monster architecture yet just for this test

Required:
- battle begins correctly
- victory returns to the correct map position/state
- event does not retrigger infinitely
- running/defeat behavior is documented
- no corruption of vanilla encounter/battle data

---

# Reward requirement

Use a vanilla placeholder reward.

Do NOT implement Runic Crest yet.
Do NOT choose the final item architecture yet.

Required:
- reward occurs once only
- save/reset/load preserves already-obtained state
- repeated interaction does not duplicate reward

Document exact placeholder item and why it was selected.

---

# Exit requirement

The player must cleanly return to normal World of Ruin flow.

Acceptance:
- no stuck controls
- no black screen
- no invalid party state
- no broken world-map/Falcon state
- map can be re-entered or correctly locked according to the temporary test design

---

# Source-controlled map package

Start the production map-source format now.

Create a folder similar to:

`maps/celes_annex_tech/`

with source-of-truth files such as:

- `map.json`
- `layout_l1.*`
- `layout_l2.*`
- `layout_l3.*` if used
- `tile_properties.*`
- `npcs.json`
- `triggers.json`
- `exits.json`
- `encounters.json`
- `README.md`
- preview image if practical

Do not make FF6Tools-edited ROM data the only source of truth.

If your exact internal representation differs, keep the same principle:
all map components must be reproducible from files in the builder project.

---

# Production builder rules

Continue enforcing:

- clean Rev 1 hash guard
- expected-byte assertions
- no in-place master-ROM editing
- allocation collision detection
- diff manifest
- PC + SNES offsets
- checksum update
- SHA-1 / CRC32 output
- static vs runtime status separation
- deterministic rebuild

Every new F0–FF allocation must be added to the authoritative allocation manifest.

---

# Regression tests

At minimum, test statically/emulator-side:

1. boot
2. vanilla opening dialogue
3. normal menu
4. at least one normal battle
5. enter new map
6. NPC dialogue
7. flag transition
8. battle trigger
9. victory return
10. reward once
11. exit to vanilla flow
12. save/reset/load
13. re-enter / re-talk behavior
14. several unrelated vanilla NPC dialogues through the global dialogue hook

Do not mark runtime PASS yourself unless the user gameplay-tests it.

---

# Deliverables

Return one self-contained package containing:

1. `README_TECH_v0.3.md`
2. `USER_QA_TECH_v0.3_VI.md`
3. deterministic builder source
4. allocation manifest
5. map source package
6. event/NPC/dialogue source data
7. output SFC
8. BPS and/or IPS patch
9. diff CSV/JSON
10. build manifest with hashes
11. exact PC/SNES patch table
12. regression test report
13. known-risk report

State clearly:

- STATIC PASS / FAIL
- EMULATOR SMOKE PASS / FAIL
- RUNTIME USER QA PENDING

---

# Do NOT do yet

Do not:
- import the final Celes dialogue
- draw final Annex art
- implement Magitek Praetor
- implement Runic Crest
- expand monster count
- choose the final 39-item architecture
- start Terra/Cyan/Shadow/Setzer/Forgotten Age/Vael arcs
- alter Creative Lock content

If you discover a technical conflict, report it before changing the design.

---

# After TECH v0.3 user PASS

Stop and return the package.

The next project decision will be:
1. lock the production map/event pipeline,
2. begin final Celes map art + real scene scripting,
3. separately continue monster and item architecture work.

Do not skip this acceptance gate.
