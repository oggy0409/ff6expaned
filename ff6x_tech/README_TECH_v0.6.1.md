# FF6 Expanded Edition — TECH v0.6.1 HOTFIX: ENEMY-GRAPHICS ROUTING VALIDATION

**STATIC PASS · EMULATOR PASS · USER RUNTIME QA PENDING** — v0.6 is **not** accepted; accepted baselines unchanged.

Baseline: Final Fantasy III (USA) (Rev 1), unheadered, SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`.
Scope: only enemy-graphics routing validation (no item architecture, no production content, no engine change).

## Result
The v0.6 runtime failure (Dark Wind clone `$182` and Vulture-palette variant `$183` not matching vanilla Dark Wind) is
**not a routing / stencil / bank / index / size / bpp defect**. `$182` and `$028` resolve to the identical record
`1B 17 00 46 1F` → graphics index `$171B`, 4bpp, tile source EA:28D8 (PC 2A28D8), stencil `$1F`, 4×4 tiles, palette `$046`;
`$183` differs only in palette (`$04A`). The WRAM tile buffer is correct in every case.

Cause: the v0.6 QA isolation battles reused vanilla formation `$008` and put the test bird in **VRAM map 1 slot 5**. With the
opening **Magitek-armor party**, the party graphics overlap that slot's VRAM box, so the slot-5 sprite shows Magitek tiles.
**Unmodified vanilla Rev 1 does exactly the same** (vanilla Dark Wind in that slot: 0/91 frames exact; exact when Magitek is
cleared). Full evidence and per-field table: `GFX_COMPARE_REPORT_v0.6.1.md` / `.json`, contact sheet
`TECH_v0.6.1_gfx_routing_contact_sheet.png`.

## What changed (QA ROM only) — exact rows in `PATCH_TABLE_v0.6.1.md`
| What | PC | SNES | v0.6.0 → v0.6.1 |
|---|---|---|---|
| formation `$242`: template `$002` (VRAM map 8, Magitek-safe); slot 0 vanilla `$028`, slot 2 `$182`, slot 3 `$183` — all three in one battle | 38C1DE–38C1EC | F8:C1DE | `10 3C FF FF 17 17 28 82 00 00 AB 4C 44 A3 23` → `80 0D 28 FF 82 83 FF FF 13 00 4B 87 00 00 3E` |
| formation `$243`: reference, 3× vanilla `$028`, same layout | 38C1ED–38C1FB | F8:C1ED | `…28 83… 23` → `80 0D 28 FF 28 28 FF FF 13 00 4B 87 00 00 32` |
| battle prop byte 0 of `$242/$243` (from template `$002`: back attack disabled) | 389908, 38990C | F8:9908, F8:990C | `C3` → `E3` |
| QA dialogue `$1012–$1018` (v0.6.1 text, new isolation menu) + 6 pointer bytes | 3F0809–3F0A34, 33004C–330060 | FF:0809, F3:004C | text / pointers |
| build metadata version byte | 30000B | F0:000B | `00` → `01` |
| SNES checksum | 00FFDC–00FFDF | C0:FFDC | `EC 03 13 FC` → `EF 0B 10 F4` |

Total 599 bytes in 12 runs vs v0.6.0 QA. No change to router F0:1240, hook C1:20FF, relocated tables, monster records,
graphics data, production or celes-tech.

New diagnostics: `tools/gfx_compare_report.py` (A/B/D report); `tools/emu_enemy_tech.py` steps 09a/09b check every bird
pixel-exact at its formation position; selftest 33 now also asserts `$242/$243` = VRAM map 8, slots 0/2/3, IDs.

## Outputs (`out/`)
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA.sfc` | `8a55707ff2b4cd1364fdabf75e91422ba90ff8bb` | `289BD3B9` | `F410` | **user QA ROM** |
| `FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA.bps` | `8df36f1f9f011eb26b77f462d478b81d379d391c` | | | patch vs clean Rev 1 |
| `FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc` | `26ebd7d3b1a16bfae94625cead054edc34a1a5b6` | `C9DB005B` | `7B38` | unchanged |
| `FF6X_Rev1_TECH_v0.6.0_CELES_TECH.sfc` | `a7ae5d4c1c49ce5cfcbca65de943678b86923fce` | `E2BDA3B1` | `8E63` | unchanged |
| `FF6X_Rev1_TECH_v0.6.0_ENEMY_ASSET_QA.sfc` | `14d179cfa61e720aa81ea9c4be518df1e13212fa` | `F13B490B` | `FC13` | v0.6.0 QA, rebuilt byte-exact (regression target `monster-tech-v0.6.0`) |

Also `.ips`, `.manifest.json` (SHA-1 `6a3d7e40…`), `.diff.csv` for the v0.6.1 QA ROM.

```
python build.py "Final Fantasy III (USA) (Rev 1).sfc"     # 15 targets, deterministic
python tools/selftest.py "<rom>"                           # 50 fail-closed guard tests
```

Docs: `GFX_COMPARE_REPORT_v0.6.1.md/.json`, `PATCH_TABLE_v0.6.1.md`, `REGRESSION_REPORT_v0.6.1.md`, `KNOWN_RISKS_v0.6.1.md`,
`USER_QA_TECH_v0.6.1_VI.md`. v0.6 docs (audits, capacity) remain valid.
