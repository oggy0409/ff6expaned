# maps/map_tech_a — MAP TECH A ($1A0), TECH v0.4 proof map

Placeholder technical content (Magitek-lab legend from the accepted Annex). Built only for target `map-tech`.
New map ID beyond the vanilla range; BG1 layout $160 (F5, via the relocated 1024-entry pointer table),
BG2 = vanilla transparent filler $12A. Events: `events/map_tech_v04/`.

- NPCs (routed through the NPC event vector table): A1 (9,14), A3 (22,14) — visibility switch = vanilla $300 (read-only);
  A2 (20,16) — visible after NPC bit $6FA.
- Trigger: alcove (10,25) → message, pushed back RIGHT.
- Short entrance (16,9) → $1A1 (13,18). Long entrance (15,29) length 1 → $013 (35,43).
