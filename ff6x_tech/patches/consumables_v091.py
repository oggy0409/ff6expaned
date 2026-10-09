"""TECH v0.9.1 - static validation and record composition of the production consumables
(items/production_v091/consumables.json), the key items and the extended shops (items/production_v091/ext_shops.json).
Extends patches/consumables_v09.py (unchanged, still used by the frozen v0.9 targets) with the v0.9.1 effect fields:

  fixed_amount    1..9999  exact HP (or MP) restored (restore items) / total damage before the split (hybrid items);
                           run by asm/item_v091/v091.s (XFixAmt). The power byte stays non-zero (nominal 255): the
                           vanilla CalcTargetDmg returns early on power 0.
  sets_status     list     statuses SET by the item (ItemProp status bytes without the 'lift status' flag $20);
                           exclusive with removes_status.
  hybrid_element  name     the damage is split: half takes this element, half is non-elemental (XHybrid). The
                           record element must be exactly this element; damage items only; one enemy.
  shop_cap        1..98    (item level) purchase cap: owned + bought <= cap (XShopCap); only for sold items.
Any violation aborts the build.
"""
from collections import Counter
from patches import consumables_v09 as V9
from patches.consumables_v09 import (CODES, TARGETING, ELEMENT, STATUS, ITEM_ANIM_PTRS, VAN_PROP, NAME_MAX,
                                     DESC_LINE_MAX, fail as _fail9)

SPELL_ANIM = dict(V9.SPELL_ANIM)
SPELL_ANIM["SPELL:BOLT_BEAM"] = 0x84 * 14             # ATTACK_ANIM_PROP offset of attack $84 (Magitek Bolt Beam)
ANIM_TEMPLATES = V9.ANIM_TEMPLATES
DISPEL_MASK = bytes.fromhex("1014FE84")              # Rev 1 spell $2C (Dispel) status bytes 10-13 (D-17)
REMEDY_MASK = bytes.fromhex("6548")                  # Rev 1 item $F5 (Remedy) status bytes 21-22


def fail(msg):
    raise SystemExit(f"consumables v0.9.1: {msg}")


def validate(items, clean, snes_to_pc):
    if len(items) != 8:
        fail(f"{len(items)} consumables, expected 8")
    if sorted(int(it["id"], 16) for it in items) != list(range(0x127, 0x12F)):
        fail("consumable ids must occupy $127-$12E exactly once (ids unchanged since v0.9)")
    if sorted(it["code"] for it in items) != CODES:
        fail("locked codes CN-01..CN-08 must each appear once")
    for key in ("symbol", "display_name", "locked_name"):
        dup = [k for k, n in Counter(it[key] for it in items).items() if n > 1]
        if dup:
            fail(f"duplicate {key}: {dup}")
    # the vanilla Dispel / Remedy masks the locked items copy are re-read from the clean ROM
    if clean[snes_to_pc(0xC46AC0) + 14 * 0x2C + 10: snes_to_pc(0xC46AC0) + 14 * 0x2C + 14] != DISPEL_MASK:
        fail("Rev 1 Dispel status mask changed?")
    if clean[snes_to_pc(VAN_PROP) + 30 * 0xF5 + 21: snes_to_pc(VAN_PROP) + 30 * 0xF5 + 23] != REMEDY_MASK:
        fail("Rev 1 Remedy status mask changed?")
    for it in items:
        i, lo = it["id"], int(it["id"], 16) & 0xFF
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
        known = {"restore_hp", "restore_mp", "power", "fraction", "removes_status", "status", "undead_invert",
                 "element", "fixed_amount", "sets_status", "hybrid_element"}
        if set(e) - known:
            fail(f"{i}: unknown effect keys {sorted(set(e) - known)}")
        if not 1 <= e.get("power", 0) <= 255 and not e.get("removes_status"):
            fail(f"{i}: power out of 1..255")
        if e.get("fraction") and not 1 <= e["power"] <= 16:
            fail(f"{i}: fraction power is in 16ths (1..16)")
        for s in e.get("status", []) + e.get("sets_status", []):
            if s not in STATUS:
                fail(f"{i}: unknown status {s}")
        if bool(e.get("status")) != bool(e.get("removes_status")):
            fail(f"{i}: 'status' (removed) only with removes_status")
        if e.get("sets_status") and e.get("removes_status"):
            fail(f"{i}: one ItemProp record either sets or removes its statuses")
        if "DEAD" in e.get("status", []) and not e.get("restore_hp"):
            fail(f"{i}: a revive item must restore HP")
        if "DEAD" in e.get("sets_status", []):
            fail(f"{i}: an item must not set Death")
        fx = e.get("fixed_amount")
        if fx is not None:
            if not 1 <= fx <= 9999 or e.get("fraction") or e.get("power", 0) == 0:
                fail(f"{i}: fixed_amount 1..9999, non-fraction, power byte non-zero")
            if not (e.get("restore_hp") or e.get("restore_mp") or e.get("hybrid_element")):
                fail(f"{i}: fixed_amount only for an HP / MP restoring or hybrid item")
            if e.get("restore_mp") and e.get("restore_hp"):
                fail(f"{i}: fixed_amount with HP and MP restore (one battle amount)")
        h = e.get("hybrid_element")
        if h is not None:
            if h not in ELEMENT or e.get("element") != [h]:
                fail(f"{i}: hybrid element must equal the record element")
            if e.get("restore_hp") or e.get("restore_mp") or e.get("removes_status") or e.get("sets_status"):
                fail(f"{i}: a hybrid item is a pure damage item")
            if it["targeting"] != "ONE_ENEMY":
                fail(f"{i}: hybrid item targets one enemy")
            if it["usable_field"]:
                fail(f"{i}: hybrid damage item is battle-only")
        cap = it.get("shop_cap")
        if cap is not None and (not 1 <= cap <= 98 or not it["sold_in_shops"]):
            fail(f"{i}: shop_cap 1..98 and only for a sold item")
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
        for n in ("display_name",):
            if len(it[n]) > NAME_MAX:
                fail(f"{i}: display name longer than 12")
        lines = it["desc"].split("{n}")
        if len(lines) > 2 or any(len(l) > DESC_LINE_MAX for l in lines):
            fail(f"{i}: description must be <= 2 lines of <= 28")
    return True


def compose(it):
    """30-byte ItemProp record (every byte explicit). sets_status = status bytes without the lift flag."""
    e = it["effect"]
    if e.get("sets_status"):
        tmp = dict(it, effect={k: v for k, v in e.items() if k != "sets_status"})
        rec = bytearray(V9.compose(tmp))
        for s in e["sets_status"]:
            o, b = STATUS[s]
            rec[o] |= b
        return bytes(rec)
    return V9.compose(it)


def anim_offset(it, clean, snes_to_pc):
    t = it["anim_template"]
    if t in SPELL_ANIM:
        return SPELL_ANIM[t]
    return V9.anim_offset(it, clean, snes_to_pc)


def engine_tables(items):
    """XFixAmt (64 x 2), XHybrid (64 x 1), XShopCap (64 x 1), XCtxFlags (64 x 1) indexed by the extended low byte.
    XCtxFlags bit0 = the record removes Vanish (kept by the v0.9.1 MagicStatusEffect hook)."""
    fix, hyb, cap, ctx = bytearray(128), bytearray(64), bytearray(64), bytearray(64)
    for it in items:
        k = int(it["id"], 16) & 0x3F
        e = it["effect"]
        if e.get("fixed_amount"):
            fix[2 * k:2 * k + 2] = e["fixed_amount"].to_bytes(2, "little")
        if e.get("hybrid_element"):
            hyb[k] = ELEMENT[e["hybrid_element"]]
        if it.get("shop_cap"):
            cap[k] = it["shop_cap"]
        if e.get("removes_status") and "VANISH" in e.get("status", []):
            ctx[k] |= 0x01
    return bytes(fix), bytes(hyb), bytes(cap), bytes(ctx)


validate_rare = V9.validate_rare
SHOP_TYPES = {1, 2, 3, 4, 5}


def validate_shops(shops, ext_ids, clean, snes_to_pc, equipment_ids=()):
    """$80-$8F once, <= 8 entries, type 1-5, price modifier 0-7; extended entries must be SOLD extended consumables
    (signature equipment is never sold: D-20); vanilla entries must be real priced vanilla items (no $FF 'Empty')."""
    seen = set()
    for s in shops:
        sid = int(s["shop_id"], 16)
        if not 0x80 <= sid <= 0x8F or sid in seen:
            fail(f"extended shop id {s['shop_id']} (allowed $80-$8F, once)")
        seen.add(sid)
        if s["type"] not in SHOP_TYPES or not 0 <= s["price_mod"] <= 7:
            fail(f"shop {s['shop_id']}: type / price modifier")
        if not 1 <= len(s["items"]) <= 8 or len(set(s["items"])) != len(s["items"]):
            fail(f"shop {s['shop_id']}: 1-8 distinct items")
        for x in s["items"]:
            v = int(x, 16)
            if v >= 0x100:
                if v in equipment_ids:
                    fail(f"shop {s['shop_id']}: signature equipment {x} is never sold (D-20)")
                if v not in ext_ids:
                    fail(f"shop {s['shop_id']}: {x} is not a sold extended consumable")
            else:
                if v == 0xFF:
                    fail(f"shop {s['shop_id']}: $FF is not an item")
                a = snes_to_pc(VAN_PROP) + 30 * v
                if (clean[a + 28] | clean[a + 29] << 8) <= 2:
                    fail(f"shop {s['shop_id']}: vanilla item ${v:02X} has no shop price (unsold / ultimate)")
    return True
