# EXTENDED SHOP AUDIT — TECH v0.9

## 1. Shop table relocation

The vanilla shop table `ShopProp` (C4:7AC0, 128 shops × 9 bytes: type / price modifier + 8 item low bytes) has
exactly **three readers** in Rev 1 (`BF C0 7A C4` = `LDA f:ShopProp,X`): C3:B9AF (item list), C3:BA32 (price
modifier), C3:BFF3 (shop type). All three are re-pointed to **`XShopProp` (FA:5400, 144 × 9 B)**: shops `$00-$7F` are
a byte copy of the vanilla table (selftest / emulator T3), shops `$80-$8F` are extended. Event command `$9B shop` takes
any shop id (no range check), so an extended shop is opened with `9B 80`.

`XShopPropHi` (FA:5940, same layout) holds one byte per entry: 1 = the entry is an extended item (`$100 | low byte`).
Extended shops may list vanilla items and sellable extended consumables only (validator `shop9-equipment-sold`: no
signature equipment, no unsold consumable).

| shop | symbol | items |
|---|---|---|
| $80 | `EXT_SHOP_REBUILT_GENERAL` | Gaia Tonic $127, Iron Ration $12B, Null Dust $12A, Potion, Tincture, Fenix Down, Remedy, Tent |
| $81 | `EXT_SHOP_REBUILT_LATE` | Remedy+ $12C, Gaia Tonic, Iron Ration, Null Dust, Potion, Fenix Down, Remedy, Warp Stone |

No list is truncated: each shop has its own 8 entries; the 128 vanilla shops are unchanged.

## 2. Every shop consumer of an item id (C3 shop module)

| Site | Purpose | v0.9 |
|---|---|---|
| C3:B9AF / BA32 / BFF3 | ShopProp readers | → XShopProp |
| C3:B9BD | list row name | `XC3_ShopListName` (9-bit name; XSHOPCURHI from the entry) |
| C3:B9C9 | list row price | `XC3_ShopListPtr` (price from the 9-bit record) |
| C3:BC5D | owned counts (8 entries) | `JSL XShopOwned`: owned quantity of exactly that item (vanilla entry: vanilla slot only; extended entry: extended slot only) |
| C3:BFC6 (`_c3bfc2`) | current buy item | `XC3_ShopLdaX`: XSHOPCURHI := entry high bit |
| C3:BCE1 / BCE5, C1B0 / C1B4 | who can equip (cursor / party sprites) | entry high bit + 9-bit record (consumables: nobody) |
| C3:BD13 | per-entry stats | `XC3_ShopPtrX` |
| C3:B7E9, BAF8, BB68 | type / stats / sell price | `XC3_PropPtrCur` (XSHOPCURHI) |
| C3:BAC6, BADF | quantity screen name | `XC3_LoadItemNameCur` |
| C3:B4F5, B502 | buy / sell description | `XC3_ItemDescCur` |
| C3:B5B7 | buy | `XC3_ShopBuy`: extended entry → `XGiveExt` × quantity (stack / first free slot), then the vanilla tail (price × quantity, GP); no stack + inventory full → nothing bought, no GP taken |
| C3:BF97 (v0.7.1 I425) | "Equipped" count | current extended item → never equipped |
| C3:BFCF (I421 override) / C3:B4FF (I420 override) | Sell item id | `XC3_SellLdaY/X`: sellable consumable → id + XSHOPCURHI = 1; other extended slot → `$FF` (cannot be selected) |
| C3:B739 | sell all | `XC3_StaInvYClr`: emptied slot's high bit cleared |
| item list in a shop (I300 / I301) | Sell list | `XC3_ExclLo`: sellable consumables listed, any other extended item blank |

## 3. Emulator evidence (`tools/emu_cons_v09.py`, `tools/emu_stress_v09.py`)

S1 list / owned / prices of shop $80 · S2 buy (stack, GP) · S3 Equipped = 0 · S4 inventory full → refused, no GP ·
S5 shop $81 · S6 vanilla shop $00 selling katanas with the consumables' low bytes: owned 0 (no alias) · L1 Sell: exactly
the 4 sellable consumables selectable · L2 sell one (price / 2) · L3 sell all (slot + bit cleared) · stress F1 with
everything owned · stress S1 vanilla shop $48 buy / sell.

## 4. Not changed

Vanilla shop contents and prices, the price modifiers, the Colosseum (no extended wager / prize), the smith model of
v0.8 (event-driven, not a shop).
