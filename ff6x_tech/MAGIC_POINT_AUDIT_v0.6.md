# TECH v0.6 — Magic Point audit and foundation (Rev 1)

## Rev 1 code path (battle win, normal victory)
```
C2:5D91  C2 10      REP #$10          ; 16-bit index
C2:5D93  7B         TDC               ; A = 0
C2:5D94  AE D4 3E   LDX wBattleID     ; 16-bit
C2:5D97  E0 00 02   CPX #$0200
C2:5D9A  B0 04      BCS +4            ; battle >= $200: no magic points (A stays 0)
C2:5D9C  BF 00 B4 DF LDA BattleMagicPoints,X   ; DF:B400, 512 bytes (1 per battle)
C2:5DA0  85 FB      STA $FB           ; $FB = MP gained; credited later to living characters with an Esper
```
Only consumer of BattleMagicPoints (symbol cross-reference). Vanilla: 424 of 512 battles give 1–10 MP;
battles `$200–$23F` always 0; new formations `$240–$3FF` were 0 (v0.5 known limitation).

## Solution (all v0.6 targets)
| ID | PC | SNES | Original | New | Why |
|---|---|---|---|---|---|
| E104 | 38E000–38E3FF | F8:E000–F8:E3FF (FORMX_MAGIC_POINTS) | FF fill | 1024-byte table | `$000–$1FF` = vanilla bytes, `$200–$23F` = 0, `$240–$3FF` = formation source `magic_points` (default 0) |
| E105 | 025D98–025D99 | C2:5D98 (CPX operand) | `00 02` | `00 04` | bound now covers all 1024 formations |
| E200 | 025D9D–025D9F | C2:5D9D (LDA operand) | `00 B4 DF` | `00 E0 F8` | read the relocated table |

* Vanilla equivalence: battles `< $200` read identical bytes; `$200–$23F` now read 0 instead of skipping —
  the skip path also leaves A = 0, so `$FB` is identical and nothing after `STA $FB` depends on the flags.
* No SRAM change; Esper learning code untouched.
* Formation source: `formations/<f>.json` `"magic_points": 0–255` (refused outside the range).

## Proof
| Check | Result |
|---|---|
| Static: table `[0:512]` == DF:B400–DF:B5FF, `[512:576]` = 0, production `[576:1024]` = 0 | PASS (selftest 31) |
| Emulator, vanilla vs production v0.6, Ramuh poked onto Terra, formations `$000 $002 $003 $013 $022 $0FF $1FF $200` (MP 0/0/1/3/2/1/0/0) | identical learn progress (e.g. `$013`: Bolt 30, Poison 15, Bolt2 6) — `audits/magic_point_diff_vanilla_vs_v06_production.json` |
| Emulator, QA ROM, **no pokes**: QA gives Ramuh (event `$86 $36`), equipped through Skills > Espers, formation `$241` (MP 3) | Bolt +30, Poison +15, Bolt2 +6 |
| Same, zero-MP new formation `$240` | learn progress unchanged |
| Same after save → reset → Continue | equipped Esper and learn progress restored |

Capacity: every formation `$240–$3FF` (448) can award 0–255 MP; 0 is never credited.
