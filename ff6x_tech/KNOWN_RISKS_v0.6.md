# TECH v0.6 — known risks / open items

| # | Risk | Severity | Mitigation / status |
|---|---|---|---|
| R1 | Consumer completeness: the colosseum stencil bank byte (C3:AFFD `lda #$d2`) was not reachable through the symbol cross-reference; found by reading every user. Other non-symbolic reads of MonsterPal/MonsterStencil could exist. | Medium | Source search for `#$d2`, `#$7820`, `#$a820/22/24`, `#$ac24` (only C3:AFFD). Differential test of all 576 vanilla formations: graphics buffer, palette numbers, palette bytes, sizes identical 576/576; Sketch path identical on 6 formations (small/large/3bpp). Colosseum not runtime-tested (late game). |
| R2 | Vanilla reads MonsterPal + `$FFF0` for every unused battle palette slot (index `$FFFF`). After relocation this reads FB:FFF0. | Low | 16 vanilla bytes (D3:7810) placed at FB:FFF0 (region ENEMYX_PAL_EMPTY_SLOT) → palette RAM identical. Must never be overwritten by later graphics allocations (manifest region). |
| R3 | Expansion flag = MonsterGfxProp byte2 bit5. Byte2 bit6 is the 9th stencil bit (`$81AB`), bits 2–4 unused. Third-party data with bit5 set would be read from the expansion bank. | Low | Vanilla never sets bits 2–6 (selftest 31); builder writes bit5 only for custom assets; stencil indices kept 8-bit. |
| R4 | Colosseum menu has its own hard-coded graphics base E9:7000 (C3:AF8D/AF93) and ignores the flag. | Info | New monsters are not colosseum-eligible (8-bit colosseum table). |
| R5 | Router adds ~10 cycles per monster graphics load: battle fade-in is 1 frame later in 3/576 formations (`$02A`, `$03D`, `$10F`); engine data identical. | Cosmetic timing | Verified as 1-frame phase shifts. |
| R6 | Dialogue width check was off by one (lines of exactly 220 px wrapped in game). | Fixed | Limit 219 px (`ff6x/text.py`); all accepted text ≤ 211 px, accepted builds byte-identical. |
| R7 | QA: Terra must be alive and have Ramuh equipped for MP credit; the opening party gets weak after many QA battles (isolation formations use full vanilla Leafer/Dark Wind stats). | QA-only | Guide orders MP test before isolation battles; heal with dropped Tonics (menu Item). |
| R8 | QA tile in the opening Magitek sequence (KNOWN_QA_ISSUE_v0.3.1); Wait mode + empty Item list (v0.5 note). | QA-only | Unchanged. |
| R9 | The Sketch drawing of a monster is shown behind Terra's sprite (vanilla behaviour), so on-screen exactness of the sketched sprite is evidence only; the decoded tiles and palette pointer are verified exactly. | Info | Poke test C04. |
| R10 | Steal/Sketch/Control on custom monsters verified only by RAM poke. | QA-only | User marks NOT TESTED. |
| R11 | Custom assets are QA placeholders; final art needs stencil-friendly shapes (sprite starts at the top edge; empty interior rows are filled with a blank tile by the builder). | Info | Importer reports `empty_rows_filled`. |
| R12 | Accepted v0.5 QA ROM issue (TESTMOB B look) is not a bug in v0.5 routing; v0.5 baseline remains byte-identical (regression target). | Info | Phase A result. |
