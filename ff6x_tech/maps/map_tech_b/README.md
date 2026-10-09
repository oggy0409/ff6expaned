# maps/map_tech_b — MAP TECH B ($1A1), TECH v0.4 proof map

Composed with the v0.4 `compose` pipeline: 32×32 canvas, a 12×12 room copied from vanilla layouts
$06F (BG1) / $070 (BG2) (art used by map $01E) into new layouts $161 / $162. Tile properties set $07,
graphics/palette from map $01E. Placeholder technical content; target `map-tech` only.

- NPC B1 (11,16): sets $14D MAP_TECH_V04_VISITED_B and NPC bit $6FA.
- Short entrance (13,19) → $1A0 (16,12). Long entrance (19,18) length 0 → $1A0 (13,26).
- Walkability proven with the engine movement rule (direction masks: tables/furniture block movement).
