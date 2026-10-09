# Audit D — Item architecture: Options 1 / 2 / 3 (DECISION REQUIRED)

Status: **BLOCKER for final rewards. No item implementation has been done.**
`ITEM_EXPANSION` (FA:0000–FA:FFFF) is marked `blocked` in `allocations.json`;
the builder refuses writes there until you approve an option.

Machine-readable: `item_usage_audit.json` (per item ID: shop / chest /
steal / drop / metamorph / colosseum prize / starting equipment / event
give-take counts). Generator: `tools/item_audit.py`.

## Key Rev 1 facts
- Item IDs are 1 byte; `$FF` = Empty. Names D2:B300 (256 × 13), data D8:5000
  (256 × 30), descriptions ED:6400 (ptrs ED:7AA0), inventory RAM `$1869–$1968`
  (IDs) + `$1969–$1A68` (qty) — inside the SRAM save block.
- **Every vanilla ID `$00–$FE` is referenced by at least one table or event.**
  There is **no free/unused item slot** in Rev 1. 64 IDs have only 1–2
  references, but they include iconic gear (Illumina, Ragnarok, Atma Weapon,
  Genji set, Cat Hood, Marvel Shoes, Moogle Charm, Rename Card…).
- Colosseum (DF:B600) has a row for **every** ID (wager index).
- Rare/key items are a **separate namespace**: 20 entries, stored as event bits
  `$1EBA–$1EBC` (24 bits → up to 4 spare bits, still to be verified), names CE:FBA0, descs CE:FCB0.
- Hard-coded ID logic exists (Edgar Tools `$A3–$AA`, Throw/skean classes,
  special weapon effects in item data), so IDs are not interchangeable.

Demand: 39 equipment concepts (13 weapons, 13 armor/head/shield, 13 relics).

## Option 1 — Reassign vanilla IDs
Replace 39 vanilla items with new ones; re-place the old items' shops/chests/drops.
- Code size: ~0 ASM; data only (names, data, descriptions, placements).
- SRAM: none. Save compatibility: old saves holding a reassigned ID silently
  become the new item.
- Risk: **high design cost** — with zero unused IDs, 39 vanilla items must be
  deleted or merged, which conflicts with "preserve vanilla". Must avoid IDs
  with hard-coded behavior.
- Test burden: low–medium.

## Option 2 — Extended / virtual item engine (16-bit or second namespace)
Everything that stores or interprets an item byte must change:
inventory RAM + SRAM layout, item/equip/relic menus, sorting, shops, chests,
battle Item/Throw/Tools menus, drops/steals, Colosseum, event `$80/$81`,
Metamorph, starting equipment, equipment checks, names/descriptions,
optimum-equip, character equipment slots (6 bytes × 16 chars).
- Code size: estimated **6–12 KB** new/changed 65816 across C0, C1/C2, C3, EE.
- SRAM: +256–512 bytes per slot if inventory widens → the 0xA00 save block
  layout changes → **old saves incompatible** unless a converter is written.
- Risk: **very high** (hundreds of byte-ID sites; battle and menu code).
- Test burden: very high (full regression of menus/battle/shops/equip).

## Option 3 — Hybrid (recommended for evaluation)
- **True equipment only for signature rewards** (e.g. one per arc ≈ 8–13),
  via Option 1-style reassignment of a *small*, carefully chosen set, or via a
  minimal second equipment bank later if approved.
- Secondary concepts as **rare/key items** (≤4 spare bits now, to verify; more needs the
  rare-item tables relocated — small, self-contained change), **permanent
  event flags**, **in-place upgrades** of an existing item (event swaps ID A→B
  using the existing give/take commands), or **quest-state bonuses**.
- Code size: small (0–2 KB). SRAM: none (flags already in save).
- Risk: low–medium. Keeps nearly all vanilla items.
- Creative impact: concepts stay locked, but some are *delivered* as key
  items/upgrades instead of new equipment IDs — **this needs your explicit
  approval because it changes how locked rewards are implemented.**

## Comparison
| | Opt 1 | Opt 2 | Opt 3 |
|---|---|---|---|
| New ASM | none | 6–12 KB | 0–2 KB |
| SRAM change | no | yes | no |
| Old saves | work (items remapped) | break w/o converter | work |
| Vanilla items lost | 39 | 0 | ≈ 8–13 (or 0 with upgrades) |
| Risk / QA | low / medium | very high / very high | low-medium / medium |

**I have not chosen.** Please choose 1, 2 or 3 (or ask for a detailed Option 3
mapping of all 39 concepts) before any reward is coded.
