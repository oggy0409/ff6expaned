# Accepted baselines (as of TECH v0.3 acceptance)

| Baseline | ROM | SHA-1 | CRC32 | Status |
|---|---|---|---|---|
| TECH v0.1 | `FF6X_Rev1_TECH_v0.1_LEGACY_REBUILD.sfc` | `c412f12938f9f4bd9c7e3f857572d3b773bab649` | `DA88A7DE` | RUNTIME VERIFIED (4 MiB, F0 reads) |
| TECH v0.2 | `FF6X_Rev1_TECH_v0.2.0_EVTEST_REBUILD.sfc` | `0258a0fc122bb109e7ca343dda61c58af2e921fb` | `32725A65` | RUNTIME VERIFIED (expansion dialogue, event bridge, flag persistence) |
| **TECH v0.3** | `FF6X_Rev1_TECH_v0.3.0_CELES_TECH.sfc` | `e0196eb30fc03cf076c0d1306b0c09b664f7b2a4` | `3E6B68E2` | **RUNTIME VERIFIED & ACCEPTED** — core Celes slice pipeline |
| TECH v0.3 production branch | `FF6X_Rev1_TECH_v0.3.0_PRODUCTION.sfc` | `0eda0bab925f8b6f1c840c20523f9413cb586ec3` | `8D05263F` | engine branch of the accepted v0.3 build |

## Evidence for TECH v0.3
User runtime test of the QA harness `FF6X_Rev1_TECH_v0.3.1_CELES_TECH_QA_ACCESS.sfc`
(SHA-1 `bf443c85dc448c0a86169f58dce43d77684c36f5`), which contains the v0.3.0 slice
byte-for-byte except the documented Q-patches (QA entry, QA exit, battle group $28→$01).
All required tests passed: Annex entry/exit, collision, Vale dialogue/state progression,
sealed door, battle start/return, no battle loop, one-time Potion reward, COMPLETE
persistence, save/reset/load, re-entry, unrelated vanilla dialogue/battle regression.

Accepted scope: map entry/exit pipeline, expansion dialogue, production flags
($14A/$14B/$14C/$6F8/$6F9), event battle return, one-time reward, persistence.
Not covered by user runtime: the v0.3 Falcon entry trigger and battle group $28
formation (QA build used group $01; same event pipeline).

The QA harness v0.3.1 is **not** a baseline (QA HARNESS ONLY).
