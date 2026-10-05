# FF6 Expanded Edition — TECH v0.3: Celes "Echoes of the Empire" technical vertical slice

**STATIC PASS · EMULATOR SMOKE PASS (27/27 + save/reset/load) · RUNTIME USER QA PENDING**

Baseline: Final Fantasy III (USA) (Rev 1), unheadered, SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`.
Accepted foundations: TECH v0.1 (4 MiB / F0 reads), TECH v0.2 (expansion dialogue, event bridge, flag persistence).
Nothing in this build is final content: no final Celes script, art, Praetor, Runic Crest, monster or item architecture.

## Outputs (`out/`)
| File | SHA-1 | CRC32 | SNES chk | Status |
|---|---|---|---|---|
| `FF6X_Rev1_TECH_v0.3.0_CELES_TECH.sfc` | `e0196eb30fc03cf076c0d1306b0c09b664f7b2a4` | `3E6B68E2` | `0C36` | **QA ROM** (production + slice) |
| `FF6X_Rev1_TECH_v0.3.0_PRODUCTION.sfc` | `0eda0bab925f8b6f1c840c20523f9413cb586ec3` | `8D05263F` | `20F6` | production branch (engine only) |
| `FF6X_Rev1_TECH_v0.2.0_EVTEST_REBUILD.sfc` | `0258a0fc122bb109e7ca343dda61c58af2e921fb` | `32725A65` | `96FF` | regression = accepted v0.2 |
| `FF6X_Rev1_TECH_v0.1_LEGACY_REBUILD.sfc` | `c412f12938f9f4bd9c7e3f857572d3b773bab649` | `DA88A7DE` | `3F4D` | regression = accepted v0.1 |

Each ROM has `.bps` (source-CRC checked), `.ips`, `.manifest.json` (every patch, placement,
changed range, listings, notes) and `.diff.csv`. `BUILD_SUMMARY.json` lists all hashes.
Celes BPS SHA-1 `ae09b2894636b36378c8e804da1a1232fee5895a`; IPS SHA-1 `0d81ef05ac37628f6313a4cd15a6ef835bd4984b`.

## Build
```
python build.py "Final Fantasy III (USA) (Rev 1).sfc"              # all 4 targets
python build.py "<rom>" --target celes-tech
python tools/selftest.py "<rom>"                                    # 16 fail-closed guard tests
```
Python 3.8+, stdlib only. Deterministic (21 output files byte-identical across rebuilds).
Dev-only tools (need extra software): `tools/oracle_check.py` (cc65 + disassembly),
`tools/emu_*.py` (stable-retro).

## What changed vs v0.2
1. **Production branch** (`production`): 4 MiB + build metadata + the accepted dialogue hook
   (C0:7FBF → F0:1000) and expansion dialogue table (only the reserved $1000 diagnostic).
   All EVTEST content removed (NPC $037/#9, trampoline, bit $0FF usage, test lines).
2. **New pipeline code** (production-grade, reusable): `ff6x/lzss.py` (verified on all 350
   vanilla layouts), `ff6x/tables.py` (packed per-map tables + exact NPC codec),
   `ff6x/eventasm.py` + `.evt` source format (24/24 encodings verified against the
   disassembly macros), `ff6x/mapsrc.py` (map package compiler + walkability proof),
   event-bit registry in `allocations.json` (refuses bits not FREE in the Rev 1 audit),
   dialogue width check against the ROM font table.
3. **Celes slice** (`celes-tech`): source in `maps/celes_annex_tech/` and `events/celes_annex_tech/`.

## Slice design
```
Falcon interior (map $00C, WoR) — step on (13,46) → "Enter the Annex? Yes/No"
  Yes → Annex map $0C7, arrive (16,27)
    corridor → NPC room: VALE placeholder (12,16) → $1002, sets STARTED
    door trigger (16,10): before Vale → "sealed", pushed back
                           after Vale  → $1007, event battle group 40 (vanilla), victory → BATTLE_DONE, step up
    battle room: reward chest object (16,6) → +1 Potion, COMPLETE, chest hidden (once)
    exit (16,29) → Falcon interior (15,47)
```

| Item | Value |
|---|---|
| Map | $0C7, 32×32, BG1 layout $15F @ F5:0000 (literal LZSS, 1154 B), BG2 = vanilla layout $12A (all tile $01), BG3 none, tile props set $24, props row from map $112 (Magitek lab) with overrides |
| NPC #0 (obj $10) | VALE placeholder · gfx $18 MAN · pal 1 · (12,16) · facing DOWN · speed 1 · no movement · event bridge CC:E5EE → F1:001C (EvVale) · visible iff NPC bit $6F8 |
| NPC #1 (obj $11) | reward chest · gfx $54 TREASURE_CHEST · pal 7 · (16,6) · no react · bridge CC:E5F3 → F1:0069 (EvChest) · visible iff NPC bit $6F9 |
| Triggers | $0C7 (16,10) → F1:0040 EvBattleDoor · $00C (13,46) → F1:0000 EvAnnexEnter |
| Exit | short entrance $0C7 (16,29) → $00C (15,47), facing DOWN, Z_UPPER |
| Battle | event battle group 40 (formation $1A1 both slots: Mega Armor + ProtoArmor), bg = map default ($1B); vanilla post-battle check CA:5EA9 |
| Reward | item $E9 **Potion** ×1 — common consumable sold in shops: proves one-time give without touching the item architecture or economy |
| Dialogue | $1001–$100A in F3:402B–F3:431A, pointers F3:0004–F3:002B (4-byte lo/hi/bank/0); hook path C0:7FBF JML F0:1000 (accepted v0.2 mechanism) |

### Production flags (all audited FREE: no vanilla script/NPC/ASM reference, init 0)
| Bit | RAM | Name | Default | Set by | Cleared by |
|---|---|---|---|---|---|
| $14A | $1EA9.2 | CELES_ANNEX_TECH_STARTED | 0 | first Vale talk | — |
| $14B | $1EA9.3 | CELES_ANNEX_TECH_BATTLE_DONE | 0 | after test battle | — |
| $14C | $1EA9.4 | **CELES_ANNEX_TECH_COMPLETE** | 0 | reward taken | — |
| $6F8 | $1F5F.0 | NPC_ANNEX_VALE_VISIBLE | 0 | entry event (Yes) | — |
| $6F9 | $1F5F.1 | NPC_ANNEX_CHEST_VISIBLE | 0 | entry event if not COMPLETE | reward event |

These are reserved permanently for the TECH slice (like $0FF) so test saves never
pollute final-arc flags. `$0FF` remains TECH_TEST only and is not used here.

### Event listing (F1:0000–F1:007E, from `events.evt`)
See `notes.event_listing` in the Celes manifest (full byte listing with labels).

## Exact patch table
`PATCH_TABLE_v0.3.md` (generated from the manifests: PC, SNES, length, original, new, consumer).
Vanilla-space claims and table repacks: `audits/vanilla_claims_v0.3.md`.

Vanilla writes in `celes-tech`:
| ID | PC | SNES | Original → New |
|---|---|---|---|
| P100 | 007FBF | C0:7FBF | `A9 CD 85 CB` → `5C 00 10 F0` (accepted hook) |
| T301 | 0CE5EE / 0CE5F3 | CC:E5EE / CC:E5F3 | `FF×5` → `B2 1C 00 27 FE` / `B2 69 00 27 FE` |
| T303 | 19D1AD | D9:D1AD | `FF FF FF` → `50 2E 1B` |
| T304 | 2DA8A7 | ED:A8A7 | 33×`00` → `00 00 1B 00 24 00 00 B6 1B 4E E7 88 86 5F A9 04 00 00 00 00 00 00 00 55 57 18 00 0E 21 00 1F 1F 00` |
| T305 | 040000–041A0F | C4:0000–C4:1A0F | trigger table repack (+2 records) |
| T305 | 041A10–046ABF | C4:1A10–C4:6ABF | NPC table repack (+2 records) |
| T305 | 1FBB00–1FD9FF | DF:BB00–DF:D9FF | short-entrance table repack (+1 record) |
| P999 | 00FFDC | C0:FFDC | `9F 75 60 8A` → `C9 F3 36 0C` |

Expansion allocations (all inside `allocations.json` regions): F0:0000 metadata, F0:1000 hook,
F1:0000 events, F3:0000 dialogue pointers, F3:4000 dialogue text, F5:0000 layout.

## Behaviour notes
- **Run away**: possible (normal monsters). FF6 event scripts can't tell escape from victory,
  so escaping also sets BATTLE_DONE in this TECH build. The production boss will use a no-escape formation.
- **Defeat**: vanilla Game Over (CA:5EA9 → GameOver) → reload save.
- **Saving inside the Annex**: not possible (no save point; same as vanilla dungeons). Save on the world map.
- **Re-entry**: always allowed. After completion Vale shows the final-state line, the door is inert, the chest stays gone.

## Reports
`REGRESSION_REPORT_v0.3.md` · `KNOWN_RISKS_v0.3.md` · `USER_QA_TECH_v0.3_VI.md` ·
`audits/eventasm_oracle_report.json` · emulator evidence in `out/emu_celes/`.
