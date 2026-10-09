# Audit C — Monster expansion dependencies (Rev 1)

Demand (Creative Lock v1.2): **35 normal mobs + 14 bosses** (+ extra entries
for multi-phase bosses). Vanilla: **384** monsters (`$000–$17F`); `$1FF` = null.

## Every structure indexed by monster ID
Reference counts = long-address code references found in the Rev 1-verified
disassembly (each must be repointed or bounds-checked when IDs ≥ `$180` exist).

| Table | SNES | Entries × size | Code refs | Note |
|---|---|---|---:|---|
| Stats (`MonsterProp`) | CF:0000 | 384 × 32 | 27 | includes Metamorph set, special attack, etc. |
| Steal/drop items | CF:3000 | 384 × 4 | 4 | 1-byte item IDs |
| Sprite overlap Y | CF:3600 | 384 × 1 | 1 | |
| Special-attack anim | CF:37C0 | 384 × 1 | 9 | |
| Control/Muddle attacks | CF:3D00 | 384 × 4 | 5 | |
| Sketch attacks | CF:4300 | 384 × 2 | 3 | |
| **Rage attacks** | CF:4600 | **256** × 2 | 3 | Rage ID space is 8-bit; initial rages bitfield C4:7AA0 (256 bits) |
| AI script pointers / scripts | CF:8400 / CF:8700 | 384 × 2 / var. | 8 | 16-bit pointers into one bank (CF) — new AI must go elsewhere |
| Names | CF:C050 | 384 × 10 | 7 | |
| Special-attack names | CF:D0D0 | 384 × 10 | 2 | |
| Graphics descriptor | D2:7000 | 384 × 5 | 15 | |
| Palettes | D2:7820 | 768 × 16 | 9 | indexed via descriptor, not monster ID |
| **Vertical alignment** | EC:E800 | **256** × 1 | 5 | indexed with an 8-bit load → IDs ≥ $100 alias `ID & $FF` (vanilla quirk; affects any new ID) |
| Formations (`BattleMonsters`) | CF:6200 | 576 × 15 | 9 | byte 14 holds the **9th bit** of each slot's monster ID → formations already address `$000–$1FF` |
| Aux. formation data | CF:5900 | 576 × 4 | – | |
| Magic points per battle | DF:B400 | 512 × 1 | – | indexed by formation |
| Colosseum | DF:B600 | 256 × 4 | – | references formations/monsters |
| Graphics stencils | D2:A824/AC24 | 128 / 48 maps | – | shared by descriptors |

Hard-coded constants worth inspecting in the monster module (candidates, not
yet classified): `#$0180` (btlgfx/sprite.asm, monster_gfx.asm, menu.asm),
`#$01FF` null checks (gfx_cmd.asm, menu.asm), and boss-specific ID compares in
battle code (e.g. final-battle formation `$01D7` check in battle/init.asm).

## Conclusion
- IDs `$180–$1FE` are addressable by formations, but **every 384-entry table
  above ends exactly where the next table starts** → appending in place is impossible.
- Expansion therefore = relocate ~11 tables to `MONSTER_EXPANSION` (F8–F9) and
  repoint ≈ 90 audited code references, plus decide policy for the two
  256-entry tables (Rage, Vertical alignment): new monsters simply are not
  Rage-able / use aliasing-safe alignment, or those tables are widened too.
- AI scripts: CF bank is full; new AI needs a bank-switch in the AI loader or
  F8/F9 relocation of the pointer table + scripts.

## Recommended order (after Phase 3)
1. Phase 3 slice: use **one existing vanilla monster** in the test battle
   (allowed: placeholder, no data overwrite) — no monster expansion yet.
2. Monster module proof: relocate tables, add **one** monster at index `$180`,
   formation test, Control/Sketch/steal/name/graphics verified in-game.
3. Then batch-add the 35 + bosses.

Tool impact: FF3usME/FF6Tools monster editors will not see relocated tables.
Monster data must be authored as builder source (JSON) from then on.
