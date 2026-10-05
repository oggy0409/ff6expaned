# TECH v0.7.2 — regression report (STATIC + Claude-side EMULATOR; user runtime pending)

All results below are on the **final** v0.7.2 build: `item-tech` `1e2604ac…`, `production` `f8f92c81…`, `celes-tech`
`2789edb5…`. Emulator = snes9x core via stable-retro, driving the real game through its menus and event engine.
POKE marks the few steps that write RAM directly (test setup only, identical in every compared ROM). This is **not**
user runtime QA. Logs and reports: `out/emulator_v072/`.

## 1. Static
| Check | Result |
|---|---|
| Clean input asserted (SHA-1 `057ADA1C…`, CRC32 `C0FA0464`) | PASS |
| 18/18 targets build; frozen accepted baselines reproduced byte-exact (SHA-1 asserted): v0.1, v0.2 evtest, v0.3 ×2, v0.3.1 QA, v0.4 ×3, v0.5 ×3, v0.6.0 production / celes-tech / QA, v0.6.1 QA | PASS |
| Determinism: two full builds, 90 output files (`.sfc/.bps/.ips/.manifest.json/.diff.csv`) | PASS (0 differences) |
| Selftest | **71/71 PASS** |
| BPS and IPS of the three v0.7.2 ROMs re-applied to clean Rev 1 → byte-identical ROMs | PASS |
| Delta v0.7.1 → v0.7.2: production 3 bytes, celes-tech 3 bytes (metadata version + checksum); QA ROM 962 bytes, all inside the QA-only claims (+ the generated QA dialogue count) | PASS (`PATCH_TABLE_v0.7.2.md`, `out/DELTA_v0.7.1_to_v0.7.2.csv`) |
| New vanilla external `VanillaColosseum` CB:78D9: Rev 1 bytes at CB:78D9 / CB:796C / CB:7972 asserted, not written | PASS |

## 2. Emulator — Colosseum (the v0.7.1 blocking failure)
`tools/emu_colosseum.py` → `COLOSSEUM_EMULATOR_REPORT.json`: **60/60 PASS**. Every Colosseum entry sets the game
clock to the same value first, so every ROM uses the same battle random seed (see `COLOSSEUM_ROOT_CAUSE_v0.7.2.md` §5).

| Group | ROMs | Path | Checks |
|---|---|---|---|
| C1–C3 | v0.7.2 QA vs clean Rev 1 | QA menu `Fight` (calls CB:78D9) vs CB:78D9 | wager Potion/Terra, ThiefKnife/Wedge, Graedus/Vicks: battle $23F entered, opponent = ColosseumProp monster, battle screen rendered (not black), A/B/X/Y don't hang it, return to Narshe with fade-in and control, 30–49 rendered battle frames identical to Rev 1, inventory after the battle identical to Rev 1; win path (POKE: opponent held at 1 HP): wager consumed, prize received |
| C4 | v0.7.2 QA | QA menu `Fight` | Terra wearing **QA Blade13D / QA Mail 13E / QA Charm13F** (equipped through the menus) vs Woolly, win (POKE) → prize, extended equipment unchanged after the battle |
| K1–K4 | v0.7.2 QA vs clean Rev 1 | QA `Get wager kit` + `Fight` vs `$80` gives + CB:78D9 | **no POKE**, natural outcomes: Elixir/Vicks (loss), Fenix Down/Wedge (**win**, Magicite), Elixir/Terra (loss), ThiefKnife/Vicks (**win**, prize CF); frames, inventory and return identical to Rev 1 |
| R1–R3 | Rev 1, v0.6.0 production, v0.7.1 QA, v0.7.2 production, v0.7.2 QA | **real receptionist** NPC CB:78C3 on the Colosseum map $19D | ThiefKnife/Wedge, Graedus/Vicks, Potion/Terra (natural): identical to Rev 1 (39–42 frames, inventory, return to $19D with fade-in) |
| CB:78D9 differential | v0.6.0 production, v0.7.1 QA, v0.7.2 production | vanilla script | C1–C3 identical to Rev 1 |
| Cancel | Rev 1, v0.7.2 QA | wager list left with B | screen fades back in, control returns |
| Root-cause references | v0.7.1 QA harness; clean Rev 1 running the v0.7.1 harness bytes | | battle not entered, brightness 0.0 (fight and cancel): the original failure, reproduced without any FF6X code |

## 3. Emulator — v0.7.1 item regressions on v0.7.2 (all rerun on the final ROMs)
| Suite | ROM | Result | Covers |
|---|---|---|---|
| `tools/emu_item_tech.py` | item-tech | **10/10** | New Game signature/zero, GIVE/TAKE/HAS (`$66/$67/$68`), vanilla `$80/$81` never merge with `$13D`, undefined/out-of-bank ids ignored |
| `tools/emu_item_qa.py` | item-tech + production | **33/33** | receive, names/icons/descriptions/details, three items equipped at once, stats + preview, Remove/Empty/relic remove, **Optimum**, **Arrange** + item move, **shop** owned count / **Sell** / Colosseum list, **save → power cycle → load**, garbage + genuine **Rev 1 (legacy) saves**, QA save in production |
| `tools/emu_item_battle.py` | item-tech (+ clean Rev 1 differential) | **17/17** | QA harness menu (grant ×2, **HAS/TAKE**), **battle hand logic**: battle list, hand props/power/names, weapon animation, damage, Jump animation, extended hand replacement refused, R↔L exchange, vanilla exchange identical to Rev 1, battle end, `$8D` |
| `tools/emu_enemy_tech.py save` (`FF6X_QA_PREFIX=1`) | item-tech | **18/18** | v0.6.1 custom monsters, AI, MP, Dark Wind isolation, save |
| `tools/emu_enemy_tech.py load` | item-tech | **11/11** | Continue, custom battle after load, Map test A, routed NPC, Celes Annex, vanilla Guard battle |
| `tools/emu_enemy_tech.py cmds` | item-tech | **6/6** | Steal / Sketch / Control on custom monsters (POKE) |
| `tools/emu_celes_suite.py` | celes-tech | **24/24** | Celes Annex dialogue hook, map/NPC/door/battle/reward/exit |

User checklist items mapped: equip ✔ (item_qa C/D/E), Arrange ✔ (H), Optimum ✔ (I), save/load ✔ (J), battle hand logic ✔
(item_battle), shops/Sell ✔ (M), event GIVE/TAKE/HAS ✔ (item_tech + item_battle), legacy saves ✔ (L).

## 4. Map / formation differential
Not rerun: production v0.7.2 differs from production v0.7.1 only at F0:000B (build-metadata version byte, never read
by the game) and the header checksum C0:FFDC/FFDE (never read by the game). So the v0.7.1 results carry over
unchanged: 412/412 maps and 576/576 formations engine-data identical to v0.6.0 (`REGRESSION_REPORT_v0.7.1.md` §3).

## 5. Findings during v0.7.2 QA
| Finding | Disposition |
|---|---|
| v0.7.1 QA harness Colosseum = `$9A` alone → black screen (fight and cancel) | **fixed** (QA harness calls CB:78D9) |
| A New Game has no wager items; the QA shop sells only brushes (whose opponent is Chupon, with no winnable prize) | QA `Get wager kit` added (vanilla `$80` gives) |
| Event `$80` gives can take up to one frame longer than in Rev 1 (I210 slot mask) → the game clock, and so the battle RNG seed, can shift for identical inputs | timing only, no item difference; documented (KNOWN_RISKS R16); tests align the clock |

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING.**
