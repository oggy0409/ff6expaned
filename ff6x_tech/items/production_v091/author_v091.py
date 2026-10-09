#!/usr/bin/env python3
"""Authoring script for the TECH v0.9.1 item data alignment (run once; the JSON files it writes are the source of
truth, validated by patches/consumables_v091.py and patches/equipment_v08.py at every build).

Input : items/production_v08/equipment.json, items/production_v09/{consumables,rare_items}.json (accepted v0.9 data)
Output: items/production_v091/{equipment,consumables,rare_items,ext_shops}.json
Every change is driven by the approved decisions (docs/design/DESIGN_DECISIONS_v1.0.md, D-03 .. D-20) and the
cross-check rows (docs/design/V09_DATA_CROSSCHECK_v1.0.csv); the row / decision is recorded in each item's
"v091_changes". Item IDs, names and save layout are unchanged.
"""
import copy, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def load(p):
    return json.load(open(os.path.join(ROOT, p)))


def dump(name, obj):
    with open(os.path.join(HERE, name), "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------------------------- equipment
eq = load("items/production_v08/equipment.json")
eq = copy.deepcopy(eq)
eq["version"] = "TECH v0.9.1"
eq["_comment"] = ("TECH v0.9.1 production signature equipment $100-$126 (v0.8 data + the approved v0.9.1 alignment: "
                  "D-03/DA-01 Leo's Blade, D-19 Darill's Coin, D-20 Tempered Edge / Doma Edge / Sandpiercer, "
                  "X0223 Magister Robe arc). Only source metadata and the Darill's Coin record change.")
by = {it["code"]: it for it in eq["items"]}


def acq(it, **kw):
    a = it["acquisition"]
    a.pop("smith", None)
    a["gp_cost"] = None
    a.update(kw)


t = by["EQ-W01"]                                      # Tempered Edge
acq(t, source_type="quest_reward", planned_source="The Empty Forge (Narshe) - quest reward; never sold",
    future_event_symbol="EV_REWARD_EMPTY_FORGE_TEMPERED_EDGE", conditions=["PREREQ_EMPTY_FORGE_DONE"])
t["v091_changes"] = ["D-20: first and only copy = The Empty Forge reward; removed from smith purchase (no GP cost); "
                     "never sold in the Reopened Narshe Forge shop"]

t = by["EQ-W03"]                                      # Leo's Blade
acq(t, source_type="event_chest",
    planned_source="Records Vault concealed officer locker (DA-01: all Leo records read + Names Room done)",
    future_event_symbol="EV_CHEST_RECORDS_VAULT_LEOS_BLADE",
    conditions=["PREREQ_LEO_RECORDS_ALL", "PREREQ_NAMES_ROOM_DONE"])
t["v091_changes"] = ["D-03 / DA-01: optional exploration reward, independent of Preserve / Burn"]

t = by["EQ-W05"]                                      # Sandpiercer
acq(t, source_type="event_chest", planned_source="Figaro Foundry - one-time chest / event reward (not a GP purchase)",
    future_event_symbol="EV_CHEST_FIGARO_FOUNDRY_SANDPIERCER", conditions=["PREREQ_FIGARO_FOUNDRY"])
t["v091_changes"] = ["D-20 / X0068-X0069: one-time chest inside the Figaro Foundry; GP cost removed"]

t = by["EQ-W08"]                                      # Doma Edge
acq(t, source_type="quest_reward", planned_source="Cyan arc / Doma reconstruction reward (no second copy in v1.x)",
    future_event_symbol="EV_REWARD_DOMA_RECONSTRUCTION_DOMA_EDGE", conditions=["PREREQ_DOMA_RECONSTRUCTION"])
t["v091_changes"] = ["D-20 / X0112: first and only copy = Cyan/Doma reconstruction reward; no smith purchase"]

t = by["EQ-A03"]                                      # Magister Robe
t["acquisition"].update(planned_source="Archive Guardian (Forgotten Age)", conditions=["PREREQ_FORGOTTEN_AGE"])
t["v091_changes"] = ["X0223-X0224: arc binding First Magi -> Forgotten Age (Bosses sheet)"]

t = by["EQ-R05"]                                      # Darill's Coin
t["mag_pwr"] = 2
t["desc"] = "Darill's Coin{n}Speed, Mag pwr, MBlock up"
t["fallback"]["running"] = "BAL-18 stat fallback (Master Design Bible v1.0 s9): Speed +5, Magic +2, M.Evade +20%"
t["v091_changes"] = ["D-19 / X0405: fallback = Speed +5, Magic +2, M.Evade +20% (Mag +2 added); description updated"]
dump("equipment.json", eq)

# ---------------------------------------------------------------------------------------------- consumables
cv = load("items/production_v09/consumables.json")
cons = copy.deepcopy(cv)
cons["_comment"] = ("TECH v0.9.1 production consumables $127-$12E: locked effects of Master Design Bible v1.0 s18 "
                    "(D-16 / D-17 exact values). fixed_hp / hybrid_element / shop_cap use the v0.9.1 extended-consumable "
                    "engine path (asm/item_v091/v091.s); every other effect is vanilla ItemProp data.")
c = {it["code"]: it for it in cons["items"]}


def not_sold(it, **acq_kw):
    it["sellable"] = False
    it["sold_in_shops"] = False
    it["price"] = 2
    it["acquisition"] = dict(acq_kw, one_time=True)


it = c["CN-01"]                                       # Gaia Tonic
it.update(desc="Restores 1500 HP{n}and grants Regen", targeting="ONE_ALLY", price=2000)
it["effect"] = {"restore_hp": True, "power": 255, "fixed_amount": 1500, "sets_status": ["REGEN"], "undead_invert": True}
it["acquisition"] = {"source_type": "shop", "planned_source": "Rebuilt Mobliz shop (ext shop $80); "
                     "also 'Seeds for Tomorrow' quest reward x3", "future_event_symbol": "EXT_SHOP_REBUILT_MOBLIZ",
                     "conditions": "PREREQ_MOBLIZ_REBUILT", "one_time": False, "gp_cost": 2000,
                     "other_rewards": [{"source": "Seeds for Tomorrow", "quantity": 3,
                                        "future_event_symbol": "EV_REWARD_SEEDS_FOR_TOMORROW_GAIA_TONIC"}]}
it["derived"] = ["price 2000 (Potion 300 for 250 HP; single-target 1500 HP + Regen)",
                 "power byte 255 = nominal (the v0.9.1 fixed-heal path replaces the amount; 0 would skip the heal)",
                 "anim template Potion", "Regen is set in battle; in the field menu only the HP is restored "
                 "(vanilla field item code has no status-set)"]
it["v091_changes"] = ["D-16 / X0504-X0505: one ally, exactly 1500 HP, sets Regen", "X0507: sold at Rebuilt Mobliz"]

it = c["CN-02"]                                       # Aether Flask
it["effect"] = {"restore_mp": True, "power": 100}
it["desc"] = "Aether Flask{n}Restores 100 MP"
it["derived"] = ["not sold (MP economy)", "anim template Ether", "display name AetherFlask (12-char field)",
                 "power 100 = exactly 100 MP (the Item command disables the damage variance; measured in battle and "
                 "field)"]
it["v091_changes"] = ["X0516: MP 250 -> 100 (locked)"]

c["CN-03"]["v091_changes"] = ["unchanged (D-16: keep)"]

it = c["CN-04"]                                       # Null Dust
it["effect"] = {"removes_status": True, "status": ["VANISH", "IMAGE", "BERSERK", "REGEN", "SLOW", "HASTE", "STOP",
                                                   "SHELL", "SAFE", "REFLECT", "LIFE3", "FLOAT"]}
it["desc"] = "Dispels one target{n}(battle only)"
not_sold(it, source_type="event_chest", planned_source="story chests / arc rewards (not in any locked shop list)",
         future_event_symbol="EV_CHEST_NULL_DUST", conditions="PREREQ_TBD_ARC_DESIGN")
it["derived"] = ["not sold (no locked shop lists it; Bible s19)", "anim template Remedy",
                 "targeting: one target, enemy by default (vanilla Dispel targeting $41)"]
it["v091_changes"] = ["D-17 / X0540: exact vanilla Dispel removal set (spell $2C status bytes 10 14 FE 84)",
                      "X0543: removed from the shops"]

it = c["CN-05"]                                       # Iron Ration
it["effect"] = {"restore_hp": True, "power": 255, "fixed_amount": 600, "undead_invert": True}
it["desc"] = "Iron Ration{n}Restores 600 HP"
it["price"] = 300
it["acquisition"] = {"source_type": "shop", "planned_source": "Rebuilt Mobliz shop (ext shop $80)",
                     "future_event_symbol": "EXT_SHOP_REBUILT_MOBLIZ", "conditions": "PREREQ_MOBLIZ_REBUILT",
                     "one_time": False, "gp_cost": 300}
it["derived"] = ["price 300 ('cheap': the Potion price, 600 HP)", "power byte 255 = nominal (fixed-heal path)",
                 "anim template Dried Meat"]
it["v091_changes"] = ["D-16 / X0552: exactly 600 HP; the unlocked Poison cure removed", "X0555: Rebuilt Mobliz"]

it = c["CN-06"]                                       # Remedy+
it["effect"] = {"removes_status": True, "status": ["BLIND", "POISON", "IMP", "PETRIFY", "SILENCE", "SAP", "ZOMBIE"]}
it["desc"] = "Remedy+{n}Remedy and cures Zombie"
it["rarity"] = "rare"
not_sold(it, source_type="event_chest", planned_source="rare find / arc rewards (not sold)",
         future_event_symbol="EV_CHEST_REMEDY_PLUS", conditions="PREREQ_TBD_ARC_DESIGN")
it["derived"] = ["anim template Remedy", "not sold"]
it["v091_changes"] = ["X0564: vanilla Remedy set (rec bytes 65 48) + Zombie", "X0567 / X0570: rare, not sold"]

it = c["CN-07"]                                       # Beacon Flare
it["effect"] = {"power": 255, "element": ["FIRE"], "removes_status": True, "status": ["VANISH"]}
it["desc"] = "Fire damage to all foes{n}and reveals the hidden"
it["derived"] = ["power 255 (no level scaling; halved over several targets)", "not sold",
                 "anim: vanilla Fire 2 spell animation", "display name BeaconFlare (12-char field)",
                 "'invisible' = VANISH (D-17; Image is not removed)"]
it["v091_changes"] = ["D-17 / X0576: Fire damage to all + removes VANISH in the same item action"]

it = c["CN-08"]                                       # Magitek Cell
it.update(targeting="ONE_ENEMY", usable_field=False, usable_battle=True, price=1500, sellable=True,
          sold_in_shops=True, anim_template="SPELL:BOLT_BEAM", rarity="rare", shop_cap=3)
it["effect"] = {"power": 255, "element": ["LIGHTNING"], "hybrid_element": "LIGHTNING", "fixed_amount": 800}
it["desc"] = "Magitek Cell{n}Lightning + raw tech damage"
it["acquisition"] = {"source_type": "shop", "planned_source": "Figaro Foundry shop after the Celes arc "
                     "(ext shop $84 = Foundry stock once EXP_CELES_DONE is set; $83 before)",
                     "future_event_symbol": "EXT_SHOP_FIGARO_FOUNDRY_POST_CELES", "conditions": "EXP_CELES_DONE",
                     "one_time": False, "gp_cost": 1500}
it["derived"] = ["total damage 800 before the split (fixed, no variance): 400 Lightning + 400 non-elemental; "
                 "Lightning-weak 1200, Lightning-null 400, Lightning-absorb 0 (400 - 400); ignores M.Def like every "
                 "item; conservative vs Bolt 3 / Drill in the World of Ruin",
                 "price 1500 (Figaro tool shops use price modifier 6: half price when Edgar leads -> 750)",
                 "shop cap 3: owned (inventory) + bought <= 3", "anim: vanilla Bolt Beam (Magitek) animation",
                 "not a spell: Item command, no MP, not reflectable / Runic-absorbable (vanilla item rules)"]
it["v091_changes"] = ["D-17 / X0588-X0593: one enemy; Lightning + non-elemental halves in one item action; "
                      "sold only at the Figaro Foundry after EXP_CELES_DONE; hold/buy at most 3"]
dump("consumables.json", cons)

# ---------------------------------------------------------------------------------------------- rare items
rv = copy.deepcopy(load("items/production_v09/rare_items.json"))
rv["_comment"] = ("TECH v0.9.1 FF6X key items (rare ids 20-24): v0.9 data with the recovered locked sources "
                  "(Creative Source Recovery v1.0, rows X0599-X0636). Only the Triune Sigil description changes text.")
r = {x["code"]: x for x in rv["rare_items"]}
GATE = "First Magi gate (one of three sigils; all three + the endgame trigger open it, D-25)"
x = r["KI-01"]
x["story_arc"] = "ARC-6 Setzer"
x["acquisition"].update(planned_source="WOB-C scene (Blackjack, before the Floating Continent); "
                        "if missed: found in the Falcon cabin", prerequisite_flags=["PREREQ_WOB_C_SCENE"])
x["function"] = "unlocks the Last Race (Setzer arc); optional (CAN-022)"
x["v091_changes"] = ["X0600 / X0602: source and function"]
x = r["KI-02"]
x["story_arc"] = "ARC-7A Forgotten Age (Sanctuary of Concord)"
x["ending_dependency"] = GATE
x["v091_changes"] = ["X0610: one of three sigils, not a Triune prerequisite"]
x = r["KI-03"]
x["story_arc"] = "ARC-7B Forgotten Age (Field of Cinders)"
x["acquisition"].update(planned_source="Empyreal Chimera boss, Field of Cinders",
                        prerequisite_flags=["PREREQ_FIELD_OF_CINDERS"])
x["ending_dependency"] = GATE
x["v091_changes"] = ["X0616-X0618: recovered source / arc; one of three sigils"]
x = r["KI-04"]
x["story_arc"] = "ARC-7C Forgotten Age (Shrine of the Silent Three)"
x["desc"] = "Sigil of the Shrine{n}of the Silent Three."
x["acquisition"].update(planned_source="Triune Sentinel boss, Shrine of the Silent Three",
                        prerequisite_flags=["PREREQ_SHRINE_OF_SILENT_THREE"])
x["consumed"] = "no"
x["ending_dependency"] = GATE
x["derived"] = ["description (text not locked; the locked fact is that the Triune Sigil is its own sigil)"]
x["v091_changes"] = ["X0624-X0628: own sigil from the Triune Sentinel; no Concord + Cinder prerequisite; description"]
x = r["KI-05"]
x["story_arc"] = "ARC-8 First Magi (Hope: Broken Seal)"
x["acquisition"].update(planned_source="optional trophy from the Vael fight (Scene V07)",
                        prerequisite_flags=["PREREQ_VAEL_DEFEATED"])
x["v091_changes"] = ["X0632-X0633: source / arc"]
dump("rare_items.json", rv)

# ---------------------------------------------------------------------------------------------- shops
shops = {"_comment": ("TECH v0.9.1 extended shops (Master Design Bible v1.0 s19, D-18). XShopProp ids $80+, 8 entries, "
                      "9-bit item ids; vanilla shops $00-$7F byte-exact. No ultimate gear; vanilla prices."),
         "shops": [
    {"shop_id": "80", "symbol": "EXT_SHOP_REBUILT_MOBLIZ", "type": 5, "price_mod": 0,
     "items": ["12B", "F5", "F0", "127", "8D"],
     "note": "Rebuilt Mobliz: Iron Ration, Remedy, Fenix Down (Phoenix Down), Gaia Tonic, Gaia Gear",
     "derived": ["vendor type (items + armor)", "order as listed in s19"]},
    {"shop_id": "81", "symbol": "EXT_SHOP_NARSHE_FORGE", "type": 5, "price_mod": 0,
     "items": ["0D", "0E", "0F", "5D", "5F"],
     "note": "Reopened Narshe Forge: Flame Sabre, Blizzard, ThunderBlade (elemental blades) + Gold Shld, "
             "Diamond Shld. Tempered Edge is NOT sold (D-20: Empty Forge reward only)",
     "derived": ["shield choice (Gold / Diamond: practical mid-late shields, no Crystal / Aegis / Genji)"]},
    {"shop_id": "82", "symbol": "EXT_SHOP_REBUILT_DOMA", "type": 5, "price_mod": 0,
     "items": ["2D", "2E", "2F", "8A", "73", "AB", "AC", "AD"],
     "note": "Rebuilt Doma: Forged, Tempest, Murasame (Cyan katanas), Ninja Gear, Head Band (ashigaru-style "
             "existing gear) + Fire Skean, Water Edge, Bolt Edge (scrolls). No Doma Edge (D-20)",
     "derived": ["gear choice for 'Ashigaru-style existing gear' (no Masamune / Strato / Sky Render)"]},
    {"shop_id": "83", "symbol": "EXT_SHOP_FIGARO_FOUNDRY", "type": 3, "price_mod": 6,
     "items": ["AA", "A3", "A4", "A5", "A7", "A8"],
     "note": "Figaro Foundry before EXP_CELES_DONE: the canonical tools (vanilla shop $54 contents, type and "
             "price modifier 6 = half price for Edgar)", "derived": []},
    {"shop_id": "84", "symbol": "EXT_SHOP_FIGARO_FOUNDRY_POST_CELES", "type": 3, "price_mod": 6,
     "items": ["AA", "A3", "A4", "A5", "A7", "A8", "12E"],
     "note": "Figaro Foundry once EXP_CELES_DONE is set: the canonical tools + limited Magitek Cell (cap 3). "
             "Technical split of the logical shop $83: the Foundry clerk event opens $84 when EXP_CELES_DONE is set",
     "derived": ["technical shop id $84 (the vanilla shop command has no per-entry condition)"]},
]}
dump("ext_shops.json", shops)
print("wrote items/production_v091/{equipment,consumables,rare_items,ext_shops}.json")
