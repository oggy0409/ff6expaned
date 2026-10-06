# CONSUMABLE BALANCE AUDIT — TECH v0.9

Every v0.9 consumable compared with the vanilla consumables (records read from the clean Rev 1 ROM). Effects run through the vanilla item code, so the vanilla rules apply: items have no level scaling (damage / healing = power with the usual random variance), **power is halved when an item hits several targets**, fractions are in 16ths of max HP / MP. All values are DERIVED (no locked numbers exist for the consumables).

## Vanilla reference

| id | name | use | targeting | effect | price |
|---|---|---|---|---|---|
| $E7 | Rename Card | field | $03 | - | 2 |
| $E8 | Tonic | battle+field | ONE_ALLY | HP +50; undead inverted | 50 |
| $E9 | Potion | battle+field | ONE_ALLY | HP +250; undead inverted | 300 |
| $EA | X-Potion | battle+field | ONE_ALLY | HP +16/16 max; undead inverted | 2 |
| $EB | Tincture | battle+field | ONE_ALLY | MP +50 | 1500 |
| $EC | Ether | battle+field | ONE_ALLY | MP +150 | 2 |
| $ED | X-Ether | battle+field | ONE_ALLY | MP +16/16 max | 2 |
| $EE | Elixir | battle+field | ONE_ALLY | HP +16/16 max; MP +16/16 max; special 04; undead inverted | 2 |
| $EF | Megalixir | battle | ALL_ALLIES | HP +16/16 max; MP +16/16 max; special 04; undead inverted | 2 |
| $F0 | Fenix Down | battle+field | ONE_ALLY | HP +2/16 max; cures DEAD; undead inverted | 500 |
| $F1 | Revivify | battle+field | ONE_ALLY | HP +2/16 max; cures ZOMBIE; undead inverted | 300 |
| $F2 | Antidote | battle+field | ONE_ALLY | cures POISON | 50 |
| $F3 | Eyedrop | battle+field | ONE_ALLY | cures BLIND | 50 |
| $F4 | Soft | battle+field | ONE_ALLY | cures PETRIFY | 200 |
| $F5 | Remedy | battle+field | ONE_ALLY | cures BLIND/POISON/IMP/PETRIFY/SILENCE/SAP | 1000 |
| $F6 | Sleeping Bag | field | ONE_ALLY | HP +16/16 max; MP +16/16 max; cures BLIND/ZOMBIE/POISON/VANISH/IMP/PETRIFY/FLOAT | 500 |
| $F7 | Tent | field | $00 | HP +16/16 max; MP +16/16 max; cures BLIND/ZOMBIE/POISON/VANISH/IMP/PETRIFY/DEAD/FLOAT | 1200 |
| $F8 | Green Cherry | battle+field | ONE_ALLY | cures IMP | 150 |
| $F9 | Magicite | battle | $43 | special 01 | 2 |
| $FA | Super Ball | battle | ALL_ENEMIES | damage 1; special 02 | 10000 |
| $FB | Echo Screen | battle+field | ONE_ALLY | cures SILENCE | 120 |
| $FC | Smoke Bomb | battle | ALL_ALLIES | special 03 | 300 |
| $FD | Warp Stone | battle+field | ALL_ALLIES | special 05 | 700 |
| $FE | Dried Meat | battle+field | ONE_ALLY | HP +150; special 06 | 150 |

## v0.9 consumables

| id | name | use | targeting | effect | per-target effect | price | position |
|---|---|---|---|---|---|---|---|
| $127 | Gaia Tonic | battle+field | ALL_ALLIES ($2E) | HP +240; undead inverted | ~120 HP x party (battle, power 240 halved); 240 on one member in the field | 1500 | party heal between Potion (250 one target) and Megalixir; cheaper than 4 Potions (1200) only in action economy — 1500 GP keeps it a convenience, not a replacement |
| $128 | Aether Flask | battle+field | ONE_ALLY ($01) | MP +250 | MP +250 | not sold | between Ether (150) and X-Ether (full); not sold (MP economy unchanged) |
| $129 | Phoenix Ash | battle+field | ONE_ALLY ($01) | HP +8/16 max; cures DEAD; undead inverted | revive + 8/16 max HP | not sold | Fenix Down (2/16) upgrade; boss reward only, not sold |
| $12A | Null Dust | battle | ONE_ENEMY ($41) | cures REGEN/HASTE/SHELL/SAFE/REFLECT/FLOAT | removes Regen/Haste/Shell/Safe/Reflect/Float from one target | 800 | no vanilla item does this (Dispel-like); battle only; 800 GP |
| $12B | Iron Ration | battle+field | ONE_ALLY ($01) | HP +200; cures POISON; undead inverted | HP +200 + cures Poison | 250 | between Potion (250) and Dried Meat (150) with an Antidote; 250 GP (Potion 300) |
| $12C | Remedy+ | battle+field | ONE_ALLY ($01) | cures BLIND/ZOMBIE/POISON/IMP/PETRIFY/CONDEMNED/SILENCE/BERSERK/CONFUSE/SAP/SLEEP/SLOW/STOP | cures Blind/Zombie/Poison/Imp/Petrify/Condemned/Mute/Berserk/Muddle/Sap/Sleep/Slow/Stop | 3000 | Remedy (Blind/Poison/Imp/Petrify/Mute/Sap) + the rest; 3000 GP vs Remedy 1000; late shop |
| $12D | Beacon Flare | battle | ALL_ENEMIES ($6E) | damage 255 (FIRE) | Fire damage ~127 each (2+ enemies) / ~255 (one), x2 vs Fire-weak | not sold | comparable to an early Fire 2; quest reward, not sold |
| $12E | Magitek Cell | battle | ALL_ALLIES ($2E) | MP +120 | MP +~60 x party (power 120 halved) | not sold | party Ether-lite; reward only, not sold |

## Findings

* No consumable exceeds the vanilla ceiling: Megalixir / Elixir (full HP+MP) and X-Ether remain the strongest restores; Phoenix Ash is stronger than Fenix Down but not purchasable.
* The sold consumables (Gaia Tonic, Iron Ration, Null Dust, Remedy+) are priced at or above the vanilla item they compete with; the strong ones (Aether Flask, Phoenix Ash, Beacon Flare, Magitek Cell) are not sold.
* Beacon Flare is the only offensive consumable usable with the Item command; its damage is capped by the item formula (power 255, no level scaling), so it never outscales magic.
* Multi-target halving is a vanilla engine rule; the party items (Gaia Tonic, Magitek Cell) were given twice the intended per-member power so that each member receives the intended amount in battle. In the field menu (one member) Gaia Tonic heals the full 240.
* Key items have no combat stats (validated: `combat_stats` must be null).
* Review items for creative confirmation: all prices, Gaia Tonic field behaviour (one member), Null Dust function, Beacon Flare power, Remedy+ price/coverage.
