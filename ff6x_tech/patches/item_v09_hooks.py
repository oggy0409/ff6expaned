"""TECH v0.9 hook table (hand-written; same format as patches/item_v071_hooks.py). Every vanilla byte the v0.9 engine
changes in addition to the v0.7.1 / v0.8 hooks: id, SNES site, exact Rev 1 bytes (re-asserted against the clean ROM by
the builder), the replacement as assembler text (assembled at the site, NOP-padded to the original length where
pad_nop is set), the consumer and the reason.

OVERRIDES replaces the assembler text of two v0.7.1 hooks (same site / same original bytes): the Sell list loaders now
let a SELLABLE extended consumable through (v0.7.1 / v0.8 masked every extended slot).
"""

C2 = ".a8\n.i8"
C1 = ".a8\n.i16"
C1A16 = ".a16\n.i16"


def H(id_, snes, expect, asm, consumer, reason, mode=".a8\n.i16", pad=False):
    h = {"id": id_, "snes": snes, "expect": expect, "asm": asm, "consumer": consumer, "reason": reason, "mode": mode}
    if pad:
        h["pad_nop"] = True
    return h


OVERRIDES = {
    "I420_SELLDESC": {"asm": "jsr XC3_SellLdaX",
                      "reason": "TECH v0.9: sell description: a sellable extended consumable shows its own description; "
                                "any other extended slot reads as $FF (XSHOPCURHI = current item high bit)"},
    "I421_SELLITEM": {"asm": "jsr XC3_SellLdaY",
                      "reason": "TECH v0.9: Sell item id: a sellable extended consumable can be sold (XSHOPCURHI = 1), "
                                "any other extended slot reads as $FF (cannot be selected)"},
}

HOOKS = [
    # ---- event API: rare items -------------------------------------------------------------------------------
    H("V901_EVCMD_69", "C0992C", "1A B9", ".word XC0_Ev69 & $FFFF",
      "EventCmdTbl entry $69 (vanilla unused: RTS lock-up; no Rev 1 script uses it)", "GIVE_RARE id (2 bytes)"),
    H("V902_EVCMD_6D", "C09934", "1A B9", ".word XC0_Ev6D & $FFFF",
      "EventCmdTbl entry $6D (vanilla unused)", "TAKE_RARE id (2 bytes)"),
    H("V903_EVCMD_6E", "C09936", "1A B9", ".word XC0_Ev6E & $FFFF",
      "EventCmdTbl entry $6E (vanilla unused)", "HAS_RARE id, switch16 (4 bytes)"),
    # ---- battle (C2) -------------------------------------------------------------------------------------------
    H("V910_INITTARGET_CMD", "C226D6", "64 BA A2 40", "jsr XC2_CmdCtx", "InitTarget C2:26D3 (A = command)",
      "records the command (XCURCMD) for the extended-consumable property lookup", C2, pad=True),
    H("V911_ITEMTARGET_PROP", "C2271D", "20 63 2B", "jsr XC2_PropCtx", "InitItemTarget C2:271A GetItemPropPtr",
      "Item command + extended consumable id -> XItemProp record of $100|id (targeting, status)", C2),
    H("V912_ITEMEFFECT_PROP", "C22A60", "20 63 2B", "jsr XC2_PropCtx", "CalcItemEffect C2:2A37 GetItemPropPtr "
      "(battle Item command and field menu use via CalcMagicEffect)",
      "extended consumable -> its own power / element / flags / status record", C2),
    H("V913_ITEMTARGET_SPELL", "C2273C", "C9 E6 20 1A 27", "jsr XC2_ItemTgt", "Init target, Item command C2:273C",
      "an extended consumable never casts a spell (carry set like the vanilla items $E6-$FF)", C2, pad=True),
    H("V914_ITEMCMD_NAMEFLAG", "C2189F", "A9 01 8D 12 34", "jsl XJ_ItemCmd", "Item / Throw command C2:189E",
      "XATKX := extended name + animation flags for a character's Item command with an extended consumable", C2, pad=True),
    H("V915_ITEMCMD_CONSUME", "C218B0", "A9 FF 9D F4 32", "jsl XJ_Consume", "Item command: held item used up",
      "clears the held-extended flag (XHELD) with the held item", C2, pad=True),
    H("V916_FIXATTACK_HOLD", "C24DB0", "99 F4 32", "jsr XC2_Hold", "FixPlayerAttack C2:4DAF (Item / Throw queued)",
      "XHELD[character] := the held item is an extended consumable", C2),
    H("V917_RETURN_HELD", "C262D8", "20 DC 54", "jsr XC2_LoadHeld", "return of a held / obtained item C2:62C7",
      "a held extended consumable goes back to the list with its own properties + marker", C2),
    H("V918_STEAL_OBTAIN", "C239EC", "9D F4 32", "jsr XC2_StaHeldVan", "Steal: obtained item C2:39EC",
      "a vanilla item replaces the held item: XHELD cleared", C2),
    H("V919_METAMORPH_OBTAIN", "C23A7C", "9D F4 32", "jsr XC2_StaHeldVan", "Metamorph: obtained item C2:3A7C",
      "a vanilla item replaces the held item: XHELD cleared", C2),
    H("V920_CMD_DISPATCH", "C21559", "85 B5 0A AA", "jsl XJ_Dispatch", "battle command dispatch C2:1554",
      "clears XATKX before every command", C2, pad=True),
    # ---- battle menu / graphics (C1, JSL to bank FA) ---------------------------------------------------------
    H("V930_ITEMROW", "C14CA5", "B9 86 26 8D 5A 57 8D 61 57", "jsl XJ_ListRow", "DrawItemListText C1:4C6B",
      "row name: XBTLNAME := extended-consumable marker of the entry (XItemName + $D00 for the name)", C1, pad=True),
    H("V931_ITEM_DECREMENT", "C17164",
      "7B AA B9 B0 2B DD 86 26 F0 0B E8 E8 E8 E8 E8 E0 00 05 D0 F1 60",
      "jsl XJ_DecFind\nbcs $C17179\nrts", "decrement of the used / thrown list item C1:7167",
      "matches id AND marker (Item command + extended consumable) instead of the id only", C1, pad=True),
    H("V932_ITEM_ADD", "C14458", "A2 00 00 DD 86 26 F0 21 E8 E8 E8 E8 E8 E0 00 05 D0 F1",
      "jsl XJ_AddFind\nbcs $C14481\nbra $C1446A", "obtained / returned item added to the list C1:4445",
      "matches id AND marker", C1, pad=True),
    H("V933_FIND_VANILLA", "C18CBC", "DD 86 26 F0 0C E8 E8 E8 E8 E8 E0 00 05 D0 F1",
      "jsl XJ_FindVan\nrts", "FindInventoryItem C1:8CB7 (hand item back to the list)",
      "vanilla entries only: a hand katana never merges into an extended consumable", C1, pad=True),
    H("V934_ATTACKNAME_ITEM", "C1605B", "AF 16 42 00 AA", "jsl XJ_AtkNameX", "item attack name C1:6050",
      "extended consumable (XATKX bit0) -> XItemName + $D00", C1A16, pad=True),
    H("V935_ITEM_ANIM", "C1BC58", "C9 E0 90 05 38 E9 E0 80 02 A9 E0 C2 20 0A AA BF 00 00 D1 AA",
      "jsl XJ_ItemAnim", "item animation C1:BC4E",
      "extended consumable (XATKX bit1) -> XItemAnimX; vanilla ItemAnimPtrs rule otherwise", C1, pad=True),
    # ---- field Item menu: use --------------------------------------------------------------------------------
    H("V940_ITEMCOLOR_ID", "C38056", "B9 69 18", "jsr XC3_LdaInvY", "GetItemNameColor C3:8045",
      "9-bit id (A low, B high bit)"),
    H("V941_ITEMCOLOR_PROP", "C3806D", "20 21 83", "jsr XC3_PropPtrB", "GetItemNameColor",
      "usable colour from the extended record"),
    H("V942_CANUSE", "C38B3D", "B9 14 00", "jsr XC3_CanUse", "CheckCanUseItem C3:8B3D",
      "extended consumable: validity from its record (vanilla rules)"),
    H("V943_USE_CTX", "C38B25", "20 2B 8C", "jsr XC3_GetIdCtx", "_c38b1a (before CalcMagicEffect)",
      "XCURCMD := $FE for an extended slot (C2 reads the extended record)"),
    H("V944_RESTORE_ID", "C38C34", "20 2B 8C", "jsr XC3_GetIdB", "_c38c33 HP / MP restore", "9-bit id"),
    H("V945_RESTORE_PROP", "C38C37", "20 21 83", "jsr XC3_PropPtrB", "_c38c33 HP / MP restore", "extended record"),
    H("V946_USE_DEC", "C38B17", "4C 97 9D", "jmp XC3_DecSel", "_c38b11 (item used)",
      "one unit of the selected 9-bit item is removed (slot cleared at 0)"),
    # ---- shops -----------------------------------------------------------------------------------------------
    H("V950_SHOP_TABLE_LIST", "C3B9AF", "BF C0 7A C4", "lda f:XShopProp,x", "shop item list C3:B9AF",
      "ShopProp relocated (XShopProp: 128 vanilla shops byte-exact + extended shops $80+)"),
    H("V951_SHOP_TABLE_PRICE", "C3BA32", "BF C0 7A C4", "lda f:XShopProp,x", "AdjustShopPrice C3:BA2C",
      "ShopProp relocated"),
    H("V952_SHOP_TABLE_TYPE", "C3BFF3", "BF C0 7A C4", "lda f:XShopProp,x", "shop type C3:BFD3", "ShopProp relocated"),
    H("V953_SHOP_ROW_NAME", "C3B9BD", "20 68 C0", "jsr XC3_ShopListName", "shop list row", "9-bit name"),
    H("V954_SHOP_ROW_PRICE", "C3B9C9", "20 21 83", "jsr XC3_ShopListPtr", "shop list row price", "9-bit record"),
    H("V955_SHOP_OWNED", "C3BC5D", "7B AA DA A4 00", "jsl XJ_ShopOwned\nrts", "_c3bc57 owned counts",
      "owned quantity of exactly the shop item (vanilla / extended)"),
    H("V956_SHOP_CUR", "C3BFC6", "BF 89 9D 7E", "jmp XC3_ShopLdaX", "_c3bfc2 current buy item",
      "XSHOPCURHI := entry high bit", pad=True),
    H("V957_BUY_DESC", "C3B4F5", "4C 38 57", "jmp XC3_ItemDescCur", "buy description", "extended description"),
    H("V958_SELL_DESC2", "C3B502", "4C 38 57", "jmp XC3_ItemDescCur", "sell description", "extended description"),
    H("V959_BUY", "C3B5B7", "20 C2 BF", "jsr XC3_ShopBuy", "_c3b5b7 buy", "extended entry: extended give"),
    H("V960_BUY_NAME", "C3BAC6", "20 68 C0", "jsr XC3_LoadItemNameCur", "buy quantity screen name", "9-bit name"),
    H("V961_SELL_NAME", "C3BADF", "20 68 C0", "jsr XC3_LoadItemNameCur", "sell quantity screen name", "9-bit name"),
    H("V962_BUY_TYPE", "C3B7E9", "20 21 83", "jsr XC3_PropPtrCur", "_c3b7e6 (item type)", "9-bit record"),
    H("V963_SHOP_STAT", "C3BAF8", "20 21 83", "jsr XC3_PropPtrCur", "DrawShopItemStat", "9-bit record"),
    H("V964_SELL_PRICE", "C3BB68", "20 21 83", "jsr XC3_PropPtrCur", "sell price", "9-bit record (price / 2)"),
    H("V965_CANEQ_ID", "C3BCE1", "BF 89 9D 7E", "jsr XC3_ShopLdaX", "shop: who can equip (current entry)",
      "XSHOPCURHI := entry high bit", pad=True),
    H("V966_CANEQ_PROP", "C3BCE5", "20 21 83", "jsr XC3_PropPtrCur", "shop: who can equip", "9-bit record"),
    H("V967_CANEQ2_ID", "C3C1B0", "BF 89 9D 7E", "jsr XC3_ShopLdaX", "shop: who can equip (party sprites)",
      "XSHOPCURHI := entry high bit", pad=True),
    H("V968_CANEQ2_PROP", "C3C1B4", "20 21 83", "jsr XC3_PropPtrCur", "shop: who can equip (party sprites)",
      "9-bit record"),
    H("V969_SHOP_STATS_X", "C3BD13", "20 21 83", "jsr XC3_ShopPtrX", "_c3bcfd per-entry stats", "9-bit record"),
    H("V970_SELLALL_CLR", "C3B739", "99 69 18", "jsr XC3_StaInvYClr", "sell all units of a slot",
      "the emptied slot's high bit is cleared"),
    # ---- Rare Items menu ---------------------------------------------------------------------------------------
    H("V980_RARE_DESCPTR", "C38339", "A2 60 FB", "ldx #XRareDescPtr & $FFFF", "InitRareItemDesc C3:8339",
      "52 rare descriptions (XRareDescPtr, absolute pointers in bank FA)"),
    H("V981_RARE_DESCBASE", "C3833E", "A2 B0 FC", "ldx #$0000", "InitRareItemDesc", "absolute pointers"),
    H("V982_RARE_DESCBANK", "C38343", "A9 CE", "lda #^XRareDescPtr", "InitRareItemDesc", "bank FA"),
    H("V983_RARE_COUNT", "C3834C", "20 6B 83", "jsr XC3_RareCount", "InitRareItemDesc (count)",
      "number of owned rare items over all pages"),
    H("V984_RARE_NAMEPTR", "C3843B", "A0 A0 FB", "ldy #XRareName & $FFFF", "GetRareItemNamePtr C3:8436",
      "52 rare names (XRareName)"),
    H("V985_RARE_NAMEBANK", "C38440", "A9 CE", "lda #^XRareName", "GetRareItemNamePtr", "bank FA"),
    H("V986_RARE_LIST", "C3838E", "20 94 83", "jsr XC3_RareListS", "InitRareItemList C3:838B",
      "list of the current page (vanilla ids 0-19 + FF6X ids 20-51)"),
    H("V987_RARE_PAGE", "C32748", "20 4A 7D", "jsr XC3_RarePage", "menu state ITEM_RARE C3:2741",
      "page turning (Down / Up at the edge, R / L)"),
    H("V988_RARE_OPEN", "C326A0", "20 8B 83", "jsr XC3_RareInit", "SelectItemOption_02 C3:268E", "page 0"),
]
