# TECH v0.7.3 — exact patch table (QA ROM only; production / celes-tech = v0.7.2, unchanged)

Delta v0.7.2 QA → v0.7.3 QA: every changed byte is in `out/DELTA_v0.7.2_to_v0.7.3.csv` (977 bytes). Production
and celes-tech: 0 bytes changed (SHA-1 `f8f92c81…` / `2789edb5…` asserted by the builder).

| Bytes | PC | SNES | What |
|---|---|---|---|
| 4 | `00FFDC-00FFDF` | C0:FFDC | SNES checksum/complement (`F5FF` → `AD8D`) |
| 1 | `30000B` | F0:000B | build metadata version `02` → `03` (QA target only) |
| 9 | `330068-330084` | F3:0068 | `Q712_QA_DLG` pointers (changed QA strings) |
| 9 | `3F0003`, `3F0010`, `3F0017-3F001D`, `3F005E`, `3F0076` | FF:0003… | `Q710_QA_EVENT` operands to relocated QA labels |
| 283 | `3F0087-3F01AB` | FF:0087–FF:01AB | `Q710_QA_EVENT`: `QaColoFight7` normalize / call CB:78D9 / restore (bytes in `COLOSSEUM_QA_STATE_v0.7.3.md` §4); later QA labels move |
| 671 | `3F080A`, `3F0A39-3F0CF4` | FF:080A, FF:0A39… | `Q712_QA_DLG` text: `TECH v0.7.3 QA ACCESS`, `Colosseum (normal party) / Fight: Terra/Locke/Celes/Edgar`; later strings move |

No hook, retarget, engine or table byte changes. The full QA ROM patch table follows (generated from the manifest).

