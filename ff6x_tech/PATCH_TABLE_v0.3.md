# TECH v0.3 — exact patch tables (generated from build manifests)

Long rows (>512 bytes) show length + SHA-1 of original/new; byte-exact data is in the `.manifest.json` and `.diff.csv` next to each ROM.

## production — `FF6X_Rev1_TECH_v0.3.0_PRODUCTION.sfc`

SHA-1 `0eda0bab925f8b6f1c840c20523f9413cb586ec3` · CRC32 `8D05263F` · SNES checksum `20F6` · status: PRODUCTION BRANCH - 4 MiB + metadata + accepted dialogue hook; no content, no EVTEST

| ID | PC | SNES | Len | Original | New | Consumer / reason |
|---|---|---|---|---|---|---|
| P000_EXPAND_4MIB | 300000–3FFFFF | F0:0000–FF:FFFF | 1048576 | `` | `FF fill` | All F0-FF expansion allocations. — Expand 3 MiB -> 4 MiB HiROM. Header ROM-size byte C0:FFD7 is already 0x0C (4 MiB class) in Rev 1; unchanged. |
| P001_BUILD_METADATA | 300000–30003F | F0:0000–F0:003F | 64 | `FF fill (expansion)` | `46 46 36 58 2D 45 45 00 01 00 03 00 00 02 00 00 70 72 6F …` | tools/verify (offline). No runtime consumer. — Machine-readable build identity for QA tooling. |
| P101_EXP_DLG_TABLE | 334000–33402A | F3:4000–F3:402A | 43 | `FF fill (expansion)` | `24 37 2F 20 2D 32 28 2E 2D 7F 23 28 20 2B 2E 26 34 24 7F …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1000: 'EXPANSION DIALOGUE ERROR:{n}ID OUT OF RANGE.' |
| P101_EXP_DLG_TABLE | 330000–330003 | F3:0000–F3:0003 | 4 | `FF fill (expansion)` | `00 40 F3 00` | P100 hook (LDA.l table,X) — 1 x 4-byte pointers for dialogue IDs $1000-$1000 |
| P100_DLG_HOOK | 301000–301032 | F0:1000–F0:1032 | 51 | `FF fill (expansion)` | `C2 20 A5 D0 C9 00 10 B0 0A E2 20 A9 CD 85 CB 5C C3 7F C0 …` | JML from C0:7FBF (GetDlgPtr) — Dialogue-pointer hook: vanilla IDs unchanged, IDs $1000+ from expansion table |
| P100_DLG_HOOK | 007FBF–007FC2 | C0:7FBF–C0:7FC2 | 4 | `A9 CD 85 CB` | `5C 00 10 F0` | GetDlgPtr C0:7FBF; callers C0:A49A ($48), C0:A4E1 ($4B), C0:D493 (debug) — Replace LDA #$CD / STA $CB with JML $F01000 (displaced code re-executed in hook) |
| P999_CHECKSUM | 00FFDC–00FFDF | C0:FFDC–C0:FFDF | 4 | `9F 75 60 8A` | `09 DF F6 20` | SNES header (emulator/flash-cart validation) — Recalculated checksum 20F6 / complement DF09 |

## celes-tech — `FF6X_Rev1_TECH_v0.3.0_CELES_TECH.sfc`

SHA-1 `e0196eb30fc03cf076c0d1306b0c09b664f7b2a4` · CRC32 `3E6B68E2` · SNES checksum `0C36` · status: TECH v0.3 vertical slice = production + Celes Annex technical slice (placeholder content)

| ID | PC | SNES | Len | Original | New | Consumer / reason |
|---|---|---|---|---|---|---|
| P000_EXPAND_4MIB | 300000–3FFFFF | F0:0000–FF:FFFF | 1048576 | `` | `FF fill` | All F0-FF expansion allocations. — Expand 3 MiB -> 4 MiB HiROM. Header ROM-size byte C0:FFD7 is already 0x0C (4 MiB class) in Rev 1; unchanged. |
| P001_BUILD_METADATA | 300000–30003F | F0:0000–F0:003F | 64 | `FF fill (expansion)` | `46 46 36 58 2D 45 45 00 01 00 03 00 00 02 00 00 63 65 6C …` | tools/verify (offline). No runtime consumer. — Machine-readable build identity for QA tooling. |
| P101_EXP_DLG_TABLE | 334000–33402A | F3:4000–F3:402A | 43 | `FF fill (expansion)` | `24 37 2F 20 2D 32 28 2E 2D 7F 23 28 20 2B 2E 26 34 24 7F …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1000: 'EXPANSION DIALOGUE ERROR:{n}ID OUT OF RANGE.' |
| P101_EXP_DLG_TABLE | 33402B–334061 | F3:402B–F3:4061 | 55 | `FF fill (expansion)` | `33 24 22 27 7F 4F 54 65 57 61 7F 20 47 47 3E 51 7F 4D 3E …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1001: 'TECH v0.3: Annex test map.{n}Enter the Annex?{n}{choice} Yes{n}{choice} No' |
| P101_EXP_DLG_TABLE | 334062–3340D5 | F3:4062–F3:40D5 | 116 | `FF fill (expansion)` | `35 20 2B 24 7F 6B 49 45 3A 3C 3E 41 48 45 3D 3E 4B 6C 61 …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1002: 'VALE (placeholder): TECH v0.3.{n}This text is from bank F3.{n}Annex flag STARTED is now ON.{n}The north door is unsealed.' |
| P101_EXP_DLG_TABLE | 3340D6–33413D | F3:40D6–F3:413D | 104 | `FF fill (expansion)` | `35 20 2B 24 7F 6B 49 45 3A 3C 3E 41 48 45 3D 3E 4B 6C 61 …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1003: 'VALE (placeholder):{n}Annex flag STARTED is still ON.{n}Go north through the door{n}to start the test battle.' |
| P101_EXP_DLG_TABLE | 33413E–3341A6 | F3:413E–F3:41A6 | 105 | `FF fill (expansion)` | `35 20 2B 24 7F 6B 49 45 3A 3C 3E 41 48 45 3D 3E 4B 6C 61 …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1004: 'VALE (placeholder):{n}Annex flag BATTLE DONE is ON.{n}Take the test reward from{n}the chest in the north room.' |
| P101_EXP_DLG_TABLE | 3341A7–33420E | F3:41A7–F3:420E | 104 | `FF fill (expansion)` | `35 20 2B 24 7F 6B 49 45 3A 3C 3E 41 48 45 3D 3E 4B 6C 61 …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1005: 'VALE (placeholder):{n}Annex flag COMPLETE is ON.{n}TECH slice finished. Exit{n}south to return to the Falcon.' |
| P101_EXP_DLG_TABLE | 33420F–334238 | F3:420F–F3:4238 | 42 | `FF fill (expansion)` | `33 41 3E 7F 3D 48 48 4B 7F 42 4C 7F 4C 3E 3A 45 3E 3D 65 …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1006: 'The door is sealed.{n}(Talk to VALE first.)' |
| P101_EXP_DLG_TABLE | 334239–334271 | F3:4239–F3:4271 | 57 | `FF fill (expansion)` | `33 24 22 27 7F 4F 54 65 57 61 7F 20 47 47 3E 51 7F 3D 3E …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1007: 'TECH v0.3: Annex defenses{n}activate! (placeholder battle)' |
| P101_EXP_DLG_TABLE | 334272–3342A2 | F3:4272–F3:42A2 | 49 | `FF fill (expansion)` | `23 3E 3F 3E 47 4C 3E 4C 7F 3A 4B 3E 7F 3D 48 50 47 65 01 …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1008: 'Defenses are down.{n}Annex flag BATTLE DONE is ON.' |
| P101_EXP_DLG_TABLE | 3342A3–3342EE | F3:42A3–F3:42EE | 76 | `FF fill (expansion)` | `33 24 22 27 7F 4F 54 65 57 7F 49 45 3A 3C 3E 41 48 45 3D …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $1009: 'TECH v0.3 placeholder reward:{n}Received 1 Potion.{n}Annex flag COMPLETE is ON.' |
| P101_EXP_DLG_TABLE | 3342EF–33431A | F3:42EF–F3:431A | 44 | `FF fill (expansion)` | `33 41 3E 7F 3C 41 3E 4C 4D 7F 42 4C 7F 3E 46 49 4D 52 65 …` | field text renderer via $C9/$CB set by P100 hook — Expansion dialogue $100A: 'The chest is empty.{n}(Reward already taken.)' |
| P101_EXP_DLG_TABLE | 330000–33002B | F3:0000–F3:002B | 44 | `FF fill (expansion)` | `00 40 F3 00 2B 40 F3 00 62 40 F3 00 D6 40 F3 00 3E 41 F3 …` | P100 hook (LDA.l table,X) — 11 x 4-byte pointers for dialogue IDs $1000-$100A |
| P100_DLG_HOOK | 301000–301032 | F0:1000–F0:1032 | 51 | `FF fill (expansion)` | `C2 20 A5 D0 C9 00 10 B0 0A E2 20 A9 CD 85 CB 5C C3 7F C0 …` | JML from C0:7FBF (GetDlgPtr) — Dialogue-pointer hook: vanilla IDs unchanged, IDs $1000+ from expansion table |
| P100_DLG_HOOK | 007FBF–007FC2 | C0:7FBF–C0:7FC2 | 4 | `A9 CD 85 CB` | `5C 00 10 F0` | GetDlgPtr C0:7FBF; callers C0:A49A ($48), C0:A4E1 ($4B), C0:D493 (debug) — Replace LDA #$CD / STA $CB with JML $F01000 (displaced code re-executed in hook) |
| T300_EVENTS | 310000–31007E | F1:0000–F1:007E | 127 | `FF fill (expansion)` | `4B 01 10 B6 0A 00 27 1B 00 27 DC F8 C0 4C 81 14 00 27 DC …` | event interpreter via F1 pointers (triggers 24-bit, NPC bridges, choice/if jumps) — Celes Annex TECH v0.3 event scripts (source events/celes_annex_tech/events.evt) |
| T301_NPC_BRIDGES | 0CE5EE–0CE5F2 | CC:E5EE–CC:E5F2 | 5 | `FF FF FF FF FF` | `B2 1C 00 27 FE` | NPC VALE_PLACEHOLDER activation (18-bit NPC event pointer) — bridge: call F1:001C (EvVale) then return |
| T301_NPC_BRIDGES | 0CE5F3–0CE5F7 | CC:E5F3–CC:E5F7 | 5 | `FF FF FF FF FF` | `B2 69 00 27 FE` | NPC REWARD_CHEST activation (18-bit NPC event pointer) — bridge: call F1:0069 (EvChest) then return |
| T302_LAYOUT | 350000–350481 | F5:0000–F5:0481 | 1154 | `FF fill (expansion)` | `<1154 bytes, sha1 97530fee0e90617be22c2a6af2f1c6556c55766b>` | LoadMapTiles (C0:2883) via SubTilemap pointer $15F — BG1 layout 32x32 from maps/celes_annex_tech/layout_bg1.txt (literal LZSS) |
| T303_LAYOUT_PTR | 19D1AD–19D1AF | D9:D1AD–D9:D1AF | 3 | `FF FF FF` | `50 2E 1B` | LoadMapTiles C0:2883: LDA.l SubTilemapPtrs,X + #SubTilemap (24-bit add) — layout index $15F -> F5:0000 (offset 1B2E50 from D9:D1B0) |
| T304_MAP_PROPS | 2DA8A7–2DA8C7 | ED:A8A7–ED:A8C7 | 33 | `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 …` | `00 00 1B 00 24 00 00 B6 1B 4E E7 88 86 5F A9 04 00 00 00 …` | LoadMapProp C0:1CAD (33 bytes -> $0520-$0540) — map $0C7 properties (map.json); tileset/palette from vanilla Magitek-lab map $112 |
| T305_REPACK_EVENT_TRIGGERS | 040000–041A0F | C4:0000–C4:1A0F | 6672 | `<6672 bytes, sha1 11e6eb893afaf5ba1f7e5ff24a1a8c0f6a05cf04>` | `<6672 bytes, sha1 fc78a00eb3717ce88bef664fd6c656b620d08de3>` | EVENT_TRIGGERS loader (pointer-relative; all consumers use the pointer table) — insert map 0C7:EvBattleDoor, map 00C:EvAnnexEnter; slack 18 -> 8 bytes (bytes changed: 3792) |
| T305_REPACK_NPC_PROPS | 041A10–046ABF | C4:1A10–C4:6ABF | 20656 | `<20656 bytes, sha1 11236bfe0b711056beca9a87333b0a2549c5af35>` | `<20656 bytes, sha1 f0b818bfc35524591d5b37c7a3537d59ded7e9fb>` | NPC_PROPS loader (pointer-relative; all consumers use the pointer table) — insert map 0C7:VALE_PLACEHOLDER, map 0C7:REWARD_CHEST; slack 85 -> 67 bytes (bytes changed: 7175) |
| T305_REPACK_SHORT_ENTRANCES | 1FBB00–1FD9FF | DF:BB00–DF:D9FF | 7936 | `<7936 bytes, sha1 829c2a1ce630c57f2fe8b9a893981a642bbbfe50>` | `<7936 bytes, sha1 6d8c830be0cf12138d5c868ae5ca270ace8b7cc1>` | SHORT_ENTRANCES loader (pointer-relative; all consumers use the pointer table) — insert map 0C7:exit->00C; slack 136 -> 130 bytes (bytes changed: 2919) |
| P999_CHECKSUM | 00FFDC–00FFDF | C0:FFDC–C0:FFDF | 4 | `9F 75 60 8A` | `C9 F3 36 0C` | SNES header (emulator/flash-cart validation) — Recalculated checksum 0C36 / complement F3C9 |
