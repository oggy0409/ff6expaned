# CONTENT v1.0 — IMPLEMENTATION PLAN (PROPOSED)

**Status: PROPOSAL. Nothing here has started.** It waits for your approval of the decisions in `CREATIVE_SOURCE_RECOVERY_v1.0.md` §7.
**Baseline:** TECH v0.9 ACCEPTED / USER RUNTIME PASS. The 3 v0.9 targets and the 21 frozen targets stay pinned and SHA-1-asserted in every build.
**Rules carried forward:** build only from clean Rev 1; one allocation manifest; assert original bytes; new hash-pinned targets only; STATIC / EMULATOR / USER RUNTIME kept separate; no user-runtime claim without you; builder sources are the source of truth; production content follows the Creative Lock (CL §8 change control).

---

## 0. Sequence at a glance

| Step | Name | ROM change | Depends on | Output |
|---|---|---|---|---|
| G0 | Creative Source Recovery gate (**done, this delivery**) | none | — | recovery report, cross-check, Celes spec, this plan |
| G1 | **Design sign-off** | none | your answers to D-01…D-25 | `DESIGN_DECISIONS_v1.0.md` (+ v1.3 narrative note if D-03/D-12 add text) |
| M1 | **TECH v0.9.1 — ITEM DATA ALIGNMENT** | yes, data | G1 (A-decisions) | consumables, shops, relic fallback and descriptions aligned to the lock; new pinned targets |
| M2 | **TECH v0.9.2 — CELES ENABLERS** (feasibility proofs) | yes, QA targets only | G1 (B-decisions) | world-map landing, Praetor phase mechanics, party-conditional events, formation layout |
| M3 | **CELES ROM SCRIPT PASS** | none (text files only) | G1, M2 | box-split script, speaker-fallback table, byte budget, for your review |
| M4 | **CONTENT v1.0 — Celes "Echoes of the Empire"** | yes | M1-M3 | playable arc in production; user QA package |

M1 and M2 are independent and can run in parallel after G1. M3 needs only G1, but uses M2 results for event constraints.

## 1. G1 — Design sign-off (no ROM change)

Answer the register. Blocking for Celes: **D-01, D-03, D-05, D-06, D-07, D-11, D-12, D-13, D-14, D-21, D-22**. Blocking for M1: **D-02, D-15, D-16, D-17, D-18, D-19**. The rest can follow later. For each answer that changes or adds creative content (D-03, D-12, possibly D-09), I write a short versioned design note in your change-control format (row changed, why, dependents, version, changelog). I do not edit the Design Pack files themselves.

**Exit criteria:** every blocking decision has an answer.

## 2. M1 — TECH v0.9.1 ITEM DATA ALIGNMENT (proposed scope)

**Goal:** make the ROM item data match the lock *before* any story event places those items.

| Work item | Source change | Engine change | Proof |
|---|---|---|---|
| Aether Flask power 250 → 100 | `consumables.json` | none | static + emulator MP delta |
| Null Dust: vanilla Dispel mask (12 statuses) | `consumables.json` | none | emulator: strips Vanish/Image/Slow/Stop/Life 3 too |
| Remedy+: Remedy set + Zombie; not sold; rarity rare | `consumables.json`, `ext_shops.json` | none | emulator per status |
| Gaia Tonic: ONE_ALLY + Regen + chosen heal (D-16) | `consumables.json`; **validator: allow status-set** | possibly item-power ASM (only if D-16 = b) | **feasibility probe first**: one record healing + setting Regen in battle and field |
| Iron Ration: chosen heal (D-16); Poison cure only if approved | `consumables.json` | as above | emulator |
| Beacon Flare: + reveal (D-17) | `consumables.json` | only if one record cannot damage + remove status | feasibility probe |
| Magitek Cell: damage item per D-17; description; anim | `consumables.json` | none expected | emulator damage / element |
| Extended shops → Rebuilt Mobliz `$80`, Narshe Forge `$81`, Rebuilt Doma `$82`, Figaro Foundry `$83` (contents per MB §19 + D-18 prices) | `ext_shops.json` | none (XShopProp is 144 entries) | QA hub shop labels |
| Darill's Coin Mag +2 (if D-19) | `equipment.json` | none | static |
| Triune Sigil description; Magister Rod description (optional) | `rare_items.json`, `equipment.json` | none | static (width check) |
| Source metadata: key-item sources/arcs, Sandpiercer, Magister Robe, Gaia Tonic ×3, Magitek Cell shop binding | JSON metadata | none | validator |

* **Targets:** new `item-tech-v0.9.1` QA + `production-v0.9.1` + `celes-tech-v0.9.1`, all hash-pinned; v0.9 stays frozen.
* **Save compatibility:** item ids are unchanged, so `XSIG` format 1 stays and v0.9 saves load as-is (re-checked by the stress suite).
* **QA:** STATIC (validators, selftest additions), EMULATOR (consumable suites updated), USER RUNTIME (short VI checklist: consumables + shops only).
* **Size estimate:** small. It is a data change plus up to 2 feasibility probes. The only risk is D-16 option (b) (ASM).

## 3. M2 — TECH v0.9.2 CELES ENABLERS (feasibility proofs, QA targets only)

The Celes arc needs engine behaviour that TECH v0.1-v0.9 never proved:

| # | Capability | Why Celes needs it | Proof target |
|---|---|---|---|
| E1 | **WoR world-map landing point** that loads a new map (+ return to the Falcon) | MB §4: "new landing point south-east of Kefka's Tower debris field". The v0.3 slice is reached only via a Falcon-interior QA trigger | emulator: land, enter, exit, save/load on the world map |
| E2 | **Mid-battle add of 2 hidden monsters** at an HP threshold (Praetor 70%) with an L/XL boss sprite | Suppressor Bits | formation_safety + VRAM check (F3/F4), emulator |
| E3 | **Boss phase swap** (Praetor 40% overload: −Defense, +Haste) | no vanilla AI command lowers Defense, so a monster swap is likely | emulator; risk **F5** (transforming bosses) closed for this boss |
| E4 | **Counted element-hit counter** (3 Lightning hits → Grounding Field: Lightning null for 3 turns) | Praetor AI | emulator; fallback = swap to a Lightning-null variant |
| E5 | **Party-member-conditional event branches** + speaker fallback | IF TERRA / CYAN / SHADOW; Locke/Edgar/Sabin lines | emulator, several party compositions |
| E6 | **Map tile/palette variants for the Imperial Ruins family** (PAL-01) on vanilla tilesets | MB §24 "reuse tilesets aggressively" | build + screenshots |
| E7 | **NPC palette variant** (Vale, memorial worker) | NPC-01/NPC-04 | emulator screenshot |
| E8 | **Persistent world-state swap on an outer map** (memorial / archive states) | MB §20, C-05 | extends the v0.4 persistent map state proof |
| E9 | Formation rules: **front attacks only** for all Celes formations; Praetor + 2 Bits layout inside the visible field | F2 / F1 | `formation_safety` ERROR-free |

* **Output:** QA-only targets (e.g. `celes-enablers-v0.9.2`). Production stays at v0.9 (or v0.9.1).
* **Exit criteria:** E1-E9 STATIC + EMULATOR PASS. **USER RUNTIME** for E1 and E2/E3 (you play the landing and a QA Praetor prototype).

## 4. M3 — CELES ROM SCRIPT PASS (text only, no ROM)

This follows NP "Next narrative pass after technical audit" and your translation-workflow habit: meaning and voice before literal wording, keep a glossary and voice guide, and treat AI output as a draft for human review.

1. Assign stable scene IDs (B01-B14 + NPC states + Graves quest).
2. Merge SS v1.0 + NP v1.1 in Arc_Beat_Lock order (resolutions per D-02/C-xx).
3. Split into FFVI boxes (≤4 lines, 219 px line width with the ROM font, the builder's existing check), apply name/control tokens, and measure bytes.
4. **Speaker-fallback table** (D-11) for every Locke/Edgar/Sabin line.
5. **Cut-first list** to reach the D-13 target, with every cut marked so you can veto it. Only edits CL §3 allows (limits, redundancy, polish), no plot/motive change.
6. Glossary (Annex, C-07, K-01, Vale, Praetor, names) + Voice_Bible check per line.

**Deliverable:** `CELES_ROM_SCRIPT_v1.0.md` + `.json` (the `dialogue.json` input format), **for your approval before insertion**.

## 5. M4 — CONTENT v1.0: Celes "Echoes of the Empire"

### 5.1 Scope (per `CELES_PRODUCTION_SPEC_v1.0.md`)

| Area | Content |
|---|---|
| Maps | world-map landing; MAP-01 Outer Ward (+ shelter, upper stores room, memorial/archive states); MAP-02 Annex B2 (observation corridor, terminal alcove, Names room); MAP-03 Infusion Theater (boss door); MAP-04 Records Vault (incinerator, exit); Falcon deck scene on the vanilla map |
| Monsters | Rust Hound, Annex Guard, Suppressor Bit, Failed Infused (WB Mobs stats); Magitek Praetor (MB §4) + overload variant (if E3 = swap) |
| Formations | 4-5 types per dungeon family (approved list, D-23), front only, plus the boss formation |
| Events | 14 beats, records choice, rewards, NPC states (before / after-Preserve / after-Burn), Falcon debrief, airship bark; optional *Graves Without Names* (D-08) |
| Rewards | Runic Crest (Praetor, fallback), Imperial Saber (Annex chest), Leo's Blade (per D-03), Memorial Band (if D-08), medical supplies (D-10); Hope: Empire |
| Flags | `EXP_CELES_STARTED/DONE/RECORDS_PRESERVED`, Empire hope bit, ~15 beat bits, ~10 NPC bits, **allocated in `data/allocations.json` after D-21** |
| Text | approved M3 script into `DIALOGUE_TEXT` (F3/F4; capacity is ample) |
| Art | per D-14: palette-adapted vanilla placeholders (PAL-01 anchors) or supplied final art through the v0.6.1 enemy-graphics pipeline |
| Audio | vanilla tracks per AUD-01..04 |

### 5.2 Builder organisation

* New package dirs: `maps/celes_ruins_*`, `events/celes_arc_v10/`, `monsters/celes_*`, `formations/celes_*.json`.
* New targets: `content-celes-v1.0` (QA, with a QA-hub jump to each beat) and **`production-v1.0`**, the first production build with story content.
* The TECH Annex slice (map `$0C7`, `celes_annex_tech`) stays frozen for its pinned targets. Production content gets its own map ids, so nothing reuses the placeholder.

### 5.3 Acceptance criteria

* **STATIC:** all validators (allocation, walkability, text width, formation safety ERROR-free, B-leak audit), selftest additions, deterministic build, all previous targets byte-exact.
* **EMULATOR:** full arc playthrough script, Preserve and Burn each; both party compositions (with and without Locke/Edgar/Sabin); save/load at every map; rewards given once (BAL-16); flags set exactly; NPC state swaps; **Kefka's Tower progression regression** (MB §30); vanilla regression set unchanged; v0.9 / v0.9.1 save migration.
* **USER RUNTIME:** VI checklist `USER_QA_CONTENT_v1.0_VI.md`. Your PASS makes `production-v1.0` the next named baseline.

### 5.4 Risks

| Risk | Mitigation |
|---|---|
| D-03 (Leo's Blade) unresolved | Ship v1.0 without Leo's Blade placed; it stays bound but unplaced (R22 state) |
| Dialogue volume vs target (D-13) | M3 cut-first list; ample bank capacity, so this is a design limit, not a technical one |
| Praetor mechanics (E2-E4) not feasible as specified | Engine-level fallbacks proposed in M2 for your approval; mechanics simplified only by your decision |
| Final art absent | Placeholder acceptance (D-14); art swap later is data-only in the enemy-gfx pipeline |
| R25 (`$40` char_prop drops equipment) | The Celes arc never runs `$40`; validator check added |
| World-map edit (E1) touches vanilla world-map data | Asserted original bytes, minimal reversible patch, WoR world regression |

## 6. What I need from you to proceed

1. Answers to the blocking decisions (D-01, D-03, D-05, D-06, D-07, D-11, D-12, D-13, D-14, D-21, D-22), plus D-02/D-15-D-19 if you want M1.
2. Approval of the order **G1 → (M1 ∥ M2) → M3 → M4**, or a different order.
3. Art: whether final art exists for MAP-01-04, MOB-01-04, Praetor and Vale, or placeholders are acceptable for v1.0.

Until then: **no ROM changes, no code.**
