# FFVI Expanded Edition — Accepted Baselines through TECH v0.5

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

Do not mark final enemy graphics architecture accepted until v0.6 passes.
