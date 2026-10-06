"""TECH v0.9 item engine build: v0.8 signature equipment ($100-$126) + 8 extended consumables ($127-$12E),
extended shops ($80+), FF6X rare items (logical rare ids 20-51; capacity 32).

Sources (single source of truth, all validated fail-closed):
  items/production_v08/equipment.json      39 signature equipment (unchanged since v0.8)
  items/production_v09/consumables.json    8 consumables (patches/consumables_v09.py)
  items/production_v09/rare_items.json     5 locked key items (rare ids 20-24)
  items/production_v09/ext_shops.json      extended shops $80, $81
  items/qa_v071/qa_items.json              QA-only equipment $13D-$13F (QA targets)
  items/qa_v09/qa_rare_items.json          QA-only rare placeholders 25-51 (QA targets: fills the 32-entry registry)
Engine: asm/item_v09 (asm/item_v08 + v09.s); hooks: patches/item_v071_hooks.py (+ OVERRIDES) + patches/item_v09_hooks.py

Tables (ITEMX_TABLES FA:0000-FA:7FFF), v0.8 layout unchanged + TECH v0.9 tables at FA:5000:
  XItemAnimX    FA:5000   64 x 2   item animation (ATTACK_ANIM_PROP offset) per extended low byte
  XRareDef      FA:5080    4       defined FF6X rare ids (bit n = rare id 20+n)
  XRareDescPtr  FA:5090   52 x 2   absolute FA pointers to the rare descriptions
  XRareName     FA:5100   52 x 13  rare names (0-19 = byte copy of CE:FBA0)
  XShopProp     FA:5400  144 x 9   shop table (0-$7F = byte copy of C4:7AC0, $80-$8F extended)
  XShopPropHi   FA:5940  144 x 9   same layout: 1 = the entry is an extended item ($100 | low byte)
  XRareDescText FA:5E80-           rare descriptions (0-19 = byte copies of the vanilla strings)
"""
import json, os
from ff6x.asm816 import Program
from ff6x.hirom import snes_to_pc, fmt_snes
from patches import item_v071, consumables_v09
from patches.item_v071 import menu_encode, HERE

ASM_V09 = os.path.join(HERE, "asm", "item_v09")
SOURCES_V09 = ["core.s", "c0.s", "c3.s", "c2.s", "c1x.s", "v09.s"]
CONS_SRC = "items/production_v09/consumables.json"
RARE_SRC = "items/production_v09/rare_items.json"
SHOP_SRC = "items/production_v09/ext_shops.json"
RARE_QA_SRC = "items/qa_v09/qa_rare_items.json"

T_ANIMX, T_RDEF, T_RDPTR, T_RNAME, T_SHOP, T_SHOPHI, T_RDTXT = (0xFA5000, 0xFA5080, 0xFA5090, 0xFA5100, 0xFA5400,
                                                                0xFA5940, 0xFA5E80)
VAN_RNAME, VAN_RDPTR, VAN_RDTXT, VAN_SHOP = 0xCEFBA0, 0xCEFB60, 0xCEFCB0, 0xC47AC0
N_SHOPS = 0x90
FLAG_DEF, FLAG_SPEAR, FLAG_CONS, FLAG_SELL = 0x01, 0x02, 0x04, 0x08
ICON_TBL = 0xC326F5


def load(path):
    return json.load(open(os.path.join(HERE, path)))


def build_tables(rom, meta):
    clean = rom.clean
    pc = snes_to_pc
    # ---- v0.8 tables (equipment + QA equipment) via the accepted composer ---------------------------------
    tables, notes = item_v071.build_tables(clean, item_v071.load_defs(meta))
    tab = {label: (at, bytearray(data)) for label, at, data in tables}
    prop, name, flags = tab["XItemProp"][1], tab["XItemName"][1], tab["XExtFlags"][1]
    dptr, dtxt = tab["XDescPtr"][1], tab["XDescText"][1]
    # ---- consumables ----------------------------------------------------------------------------------------
    cons = load(CONS_SRC)["items"]
    consumables_v09.validate(cons, clean, pc)
    animx = bytearray(64 * 2)
    icons = set(clean[pc(ICON_TBL):pc(ICON_TBL) + 17])
    for it in cons:
        i = int(it["id"], 16); k = i - 0x100
        if flags[k]:
            raise SystemExit(f"{it['id']}: id already defined")
        rec = consumables_v09.compose(it)
        prop[30 * i:30 * i + 30] = rec
        nm = menu_encode(it["display_name"], 0xFE)
        if len(nm) > consumables_v09.NAME_MAX:
            raise SystemExit(f"{it['id']}: display name longer than 12")
        name[13 * i:13 * i + 13] = b"\xFF" + nm + b"\xFF" * (12 - len(nm))
        if 0xFF not in icons:
            raise SystemExit("Arrange icon table has no blank icon")
        lines = it["desc"].split("{n}")
        if len(lines) > 2 or any(len(l) > consumables_v09.DESC_LINE_MAX for l in lines):
            raise SystemExit(f"{it['id']}: description must be <= 2 lines of <= 28")
        flags[k] = FLAG_DEF | FLAG_CONS | (FLAG_SELL if it["sellable"] else 0)
        txt = menu_encode(it["desc"], 0xFF) + b"\x00"
        dptr[2 * k:2 * k + 2] = ((item_v071.T_DTXT + len(dtxt)) & 0xFFFF).to_bytes(2, "little")
        dtxt += txt
        av = consumables_v09.anim_offset(it, clean, pc)
        animx[2 * (i & 0x3F):2 * (i & 0x3F) + 2] = av.to_bytes(2, "little")
        notes[f"{i:03X}"] = {"name": it["display_name"], "base": None, "type": 6, "prop": rec.hex(" ").upper(),
                             "name_bytes": name[13 * i:13 * i + 13].hex(" ").upper(), "flags": f"{flags[k]:02X}",
                             "anim": f"{av:04X}", "source": CONS_SRC}
    if item_v071.T_DTXT + len(dtxt) > T_ANIMX:
        raise SystemExit("XDescText overlaps the v0.9 tables")
    # ---- rare items -----------------------------------------------------------------------------------------
    prod_r = load(RARE_SRC)["rare_items"]
    qa_r = []
    if meta.get("qa_harness"):
        d = load(RARE_QA_SRC)
        assert d.get("qa")
        qa_r = d["rare_items"]
    consumables_v09.validate_rare(prod_r, qa_r)
    rname = bytearray(clean[pc(VAN_RNAME):pc(VAN_RNAME) + 20 * 13]) + b"\xFF" * (32 * 13)
    rdef = bytearray(4)
    rdtxt = bytearray()
    rdptr = bytearray(52 * 2)
    van_ptr = [clean[pc(VAN_RDPTR) + 2 * j] | clean[pc(VAN_RDPTR) + 2 * j + 1] << 8 for j in range(20)]
    for j in range(20):
        a = pc(VAN_RDTXT) + van_ptr[j]
        e = a
        while clean[e] != 0:
            e += 1
        rdptr[2 * j:2 * j + 2] = ((T_RDTXT + len(rdtxt)) & 0xFFFF).to_bytes(2, "little")
        rdtxt += clean[a:e + 1]
    rnotes = {}
    for r in sorted(prod_r + qa_r, key=lambda r: r["rare_id"]):
        j = r["rare_id"]
        nm = menu_encode(r["display_name"], 0xFE)
        rname[13 * j:13 * j + 13] = nm + b"\xFF" * (13 - len(nm))
        rdef[(j - 20) >> 3] |= 1 << ((j - 20) & 7)
        rdptr[2 * j:2 * j + 2] = ((T_RDTXT + len(rdtxt)) & 0xFFFF).to_bytes(2, "little")
        rdtxt += menu_encode(r["desc"], 0xFF) + b"\x00"
        rnotes[str(j)] = {"code": r["code"], "name": r["display_name"], "qa": r in qa_r}
    for j in range(20, 52):                       # undefined ids: empty description
        if not rdef[(j - 20) >> 3] & (1 << ((j - 20) & 7)):
            rdptr[2 * j:2 * j + 2] = ((T_RDTXT + len(rdtxt)) & 0xFFFF).to_bytes(2, "little")
    rdtxt += b"\x00"
    if T_RDTXT + len(rdtxt) > item_v071.T_END + 1:
        raise SystemExit("rare description text overflows ITEMX_TABLES")
    # ---- shops ----------------------------------------------------------------------------------------------
    shops = load(SHOP_SRC)["shops"]
    sold = {int(it["id"], 16) for it in cons if it["sold_in_shops"]}
    consumables_v09.validate_shops(shops, sold)
    shop = bytearray(clean[pc(VAN_SHOP):pc(VAN_SHOP) + 128 * 9]) + b"\xFF" * (16 * 9)
    shophi = bytearray(N_SHOPS * 9)
    for s in shops:
        sid = int(s["shop_id"], 16)
        rec = bytearray([s["type"] | s["price_mod"] << 3]) + b"\xFF" * 8
        for e, x in enumerate(s["items"]):
            v = int(x, 16)
            rec[1 + e] = v & 0xFF
            shophi[sid * 9 + 1 + e] = 1 if v >= 0x100 else 0
        shop[sid * 9:sid * 9 + 9] = rec
    for sid in range(0x82, N_SHOPS):              # unused extended shop ids: type 3, empty
        shop[sid * 9] = 3
    out = [(l, at, bytes(d)) for l, (at, d) in tab.items()]
    out += [("XItemAnimX", T_ANIMX, bytes(animx)), ("XRareDef", T_RDEF, bytes(rdef)),
            ("XRareDescPtr", T_RDPTR, bytes(rdptr)), ("XRareName", T_RNAME, bytes(rname)),
            ("XShopProp", T_SHOP, bytes(shop)), ("XShopPropHi", T_SHOPHI, bytes(shophi)),
            ("XRareDescText", T_RDTXT, bytes(rdtxt))]
    notes["_rare"] = rnotes
    notes["_shops"] = {s["shop_id"]: s["items"] for s in shops}
    return out, notes


def table_externs():
    e = item_v071.table_externs()
    e.update({"XItemAnimX": T_ANIMX, "XRareDef": T_RDEF, "XRareDescPtr": T_RDPTR, "XRareName": T_RNAME,
              "XShopProp": T_SHOP, "XShopPropHi": T_SHOPHI, "XRareDescText": T_RDTXT,
              "XDescText": item_v071.T_DTXT})
    return e


def hooks():
    from patches.item_v071_hooks import HOOKS as H071
    from patches.item_v09_hooks import HOOKS as H09, OVERRIDES
    out = []
    for h in H071:
        h = dict(h)
        if h["id"] in OVERRIDES:
            h.update(OVERRIDES[h["id"]])
        out.append(h)
    return out + list(H09)


def build(rom, target, alloc, meta):
    notes = {"ext_items": {}, "tables": {}, "sections": {}, "hooks": []}
    tables, notes["ext_items"] = build_tables(rom, meta)
    for label, at, data in tables:
        rom.place("ITEMX_TABLES", data, label, "I101_ITEM_TABLES", at=at,
                  reason=f"{label}: extended item table (TECH v0.9 layout)",
                  consumer="retargeted ItemProp/ItemName consumers and the extended item engine")
        notes["tables"][label] = {"snes": fmt_snes(at), "length": len(data)}
    ext = table_externs()
    src = []
    for f in SOURCES_V09:
        src.append(f"; ==== {f}\n" + open(os.path.join(ASM_V09, f)).read())
    prog = Program("\n".join(src), ext, "item_v09")
    secs = prog.assemble()
    for name, (org, code) in secs.items():
        how, reg = item_v071.REGION_OF[name]
        if how == "place":
            rom.place(reg, code, f"{name}", "I102_ITEM_ENGINE_CODE", at=org,
                      reason="TECH v0.9 extended item engine (65816, asm/item_v09)",
                      consumer="JSL from hook sites / bank stubs")
        else:
            rom.patch(org, b"\xFF" * len(code), code, f"I103_{name}_STUBS", claim=reg,
                      consumer=f"JSR from same-bank hook sites ({name})",
                      reason="same-bank helper stubs in audited vanilla padding (never referenced, all $FF)")
        notes["sections"][name] = {"snes": fmt_snes(org), "length": len(code)}
    syms = dict(ext); syms.update(prog.symbols)
    notes["retargeted_operands"] = item_v071.retarget_tables(rom, "I110_RETARGET")
    for h in hooks():
        site = int(h["snes"], 16)
        expect = bytes.fromhex(h["expect"])
        mode = h.get("mode", ".a8\n.i16")
        hp = Program(f".section H ${site:06X}\n{mode}\n{h['asm']}\n", syms, h["id"])
        new = hp.assemble()["H"][1]
        if len(new) < len(expect) and h.get("pad_nop"):
            new = new + b"\xEA" * (len(expect) - len(new))
        if len(new) != len(expect):
            raise SystemExit(f"{h['id']}: hook {len(new)} bytes vs expected original {len(expect)}")
        rom.patch(site, expect, new, h["id"], consumer=h["consumer"], reason=h["reason"])
        notes["hooks"].append({"id": h["id"], "snes": fmt_snes(site), "pc": f"{snes_to_pc(site):06X}",
                               "original": expect.hex(" ").upper(), "new": new.hex(" ").upper(),
                               "asm": h["asm"], "consumer": h["consumer"], "reason": h["reason"]})
    notes["symbols"] = {k: fmt_snes(v) for k, v in sorted(prog.symbols.items()) if v >= 0xC00000 and "@" not in k}
    notes["listing"] = {n: prog.listing(n) for n in secs}
    return notes
