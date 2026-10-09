# RARE ITEM EVENT API — TECH v0.9

Three event opcodes that are **unused in Rev 1** (`EventCmdTbl` entries pointed to the vanilla `RTS` lock-up at
C0:B91A; no Rev 1 script uses them) now call the rare-item engine (`asm/item_v09/c0.s`, `v09.s`):

| opcode | bytes | syntax (`.evt`) | effect |
|---|---|---|---|
| `$69` | `69 id` | `give_rare <id>` | rare id owned (0-19: vanilla event bit `$1D0 + id`; 20-51: `XRARE` bit, only if defined in `XRareDef`) |
| `$6D` | `6D id` | `take_rare <id>` | rare id not owned |
| `$6E` | `6E id sl sh` | `has_rare <id> -> SWITCH` | event switch `sh:sl` := 1 if owned, else 0 |

* `id` is a **logical rare id 0-51** (one byte). Ids ≥ 52 and undefined FF6X ids are ignored (no RAM change).
* The rare-block signature is rewritten on every FF6X change.
* The commands exist only with the TECH v0.9 engine: the event assembler refuses them for other targets
  (`give-rare-without-v09-engine`) and refuses ids > 51.
* The v0.7.1 extended-item commands (`$66 give_ext_item`, `$67 take_ext_item`, `$68 has_ext_item`) also handle the
  consumables `$127-$12E` (stacking to 99, first free slot; inventory full → nothing).

## Locked key items

| rare id | symbol | give | check |
|---|---|---|---|
| 20 | `KEY_DARILLS_TOKEN` | `give_rare 20` | `has_rare 20 -> SW` |
| 21 | `KEY_CONCORD_SIGIL` | `give_rare 21` | `has_rare 21 -> SW` |
| 22 | `KEY_CINDER_SIGIL` | `give_rare 22` | `has_rare 22 -> SW` |
| 23 | `KEY_TRIUNE_SIGIL` | `give_rare 23` | `has_rare 23 -> SW` |
| 24 | `KEY_BROKEN_SEAL` | `give_rare 24` | `has_rare 24 -> SW` |

Example (future story event; derived Triune prerequisite, sigils kept):

```
has_rare 21 -> TMP_A
has_rare 22 -> TMP_B
if_switch TMP_A=0 -> NotYet
if_switch TMP_B=0 -> NotYet
give_rare 23
```

## Evidence

Emulator R2a: GIVE / HAS / TAKE for all 52 logical ids (20 vanilla + 32 FF6X) · R2b no other event bit changes ·
R2c ids ≥ 52 ignored · R2d vanilla id 3 = bit `$1D3` · R7b production ignores undefined ids 25-51 · QA hub menus R3
(grant / remove / toggle / check). Selftest: opcodes only in v0.9 targets (frozen v0.8 keeps the vanilla entries).
