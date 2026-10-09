# CONSUMABLE ACQUISITION MAP — TECH v0.9

Locked: *some consumables are sold in rebuilt shops*. Which ones, the shops and every other source are DERIVED placements for future story / reconstruction events (no story event is implemented in v0.9 — hard stop). The QA build reaches the two extended shops from the QA hub.

| id | name | source | planned source | event / shop symbol | conditions | one-time | GP |
|---|---|---|---|---|---|---|---|
| $127 | Gaia Tonic | shop | rebuilt shops (World of Ruin reconstruction) | `EXT_SHOP_REBUILT_GENERAL` | PREREQ_RECONSTRUCTION_SHOPS | no | 1500 |
| $128 | Aether Flask | event_chest | story chests / quest rewards (not sold) | `EV_CHEST_AETHER_FLASK` | PREREQ_TBD_ARC_DESIGN | yes | — |
| $129 | Phoenix Ash | boss_reward | arc boss rewards (not sold) | `EV_BOSS_PHOENIX_ASH` | PREREQ_TBD_ARC_DESIGN | yes | — |
| $12A | Null Dust | shop | rebuilt shops (World of Ruin reconstruction) | `EXT_SHOP_REBUILT_GENERAL` | PREREQ_RECONSTRUCTION_SHOPS | no | 800 |
| $12B | Iron Ration | shop | rebuilt shops (World of Ruin reconstruction) | `EXT_SHOP_REBUILT_GENERAL` | PREREQ_RECONSTRUCTION_SHOPS | no | 250 |
| $12C | Remedy+ | shop | rebuilt shops (late reconstruction) | `EXT_SHOP_REBUILT_LATE` | PREREQ_RECONSTRUCTION_LATE | no | 3000 |
| $12D | Beacon Flare | quest_reward | Beacon quest (not sold) | `EV_REWARD_BEACON_FLARE` | PREREQ_BEACON_QUEST | yes | — |
| $12E | Magitek Cell | quest_reward | Magitek research / Vector arc (not sold) | `EV_REWARD_MAGITEK_CELL` | PREREQ_VECTOR_ARC | yes | — |

## Extended shops (XShopProp ids $80+, event command $9B)

| shop | symbol | items (9-bit ids) | note |
|---|---|---|---|
| $80 | `EXT_SHOP_REBUILT_GENERAL` | $127, $12B, $12A, $E9, $EB, $F0, $F5, $F7 | rebuilt general store: Gaia Tonic, Iron Ration, Null Dust + vanilla Potion, Tincture, Fenix Down, Remedy, Tent |
| $81 | `EXT_SHOP_REBUILT_LATE` | $12C, $127, $12B, $12A, $E9, $F0, $F5, $FD | rebuilt late store: Remedy+ (late game) + the general consumables + vanilla Potion, Fenix Down, Remedy, Warp Stone |

Excluded channels (validated): Steal, Drop, Metamorph, Colosseum (wager and prize), Throw. Enemies never use them. Not equippable. The 4 sold consumables can be sold back (price / 2); the 4 unsold ones cannot be sold.
