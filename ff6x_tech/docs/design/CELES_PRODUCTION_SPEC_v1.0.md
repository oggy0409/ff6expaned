# CELES — "ECHOES OF THE EMPIRE" — PRODUCTION SPEC v1.0

**Status:** RECOVERED FROM LOCKED SOURCES — for review. **No ROM change. No code.**
**Gate:** Creative Source Recovery & Design Confirmation (follows TECH v0.9 ACCEPTED / USER RUNTIME PASS).
**Sources (Design Pack v1.2 CREATIVE LOCK):**

| Tag | Document | Celes material |
|---|---|---|
| **WB** | `FFVI_Expanded_Edition_Content_Data_v1.2_CREATIVE_LOCK.xlsx` | Quest_Arcs, Arc_Beat_Lock (ARC-1), Narrative_Scope, Mobs, Bosses, Weapons/Relics, Event_Flags, Maps, Map/Mob/Boss/Character art prompts, Key_Props, VFX, Audio, Voice_Bible, Canon_Lock, Palette_Families |
| **NP** | `Narrative_Production_Pass_v1.1.md` | lines 183-537 (scenes C00-C09 + post-quest NPC states); line 1995 (cross-arc line) |
| **SS** | `Scenario_Script_v1.0.md` | lines 196-450 (C01-C08, NPC states); 1803-1831 (Graves Without Names); 1838-1839 (airship bark); 1881-1911 (endings E01/E02) |
| **MB** | `Master_Design_Bible_v1.0.md` | §4 (lines 71-194), §12, §13, §14, §15, §19, §20, §21, §22, §23, §24, §30 |
| **CL** | `Creative_Content_Lock_v1.2.md` | canon and balance locks, change-control rule |

**Source precedence used in this spec.** For narrative content: WB v1.2 sheets (Arc_Beat_Lock, Canon_Lock, Voice_Bible) > NP v1.1 > SS v1.0 > MB v1.0. This order is my proposal (D-01): the v1.2 README lists the narrative baseline as 1. Scenario Script v1.0, 2. Narrative Production Pass v1.1, 3. v1.2 Voice_Bible / Canon_Lock / Arc_Beat_Lock, but states no precedence and does not mention the Bible. For data the workbook is silent on, MB applies. Every place where sources disagree is marked **⚠ CONFLICT** and listed in §12. Anything here that is not in a locked source is marked **PROPOSAL** and needs your approval under the CL §8 change-control rule.

---

## 1. Arc identity

| Field | Locked value | Source |
|---|---|---|
| Arc ID / title | ARC-1 — *Echoes of the Empire* | WB Quest_Arcs, Arc_Beat_Lock |
| Era / location | World of Ruin — Vector Ruins | WB Quest_Arcs |
| Focus | Celes | WB Quest_Arcs |
| Narrative purpose | "Give Celes closure with the Empire and reveal the Magitek-human experimentation program without softening Kefka." / "Magitek program / Imperial guilt" | MB §4; WB Quest_Arcs |
| Target beats | **14** (mandatory beat chain, §3) | WB Arc_Beat_Lock |
| Target playtime | **35-55 min** | WB Arc_Beat_Lock |
| Target new dialogue boxes | **85-120** | WB Arc_Beat_Lock, Narrative_Scope |
| Arc reward / state | **Hope: Empire + Runic Crest** | WB Arc_Beat_Lock, Quest_Arcs |
| Difficulty band | Mobs Lv 30-34 (band A/B), boss Lv 36 with 47,800 HP, which fits band B ("late-WoR sidegrade", boss HP 34-48k), not band A (24-38k) | WB Mobs/Bosses; MB §3 |
| Production order | **Milestone 1 — vertical slice**: "4 maps, 4 normal mobs, Magitek Praetor, Runic Crest fallback version, complete events/dialogue, save/load regression, Kefka Tower progression regression. If this runs safely, it becomes the technical template for every other arc." | MB §30 |

## 2. Prerequisites / unlock

| Condition | Value | Source |
|---|---|---|
| Trigger | Falcon obtained + Celes recruited | WB Arc_Beat_Lock; MB §4 |
| Party | **Celes mandatory; Locke recommended** | WB Arc_Beat_Lock (MB §4: "Celes in party") |
| Access | "Visit Vector ruins via a **new landing point south-east of Kefka's Tower debris field**" | MB §4 |
| Other arcs | None. All WoR arcs are optional and order-flexible (CAN-023). | WB Canon_Lock |
| WOB-A seed | Optional. Missing it "changes a few lines, not access" (CAN-022). No Celes line is written conditional on WOB-A in the locked text. | WB Canon_Lock; NP line 105 |
| Shadow / others | Only party-reaction lines (IF TERRA / IF CYAN / IF SHADOW) depend on who is present. | NP C04B |

## 3. Story beats — locked 14-beat chain, mapped to scenes

Arc_Beat_Lock chain: *Landing distrust → outer ward → Vale → survivor dispute → Annex → observation → infusion theater → record reel → party reactions → Leo petitions → names room → Praetor → records choice → memorial / Falcon debrief.*

| # | Beat | Scene(s) and source lines | Location (§5) | Content summary | Est. boxes |
|---|---|---|---|---|---|
| B01 | Landing distrust | NP **C00** (185-210) | Outer Ward, service field | Two survivors retreat from armed travelers; "She is [Imperial]." / "Was." / "Trust what we do next." | 9 |
| B02 | Outer ward | SS **C01** (198-212) + NP **C01** optional barks (212-242); MB §4 step 1 | Outer Ward | Celes names the district ("Officers' quarter. Research wing to the east."). Optional: Broken Barracks Sign ("THIRD MAGITEK TRAINING COMPANY"), Collapsed Kitchen. MB adds "Celes recognizes an old officer insignia". | 6 + 8 opt |
| B03 | Vale | SS **NPC Vale** (214-230) + **C02 Vale's confession** (232-252) + NP **C02** add (244-256) | Outer Ward, survivor shelter | Vale recognizes "General Celes". Confession: "I carried instruments. Wrote temperatures. Held people still." / "Now I wake up remembering their names." / "Good." NP adds "We heard you died at the Floating Continent." | 20 |
| B04 | Survivor dispute | NP **C02A** (258-282) | Outer Ward | Medicine vs the dead; Celes: "The upper stores were medical supply rooms." Gives the survivors a practical reason to care. | 11 |
| B05 | Annex | SS **C03** (254-268); NP C03 "v1.0 remains" | Annex entrance | Vale: "I can't go farther." / "Won't." Celes: "Of course I am [afraid]. Open the door." | 7 |
| B06 | Observation | NP **C03A** (288-312) | Annex B2 observation corridor | Empty chair bolted to the floor: "It wasn't for the patient." / "To learn not to react." / "I became a general." | 9 |
| B07 | Infusion theater | SS **C04** (270-286) | Infusion Theater | "I know this room." / "I woke up here." / "We do it once." | 6 |
| B08 | Record reel | SS **Terminal C-A** (288-306, K-01) + **Terminal C-B** (308-328, C-07) + NP **C04A** training reel (318-338) | Infusion Theater | K-01: instability, "FURTHER INFUSION AUTHORIZED BY IMPERIAL DECREE"; Celes: "I won't turn a monster into an excuse because a file has his initial." C-07: revised protocol, "AGE EXCEPTION APPROVED". Training reel = crude stills, not a cinematic; Celes powers it down herself. | 20 |
| B09 | Party reactions | NP **C04B** (340-376): IF TERRA / IF CYAN / IF SHADOW | Infusion Theater | Conditional, 3 sets. | 0-6 (cond.) |
| B10 | Leo petitions | SS **C05** (330-346) + NP **C05** 4th record (378-400) | Annex terminal (PROPOSAL: terminal alcove, §5) | SS: two denials + "FORMAL PROTEST ENTERED"; NP adds a transfer request, also denied: "SUBJECT C-07 REMAINS IMPERIAL PROPERTY." / "He tried to take me out." / "He was annoyingly decent like that." | 13 |
| B11 | Names room | NP **C05A** (402-428) | Names room (side room) | Vale reads three fictional names (Mila Renn 17, Doren Kess 20, Pera Sol 15). "Remember the names first." **⚠ Vale is inside the Annex here (see C-04).** | 10 |
| B12 | Praetor | SS **C06** activation (348-362) → **BOSS** → SS **C07** after boss (364-376) + NP **C06A** no-fanfare (434-450) | Infusion Theater (boss door) | "BIOMETRIC MATCH. CELES CHERE. STATUS: DESERTER. SENTENCE: IMMEDIATE." After: "You all right?" / "No." and the silent-room beat "Don't ask me yet." / "Now." | 4 + 6 + 7 |
| B13 | Records choice | SS **C08** (378-432) + NP **C07** branch beats (452-474) | Records Vault | `[CHOICE] Preserve the records / Burn the records`. Burn = burn the **procedure**, keep the names (v1.2: "names always preserved"). Branch lines in §8. | 10 + 7/6 |
| B14 | Memorial / Falcon debrief | NP **C08** surface memorial (476-492) + NP **C09** Falcon debrief (494-520) + NPC states (§6) | Outer Ward → Falcon deck | Tags on a temporary wall: "A name is not an absolution. It is a record." Falcon railing: "Stay." / "Wasn't going anywhere." | 7 + 12 |

**Total estimated dialogue boxes in the locked text: ~216** (SS ≈ 97 + NP ≈ 119, NPC-state lines included; terminal lines merged two per box). That is **about 1.8× the locked 85-120 target** → decision D-13 (§13).

**Beat-order ⚠ CONFLICT C-02.** MB §4 puts the Praetor before the Leo record (found in the Records Vault). SS, NP and the v1.2 Arc_Beat_Lock all run **Leo petitions → names room → Praetor → records choice**. This spec follows v1.2.

## 4. Dialogue / scenes — implementation notes

* **Speakers used in the locked text:** Celes (≈84 lines), Vale (33), Locke (24), Edgar (14), Sabin (11), Terminal/System (24), survivors (≈20), Terra/Cyan/Shadow (conditional, 10).
* **⚠ Party dependency (C-11).** Mandatory scenes give lines to Locke, Edgar and Sabin, but the lock only *requires* Celes ("Locke recommended"). The implementation needs a **speaker-fallback table** (who speaks a line when its owner is absent, or whether the line drops). That is a text decision → D-11.
* **Conditional lines:** `[IF TERRA]`, `[IF CYAN]`, `[IF SHADOW]` (NP C04B); `[IF CELES]` on the barracks sign (always true, since Celes is mandatory).
* **Choice:** one 2-option choice (Preserve / Burn), proven engine feature (TECH v0.3 slice uses a dialogue choice).
* **Text rules:** Voice_Bible rows for Celes, Locke, Edgar, Sabin, Terra, Cyan, Shadow and **Vale** ("Precise, guilty, bureaucratic habits linger; ordinary survivor, not philosopher … no exposition machine; no sudden heroism"). CL §3 allows wording edits for ROM text-box limits / control codes, line breaking, localization polish, consistency with the selected FFIII US script baseline, removal of redundancy and gameplay QA. Changing plot, motive, canon or scene purpose requires a deliberate versioned design change. NP "Hard style rules" 1-15 and SS "Final style checklist" 1-10 apply.
* **Names to keep fictional and short:** Mila Renn, Doren Kess, Pera Sol (NP 418-424).
* **Terminal/record wording:** use the SS/NP record lines. The MB §4 record lines are older variants (C-13).
* **Cross-arc lines that read Celes state:** NP V01A (line 1995) `[If Celes arc completed:] Celes: "I've seen that kind of success before."`; NP EC-01 ending (requires Mobliz + Empire); MB §19 Figaro Foundry "sells limited Magitek Cell after Celes arc"; MB §11 Vael *Last Edict* (≥6 / all 8 Hope flags).
* **Airship bark after quest (SS 1839):** "I don't need the Empire forgiven. I need it remembered correctly."

## 5. Maps

| ID | Map / state | Type | Locked layout elements | Palette anchors | Source |
|---|---|---|---|---|---|
| — | **WoR world-map landing point** | world-map entrance | "new landing point south-east of Kefka's Tower debris field"; NP C00: "broken Imperial service field" | — | MB §4; NP C00 |
| MAP-01 | **Vector Ruins — Outer Ward** | new dungeon exterior | collapsed gate, half-buried Imperial eagle/emblem, cracked avenue, **one survivor shelter**, **Annex entrance behind fallen masonry**; props: filing crates, bent pipes, torn red banners, ration tins, **numbered grave markers** | ash grey, oxidized iron, faded Imperial crimson | WB Map_Art_Prompts |
| MAP-02 | **Imperial Research Annex B2** | dungeon | airlock door, **observation booth**, branching lab corridor, broken lift, **terminal alcove**; numbered doors, restraints, glass cylinders; red emergency lamps | cold blue-grey metal, dirty ivory tile, oxidized green | WB Map_Art_Prompts |
| MAP-03 | **Infusion Theater** | boss room | circular chamber, **central restraint dais**, four machinery pylons, observation balcony/window, **sealed boss door** | dirty ivory, steel blue, dried maroon, cyan glass | WB Map_Art_Prompts |
| MAP-04 | **Records Vault** | story room | sealed cabinet wall, central reading table, terminal, **furnace/incinerator niche**, **exit to surface** | charcoal, parchment tan, muted green, brass | WB Map_Art_Prompts |
| — | Vector ruin landing area | modified/reused | listed under "Modified/reused maps" | — | MB §24 |
| — | Vector Ruins world state | map state | "A memorial marker appears if records preserved; a burned-out archive appears if destroyed." **⚠ C-05** | — | MB §20 |
| — | Falcon deck (railing) | vanilla map | C09 debrief scene | — | NP C09 |

**Rooms the scenes need, PROPOSAL for placement:** the *upper stores / medical supply rooms* (C02A) are not a separate map in the budget, so they would be a room in MAP-02 or an Outer Ward building. The *Names room* (C05A) would be a MAP-02 side room. The *Leo petition terminal* (C05) would be the MAP-02 "terminal alcove". Resulting route: Outer Ward → Annex B2 (observation → theater → back to alcove + names room) → Infusion Theater boss door → Records Vault → surface → Falcon.

**Tile policy:** MB §24 says "reuse tilesets aggressively; create new tiles only for signature areas". STYLE-02/05 ask for a small reusable tile vocabulary. The TECH slice map `$0C7` already uses the vanilla Magitek-lab tileset (`tile_property_set 0x24`) as **placeholder**.

## 6. NPCs

| NPC | Role | Locked visual / voice | Sprite plan | States | Source |
|---|---|---|---|---|---|
| **Vale** (NPC-01) | original major NPC; survivor witness | Former Annex records technician, late 40s; lean, slightly stooped civilian; work coat over old Imperial utility clothes; no armor; hands stained with ink/oil (paraphrased from NPC-01). Palette: ash grey, muted olive, parchment tan, small brass. **No lab coat.** Voice: Voice_Bible "Vale". | **unique palette/sprite variant preferred** | before / during (Annex, Vault) / after ("Neither did the patients.") | WB Character_NPC_Prompts, Voice_Bible; SS; NP |
| ⚠ **C-03 role** | MB §4: "former Imperial medic **Dr. Edrin Vale**", "junior physician"; SS: "Former Imperial Medic Vale"; v1.2: "records technician", "guilt over clerical participation" | | | | |
| Survivor / Survivor A / Survivor B | landing distrust, dispute, memorial | civilians | vanilla civilian sprites | C00, C02A, C08 | NP |
| Survivor 1 / Survivor 2 | persistent NPC states | — | vanilla | before / after-preserve / after-burn | SS 434-450 |
| Former Cook, Former Clerk, Young Survivor | post-quest NPC pool | — | vanilla | after | NP 522-536 |
| **Vector Memorial Worker** (NPC-04) | memorial | stone-dusted apron, headcloth, chisel pouch, one faded red Imperial thread | **reuse vanilla worker sprite** + palette | "We ran out of stone before we ran out of names." | WB; NP |
| Former Imperial soldier | NPC states | — | vanilla soldier/civilian | before / after preserve / after burn | MB §21 |
| Former Soldier | Graves Without Names | — | vanilla | completion | SS 1823-1829 |
| **Imperial Child Celes (memory)** (NPC-12) | record reel only | small pale-haired child silhouette, dirty-ivory clothing, never graphic | "use sparingly; **may be abstract silhouette instead of new sprite**" | C04A stills | WB |
| Figaro Archivist | ending E01 only | — | vanilla | ending (deferred) | SS 1881-1899 |

**Locked NPC state lines (for implementation):**

* *Before quest*: Survivor 1 "Nothing grows here. Maybe nothing should." / Survivor 2 "We were clerks, cooks, mechanics. Not everyone in Vector carried a sword." / former soldier "Don't look at the uniform. I don't wear it anymore."
* *After Preserve*: "Figaro took the records. Strange... seeing soldiers guard paper instead of people." / "My brother's name was in there. At least now somebody knows." / "Put my name in the book too. I followed orders. That's still something I did." / "A Figaro archivist asked me to sign my testimony. My hands shook more than they did in the Annex."
* *After Burn*: "Smoke again. Vector always ends in smoke." / "They kept the list of names. That's enough for me." / "No records left? Maybe that's mercy. Maybe it's cowardice." / "The procedure is ash. The roster isn't. I think she chose correctly. I also think I will wonder forever."
* *After (either)*: Former Cook, Former Clerk, Young Survivor, Vale, Memorial Worker (NP 524-532).

Narrative_Scope asks for **6-10 survivor NPC states**. The locked lines cover that.

## 7. Enemies / bosses

### 7.1 Normal mobs (WB Mobs = MB §13)

| Enemy | Lv | HP | MP | BP | Def | MDef | Mag | Spd | Weak | Absorb/Null | EXP | GP | Behavior | Art (Mob_Art_Prompts) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|---:|---|---|
| **Rust Hound** (MOB-01) | 30 | 2800 | 200 | 29 | 125 | 105 | 8 | 44 | Ice | Poison null | 1300 | 700 | Pack Howl = Haste allies | M; low iron-plated dog, exposed gear ribs, one red lens, cable tail |
| **Annex Guard** (MOB-02) | 31 | 3400 | 350 | 31 | 140 | 120 | 8 | 38 | Lightning | — | 1450 | 900 | Magitek Laser | M; squat security automaton, shield chest, piston legs, shoulder emitter |
| **Suppressor Bit** (MOB-03) | 33 | 2200 | 1200 | 20 | 155 | 150 | 11 | 50 | Water | Lightning null | 1200 | 500 | Reflect support | S; compact oval drone, cyan core, three prongs |
| **Failed Infused** (MOB-04) | 34 | 5200 | 1800 | 34 | 135 | 135 | 12 | 36 | Holy | Poison absorb | 1900 | 900 | random elemental spells | M; gaunt human, one crystal-overgrown arm; **no gore** |

Guardrails: BAL-01 (Lv 30-44), BAL-02 (2,200-8,500 HP; all four fit), BAL-10 (≤1 absorb + 1 null), BAL-12 (1-2 signature statuses), **BAL-14 (3-5 formation types per dungeon family)**, BAL-17 (drops: consumables/sellables/mid-tier gear; **no signature equipment**).

**Encounter formations: NOT LOCKED.** PROPOSAL (for approval): Outer Ward: Rust Hound ×2, Rust Hound ×3. Annex B2: Annex Guard ×2, Annex Guard + Suppressor Bit, Failed Infused ×1-2, Rust Hound + Annex Guard. That gives 4-5 types per dungeon family (BAL-14). **Front attacks only** until back/pincer placement is validated (TECH risk F2).

### 7.2 Boss — Magitek Praetor (MB §4; WB Bosses; BOSS-01)

| Stat | Value | | Stat | Value |
|---|---|---|---|---|
| Level | 36 | | Defense | 165 |
| HP | 47,800 (single phase; BAL-05 36k-58k ✔) | | Magic Defense | 150 |
| MP | 9,000 | | Magic Power | 13 |
| Speed | 45 | | Weak | Lightning |
| Battle Power | 34 | | Null | Poison |
| Absorb | none | | Immune | Doom, Petrify, Confuse |

**AI (locked):**
1. Opening: **Magitek Barrier** (Protect + Shell).
2. Rotation: Magitek Laser / Missile / Tek Beam / physical.
3. **At 70% HP:** launches two **Suppressor Bits** (the MOB-03 record).
4. **At 40% HP:** *Barrier overload*: loses Defense, gains Haste.
5. **If hit by Lightning three times:** *Grounding Field*, temporarily nulls Lightning for 3 turns (BAL-11: a weakness must not trivialize).

* **Reward:** **Runic Crest** (§9).
* **Visual (BOSS-01):** L/XL heavy olive-gunmetal quadruped/tank chassis, raised armored command torso, red targeting lens, **two support-drone hardpoints**, cyan vent slits, old Imperial execution insignia scratched into plating. Front armor closed in barrier phase; plates flare open in overload. Must read as "the logical apex of Annex Guard / Suppressor Bit design" (STYLE-13).
* **VFX:** VFX-01 Praetor Barrier (thin blue-white shimmer close to armor, 2-3 frame pulse; reuse Reflect/force-field palette; no dome, no hex-grid hologram). VFX-02 Overload Vent (cyan vents → white/orange + short steam burst; reuse steam/spark tiles; no explosion loop).
* **Engine notes (TECH, not creative):**
  * Bit launch at 70%: hidden formation members shown by AI. This is vanilla behaviour, but the formation must fit the L/XL boss plus 2 S bits (risk F3/F4).
  * Defense loss at 40%: no vanilla AI command lowers Defense, so it is likely a **monster swap** (an "overload" variant record), which is risk **F5** (transforming bosses not modelled).
  * Temporary Lightning null: needs a monster swap or ASM.
  * Attack names are mapped to the nearest vanilla attacks during the TECH gate.

## 8. Flags and branching

### 8.1 Locked logical flags (MB §23; WB Event_Flags)

| Logical flag | Meaning | Hope? | Proposed bit (`audits/eventbit_allocation_PROPOSED.json`, NOT yet approved) |
|---|---|---|---|
| `EXP_CELES_STARTED` | arc started | — | `$0E8` (`$1E9D.0`) |
| `EXP_CELES_DONE` | arc complete | **Yes (Hope: Empire)** | `$0E9` (`$1E9D.1`) |
| `EXP_CELES_RECORDS_PRESERVED` | Preserve (1) / Burn (0) | No | `$0EA` (`$1E9D.2`) |
| `EXP_HOPE_0x` (Empire) | packed Hope bit | Yes | `$0E0` (`$1E9C.0`) — *which index = Empire is not locked* |

### 8.2 Implementation beat flags (TECHNICAL, not creative; PROPOSAL)

About 12-15 event bits: landing-seen, Vale-met, dispute-seen, Annex-unsealed, theater-records-seen, Leo-records-read, names-room-done, Praetor-defeated (gives Runic Crest), Imperial-Saber chest (treasure bit), records-choice-made, memorial-seen, Falcon-debrief-seen, Leo's-Blade-given (if the branch is defined), Graves-quest started/done. Plus about 8-12 NPC-visibility bits for survivor / Vale / memorial state swaps. The proposal file lists **72 unallocated free bits** in `$000-$2FF` and 356 unreferenced NPC bits, so the budget is not a constraint.

### 8.3 Branching rules (locked, plus one marked interpretation)

* **Records choice:** Preserve vs Burn *procedure data*. **Names are always preserved** (Arc_Beat_Lock; SS Burn: "Keep the names. Burn the procedure.").
* **Either choice sets Hope: Empire** (MB §4 step 10). "No gameplay penalty" (MB §4 step 9). CAN-024: the choice "changes archive aftermath/NPC text, **not Celes's redemption or global ending**". → *Interpretation (not a stated lock):* no reward should depend on Preserve vs Burn.
* **Branch consequences:** NPC lines (§6); world state (MB §20: memorial marker vs burned-out archive, ⚠ C-05); expanded ending **E01 Preserve** (Figaro archive, Leo files "With the others") / **E02 Burn** (Vector memorial, Celes places old insignia: "We remembered the names."). The endings are deferred work but read these flags.
* **Party-conditional lines:** IF TERRA / IF CYAN / IF SHADOW (C04B).

## 9. Rewards (equipment, key items, state)

| Reward | Type / id | Locked source | Stats (locked = current v0.8) | Status for v1.0 |
|---|---|---|---|---|
| **Runic Crest** | relic `$11A` | **Magitek Praetor** boss reward / arc reward | Celes only; Mag +5, M.Eva +20; ASM: "when Runic absorbs a spell, restores 20% more MP" — **fallback: Mag +5 / M.Eva +20 only** | Ready (fallback). MB §30 Milestone 1 explicitly says *Runic Crest fallback version*. |
| **Imperial Saber** | weapon `$101` | **"Vector Annex chest"** | Celes only; Atk 205, Mag +3, M.Eva +20 | Ready. Place as a one-time chest in Annex B2 (exact room = PROPOSAL). |
| **Leo's Blade** | weapon `$102` | **"rare Celes arc reward branch"** | Terra/Celes/Edgar/Locke; Atk 218, Vig +3, Sta +3, Holy | **BLOCKED.** No locked document defines the branch, and tying it to the records choice would conflict with MB §4 "no gameplay penalty" and CAN-024 (interpretation). Decision D-03. |
| **Memorial Band** | relic `$11F` | minor quest **"Graves Without Names"** (Vector ruins: identify soldiers/civilians → memorial appears) | All; Sta +4; blocks Berserk/Confuse | Companion quest using the same maps and Vale (SS 1803-1831). Scope decision D-08. |
| **Hope: Empire** | flag | arc completion | — | Set at the records choice / end of B14 |
| Magitek Cell shop unlock | consumable `$12E` | Figaro Foundry "sells limited Magitek Cell **after Celes arc**" | **v0.9 Magitek Cell is a different item** (party MP) from the locked one ("Lightning non-elemental hybrid damage; limited quantity") | Cross-arc. The Figaro arc is not built, so v1.0 only needs `EXP_CELES_DONE` available. |
| Medical supplies (C02A "There could be medicine in there… We look.") | not an item lock | implied by the narrative | — | PROPOSAL: vanilla consumables in the upper stores (D-10) |
| *Imperial Mantle* | armor `$10E` | **no locked source** (Armor sheet has none) | Celes/Terra; Def 78, MDef 72, Mag +4, M.Eva +20 | Thematic candidate only. Placing it here is a **versioned design change** (D-09). |

**Key items:** **none locked for the Celes arc.** The 5 locked key items belong to WOB-C/Setzer (Darill's Token), the Forgotten Age (3 sigils) and the First Magi (Broken Seal). The Celes key *props* (§10) are story objects, not inventory items.

## 10. Key props (WB Key_Props)

| ID | Object | Locked visual | Narrative function |
|---|---|---|---|
| PROP-01 | K-01 Subject Record | thin metal-backed Imperial record slate/tag bundle stamped K-01; **no Kefka portrait** | story evidence; implication only (CAN-010, CAN-031) |
| PROP-02 | C-07 Subject Tag | small rectangular subject tag with rounded corners, punched mounting hole, stamped C-07; later placed **face-up** at the memorial | Celes identity evidence (CAN-011) |
| PROP-03 | Failed Subject Tags K-02-K-06 | five similar numbered tags, scratched, mismatched; face-up arrangement | humanizes failed subjects without bodies |
| PROP-04 | Leo Petition File | folded formal petition, Leo's seal impression, repeated denial stamps | compatible Leo lore; **no secret rebellion** (CAN-012) |
| PROP-05 | Vector Memorial Stone | plain low stone slabs, names only, no rank hierarchy, no statues | "names are record, not absolution" |

## 11. Visual / art / audio requirements

* **Palette family PAL-01 "Imperial Ruins":** ash grey, oxidized iron, faded crimson, dirty ivory, muted cyan. Signature contrast: faded crimson cloth + green/bronze machinery. Avoid saturated sci-fi blue/red. Applies to MAP-01-04, MOB-01-04 and the Praetor.
* **Global style:** STYLE-01..18 (FFVI SNES 16-bit; enemies three-quarter side view; 8-15 colors; boss = elaborate relative of area vocabulary; Imperial machines = pipes, rivets, brass/iron, simple lenses; **AI output is concept/reference only; final assets hand-cleaned and indexed**, STYLE-18). CL §5 global negatives: no photorealism, 3D look, anime rendering, neon, gore.
* **Required new art (final):** 4 map tilesets/tile groups (MAP-01-04, reuse-first); 4 mob sprites + Praetor (L/XL); Vale palette/sprite variant; memorial worker palette; optional child-Celes silhouette (stills). **No final art exists yet**: the TECH slice uses vanilla placeholders, and "final custom enemy art" is deferred work. Decision D-14.
* **Equipment art:** EQ-W02 Imperial Saber (narrow curved officer saber, brass basket guard), EQ-W03 Leo's Blade, EQ-R01 Runic Crest (clasp refashioned from an Imperial seal, emblem filed away), EQ-R06 Memorial Band. **Concept only: ROM keeps existing icon families** (LOCK-06). This matches v0.8.
* **Audio (AUD-01..04, vanilla tracks only):** Outer Ward = Dark World / subdued ruin (silence for the first 2 s on landing if the event budget allows). Annex B2 = Devil's Lab / Magitek-facility mood, lower intensity, **no boss music in exploration**. Infusion Theater records = music fades to near-silence, terminal beeps carry the scene. Vector memorial = Celes's Theme **only after the names are read**, or silence. MB §26 suggests "The Empire Gestahl" / darker ambient for the Annex.

## 12. Source conflicts and gaps (Celes-relevant)

| ID | Topic | Disagreement | Proposed resolution (needs approval) |
|---|---|---|---|
| C-02 | Beat order | MB §4: Praetor → Leo record in Records Vault; SS/NP/WB v1.2: Leo petitions → names room → Praetor | Follow WB Arc_Beat_Lock v1.2 |
| C-03 | Vale's role | MB: "Dr. Edrin Vale", medic / junior physician; SS: "Former Imperial Medic"; WB v1.2: records technician, no lab coat | Follow WB v1.2 visual/role; name him "Vale"; keep SS/NP lines (they fit either role) |
| C-04 | Vale inside the Annex | SS C03: Vale "won't" go farther; NP C05A (names room, inside) and SS C08 ("Vale enters Records Vault") need him inside | Add a non-dialogue staging beat (Vale follows after the theater) or re-stage C05A after the Praetor. Text-free, but it changes staging → approval |
| C-05 | Memorial world state | MB §20: memorial marker **if preserved**, burned-out archive if burned; NP C08: tag wall in both branches; minor quest "Graves Without Names": "memorial appears"; SS E02 (Burn) takes place at the "Vector memorial" | Temporary tag wall after the arc (both branches); stone memorial (PROP-05) after Graves Without Names; archive state per branch |
| C-11 | Party composition | Mandatory scenes use Locke, Edgar, Sabin; lock requires only Celes | Speaker-fallback table (D-11) |
| C-12 | "I know this corridor/room" | MB places it at the Annex entrance; SS at the Infusion Theater | Follow SS |
| C-13 | Record wording | MB §4 record lines vs SS Terminal C-A/C-B | Follow SS/NP |
| C-14 | Post-boss order | SS C07 ("You all right?") and NP C06A ("That's it?") are both locked | Play NP C06A (silence beat) then SS C07, or merge (text pass) |
| G-01 | Narrative_Scope asks for "**one failed-subject mercy/choice scene**" and "**party-conditional Leo reactions**" | Not written anywhere in NP v1.1 | Versioned narrative addition (v1.3) or explicit waiver (D-12) |
| G-02 | Leo's Blade "rare branch" | Undefined everywhere | D-03 |
| G-03 | Dialogue volume | ≈216 boxes in the locked text vs 85-120 target | ROM Script Pass (NP "Next narrative pass": stable scene IDs, box split, byte measure, cut-first list) + decision D-13 |

## 13. Decisions needed before CONTENT v1.0 (Celes subset)

**BLOCKING:** D-03 Leo's Blade branch · D-05 Vale role (C-03) · D-06 Vale staging (C-04) · D-07 memorial state (C-05) · D-11 speaker fallback · D-12 Narrative_Scope gaps · D-13 box budget · D-14 placeholder vs final art for v1.0 · D-21 event-bit approval (Celes subset) · D-22 formation rules (front attacks only; Praetor + 2 Bits layout).
**NON-BLOCKING:** D-04 Runic Crest ASM (recommend fallback per MB §30) · D-08 Graves Without Names in scope · D-09 Imperial Mantle placement · D-10 medical-supplies contents · D-23 encounter list · D-24 post-boss scene order.

Full list with options: `CREATIVE_SOURCE_RECOVERY_v1.0.md` §7.
