"""TECH v0.8 - static validation of the 39 production signature equipment definitions
(items/production_v08/equipment.json). Called by patches/item_v071.load_defs for every target that carries them;
any violation aborts the build.

Checks: exactly 39 items, ids $100-$126 each used once, locked codes EQ-W01..W13 / A01..A13 / R01..R13 each once,
category counts (13 weapons, 7 body, 4 helmets, 2 shields, 13 relics), unique symbols / display names, users are
permanent characters, Gau/Umaro never on an extended weapon or shield (engine rule R8), weapon Battle Power inside the
locked 184-222 envelope, stat nibbles in range, spear flag only on spears, acquisition: one binding per item, unique
reward ids and future event symbols, one-time only, GP cost only (and always) for smith purchases, fallback
documented for every relic whose locked line names an optional ASM effect.
"""
from collections import Counter

CODES = [f"EQ-W{n:02d}" for n in range(1, 14)] + [f"EQ-A{n:02d}" for n in range(1, 14)] + \
        [f"EQ-R{n:02d}" for n in range(1, 14)]
CATEGORY_COUNT = {"weapon": 13, "armor": 7, "helmet": 4, "shield": 2, "relic": 13}
PERMANENT = ["Terra", "Locke", "Cyan", "Shadow", "Edgar", "Sabin", "Celes", "Strago", "Relm", "Setzer", "Mog", "Gau",
             "Gogo", "Umaro"]
WEAPON_POWER = (184, 222)
SOURCE_TYPES = {"smith_purchase", "event_chest", "quest_reward", "boss_reward", "arc_reward_tbd"}


def fail(msg):
    raise SystemExit(f"equipment v0.8: {msg}")


def validate(items):
    if len(items) != 39:
        fail(f"{len(items)} production items, expected 39")
    ids = sorted(int(it["id"], 16) for it in items)
    if ids != list(range(0x100, 0x127)):
        fail("ids must occupy $100-$126 exactly once")
    codes = [it["code"] for it in items]
    if sorted(codes) != sorted(CODES):
        fail(f"locked concept codes mismatch: {sorted(set(CODES) ^ set(codes))}")
    if Counter(it["category"] for it in items) != Counter(CATEGORY_COUNT):
        fail(f"category counts {dict(Counter(it['category'] for it in items))}")
    for key in ("symbol", "display_name", "locked_name"):
        dup = [k for k, n in Counter(it[key] for it in items).items() if n > 1]
        if dup:
            fail(f"duplicate {key}: {dup}")
    rewards, symbols = Counter(), Counter()
    for it in items:
        i = it["id"]
        if not it["users"] or any(u not in PERMANENT for u in it["users"]):
            fail(f"{i}: users must be permanent characters")
        if len(set(it["users"])) != len(it["users"]):
            fail(f"{i}: duplicate user")
        if it["category"] in ("weapon", "shield") and set(it["users"]) & {"Gau", "Umaro"}:
            fail(f"{i}: extended weapon/shield must not be equippable by Gau or Umaro (R8)")
        for k in ("vigor", "speed", "stamina", "mag_pwr"):
            if not -7 <= it[k] <= 7:
                fail(f"{i}: {k} out of -7..7")
        for k in ("evade", "mblock"):
            if it[k] % 10 or not 0 <= it[k] <= 50:
                fail(f"{i}: {k} must be 0..50 in steps of 10")
        if it["category"] == "weapon":
            if not WEAPON_POWER[0] <= it["power"] <= WEAPON_POWER[1]:
                fail(f"{i}: Battle Power {it['power']} outside the locked {WEAPON_POWER} envelope")
            if it["spear"] != (it["family"] == "spear"):
                fail(f"{i}: spear flag must match the spear family")
        elif it.get("spear"):
            fail(f"{i}: spear flag on non-weapon")
        if not it.get("unique"):
            fail(f"{i}: signature equipment must be unique")
        a = it.get("acquisition")
        if not a:
            fail(f"{i}: no acquisition binding")
        if a["source_type"] not in SOURCE_TYPES:
            fail(f"{i}: source type {a['source_type']}")
        if not a.get("one_time"):
            fail(f"{i}: acquisition must be one-time (BAL-16 no repeat farming)")
        if not a.get("planned_source") or not a.get("future_event_symbol"):
            fail(f"{i}: planned source / event symbol missing")
        if (a["source_type"] == "smith_purchase") != bool(a.get("gp_cost")):
            fail(f"{i}: gp_cost exactly for smith purchases")
        if a["source_type"] == "smith_purchase" and not a.get("smith"):
            fail(f"{i}: smith purchase rules missing")
        rewards[a["reward_id"]] += 1
        symbols[a["future_event_symbol"]] += 1
        if "(ASM" in it["locked_stats"] and not (it.get("fallback") and it["fallback"].get("deferred_effect")):
            fail(f"{i}: optional ASM effect without a documented BAL-18 fallback")
    for what, c in (("reward_id", rewards), ("future_event_symbol", symbols)):
        dup = [k for k, n in c.items() if n > 1]
        if dup:
            fail(f"duplicate {what} (one signature reward per binding): {dup}")
    return True


def equip_matrix(items):
    """item x 14 permanent characters (1 = can equip), from the source definitions"""
    return {it["id"]: [1 if c in it["users"] else 0 for c in PERMANENT] for it in items}
