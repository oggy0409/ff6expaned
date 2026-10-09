# TECH v0.6.1 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

## Static
| Check | Result |
|---|---|
| Accepted baselines rebuilt byte-exact: v0.1, v0.2, v0.3 (+production), v0.3.1 QA, v0.4 ×3, v0.5 ×3 | PASS (SHA-1 asserted) |
| v0.6.0 production / celes-tech unchanged (`26ebd7d3…`, `a7ae5d4c…`); v0.6.0 QA rebuilt byte-exact (`14d179cf…`) | PASS |
| Determinism: two full builds, 76 output files | PASS (0 differences) |
| Selftests | 50/50 PASS (test 33 updated: Q61x IDs; `$242/$243` VRAM map 8, slots 0/2/3, IDs 028/182/183 and 3×028) |
| Byte diff v0.6.0 QA → v0.6.1 QA | 599 B / 12 runs, all QA formations / QA text / metadata / checksum (`PATCH_TABLE_v0.6.1.md`) |

## Emulator (snes9x via stable-retro) — NOT user runtime QA
### 1. Routing comparison (`GFX_COMPARE_REPORT_v0.6.1.md`, 8 scenarios)
`$028/$182/$183`: records, graphics index, tile source, stencil, size, buffer identical (palette only differs for `$183`).
Slot-5 corruption with Magitek party reproduced in **vanilla Rev 1** `$008` (S1) and v0.6.0 QA (S3); absent without Magitek
(S2, S4, S5) and in the v0.6.1 layout (S6, S7) and vanilla `$002` (S8).

### 2. QA ROM v0.6.1 from New Game — save 18/18, load 11/11, poke 6/6 (`out/emu_enemy_tech_v061/`, `out/emu_enemy_tech_cmds_v061/`)
| Step | Result |
|---|---|
| Custom monster battle `$240`: IDs `$180/$181`, palettes `$300/$302`, buffer exact, sprites pixel-exact, AI, kill order, victory/return | PASS |
| MP test: `$241` → Bolt 30 / Poison 15 / Bolt2 6; `$240` → unchanged | PASS |
| **09a** `$242` from QA menu with Magitek party: slots 0/2/3 = `028/182/183`, palettes `046/046/04A`, every bird pixel-exact at its formation position; win, return | PASS |
| **09b** `$243` reference: 3× `028`, all pixel-exact; win, return | PASS |
| Save → new process → Continue; custom battle after load | PASS |
| Map test A `$1A0`, Celes Annex, vanilla opening Guard battle | PASS |
| Steal / Sketch / Control on custom monsters (RAM poke) | PASS |

### 3. Carried over from v0.6 (production / celes-tech byte-identical, so still valid)
576/576 vanilla formations btlgfx identical vs vanilla; Sketch path 6/6; MP 8/8; map differential 412/412; Celes suite 24/24.

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING.**
