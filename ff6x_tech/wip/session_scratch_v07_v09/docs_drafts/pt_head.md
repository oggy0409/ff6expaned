# TECH v0.7.2 — exact patch tables (PC + SNES)

Generated from the build manifests (`tools/patch_table.py`, `TECH_VER=v0.7.2`); the byte-exact data is in each ROM's
`.manifest.json` and `.diff.csv` (diff vs clean Rev 1). Every row's original bytes are asserted against the clean
Rev 1 image (+ the accepted 4 MiB expansion fill) at build time; a mismatch aborts the build.

The patch families are unchanged from v0.7.1 (see `PATCH_TABLE_v0.7.1.md`, "Patch ID families added in v0.7.1").
**v0.7.2 adds no engine patch, no hook, no retarget and no new allocation.**

## Delta v0.7.1 → v0.7.2 (every changed byte: `out/DELTA_v0.7.1_to_v0.7.2.csv`)

Totals: PRODUCTION **3** bytes, CELES_TECH **3** bytes (metadata + checksum only), ITEM_BANK_QA 962 bytes
(4 + 1 + 1 + 8 + 215 + 14 + 719, all QA-only).

| ROM | Bytes | PC | SNES | What |
|---|---|---|---|---|
| PRODUCTION | 1 | `30000B` | F0:000B | build metadata: version minor `01` → `02` |
| PRODUCTION | 2 | `00FFDC`, `00FFDE` | C0:FFDC | SNES checksum/complement `72 E5 8D` → `71 E5 8E` (`1A8D` → `1A8E`) |
| CELES_TECH | 1 | `30000B` | F0:000B | build metadata: version minor `01` → `02` |
| CELES_TECH | 2 | `00FFDC`, `00FFDE` | C0:FFDC | SNES checksum/complement (`2DB8` → `2DB9`) |
| ITEM_BANK_QA | 4 | `00FFDC-00FFDF` | C0:FFDC | SNES checksum/complement (`7984` → `F5FF`) |
| ITEM_BANK_QA | 1 | `30000B` | F0:000B | build metadata: version minor `01` → `02` |
| ITEM_BANK_QA | 1 | `301017` | F0:1017 | `P100_DLG_HOOK` (existing dialogue hook, generated): expansion-dialogue count `CMP #$0020` → `#$0022` (two new QA strings; production keeps its own count) |
| ITEM_BANK_QA | 8 | `3F0003`, `3F0010-3F001D`, `3F005E`, `3F0076` | FF:0003… | `Q710_QA_EVENT`: call/jump/choice operands to the relocated QA labels |
| ITEM_BANK_QA | 215 | `3F0080-3F015E` | FF:0080–FF:015E | `Q710_QA_EVENT`: **hotfix** — `QaColo7` sub-menu, `QaColoFight7` = call CB:78D9, `QaColoKit7` wager kit (below); the rest of the QA event block moves (same code, relocated labels) |
| ITEM_BANK_QA | 14 | `330064-330087` | F3:0064–F3:0087 | `Q712_QA_DLG` pointer table: two new QA dialogue pointers, later pointers moved |
| ITEM_BANK_QA | 719 | `3F080A`, `3F0A05-3F0CEA` | FF:080A, FF:0A05… | `Q712_QA_DLG` text: `TECH v0.7.2 QA ACCESS`, `Colosseum (full battle)`, new `qa7_colo` / `qa7_colo_kit`; later QA strings move |

All QA bytes are inside the existing item-tech-only claims `Q710_QA_EVENT` (FF:0000–FF:015E) and `Q712_QA_DLG`
(+ the generated count in `P100_DLG_HOOK`). Production and celes-tech contain none of them (selftest 44, QA isolation).
The event assembler asserts these vanilla bytes for the new `call VanillaColosseum` external without writing them
(`patches/map_v04.py VANILLA_ASSERTS`): CB:78D9 `5A 08 5C 9A C0 EE 01 72 79 01 C0 EF 01 6C 79 01`,
CB:796C `AF B2 72 79 01 FE`, CB:7972 `59 04 5C FE`.

### QA harness Colosseum entry, byte for byte

| | Address | Bytes | Meaning |
|---|---|---|---|
| v0.7.1 | FF:0080 `QaColo7` | `9A` | `$9A` colosseum menu **only** |
| | FF:0081 | `31 82 81 FF` | `party_step RIGHT 1` |
| | FF:0085 | `FE` | return |
| v0.7.2 | FF:0080 `QaColo7` | `4B 19 10` | dlg `qa7_colo` "Colosseum (vanilla script) / Fight (wager list) / Get wager kit / Cancel" |
| | FF:0083 | `B6 8D 00 35 96 00 35 5A 01 35` | choice → `QaColoFight7`, `QaColoKit7`, `QaCancel6` |
| | FF:008D `QaColoFight7` | `B2 D9 78 01` | `call` CB:78D9 = the receptionist's own "(With pleasure.)" branch |
| | FF:0091 | `31 82 81 FF` · `FE` | `party_step RIGHT 1`, return |
| | FF:0096 `QaColoKit7` | `80 EE` ×3 · `80 F0` ×3 · `80 04` · `80 09` | give Elixir ×3, Fenix Down ×3, ThiefKnife, ValiantKnife (vanilla event `$80`) |
| | FF:00A6 | `4B 1A 10` · `31 82 81 FF` · `FE` | dlg `qa7_colo_kit`, `party_step RIGHT 1`, return |

Called vanilla script (unchanged, Rev 1 bytes): CB:78D9 `5A 08` fade_out 8 · `5C` wait_fade · `9A` colosseum menu ·
`C0 EE 01 72 79 01` if $1EE=0 (no valid wager) → CB:7972 · `C0 EF 01 6C 79 01` if $1EF=0 → CB:796C ·
CB:796C `AF` colosseum battle ($23F) · `B2 72 79 01` call CB:7972 · `FE` · CB:7972 `59 04` fade_in 4 · `5C` · `FE`.

