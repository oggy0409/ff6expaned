"""TECH v0.9 - static validation and record composition of the 8 production consumables
(items/production_v09/consumables.json), the FF6X rare-item registry (items/production_v09/rare_items.json, QA:
items/qa_v09/qa_rare_items.json) and the extended shops (items/production_v09/ext_shops.json).
Any violation aborts the build.
"""
from collections import Counter

CODES = [f"CN-{n:02d}" for n in range(1, 9)]
KEY_CODES = [f"KI-{n:02d}" for n in range(1, 6)]
TARGETING = {"ONE_ALLY": 0x01, "ONE_ENEMY": 0x41, "ALL_ALLIES": 0x2E, "ALL_ENEMIES": 0x6E}
ELEMENT = {"FIRE": 0x01, "ICE": 0x02, "LIGHTNING": 0x04, "POISON": 0x08, "WIND": 0x10, "HOLY": 0x20, "EARTH": 0x40,
           "WATER": 0x80}
# status name -> (record byte 21..24, bit)
STATUS = {"BLIND": (21, 0x01), "ZOMBIE": (21, 0x02), "POISON": (21, 0x04), "MAGITEK": (21, 0x08), "VANISH": (21, 0x10),
          "IMP": (21, 0x20), "PETRIFY": (21, 0x40), "DEAD": (21, 0x80),
          "CONDEMNED": (22, 0x01), "NEAR_FATAL": (22, 0x02), "IMAGE": (22, 0x04), "SILENCE": (22, 0x08),
          "BERSERK": (22, 0x10), "CONFUSE": (22, 0x20), "SAP": (22, 0x40), "SLEEP": (22, 0x80),
          "DANCE": (23, 0x01), "REGEN": (23, 0x02), "SLOW": (23, 0x04), "HASTE": (23, 0x08), "STOP": (23, 0x10),
          "SHELL": (23, 0x20), "SAFE": (23, 0x40), "REFLECT": (23, 0x80),
          "RAGE": (24, 0x01), "FREEZE": (24, 0x02), "LIFE3": (24, 0x04), "MORPH": (24, 0x08), "CHANT": (24, 0x10),
          "HIDE": (24, 0x20), "INTERCEPTOR": (24, 0x40), "FLOAT": (24, 0x80)}
ANIM_TEMPLATES = {"E8", "E9", "EA", "EB", "EC", "ED", "EE", "F0", "F1", "F2", "F3", "F4", "F5", "F8", "FE"}
SPELL_ANIM = {"SPELL:FIRE_2": 0x0046}       # ATTACK_ANIM_PROP offset of spell 5 (Fire 2): 5 * 14
ITEM_ANIM_PTRS = 0xD10000
VAN_PROP = 0xD85000
NAME_MAX, RARE_NAME_MAX, DESC_LINE_MAX = 12, 13, 28
RARE_VAN, RARE_N = 20, 52


def fail(msg):
    raise SystemExit(f"consumables v0.9: {msg}")


def validate(items, clean, snes_to_pc):
    if len(items) != 8:
        fail(f"{len(items)} consumables, expected 8")
    ids = sorted(int(it["id"], 16) for it in items)
    if ids != list(range(0x127, 0x12F)):
        fail("consumable ids must occupy $127-$12E exactly once ($12F-$13C reserve, $13D-$13F QA)")
    if sorted(it["code"] for it in items) != CODES:
        fail("locked codes CN-01..CN-08 must each appear once")
    for key in ("symbol", "display_name", "locked_name"):
        dup = [k for k, n in Counter(it[key] for it in items).items() if n > 1]
        if dup:
            fail(f"duplicate {key}: {dup}")
    for it in items:
        i, lo = it["id"], int(it["id"], 16) & 0xFF
        # the Item command can never use the vanilla item with this low byte (C2 identifies the extended consumable
        # by command = Item + low byte): it must not be battle-usable, and it must not be a spell-casting item
        van = clean[snes_to_pc(VAN_PROP) + 30 * lo]
        if van & 0x20:
            fail(f"{i}: vanilla item ${lo:02X} is battle-usable - low byte would be ambiguous for the Item command")
        if it["category"] != "consumable":
            fail(f"{i}: category")
        for k in ("steal", "drop", "metamorph", "colosseum_wager", "throwable", "equippable", "enemy_use"):
            if it[k]:
                fail(f"{i}: {k} must be false (v0.9 exclusion rule)")
        if not (it["usable_battle"] or it["usable_field"]):
            fail(f"{i}: a consumable must be usable somewhere")
        if it["targeting"] not in TARGETING:
            fail(f"{i}: targeting {it['targeting']}")
        e = it["effect"]
        if not 1 <= e.get("power", 0) <= 255 and not e.get("removes_status"):
            fail(f"{i}: power out of 1..255")
        if e.get("fraction") and not 1 <= e["power"] <= 16:
            fail(f"{i}: fraction power is in 16ths (1..16)")
        for s in e.get("status", []):
            if s not in STATUS:
                fail(f"{i}: unknown status {s}")
        if bool(e.get("status")) != bool(e.get("removes_status")):
            fail(f"{i}: status list only with removes_status")
        if "DEAD" in e.get("status", []) and not e.get("restore_hp"):
            fail(f"{i}: a revive item must restore HP")
        if it["sellable"] != it["sold_in_shops"]:
            fail(f"{i}: sellable == sold in shops (v0.9 rule)")
        if it["sellable"] and not 2 <= it["price"] <= 65535:
            fail(f"{i}: price")
        if it["anim_template"] not in ANIM_TEMPLATES and it["anim_template"] not in SPELL_ANIM:
            fail(f"{i}: animation template {it['anim_template']}")
        a = it["acquisition"]
        for k in ("source_type", "planned_source", "future_event_symbol", "conditions"):
            if not a.get(k):
                fail(f"{i}: acquisition.{k} missing")
        if (a["source_type"] == "shop") != it["sold_in_shops"]:
            fail(f"{i}: shop acquisition iff sold in shops")
        if not it.get("derived"):
            fail(f"{i}: derived-field list missing")
    return True


def compose(it):
    """30-byte ItemProp record of a consumable, every byte explicit (no template bytes)."""
    rec = bytearray(30)
    rec[0] = 6 | (0x20 if it["usable_battle"] else 0) | (0x40 if it["usable_field"] else 0)
    rec[14] = TARGETING[it["targeting"]]
    e = it["effect"]
    for n in e.get("element", []):
        rec[15] |= ELEMENT[n]
    f = 0
    if e.get("fraction"):
        f |= 0x80
    if e.get("removes_status"):
        f |= 0x20
    if e.get("restore_mp"):
        f |= 0x10
    if e.get("restore_hp"):
        f |= 0x08
    if e.get("undead_invert"):
        f |= 0x02
    rec[19] = f
    rec[20] = e.get("power", 0)
    for s in e.get("status", []):
        o, b = STATUS[s]
        rec[o] |= b
    rec[27] = 0xFF                                     # no item special effect
    p = it["price"]
    rec[28], rec[29] = p & 0xFF, p >> 8
    return bytes(rec)


def anim_offset(it, clean, snes_to_pc):
    t = it["anim_template"]
    if t in SPELL_ANIM:
        return SPELL_ANIM[t]
    i = int(t, 16) - 0xE0
    a = snes_to_pc(ITEM_ANIM_PTRS) + 2 * i
    v = clean[a] | clean[a + 1] << 8
    if v == 0xFFFF:
        fail(f"{it['id']}: template ${t} has no item animation")
    return v


def validate_rare(prod, qa):
    if sorted(r["code"] for r in prod) != KEY_CODES:
        fail("locked key items KI-01..KI-05 must each appear once")
    ids = [r["rare_id"] for r in prod + qa]
    if len(ids) != len(set(ids)):
        fail("duplicate rare id")
    for r in prod:
        if not RARE_VAN <= r["rare_id"] < RARE_VAN + 5:
            fail(f"production rare id {r['rare_id']} outside 20-24")
        if r.get("combat_stats") is not None:
            fail(f"{r['code']}: key items have no combat stats")
        for k in ("symbol", "story_arc", "acquisition", "consumed", "ending_dependency"):
            if k not in r:
                fail(f"{r['code']}: {k} missing")
        if not r["acquisition"].get("future_event_symbol") or not r["acquisition"].get("one_time"):
            fail(f"{r['code']}: one-time acquisition binding missing")
    for r in qa:
        if not 25 <= r["rare_id"] < RARE_N:
            fail(f"QA rare id {r['rare_id']} outside 25-51")
    for r in prod + qa:
        if len(r["display_name"]) > RARE_NAME_MAX:
            fail(f"rare {r['rare_id']}: name longer than 13")
        lines = r["desc"].split("{n}")
        if len(lines) > 2 or any(len(l) > DESC_LINE_MAX + 4 for l in lines):
            fail(f"rare {r['rare_id']}: description must be <= 2 lines of <= 32")
    return True


def validate_shops(shops, ext_ids):
    seen = set()
    for s in shops:
        sid = int(s["shop_id"], 16)
        if not 0x80 <= sid <= 0x8F or sid in seen:
            fail(f"extended shop id {s['shop_id']} (allowed $80-$8F, once)")
        seen.add(sid)
        if len(s["items"]) > 8:
            fail(f"shop {s['shop_id']}: more than 8 items")
        for x in s["items"]:
            v = int(x, 16)
            if v >= 0x100 and v not in ext_ids:
                fail(f"shop {s['shop_id']}: {x} is not a sold extended consumable")
    return True
