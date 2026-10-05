# FF6 Expanded Edition — TECH v0.6.2 formation safety + TECH v0.7 item architecture audit

| Part | Status |
|---|---|
| TECH v0.6.1 | **ACCEPTED / RUNTIME VERIFIED** (named baseline, `docs/ACCEPTED_BASELINES_v0.6.1.md`) |
| TECH v0.6.2 formation safety | STATIC PASS · EMULATOR PASS · tooling only, **no ROM byte changed** (no user QA required) |
| TECH v0.7 item architecture | **AUDIT / DECISION REPORT ONLY** — nothing implemented, no architecture chosen |

## ROMs (rebuilt, unchanged)
| File | SHA-1 | CRC32 |
|---|---|---|
| `FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA.sfc` (accepted) | `8a55707ff2b4cd1364fdabf75e91422ba90ff8bb` | `289BD3B9` |
| `FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc` | `26ebd7d3b1a16bfae94625cead054edc34a1a5b6` | `C9DB005B` |
| `FF6X_Rev1_TECH_v0.6.0_CELES_TECH.sfc` | `a7ae5d4c1c49ce5cfcbca65de943678b86923fce` | `E2BDA3B1` |
All 15 targets reproduce (v0.1 … v0.6.1); builder now asserts the v0.6.1 QA hash. Determinism: 2 builds, 86 files, 0 diffs.
Selftests 59/59 (9 new formation-safety guards).

## TECH v0.6.2 (details: `FORMATION_SAFETY_v0.6.2.md`)
* Builder validates every Expanded Edition formation on the built image: opaque sprite bounding box vs visible field
  (x 8–247, y 4–150, window y ≥ 151); edge margin < 8 px = ERROR, < 16 px = WARNING; crossing into the window = ERROR;
  party lane x > 167 = WARNING; `layout_exception` only for large-boss sprites with a reason.
* R13 audit: Magitek armor overwrites monster VRAM cells rows 0–11 × cols 12–15 (48 cells) for 1–3 riders, any
  formation; matrix for all 13 VRAM maps in `data/vram_safety.json` (all-safe maps: 2, 8, 9, 10, 11; always unsafe:
  map 1 slot 5, map 7 slot 1, map 12 slot 5; others sprite-dependent).
* `magitek_possible` mandatory per EE formation; conflict = ERROR + suggested safe VRAM maps; new optional `vram_map`.
* Preview PNG per formation (`out/formation_preview/`), also without building ROMs: `build.py <rom> --preview-only`.
* The validator flags the accepted v0.6.1 `$242/$243` slot-0 Dark Wind (left margin 0 px) and, on the v0.6.0 QA ROM,
  the slot-5 Magitek conflict that caused the v0.6 failure. Frozen QA targets run in report mode.

Changed files (no ROM effect): `ff6x/formation_safety.py`, `ff6x/formation_preview.py`, `ff6x/png.py` (RGB writer),
`ff6x/monsters.py` (`vram_map`), `build.py` (validation, previews, `--preview-only`, v0.6.1 hash lock, runtime status),
`data/vram_safety.json`, `formations/*.json` (+`magitek_possible`), `formations/examples/`, `tools/selftest.py`,
`tools/magitek_vram_audit.py`, `tools/formation_safety_examples.py`, `devtools/make_vram_safety.py`,
`devtools/vanilla_formation_calibration.py`, `devtools/item_mapping_v07.py`.

## TECH v0.7 audit (details: `ITEM_ARCHITECTURE_DECISION_v0.7.md`, `audits/ITEM_MAPPING_PROPOSAL_v0.7.json`)
0 free item IDs in Rev 1. Compared A (reassign 39 vanilla IDs: 113 vanilla references displaced, no ASM),
B (full 9-bit item engine: 6–12 KB ASM, very high risk), C (equipment-only "signature bank" `$100–$13F`, event-delivered,
no vanilla displacement, 2–5 KB ASM, needs 12+ B proven-free saved RAM). **Recommendation: C, pending your approval**,
plus decisions D2 (8 new consumables), D3 (5 key items via rare-item extension), D4–D6.

## Known risks
`KNOWN_RISKS_v0.6.2.md` (R1–R15, F1–F5).
