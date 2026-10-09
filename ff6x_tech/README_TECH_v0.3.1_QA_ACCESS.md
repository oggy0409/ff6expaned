# FF6 Expanded Edition — TECH v0.3.1 CELES TECH QA ACCESS

> **QA HARNESS ONLY — NOT A PRODUCTION BASELINE.**
> Purpose: let the user run the TECH v0.3 Celes Annex QA from a **New Game**, without a World of Ruin / Falcon save.
> The accepted TECH v0.3.0 builds are **unchanged** (hashes below re-verified). Do not branch production work from this ROM.

**STATIC PASS · EMULATOR SMOKE PASS (21/21 save phase + 7/7 load phase, no RAM pokes) · RUNTIME USER QA PENDING**

## Outputs
| File | SHA-1 | CRC32 | SNES chk |
|---|---|---|---|
| `FF6X_Rev1_TECH_v0.3.1_CELES_TECH_QA_ACCESS.sfc` | `bf443c85dc448c0a86169f58dce43d77684c36f5` | `B982BC11` | `CCD9` |
| `…QA_ACCESS.bps` (source CRC checked: Rev 1 `C0FA0464`) | `345cc933c16f9cf8849a7ed72987c66a6e6e6e3a` | | |
| `…QA_ACCESS.ips` | `d071aa41378c19520a93359d1670ce9324142c25` | | |

MD5 of the ROM: `8c794766d1efa558fb0494db377fb472`. Size 4 MiB (0x400000).

Unchanged accepted / regression builds (rebuilt in the same run, byte-identical):

| Target | SHA-1 | CRC32 |
|---|---|---|
| `celes-tech` v0.3.0 | `e0196eb30fc03cf076c0d1306b0c09b664f7b2a4` | `3E6B68E2` |
| `production` v0.3.0 | `0eda0bab925f8b6f1c840c20523f9413cb586ec3` | `8D05263F` |
| `evtest` (= accepted v0.2) | `0258a0fc122bb109e7ca343dda61c58af2e921fb` | `32725A65` |
| `legacy-v0.1` (= accepted v0.1) | `c412f12938f9f4bd9c7e3f857572d3b773bab649` | `DA88A7DE` |

Build: `python build.py "<clean Rev 1>.sfc" --target celes-qa` (or `all`). Deterministic: all 26 output files byte-identical across two rebuilds.

## What the harness does
```
New Game → first control, Narshe opening streets (map $013, start tile (38,49))
  walk 6 up → plaza (38,43) → 4 left → QA tile (34,43)
    prompt $100B "TECH v0.3 QA ACCESS / Enter Celes Annex test? / Yes / No"
      Yes → call F1:000A  (unmodified v0.3 EvAnnexEnter_Yes) → map $0C7 (16,27)   [same as Falcon entry]
      No  → call CC:9AEB  (unmodified vanilla SavePoint)   → blue flash, Save enabled on this tile
  Annex: exactly the v0.3 events/dialogue/flags/map; exit (16,29) → map $013 (35,43), facing LEFT
  QA tile again → No → menu Save → reset → Continue → reloads on the QA tile (no prompt loop)
```

## QA-only patches (exact)
All IDs start with `Q`; they exist only in target `celes-qa`. Production/celes-tech contain none of them (selftest #16).

| ID | PC | SNES | Len | Original | New | Consumer / reason |
|---|---|---|---|---|---|---|
| Q100_QA_DLG | 3F0800–3F0836 | FF:0800–FF:0836 | 55 | FF fill | QA prompt string (`33 24 22 27 7F 4F 54 65 57 7F 30 20 …`) | text renderer via P100 hook; dialogue $100B |
| Q100_QA_DLG | 33002C–33002F | F3:002C–F3:002F | 4 | `FF FF FF FF` | `00 08 FF 00` | P100 hook pointer slot for ID $100B (next slot after the v0.3 table) |
| Q101_QA_DLG_COUNT | 301017–301018 | F0:1017–F0:1018 | 2 | `0B 00` | `0C 00` | override of P100 `CMP #count` → IDs up to $100B accepted |
| Q200_QA_EVENT | 3F0000–3F0019 | FF:0000–FF:0019 | 26 | FF fill | `C0 B5 81 19 00 35 4B 0B 10 B6 10 00 35 15 00 35 B2 0A 00 27 FE B2 EB 9A 02 FE` | QA access event (listing below) |
| Q303_QA_BATTLE_GROUP | 310058 | F1:0058 | 1 (asserted 3: `4D 28 3F`) | `28` | `01` | override of the v0.3 door battle (event cmd $4D in EvBattleDoor_Fight): group $28 Mega Armor+ProtoArmor → group $01 (vanilla opening Guard battle, formation $002) |
| Q305_REPACK_EVENT_TRIGGERS_QA | 040000–041A0F | C4:0000–C4:1A0F | 6672 | vanilla table (asserted, SHA-1 `11e6eb89…`) | v0.3 table + record `22 2B 00 00 35` for map $013 at PC 0403FB / C4:03FB; later pointers +5 | replaces T305 trigger repack; slack 18 → 3 |
| Q305_REPACK_SHORT_ENTRANCES_QA | 1FBB00–1FD9FF | DF:BB00–DF:D9FF | 7936 | vanilla table (asserted) | v0.3 table; the Annex exit record at PC 1FCC76 / DF:CC76 is `10 1D 13 30 23 2B` instead of `10 1D 0C 24 0F 2F` | replaces T305 entrance repack: exit → map $013 (35,43) LEFT, lower z |

Plus build-identity changes: P001 metadata (`celes-qa`, 0.3.1) and P999 checksum.
Byte diff vs the accepted v0.3.0 `celes-tech` ROM: 3,564 bytes, all in the ranges above
(3,465 of them are the +5 pointer shift inside the trigger table).

### QA event listing (FF:0000, from `events/celes_qa_access/qa_access.evt`)
```
FF:0000  C0 B5 81 19 00 35      if_switch VANILLA_TILE_EVENT_LATCH($1B5)=1 -> QaRet
FF:0006  4B 0B 10               dlg $100B qa_prompt
FF:0009  B6 10 00 35 15 00 35   choice QaYes, QaNo
FF:0010  B2 0A 00 27            QaYes: call F1:000A (EvAnnexEnter_Yes, v0.3)
FF:0014  FE                     return
FF:0015  B2 EB 9A 02            QaNo:  call CC:9AEB (vanilla SavePoint)
FF:0019  FE                     QaRet: return
```

### Allocations (data/allocations.json, manifest v3)
- New region **QA_HARNESS FF:0000–FF:FFFF**, targets `["celes-qa"]` only. For every other target FF stays `UNALLOCATED` (reserved).
- `celes-qa` added to the v0.3 regions/claims/table repacks/bits (same allocations as `celes-tech`).
- Event bit **$1B5** declared as `vanilla_read_only_refs` (read-only; the assembler refuses any write — selftest #17).
- No new event or NPC bits. The QA flags are the v0.3 production flags ($14A/$14B/$14C/$6F8/$6F9).
- Trigger slack after QA: 3 bytes (QA build only; production/celes-tech keep 8).

## Why each choice
| Choice | Reason |
|---|---|
| Map $013 tile (34,43) | First controllable field map after New Game (6 steps north + 4 west); plaza corner, lower z, off the scripted path; no vanilla trigger/NPC/entrance on (34,43)/(35,43) (build-time asserted). |
| Vanilla SavePoint call | Normal save mechanics ($1BF save-allowed, $1B5 latch, info prompt first time) — no SRAM/menu hack. |
| Latch check first | Prevents the prompt from re-opening every frame while standing on the tile, and after Continue. |
| Exit to (35,43), not onto the tile | Avoids an automatic prompt on arrival; one step LEFT re-opens it. |
| Battle group $01 | The New Game party (Terra Lv3 / Wedge / Vicks in Magitek armor) cannot beat group $28 without RAM edits; group $01 is the vanilla opening battle and was won in the emulator with no pokes. |

## Static checks
- 21/21 selftests (incl. new: QA_HARNESS refused for production & celes-tech; no Q-patches and pristine FF bank in production/celes-tech; vanilla read-only bit write refused; override with wrong owner refused).
- Event assembler oracle 24/24 vs the Rev 1 disassembly macros.
- Original-byte asserts: vanilla SavePoint head (CC:9AEB `C0 B5 81 B3 5E 00`), event battle group 1 (`02 00 02 00`), battle command bytes `4D 28 3F`, hook bound `0B 00`, full trigger/entrance tables.

## Emulator smoke (Claude-side, snes9x core) — NOT user runtime QA
`out/emu_qa/` (`qa_save_phase_result.json`, `qa_load_phase_result.json`, screenshots, contact sheet). No RAM pokes.
New Game → QA tile → No (SavePoint info prompt) → latch holds → Yes → Annex collision grid match → sealed door $1006 →
Vale $1002/$1003 → battle (real fight, won) → $1008 + step → no loop → Potion +1 once → Vale $1005 → exit to (35,43) →
No → Save greyed off-tile / enabled on tile → slot 1 written → **new emulator process** → Continue → same tile, flags + Potion
restored, no prompt loop → re-entry: Vale $1005, chest gone, door inert → exit → vanilla opening guard event ($000D + battle) → control returns.

## Known risks / limits (QA build)
| # | Item |
|---|---|
| Q-R1 | Battle step uses vanilla group $01, not v0.3 group $28. The battle *pipeline* (cmd $4D, return, CA:5EA9 check, BATTLE_DONE, step-up, no loop) is identical; only the enemy formation differs. |
| Q-R2 | The Annex exit always goes to Narshe in this ROM, including when entering from the Falcon trigger (still present). Vale's final line still says "return to the Falcon" (v0.3 text kept byte-identical). |
| Q-R3 | Saving in the Narshe opening area is not possible in vanilla; it is here only on the QA tile. Use this save only for QA. |
| Q-R4 | QA dialogue ID $100B occupies the next expansion pointer slot in this ROM only; production will assign $100B independently. |
| Q-R5 | First SavePoint use shows the vanilla "Want info about Save Points?" prompt (expected). |
| Q-R6 | Event script executing from bank FF is new in this build (v0.2/v0.3 ran from F1); emulator-verified, user runtime pending. |
| — | All TECH v0.3 risks (`KNOWN_RISKS_v0.3.md`) still apply. |
