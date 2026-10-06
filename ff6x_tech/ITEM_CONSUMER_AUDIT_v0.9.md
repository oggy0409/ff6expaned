# ITEM CONSUMER AUDIT — TECH v0.9

Every Rev 1 consumer of an item id / item record that the extended ids `$100-$13F` can reach, after TECH v0.9. Base: `ITEM_CONSUMER_AUDIT_v0.7.1.md` (the complete Rev 1 consumer list, `audits/item_consumer_audit_v071.json`) — every consumer listed there is still handled by the same hook / retarget. v0.9 adds the consumers that only matter once an extended item can be **used** (field menu, battle Item command), **bought / sold**, and the Rare Items menu.

## Summary

| group | count |
|---|---|
| relocated-table long operands (ItemProp / ItemName / weapon / Jump animation) | 118 |
| v0.7.1 / v0.8 hook sites (unchanged) | 152 |
| v0.7.1 hook sites with a v0.9 replacement routine (Sell) | 2 |
| v0.9 hook sites (new) | 57 |

Hook ids `I2xx` event / C0, `I3xx-I4xx` menus (C3), `I5xx` battle (C2 / C1), `V9xx` TECH v0.9. Every site's Rev 1 bytes are re-asserted by the builder before patching; every routine is assembled from `asm/item_v09`.

## v0.9 overrides of v0.7.1 hooks

| id | new routine | reason |
|---|---|---|
| I420_SELLDESC | `jsr XC3_SellLdaX` | TECH v0.9: sell description: a sellable extended consumable shows its own description; any other extended slot reads as $FF (XSHOPCURHI = current item high bit) |
| I421_SELLITEM | `jsr XC3_SellLdaY` | TECH v0.9: Sell item id: a sellable extended consumable can be sold (XSHOPCURHI = 1), any other extended slot reads as $FF (cannot be selected) |

## v0.9 hook sites

| id | site | Rev 1 bytes | replacement | consumer | reason |
|---|---|---|---|---|---|
| V901_EVCMD_69 | C0:992C | `1A B9` | `.word XC0_Ev69 & $FFFF` | EventCmdTbl entry $69 (vanilla unused: RTS lock-up; no Rev 1 script uses it) | GIVE_RARE id (2 bytes) |
| V902_EVCMD_6D | C0:9934 | `1A B9` | `.word XC0_Ev6D & $FFFF` | EventCmdTbl entry $6D (vanilla unused) | TAKE_RARE id (2 bytes) |
| V903_EVCMD_6E | C0:9936 | `1A B9` | `.word XC0_Ev6E & $FFFF` | EventCmdTbl entry $6E (vanilla unused) | HAS_RARE id, switch16 (4 bytes) |
| V910_INITTARGET_CMD | C2:26D6 | `64 BA A2 40` | `jsr XC2_CmdCtx` | InitTarget C2:26D3 (A = command) | records the command (XCURCMD) for the extended-consumable property lookup |
| V911_ITEMTARGET_PROP | C2:271D | `20 63 2B` | `jsr XC2_PropCtx` | InitItemTarget C2:271A GetItemPropPtr | Item command + extended consumable id -> XItemProp record of $100|id (targeting, status) |
| V912_ITEMEFFECT_PROP | C2:2A60 | `20 63 2B` | `jsr XC2_PropCtx` | CalcItemEffect C2:2A37 GetItemPropPtr (battle Item command and field menu use via CalcMagicEffect) | extended consumable -> its own power / element / flags / status record |
| V913_ITEMTARGET_SPELL | C2:273C | `C9 E6 20 1A 27` | `jsr XC2_ItemTgt` | Init target, Item command C2:273C | an extended consumable never casts a spell (carry set like the vanilla items $E6-$FF) |
| V914_ITEMCMD_NAMEFLAG | C2:189F | `A9 01 8D 12 34` | `jsl XJ_ItemCmd` | Item / Throw command C2:189E | XATKX := extended name + animation flags for a character's Item command with an extended consumable |
| V915_ITEMCMD_CONSUME | C2:18B0 | `A9 FF 9D F4 32` | `jsl XJ_Consume` | Item command: held item used up | clears the held-extended flag (XHELD) with the held item |
| V916_FIXATTACK_HOLD | C2:4DB0 | `99 F4 32` | `jsr XC2_Hold` | FixPlayerAttack C2:4DAF (Item / Throw queued) | XHELD[character] := the held item is an extended consumable |
| V917_RETURN_HELD | C2:62D8 | `20 DC 54` | `jsr XC2_LoadHeld` | return of a held / obtained item C2:62C7 | a held extended consumable goes back to the list with its own properties + marker |
| V918_STEAL_OBTAIN | C2:39EC | `9D F4 32` | `jsr XC2_StaHeldVan` | Steal: obtained item C2:39EC | a vanilla item replaces the held item: XHELD cleared |
| V919_METAMORPH_OBTAIN | C2:3A7C | `9D F4 32` | `jsr XC2_StaHeldVan` | Metamorph: obtained item C2:3A7C | a vanilla item replaces the held item: XHELD cleared |
| V920_CMD_DISPATCH | C2:1559 | `85 B5 0A AA` | `jsl XJ_Dispatch` | battle command dispatch C2:1554 | clears XATKX before every command |
| V930_ITEMROW | C1:4CA5 | `B9 86 26 8D 5A 57 8D 61 57` | `jsl XJ_ListRow` | DrawItemListText C1:4C6B | row name: XBTLNAME := extended-consumable marker of the entry (XItemName + $D00 for the name) |
| V931_ITEM_DECREMENT | C1:7164 | `7B AA B9 B0 2B DD 86 26 F0 0B E8 E8 E8 E8 E8 E0 00 05 D0 F1 60` | `jsl XJ_DecFind ; bcs $C17179 ; rts` | decrement of the used / thrown list item C1:7167 | matches id AND marker (Item command + extended consumable) instead of the id only |
| V932_ITEM_ADD | C1:4458 | `A2 00 00 DD 86 26 F0 21 E8 E8 E8 E8 E8 E0 00 05 D0 F1` | `jsl XJ_AddFind ; bcs $C14481 ; bra $C1446A` | obtained / returned item added to the list C1:4445 | matches id AND marker |
| V933_FIND_VANILLA | C1:8CBC | `DD 86 26 F0 0C E8 E8 E8 E8 E8 E0 00 05 D0 F1` | `jsl XJ_FindVan ; rts` | FindInventoryItem C1:8CB7 (hand item back to the list) | vanilla entries only: a hand katana never merges into an extended consumable |
| V934_ATTACKNAME_ITEM | C1:605B | `AF 16 42 00 AA` | `jsl XJ_AtkNameX` | item attack name C1:6050 | extended consumable (XATKX bit0) -> XItemName + $D00 |
| V935_ITEM_ANIM | C1:BC58 | `C9 E0 90 05 38 E9 E0 80 02 A9 E0 C2 20 0A AA BF 00 00 D1 AA` | `jsl XJ_ItemAnim` | item animation C1:BC4E | extended consumable (XATKX bit1) -> XItemAnimX; vanilla ItemAnimPtrs rule otherwise |
| V940_ITEMCOLOR_ID | C3:8056 | `B9 69 18` | `jsr XC3_LdaInvY` | GetItemNameColor C3:8045 | 9-bit id (A low, B high bit) |
| V941_ITEMCOLOR_PROP | C3:806D | `20 21 83` | `jsr XC3_PropPtrB` | GetItemNameColor | usable colour from the extended record |
| V942_CANUSE | C3:8B3D | `B9 14 00` | `jsr XC3_CanUse` | CheckCanUseItem C3:8B3D | extended consumable: validity from its record (vanilla rules) |
| V943_USE_CTX | C3:8B25 | `20 2B 8C` | `jsr XC3_GetIdCtx` | _c38b1a (before CalcMagicEffect) | XCURCMD := $FE for an extended slot (C2 reads the extended record) |
| V944_RESTORE_ID | C3:8C34 | `20 2B 8C` | `jsr XC3_GetIdB` | _c38c33 HP / MP restore | 9-bit id |
| V945_RESTORE_PROP | C3:8C37 | `20 21 83` | `jsr XC3_PropPtrB` | _c38c33 HP / MP restore | extended record |
| V946_USE_DEC | C3:8B17 | `4C 97 9D` | `jmp XC3_DecSel` | _c38b11 (item used) | one unit of the selected 9-bit item is removed (slot cleared at 0) |
| V950_SHOP_TABLE_LIST | C3:B9AF | `BF C0 7A C4` | `lda f:XShopProp,x` | shop item list C3:B9AF | ShopProp relocated (XShopProp: 128 vanilla shops byte-exact + extended shops $80+) |
| V951_SHOP_TABLE_PRICE | C3:BA32 | `BF C0 7A C4` | `lda f:XShopProp,x` | AdjustShopPrice C3:BA2C | ShopProp relocated |
| V952_SHOP_TABLE_TYPE | C3:BFF3 | `BF C0 7A C4` | `lda f:XShopProp,x` | shop type C3:BFD3 | ShopProp relocated |
| V953_SHOP_ROW_NAME | C3:B9BD | `20 68 C0` | `jsr XC3_ShopListName` | shop list row | 9-bit name |
| V954_SHOP_ROW_PRICE | C3:B9C9 | `20 21 83` | `jsr XC3_ShopListPtr` | shop list row price | 9-bit record |
| V955_SHOP_OWNED | C3:BC5D | `7B AA DA A4 00` | `jsl XJ_ShopOwned ; rts` | _c3bc57 owned counts | owned quantity of exactly the shop item (vanilla / extended) |
| V956_SHOP_CUR | C3:BFC6 | `BF 89 9D 7E` | `jmp XC3_ShopLdaX` | _c3bfc2 current buy item | XSHOPCURHI := entry high bit |
| V957_BUY_DESC | C3:B4F5 | `4C 38 57` | `jmp XC3_ItemDescCur` | buy description | extended description |
| V958_SELL_DESC2 | C3:B502 | `4C 38 57` | `jmp XC3_ItemDescCur` | sell description | extended description |
| V959_BUY | C3:B5B7 | `20 C2 BF` | `jsr XC3_ShopBuy` | _c3b5b7 buy | extended entry: extended give |
| V960_BUY_NAME | C3:BAC6 | `20 68 C0` | `jsr XC3_LoadItemNameCur` | buy quantity screen name | 9-bit name |
| V961_SELL_NAME | C3:BADF | `20 68 C0` | `jsr XC3_LoadItemNameCur` | sell quantity screen name | 9-bit name |
| V962_BUY_TYPE | C3:B7E9 | `20 21 83` | `jsr XC3_PropPtrCur` | _c3b7e6 (item type) | 9-bit record |
| V963_SHOP_STAT | C3:BAF8 | `20 21 83` | `jsr XC3_PropPtrCur` | DrawShopItemStat | 9-bit record |
| V964_SELL_PRICE | C3:BB68 | `20 21 83` | `jsr XC3_PropPtrCur` | sell price | 9-bit record (price / 2) |
| V965_CANEQ_ID | C3:BCE1 | `BF 89 9D 7E` | `jsr XC3_ShopLdaX` | shop: who can equip (current entry) | XSHOPCURHI := entry high bit |
| V966_CANEQ_PROP | C3:BCE5 | `20 21 83` | `jsr XC3_PropPtrCur` | shop: who can equip | 9-bit record |
| V967_CANEQ2_ID | C3:C1B0 | `BF 89 9D 7E` | `jsr XC3_ShopLdaX` | shop: who can equip (party sprites) | XSHOPCURHI := entry high bit |
| V968_CANEQ2_PROP | C3:C1B4 | `20 21 83` | `jsr XC3_PropPtrCur` | shop: who can equip (party sprites) | 9-bit record |
| V969_SHOP_STATS_X | C3:BD13 | `20 21 83` | `jsr XC3_ShopPtrX` | _c3bcfd per-entry stats | 9-bit record |
| V970_SELLALL_CLR | C3:B739 | `99 69 18` | `jsr XC3_StaInvYClr` | sell all units of a slot | the emptied slot's high bit is cleared |
| V980_RARE_DESCPTR | C3:8339 | `A2 60 FB` | `ldx #XRareDescPtr & $FFFF` | InitRareItemDesc C3:8339 | 52 rare descriptions (XRareDescPtr, absolute pointers in bank FA) |
| V981_RARE_DESCBASE | C3:833E | `A2 B0 FC` | `ldx #$0000` | InitRareItemDesc | absolute pointers |
| V982_RARE_DESCBANK | C3:8343 | `A9 CE` | `lda #^XRareDescPtr` | InitRareItemDesc | bank FA |
| V983_RARE_COUNT | C3:834C | `20 6B 83` | `jsr XC3_RareCount` | InitRareItemDesc (count) | number of owned rare items over all pages |
| V984_RARE_NAMEPTR | C3:843B | `A0 A0 FB` | `ldy #XRareName & $FFFF` | GetRareItemNamePtr C3:8436 | 52 rare names (XRareName) |
| V985_RARE_NAMEBANK | C3:8440 | `A9 CE` | `lda #^XRareName` | GetRareItemNamePtr | bank FA |
| V986_RARE_LIST | C3:838E | `20 94 83` | `jsr XC3_RareListS` | InitRareItemList C3:838B | list of the current page (vanilla ids 0-19 + FF6X ids 20-51) |
| V987_RARE_PAGE | C3:2748 | `20 4A 7D` | `jsr XC3_RarePage` | menu state ITEM_RARE C3:2741 | page turning (Down / Up at the edge, R / L) |
| V988_RARE_OPEN | C3:26A0 | `20 8B 83` | `jsr XC3_RareInit` | SelectItemOption_02 C3:268E | page 0 |

## Consumers reviewed and left unchanged (v0.9)

| consumer | why no change |
|---|---|
| C2 `CalcItemEffect` record reads (power, element, status, flags) | read through the relocated `XItemProp` with the 9-bit offset returned by `XB_PropCtx` |
| C3 `UseItem` tent / sleeping bag / warp checks (C3:84C4) | compare the low byte with `$F6/$F7/$FD`; consumable low bytes are `$27-$2E` |
| C3 rename-card check (C3:8AA5) | compares the low byte with `$E7` |
| C1 battle Item menu usability / colour (`UsageFlags` bit 7) | marker is bit 0; every C1 reader masks the bits it uses |
| C1 Throw / Tools lists | built from items with usage bit `$20` (throwable) / tools; consumables have neither |
| C1 hand exchange (`set_item_one`) | requires `UsageFlags & $18` (weapon / shield); consumables refused |
| C2 Mimic of an Item command | re-runs command `$01` with the same id → same extended context, no decrement (vanilla) |
| monster AI `use_item` | Rev 1 AI only names `$E8+` items (13 scripts); `throw_item` uses command `$08` |
| C2 battle-end drops / steals into the inventory | vanilla ids; vanilla give paths skip extended slots (v0.7.1 masks) |
| Colosseum wager list / prize | extended items hidden (`XC3_ExclLo`), wager removal masked (v0.7.1 I521) |
| Equip / Relic lists, Optimum | filter by item type; consumables are type 6 |
