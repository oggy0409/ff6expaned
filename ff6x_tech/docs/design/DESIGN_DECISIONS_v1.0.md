# FF6X DESIGN DECISIONS v1.0 (G1 — CLOSED)

**Approved by the user on 2026-10-06** after the Creative Source Recovery gate (`CREATIVE_SOURCE_RECOVERY_v1.0.md`).
These decisions are binding for TECH v0.9.1 / v0.9.2 and CONTENT v1.0. The user's wording is reproduced faithfully. Implementation notes are marked *Impl*.

## Provenance (D-02 resolved)

| Source | SHA-1 | Role |
|---|---|---|
| `FFVI_Expanded_Edition_Content_Data_v1.3_TECH_GATE.xlsx` | `79663bea…17f53a0` | **latest workbook**; used for technical provenance only |
| `FFVI_Expanded_Edition_Content_Data_v1.2_CREATIVE_LOCK.xlsx` | `1f4ae82d…53794b8f1` | creative lock; creative values identical in v1.3 |
| Design Bible v1.0, Narrative Pass v1.1, Scenario Script v1.0, Creative Lock v1.2, README v1.2 | see `docs/design_sources/SHA1SUMS.txt` | narrative / design sources |

The user compared the two workbooks, and the builder session confirmed it sheet by sheet:
- Every one of the 27 shared sheets has identical cell values, except that Dashboard gains one row and Creative_Lock_Matrix gains LOCK-21.
- v1.3 adds four sheets: Technical_Capacity, Tech_Test_v0.1, Implementation_Phases and Technical_Sources.
- The v1.3 technical statuses ("runtime pending", item-ID capacity "RED", event/dialogue "YELLOW") are **historical**. TECH v0.1-v0.9 superseded them; TECH v0.9 is ACCEPTED / USER RUNTIME PASS.
- The 642-row cross-check (`V09_DATA_CROSSCHECK_v1.0`) stays valid without re-audit. Its row SRC-01 is resolved.

## Decisions

| ID | Decision (approved) |
|---|---|
| D-01 | Conflict precedence: (1) v1.2/v1.3 Canon_Lock / Arc_Beat_Lock / Voice_Bible and other explicit locked workbook rows; (2) Narrative Production Pass v1.1; (3) Scenario Script v1.0; (4) Master Design Bible v1.0 where newer locked sources are silent. For scene dialogue the Scenario Script stays the spine; the Narrative Pass may expand or refine it where it does not contradict higher locks. Never silently merge contradictory text. |
| D-02 | v1.3 exists; creative values are unchanged; use v1.3 for technical provenance; no re-audit. |
| D-03 | **Leo's Blade** = optional exploration reward, independent of Preserve/Burn (versioned design addition **DA-01** below). |
| D-04 | Runic Crest: BAL-18 fallback in CONTENT v1.0; no custom ASM yet. |
| D-05 | Vale: name "Vale"; former Imperial **records technician** (v1.2 workbook); NOT "Dr. Edrin Vale"; not a heroic doctor or exposition character. Compatible guilt/instrument-record dialogue may remain. |
| D-06 | Vale quietly follows into the Annex after the Infusion Theater record sequence (text-free staging); present for the Names Room. |
| D-07 | After the arc, BOTH branches get the temporary name/tag memorial wall. Archive state is branch-specific (Preserve = archive retained; Burn = procedure archive visibly burned). After *Graves Without Names* the tag wall becomes the permanent stone memorial. |
| D-08 | *Graves Without Names* is IN SCOPE for CONTENT v1.0; reward Memorial Band; same Vector Ruins map family and Vale. |
| D-09 | Imperial Mantle: source stays TBD; not placed in the Celes arc. |
| D-10 | Medical supplies: vanilla consumables only. |
| D-11 | Celes is the only mandatory member; never force Locke/Edgar/Sabin. The speaker-fallback table is built in the ROM Script Pass. If no natural fallback exists, drop a non-essential reaction line rather than give it to an out-of-character speaker. |
| D-12 | Add (1) one failed-subject mercy/choice scene and (2) party-conditional Leo reactions as **narrative amendment v1.3** (a content note, not the workbook version). Compact, no lore contradiction, no reward difference, no second major morality branch, no Kefka excuse, must pass the Voice Bible. **Exact text shown to the user in the ROM Script Pass before insertion.** |
| D-13 | The 85-120 box target applies to the **mandatory main-arc path** (preferably 100-120). NPC states, *Graves Without Names*, inspectable text and alternate party reactions may sit outside it. Still run a compression/edit pass with no telegraphic cuts. A CUT-FIRST report goes to the user for approval before insertion. |
| D-14 | Palette-adapted vanilla placeholders for CONTENT v1.0 runtime/story validation; never treated as final art. A final art pass comes later for the maps, the 4 mobs, Praetor, and Vale/NPC variants. |
| D-15 | TECH v0.9.1 (item alignment) and v0.9.2 (Celes enablers) in **one work cycle**; logically separate in source/targets/reports; **one** consolidated user runtime QA package; no intermediate user gameplay tests. |
| D-16 | **Exact locked values**: Gaia Tonic = one ally, heal exactly 1,500 HP, set Regen. Iron Ration = heal exactly 600 HP. Smallest safe extended-consumable-only fixed-heal path; vanilla consumables untouched. If unsafe: STOP and report with evidence. |
| D-17 | **Null Dust** = battle, one target, the exact vanilla Dispel removable set. **Beacon Flare** = Fire damage to all enemies + remove VANISH (Image is not "invisible"); the Fire damage is kept when revealing. **Magitek Cell** = one enemy; two damage components in the same item action (Lightning + non-elemental, about 50/50); technological item damage, not a spell; Magitek/Lightning visuals; no MP cost. Limited: sold at Figaro Foundry only after `EXP_CELES_DONE`; the player may hold or buy at most 3 from that stock at one time; leaving and re-entering must not bypass this. Price and total power are DERIVED and must be conservative and documented. |
| D-18 | Extended shops: `$80` Rebuilt Mobliz, `$81` Reopened Narshe Forge, `$82` Rebuilt Doma, `$83` Figaro Foundry, per Bible §19. No ultimate gear; unlocked prices DERIVED and documented. |
| D-19 | Darill's Coin fallback = Speed +5, **Magic +2**, M.Evade +20%. |
| D-20 | Tempered Edge: first and only copy = *The Empty Forge* reward; never sold. Doma Edge: first and only copy = Cyan/Doma reconstruction reward; no second copy in v1.x. Sandpiercer: one-time chest/event reward inside Figaro Foundry; not a GP purchase. |
| D-21 | `EXP_HOPE_EMPIRE` ≈ `$0E0`, `EXP_CELES_STARTED` `$0E8`, `EXP_CELES_DONE` `$0E9`, `EXP_CELES_RECORDS_PRESERVED` `$0EA`. About 15 beat bits and about 10 NPC bits come from the audited free pools; each passes `allocations.json` overlap and expected-byte checks; no vanilla bits are taken. |
| D-22 | Celes formations are FRONT ATTACK ONLY in CONTENT v1.0. Praetor + 2 Suppressor Bits must pass formation_safety and the VRAM checks. |
| D-23 | Encounters: Outer Ward = Rust Hound ×2, Rust Hound ×3. Annex = Annex Guard ×2, Annex Guard + Suppressor Bit, Failed Infused ×1, Failed Infused ×2, Rust Hound + Annex Guard. No signature-equipment drops. |
| D-24 | Post-boss: NP C06A quiet beat first, then SS C07. May be tightly merged in the Script Pass without changing meaning. |
| D-25 | 8 Hope flags. The First Magi gate = 3 sigils + endgame trigger; it does NOT require all 8 Hope flags. |

## DA-01 — Versioned design addition: Leo's Blade acquisition (from D-03)

| Field | Value |
|---|---|
| Locked row changed | Weapons sheet, Leo's Blade, Source "Celes arc rare branch" / Bible §15 "rare Celes arc reward branch" (the locked text left the branch undefined) |
| Why | No source defined the branch. Tying it to Preserve/Burn would contradict Bible §4 ("no gameplay penalty") and CAN-024. |
| New definition | Optional exploration reward. Conditions: (1) the player has read **all** Leo petition / transfer records (SS C05 + NP C05 fourth record); (2) the **Names Room** interaction (NP C05A) is complete; (3) the player then finds an **optional concealed officer locker / archive cabinet in the Records Vault**. One-time reward = Leo's Blade (`$102`). |
| Independence | Never depends on Preserve vs Burn. Neither records choice gives a gameplay reward penalty. |
| Dependents | `items/production_v08/equipment.json` acquisition of `$102` (conditions `PREREQ_LEO_RECORDS_ALL`, `PREREQ_NAMES_ROOM_DONE`; source `event_chest`, Records Vault concealed cabinet); Celes spec §9; CONTENT v1.0 event plan. |
| Version | Design addition DA-01, recorded with decisions v1.0 (2026-10-06). |

## Narrative amendment v1.3 (from D-12) — PENDING TEXT

Two compact additions, written in the CELES ROM Script Pass and **shown to the user before insertion**: (1) a failed-subject mercy/choice scene; (2) party-conditional Leo reactions. Constraints are listed under D-12. No text exists yet.
