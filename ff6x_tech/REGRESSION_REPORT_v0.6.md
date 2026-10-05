# TECH v0.6 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

## Static
| Check | Result |
|---|---|
| Accepted baselines rebuilt byte-exact: v0.1, v0.2, v0.3 (+production), v0.3.1 QA, v0.4 ×3, **v0.5 ×3 (accepted)** | PASS (SHA-1 asserted) |
| Determinism (71 output files, two full builds) | PASS (0 differences) |
| Selftests | **50/50 PASS** (10 new v0.6 guards) |
| MonsterPal 768 units, MonsterStencil 128 small + 48 large, MP 512 entries identical to vanilla; `$200–$3FF` MP = 0; empty-slot shadow = D3:7810; production ENEMYX_GFX untouched | PASS (selftest 31) |
| Production v0.6 vanilla-space diff = 419 bytes, all declared (v0.5 set + 15 enemy operands + C1:20FF hook + C2:5D98 bound + checksum) | PASS (selftest 32) |
| QA content (Q600–Q603, custom assets, `$240–$243`, groups `$FB–$FE`) only in monster-tech | PASS (selftest 33) |
| Asset guards: size, 3bpp colour range, palette count, PNG/JSON palette mismatch, top edge, VRAM box, undeclared retarget | PASS (selftests 34–35) |

## Emulator (snes9x via stable-retro) — NOT user runtime QA
### 1. All 576 vanilla formations, vanilla Rev 1 vs production v0.6 (same start RAM, battle injected)
| Field | Identical |
|---|---|
| battle-engine monster data (v0.5 fingerprint) | 576/576 |
| **btlgfx: decoded tile buffer (8 KB), per-slot palette numbers, loaded palettes, palette bytes, sprite sizes, overlap** | **576/576** |
| screen at +90 frames | 573/576 (`$02A`, `$03D`, `$10F`: production frame N+1 == vanilla frame N) |
`audits/formation_diff_vanilla_vs_v06_production.json`

### 2. Sketch graphics path, vanilla vs production v0.6 (POKE: Terra's commands), formations `$000 $007 $00A $057 $066 $07E` (small, 3bpp, large stencils)
stable (graphics buffer, `$6169` palette pointer) states identical 6/6 — `audits/sketch_diff_vanilla_vs_v06_production.json`

### 3. Magic Points, vanilla vs production v0.6 (POKE: Ramuh on Terra), 8 formations incl. `$1FF`, `$200`
learn progress identical 8/8; QA ROM `$241` → +30/+15/+6, `$240` → 0 — `audits/magic_point_diff_vanilla_vs_v06_production.json`

### 4. Phase A isolation (Dark Wind) — `out/gfx_isolation_v06/`
A1 exact clone: tiles/palette/size identical, full battle screen pixel-identical to vanilla `$008` after 600 frames.
A2 Vulture palette: tiles/size identical, only the bird's box differs → **palette-only** issue.

### 5. QA ROM from New Game — save 18/18, load 11/11 (no RAM pokes)
| Step | Result |
|---|---|
| QA prompt → Custom monster battle → `$240`; IDs `$180/$181`; palettes `$300/$302`; sizes 4×5 / 4×4 | PASS |
| decoded tile buffer == source tiles (4bpp + 3bpp), no neighbouring data | PASS |
| both sprites pixel-exact on screen vs PNG + palette.json (994 + 448 opaque pixels) | PASS |
| AI pointers `$3952/$3958` (F9); Mute (A) and Slow (B) observed | PASS |
| B killed first → A still pixel-exact; victory, return (35,43), +75 gil | PASS |
| MP test: Ramuh from QA event, equipped via Skills > Espers, `$241` → Bolt 30 / Poison 15 / Bolt2 6; `$240` → unchanged | PASS |
| isolation battles `$242` / `$243` from the QA menu: IDs, palettes `046`/`046` and `046`/`04A`, win, return | PASS |
| QA Save Point → Save → new process → Continue: gil, inventory, map, position, Esper, learn progress restored | PASS |
| custom battle after load: buffer exact, sprites pixel-exact, win | PASS |
| Map test A ($1A0) grid + NPC A1, south exit; Celes Annex (Vale, exit); vanilla Guard battle | PASS |

### 6. POKE phase (Steal/Sketch/Control on custom monsters) — 6/6
steal slots E9/E8, F0/F2; Steal both; **Sketch: custom tiles decoded exactly by the Sketch loader, palette pointer `$3000`/`$3020`**, drawn next to Terra; Control both.

### 7. v0.4/v0.3 pipelines on v0.6
map differential 412 maps: map/props/BG/tile props/NPC pointers/static NPC fields 412/412 (raw objects 391/412, animation counters);
Celes slice suite on celes-tech v0.6: 24/24 PASS.

Evidence: `out/emu_enemy_tech/`, `out/emu_enemy_tech_cmds/`, `out/gfx_isolation_v06/`, `out/emu_celes_v06/`, `out/TECH_v0.6_emulator_contact_sheet.png`.

**EMULATOR PASS. USER RUNTIME QA PENDING.**
