# FFVI Expanded Edition — Accepted Baselines

## Creative/content
- `v1.2 CREATIVE LOCK` remains the authoritative design source.

## ROM baseline
- Final Fantasy III (USA) (Rev 1) / FFVI US v1.1
- Unheadered size: `0x300000`
- SHA-1: `057ADA1C641E3E0B3CA34E6E4F4EB1B05A87143A`
- CRC32: `C0FA0464`

## TECH v0.1 — ACCEPTED / RUNTIME VERIFIED
User confirmed:
- EXPTEST displayed correctly for opening MagiTek
- MagiTek behavior remained correct
- normal Fight displayed as EXPTEST
- Fight behavior remained correct
- save/reset/load OK

This accepted the 4 MiB expansion and F0-bank runtime read foundation.

## TECH v0.2 — ACCEPTED / RUNTIME VERIFIED
User confirmed:
- new dialogue stored in expansion bank displayed correctly
- event bit changed to ON on first interaction
- second interaction showed the persisted ON state
- save/reset/load preserved the state
- vanilla flow/dialogue around the test remained functional
- no freeze or return-control issue observed

TECH v0.2 is now the gameplay-accepted technical baseline.

### Permanent rule
- Test bit `$0FF` is reserved forever for TECH_TEST.
- Never allocate `$0FF` to production content.

## Next target
`TECH v0.3 — Celes / Echoes of the Empire Technical Vertical Slice`
