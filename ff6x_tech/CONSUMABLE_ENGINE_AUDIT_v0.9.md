# CONSUMABLE ENGINE AUDIT — TECH v0.9

How an extended consumable (`$127-$12E`, 9-bit id = vanilla low byte + high bit outside the vanilla byte) reaches every
place the vanilla item code reads an item id, and what the v0.9 engine (`asm/item_v09`, `patches/item_v09_hooks.py`)
does there. Effects are **data**: the consumable's 30-byte ItemProp record (`XItemProp`, FA:0000) is run by the
vanilla item code (C2 `CalcItemEffect` in battle and, through `CalcMagicEffect`, in the field menu; C3 `_c38c33` for
the field HP/MP restore). No item-specific ASM exists.

## 1. Identification without ambiguity

* The low bytes `$27-$2E` belong to the vanilla katanas Blossom … Tempest. They are **not usable with the Item command**
  (ItemProp byte 0 bit 5 clear; the builder fails if that ever changes — validator `cons9-battle-usable-alias`) and
  the Throw command is a different command (`$08`). Monster AI never uses them with `use_item` (the 13 `use_item`
  scripts in the Rev 1 AI only name `$E8+` items; katanas are only *thrown*).
* Hence in battle **(command = Item, low byte, `XExtFlags` consumable bit)** identifies an extended consumable.
* `XExtFlags` (FA:35C0, one byte per extended low byte): bit0 defined, bit1 spear (v0.7.1), **bit2 consumable, bit3
  sellable** (v0.9).

## 2. Field Item menu (C3)

| Site | Vanilla | v0.9 |
|---|---|---|
| C3:8056 / C3:806D (`GetItemNameColor`) | `LDA $1869,Y` / `JSR GetItemPropPtr` | `XC3_LdaInvY` / `XC3_PropPtrB`: colour from the 9-bit record (battle-only consumables grey) |
| C3:849D / C3:84A8 (`UseItem`, v0.7.1 I304 / I305) | id + record | unchanged hooks: type 6 + menu bit → character selection; battle-only → refused |
| C3:8B3D (`CheckCanUseItem`) | per-id list of vanilla items | `XC3_CanUse`: extended slot → validity **from its record** with the vanilla rules: revive only a fallen character, cure if the character has a status the item removes (status 1 / status 4), HP/MP restore only below max and not Wound/Petrify/Zombie; returns to the caller of CheckCanUseItem |
| C3:8B25 (`_c38b1a`, before `JSL CalcMagicEffect`) | `JSR GetInventoryItemID` | `XC3_GetIdCtx`: `XCURCMD := $FE` for an extended slot |
| C2:2A60 (`CalcItemEffect` → `GetItemPropPtr`) | `id * 30` | `XB_PropCtx`: `XCURCMD = $FE` (consumed) or (Item command + consumable) → `(0x100 + id) * 30`; all flags preserved |
| C3:8C34 / C3:8C37 (`_c38c33` HP/MP restore) | id + record | `XC3_GetIdB` / `XC3_PropPtrB` |
| C3:8B17 (`_c38b11` tail) | `JMP DecItemQty` (search by id) | `XC3_DecSel`: one unit of the **selected slot's** 9-bit item (`XTakeExt`; slot emptied + high bit cleared at 0) |

Field menu targeting is always one character (vanilla); Gaia Tonic (party in battle) heals one member in the field.

## 3. Battle (C2 / C1)

| Site | Vanilla | v0.9 |
|---|---|---|
| C2:54B0 (inventory init, v0.7.1 I516) | every slot copied with `CopyItemProp(low byte)` | `XC2_ExtSlotsEmpty`: extended **equipment** slots copied as empty (signature equipment never visible in battle — unchanged rule); extended **consumable** slots → real entry from `XB_ConsEntry`: id, usage (`$80` unless battle-usable) **+ marker `$01`**, targeting from the record, quantity, equip flags `$0F` |
| C2:26D6 (`InitTarget`, A = command) | `STZ $BA / LDX #$40` | `XC2_CmdCtx`: `XCURCMD := command` |
| C2:271D (`InitItemTarget`) | `GetItemPropPtr` | `XB_PropCtx` (targeting / status of the record) |
| C2:273C (Item init target) | `CMP #$E6` (C=1: item does not cast a spell) | `XB_ItemTgtC`: C=1 for an extended consumable (its low byte is < `$E6`) |
| C2:189F (Item / Throw command) | attack-name type 1 | `XB_ItemCmd`: `XATKX := 3` (extended name + animation) for a character's Item command with a consumable |
| C2:18B0 (held item used up) | `LDA #$FF / STA $32F4,X` | `XB_Consume`: + `XHELD[char] := 0`, **P preserved** (see §6) |
| C2:4DB0 (`FixPlayerAttack`) | held item id | `XB_Hold`: `XHELD[char] := (Item command and consumable)` |
| C2:39EC / C2:3A7C (Steal / Metamorph obtained item) | `STA $32F4,X` | `XB_StaHeldVan`: + `XHELD[char] := 0` (a vanilla item replaces the held one) |
| C2:62D8 (held / obtained item back to the list) | `LoadItemProp(id)` | `XB_LoadHeld`: held consumable → extended properties + marker |
| C2:1559 (command dispatch) | `STA $B5 / ASL / TAX` | `XB_Dispatch`: `XATKX := 0` before every command |
| C1:4CA5 (`DrawItemListText`) | id at +5 / +12 | `XC1_ListRow`: `XBTLNAME := marker` (name from XItemName + $D00), +12 := `$FF` for a consumable (the EN template draws that byte as a text code) |
| C1:7164 (decrement on command) | search by id | `XC1_DecFind`: id **and** marker = (command is Item and consumable) |
| C1:4458 (obtained / returned item added) | search by id | `XC1_AddFind`: id and marker |
| C1:8CBC (`FindInventoryItem`, hand item back) | search by id | `XC1_FindVan`: vanilla entries (marker 0) only |
| C1:605B (item attack name) | `ItemName + id*13` | `XC1_AtkNameX`: `XATKX` bit0 → `XItemName + (0x100 + id)*13` (consumed) |
| C1:BC58 (item animation) | `ItemAnimPtrs[id-$E0]` | `XC1_ItemAnim`: `XATKX` bit1 → `XItemAnimX[low byte]` (consumed); vanilla rule otherwise |
| C2:4981 (battle end, v0.7.1 I520) | copy back all slots | `XBattleEndInv`: extended-equipment slots keep their contents; every other slot copied back with its high bit = the entry's marker; an item placed at an extended-equipment position is merged (consumable: `XGiveExt`; vanilla: `PutVanilla`) |

Every C1 reader of `UsageFlags` masks the bits it uses; bit0 is unused by the vanilla code (marker free).

## 4. Inventory primitives, Arrange, descriptions, exclusions

Unchanged v0.7.1 / v0.8 engine: `XGiveExt` / `XTakeExt` / `XHasExt` (stack to 99, first free slot, inventory full →
nothing), vanilla give / take / find hooks mask extended slots (`XC0_LdaInvXMask`, `XC3_CmpInvYMask`), Arrange
(`XArrange`, icon `$FF` is in the Arrange icon table — asserted by the builder), descriptions (`XC3_ItemDescB` /
`XDescPtr`). v0.9 makes the shop / Colosseum exclusion slot-aware (`XC3_ExclLo`): Colosseum hides every extended
item, a shop hides extended items except **sellable consumables** (Sell). Equip / Relic lists filter by item type
(consumables are type 6) — no change needed (emulator X2).

## 5. Context bytes (transient, saved RAM `$1E36-$1E3D`, cleared at New Game / load)

`XCURCMD $1E36`, `XATKX $1E37`, `XHELD $1E38-$1E3B`, `XSHOPCURHI $1E3C`, `XRAREPAGE $1E3D` (`data/allocations.json`
`saved_ram_allocations`).

## 6. Defect found and fixed during internal testing (before packaging)

**Battle Item command took the spell path for every consumable** (no effect, no animation). Root cause: the first
version of the C2:18B0 hook (`XB_Consume`) ran `CPX #$08`, destroying the carry that `InitTarget` returns and that the
vanilla code tests two instructions later (`BCC @18e3`: item casts a spell). Fix: `XB_Consume` / `XB_StaHeldVan`
preserve P. Emulator B2-B9 verify every consumable's effect afterwards.

Also fixed during testing: the battle list drew `DIRK` after a consumable's quantity (the EN template's byte +12 is
drawn as a text code; now `$FF` for consumables), and the Rare Items description kept the previous page's text after
an L / R page flip (description task now reset).

## 7. Static audit of the B accumulator (`devtools/b_leak_audit_v09.py`)

The new producers (`XC3_GetIdB` and the `XC3_LdaInvY` use at C3:8056) and every v0.7.1 / v0.8 producer were walked
on the v0.9 QA ROM: **1 finding, the known unreachable I304 Megalixir compare (v0.8, unchanged)**. All new C3 shop /
rare routines leave B = 0 (`XC3_ShopLdaX`, `XC3_PropPtrCur`, `XC3_LoadItemNameCur`, …).
