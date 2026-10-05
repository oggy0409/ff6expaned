#!/usr/bin/env python3
"""DEV-ONLY (TECH v0.7.1): item consumer audit -> audits/item_consumer_audit_v071.json + markdown tables
(ITEM_CONSUMER_AUDIT_v0.7.1.md section "Generated tables").

Inputs: the exact Rev 1 instruction index (devtools/rev1_insn_index.py), the disassembly sources (for the
enclosing routine of each site), patches/item_v071_hooks.py and data/item_relocation_v071.json.

Every Rev 1 instruction that reads or writes the inventory ($1869-$1A68) or the equipment bytes ($161F-$1624,
any index) and every long operand into ItemProp / ItemName / WeaponAnimProp is listed with one status:
  HOOKED     replaced by a same-length hook (id in patches/item_v071_hooks.py)
  RETARGET   long operand moved to the 320-entry copy in bank FA (the id reaching it decides ext-awareness,
             see ROUTINES)
  REVIEWED   left unchanged; the reviewed reason (REASONS) states why an extended item cannot be mis-read there
Any site without a hook, a retarget or a reviewed reason makes this tool exit non-zero.
usage: item_consumer_audit_v071.py <insn.tsv> <ff6dis_root> <out.json> <out.md>"""
import json, os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from patches.item_v071_hooks import HOOKS

EMPTY = "EMPTY-TEST: empty-slot scan (CMP #$FF) on the raw low byte; an extended slot is never $FF, so it is correctly treated as occupied"
SELECTED = "SELECTED: acts on a slot chosen by a hooked masked search (never an extended slot) or by an empty-slot scan"
USABLE = "USABLE-ONLY: field item-use path, reached only for type-6 menu-usable items (UseItem prop pointer is hooked, I305); extended items are equipment"
DEAD_ARR = "DEAD: copy/sort helpers of Arrange, only called from C3:267F/C3:2682, which I310 replaces with XArrange"
ENDING = "ENDING: the_end cutscene reuses this WRAM as scratch after the final battle; the game cannot be saved afterwards (vanilla behaviour)"
REASONS = {
    "C0:4A6C": "RANGE: Tintinabar relic test (relic ids $B0-$E6); extended low bytes are $00-$3F",
    "C0:4A73": "RANGE: as C0:4A6C (relic 2)",
    "C0:9FF2": "EventCmd_8d writes $FF after I213 (XC0_8dLoad) already returned an extended item to the inventory and cleared its bit",
    "C0:A006": EMPTY, "C0:A01C": SELECTED, "C0:A021": SELECTED, "C0:A029": SELECTED,
    "C0:A0D7": "COVERED: CharProp init stores vanilla ids; I216 (C0:A0D0) clears the record's 6 equipment bits first",
    "C0:A0DE": "COVERED: as C0:A0D7", "C0:A0E5": "COVERED: as C0:A0D7", "C0:A0EC": "COVERED: as C0:A0D7",
    "C0:A0F3": "COVERED: as C0:A0D7",
    "C0:AD0D": EMPTY, "C0:AD1E": SELECTED, "C0:AD22": SELECTED, "C0:AD29": SELECTED, "C0:AD3E": SELECTED,
    "C0:AD41": SELECTED, "C0:AD48": "SELECTED: TakeItem empties a vanilla slot found by the masked search I212 (its bit is already 0)",
    "C0:BDC0": "New Game inventory init ($FF / 0); I220 then zeroes every extension bit",
    "C0:BDC3": "New Game inventory init ($FF / 0); I220 then zeroes every extension bit",
    "C2:20B9": "battle hand write-back of the low byte; the high bit is untouched and an extended hand cannot change in battle (I542 swap guard)",
    "C2:20BD": "as C2:20B9 (R-hand)",
    "C2:498A": "DEAD: inside C2:4981-C2:499D, bypassed by I520 (XBattleEndInv)",
    "C2:4993": "DEAD: inside C2:4981-C2:499D, bypassed by I520 (XBattleEndInv)",
    "C2:49B2": "SELECTED: colosseum wager slot found by the masked compare I521", "C2:49BB": "SELECTED: as C2:49B2",
    "C2:49BE": "SELECTED: as C2:49B2",
    "C2:54B4": "RANGE: battle tool-list builder (ids $A3-$AA); extended low bytes are $00-$3F",
    "C2:5FF3": "RANGE: Cursed Shld ($66) -> Paladin Shld; extended low bytes are $00-$3F",
    "C2:6009": "RANGE: as C2:5FF3 (writes $67 only into a slot that held vanilla $66)",
    "C3:26BA": DEAD_ARR, "C3:26C3": DEAD_ARR, "C3:26CE": DEAD_ARR, "C3:26D6": DEAD_ARR, "C3:272C": DEAD_ARR,
    "C3:2733": DEAD_ARR,
    "C3:27BA": "COVERED: item move swaps raw bytes; I309 (C3:27DE, XC3_SwapBits) swaps the two high bits",
    "C3:27BF": "COVERED: as C3:27BA", "C3:27C8": "COVERED: as C3:27BA", "C3:27CB": "COVERED: as C3:27BA",
    "C3:27D0": "COVERED: as C3:27BA", "C3:27D3": "COVERED: as C3:27BA", "C3:27D6": "COVERED: as C3:27BA",
    "C3:27DB": "COVERED: as C3:27BA",
    "C3:8056": "ALIAS-SAFE: item-list text colour (usable test via vanilla props of the low byte); aliases $00-$3F are weapons -> grey, identical to an extended (never usable) item",
    "C3:8359": "count of non-empty slots (CMP #$FF): an extended slot correctly counts as an item",
    "C3:84C4": USABLE, "C3:8A75": USABLE, "C3:8B02": USABLE, "C3:8C2F": USABLE,
    "C3:9829": "DEAD: GetBestEquip body, replaced by I357 (JMP XC3_GetBestEquip)",
    "C3:9855": "DEAD: GetBest2Hand body, replaced by I358 (JMP XC3_GetBest2Hand)",
    "C3:9D74": EMPTY, "C3:9D80": SELECTED, "C3:9D8A": SELECTED, "C3:9D92": SELECTED, "C3:9DA9": SELECTED,
    "C3:9DB0": SELECTED, "C3:9DB4": SELECTED, "C3:9DBA": SELECTED,
    "C3:9DBF": "SELECTED: DecItemQty empties a vanilla slot found by I391 (bit already 0); extended decrements use XC3_DecQtyB",
    "C3:B5C9": EMPTY, "C3:B5D5": SELECTED, "C3:B5E4": SELECTED, "C3:B5E7": SELECTED,
    "C3:B729": "SELECTED: sell acts on the selected sell-list slot; extended slots cannot be selected (I421, emulator M2)",
    "C3:B72F": "SELECTED: as C3:B729", "C3:B739": "SELECTED: as C3:B729", "C3:B73D": "SELECTED: as C3:B729",
    "C3:BC76": "SELECTED: shop owned count after the masked search I424",
    "C3:BCA1": "SELECTED: quantity of the selected sell slot (never extended)",
}
EMPTY_HAND = "EMPTY-TEST: hand empty test (CMP #$FF) on the slot low byte; an extended slot is never $FF -> occupied (correct)"
DEAD_RM = "DEAD: EquipRemoveAll body, replaced by I340 (JMP XC3_RemoveAll)"
RELIC_RANGE = "RANGE: compared only with vanilla relic ids (Genji Glove / Gauntlet / Merit Award / shop relic $B0-$E6); extended low bytes are $00-$3F"
REASONS.update({
    "C3:9070": "RANGE: DrawRelicMenu saves the relic low bytes for CheckReequipRelics, which tests vanilla relic ids only; an extended relic's low byte is $00-$3F and differs from every relic id",
    "C3:9075": "RANGE: as C3:9070",
    "C3:9420": EMPTY_HAND, "C3:9427": EMPTY_HAND, "C3:997F": EMPTY_HAND, "C3:9986": EMPTY_HAND,
    "C3:99FC": EMPTY_HAND, "C3:9A03": EMPTY_HAND,
    "C3:96AB": DEAD_RM, "C3:96B1": DEAD_RM, "C3:96B7": DEAD_RM, "C3:96BD": DEAD_RM, "C3:96C5": DEAD_RM,
    "C3:96C8": DEAD_RM, "C3:96CB": DEAD_RM, "C3:96CE": DEAD_RM,
    "C3:9F5F": RELIC_RANGE, "C3:9F66": RELIC_RANGE, "C3:9F8B": RELIC_RANGE, "C3:9F9A": RELIC_RANGE,
    "C3:BF2E": RELIC_RANGE + " (shop relic branch @bf18, shop item is a relic)", "C3:BF35": RELIC_RANGE + " (as C3:BF2E)",
})
REASONS.update({
    "C2:54A1": "COVERED: vanilla battle-inventory copy loop kept; I516 (C2:54B0, XC2_ExtSlotsEmpty) re-copies every extended slot exactly as an empty slot",
    "C2:54A7": "COVERED: as C2:54A1",
})
OTHER_HAND = "check_equip input: the OTHER hand (two-hand compatibility, usage flags); the REPLACED hand is refused by I542 when extended"
EXCH = "hand <-> inventory exchange executed only after check_equip passed (I542 refused an extended replaced hand)"
UNUSABLE = "use-a-hand-item path: an extended hand is never usable (usage $80 kept by XC2_LoadItemPropX)"
for a in ("C1:8A58", "C1:8A5E", "C1:8A69", "C1:8A6F", "C1:8F9A", "C1:8FA0", "C1:9061", "C1:9067"):
    REASONS[a] = OTHER_HAND
for a in ("C1:8B50", "C1:8B63", "C1:8B6D", "C1:8B72", "C1:8B76", "C1:8B79", "C1:8B7C", "C1:8B85", "C1:8B8B", "C1:8B91",
          "C1:8B97", "C1:8B9C", "C1:8C05", "C1:8C18", "C1:8C22", "C1:8C27", "C1:8C2B", "C1:8C2E", "C1:8C31", "C1:8C3A",
          "C1:8C40", "C1:8C46", "C1:8C4C", "C1:8C51", "C1:8F79", "C1:8FC2", "C1:8FD8", "C1:8FDE", "C1:8FE4", "C1:8FEA",
          "C1:8FEF", "C1:9040", "C1:9089", "C1:909F", "C1:90A5", "C1:90AB", "C1:90B1", "C1:90B6"):
    REASONS[a] = EXCH
for a in ("C1:7126", "C1:712D", "C1:7133", "C1:7138", "C1:713B", "C1:713E", "C1:7141", "C1:7145", "C1:714C", "C1:7152",
          "C1:7157", "C1:715A", "C1:715D", "C1:7160", "C1:8ED7", "C1:8EDE", "C1:8EE5", "C1:8EEC"):
    REASONS[a] = UNUSABLE
for a in ("C1:8E72", "C1:8E84", "C1:8E87", "C1:8E97"):
    REASONS[a] = "COVERED: R-hand <-> L-hand exchange; I545 (C1:8E8F, XC1_HandSwapBits) swaps the two equipment bits with the entries"
for a in ("C1:8F2F", "C1:8F35", "C1:8F3D", "C1:8F43"):
    REASONS[a] = "read-only copy of the selected hand for the cursor display (w7e890d/e)"
REASONS.update({
    "C1:4BD4": "COVERED: R-hand header id; the name is chosen through the XBTLNAME queue (I540/I541)",
    "C1:BA2F": "Jump: usage flag $10 of the hand (an extended weapon carries the weapon flag like a vanilla weapon); index hooked I543/I544",
    "C1:BA36": "as C1:BA2F (left hand)",
    "C2:0629": "SetRage (Gau): hands := monster attack type; extended weapons/shields can never be equippable by Gau/Umaro (builder refuses)",
    "C2:062C": "as C2:0629",
    "C2:20AB": "battle write-back source (see C2:20B9)", "C2:20AF": "battle write-back source (see C2:20B9)",
    "C2:2930": "RHandItem := equipment low byte (CalcEquipEffect $11C6); extended-ness is taken from the slot bit by I530-I533",
    "C2:2D00": "monster entries only (MonsterProp attack type)",
    "C2:3F14": "Ogre Nix break write: reached only when I533 matched, never for an extended weapon",
    "C2:3F17": "as C2:3F14", "C2:3F1A": "as C2:3F14",
})
for a in ("E5:F7B7", "E5:FAEB", "E5:FB0A", "E5:FB0D", "E5:FB30", "E5:FB61", "E5:FB6B", "E5:FB8A", "E5:FB8D", "E5:FBB0",
          "E5:FBE1", "E5:FBEB", "E5:FC0A", "E5:FC0D", "E5:FC30", "E5:FC61"):
    REASONS[a] = ENDING

SITE_CLASS = {"C1:BA4C": ("EXT-AWARE", "ItemJumpThrowAnim index from I543/I544 (extended weapon -> $80 + low byte, XJumpAnim "
                                       "FA:3700); the Throw consumer C1:B9CC keeps D1:0040 (thrown ids are vanilla only)")}
# routine -> how an id reaches the relocated table consumer
EXT = "EXT-AWARE"
VAN = "VANILLA-ONLY"
ROUTINES = {
    "CalcEquipEffect": (EXT, "9-bit id from I500 (XC2_EqLoad), offset from I501 (XC2_PropOfs)"),
    "InitItemTarget": (VAN, "battle Item/Throw command ids: the battle item list never holds an extended id (extended slots are presented empty, extended hands are not usable/throwable)"),
    "_magicitem": (VAN, "item/thrown item used in battle: same reason as InitItemTarget"),
    "LoadItemProp": (VAN, "battle inventory: extended slots are re-copied as empty slots (I516); extended hands go through XC2_LoadItemPropX (I511/I513)"),
    "LearnItemMagic": (EXT, "offset from I502 (XC2_LearnOfs, 9-bit id of the equipment slot)"),
    "GetItemNameColor": ("ALIAS-SAFE", "see C3:8056"),
    "UseItem": (EXT, "prop pointer I305 (XC3_PropPtrB); extended items are not type 6, so the use path stops"),
    "DrawItemDetails": (EXT, "I306/I307"), "DrawWeaponPower": (EXT, "X from I307; id test I308"),
    "DrawWeaponLearnedMagic": (EXT, "X from I307"), "DrawItemEvadeModifier": (EXT, "X from I307"),
    "_c388a0": (EXT, "X from I307"), "_c38959": (EXT, "X from I307"),
    "_c38c33": (VAN, "field item-use effects: usable items only"), "lpget": (VAN, "field item-use effects: usable items only"),
    "GetValidWeapons": (EXT, "I353/I354"), "GetValidShields": (EXT, "I355/I356"),
    "GetBest2Hand": (EXT, "routine replaced by I358 (XC3_GetBest2Hand reads XItemProp with 9-bit ids)"),
    "_c39975": (EXT, "I367-I370"), "CheckHandEffects": (EXT, "I371-I374"), "CheckCanEquipItem": (EXT, "I375-I380"),
    "GetValidEquip": (EXT, "I381-I386"), "_c3a051": (EXT, "I392/I393"), "SortValidEquip": (EXT, "I402/I403"),
    "_c3b7e6": (VAN, "shop item ids (1-byte shop lists)"), "CalcShopPrice": (VAN, "shop item ids"),
    "DrawShopItemStat": (VAN, "shop item ids"), "_c3bb65": (VAN, "shop item ids"), "_c3bcc9": (VAN, "shop item ids"),
    "_c3bcfd": (EXT, "party comparison: equipment ids from I430-I451"), "_c3c19c": (VAN, "shop item ids"),
    "CalcItemWidth": (VAN, "dialogue item name (event-supplied 1-byte id)"),
    "UpdateDlgText": (VAN, "dialogue item name (event-supplied 1-byte id)"),
    "Loop3": (VAN, "CalcItemWidth (field/text.asm, label inside the proc): dialogue item name, event-supplied 1-byte id"),
    "_83ee": (VAN, "UpdateDlgText (field/text.asm, label inside the proc): dialogue item name, event-supplied 1-byte id"),
    "_c16048": (VAN, "battle message item names (steal / win / thrown): battle ids only"),
    "ListTextCmd_12": (VAN, "battle item list rows: extended slots presented empty"),
    "ListTextCmd_0e": (EXT, "hand names: I540/I541 (XBTLNAME queue -> XItemName + $100*13)"),
    "MenuTextCmd_12": (VAN, "battle message item names"), "MenuTextCmd_0e": (VAN, "battle message item names"),
    "FindItemsWithIcon": ("DEAD", DEAD_ARR), "_c380ce": (EXT, "called by XC3_ListNameY (I301) for vanilla names; extended names read XItemName directly"),
    "_c38fe1": (EXT, "replaced by I321 (XC3_EqpName)"), "LoadEquipListItemName": (EXT, "I387/I388"),
    "LoadItemName": (VAN, "shop list names (shop ids)"),
    "InitWeaponAnim": (EXT, "animation number from I530 (XC2_AnimId: extended weapon -> $C0+low byte)"),
}


def main(tsv, dis, out_json, out_md):
    rows = [l.rstrip("\n").split("\t") for l in open(tsv)]
    idx = {r[0]: i for i, r in enumerate(rows)}
    hooked = {}
    for h in HOOKS:
        a = int(h["snes"], 16)
        for k in range(len(bytes.fromhex(h["expect"]))):
            hooked[a + k] = h["id"]
    srcs = {}

    def routine(snes):
        r = rows[idx[snes]]
        f, ln = r[5].rsplit(":", 1)
        lines = srcs.setdefault(f, open(os.path.join(dis, f.lstrip("./"))).read().splitlines())
        for k in range(int(ln) - 1, -1, -1):
            l = lines[k]
            m = re.match(r"^\.proc\s+(\w+)", l) or re.match(r"^([A-Za-z_]\w*):", l)
            if m:
                return m.group(1)
        return "?"
    sites, missing = [], []
    for r in rows:
        if r[3] not in ("abs", "absx", "absy", "absl", "abslx") or not r[4] or r[2] in ("JMP", "JSR", "JSL", "JML"):
            continue
        v = int(r[4], 16)
        if r[3] in ("absl", "abslx"):
            if v >> 16 != 0x7E:
                continue
            v &= 0xFFFF
        kind = "inventory id" if 0x1869 <= v <= 0x1968 else "inventory qty" if 0x1969 <= v <= 0x1A68 else \
            "equipment" if 0x161F <= v <= 0x1624 else None
        if kind is None and r[0].startswith("C3") and r[3] == "absy" and 0x001F <= v <= 0x0024:
            kind = "equipment (char ptr)"            # menu: Y = $1600 + rec*37 (GetSelCharPropPtr / CharPropPtrs)
        if kind is None and r[0].startswith("C2") and r[3] == "absx" and v == 0x15FB:
            kind = "equipment (UpdateEquip)"         # X = rec*37 + $24 + slot
        if kind is None and r[0][:2] in ("C1", "C2") and (v in (0x3CA8, 0x3CA9) or 0x2B86 <= v <= 0x2BAD):
            kind = "battle hand id/list"
        if not kind:
            continue
        a = int(r[0].replace(":", ""), 16)
        if a in hooked:
            st, why = "HOOKED", hooked[a]
        elif r[0] in REASONS:
            st, why = "REVIEWED", REASONS[r[0]]
        else:
            st, why = "MISSING", ""
            missing.append(r[0])
        sites.append({"snes": r[0], "insn": f"{r[2]} {r[4]}", "kind": kind, "routine": routine(r[0]), "status": st,
                      "detail": why, "src": f"{r[5]} {r[6].strip()[:60]}"})
    rel = json.load(open(os.path.join(HERE, "data", "item_relocation_v071.json")))
    tables = []
    for t, v in rel["tables"].items():
        for c in v["consumers"]:
            s = c["snes"][:2] + ":" + c["snes"][2:]
            ro = routine(s)
            cls = SITE_CLASS.get(s) or ROUTINES.get(ro)
            if s in SITE_CLASS:
                ro = "Jump animation (anim_cmd.asm:521, battle command $16 handler)"
            if cls is None:
                missing.append(f"{s} ({ro})")
                cls = ("MISSING", "")
            tables.append({"snes": s, "table": t, "routine": ro, "class": cls[0], "detail": cls[1]})
    res = {"_comment": "Generated by devtools/item_consumer_audit_v071.py", "ram_sites": sites, "table_consumers": tables,
           "hooks": [{k: h[k] for k in ("id", "snes", "original_asm", "asm", "consumer", "reason")} for h in HOOKS],
           "missing": missing}
    json.dump(res, open(out_json, "w"), indent=1)
    with open(out_md, "w") as f:
        f.write("### A. Inventory / equipment RAM accesses (every Rev 1 instruction)\n\n| SNES | Insn | Kind | Routine | Status | Hook / reviewed reason |\n|---|---|---|---|---|---|\n")
        for s in sites:
            f.write(f"| {s['snes']} | `{s['insn']}` | {s['kind']} | {s['routine']} | {s['status']} | {s['detail']} |\n")
        f.write(f"\n### B. Relocated-table consumers ({len(tables)} long operands), by routine\n\n| Routine | Sites | Class | How an id reaches it |\n|---|---|---|---|\n")
        by = {}
        for t in tables:
            by.setdefault((t["routine"], t["class"], t["detail"]), []).append(f"{t['table']}@{t['snes']}")
        for (ro, c, d), v in by.items():
            f.write(f"| {ro} | {', '.join(v)} | {c} | {d} |\n")
        f.write(f"\n### C. Hook sites ({len(HOOKS)})\n\n| ID | SNES | Original Rev 1 | Replacement | Consumer | Reason |\n|---|---|---|---|---|---|\n")
        for h in HOOKS:
            f.write(f"| {h['id']} | {h['snes'][:2]}:{h['snes'][2:]} | `{h['original_asm']}` | `{h['asm'].replace(chr(10), ' / ')}` | {h['consumer']} | {h['reason']} |\n")
    n = {k: sum(1 for s in sites if s["status"] == k) for k in ("HOOKED", "REVIEWED", "MISSING")}
    print("ram sites", len(sites), n, "table consumers", len(tables), "missing", missing)
    if missing:
        raise SystemExit("unclassified consumer sites")


if __name__ == "__main__":
    main(*sys.argv[1:5])
