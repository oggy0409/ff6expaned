#!/usr/bin/env python3
"""TECH v0.8: generate the equipment documents from the canonical source (items/production_v08/equipment.json) and
the clean Rev 1 ROM (vanilla comparison data).

  EQUIPMENT_MASTER_TABLE_v0.8.{json,csv,md}   EQUIP_MATRIX_v0.8.csv   EQUIPMENT_ACQUISITION_MAP_v0.8.{json,md}
  EQUIPMENT_ANIMATION_MAP_v0.8.md   FALLBACK_EFFECTS_v0.8.md   EQUIPMENT_BALANCE_AUDIT_v0.8.md

usage: equipment_docs_v08.py <clean_rev1.sfc> <outdir>
"""
import csv, json, os, sys
from itertools import combinations
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from patches import item_v071 as IV
from patches.equipment_v08 import equip_matrix

CHARS = IV.CHARS
TYPES = {1: "weapon", 2: "armor", 3: "shield", 4: "helmet", 5: "relic"}
EL = {v: k for k, v in IV.ELEMENT.items()}
ST = {v: k for k, v in IV.STATUS12.items()}
RELIC_NAMES = {(9, 0x01): "ATLAS_ARMLET", (9, 0x02): "EARRING", (9, 0x04): "HP_PLUS_25", (9, 0x08): "HP_PLUS_50",
               (9, 0x10): "HP_PLUS_12", (9, 0x20): "MP_PLUS_25", (9, 0x40): "MP_PLUS_50", (9, 0x80): "MP_PLUS_12",
               (10, 0x01): "GALE_HAIRPIN", (10, 0x02): "BACK_GUARD", (10, 0x04): "JUMP", (10, 0x08): "X_MAGIC",
               (10, 0x10): "CONTROL", (10, 0x20): "GIL_TOSS", (10, 0x40): "CAPTURE", (10, 0x80): "DRAGON_HORN",
               (11, 0x01): "INC_STEAL_RATE", (11, 0x02): "SINGLE_EARRING", (11, 0x04): "INC_SKETCH_RATE",
               (11, 0x08): "INC_CONTROL_RATE", (11, 0x10): "MAX_HIT_RATE", (11, 0x20): "MP_COST_HALF",
               (11, 0x40): "MP_COST_1", (11, 0x80): "STRENGTH_PLUS_50", (12, 0x01): "X_FIGHT", (12, 0x02): "RAND_RETAL",
               (12, 0x04): "RAND_EVADE", (12, 0x08): "GAUNTLET", (12, 0x10): "GENJI_GLOVE", (12, 0x20): "EQUIP_MERIT",
               (12, 0x40): "COVER", (13, 0x01): "SHELL_HP_LOW", (13, 0x02): "SAFE_HP_LOW", (13, 0x08): "DOUBLE_EXP",
               (13, 0x10): "DOUBLE_GP", (13, 0x80): "MAKE_UNDEAD"}


def ch(c):
    if 0x80 <= c <= 0x99: return chr(65 + c - 0x80)
    if 0x9A <= c <= 0xB3: return chr(97 + c - 0x9A)
    if 0xB4 <= c <= 0xBD: return chr(48 + c - 0xB4)
    return {0xC0: "/", 0xC3: "'", 0xC4: "-", 0xC5: ".", 0xC6: ","}.get(c, " ")


def nib(v): return v if v < 8 else -(v - 8)
def nibe(v): return v * 10 if v < 6 else -(v - 5) * 10


def decode(rec, name, i):
    t = rec[0] & 7
    eq = rec[1] | rec[2] << 8
    d = {"id": i, "name": name, "type": TYPES.get(t, "other"), "users": [CHARS[k] for k in range(14) if eq >> k & 1],
         "merit": bool(eq & 0x8000), "imp": bool(eq & 0x4000), "power": rec[20], "hit_mdef": rec[21], "vig": nib(rec[16] & 15),
         "spd": nib(rec[16] >> 4), "sta": nib(rec[17] & 15), "mag": nib(rec[17] >> 4), "evade": nibe(rec[26] & 15),
         "mblock": nibe(rec[26] >> 4)}
    pos, neg = set(), set()
    if t == 1:
        for b, n in EL.items():
            if rec[15] & b: pos.add("attack:" + n)
        if rec[18]: pos.add(f"spell_cast:{rec[18]:02X}")
        if rec[27] >> 4: pos.add(f"weapon_special:{rec[27] >> 4}")
    else:
        for b, n in EL.items():
            if rec[15] & b: pos.add("half:" + n)
            if rec[22] & b: pos.add("absorb:" + n)
            if rec[23] & b: pos.add("null:" + n)
            if rec[24] & b: neg.add("weak:" + n)
    imm = rec[6] | rec[7] << 8
    for b, n in ST.items():
        if imm & b: pos.add("immune:" + n)
    if rec[8] or rec[25]: pos.add(f"auto_status:{rec[8]:02X}{rec[25]:02X}")
    for (o, b), n in RELIC_NAMES.items():
        if rec[o] & b: pos.add("relic:" + n)
    if rec[5]: pos.add(f"field:{rec[5]:02X}")
    d["pos"], d["neg"] = pos, neg
    return d


NUM = ["power", "hit_mdef", "vig", "spd", "sta", "mag", "evade", "mblock"]


def dominates(a, b):
    """a dominates b: >= on every number, features(b) <= features(a), negatives(a) <= negatives(b), > on one"""
    if not all(a[k] >= b[k] for k in NUM):
        return False
    if not (b["pos"] <= a["pos"] and a["neg"] <= b["neg"]):
        return False
    return any(a[k] > b[k] for k in NUM) or a["pos"] > b["pos"] or a["neg"] < b["neg"]


def main(clean, out):
    van = open(clean, "rb").read()
    pc = lambda a: a - 0xC00000
    items = json.load(open(os.path.join(HERE, "items/production_v08/equipment.json")))["items"]
    V = []
    for i in range(256):
        rec = van[pc(IV.VAN_PROP) + 30 * i:pc(IV.VAN_PROP) + 30 * i + 30]
        if rec[0] & 7 in (1, 2, 3, 4, 5) and i != 0xFF:
            nm = "".join(ch(c) for c in van[pc(IV.VAN_NAME) + 13 * i + 1:pc(IV.VAN_NAME) + 13 * i + 13]).strip()
            d = decode(rec, nm, f"{i:02X}")
            if not d["imp"]:                    # Imp-only gear (equip flag $4000) is not a normal option
                V.append(d)
    N = [decode(IV.compose_v08(van, it), it["display_name"], it["id"]) for it in items]
    for n, it in zip(N, items):
        n["it"] = it
    os.makedirs(out, exist_ok=True)
    w = lambda f: open(os.path.join(out, f), "w")

    # ------------------------------------------------------------------ master table
    rows = []
    for it in items:
        a = it["acquisition"]
        rows.append({"id": f"${it['id']}", "code": it["code"], "symbol": it["symbol"], "locked_name": it["locked_name"],
                     "display_name": it["display_name"], "category": it["category"], "family": it["family"],
                     "icon_template": f"${it['template']} {it['template_name']}", "users": "/".join(it["users"]),
                     "power_or_def": it["power"], "hit_or_mdef": it.get("hit_rate", it.get("mdef")),
                     "vigor": it["vigor"], "speed": it["speed"], "stamina": it["stamina"], "mag_pwr": it["mag_pwr"],
                     "evade": it["evade"], "mblock": it["mblock"],
                     "elements": ";".join([f"attack:{e}" for e in it.get("elem_attack", [])] +
                                          [f"half:{e}" for e in it.get("elem_half", [])] +
                                          [f"absorb:{e}" for e in it.get("elem_absorb", [])] +
                                          [f"null:{e}" for e in it.get("elem_null", [])] +
                                          [f"weak:{e}" for e in it.get("elem_weak", [])]),
                     "status_immunity": ";".join(it.get("immune_status", [])),
                     "relic_effects": ";".join(it.get("relic_effects", [])),
                     "weapon_flags": ";".join(it.get("weapon_flags", [])), "weapon_special": it.get("weapon_special", ""),
                     "spear_jump_x2": it.get("spear", False), "proc_spell": "none",
                     "animation": f"${it['template']} {it['template_name']}" if it["category"] == "weapon" else "",
                     "description": it["desc"].replace("{n}", " / "), "source_type": a["source_type"],
                     "planned_source": a["planned_source"], "reward_id": a["reward_id"],
                     "future_event_symbol": a["future_event_symbol"], "gp_cost": a.get("gp_cost") or "",
                     "unique": it["unique"], "fallback": (it["fallback"] or {}).get("deferred_effect") or "",
                     "locked_stats": it["locked_stats"]})
    json.dump({"_comment": "generated by tools/equipment_docs_v08.py from items/production_v08/equipment.json",
               "items": items}, w("EQUIPMENT_MASTER_TABLE_v0.8.json"), indent=1, ensure_ascii=False)
    with w("EQUIPMENT_MASTER_TABLE_v0.8.csv") as f:
        cw = csv.DictWriter(f, fieldnames=list(rows[0])); cw.writeheader(); cw.writerows(rows)
    with w("EQUIPMENT_MASTER_TABLE_v0.8.md") as f:
        f.write("# TECH v0.8 — equipment master table ($100-$126)\n\nGenerated from `items/production_v08/equipment.json` "
                "(canonical source). Locked name = the creative lock; display name = the in-game 12-character name "
                "(ROM name field = icon + 12 characters, as vanilla; the locked name opens the description where the "
                "display name is abbreviated).\n\n## ID map\n\n| ID | Name (locked) | In-game | Type | Acquisition | Notes |\n|---|---|---|---|---|---|\n")
        for it in items:
            a = it["acquisition"]
            note = []
            if it["fallback"]: note.append("BAL-18 fallback: " + it["fallback"]["deferred_effect"] + " deferred")
            if it.get("spear"): note.append("Jump x2 (spear)")
            if a.get("gp_cost"): note.append(f"smith {a['gp_cost']} GP")
            f.write(f"| ${it['id']} | {it['locked_name']} | {it['display_name']} | {it['category']} ({it['family']}) | "
                    f"{a['source_type']}: {a['planned_source']} | {'; '.join(note)} |\n")
        f.write("\nReserve $127-$13C: free. QA-only $13D-$13F: QA Blade13D / QA Mail 13E / QA Charm13F (QA ROM only).\n\n"
                "## Stats\n\n| ID | Name | Users | Pwr/Def | Hit/MDef | Vig | Spd | Sta | Mag | Eva | MBlk | Elements | Status immunity | Relic bits | Weapon flags / special |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['id']} | {r['locked_name']} | {r['users']} | {r['power_or_def']} | {r['hit_or_mdef']} | "
                    f"{r['vigor']:+d} | {r['speed']:+d} | {r['stamina']:+d} | {r['mag_pwr']:+d} | {r['evade']} | "
                    f"{r['mblock']} | {r['elements'] or '-'} | {r['status_immunity'] or '-'} | {r['relic_effects'] or '-'} | "
                    f"{r['weapon_flags'] or '-'}{' / ' + r['weapon_special'] if r['weapon_special'] not in ('', 'NONE') else ''} |\n")
        f.write("\n## Derived (not given by the locked stat line)\n\nEvery derivation, per item:\n\n")
        for it in items:
            f.write(f"* **${it['id']} {it['locked_name']}** — locked: `{it['locked_stats']}`. " +
                    "; ".join(f"{k}: {v}" for k, v in it["derived"].items() if v) + "\n")
        f.write("\nCommon to all 39: price field 2 (vanilla value for unsold items; Sell excludes $1xx), no spell cast / "
                "proc, not throwable, no MERIT / IMP equip flag, no auto-status, no field effect, unique.\n")

    # ------------------------------------------------------------------ equip matrix
    mat = equip_matrix(items)
    with w("EQUIP_MATRIX_v0.8.csv") as f:
        f.write("id,name,category," + ",".join(CHARS) + "\n")
        for it in items:
            f.write(f"${it['id']},{it['locked_name']},{it['category']}," + ",".join(str(v) for v in mat[it["id"]]) + "\n")

    # ------------------------------------------------------------------ acquisition map
    acq = [{"item_id": f"${it['id']}", "name": it["locked_name"], **it["acquisition"]} for it in items]
    json.dump({"_comment": "reward bindings (source-controlled); story events bind to future_event_symbol later. "
               "Validated by patches/equipment_v08.py: one binding per item, unique reward ids and symbols, one-time only, "
               "GP cost only for smith purchases.", "bindings": acq}, w("EQUIPMENT_ACQUISITION_MAP_v0.8.json"), indent=1)
    with w("EQUIPMENT_ACQUISITION_MAP_v0.8.md") as f:
        f.write("# TECH v0.8 — acquisition map\n\nEvery production item has exactly one one-time binding. Story events / maps "
                "for these sources are not implemented yet; they bind to `future_event_symbol` later and must use the "
                "extended event API (`give_ext_item`, `has_ext_item`). Signature equipment is excluded from vanilla shops, "
                "Sell, Steal, Drop, Metamorph, Colosseum wager and Throw (Option C engine: 1-byte sources cannot hold $1xx).\n\n"
                "| reward_id | item | source type | planned source | future_event_symbol | conditions | one-time | GP |\n|---|---|---|---|---|---|---|---|\n")
        for a in acq:
            f.write(f"| {a['reward_id']} | {a['item_id']} {a['name']} | {a['source_type']} | {a['planned_source']} | "
                    f"`{a['future_event_symbol']}` | {', '.join(a['conditions'])} | {'yes' if a['one_time'] else 'NO'} | "
                    f"{a.get('gp_cost') or ''} |\n")
        f.write("\n## Smith items (event-driven purchase, D4)\n\nNot in any vanilla shop inventory; no reforge consumption (D6: "
                "Tempered Edge, Raider Knife and Doma Edge are independent items).\n\n| item | smith | GP | prerequisite placeholder | already owned | not enough GP | inventory full |\n|---|---|---|---|---|---|---|\n")
        for it in items:
            a = it["acquisition"]
            if a["source_type"] == "smith_purchase":
                s = a["smith"]
                f.write(f"| ${it['id']} {it['locked_name']} | {a['planned_source']} | {a['gp_cost']} | {', '.join(a['conditions'])} | "
                        f"{s['already_owned']} | {s['insufficient_gp']} | {s['inventory_full']} |\n")
        f.write("\nGP costs are derived (the locked sheets give none): tier of the nearest vanilla shop weapon "
                "(Falchion 17000, Partisan 13000) scaled to the higher Battle Power — Tempered Edge 18000, "
                "Sandpiercer 20000, Doma Edge 24000. The purchase script template is the QA smith demo "
                "(`events/qa_access_v08/events.evt` `QaSmithBuy8`), runtime-tested.\n\n"
                "Raider Knife (\"Reconstruction chain\") is bound as a quest reward, not a smith purchase: the locked "
                "source names a quest chain, not a smith.\n\n"
                "Items whose source the locked Armor sheet leaves to arc design (`arc_reward_tbd`) keep a reserved "
                "binding symbol and placeholder prerequisite until the arc content exists.\n")

    # ------------------------------------------------------------------ animation map
    with w("EQUIPMENT_ANIMATION_MAP_v0.8.md") as f:
        f.write("# TECH v0.8 — weapon graphics / animation map\n\nNo new custom weapon graphic is locked, so every weapon uses "
                "a deliberate vanilla template of the same family. The builder copies the template's WeaponAnimProp entry "
                "(EC:E400, index template+1) into XWeaponAnimFull[$C0 + low byte] and its ItemJumpThrowAnim byte "
                "(D1:0040) into XJumpAnim[$80 + low byte]; the ItemProp record is built from the item definition only. "
                "The low-byte vanilla alias (e.g. $100 -> Dirk, $13D -> Chocobo Brsh) is never consulted for graphics. "
                "Verified in the emulator (`tools/emu_equip_battle_v08.py` W1/J1): the animation number used by Fight, and "
                "every rendered frame of Fight (all 13) and Jump (both spears) equal to the same battle continued with the "
                "template weapon in hand (one in-battle state, only the hand item id differs).\n\n"
                "| ID | Weapon | Family | Template (graphic + animation) | Icon | Jump | Runic | 2-hand (Gauntlet) | Bushido flag | Dual wield | Notes |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
        for it in items:
            if it["category"] != "weapon":
                continue
            fl = it["weapon_flags"]
            f.write(f"| ${it['id']} | {it['locked_name']} | {it['family']} | ${it['template']} {it['template_name']} | "
                    f"{it['template_name']}'s | {'x2 (spear)' if it['spear'] else ('yes' if True else '')} | "
                    f"{'yes' if 'RUNIC' in fl else 'no'} | {'yes' if 'TWO_HAND' in fl else 'no'} | "
                    f"{'yes' if 'BUSHIDO' in fl else 'no'} | Genji Glove: yes | "
                    f"{'steal on hit (ThiefKnife special)' if it['weapon_special'] == 'STEAL' else ''} |\n")
        f.write("\nNot throwable (Throw excluded under Option C). Offering (4 strikes) and Genji Glove (dual wield) use the "
                "same per-hand animation numbers (emulator O1 / G1). No weapon casts a spell (proc).\n")

    # ------------------------------------------------------------------ fallback
    with w("FALLBACK_EFFECTS_v0.8.md") as f:
        f.write("# TECH v0.8 — BAL-18 fallback effects (D5)\n\nRelics whose locked line names an optional custom-ASM effect ship "
                "with their BAL-18 stat fallback: the locked stat line only (plus a vanilla flag where the v0.7 audit named "
                "one). No new relic ASM in v0.8. The item identity (name, users, slot, source) is unchanged.\n\n"
                "| ID | Relic | Users | Deferred effect (later module) | Running now |\n|---|---|---|---|---|\n")
        for it in items:
            if it["fallback"]:
                f.write(f"| ${it['id']} | {it['locked_name']} | {'/'.join(it['users'])} | {it['fallback']['deferred_effect']} | "
                        f"{it['fallback']['running']} |\n")
        f.write("\nImplemented with existing vanilla flags (not fallbacks): Raider Knife steal-on-hit (ThiefKnife special), "
                "Painter's Lens Sketch rate (Beret bit), Elder's Seal / Magister Robe MP +1/8 (Bard's Hat bit), Legacy of "
                "the Magi MP +1/4 (Minerva bit), Keepsake Ring Doom/Zombie/death immunity (Memento Ring mechanism), Memorial "
                "Band Berserk/Muddle immunity (Peace Ring mechanism), spears' Jump x2 (extended spear flag).\n")

    # ------------------------------------------------------------------ balance audit
    lines = ["# TECH v0.8 — equipment balance audit", "",
             "Method: every production item compared with every vanilla equipment record of the same type that at least one "
             "common character can wear. *Dominates* = at least as good in every number (power/defense, hit/MDef, Vigor, "
             "Speed, Stamina, Mag.Pwr, Evade, MBlock), every feature of the other (elements absorbed/nulled/halved, weapon "
             "element, status immunity, relic bits, weapon special, spell cast) and no extra weakness, and better in one. "
             "Locked stats are not changed by this audit; findings that would need a change are listed for creative review.", ""]
    dom, domd, near = [], [], {}
    for n in N:
        cand = [v for v in V if v["type"] == n["type"] and set(v["users"]) & set(n["users"])]
        dom += [(n, v) for v in cand if dominates(n, v)]
        domd += [(n, v) for v in cand if dominates(v, n)]
        key = (lambda v: abs(v["power"] - n["power"]) + abs(v["hit_mdef"] - n["hit_mdef"])) if n["type"] != "relic" else \
            (lambda v: sum(abs(v[k] - n[k]) for k in NUM) + 10 * len(v["pos"] ^ n["pos"]))
        near[n["id"]] = sorted(cand, key=key)[:2]
    lines += ["## Comparison with the nearest vanilla equivalents", "",
              "| ID | Item | Pwr/Def | Hit/MDef | V/S/St/M | Eva/MBlk | Features | Nearest vanilla (Pwr, Hit/MDef, V/S/St/M, Eva/MBlk, features) |",
              "|---|---|---|---|---|---|---|---|"]
    for n in N:
        nv = "; ".join(f"${v['id']} {v['name']} ({v['power']}, {v['hit_mdef']}, {v['vig']:+d}/{v['spd']:+d}/{v['sta']:+d}/{v['mag']:+d}, "
                       f"{v['evade']}/{v['mblock']}, {', '.join(sorted(v['pos'] | v['neg'])) or '-'})" for v in near[n["id"]])
        lines.append(f"| ${n['id']} | {n['it']['locked_name']} | {n['power']} | {n['hit_mdef']} | {n['vig']:+d}/{n['spd']:+d}/"
                     f"{n['sta']:+d}/{n['mag']:+d} | {n['evade']}/{n['mblock']} | {', '.join(sorted(n['pos'] | n['neg'])) or '-'} | {nv} |")
    def top3(c, t):
        return sorted([v for v in V if v["type"] == t and c in v["users"]], key=lambda v: -v["power"])[:3]
    late = []
    for n, v in dom:
        common = set(n["users"]) & set(v["users"])
        if any(v in top3(c, n["type"]) for c in common) and n["type"] != "relic":
            late.append((n, v, sorted(common)))
    lines += ["", "## Strictly dominant", "",
              f"{len(dom)} (production item, vanilla item) pairs where the production item is at least as good in every "
              "respect. Dominating early / mid-game gear is the intended role of a later, unique signature reward. The "
              "relevant question is dominance over a character's endgame options (the three strongest vanilla items of "
              "that slot the character can wear; Imp-only gear excluded):", ""]
    if late:
        lines += ["| Production item | dominates endgame vanilla | for | note |", "|---|---|---|---|"]
        for n, v, cm in late:
            lines.append(f"| ${n['id']} {n['it']['locked_name']} ({n['power']}) | ${v['id']} {v['name']} ({v['power']}) | "
                         f"{'/'.join(cm)} | locked values; the slot's strongest vanilla item is not dominated (next sections) |")
    else:
        lines.append("None.")
    per = {}
    for n, v in dom:
        per.setdefault(n["id"], []).append(v["name"])
    lines += ["", "Lower-tier dominance per item (count): " + ", ".join(f"${k} {len(x)}" for k, x in sorted(per.items())) + "."]
    lines += ["", "## Strictly dominated (a vanilla item better in every respect)", ""]
    if domd:
        lines += ["| Production item | dominated by vanilla | common users | tier of the vanilla item |", "|---|---|---|---|"]
        for n, v in domd:
            tier = "ultimate / endgame (Illumina, Ragnarok, Excalibur, Paladin Shld...): expected" if v["id"] in (
                "1A", "1B", "1C", "18", "67") else "REVIEW"
            lines.append(f"| ${n['id']} {n['it']['locked_name']} | ${v['id']} {v['name']} | "
                         f"{'/'.join(sorted(set(n['users']) & set(v['users'])))} | {tier} |")
        lines += ["", "No production item is dominated by a same-tier or earlier vanilla item; the only dominating items "
                  "are endgame / ultimate rewards, which a mid-game signature item is allowed to lose to."
                  if all(v["id"] in ("1A", "1B", "1C", "18", "67") for n, v in domd) else "REVIEW the rows marked above."]
    else:
        lines.append("None.")
    # iconic endgame
    ICONIC = ["1A", "1B", "1C", "18", "23", "24", "59", "32", "3C", "40", "9A", "9C", "A2", "64", "67", "68", "81", "83", "CA"]
    lines += ["", "## Iconic endgame equipment is not invalidated", "",
              "| Vanilla | Pwr/Def | best production item of the same type for the same users | Pwr/Def | dominated? |", "|---|---|---|---|---|"]
    for vid in ICONIC:
        v = next((x for x in V if x["id"] == vid), None)
        if v is None:
            continue
        cand = [n for n in N if n["type"] == v["type"] and set(n["users"]) & set(v["users"])]
        if not cand:
            continue
        b = max(cand, key=lambda n: n["power"])
        lines.append(f"| ${v['id']} {v['name']} | {v['power']} | ${b['id']} {b['it']['locked_name']} | {b['power']} | "
                     f"{'YES' if dominates(b, v) else 'no'} |")
    lines += ["", "No production weapon exceeds Battle Power 222 (locked envelope 184-222); Illumina / Ragnarok / Atma "
              "Weapon (255) and the 227-253 spears stay above every production weapon."]
    # optimum
    lines += ["", "## Optimum: which slots move to a new item (highest power / defense per slot, as the vanilla Optimum)", "",
              "| Character | Weapon (vanilla best -> with v0.8) | Shield | Helmet | Armor |", "|---|---|---|---|---|"]
    tot, new = 0, 0
    for c in CHARS:
        cells = []
        for t in ("weapon", "shield", "helmet", "armor"):
            vb = max([v for v in V if v["type"] == t and c in v["users"]], key=lambda v: v["power"], default=None)
            nb = max([n for n in N if n["type"] == t and c in n["users"]], key=lambda v: v["power"], default=None)
            if not vb and not nb:
                cells.append("-"); continue
            tot += 1
            if nb and (not vb or nb["power"] > vb["power"]):
                new += 1
                cells.append(f"{vb['name'] if vb else '-'} ({vb['power'] if vb else 0}) -> **{nb['it']['display_name']} ({nb['power']})**")
            else:
                cells.append(f"{vb['name']} ({vb['power']}) kept")
        lines.append(f"| {c} | " + " | ".join(cells) + " |")
    lines += ["", f"Optimum moves {new} of {tot} character slots to a production item; the rest keep their vanilla best. "
              "Signature items with lower raw power (e.g. Magister Robe, Imperial Mantle, the relic-like helmets) are picked "
              "for their specialisation, not by Optimum."]
    # stacking
    lines += ["", "## Stacking maxima per character (equipment only; Evade / MBlock in %, stats as bonus)", "",
              "FF6 Rev 1 note: the SNES Evade bug makes physical evasion use MBlock, so MBlock is the stacking value that "
              "matters in practice.", "",
              "| Character | max MBlock vanilla | max MBlock vanilla+v0.8 | max Evade vanilla | with v0.8 | max Speed bonus vanilla | with v0.8 |",
              "|---|---|---|---|---|---|---|"]
    def best(c, pool, key):
        tot = 0
        for t in ("weapon", "shield", "helmet", "armor"):
            tot += max([x[key] for x in pool if x["type"] == t and c in x["users"]], default=0)
        rel = sorted([x[key] for x in pool if x["type"] == "relic" and c in x["users"]], reverse=True)[:2]
        return tot + sum(rel)
    flagged = []
    for c in CHARS:
        mb0, mb1 = best(c, V, "mblock"), best(c, V + N, "mblock")
        ev0, ev1 = best(c, V, "evade"), best(c, V + N, "evade")
        sp0, sp1 = best(c, V, "spd"), best(c, V + N, "spd")
        lines.append(f"| {c} | {mb0} | {mb1} | {ev0} | {ev1} | {sp0:+d} | {sp1:+d} |")
        if mb1 > mb0 + 20 or sp1 > sp0 + 4:
            flagged.append(c)
    lines += ["", "Raised by more than +20 MBlock or +4 Speed over the vanilla maximum: " + (", ".join(flagged) or "none") + ".",
              "Speed: the raised peaks reach the vanilla party ceiling (Locke +21 with vanilla gear); MBlock: Terra/Celes "
              "gain +20/+30 over a vanilla peak that is already far above 100%.",
              "", "## Dangerous combinations reviewed", "",
              "* **Shadow evasion** — Moonless (Eva +30, Spd +7), Concord Vest (Eva +20, Spd +4) and Concord Shield (Eva/MBlock +20) "
              "stack Evade, but Evade is the bugged stat; Shadow's MBlock and Speed peaks are in the table above. Not changed (locked).",
              "* **Magic users' MBlock** — Legacy of the Magi (+30), Magister Rod (+20), Concord Shield (+20), Magi Circlet (+10), "
              "Runic Crest / Imperial Mantle / Imperial Saber (+20, Celes/Terra) reach the same band as vanilla Illumina / Force "
              "Shld / Paladin Shld stacks; not above the vanilla ceiling for Terra/Celes (see table).",
              "* **Elemental immunity** — the new items add Fire null (Royal Gear), Fire absorb (Ashen Mail, Ashguard, both "
              "with Ice weakness), Wind half (Falcon Jacket, Gale Pin) and Holy half (Concord Shield). Stacking Ashen Mail + "
              "Ashguard keeps a single Fire absorb and a single Ice weakness; no new item grants absorb/null of Ice, Lightning, "
              "Poison, Earth or Water, so no new full elemental immunity set is possible beyond vanilla (Paladin/Flame/Ice Shld).",
              "* **Relic stacking** — two relics per character: the strongest new pairs are Legacy of the Magi + Maduin's "
              "Locket (Terra: Mag +13, MP +25% twice does not stack beyond the single MP +25% bit) and Doma Crest + "
              "Memorial Band / Master's Cord-type pairs (stat +9/+10). MP bits are flags: two MP +25% relics give +25%. "
              "No new relic copies Offering, Genji Glove, Hyper Wrist, Gem Box or other vanilla multiplier relics.",
              "* **Kefka's Tower / final bosses** — no new item raises a damage multiplier (no Atlas/Earring/Hyper Wrist bit, "
              "no X-Fight / X-Magic, no proc), every new weapon is below 255 power, so the end-game damage ceiling is the "
              "vanilla one.",
              "", "## Unintended caps", "",
              "All bonuses are inside the ItemProp nibble ranges (stats -7..+7, Evade/MBlock 0..50 in steps of 10); the "
              "builder refuses values outside. Speed +7 (Moonless) and Mag +7 (Magister Rod, Concord Brush, Legacy of the "
              "Magi) are at the field maximum and exactly the locked values (no silent clipping).",
              "", "## Changes made by this audit", "",
              "None to locked values. Derived fields were chosen conservatively (family-default hit rates and weapon flags; "
              "the smaller MP bit for 'MP-oriented'; a 4-status subset for Child's Ribbon; half (not null) for every 'resist')."]
    open(os.path.join(out, "EQUIPMENT_BALANCE_AUDIT_v0.8.md"), "w").write("\n".join(lines) + "\n")
    print("written to", out, "| dominant:", len(dom), "dominated:", len(domd))


if __name__ == "__main__":
    main(*sys.argv[1:3])
