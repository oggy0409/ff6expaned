# FFVI Expanded Edition — Accepted Baselines through TECH v0.4

## ROM baseline
- Final Fantasy III (USA) (Rev 1) / FFVI US v1.1
- Clean unheadered
- SHA-1: `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`
- CRC32: `C0FA0464`

## Creative/content
- `v1.2 CREATIVE LOCK` remains authoritative.
- Do not reinterpret story, maps, mobs, bosses, equipment concepts, voices, canon locks, or ending philosophy without explicit approval.

## Runtime-accepted technical baselines

### TECH v0.1 — ACCEPTED
- 4 MiB expansion works at runtime.
- F0-bank relocated command-name data is read correctly.
- MagiTek/Fight functionality preserved.
- Save/reset/load OK.

### TECH v0.2 — ACCEPTED
- Expanded-bank dialogue works at runtime.
- Event bridge/hook works.
- Persistent event bit survives save/reset/load.
- Vanilla dialogue flow remains functional.

### TECH v0.3 — ACCEPTED
- New map pipeline works.
- New NPC + expanded dialogue + persistent production flag works.
- Battle trigger/return works.
- One-time reward works.
- Exit to vanilla flow works.
- Save/reset/load + re-entry works.

### TECH v0.3.1 QA harness
- Core v0.3 pipeline confirmed by user.
- Known harness-only issue: saving/loading during opening Narshe Magitek field sequence restores the walking field sprite while battle Magitek state remains correct.
- Do not patch production save engine for this.
- `$0FF` remains permanently reserved for TECH_TEST.

### TECH v0.4 — ACCEPTED / RUNTIME VERIFIED
User confirmed all QA items passed.

Accepted runtime evidence:
- relocated/expanded map tables work,
- new map IDs `$1A0` / `$1A1` work,
- scalable NPC event-vector routing works,
- event triggers work,
- short entrances work,
- long entrances work,
- cross-map persistent flag state works after save/reset/load,
- Celes Annex test still works on the new map pipeline,
- vanilla opening regression test passed.

Map foundation is now considered production-capable for the planned Expanded Edition scope.

## Next target
`TECH v0.5 — MONSTER EXPANSION FOUNDATION`
