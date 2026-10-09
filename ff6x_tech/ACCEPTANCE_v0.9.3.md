# TECH v0.9.3 — ACCEPTED / USER RUNTIME PASS (frozen 2026-10-07)

The v0.9.3 package (`FF6X_TECH_v0.9.3_VISUAL_STATE_VRAM_HOTFIX_QA.zip`) passed your runtime QA. It is now the accepted
baseline. This record changes no ROM byte. `build.py` now also pins the accepted QA hash, and all 27 targets were
rebuilt byte-identical after the change.

## Accepted hashes
| target | file | SHA-1 | CRC32 | note |
|---|---|---|---|---|
| `item-tech` (QA) | `FF6X_Rev1_TECH_v0.9.3_VISUAL_STATE_VRAM_HOTFIX_QA.sfc` | `15af77fe9c01f54844fbcbbb0c5f1d65768d55f0` | `02DA7373` | v0.9.1 item alignment + v0.9.2 Celes enablers + v0.9.3 visual hotfix |
| `production` | `FF6X_Rev1_TECH_v0.9.1_PRODUCTION.sfc` | `2dc73bfbbcf4657eb59eec93bd614181ecdc817c` | `01AE6F84` | v0.9.1 item alignment; **unchanged** by v0.9.2 / v0.9.3 |
| `celes-tech` | `FF6X_Rev1_TECH_v0.9.1_CELES_TECH.sfc` | `e2192311a997ee49315807508d71ca202d4a8d09` | `EA66714A` | v0.9.1 item alignment; **unchanged** by v0.9.2 / v0.9.3 |

The frozen v0.9 targets (`production-v0.9` `99cd74df…`, `celes-tech-v0.9` `e4c07031…`, `item-tech-v0.9` `e1136805…`) still
rebuild byte-exact.

## User runtime results
| area | result |
|---|---|
| map `$1A2` ash / steel palette | **PASS** (visibly applied) |
| Lunaris (WoR dog) sprite | **PASS** (corruption fixed) |
| Suppressor Bits (both) | **PASS** (both render cleanly) |
| E5 party dialogue | **PASS** |
| E7 Vale | **PASS** |
| E8 event / state logic | **PASS** |
| E8 save persistence | **PASS** |
| v0.9.1 / v0.9.2 items: consumables, shops, Magitek Cell cap, Darill's Coin; save / load / migration; WoR + Falcon; Praetor 70% / 40%; Grounding Field | **PASS** (user QA of v0.9.2; these bytes did not change in v0.9.3) |

## Classification
* **E8 state / persistence architecture: ACCEPTED.** This covers the event bits, the startup-event redraw, `states.json`
  as the source, the builder validation and persistence.
* **E8 placeholder art: REJECTED FOR PRODUCTION.** The E8 placeholder memorial / archive artwork is deferred to a
  dedicated art pass (ART ASSET GATE v1.0, then human art). The v0.9.3 vanilla-tile objects stay in the QA ROM only as
  state markers.
* Closed; do not reopen: the Lunaris / Suppressor Bit VRAM investigation and the v0.9.3 VRAM fixes (`QaCelParty93`).

## Documentation fixes in this freeze
* `PROJECT_STATE_v0.9.3.json`:
  * baseline set to v0.9.3;
  * the v0.9 hashes kept under `frozen_v0_9_hashes`;
  * status set to PASS / PASS / PASS;
  * the risk reference updated to R1-R78.
* The **Creative Lock / Tech Gate** sources were listed as missing in the older state files. That was stale: they are in
  `docs/design_sources/`, recovered by `CREATIVE_SOURCE_RECOVERY_v1.0`.
* `KNOWN_RISKS_v0.9.3.md`: R55 records the art rejection; a new row corrects the creative-sources note.
* `build.py`:
  * the QA target status now reads accepted, and the accepted QA hash is pinned (`expect_sha1` / `expect_crc32`);
  * the manifest runtime labels were updated.
  * Neither change touches ROM bytes.

## Next
ART ASSET GATE v1.0 (export only). CONTENT v1.0 and the Celes ROM Script Pass have **not** started.
