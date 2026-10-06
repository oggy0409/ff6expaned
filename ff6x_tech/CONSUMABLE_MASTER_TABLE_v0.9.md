# CONSUMABLE MASTER TABLE — TECH v0.9

Generated from `items/production_v09/consumables.json` (single source of truth; `tools/consumable_docs_v09.py`).
**Locked** (ITEM_ARCHITECTURE_DECISION_v0.7.md §2, from the Creative Lock): the 8 names and that some are sold in rebuilt shops. **Every other field is DERIVED** (the Creative Lock / Tech Gate spreadsheets are not in the project) and listed per item under *Derived*; these need creative confirmation.

| id | code | name (display) | use | targeting | effect (record) | price | sold / sell | animation |
|---|---|---|---|---|---|---|---|---|
| $127 | CN-01 | Gaia Tonic (Gaia Tonic) | battle+field | ALL_ALLIES ($2E) | HP +240; undead inverted | 1500 | yes / 750 | item $E9 (Potion) |
| $128 | CN-02 | Aether Flask (AetherFlask) | battle+field | ONE_ALLY ($01) | MP +250 | — | no / no | item $EC (Ether) |
| $129 | CN-03 | Phoenix Ash (Phoenix Ash) | battle+field | ONE_ALLY ($01) | HP +8/16 max; cures DEAD; undead inverted | — | no / no | item $F0 (Fenix Down) |
| $12A | CN-04 | Null Dust (Null Dust) | battle | ONE_ENEMY ($41) | cures REGEN/HASTE/SHELL/SAFE/REFLECT/FLOAT | 800 | yes / 400 | item $F5 (Remedy) |
| $12B | CN-05 | Iron Ration (Iron Ration) | battle+field | ONE_ALLY ($01) | HP +200; cures POISON; undead inverted | 250 | yes / 125 | item $FE (Dried Meat) |
| $12C | CN-06 | Remedy+ (Remedy+) | battle+field | ONE_ALLY ($01) | cures BLIND/ZOMBIE/POISON/IMP/PETRIFY/CONDEMNED/SILENCE/BERSERK/CONFUSE/SAP/SLEEP/SLOW/STOP | 3000 | yes / 1500 | item $F5 (Remedy) |
| $12D | CN-07 | Beacon Flare (BeaconFlare) | battle | ALL_ENEMIES ($6E) | damage 255 (FIRE) | — | no / no | SPELL:FIRE_2 |
| $12E | CN-08 | Magitek Cell (MagitekCell) | battle | ALL_ALLIES ($2E) | MP +120 | — | no / no | item $ED (X-Ether) |

Common to all 8: blank icon (as vanilla items), quantity 1–99 per stack (vanilla rule), not stealable, not dropped, not a Metamorph result, not a Colosseum wager, not throwable, not equippable, never used by enemies (exclusion rule v0.9, validated by the builder). The vanilla item with the same low byte is a katana ($27–$2E) that the Item command can never use, so the battle code identifies the consumable without ambiguity.

## $127 Gaia Tonic (CN-01, `CN_GAIA_TONIC`)

* Description: *Restores HP to the party / (menu: one member)*
* Record (30 bytes): `66 00 00 00 00 00 00 00 00 00 00 00 00 00 2E 00 00 00 00 0A F0 00 00 00 00 00 00 FF DC 05`
* Acquisition: shop — rebuilt shops (World of Ruin reconstruction) (`EXT_SHOP_REBUILT_GENERAL`, PREREQ_RECONSTRUCTION_SHOPS, repeatable (shop))
* Derived: effect (party HP restore: power 240 = 120 HP per member - the vanilla engine halves an item's power when it hits several targets; between Tonic 50 and Potion 250 per target); targeting; price 1500; anim template Potion; menu use = one member (the vanilla field menu has no party-wide item use)

## $128 Aether Flask (CN-02, `CN_AETHER_FLASK`)

* Description: *Aether Flask / Restores a lot of MP*
* Record (30 bytes): `66 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 10 FA 00 00 00 00 00 00 FF 02 00`
* Acquisition: event_chest — story chests / quest rewards (not sold) (`EV_CHEST_AETHER_FLASK`, PREREQ_TBD_ARC_DESIGN, one-time)
* Derived: effect (MP restore power 250, between Ether 150 and X-Ether full); not sold (MP economy); anim template Ether; display name AetherFlask (12-char field)

## $129 Phoenix Ash (CN-03, `CN_PHOENIX_ASH`)

* Description: *Revives one ally / with half of max HP*
* Record (30 bytes): `66 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 AA 08 80 00 00 00 00 00 FF 02 00`
* Acquisition: boss_reward — arc boss rewards (not sold) (`EV_BOSS_PHOENIX_ASH`, PREREQ_TBD_ARC_DESIGN, one-time)
* Derived: effect (revive with 8/16 = 50% HP; Fenix Down is 2/16); not sold; anim template Fenix Down

## $12A Null Dust (CN-04, `CN_NULL_DUST`)

* Description: *Strips Haste/Safe/Shell/ / Regen/Reflect/Float*
* Record (30 bytes): `26 00 00 00 00 00 00 00 00 00 00 00 00 00 41 00 00 00 00 20 00 00 00 EA 80 00 00 FF 20 03`
* Acquisition: shop — rebuilt shops (World of Ruin reconstruction) (`EXT_SHOP_REBUILT_GENERAL`, PREREQ_RECONSTRUCTION_SHOPS, repeatable (shop))
* Derived: function (Dispel-like removal of the six beneficial statuses; read from the name 'Null'); battle only; targeting (one target, enemy by default); price 800; anim template Remedy

## $12B Iron Ration (CN-05, `CN_IRON_RATION`)

* Description: *Restores HP and / cures Poison*
* Record (30 bytes): `66 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 2A C8 04 00 00 00 00 00 FF FA 00`
* Acquisition: shop — rebuilt shops (World of Ruin reconstruction) (`EXT_SHOP_REBUILT_GENERAL`, PREREQ_RECONSTRUCTION_SHOPS, repeatable (shop))
* Derived: effect (HP power 200 + Poison cure; Dried Meat is 150 HP); price 250; anim template Dried Meat

## $12C Remedy+ (CN-06, `CN_REMEDY_PLUS`)

* Description: *Cures all bad status / incl. Zombie/Muddle/Stop*
* Record (30 bytes): `66 00 00 00 00 00 00 00 00 00 00 00 00 00 01 00 00 00 00 20 00 67 F9 14 00 00 00 FF B8 0B`
* Acquisition: shop — rebuilt shops (late reconstruction) (`EXT_SHOP_REBUILT_LATE`, PREREQ_RECONSTRUCTION_LATE, repeatable (shop))
* Derived: effect (Remedy set + Zombie, Condemned, Berserk, Muddle, Sleep, Slow, Stop); price 3000 (Remedy 1000); anim template Remedy

## $12D Beacon Flare (CN-07, `CN_BEACON_FLARE`)

* Description: *Beacon Flare / Fire damage to all foes*
* Record (30 bytes): `26 00 00 00 00 00 00 00 00 00 00 00 00 00 6E 01 00 00 00 00 FF 00 00 00 00 00 00 FF 02 00`
* Acquisition: quest_reward — Beacon quest (not sold) (`EV_REWARD_BEACON_FLARE`, PREREQ_BEACON_QUEST, one-time)
* Derived: function (fire damage to all enemies; read from 'Flare'); power 255 (items have no level scaling and the power is halved over several targets: ~127 per enemy with 2+ enemies, ~255 on one, x2 vs Fire-weak); not sold; anim: vanilla Fire 2 spell animation; display name BeaconFlare (12-char field)

## $12E Magitek Cell (CN-08, `CN_MAGITEK_CELL`)

* Description: *Magitek Cell / Restores the party's MP*
* Record (30 bytes): `26 00 00 00 00 00 00 00 00 00 00 00 00 00 2E 00 00 00 00 10 78 00 00 00 00 00 00 FF 02 00`
* Acquisition: quest_reward — Magitek research / Vector arc (not sold) (`EV_REWARD_MAGITEK_CELL`, PREREQ_VECTOR_ARC, one-time)
* Derived: function (party MP restore: power 120 = 60 MP per member after the multi-target halving; read from 'Cell' = energy); battle only; not sold; anim template X-Ether; display name MagitekCell (12-char field)
