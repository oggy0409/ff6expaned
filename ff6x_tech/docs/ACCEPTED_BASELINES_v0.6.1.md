# FFVI Expanded Edition — Accepted Baselines through TECH v0.6.1

## ROM baseline
- Final Fantasy III (USA) (Rev 1) / FFVI US v1.1
- Clean unheadered
- SHA-1: `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`
- CRC32: `C0FA0464`

## Runtime-accepted technical baselines

### TECH v0.1 — ACCEPTED
4 MiB expansion + F0 data reads.

### TECH v0.2 — ACCEPTED
Expanded dialogue + event bridge/hook + persistent event bit.

### TECH v0.3 — ACCEPTED
New map/NPC/dialogue/event/battle/reward/save-load pipeline.

### TECH v0.4 — ACCEPTED
Expanded map foundation: relocated map tables, new map IDs, scalable NPC vector routing,
short/long entrances, persistent map state.

### TECH v0.5 — ACCEPTED / RUNTIME VERIFIED
User confirmed:
- monster IDs `0x180` and `0x181` load together correctly,
- names/stats/AI behave correctly,
- targeting, victory, return and save/load are correct,
- vanilla battle regression is OK.

Known visual observation:
- TESTMOB B placeholder bird graphic appears visually poor / garbled-looking.
- This does NOT invalidate the v0.5 monster-ID/formation architecture because the test used
  placeholder vanilla graphics/palette routing.
- TECH v0.6 must explicitly determine whether this is only an intentionally mismatched palette/
  placeholder presentation or a real graphics metadata/dimension/tile-routing defect.

Resolved in v0.6: palette-only (Vulture palette on Dark Wind pixels).

### TECH v0.6.0 — NOT ACCEPTED (superseded)
QA isolation battles used vanilla `$008` VRAM map 1 slot 5, which the Magitek party overwrites (vanilla engine behaviour).
Regression target `monster-tech-v0.6.0` (`14d179cf…` / `F13B490B`).

### TECH v0.6.1 — ACCEPTED / RUNTIME VERIFIED (named baseline `TECH_v0.6.1_ENEMY_ASSET_MP`)
| ROM | SHA-1 | CRC32 |
|---|---|---|
| `FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA.sfc` (user-tested) | `8a55707ff2b4cd1364fdabf75e91422ba90ff8bb` | `289BD3B9` |
| `FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc` (engine of v0.6.1) | `26ebd7d3b1a16bfae94625cead054edc34a1a5b6` | `C9DB005B` |
| `FF6X_Rev1_TECH_v0.6.0_CELES_TECH.sfc` | `a7ae5d4c1c49ce5cfcbca65de943678b86923fce` | `E2BDA3B1` |

User confirmed: enemy graphics routing (exact clone identical to vanilla Dark Wind; palette variant = same shape),
custom assets, custom palettes, Magic Points (`$241` = 3, `$240` = 0), save/load, vanilla regression.
Accepted foundation: relocated MonsterPal / MonsterStencil / BattleMagicPoints, router F0:1240 + hook C1:20FF,
custom 4bpp/3bpp asset pipeline, expansion graphics bank FB/FC.

Known non-blocking visual issue: QA formation `$242/$243` slot 0 Dark Wind touches the visible left edge (x = 8).
Not a routing failure; addressed by the v0.6.2 formation-safety rules (production formations), QA build left frozen.
Steal / Sketch / Control on custom monsters: emulator poke only (user NOT TESTED).

### TECH v0.6.2 — tooling only (no ROM change)
Formation layout validation, Magitek VRAM safety table, previews (`FORMATION_SAFETY_v0.6.2.md`). Builder now asserts the
v0.6.1 hashes above.
