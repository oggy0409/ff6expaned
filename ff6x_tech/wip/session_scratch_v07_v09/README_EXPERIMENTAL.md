# EXPERIMENTAL / DEBUG SCRATCH — TECH v0.7.1 … v0.9 sessions

**Status: EXPERIMENTAL. Never imported by `build.py`, never part of any accepted ROM, not run by `tools/selftest.py`.**
Safe to delete; kept on purpose (handoff rule: do not delete dead ends) because they document how defects were found.

These are the session's throw-away probes, copied verbatim from the session scratchpad at the v0.9 freeze. Most
of them hard-code the scratchpad path
`/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad` (variable `S`) and ROM
paths under it (`o09/`, `outA/`, `final/` …); edit those before re-running. They need `stable-retro`, `numpy`,
`Pillow` (same as `tools/emu_*.py`).

| File(s) | What it was for | Outcome |
|---|---|---|
| `run072.sh`, `run073.sh`, `run08.sh`, `run09.sh`, `run_final.sh` | regression runners per milestone (the v0.9 one is generalised in `tools/run_regression_v09.sh`) | superseded by `tools/run_regression_v09.sh` |
| `stage.sh`, `hashes.py`, `delta.py` | v0.9 QA-package staging, `HASHES_v0.9.txt`, v0.x→v0.y byte delta | superseded by `tools/patch_table_v09.py` + `tools/handoff_verify_v09.py` |
| `colo*.py`, `recep.py` | v0.7.2 Colosseum black-screen reproduction / receptionist probes | root cause found → `COLOSSEUM_ROOT_CAUSE_v0.7.2.md` |
| `menu*.py`, `scr*.py`, `probe*.py`, `dbg*.py`, `eqdbg.py`, `c1diag*.py` | menu navigation / screen / RAM probes (v0.7.1-v0.8) | folded into `tools/emu_*` suites |
| `bt*.py`, `b3c.py`, `gswap.py`, `hswap.py`, `jump.py`, `h4.py` | battle hand / Genji / Jump probes (v0.7.1-v0.8) | folded into `tools/emu_item_battle.py`, `tools/emu_equip_battle_v08.py` |
| `ram_bisect.py`, `lag.py` | v0.8 B-accumulator bisect; event `$80` timing (R16) | → `ENGINE_FIX_v0.8_B_ACCUMULATOR.md`, KNOWN_RISKS R16 |
| `cactrot.py`, `chest2.py`, `celes_dbg.py` | early map / chest / Celes Annex probes | informative only |
| `dis.py`, `dis.sh` | disassembly helpers (need the everything8215/ff6 disassembly) | informative only |
| `v09_probes/a1.py … a12.py` | v0.9 probes: field use (A twice), battle item flow, consumable animation frames, extended shop, Sell, rare paging / description overlap, Throw list | folded into `tools/emu_cons_v09.py`, `emu_cons_battle_v09.py`, `emu_rare_v09.py`, `emu_stress_v09.py` |
| `docs_drafts/` | patch-table drafts (`pt*.md`), item mapping draft (`ica_tables.md`), `asm_oracle.json` result, the v0.7.1 relocation file before a fix, v0.7.2 delta notes | drafts; the published versions are the `PATCH_TABLE_v*.md` / `data/` files |

Not copied (too large or regenerable): `insn.tsv` (7.5 MB, regenerate with `devtools/rev1_insn_index.py`), the
everything8215/ff6 disassembly checkout (`ff6dis/`, external), emulator save states, screenshots of debug runs,
intermediate ROM builds.
