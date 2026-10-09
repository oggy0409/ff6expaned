# KNOWN_QA_ISSUE_v0.3.1 — Magitek field sprite not restored after load at the QA tile

**Scope:** QA harness only (`FF6X_Rev1_TECH_v0.3.1_CELES_TECH_QA_ACCESS`). Not a TECH v0.3 production failure.

## Observation (user runtime test)
Saving at the temporary QA save point (map $013, opening Narshe streets, tile (34,43))
during the opening Magitek field sequence, then reset/load: the party's field sprite
reloads as the normal walking sprite instead of the mounted Magitek sprite.
Battle presentation/state still shows Magitek correctly.

## Cause (assessment)
Vanilla never allows saving during the opening Magitek sequence. The "riding Magitek"
field presentation is runtime object state set by the opening event scripts, not part
of the data restored from a save slot; on load the map is re-entered with the default
walking presentation. Battle uses the character data (which is saved), so it stays Magitek.
This is a consequence of the QA harness enabling a save where vanilla has none.

## Decision
- The production save engine is **not** modified. No workaround is merged into any
  production branch.
- The opening-Magitek QA tile is marked **UNSUITABLE for field-sprite persistence testing**.
  It remains valid for: map entry/exit, collision, NPC/trigger/entrance behaviour,
  dialogue, battle return, flag persistence (event/NPC bits, inventory) across save/load.
- Any QA harness that needs field-sprite persistence must use a location where the
  party is already in normal walking state (future harness work; not part of v0.4).
