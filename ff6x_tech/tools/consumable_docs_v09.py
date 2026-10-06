#!/usr/bin/env python3
"""TECH v0.9: generate the consumable / rare-item documents from the canonical sources and the clean Rev 1 ROM.

  CONSUMABLE_MASTER_TABLE_v0.9.{json,csv,md}     CONSUMABLE_ACQUISITION_MAP_v0.9.{json,md}
  CONSUMABLE_BALANCE_AUDIT_v0.9.md               RARE_ITEM_MASTER_TABLE_v0.9.{json,md}
  RARE_ITEM_ACQUISITION_MAP_v0.9.{json,md}

usage: consumable_docs_v09.py <clean_rev1.sfc> <outdir>
"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from patches import item_v071 as IV, consumables_v09 as CV
from ff6x.hirom import snes_to_pc

CONS = json.load(open(os.path.join(HERE, "items/production_v09/consumables.json")))["items"]
RARE = json.load(open(os.path.join(HERE, "items/production_v09/rare_items.json")))["rare_items"]
SHOPS = json.load(open(os.path.join(HERE, "items/production_v09/ext_shops.json")))["shops"]
TGT = {v: k for k, v in CV.TARGETING.items()}
STATUS_BY = {v: k for k, v in CV.STATUS.items()}


def ch(c):
    if 0x80 <= c <= 0x99: return chr(65 + c - 0x80)
    if 0x9A <= c <= 0xB3: return chr(97 + c - 0x9A)
    if 0xB4 <= c <= 0xBD: return chr(48 + c - 0xB4)
    return {0xC0: "/", 0xC3: "'", 0xC4: "-", 0xC5: ".", 0xC6: ",", 0xCA: "+", 0xBE: "!", 0xBF: "?"}.get(c, " ")


def van_name(clean, i):
    a = snes_to_pc(IV.VAN_NAME) + 13 * i
    return "".join(ch(c) for c in clean[a + 1:a + 13]).strip()


def effect_text(rec):
    f, p = rec[19], rec[20]
    parts = []
    if f & 0x08:
        parts.append(f"HP +{p}/16 max" if f & 0x80 else f"HP +{p}")
    if f & 0x10:
        parts.append(f"MP +{p}/16 max" if f & 0x80 else f"MP +{p}")
    st = [STATUS_BY[(o, b)] for o in range(21, 25) for b in (1, 2, 4, 8, 16, 32, 64, 128) if rec[o] & b]
    if f & 0x20 and st:
        parts.append("cures " + "/".join(st))
    elif st:
        parts.append("inflicts " + "/".join(st))
    if not f & 0x38 and p:
        el = [k for k, v in CV.ELEMENT.items() if rec[15] & v]
        parts.append(f"damage {p}" + (f" ({'/'.join(el)})" if el else ""))
    if rec[27] != 0xFF:
        parts.append(f"special {rec[27]:02X}")
    if f & 0x02:
        parts.append("undead inverted")
    return "; ".join(parts) or "-"


def usage(rec):
    u = []
    if rec[0] & 0x20: u.append("battle")
    if rec[0] & 0x40: u.append("field")
    return "+".join(u) or "-"


def main(clean_path, out):
    clean = open(clean_path, "rb").read()
    rows = []
    for it in CONS:
        rec = CV.compose(it)
        i = int(it["id"], 16)
        rows.append({"id": f"${i:03X}", "code": it["code"], "symbol": it["symbol"], "locked_name": it["locked_name"],
                     "display_name": it["display_name"], "category": "consumable", "icon": "blank (as vanilla items)",
                     "description": it["desc"].replace("{n}", " / "), "use": usage(rec),
                     "targeting": f"{it['targeting']} (${rec[14]:02X})", "effect": effect_text(rec),
                     "effect_source": it["effect"], "power": rec[20], "flags19": f"${rec[19]:02X}",
                     "status_bytes_21_24": " ".join(f"{rec[o]:02X}" for o in range(21, 25)),
                     "price": it["price"], "sold": it["sold_in_shops"], "sellable": it["sellable"],
                     "sell_price": it["price"] // 2 if it["sellable"] else None, "rarity": it["rarity"],
                     "quantity_rule": it["quantity"], "animation": it["anim_template"] if it["anim_template"].startswith("SPELL")
                     else f"item ${it['anim_template']} ({van_name(clean, int(it['anim_template'], 16))})",
                     "steal": False, "drop": False, "metamorph": False, "colosseum_wager": False, "throwable": False,
                     "equippable": False, "enemy_use": False, "low_byte_alias": f"${i & 0xFF:02X} {van_name(clean, i & 0xFF)} "
                     "(never battle-usable; separate entry everywhere)",
                     "acquisition": it["acquisition"], "derived": it["derived"], "record": rec.hex(" ").upper()})
    json.dump({"_comment": "TECH v0.9 consumables $127-$12E (generated from items/production_v09/consumables.json). "
               "Locked: names. Every other field DERIVED (see 'derived').", "consumables": rows},
              open(os.path.join(out, "CONSUMABLE_MASTER_TABLE_v0.9.json"), "w"), indent=1)
    keys = ["id", "code", "symbol", "locked_name", "display_name", "use", "targeting", "effect", "power", "price", "sold",
            "sellable", "sell_price", "rarity", "animation", "low_byte_alias", "description", "record"]
    with open(os.path.join(out, "CONSUMABLE_MASTER_TABLE_v0.9.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(keys + ["acquisition", "derived"])
        for r in rows:
            w.writerow([r[k] for k in keys] + [json.dumps(r["acquisition"]), " | ".join(r["derived"])])
    md = ["# CONSUMABLE MASTER TABLE — TECH v0.9", "",
          "Generated from `items/production_v09/consumables.json` (single source of truth; `tools/consumable_docs_v09.py`).",
          "**Locked** (ITEM_ARCHITECTURE_DECISION_v0.7.md §2, from the Creative Lock): the 8 names and that some are sold in "
          "rebuilt shops. **Every other field is DERIVED** (the Creative Lock / Tech Gate spreadsheets are not in the "
          "project) and listed per item under *Derived*; these need creative confirmation.", "",
          "| id | code | name (display) | use | targeting | effect (record) | price | sold / sell | animation |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['code']} | {r['locked_name']} ({r['display_name']}) | {r['use']} | {r['targeting']} | "
                  f"{r['effect']} | {r['price'] if r['sold'] else '—'} | "
                  f"{'yes / ' + str(r['sell_price']) if r['sold'] else 'no / no'} | {r['animation']} |")
    md += ["", "Common to all 8: blank icon (as vanilla items), quantity 1–99 per stack (vanilla rule), not stealable, "
           "not dropped, not a Metamorph result, not a Colosseum wager, not throwable, not equippable, never used by "
           "enemies (exclusion rule v0.9, validated by the builder). The vanilla item with the same low byte is a katana "
           "($27–$2E) that the Item command can never use, so the battle code identifies the consumable without ambiguity.", ""]
    for r in rows:
        md += [f"## {r['id']} {r['locked_name']} ({r['code']}, `{r['symbol']}`)", "",
               f"* Description: *{r['description']}*", f"* Record (30 bytes): `{r['record']}`",
               f"* Acquisition: {r['acquisition']['source_type']} — {r['acquisition']['planned_source']} "
               f"(`{r['acquisition']['future_event_symbol']}`, {r['acquisition']['conditions']}, "
               f"{'one-time' if r['acquisition']['one_time'] else 'repeatable (shop)'})",
               "* Derived: " + "; ".join(r["derived"]), ""]
    open(os.path.join(out, "CONSUMABLE_MASTER_TABLE_v0.9.md"), "w").write("\n".join(md))
    # ---------------------------------------------------------------- acquisition map
    acq = {"consumables": [{"id": r["id"], "name": r["locked_name"], **r["acquisition"]} for r in rows],
           "extended_shops": SHOPS,
           "excluded_channels": {"steal": "none", "drop": "none", "metamorph": "none", "colosseum": "never a wager / prize",
                                 "throw": "never throwable"}}
    json.dump(acq, open(os.path.join(out, "CONSUMABLE_ACQUISITION_MAP_v0.9.json"), "w"), indent=1)
    md = ["# CONSUMABLE ACQUISITION MAP — TECH v0.9", "",
          "Locked: *some consumables are sold in rebuilt shops*. Which ones, the shops and every other source are DERIVED "
          "placements for future story / reconstruction events (no story event is implemented in v0.9 — hard stop). The QA "
          "build reaches the two extended shops from the QA hub.", "",
          "| id | name | source | planned source | event / shop symbol | conditions | one-time | GP |", "|---|---|---|---|---|---|---|---|"]
    for a in acq["consumables"]:
        md.append(f"| {a['id']} | {a['name']} | {a['source_type']} | {a['planned_source']} | `{a['future_event_symbol']}` | "
                  f"{a['conditions']} | {'yes' if a['one_time'] else 'no'} | {a.get('gp_cost') or '—'} |")
    md += ["", "## Extended shops (XShopProp ids $80+, event command $9B)", "",
           "| shop | symbol | items (9-bit ids) | note |", "|---|---|---|---|"]
    for s in SHOPS:
        md.append(f"| ${s['shop_id']} | `{s['symbol']}` | {', '.join('$' + x for x in s['items'])} | {s['note']} |")
    md += ["", "Excluded channels (validated): Steal, Drop, Metamorph, Colosseum (wager and prize), Throw. Enemies never use "
           "them. Not equippable. The 4 sold consumables can be sold back (price / 2); the 4 unsold ones cannot be sold.", ""]
    open(os.path.join(out, "CONSUMABLE_ACQUISITION_MAP_v0.9.md"), "w").write("\n".join(md))
    # ---------------------------------------------------------------- balance audit
    van = []
    for i in range(0xE7, 0x100):
        a = snes_to_pc(IV.VAN_PROP) + 30 * i
        rec = clean[a:a + 30]
        if rec[0] & 7 != 6:
            continue
        van.append((i, van_name(clean, i), usage(rec), TGT.get(rec[14], f"${rec[14]:02X}"), effect_text(rec),
                    rec[28] | rec[29] << 8))
    md = ["# CONSUMABLE BALANCE AUDIT — TECH v0.9", "",
          "Every v0.9 consumable compared with the vanilla consumables (records read from the clean Rev 1 ROM). Effects run "
          "through the vanilla item code, so the vanilla rules apply: items have no level scaling (damage / healing = "
          "power with the usual random variance), **power is halved when an item hits several targets**, fractions are "
          "in 16ths of max HP / MP. All values are DERIVED (no locked numbers exist for the consumables).", "",
          "## Vanilla reference", "", "| id | name | use | targeting | effect | price |", "|---|---|---|---|---|---|"]
    for i, n, u, t, e, p in van:
        md.append(f"| ${i:02X} | {n} | {u} | {t} | {e} | {p} |")
    md += ["", "## v0.9 consumables", "", "| id | name | use | targeting | effect | per-target effect | price | position |",
           "|---|---|---|---|---|---|---|---|"]
    pos = {"127": ("~120 HP x party (battle, power 240 halved); 240 on one member in the field", "party heal between Potion "
                   "(250 one target) and Megalixir; cheaper than 4 Potions (1200) only in action economy — 1500 GP keeps it a "
                   "convenience, not a replacement"),
           "128": ("MP +250", "between Ether (150) and X-Ether (full); not sold (MP economy unchanged)"),
           "129": ("revive + 8/16 max HP", "Fenix Down (2/16) upgrade; boss reward only, not sold"),
           "12A": ("removes Regen/Haste/Shell/Safe/Reflect/Float from one target", "no vanilla item does this (Dispel-like); "
                   "battle only; 800 GP"),
           "12B": ("HP +200 + cures Poison", "between Potion (250) and Dried Meat (150) with an Antidote; 250 GP (Potion 300)"),
           "12C": ("cures Blind/Zombie/Poison/Imp/Petrify/Condemned/Mute/Berserk/Muddle/Sap/Sleep/Slow/Stop",
                   "Remedy (Blind/Poison/Imp/Petrify/Mute/Sap) + the rest; 3000 GP vs Remedy 1000; late shop"),
           "12D": ("Fire damage ~127 each (2+ enemies) / ~255 (one), x2 vs Fire-weak", "comparable to an early Fire 2; quest "
                   "reward, not sold"),
           "12E": ("MP +~60 x party (power 120 halved)", "party Ether-lite; reward only, not sold")}
    for r in rows:
        k = r["id"][1:]
        md.append(f"| {r['id']} | {r['locked_name']} | {r['use']} | {r['targeting']} | {r['effect']} | {pos[k][0]} | "
                  f"{r['price'] if r['sold'] else 'not sold'} | {pos[k][1]} |")
    md += ["", "## Findings", "",
           "* No consumable exceeds the vanilla ceiling: Megalixir / Elixir (full HP+MP) and X-Ether remain the strongest "
           "restores; Phoenix Ash is stronger than Fenix Down but not purchasable.",
           "* The sold consumables (Gaia Tonic, Iron Ration, Null Dust, Remedy+) are priced at or above the vanilla item "
           "they compete with; the strong ones (Aether Flask, Phoenix Ash, Beacon Flare, Magitek Cell) are not sold.",
           "* Beacon Flare is the only offensive consumable usable with the Item command; its damage is capped by the item "
           "formula (power 255, no level scaling), so it never outscales magic.",
           "* Multi-target halving is a vanilla engine rule; the party items (Gaia Tonic, Magitek Cell) were given twice the "
           "intended per-member power so that each member receives the intended amount in battle. In the field menu "
           "(one member) Gaia Tonic heals the full 240.",
           "* Key items have no combat stats (validated: `combat_stats` must be null).",
           "* Review items for creative confirmation: all prices, Gaia Tonic field behaviour (one member), Null Dust "
           "function, Beacon Flare power, Remedy+ price/coverage.", ""]
    open(os.path.join(out, "CONSUMABLE_BALANCE_AUDIT_v0.9.md"), "w").write("\n".join(md))
    # ---------------------------------------------------------------- rare items
    van_r = []
    for j in range(20):
        a = snes_to_pc(0xCEFBA0) + 13 * j
        van_r.append({"rare_id": j, "name": "".join(ch(c) for c in clean[a:a + 13]).strip(), "storage": f"event bit ${0x1D0 + j:03X}",
                      "source": "vanilla (unchanged)"})
    rr = []
    for r in RARE:
        j = r["rare_id"]
        rr.append({"rare_id": j, "code": r["code"], "symbol": r["symbol"], "locked_name": r["locked_name"],
                   "display_name": r["display_name"], "description": r["desc"].replace("{n}", " / "),
                   "story_arc": r["story_arc"], "acquisition": r["acquisition"], "consumed": r["consumed"],
                   "ending_dependency": r["ending_dependency"], "combat_stats": None,
                   "storage": f"XRARE $1E{0x1D + ((j - 20) >> 3):02X} bit {(j - 20) & 7}",
                   "event_api": {"give": f"$69 {j:02X}", "take": f"$6D {j:02X}", "has": f"$6E {j:02X} sl sh"},
                   "derived": r["derived"]})
    json.dump({"_comment": "TECH v0.9 rare items: logical rare ids 0-19 vanilla, 20-24 the 5 locked key items, 25-51 "
               "reserved (32 FF6X ids = capacity). Locked: the 5 names.", "vanilla": van_r, "ff6x": rr,
               "reserved": {"ids": "25-51", "count": 27, "qa_fillers": "items/qa_v09/qa_rare_items.json (QA build only)"}},
              open(os.path.join(out, "RARE_ITEM_MASTER_TABLE_v0.9.json"), "w"), indent=1)
    md = ["# RARE / KEY ITEM MASTER TABLE — TECH v0.9", "",
          "Registry: `items/production_v09/rare_items.json` (source-controlled; validated by the builder). Logical rare ids "
          "0–19 are the vanilla rare items (unchanged, event bits $1D0–$1E3); **20–51 are FF6X rare items (32 = capacity)**: "
          "20–24 the 5 locked key items, 25–51 reserved (the QA build fills them with placeholders to prove the capacity). "
          "Locked: the 5 names. Story arc, source, prerequisites, consumption and ending dependency are DERIVED from the "
          "names / the locked concept list and need creative confirmation.", "",
          "| rare id | code | name (13-char display) | arc | acquisition (symbol) | prerequisite | one-time | consumed | ending | storage |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rr:
        a = r["acquisition"]
        md.append(f"| {r['rare_id']} | {r['code']} | {r['locked_name']} ({r['display_name']}) | {r['story_arc']} | "
                  f"{a['planned_source']} (`{a['future_event_symbol']}`) | {', '.join(a['prerequisite_flags'])} | "
                  f"{'yes' if a['one_time'] else 'no'} | {r['consumed']} | {r['ending_dependency']} | {r['storage']} |")
    md += ["", "Descriptions:", ""] + [f"* {r['rare_id']} {r['locked_name']}: *{r['description']}*" for r in rr]
    md += ["", "Key items have no combat stats. Vanilla rare items (0–19): " + ", ".join(f"{v['rare_id']} {v['name']}" for v in van_r), ""]
    open(os.path.join(out, "RARE_ITEM_MASTER_TABLE_v0.9.md"), "w").write("\n".join(md))
    acqr = {"key_items": [{"rare_id": r["rare_id"], "name": r["locked_name"], **r["acquisition"], "consumed": r["consumed"]}
                          for r in rr],
            "bindings": "every key item has exactly one future event symbol EV_RARE_*; no orphan (validated)"}
    json.dump(acqr, open(os.path.join(out, "RARE_ITEM_ACQUISITION_MAP_v0.9.json"), "w"), indent=1)
    md = ["# RARE / KEY ITEM ACQUISITION MAP — TECH v0.9", "",
          "One binding per key item (future event symbol, prerequisite flags, one-time). The events themselves are story "
          "content (hard stop for v0.9); they will use the v0.9 event API (`RARE_ITEM_EVENT_API_v0.9.md`).", "",
          "| rare id | name | planned source | event symbol | prerequisites | one-time | consumed |", "|---|---|---|---|---|---|---|"]
    for a in acqr["key_items"]:
        md.append(f"| {a['rare_id']} | {a['name']} | {a['planned_source']} | `{a['future_event_symbol']}` | "
                  f"{', '.join(a['prerequisite_flags'])} | {'yes' if a['one_time'] else 'no'} | {a['consumed']} |")
    md += ["", "Triune Sigil (23): its prerequisite is owning both Concord Sigil (21) and Cinder Sigil (22) — an event checks "
           "`HAS_RARE 21` and `HAS_RARE 22` before `GIVE_RARE 23`. The two sigils are kept (consumption is not locked).", ""]
    open(os.path.join(out, "RARE_ITEM_ACQUISITION_MAP_v0.9.md"), "w").write("\n".join(md))
    print("docs written")


if __name__ == "__main__":
    main(*sys.argv[1:3])
