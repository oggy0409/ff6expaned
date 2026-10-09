# FF6 Expanded Edition — TECH Foundation v0.2.0

Baseline: **Final Fantasy III (USA) (Rev 1)**, unheadered, 0x300000,
SHA-1 `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`, CRC32 `C0FA0464`.
No story/content is implemented in this round.

| Target | Purpose | Status |
|---|---|---|
| `foundation` | **Production branch**: 4 MiB + build metadata. No gameplay change. EXPTEST removed. | STATIC PASS · emulator boot smoke OK · RUNTIME PENDING |
| `evtest` | **Test branch**: Phase 2 event + dialogue in expansion space | STATIC PASS · emulator smoke OK · **RUNTIME PENDING (user)** |
| `legacy-v0.1` | Regression: TECH v0.1 rebuilt through the new framework | byte-identical to accepted v0.1 (`c412f129…`) |

## Build
```
python build.py "Final Fantasy III (USA) (Rev 1).sfc"            # all targets
python build.py "Final Fantasy III (USA) (Rev 1).sfc" --target evtest
python tools/selftest.py "Final Fantasy III (USA) (Rev 1).sfc"   # 10 fail-closed guard tests
```
Windows: drag the ROM onto `BUILD.bat`. Python 3.8+ only, no extra packages.
Outputs go to `out/`: `.sfc`, `.ips`, `.bps`, `.manifest.json`, `.diff.csv`, `BUILD_SUMMARY.json`.
Builds are deterministic (two clean rebuilds compared byte-for-byte, including manifests).

## Hashes (v0.2.0)
| File | SHA-1 | CRC32 | SNES chk |
|---|---|---|---|
| `FF6X_Rev1_TECH_v0.2.0_FOUNDATION.sfc` | `18eafebbd40cd43a8b00e32b162ebe6284599e14` | `36DDE8C2` | `6242` |
| `FF6X_Rev1_TECH_v0.2.0_EVTEST.sfc` | `0258a0fc122bb109e7ca343dda61c58af2e921fb` | `32725A65` | `96FF` |
| `FF6X_Rev1_TECH_v0.1_LEGACY_REBUILD.sfc` | `c412f12938f9f4bd9c7e3f857572d3b773bab649` | `DA88A7DE` | `3F4D` |

BPS patches verify the source CRC32 (they refuse a wrong ROM). IPS has no check.

## Framework (Phase 1)
```
build.py                 targets, outputs, manifests
ff6x/hirom.py            explicit C0–FF ⇄ PC conversion (mirrors rejected), event-pointer helpers
ff6x/romimage.py         hash guard, read-only master, expand, guarded patch()/place(),
                         byte ownership + collision detection, checksum, unattributed-change check
ff6x/allocations.py      loader/validator for data/allocations.json (overlap rejection)
ff6x/asm65816.py         tiny explicit assembler (listing in manifest)
ff6x/text.py             DTE-free dialogue encoder
ff6x/patchfmt.py         IPS + BPS writers and reference appliers (round-trip verified each build)
data/baseline.json       Rev 1 identity
data/allocations.json    SINGLE SOURCE OF TRUTH for F0–FF + vanilla-space claims
patches/                 core.py, dialogue_hook.py, evtest.py, legacy_v01.py
tools/                   selftest, audits, emulator smoke harness
audits/                  event-bit, map, monster, item reports (+ JSON)
```
Guarantees enforced at build time: hash mismatch → abort; copier header →
abort; every vanilla write asserts original bytes in the clean ROM;
expansion writes must lie inside a region active for the target and on
pristine `FF`; regions in the same target may not overlap; any byte changed
without an owning patch → abort; reserved/blocked regions refuse writes;
checksum + complement recomputed and self-checked; header bytes asserted.

### Allocation map (F0–FF)
| Region | SNES | Status |
|---|---|---|
| BUILD_METADATA | F0:0000–F0:00FF | active |
| RESERVED_F0_LOW | F0:0100–F0:0FFF | reserved (never alias v0.1 layout) |
| ENGINE_CODE | F0:1000–F0:7FFF | active |
| ENGINE_TABLES | F0:8000–F0:FFFF | reserved |
| EVENT_EXPANSION | F1:0000–F2:FFFF | active |
| DIALOGUE_PTRS | F3:0000–F3:3FFF | active (IDs $1000–$1FFF, 4 B each) |
| DIALOGUE_TEXT | F3:4000–F4:FFFF | active |
| MAP_EXPANSION | F5:0000–F7:FFFF | reserved |
| MONSTER_EXPANSION | F8:0000–F9:FFFF | reserved |
| ITEM_EXPANSION | FA:0000–FA:FFFF | **blocked** (item decision) |
| GRAPHICS_EXPANSION | FB:0000–FE:FFFF | reserved |
| UNALLOCATED | FF:0000–FF:FFFF | reserved |

## Phase 2 — event + dialogue proof (`evtest`)
**Pointer formats found (Rev 1, verified bytes):**
- Event operands (`$B2` call, `$C0–$CF` jumps…) are 24-bit, interpreter does
  `adc #$CA` on the high byte → **F0–FF reachable natively** (F1 = `$27`).
- NPC event pointers are **18-bit** → CA:0000–CD:FFFF only → 5-byte bridge needed.
- Dialogue: 13-bit ID → `GetDlgPtr` C0:7FBF reads 16-bit pointers at CC:E602,
  bank CD/CE chosen by CC:E600. Only `GetDlgPtr` reads that table. Text
  renderer reads `[$C9]` with bank `$CB` → any bank works once `$C9/$CB` are set.

**Every changed byte** (PC / SNES / original → new / consumer):
| ID | PC | SNES | Original | New | Consumer / reason |
|---|---|---|---|---|---|
| P100 | 007FBF–007FC2 | C0:7FBF | `A9 CD 85 CB` | `5C 00 10 F0` | `GetDlgPtr` entry → JML hook; callers C0:A49A (`$48`), C0:A4E1 (`$4B`), C0:D493 (debug) |
| P100 | 301000–301032 | F0:1000 | FF | `C2 20 A5 D0 C9 00 10 B0 0A E2 20 A9 CD 85 CB 5C C3 7F C0 29 FF 0F C9 03 00 90 03 A9 00 00 0A 0A AA BF 00 00 F3 85 C9 E2 20 BF 02 00 F3 85 CB 5C DC 7F C0` | ID < $1000: re-run displaced `LDA #$CD/STA $CB`, JML C0:7FC3 (vanilla). ID ≥ $1000: ptr from F3 table, JML C0:7FDC (vanilla epilogue) |
| P101 | 330000–33000B | F3:0000 | FF | `00 40 F3 00 2B 40 F3 00 7F 40 F3 00` | expansion dialogue pointers $1000–$1002 |
| P101 | 334000–3340CD | F3:4000 | FF | 3 strings | $1000 out-of-range diagnostic, $1001 first line, $1002 repeat line |
| T200 | 310000–310015 | F1:0000 | FF | `C0 FF 80 0F 00 27 4B 01 10 D0 FF 4B 52 00 FE 4B 02 10 4B 52 00 FE` | if bit $0FF → Seen; dlg $1001; set bit $0FF; dlg $0052 (vanilla); return / Seen: dlg $1002; dlg $0052; return |
| T201 | 0CE5EE–0CE5F2 | CC:E5EE | `FF FF FF FF FF` | `B2 00 00 27 FE` | trampoline (call F1:0000, return); padding proven unused: `audits/vanilla_claim_CCE5EE.md` |
| T202 | 0426F4–0426F6 | C4:26F4 | `D8 75 C8` | `EE E5 CA` | Figaro Castle (map $037) NPC #9 event ptr CA:75D8 → CC:E5EE; palette/scroll/switch bits preserved |
| P001 | 300000–30003F | F0:0000 | FF | metadata | build ID (no runtime consumer) |
| P999 | 00FFDC–00FFDF | C0:FFDC | `9F 75 60 8A` | `00 69 FF 96` | checksum `96FF` / complement `6900` |

Trigger: Figaro Castle (WoB), rooftop NPC at (44,21) who normally says
"Weapons and items manufactured here are sent to South Figaro."
Event bit: `$0FF` (`$1E9F` bit 7), audited unreferenced, reserved forever as TECH_TEST.
Vanilla flow: vanilla line is still shown after the new line; event returns
through the trampoline's `FE`; the vanilla NPC script at CA:75D8 is untouched.

## Verification performed by Claude (not user runtime)
- TECH v0.1 reproduced: the clean Rev 1 image was recovered from the accepted
  v0.1 ROM (truncate to 3 MiB, restore the 3 `BF A0 CE D8` loads and the
  original checksum `8A60/759F`) → SHA-1 `057ADA1C…` matched exactly; the
  original `build_tech_test.py` and the new framework both rebuild `c412f129…`.
- Static: all asserts, IPS/BPS round-trip, checksum, deterministic rebuild,
  10/10 negative guard tests.
- Disassembly cross-check: everything8215/ff6 built with `ROM_VERSION=1`
  matches Rev 1 in all code and event regions (differences only in text/DTE
  assets), so the routine/label addresses used here are Rev 1-valid.
- **Emulator smoke (snes9x core, headless, RAM-poke teleport):** both ROMs
  boot → New Game → first control. `evtest`: on map $037 the NPC's runtime
  event pointer is CC:E5EE; talking shows `$1001` from bank F3 then vanilla
  `$0052`; bit $0FF goes 0→1; second talk shows `$1002`; out-of-range ID
  `$1FFF` shows the diagnostic; player regains control. Screenshots in
  `out/emu_evtest/`. Save/reset/load was **not** emulated.

## Known risks
- Runtime on real hardware/other emulators not yet confirmed by you.
- The teleport used in the emulator test skips normal progression; the real
  route to Figaro Castle has not been played.
- If the NPC is hidden at the moment you visit (bit `$30B` cleared during the
  night/escape scene), the test cannot trigger — use the first daytime visit.
- `GetDlgPtr` hook affects every dialogue (vanilla path re-executes the exact
  original instructions; watch for any wrong/garbled vanilla text).

## Next
After you report PASS for `evtest`, it becomes baseline **TECH v0.2**, the
dialogue hook moves into the production branch, and Phase 3 (Celes vertical
slice on map `0C7`) starts. Item architecture needs your decision first for rewards.
