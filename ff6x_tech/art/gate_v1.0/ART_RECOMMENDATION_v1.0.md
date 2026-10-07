# ART RECOMMENDATION v1.0 — E8 memorial / archive (references only)

This note points at the vanilla references that best fit each asset. **It does not create or choose final art**: the
human art pass decides. Ids refer to `VANILLA_REFERENCE/INDEX.md`. The crops are static ROM renders with every metatile
and 8 × 8 id.

"New 8×8" counts the graphics of a crop that $1A2 does not already load. It is the import cost if that vanilla art were
reused directly. 0 means the look can be rebuilt only with new metatile definitions.

| asset | best references | why | also look at |
|---|---|---|---|
| **Temporary memorial** (name plaques / tags / records of the dead) | **T1** Darill's Tomb small red-framed plates on pedestals; **T4** Tzen hanging signboards | T1 has the plate language: small framed markers with a carved face, at a scale that repeats well across the 4 × 2 region. In-game they are tomb markers / switches, so use them for form only. T4 shows tags or boards hung from a rail, which reads as "temporary, hand-made". | **T6** Vector Imperial banner (a cloth / name banner fits the Empire setting); **T5** esper-room wall panels in $1A2's own graphics (0 new 8×8): a backing panel that matches the wall |
| **Permanent stone memorial** (heavier, permanent) | **P2 / P1** Darill's Tomb headstones on grave slabs; **P3** Maranda stone obelisk | The headstone + base is the clearest "memorial" silhouette in FFVI. The obelisk is the vertical shape if the 4 × 3 option is approved. Both read as stone and permanent next to the light, small tags. | **P6** Ancient Castle statues / wall trophies (formal, commemorative); **P5** Mobliz WoR outdoor headstones (simplest form) |
| **Archive preserve** (intact shelves / records) | **A2** Ancient Castle single tall bookshelf; **A1** Figaro library shelves | A2 is close to the 2 × 2 doorway in size and reads as "records" at a glance. A1 shows how shelves of records repeat. | **A5** Magitek Factory crates (0 new 8×8: storage built from graphics $1A2 already loads); **A3 / A4** house shelves / drawers (cabinet option) |
| **Archive burn** (burned shelves / rubble / soot, not black) | **B2** Mobliz WoR burned house; **B6** Kefka's Tower rubble with wrecked Imperial machinery | B2 has charred wood, broken boards and soot over a still-recognisable structure. That is the "burned, not missing" read this state needs. B6 gives rubble that belongs to the Empire. | **B1 / B5** WoR roof holes and soot (damage at small scale); **B4** Darill's Tomb collapsed masonry. Note **B3**: Thamasa flames show "burning", not "burned". |
| **Archive sealed** | v0.9.3 grate door (`$12/$13`) | Already reads as a closed door in user QA; may be reused if approved | — |

## Practical notes for the art pass
* Every vanilla reference except T5 / A5 / A6 comes from another tileset and palette. It is a **style** reference: the
  final art has to be redrawn in the $1A2 palette rows and within the 15-colour-per-8×8 limit (`CUSTOM_ASSET_SPEC.md` §1).
* The temporary and permanent memorials should read as different objects, not one object in two colours:
  * temporary: many small light items;
  * permanent: one heavy carved mass with a base.
* The burn state must keep a recognisable shelf or frame silhouette. It must use dark greys and browns, never index 0;
  index 0 is the pure-black void the user rejected.
* Decisions to make before the art pass:
  1. permanent memorial 4 × 2 or 4 × 3 (`CUSTOM_ASSET_SPEC.md` §2);
  2. reuse the sealed gate (yes / no);
  3. whether new colours may use palette rows 4-6 of `$30`, or wait for the production palette of the Vector ruins.
