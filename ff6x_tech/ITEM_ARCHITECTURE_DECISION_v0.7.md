# TECH v0.7 — ITEM / EQUIPMENT ARCHITECTURE AUDIT (decision report)

**AUDIT ONLY — nothing implemented. No architecture chosen. `ITEM_EXPANSION` (FA:0000–FA:FFFF) stays `blocked` in
`allocations.json` until you approve.** No ROM byte changed (v0.6.1 hashes asserted by the builder).

Sources: clean Rev 1 ROM (`057ADA1C…`), ff6dis disassembly (used as oracle; C0/C2/C3 inline addresses match Rev 1 at every
spot-check, **bank C1 does not** — Rev 1 addresses there must be re-derived before any patch), `audits/item_usage_audit.json`
(per-ID references), locked `Content_Data_v1.3` (Weapons / Armor / Relics / Balance_Guardrails / Equipment_Art_Prompts),
Master Design Bible §14–§18. Machine-readable: `audits/ITEM_MAPPING_PROPOSAL_v0.7.json`.

## 1. Rev 1 facts that decide the architecture
| Fact | Evidence |
|---|---|
| Item ID = 1 byte; **every ID `$00–$FE` is a real vanilla item**, `$FF` = Empty **and** Unarmed | `.enum ITEM` (common/const.inc:117); usage audit: every ID referenced |
| Type ranges: weapons `$00–$59`, shields `$5A–$68`, helmets `$69–$83`, armor `$84–$A2`, tools `$A3–$AA`, throw `$AB–$AF`, relics `$B0–$E6`, consumables `$E7–$FE` | enum + ItemProp type bits |
| ItemProp D8:5000 (PC 185000) 256×30 B, packed against GenjuProp D8:6E00; ItemName D2:B300–D2:BFFF 256×13 (byte 0 = icon); ItemDescPtrs ED:7AA0 packed against CharProp | data/item_prop.asm, text/item.asm — **no table can grow in place** |
| Inventory WRAM `$1869–$1968` IDs + `$1969–$1A68` qty (max 99, `cmp #MAX_ITEM_QTY` in GiveItem C0/ACFC and battle/menu qty code) | field/event.asm GiveItem C0/ACFC |
| Equipment: 6 one-byte slots per character record `$1600+37n` +`$1F…$24` (16 records) | notes/field-ram.txt |
| Save = WRAM `$1600–$1FFF` (`$0A00` B) copied per slot to SRAM `$306000/$306A00/$307400`; 16-bit checksum of `$1600–$1FFD` at `$1FFE` | menu/save.asm CopyGameDataToSRAM C3/151D, CalcSaveSlotChecksum C3/19D1 |
| Battle inventory `wItemList` 7E:2686 = (256 + 8 hand slots) × 5 B, ID 1 byte; Tools/Throw list 7E:4005 (built in C1) | battle/battle_common.inc:51, party.asm InitInventory C2/546E, battle_end UpdateSRAM C2/4936, btlgfx_ram.inc:212 |
| Shops C4:7AC0: 9 B per shop, 8 one-byte item IDs | data/shop_prop.asm |
| Chests ED:8634: 5 B, contents = 1-byte item ID | field/player.asm CheckTreasure |
| Steal/drop CF:3000 (4 one-byte IDs per monster), Metamorph C4:7F40, Colosseum DF:B600 **indexed by wagered item ID** (256 rows) | battle/init_2.asm:19, win.asm:220, target_effect.asm:321, menu/colosseum.asm:835 |
| Event `$80` give / `$81` take: 1-byte operand; GiveItem's empty-slot search is unbounded | field/event.asm:2992–3036 |
| WeaponAnimProp EC:E400: 93×8 B indexed by **weapon ID + 1** (valid only for `$00–$59`; `$5B/$5C` = Atma) | battle/init_attacker.asm:355 |
| **Hard-coded ID logic**: spear Jump ×2 = ID range `$1D–$24` (C2:1512); Tools `$A3–$AA`; ThrowToolsItemTbl C2:2708 (`$A4 $A5 $AB $AC $AD`); Inviz/Shadow Edge `$AE/$AF`; Ogre Nix `$17`; Cursed→Paladin Shield `$66→$67`; Umaro `$C5/$C6`; Atma/Soul Sabre/Dice `$1C/$16/$51/$52` (power "???"); Striker `$29` (Colosseum Shadow); Tintinabar `$E5`; Sprint Shoes `$E6` threshold; Genji Glove/Gauntlet/Merit Award `$D1/$D0/$DA` (reequip prompt); field-use consumables (individual ID compares, menu/item.asm); ImpItem list ED:82E4 | battle_cmd.asm, init_target.asm, win.asm, menu/item.asm, equip.asm (research report §4) |
| Arrange (menu) rebuilds the inventory only from the 17 icon chars in C3:26F5 — any other icon is dropped | field_menu.asm:2195–2270 (verified) |
| Rare (key) items: 20 used (event bits `$1D0–$1E3` → `$1EBA–$1EBC.3`); the EN list reads all 24 bits of `$1EBA–$1EBC` into a 20-entry buffer (7E:9D89), names block holds 20 | menu/item.asm:1101–1141; `$1E4–$1E7` have no script refs but setting one overflows the buffer → needs the list extension |
| Candidate unused saved WRAM (unproven): `$1E1D–$1E3F` (35 B: no reference; new-game clear stops at `$1E1C`); `$1CF8–$1D27` (48 B: EN only writes it at new game, readers are JP-only); `$1DD6–$1DDC` is **not** a candidate (event cmds `$B7–$B9` address `$1DC9,y`) | field/init.asm:129–152, field/event.asm:3929–4652; must be audited like event bits before use |

## 2. Demand from the locked design
* **39 equipment concepts**: 13 weapons, 7 body armor, 4 helmets, 2 shields, 13 relics (stats inside BAL-07/08 envelopes).
* Locked rules that matter: BAL-16 one signature reward per arc, **no repeat farming**; BAL-17 signature equipment
  **not from steal/drop** (chest/boss/quest only); BAL-09/18 ASM-enhanced relic effects are optional with stat fallback;
  Equipment_Art_Prompts: "ROM uses existing weapon category/icon unless UI expansion is later approved".
* Also locked (not part of the 39, same ID problem): **8 new consumables** (Gaia Tonic, Aether Flask, Phoenix Ash, Null Dust,
  Iron Ration, Remedy+, Beacon Flare, Magitek Cell — some sold in rebuilt shops) and **5 key items** (Darill's Token,
  Concord/Cinder/Triune Sigil, Broken Seal).
* Free 1-byte IDs: **0**.

## 3. What each architecture has to touch
| Subsystem (reads/writes an item ID) | A: reassign vanilla IDs | B: true extended ID engine (9-bit, all item kinds) | C: hybrid "signature equipment bank" (9-bit IDs for the 39 equipment only, limited sources) |
|---|---|---|---|
| ItemProp / name / description lookup (battle C2:2B63, menu ×30 multiply, ~15 display routines) | data only | all lookups 16-bit → new tables in FA | same as B for ID ≥ $100 (one shared lookup helper) |
| Inventory `$1869/$1969` + battle `wItemList` | none | ID bit 8 per slot (qty bit 7 or 32-B bitmap) at every read/write | same as B |
| 6 equip slots × 16 characters | none | +96 bits (12 B) of saved RAM, every equip read (UpdateEquip C2:0E77, menus, optimum, battle hand swap) | same as B |
| Event give/take `$80/$81` | none | new 9-bit form | new 9-bit give/take via the accepted v0.2 event hook |
| Chests ED:8634 | edit contents | contents byte + spare flag bit (unverified) | **not used**: ext items come from event chests (v0.3 pipeline) |
| Shops C4:7AC0 / sell menu | edit lists | shop format + menu buy/sell | ext items not sold; sell/wager lists skip them |
| Steal / drop / Metamorph CF:3000, C4:7F40 | clean up reassigned IDs | table format change | **not used** (BAL-17) |
| Colosseum DF:B600 | reassigned ID's row applies to the new item (must hide/blank) | 2nd table or block | ext items blocked from wager list |
| Throw / Tools / battle Item | n/a for equipment | extend lists | excluded (Moonless not throwable unless added) |
| WeaponAnimProp (weapon ID + 1) | reuse the replaced weapon's entry (same family) | new table + index math | same as B for 13 weapons |
| Spear Jump ×2 range `$1D–$24` | kept if the spear replaces a spear | extend check | extend check for 2 spears |
| Arrange / icon table | reuse icons | ext icons must be in table | same (existing icons) |
| Save / SRAM | **unchanged** | +12 B (+32 B if bitmap) in audited free saved bytes, or layout change | same as B |
| Est. new 65816 code | ~0 | **6–12 KB**, ~100+ sites (C0, C1*, C2, C3, EE) | **2–5 KB**, ~45–65 sites (C0, C1*, C2, C3) |
| QA burden | medium (every displaced location) | very high (all menus, shops, battle, steal/drop, Colosseum) | high but bounded (equip/menus/battle/save for ext IDs) |

\* C1 = btlgfx; Rev 1 offsets differ from the disassembly and must be re-derived.

## 4. The options
### A — Reassign vanilla IDs
39 vanilla items become the new ones (same type/family so WeaponAnimProp, spear range and icons keep working).
* **Displaces 39 vanilla items** and their content: first-candidate set below = 59 shop slots, 19 chests, 11 steals,
  7 drops, 6 Metamorph results, 11 Colosseum prize entries (113 references) — each must be re-pointed to another item.
* Relics are the worst case: vanilla relics are functionally unique, so 13 vanilla relic effects disappear.
* Old saves: any held reassigned ID silently becomes the new item. SRAM unchanged. Engine: none.
* Conflicts with "preserve vanilla" (rule 18) and Design Bible principle 8 ("Lightbringer, Ragnarok… remain meaningful") only
  partly — the candidates avoid iconic gear, but mid-tier gear and shops change.

### B — True extended item engine
9-bit (or 16-bit) IDs for every item kind; new items can come from any source.
* Zero vanilla displacement; supports the 8 consumables and shop sales too.
* Largest change in the project so far (all item paths incl. battle Item/Throw/Tools, shops, steal/drop, Metamorph,
  Colosseum, menus, save). Very high regression risk; save extension required.

### C — Hybrid "signature equipment bank" (equipment-only extension)
IDs `$100–$13F` (64, 39 used) only for **equipment** (weapon/shield/helmet/armor/relic). Delivered only by event
reward (boss / quest / event chest) — exactly the locked sources; never sold, stolen, dropped, morphed, wagered or thrown.
* Zero vanilla items displaced; matches BAL-16/17 by construction (unique, non-farmable).
* Engine limited to: lookups, inventory/equip storage, equip/status menus, battle equipment use (stats, weapon animation,
  hand swap), event give/take, filters that keep ext IDs out of shop/sell/Colosseum/Throw lists, spear check.
* Needs 12 B of proven-free saved RAM (equip high bits; candidates `$1E1D–$1E3F`, `$1CF8–$1D27`) + inventory high bit (qty bit 7 with all qty sites masked, or a
  32-B bitmap). Old saves compatible **if** those bytes are proven unused/zero (to audit first).
* Does **not** cover the 8 consumables (sold in shops / usable in battle) → separate decision D2.

### C-min — fallback if no engine work is accepted (not recommended)
Reassign only ~8–13 arc-signature items (A for those) and cut/merge the rest — **changes locked content; needs explicit
creative approval**, listed only for completeness.

## 5. Comparison
| | A | B | C |
|---|---|---|---|
| Vanilla items displaced | 39 (113 references) | 0 | 0 |
| New ASM | ~0 | 6–12 KB | 2–5 KB |
| Save / SRAM | unchanged; old saves remap items | +12–44 B saved RAM or new layout | +12–44 B saved RAM (audit) |
| Old saves | load, items silently change | load if extension bytes are free/zero | load if extension bytes are free/zero |
| Creative fidelity (39 as true equipment) | yes | yes | yes |
| Locked sources (chest/boss/quest) | yes | yes | yes (event-delivered) |
| Shops / steal / drop for new gear | possible | possible | not possible (not wanted by BAL-17) |
| New consumables (8) | need 8 more reassigned IDs | covered | **not covered → D2** |
| Regression risk | low–medium | very high | medium |
| User QA | medium | very high | high, bounded |
| Reversibility | data only | large | medium (one module) |

## 6. Mapping of all 39 locked concepts
All 39 stay **true equipment** with their locked stats, users, visuals and sources in every option. Under C none
reuses a vanilla ID; none becomes a key item. "A" shows the first candidate if A were chosen (same family, no
hard-coded behaviour, fewest sources — final pick needs review) and the vanilla content it would displace.
Common to every row under C: engine = shared signature-bank module; SRAM = shared +12 B (+ inventory bit);
menu = equip/item/status show it, sell/Colosseum/Throw lists skip it; shop/drop/steal/Metamorph/Colosseum = none.

| Code | Concept (slot · users) | True equip? | A: reuses vanilla ID → displaced | C: ID · delivery | Upgrade / key? | Effect implementation | Risk (C) |
|---|---|---|---|---|---|---|---|
| EQ-W01 | **Tempered Edge** (sword · Terra/Celes/Edgar/Locke) | yes | `$15` Falchion → shop ×1, colosseum prize ×1 | `$100` · Narshe forge quest | optional reforge (approval) / no | data | low-medium |
| EQ-W02 | **Imperial Saber** (sword · Celes) | yes | `$19` Scimitar → drop ×2, colosseum prize ×1 | `$101` · Vector Annex chest | no / no | data | low-medium |
| EQ-W03 | **Leo's Blade** (sword · Terra/Celes/Edgar/Locke) | yes | `$11` Break Blade → chest ×1, steal ×1, colosseum prize ×1 | `$102` · Celes arc rare branch | no / no | data (Holy = element bit $20) | low-medium |
| EQ-W04 | **Raider Knife** (knife · Locke) | yes | `$05` Assassin → chest ×1, metamorph ×1, colosseum prize ×1 | `$103` · Reconstruction chain | optional reforge (approval) / no | data (weapon special THIEFKNIFE, attacker effect $01) | low-medium |
| EQ-W05 | **Sandpiercer** (spear · Edgar/Mog) | yes | `$20` Partisan → shop ×1, steal ×1 | `$104` · Figaro Foundry | no / no | data; Jump x2 needs the spear ID range check C2:1512 (A: kept by staying in $1D-$24; B/C: extend check) | medium |
| EQ-W06 | **Duncan Claw** (claw · Sabin) | yes | `$55` Kaiser → shop ×2 | `$105` · Master's Echo | no / no | data | low-medium |
| EQ-W07 | **Moonless** (ninja blade · Shadow) | yes | `$26` Kodachi → shop ×1 | `$106` · Bandit's Hollow | no / no | data; Throw-able only if the Throw list handles the ID (A: yes; C: no unless added) | medium |
| EQ-W08 | **Doma Edge** (katana · Cyan) | yes | `$2E` Tempest → chest ×1, steal ×1 | `$107` · Doma rebuilt smith | optional reforge (approval) / no | data (Bushido flag) | low-medium |
| EQ-W09 | **Darill's Dirk** (knife · Setzer/Locke) | yes | `$08` Graedus → drop ×2, colosseum prize ×1 | `$108` · Sky Graveyard | no / no | data | low-medium |
| EQ-W10 | **Magister Rod** (rod · Strago/Relm) | yes | `$39` Pearl Rod → shop ×1, chest ×1 | `$109` · Forgotten Age | no / no | data | low-medium |
| EQ-W11 | **Concord Brush** (brush · Relm) | yes | `$3F` Magical Brsh → chest ×1 | `$10A` · Sanctuary of Concord | no / no | data | low-medium |
| EQ-W12 | **Gale Lance** (spear · Mog/Edgar) | yes | `$1F` Stout Spear → shop ×2, drop ×1 | `$10B` · Beacon quest | no / no | data; Jump x2 spear range as EQ-W05 | medium |
| EQ-W13 | **Echo Dagger** (knife · Gogo) | yes | `$07` SwordBreaker → shop ×1, steal ×2, colosseum prize ×1 | `$10C` · Cradle of Silence | no / no | data | low-medium |
| EQ-A01 | **Royal Gear** (body · Edgar/Sabin) | yes | `$95` DiamondArmor → shop ×2 | `$10D` · Brass Colossus (Figaro arc) | no / no | data | low-medium |
| EQ-A02 | **Imperial Mantle** (body · Celes/Terra) | yes | `$91` Light Robe → shop ×1 | `$10E` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A03 | **Magister Robe** (body · Terra/Celes/Relm/Strago/Gogo) | yes | `$97` Tao Robe → shop ×1, colosseum prize ×1 | `$10F` · Archive Guardian (First Magi) | no / no | data (MP +12.5/25% relic bits) | low-medium |
| EQ-A04 | **Ashen Mail** (body · Edgar/Cyan/Setzer) | yes | `$8C` Mithril Mail → shop ×2, steal ×1, metamorph ×1 | `$110` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A05 | **Concord Vest** (body · Locke/Shadow/Gau/Mog/Gogo) | yes | `$96` Dark Gear → shop ×2 | `$111` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A06 | **Doma Plate** (body · Cyan/Edgar/Celes/Terra) | yes | `$98` Crystal Mail → shop ×1, chest ×1, metamorph ×1 | `$112` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A07 | **Falcon Jacket** (body · Setzer/Locke/Shadow) | yes | `$8E` Mirage Vest → colosseum prize ×1 | `$113` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A08 | **Child's Ribbon** (helmet · Terra/Relm/Celes) | yes | `$70` Coronet → chest ×1, colosseum prize ×1 | `$114` · not specified in Armor sheet (placed by arc design) | no / no | data (status immunity words) | low-medium |
| EQ-A09 | **Doma Kabuto** (helmet · Cyan) | yes | `$7C` Diamond Helm → shop ×3, steal ×1, colosseum prize ×1 | `$115` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A10 | **Engineer Goggles** (helmet · Edgar/Setzer) | yes | `$79` Mystery Veil → shop ×2 | `$116` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A11 | **Magi Circlet** (helmet · magic users) | yes | `$75` Tiara → shop ×2 | `$117` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A12 | **Concord Shield** (shield · broad) | yes | `$63` Crystal Shld → shop ×1, metamorph ×1 | `$118` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-A13 | **Ashguard** (shield · heavy users) | yes | `$5F` Diamond Shld → shop ×3 | `$119` · not specified in Armor sheet (placed by arc design) | no / no | data | low-medium |
| EQ-R01 | **Runic Crest** (relic · Celes) | yes | `$B9` Guard Ring → shop ×2 | `$11A` · Celes arc (Magitek Praetor) | no / no | data + optional ASM (BAL-18 stat fallback) | medium |
| EQ-R02 | **Maduin's Locket** (relic · Terra) | yes | `$C2` Cursed Ring → metamorph ×2, colosseum prize ×1 | `$11B` · Terra arc (Magi-Eater) | no / no | data + optional ASM (fallback MP +25%) | medium |
| EQ-R03 | **Doma Crest** (relic · Cyan) | yes | `$D4` Beads → shop ×1, chest ×2 | `$11C` · Cyan arc (Miasma Regent) | no / no | data + optional ASM | medium |
| EQ-R04 | **Keepsake Ring** (relic · Shadow/Relm) | yes | `$E1` Back Guard → shop ×1, chest ×2, steal ×1 | `$11D` · Shadow/Relm arc (Guiltshade) | no / no | data (status immunity; Memento-Ring-like) | low-medium |
| EQ-R05 | **Darill's Coin** (relic · Setzer) | yes | `$D6` Coin Toss → chest ×1 | `$11E` · Setzer arc (Sky Reaver) | no / no | data + optional ASM | medium |
| EQ-R06 | **Memorial Band** (relic · all) | yes | `$BE` True Knight → shop ×4, chest ×1 | `$11F` · Vector memorial | no / no | data | low-medium |
| EQ-R07 | **Gale Pin** (relic · all) | yes | `$B7` Barrier Ring → shop ×4, chest ×1, drop ×1 | `$120` · Coast beacon | no / no | data | low-medium |
| EQ-R08 | **Beastheart** (relic · Gau) | yes | `$B6` Fairy Ring → shop ×4, chest ×1 | `$121` · Gau side content | no / no | data + optional ASM | medium |
| EQ-R09 | **Painter's Lens** (relic · Relm) | yes | `$C7` Sneak Ring → shop ×1, chest ×1, steal ×2 | `$122` · Relm extension | no / no | data (RELIC_EFFECT3 INC_SKETCH_RATE, Beret's bit) | low-medium |
| EQ-R10 | **Elder's Seal** (relic · Strago) | yes | `$B1` Star Pendant → shop ×3, chest ×1, steal ×1 | `$123` · Ancient lore | no / no | data (MP_PLUS_12) | low-medium |
| EQ-R11 | **Engineer's Badge** (relic · Edgar) | yes | `$E3` Sniper Sight → shop ×5, chest ×1 | `$124` · Figaro | no / no | data + optional ASM | medium |
| EQ-R12 | **Master's Cord** (relic · Sabin) | yes | `$D5` Black Belt → shop ×4, drop ×1 | `$125` · Duncan | no / no | data + optional ASM | medium |
| EQ-R13 | **Legacy of the Magi** (relic · Terra/Celes/Relm/Strago/Gogo) | yes | `$E2` Gale Hairpin → shop ×1, chest ×1 | `$126` · Vael Unbound (superboss) | no / no | data (MP_PLUS_25) | low-medium |

Notes per row: ASM-optional relic effects (Runic Crest, Maduin's Locket, Doma Crest, Darill's Coin, Beastheart, Engineer's
Badge, Master's Cord) ship first with their BAL-18 stat fallback; the enhancement patches are separate later modules.
Sandpiercer / Gale Lance need the spear Jump ×2 check extended under B/C (free under A). Moonless is not throwable under C
unless the Throw list is extended. Armor sources not listed in the Armor sheet are placed by the arc design (Royal Gear =
Brass Colossus, Magister Robe = Archive Guardian per Design Bible §14).

## 7. Recommendation (needs your approval — not chosen)
**C — signature equipment bank**, with these tradeoffs:
* + keeps every vanilla item, shop, chest, steal/drop and Colosseum row unchanged; old saves stay valid (after the
  free-RAM audit); all 39 concepts remain true equipment exactly as locked; non-farmable by construction (BAL-16/17).
* + about half the engine scope of B; one module, testable with a 3-item proof (1 weapon, 1 armor, 1 relic).
* − still real 65816 work in C0/C1/C2/C3 (C1 needs Rev 1 address re-derivation); needs 12+ B of proven-free saved RAM.
* − new gear cannot be sold, stolen, dropped, wagered or thrown (consistent with the lock; Moonless throw is a gap).
* − does not solve the 8 consumables (D2).
Choose **B** instead if you want new items in shops/steal/drop or all 8 consumables in one system and accept the largest
risk; choose **A** only if zero engine work matters more than keeping vanilla items.

## 8. Decisions needed
| # | Decision | Options |
|---|---|---|
| D1 | Equipment architecture | A / B / **C (recommended)** / C-min |
| D2 | 8 new consumables | (a) extend C to consumables + shops/battle Item (≈ B scope), (b) reassign 8 vanilla consumable IDs, (c) defer |
| D3 | 5 key items | rare-item extension: relocate names/descs, enlarge the 20-entry list buffer, then use audited bits `$1E4–$1E7` (+ more) — small, independent of D1 |
| D4 | Smith-sourced gear (Narshe forge, Figaro Foundry, Doma rebuilt smith) | event gift/purchase (works with C) vs real shop (needs shop extension) |
| D5 | ASM relic enhancements | ship stat fallback first (BAL-18), add patches later |
| D6 | Optional reforge-style delivery for Tempered Edge / Raider Knife / Doma Edge | default no (locked sources unchanged) |

## 9. If C is approved — TECH v0.7 proof plan (not started)
1. Saved-RAM allocator audit (like the event-bit audit) for 12–44 B; record in `allocations.json`.
2. Consumer list with Rev 1 PC/SNES for every ID site (C1 re-derived), each patch with consumer/reason.
3. Proof build: 3 ext items (`$100` weapon, `$101` body armor, `$102` relic) given by a QA event; equip, battle stats/animation,
   menus, Arrange, save/load, old-save load; vanilla regression (576 formations, menus, shops).
4. User runtime QA, then production data for the 39.
