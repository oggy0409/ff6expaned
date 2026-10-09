# FINAL FANTASY VI — EXPANDED EDITION
## Creative & Content Lock Bible v1.2

**Status: CREATIVE CONTENT LOCKED**

This document freezes the creative target before technical ROM implementation begins.
The project baseline is the official North American **Final Fantasy III (USA) (Rev 1) / v1.1 / Revision A** ROM.

## 1. Locked ROM baseline

- File: `Final Fantasy III (USA) (Rev 1).sfc`
- Size: 3,145,728 bytes, unheadered
- SHA-1: `057ada1c641e3e0b3ca34e6e4f4eb1b05a87143a`
- CRC32: `C0FA0464`
- Internal revision: 1.1
- Publisher/release lineage: official Squaresoft North American SNES revision

This is now the **only baseline** for FFVI Expanded Edition unless the project explicitly creates a new branch.
Community patches written for US v1.0 must not be applied blindly; required fixes/features must be audited or ported to Rev 1.

## 2. What is frozen

The following are now treated as source-of-truth creative decisions:

1. Eight major World of Ruin/endgame arcs plus three World of Balance lore seeds.
2. Arc triggers, required characters, branch behavior, minimum beat counts, ending consequences and signature rewards.
3. Canon boundaries: no resurrection, no secret true villain, no fourth god, no time travel, no undoing the original ending.
4. Character voice rules for the full playable cast and all important expansion NPCs.
5. 28 new/modified map and map-state visual concepts.
6. 35 normal enemy concepts.
7. All planned boss/phase concepts.
8. Palette families and continuity anchors for every art family.
9. Original expansion NPC visual identities and reuse policy for minor NPCs.
10. Visual forms for every new weapon, armor piece and relic.
11. Key lore objects, documents, memorial props and recurring symbols.
12. Boss telegraphs, environmental VFX and reconstruction-state animations.
13. Music/SFX direction, using the vanilla soundtrack and sound vocabulary first.
14. Weapon/armor/relic power envelope, monster/boss HP tiers and vanilla-plus difficulty philosophy.
15. Expanded ending philosophy: conditional vignettes only; Kefka and the vanilla resolution remain the climax.

## 3. Narrative lock

Narrative source of truth is the combination of:

- `Scenario Script v1.0` — key scenes and dialogue spine.
- `Narrative Production Pass v1.1` — additional beats, exploration dialogue, party reactions, NPC states and pacing expansion.
- `Voice_Bible`, `Canon_Lock` and `Arc_Beat_Lock` in the v1.2 spreadsheet.

The previous concern that the story was too short is resolved by **adding more situations rather than longer speeches**.
Major arcs are locked to roughly **12–15 meaningful beats** and normally **65–125 new dialogue boxes**, depending on arc.
Short World of Balance seeds remain intentionally short.

From this point forward, narrative wording may be edited for:

- ROM text-box limits and control codes;
- line breaking;
- localization polish;
- consistency with the selected FFIII US script baseline;
- removal of redundancy;
- gameplay QA.

Those edits must not change the locked plot, character motive, canon rule or scene purpose without a deliberate versioned design change.

## 4. Critical canon locks

- Kefka is still the final antagonist.
- Magic/Espers still disappear at the end.
- Leo, Rachel and Darill remain dead.
- Vael is a War of the Magi-era human mage, not the creator of the Espers, Warring Triad, Kefka or the Empire.
- K-01 strongly implies Kefka but is not used to excuse his actions.
- C-07 is Celes.
- Leo's petitions add compatible history; they do not make him a hidden rebel mastermind.
- Shadow/Clyde and Relm remain a story of implication and evidence, not a blunt exposition reveal.
- If Shadow died at the Floating Continent, he stays dead. A shorter Relm-only branch replaces the full confrontation.
- Cyan does not become king of restored Doma.
- Terra does not discover a new Esper destiny after Mobliz.
- Edgar remains king; Sabin does not replace him.
- Gogo's identity is not revealed.
- Umaro does not gain fluent dialogue.
- No multiverse, time travel, hidden fourth deity or post-Kefka playable chapter in the Expanded Edition branch.

## 5. Visual production rule

The spreadsheet is the visual source of truth.
Every generation/redraw must carry forward its row's **Continuity Anchors** and respect its palette family.

AI-generated material is concept/reference art by default.
Final ROM art must be cleaned into the native FFVI tile/sprite/palette constraints after the technical audit.

Global restrictions:

- no photorealism;
- no 3D-render look;
- no modern anime rendering;
- no anti-aliased soft painting;
- no cyberpunk neon;
- no modern weapons/technology;
- no oversized empty rooms;
- no visual effect that obscures gameplay readability.

## 6. Balance lock

The expansion is **vanilla-plus**, not a hardtype/kaizo mod.

- Normal WoR mobs generally sit in the Lv30–44 range.
- Cradle enemies generally sit in the Lv46–49 range.
- Midgame optional bosses target roughly 36k–58k single-phase HP.
- Encounters above the SNES single-monster HP comfort zone use phase/formation structure rather than arbitrary HP inflation.
- New weapons do not exceed vanilla iconic top-tier equipment simply to create power creep.
- New armor and relics are specialist sidegrades or character-identity rewards.
- Unique arc rewards are not repeat-farm drops.
- Any optional ASM-enhanced relic effect has a stat/passive fallback.

Exact numbers may move during QA **inside these locked ranges**.

## 7. What is deliberately NOT locked yet

Only technical implementation data remains open:

- exact ROM offsets and free-space allocations;
- exact event-bit numbers;
- exact map IDs, tileset IDs and palette indices;
- exact monster/item slot IDs;
- final text-bank placement and byte budgets;
- exact native animation indices;
- ASM addresses/hooks;
- tool/patch compatibility details for Rev 1.

These cannot be responsibly frozen before auditing the target ROM and tools.
They are not creative-design changes.

## 8. Change-control rule

After v1.2, a creative change requires all of the following:

1. identify the locked row/rule being changed;
2. explain why the existing design fails in gameplay/canon/technical implementation;
3. update every dependent sheet/document;
4. increment the design version;
5. preserve a changelog.

No asset should be redesigned from memory. No dialogue arc should be rewritten from memory. No new lore should be inserted ad hoc during ROM work.

**Next phase after this lock:** Rev 1 technical audit only.
