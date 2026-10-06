# maps/celes_outer_v092 - TECH v0.9.2 QA enabler map $1A2 (Vector Outer Ward placeholder)

QA-only proof map for the Celes enablers (not CONTENT v1.0 art or text). See map.json `status` / `rooms`.
* E1: reached from the World of Ruin (map $001) tile (146,202) east of Kefka's Tower (short entrance with SET_PARENT);
  the south exit loads the parent map ($1FF) = back on the world map next to the parked Falcon.
* E6: palette $30 = PAL-01 Imperial Ruins variant derived from vanilla map palette $18 (palettes/v092).
* E7: Vale uses sprite palette slot 7, loaded with the new sprite palette $20 by the startup event.
* E8: memorial wall (10-12,10) and archive door (19-20,10) tiles are set by the startup event from the persistent
  event bits (EXP_CELES_DONE, EXP_CELES_RECORDS_CHOSEN / _PRESERVED, EXP_GRAVES_DONE).
