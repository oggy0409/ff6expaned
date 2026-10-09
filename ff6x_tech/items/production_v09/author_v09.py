#!/usr/bin/env python3
"""Authoring script for the TECH v0.9 canonical sources (run once; the JSON files are the source of truth).
Locked (ITEM_ARCHITECTURE_DECISION_v0.7.md section 2, from the Creative Lock): the 8 consumable NAMES and that "some
are sold in rebuilt shops"; the 5 key-item NAMES. The original Creative Lock / Tech Gate spreadsheets are not in the
project (README_TECH_v0.9 section 0), so every other field is DERIVED and listed per item in "derived"."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

def cons(i, code, sym, name, disp, desc, use, tgt, eff, price, sold, rarity, anim, src, derived):
    return {"id": f"{i:03X}", "code": code, "symbol": sym, "locked_name": name, "display_name": disp,
            "category": "consumable", "desc": desc, "usable_battle": "battle" in use, "usable_field": "field" in use,
            "targeting": tgt, "effect": eff, "price": price, "sellable": sold, "sold_in_shops": sold,
            "rarity": rarity, "anim_template": anim, "quantity": "stack 1-99 (vanilla rule)",
            "steal": False, "drop": False, "metamorph": False, "colosseum_wager": False, "throwable": False,
            "equippable": False, "enemy_use": False, "acquisition": src, "derived": derived}

C = [
 cons(0x127, "CN-01", "CN_GAIA_TONIC", "Gaia Tonic", "Gaia Tonic", "Restores HP to the party{n}(menu: one member)",
      ["battle", "field"], "ALL_ALLIES", {"restore_hp": True, "power": 240, "undead_invert": True}, 1500, True, "common",
      "E9", {"source_type": "shop", "planned_source": "rebuilt shops (World of Ruin reconstruction)",
             "future_event_symbol": "EXT_SHOP_REBUILT_GENERAL", "conditions": "PREREQ_RECONSTRUCTION_SHOPS",
             "one_time": False, "gp_cost": 1500},
      ["effect (party HP restore: power 240 = 120 HP per member - the vanilla engine halves an item's power when it "
       "hits several targets; between Tonic 50 and Potion 250 per target)", "targeting", "price 1500",
       "anim template Potion", "menu use = one member (the vanilla field menu has no party-wide item use)"]),
 cons(0x128, "CN-02", "CN_AETHER_FLASK", "Aether Flask", "AetherFlask", "Aether Flask{n}Restores a lot of MP",
      ["battle", "field"], "ONE_ALLY", {"restore_mp": True, "power": 250}, 2, False, "rare", "EC",
      {"source_type": "event_chest", "planned_source": "story chests / quest rewards (not sold)",
       "future_event_symbol": "EV_CHEST_AETHER_FLASK", "conditions": "PREREQ_TBD_ARC_DESIGN", "one_time": True},
      ["effect (MP restore power 250, between Ether 150 and X-Ether full)", "not sold (MP economy)", "anim template Ether",
       "display name AetherFlask (12-char field)"]),
 cons(0x129, "CN-03", "CN_PHOENIX_ASH", "Phoenix Ash", "Phoenix Ash", "Revives one ally{n}with half of max HP",
      ["battle", "field"], "ONE_ALLY", {"restore_hp": True, "fraction": True, "power": 8, "removes_status": True,
                                       "status": ["DEAD"], "undead_invert": True}, 2, False, "rare", "F0",
      {"source_type": "boss_reward", "planned_source": "arc boss rewards (not sold)",
       "future_event_symbol": "EV_BOSS_PHOENIX_ASH", "conditions": "PREREQ_TBD_ARC_DESIGN", "one_time": True},
      ["effect (revive with 8/16 = 50% HP; Fenix Down is 2/16)", "not sold", "anim template Fenix Down"]),
 cons(0x12A, "CN-04", "CN_NULL_DUST", "Null Dust", "Null Dust", "Strips Haste/Safe/Shell/{n}Regen/Reflect/Float",
      ["battle"], "ONE_ENEMY", {"removes_status": True, "status": ["REGEN", "HASTE", "SHELL", "SAFE", "REFLECT", "FLOAT"]},
      800, True, "uncommon", "F5",
      {"source_type": "shop", "planned_source": "rebuilt shops (World of Ruin reconstruction)",
       "future_event_symbol": "EXT_SHOP_REBUILT_GENERAL", "conditions": "PREREQ_RECONSTRUCTION_SHOPS",
       "one_time": False, "gp_cost": 800},
      ["function (Dispel-like removal of the six beneficial statuses; read from the name 'Null')", "battle only",
       "targeting (one target, enemy by default)", "price 800", "anim template Remedy"]),
 cons(0x12B, "CN-05", "CN_IRON_RATION", "Iron Ration", "Iron Ration", "Restores HP and{n}cures Poison",
      ["battle", "field"], "ONE_ALLY", {"restore_hp": True, "power": 200, "removes_status": True, "status": ["POISON"],
                                       "undead_invert": True}, 250, True, "common", "FE",
      {"source_type": "shop", "planned_source": "rebuilt shops (World of Ruin reconstruction)",
       "future_event_symbol": "EXT_SHOP_REBUILT_GENERAL", "conditions": "PREREQ_RECONSTRUCTION_SHOPS",
       "one_time": False, "gp_cost": 250},
      ["effect (HP power 200 + Poison cure; Dried Meat is 150 HP)", "price 250", "anim template Dried Meat"]),
 cons(0x12C, "CN-06", "CN_REMEDY_PLUS", "Remedy+", "Remedy+", "Cures all bad status{n}incl. Zombie/Muddle/Stop",
      ["battle", "field"], "ONE_ALLY", {"removes_status": True,
       "status": ["BLIND", "ZOMBIE", "POISON", "IMP", "PETRIFY", "CONDEMNED", "SILENCE", "BERSERK", "CONFUSE", "SAP",
                  "SLEEP", "SLOW", "STOP"]}, 3000, True, "uncommon", "F5",
      {"source_type": "shop", "planned_source": "rebuilt shops (late reconstruction)",
       "future_event_symbol": "EXT_SHOP_REBUILT_LATE", "conditions": "PREREQ_RECONSTRUCTION_LATE",
       "one_time": False, "gp_cost": 3000},
      ["effect (Remedy set + Zombie, Condemned, Berserk, Muddle, Sleep, Slow, Stop)", "price 3000 (Remedy 1000)",
       "anim template Remedy"]),
 cons(0x12D, "CN-07", "CN_BEACON_FLARE", "Beacon Flare", "BeaconFlare", "Beacon Flare{n}Fire damage to all foes",
      ["battle"], "ALL_ENEMIES", {"power": 255, "element": ["FIRE"]}, 2, False, "rare", "SPELL:FIRE_2",
      {"source_type": "quest_reward", "planned_source": "Beacon quest (not sold)",
       "future_event_symbol": "EV_REWARD_BEACON_FLARE", "conditions": "PREREQ_BEACON_QUEST", "one_time": True},
      ["function (fire damage to all enemies; read from 'Flare')",
       "power 255 (items have no level scaling and the power is halved over several targets: ~127 per enemy "
       "with 2+ enemies, ~255 on one, x2 vs Fire-weak)", "not sold",
       "anim: vanilla Fire 2 spell animation", "display name BeaconFlare (12-char field)"]),
 cons(0x12E, "CN-08", "CN_MAGITEK_CELL", "Magitek Cell", "MagitekCell", "Magitek Cell{n}Restores the party's MP",
      ["battle"], "ALL_ALLIES", {"restore_mp": True, "power": 120}, 2, False, "rare", "ED",
      {"source_type": "quest_reward", "planned_source": "Magitek research / Vector arc (not sold)",
       "future_event_symbol": "EV_REWARD_MAGITEK_CELL", "conditions": "PREREQ_VECTOR_ARC", "one_time": True},
      ["function (party MP restore: power 120 = 60 MP per member after the multi-target halving; read from "
       "'Cell' = energy)", "battle only", "not sold",
       "anim template X-Ether", "display name MagitekCell (12-char field)"]),
]

def rare(rid, code, sym, name, disp, desc, arc, src, prereq, consumed, ending, derived):
    return {"rare_id": rid, "code": code, "symbol": sym, "locked_name": name, "display_name": disp, "desc": desc,
            "story_arc": arc, "acquisition": {"planned_source": src, "future_event_symbol": "EV_RARE_" + sym[4:],
                                             "prerequisite_flags": prereq, "one_time": True},
            "consumed": consumed, "ending_dependency": ending, "combat_stats": None, "derived": derived}

R = [
 rare(20, "KI-01", "KEY_DARILLS_TOKEN", "Darill's Token", "Darill'sToken", "A token of Darill, kept{n}aboard the Falcon.",
      "Setzer arc (Darill)", "Setzer arc: Darill's tomb / Falcon", ["PREREQ_SETZER_ARC"], "no", "none",
      ["story arc + source from the name", "display name Darill'sToken (13-char rare-name field)", "description"]),
 rare(21, "KI-02", "KEY_CONCORD_SIGIL", "Concord Sigil", "Concord Sigil", "Sigil of the Sanctuary{n}of Concord.",
      "Sanctuary of Concord arc", "Sanctuary of Concord", ["PREREQ_SANCTUARY_OF_CONCORD"], "no", "Triune Sigil prerequisite",
      ["source from the name (Sanctuary of Concord is a locked equipment source)", "description"]),
 rare(22, "KI-03", "KEY_CINDER_SIGIL", "Cinder Sigil", "Cinder Sigil", "A sigil warm as{n}smoldering cinders.",
      "arc TBD (Cinder)", "arc design (source not recovered)", ["PREREQ_TBD_ARC_DESIGN"], "no", "Triune Sigil prerequisite",
      ["story arc / source unknown (TBD)", "description"]),
 rare(23, "KI-04", "KEY_TRIUNE_SIGIL", "Triune Sigil", "Triune Sigil", "Three sigils made one.",
      "reconstruction / finale", "joins the Concord and Cinder sigils", ["HAS_RARE KEY_CONCORD_SIGIL", "HAS_RARE KEY_CINDER_SIGIL"],
      "no (the two sigils are kept: consumption not locked)", "ending / reconstruction dependency",
      ["prerequisite = both sigils (read from 'Triune')", "no consumption of the two sigils (not locked)", "description"]),
 rare(24, "KI-05", "KEY_BROKEN_SEAL", "Broken Seal", "Broken Seal", "A broken seal. Its power{n}is spent.",
      "finale / reconstruction", "late story (World of Ruin)", ["PREREQ_TBD_ARC_DESIGN"], "no", "ending / reconstruction dependency",
      ["story placement", "description"]),
]

json.dump({"_comment": "TECH v0.9 production consumables $127-$12E. Locked: names + 'some sold in rebuilt shops'. "
           "Everything else DERIVED (see 'derived'); effects are ItemProp data run by the vanilla item code.",
           "items": C}, open(os.path.join(HERE, "consumables.json"), "w"), indent=1)
json.dump({"_comment": "TECH v0.9 production key / rare items (logical rare ids 20-24; 0-19 are the vanilla rare items). "
           "Locked: names. Everything else DERIVED (see 'derived').", "rare_items": R},
          open(os.path.join(HERE, "rare_items.json"), "w"), indent=1)
# extended shops (ids $80+; event command $9B takes any shop id): "some consumables are sold in rebuilt shops"
# (locked). Shop composition / placement is DERIVED; no vanilla shop is changed.
S = [
 {"shop_id": "80", "symbol": "EXT_SHOP_REBUILT_GENERAL", "type": 3, "price_mod": 0,
  "items": ["127", "12B", "12A", "E9", "EB", "F0", "F5", "F7"],
  "note": "rebuilt general store: Gaia Tonic, Iron Ration, Null Dust + vanilla Potion, Tincture, Fenix Down, Remedy, Tent",
  "derived": ["composition", "shop id $80", "placement (future World of Ruin reconstruction event)"]},
 {"shop_id": "81", "symbol": "EXT_SHOP_REBUILT_LATE", "type": 3, "price_mod": 0,
  "items": ["12C", "127", "12B", "12A", "E9", "F0", "F5", "FD"],
  "note": "rebuilt late store: Remedy+ (late game) + the general consumables + vanilla Potion, Fenix Down, Remedy, Warp Stone",
  "derived": ["composition", "shop id $81", "placement (future late reconstruction event)"]},
]
json.dump({"_comment": "TECH v0.9 extended shops (XShopProp ids $80+, 8 entries each, 9-bit item ids). Vanilla shops "
           "$00-$7F are copied byte-exact.", "shops": S}, open(os.path.join(HERE, "ext_shops.json"), "w"), indent=1)
print(len(C), len(R), len(S))
