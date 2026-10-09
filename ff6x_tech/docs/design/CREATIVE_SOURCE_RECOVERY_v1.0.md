# CREATIVE SOURCE RECOVERY & DESIGN CONFIRMATION GATE — v1.0

**Project:** FFVI Expanded Edition (FF6X) · **Baseline:** TECH v0.9 ACCEPTED / USER RUNTIME PASS (unchanged)
**Input:** `FFVI_Expanded_Edition_Design_Pack_v1.2_CREATIVE_LOCK.zip` (uploaded 2026-10-06)
**Scope:** compare the locked creative sources against the v0.8/v0.9 implementation data; recover the Celes arc design.
**ROM changes in this gate: NONE. Code changes: NONE.** The v0.9 handoff tree was only read. `build.py` was not run after the startup verification (HANDOFF VERIFY PASS, 114/114 self-tests).

Companion files:
* `V09_DATA_CROSSCHECK_v1.0.xlsx` / `.csv`: 642 field-level rows (LOCKED / CURRENT / STATUS / correction / ROM impact / decision)
* `CELES_PRODUCTION_SPEC_v1.0.md`: recovered Celes "Echoes of the Empire" design
* `CONTENT_v1.0_IMPLEMENTATION_PLAN_PROPOSED.md`: proposed next milestones (awaiting approval)

---

## 1. What was recovered

| File in the pack | Size | What it locks |
|---|---:|---|
| `FFVI_Expanded_Edition_v1.2_README.md` | 1.7 KB | baseline = Rev 1 (SHA-1 `057ada1c…`, matches the project); narrative baseline order; "next phase = Rev 1 technical audit" |
| `FFVI_Expanded_Edition_Creative_Content_Lock_v1.2.md` | 6.5 KB | 15 frozen categories, canon locks, balance lock, what is NOT locked (technical data), change-control rule |
| `FFVI_Expanded_Edition_Content_Data_v1.2_CREATIVE_LOCK.xlsx` | 105 KB | 27 sheets: Quest_Arcs, Mobs (35), Bosses (14), **Weapons (13), Armor (13), Relics (13)**, Event_Flags (14), Maps (28), Map/Mob/Boss/Character/Equipment art prompts, Key_Props (22), VFX (24), Audio (20), Voice_Bible (20), Canon_Lock (32), Arc_Beat_Lock (16), Balance_Guardrails (20), Palette_Families, Creative_Lock_Matrix, Baseline_Revision |
| `FFVI_Expanded_Edition_Master_Design_Bible_v1.0.md` | 48.5 KB | arc designs with boss stats, **§18 consumables / key items with effects**, §12 minor quests + rewards, **§19 shops**, §20 world states, §23 flag plan, §24 map budget, §30 production order |
| `FFVI_Expanded_Edition_Narrative_Production_Pass_v1.1.md` | 49.4 KB | 12-15-beat expansion of every arc, NPC pools, density rules |
| `FFVI_Expanded_Edition_Scenario_Script_v1.0.md` | 36.1 KB | key scenes and dialogue spine, minor-quest scripts, endings |

**About the "Tech Gate" spreadsheet.** The pack contains **no separate Tech Gate document**. The technical gate items are the workbook's `Creative_Lock_Matrix` rows LOCK-17..LOCK-20, all marked *DEFERRED / OPTIONAL TECHNICAL*: offsets/free space, text-box budgets, palette/tile indices, relic ASM. The TECH v0.1-v0.9 work has already covered those audits.

**Version question (D-02).** The v0.7 decision (`ITEM_ARCHITECTURE_DECISION_v0.7.md` line 8) and the v0.8 `equipment.json` cite **`Content_Data_v1.3`**, but this upload is **v1.2**. All 39 locked stat lines in v0.8 equal the v1.2 workbook (field-checked), so no stat changes result either way. Please confirm whether a v1.3 exists and supersedes anything.

**Source precedence used** (proposed, D-01): v1.2 workbook sheets > Narrative Production Pass v1.1 > Scenario Script v1.0 > Master Design Bible v1.0 for narrative and structure. The v1.2 README lists the narrative baseline as 1. Scenario Script v1.0, 2. Narrative Production Pass v1.1, 3. the v1.2 Voice_Bible / Canon_Lock / Arc_Beat_Lock sheets, but it states no precedence and does not mention the Bible; the order above is my proposal built on that list. The Bible is used wherever the workbook is silent: consumable effects, shops, minor-quest rewards, relic fallbacks, boss stats.

## 2. Headline result

| Status | Rows | Meaning |
|---|---:|---|
| **MATCH** | 416 | the current v0.8/v0.9 value equals the locked value |
| **DERIVED** | 194 | the locked sources say nothing (or only something vague); v0.8/v0.9 filled the gap, so it needs confirmation |
| **MISMATCH** | 32 | the locked sources state a value and v0.8/v0.9 differs |
| **Total** | 642 | 39 equipment × ~13 fields (501 rows), 8 consumables × 12, 5 key items × 8, 2 shops, 3 global |

**Summary by family:**
1. **The 39 signature equipment items are faithful.** Every name, Attack/Defense/Magic-Defense value and stat bonus matches v1.2 (0 numeric mismatches), as does every explicitly listed equip list and named element/status effect. Where the lock is vague, v0.8 filled in a reading that needs confirmation (DERIVED): 3 equip lists ("magic users", "broad", "heavy users") and 5 effects ("MP-oriented", "resist" ×3, "status resist subset"). Remaining issues: **1 relic fallback mismatch** (Darill's Coin), **1 arc-binding mismatch** (Magister Robe), smith-purchase interpretations for Tempered Edge, Doma Edge and Sandpiercer (all derived; Sandpiercer most doubtful), 1 description with unlocked lore (Magister Rod), and 11 armor pieces with **no locked source** (correctly left `arc_reward_tbd`).
2. **The 8 consumables need re-authoring.** The handoff said only names were locked, but **Master Design Bible §18 locks an effect for every consumable** and §19 locks the shops. **7 of the 8 locked effects differ** from v0.9 (Null Dust and Beacon Flare only partly). Only Phoenix Ash matches, and **Magitek Cell is a different item entirely**. Two locked numbers (Gaia Tonic 1,500 HP, Iron Ration 600 HP) exceed what the vanilla item code can do as data alone.
3. **The 5 key items:** names match. **Sources and functions are now recoverable** from §2, §9, §10, §11, §18 and NP line 1663. The v0.9 Triune Sigil logic (built from the other two) and its description contradict the lock.
4. **Extended shops $80/$81 don't match** the four locked reconstruction shops (Rebuilt Mobliz, Rebuilt Doma, Reopened Narshe Forge, Figaro Foundry).
5. **Balance:** every equipment value is inside BAL-07/BAL-08; no consumable exceeds a vanilla ceiling.

## 3. Discrepancy report — signature equipment (39)

Full per-field rows: CSV/XLSX, Area = *Equipment - …*. Every row below is **not MATCH**. All numeric stats, and every explicitly listed equip list and element, are **MATCH** and not repeated here. The vague ones are in the interpretation row near the end of the table.

| Row | Item | Field | LOCKED SOURCE value | CURRENT v0.9 value | Status | Recommended correction | ROM change? |
|---|---|---|---|---|---|---|---|
| X0405 | **Darill's Coin** `$11E` | Relic fallback (BAL-18) | MB §9: "Fallback without ASM: **Speed +5, Magic +2, M.Evade +20%**" (workbook row lists only Spd +5, M.Eva +20) | Spd +5, M.Eva +20 | **MISMATCH** | Add Mag +2, **or** record that the v1.2 Relics row supersedes the Bible fallback (D-19) | **Yes**: 1 ItemProp byte + description |
| X0068/69 | **Sandpiercer** `$104` | Acquisition; smith GP | WB "Figaro Foundry". MB §8: Foundry is a new **map** of the Figaro arc; the §19 Foundry shop entry lists Tools + limited Magitek Cell, not Sandpiercer (the list is not stated to be exhaustive) | `smith_purchase` 20,000 GP | DERIVED (doubtful) | Recommended: chest/event reward inside the Figaro Foundry map, dropping the GP cost (D-20) | No (source metadata) |
| X0223/24 | **Magister Robe** `$10F` | Acquisition; arc | Archive Guardian boss; WB Bosses arc = **Forgotten Age** (MB §14 "Magi") | "Archive Guardian (First Magi)", `PREREQ_FIRST_MAGI_ARC` | **MISMATCH** | Re-bind to the Forgotten Age | No |
| — | **Tempered Edge** `$100` | Acquisition; smith GP | WB "Narshe forge quest"; MB §12 *The Empty Forge* **reward = Tempered Edge**; MB §19 *Reopened Narshe Forge* **sells** Tempered Edge (sources conflict) | one-time smith purchase 18,000 GP after `PREREQ_NARSHE_FORGE_QUEST` | DERIVED | Choose: quest reward (1 copy) or one-time forge purchase (D-20) | No |
| — | **Doma Edge** `$107` | Acquisition; smith GP | WB "Doma rebuilt smith"; MB §19 "only after quest and at **very high price if a second copy is allowed**" | one-time smith 24,000 GP after `PREREQ_DOMA_SMITH_REBUILT` | DERIVED | Decide first-copy delivery + second-copy policy (BAL-16) (D-20) | No |
| — | **Leo's Blade** `$102` | Acquisition | "rare Celes arc reward branch" (never defined) | quest_reward, `PREREQ_CELES_ARC_RARE_BRANCH` | MATCH (text) | **Define the branch: BLOCKING for Celes** (D-03) | No |
| — | **Gale Lance** `$10B` | Acquisition | "beacon quest" (Setzer's Race Beacon Tower **or** *Light on the Coast*?) | "Beacon quest" | MATCH (text) | Clarify later | No |
| — | **Magister Rod** `$109` | Description | not locked; visual = "ancient staff/rod … three-prong crystal cradle" | "Rod of the First Magi" (ties it to Vael) | DERIVED | Neutral wording, e.g. "Ancient crystal rod" | Yes: text |
| — | Imperial Mantle, Ashen Mail, Concord Vest, Doma Plate, Falcon Jacket, Child's Ribbon, Doma Kabuto, Engineer Goggles, Magi Circlet, Concord Shield, Ashguard | Acquisition | **no locked source** (the Armor sheet has no Source column; not in Bible/Script/Narrative) | `arc_reward_tbd` (11 items) | DERIVED | Keep TBD; assign only by versioned design change | No |
| — | Magister Robe (MP-oriented), Falcon Jacket / Concord Shield / Gale Pin ("resist"), Child's Ribbon ("status subset"), Concord Shield ("broad"), Ashguard ("heavy users"), Magi Circlet ("magic users") | interpretation | vague wording | MP +12.5%; half damage; Blind/Poison/Silence/Sleep; 12-char set (no Gau/Umaro, engine rule R8); heavy-shield set; 5-char magic set | DERIVED | Confirm the readings | Yes, only if changed |
| — | 18 items | display name | locked full name | 12-char abbreviation (R21) | DERIVED | Accept, or approve UI name-field widening (engine) | Only if changed |
| — | 13 weapons | hit rate, weapon flags | not specified | family defaults | DERIVED | Accept | Only if changed |
| — | all 39 | description | **not locked** | v0.8 text | DERIVED | Accept / edit | Only if changed |

**Relic fallback effects, full check (BAL-18):**

| Relic | Locked ASM effect (deferred) | Locked fallback | v0.8 running | Status |
|---|---|---|---|---|
| Runic Crest | Runic absorb restores **20% more MP** | Mag +5 / M.Eva +20 only | Mag +5, M.Eva +20 | MATCH |
| Maduin's Locket | Trance duration +25% | MP +25% via existing relic flag | Mag +6, Sta +3, **MP +25%** | MATCH |
| Doma Crest | Bushido charge −1 step | stats; **Auto-Haste must NOT be used** | Vig +5, Sta +5, Spd +2 | MATCH |
| Darill's Coin | Slots bad-result probability reduced | **Spd +5, Mag +2, M.Eva +20** | Spd +5, M.Eva +20 | **MISMATCH** |
| Beastheart | Rage enhancement (reserved) | stats | Vig +4, Sta +4 | MATCH |
| Engineer's Badge | Tools +10% | stats | Vig +3, Spd +3 | MATCH |
| Master's Cord | Blitz +10% | stats | Vig +5, Sta +5 | MATCH |

The locked ASM effect text is now recorded in the CSV (rows *ASM-enhanced effect*). The v0.8 notes only said "enhanced Runic", "improved Slots" and so on.

## 4. Discrepancy report — consumables (8)

Source: MB §18 (effects), §12 (quest rewards), §19 (shops). **Engine fact used:** the vanilla item code heals/damages by flat `power` (1 byte, ≤255; v0.9 emulator measured ~1 HP per point) or by 16ths of max HP/MP. v0.9's builder validator refuses status-*setting* items.

| Row | Item | LOCKED SOURCE value | CURRENT v0.9 value | Status | Recommended correction | ROM change? |
|---|---|---|---|---|---|---|
| X0504-07 | **Gaia Tonic** `$127` | **heals 1,500 HP + Regen, one ally**; sold at Rebuilt Mobliz; *Seeds for Tomorrow* reward ×3 | party HP power 240 (~105-120 each in battle; 240 in field); generic shop $80/$81; 1,500 GP | **MISMATCH** (effect, targeting, shop, source) | ONE_ALLY + set Regen. 1,500 HP is above the 255 cap: (a) fraction (e.g. 6/16 max HP) + Regen, (b) item-power ASM, or (c) versioned number change (D-16). Status-set needs an emulator proof + validator change | **Yes**: ItemProp + validator; (b) = engine |
| X0516 | **Aether Flask** `$128` | **restores 100 MP** | MP +250 | **MISMATCH** | power 100 | **Yes**: 1 byte |
| — | **Phoenix Ash** `$129` | revives one ally at 50% HP; rare | revive + 8/16 HP; rare; not sold | MATCH | — | No |
| X0540 | **Null Dust** `$12A` | **Dispel one target** | removes 6 statuses (Regen/Haste/Shell/Safe/Reflect/Float) | **MISMATCH** (partial) | Copy vanilla Dispel's mask, read from Rev 1 spell `$2C` (`C4:6AC0`+14·$2C, status bytes `10 14 FE 84`): **Vanish, Image, Berserk, Regen, Slow, Haste, Stop, Shell, Safe, Reflect, Life 3, Float**. Targeting `$41` already equals Dispel's | **Yes**: status bytes |
| X0552-55 | **Iron Ration** `$12B` | **heals 600 HP**; cheap; Rebuilt Mobliz shop | HP +200 + **Poison cure** (unlocked); generic shop; 250 GP | **MISMATCH** | 600 > 255 cap → same options as Gaia Tonic; drop the Poison cure unless approved; sell at Rebuilt Mobliz | **Yes** |
| X0564-70 | **Remedy+** `$12C` | **cures normal status + Zombie**; type **rare** | cures 13 statuses incl. Condemned/Berserk/Muddle/Sleep/Slow/Stop; sold 3,000 GP in shop $81; rarity "uncommon" | **MISMATCH** | Vanilla Remedy set (Blind/Poison/Imp/Petrify/Mute/Sap) **+ Zombie**; not sold (rare), unless approved | **Yes**: status bytes + shop |
| X0576 | **Beacon Flare** `$12D` | **Fire damage to all + reveals invisible enemies** | Fire 255 to all; no reveal | **MISMATCH** (partial) | Add the reveal (e.g. remove Vanish) after proving one item record can damage *and* remove status; define "invisible" (D-17) | **Yes**: ItemProp; engine if needed |
| X0588-93 | **Magitek Cell** `$12E` | **"Lightning non-elemental hybrid damage; limited quantity"**; Figaro Foundry "**sells limited Magitek Cell after Celes arc**" | **party MP restore** 120; not sold; "Vector arc reward" | **MISMATCH** (different item) | Re-author as a battle damage item; define "hybrid" and "limited"; bind the Foundry sale to `EXP_CELES_DONE` (D-17) | **Yes**: ItemProp + description + shop/events |

DERIVED and needing confirmation: all prices; Aether Flask / Phoenix Ash / Beacon Flare acquisition; animations; descriptions (6 must be rewritten to match corrected effects); exclusion from steal/drop (BAL-17 *allows* consumables as drops).

## 5. Discrepancy report — key / rare items (5)

Recovered locked facts: MB §2 (WOB-C), §9 (Setzer unlock), §10 (three dungeons + bosses), §11 (Broken Seal), §18 (functions); WB Arc_Beat_Lock 7A-7C, 8; Key_Props.

| Row | Item (rare id) | Field | LOCKED SOURCE value | CURRENT v0.9 value | Status | Correction | ROM? |
|---|---|---|---|---|---|---|---|
| X0600 | **Darill's Token** (20) | source | WOB-C scene on the Blackjack (before Floating Continent); "if missed, token can be found in Falcon cabin"; function **unlocks the Last Race** | "Setzer arc: Darill's tomb / Falcon" | **MISMATCH** | WOB-C + Falcon-cabin fallback | No |
| X0610 | **Concord Sigil** (21) | function | **First Magi gate** (one of three); source Concord Sentinel ✔ | "Triune Sigil prerequisite" | **MISMATCH** | All three sigils together open the gate | No |
| X0616-18 | **Cinder Sigil** (22) | source, arc, function | **Empyreal Chimera**, Field of Cinders (ARC-7B); First Magi gate | "arc TBD, source not recovered" | **MISMATCH** (now recoverable) | Fill the recovered source | No |
| X0624-28 | **Triune Sigil** (23) | source, arc, function, prerequisite, **description** | **Triune Sentinel**, Shrine of the Silent Three (ARC-7C); its own sigil | "joins the Concord and Cinder sigils"; prereq HAS both; desc "Three sigils made one." | **MISMATCH** | Remove the composite rule; rewrite the description | **Yes**: description text only |
| X0632-33 | **Broken Seal** (24) | source, arc | optional trophy of the **Vael** fight (Scene V07); no combat effect; expanded-ending condition | "late story (World of Ruin)", TBD | **MISMATCH** (now recoverable) | Bind to the Vael defeat (ARC-8) | No |

Names: all 5 MATCH. Combat stats: none (MATCH). Descriptions other than Triune: DERIVED.

## 6. Discrepancy report — shops, balance, arcs

**Extended shops (X0638-39) — MISMATCH.** Locked (MB §19):
* **Rebuilt Mobliz**: Iron Ration, Remedy, Phoenix Down, Gaia Tonic, Gaia Gear
* **Rebuilt Doma**: existing gear, Doma Edge (after quest, very high price, only if a 2nd copy is allowed), "consumable scrolls"
* **Reopened Narshe Forge**: Tempered Edge, base-game elemental blades, shields
* **Figaro Foundry**: Tools; **limited Magitek Cell after Celes arc**
* Gil-sink target 150,000-250,000.

v0.9 has instead a "rebuilt general" `$80` (Gaia Tonic, Iron Ration, **Null Dust**, Potion, Tincture, Fenix Down, Remedy, Tent) and a "rebuilt late" `$81` (**Remedy+**, …). Correction: re-author as the four locked shops (ids `$80-$83`; `$82-$8F` are free, R40). **ROM: Yes** (XShopProp / XShopPropHi). Recommended for the data-alignment milestone, though shop *placement* waits for each arc.

**Balance — MATCH.** All 13 weapons are within BAL-07 (184-222). All 7 bodies are within BAL-08 (Def 70-92, MDef 52-82). Every relic is identity/sidegrade with a fallback (BAL-09/18). The existing v0.8 balance audit (R31: Doma Edge > Strato for Cyan, etc.) stays inside the locked ranges.

**Story arc bindings.** 22 equipment items MATCH their locked arc and 16 have no locked arc (DERIVED). Magister Robe is a MISMATCH (First Magi → Forgotten Age). Undefined chains (Raider Knife "Reconstruction chain", Beastheart "Gau side content", Painter's Lens "Relm extension", Elder's Seal "Ancient lore") remain DERIVED. The v0.8 binding symbols are source-only, so nothing is placed in the ROM yet (R22).

**Global:** Hope-flag count (Quest_Arcs: 8; the Event_Flags sheet marks 10 rows "Hope? Yes") and the First Magi gate (Bible: all 8 Hope flags; Arc_Beat_Lock: 3 sigils + endgame trigger) disagree inside the locked sources. Recommend the v1.2 Arc_Beat_Lock reading (D-25). This is not needed for CONTENT v1.0 beyond assigning the Empire hope bit.

## 7. Decisions register

Status: **B** = blocking for CONTENT v1.0 (Celes) · **A** = needed for the item-data alignment · **L** = later arcs.

| ID | Decision | Options | Recommendation | Gate |
|---|---|---|---|---|
| D-01 | Source precedence | as §1 / other | v1.2 workbook > NP v1.1 > SS v1.0 > MB v1.0; MB where the workbook is silent | B |
| D-02 | Does Content_Data **v1.3** exist? | supply it / v1.2 is final | If it exists, upload it and I re-run the cross-check (scripted) | A |
| D-03 | **Leo's Blade "rare Celes arc reward branch"** | (a) optional-exploration condition independent of Preserve/Burn (e.g. all Leo records read + Names Room + a hidden Vault cabinet); (b) tied to *Graves Without Names*; (c) move it out of the Celes arc. **Not** Preserve/Burn (MB §4 "no gameplay penalty", CAN-024) | (a), as a versioned design note | **B** |
| D-04 | Runic Crest ASM in v1.0? | fallback / ASM | Fallback (MB §30 Milestone 1 says "Runic Crest fallback version") | B |
| D-05 | Vale's role / name | WB records technician / MB medic "Dr. Edrin Vale" | WB v1.2 visual + role; name "Vale" | **B** |
| D-06 | Vale inside the Annex | staging beat / re-stage C05A after the boss | Text-free staging beat (Vale follows after the theater) | **B** |
| D-07 | Vector memorial world state | as §12 C-05 of the Celes spec | Tag wall after arc (both branches) → stone memorial after Graves quest; archive state per branch | **B** |
| D-08 | *Graves Without Names* (Memorial Band) in v1.0 scope | in / later | In: same maps, Vale, ~11 boxes | B |
| D-09 | Imperial Mantle (no locked source) | leave TBD / place in Celes arc | Leave TBD unless you approve a versioned change | L |
| D-10 | "Medical supplies" (C02A) contents | vanilla consumables / none | Vanilla consumables (avoids unsourced v0.9 items) | B |
| D-11 | Speaker fallback when Locke/Edgar/Sabin are absent | fallback table / force party / drop lines | Fallback table, drafted in the ROM Script Pass for your review | **B** |
| D-12 | Narrative_Scope gaps: "failed-subject mercy/choice scene", "party-conditional Leo reactions" | write as v1.3 narrative addition / waive | You decide; I will not write new story text without a versioned change | **B** |
| D-13 | Dialogue volume ≈216 boxes vs locked 85-120 | compress via ROM Script Pass / raise target / count mandatory path only | ROM Script Pass with a cut-first list; you approve the result | **B** |
| D-14 | Art for v1.0 | final art supplied / palette-adapted vanilla placeholders now, final art later | Placeholders for v1.0 tech-content acceptance, final art as a follow-up (STYLE-18 needs hand-cleaned assets) | **B** |
| D-15 | Apply item-data corrections | before Celes (TECH v0.9.1) / bundled with v1.0 / later | Separate small milestone **TECH v0.9.1 ITEM DATA ALIGNMENT** before CONTENT v1.0 | A |
| D-16 | Gaia Tonic 1,500 HP / Iron Ration 600 HP | fraction heal / power-multiplier ASM / versioned number change | Decide after an emulator feasibility probe (in v0.9.1) | A |
| D-17 | Magitek Cell ("hybrid", "limited") and Beacon Flare ("reveal invisible") | definitions | You define. I propose: Cell = Lightning-element damage to one enemy, sold max N per visit via event; Flare reveal = remove Vanish | A |
| D-18 | Extended shops | re-author as 4 locked shops | Yes, ids `$80-$83` | A |
| D-19 | Darill's Coin fallback Mag +2 | Bible / workbook | Bible (it is the specific fallback statement) | A |
| D-20 | Tempered Edge / Doma Edge / Sandpiercer delivery and GP | as §3 | Tempered Edge = Empty Forge reward; Doma Edge = Cyan-arc reward, 2nd copy not sold (BAL-16); Sandpiercer = Foundry chest | L |
| D-21 | Event-bit allocation (Celes subset) | approve `$0E0/$0E8-$0EA` + ~15 beat bits + ~10 NPC bits | Approve with the CONTENT v1.0 plan | **B** |
| D-22 | Formation rules for Celes battles | front only / allow others | Front attacks only; Praetor + 2 Bits layout validated by `formation_safety` | **B** |
| D-23 | Encounter formations (not locked) | Celes spec §7.1 proposal | Approve or edit | B |
| D-24 | Post-boss scene order (SS C07 vs NP C06A) | order | NP C06A then SS C07 | B |
| D-25 | Hope-flag count / First Magi gate | WB / MB | WB v1.2 (8 hope flags; 3 sigils gate) | L |

## 8. ROM-impact summary

| Correction group | Rows | ROM change? | When |
|---|---|---|---|
| Consumable effects / targeting / descriptions (Gaia Tonic, Aether Flask, Null Dust, Iron Ration, Remedy+, Beacon Flare, Magitek Cell) | X0504-X0593 | **Yes**: FA ItemProp records + description text. Gaia Tonic / Iron Ration / Beacon Flare may need validator or engine work | TECH v0.9.1 (proposed) |
| Extended shops → 4 locked shops | X0638-39 | **Yes**: XShopProp / XShopPropHi data | TECH v0.9.1 |
| Darill's Coin Mag +2 (if approved) | X0405 | **Yes**: 1 byte + description | TECH v0.9.1 |
| Triune Sigil description; Magister Rod description (optional) | X0628, Magister Rod row | **Yes**: text | TECH v0.9.1 |
| Acquisition / source / arc bindings / smith costs / prerequisites (Sandpiercer, Magister Robe, key items, Tempered/Doma Edge, Gaia Tonic ×3, Magitek Cell shop) | many | **No**: source metadata only (equipment price bytes are a constant 2; bindings are not placed) | with the arc that places them |
| Interpretations confirmed as-is (DERIVED accepted) | 194 | No | — |

Every ROM change will follow the accepted rules: new hash-pinned targets; **v0.9 targets stay frozen and asserted**; STATIC / EMULATOR / USER RUNTIME kept separate.

## 9. Integrity statement

* The v0.9 handoff tree was verified once at the start of this work: **HANDOFF VERIFY PASS**, all 24 targets SHA-1-asserted, **ALL 114 SELF-TESTS PASS**. Since then it has only been read, with no file written.
* The design pack was extracted to its own directory and parsed read-only (workbook dumped sheet-by-sheet to CSV for the comparison script).
* The cross-check is reproducible: `crosscheck.py` compares the workbook stat lines automatically. Qualitative judgements come from the cited Bible/Script/Narrative passages.
