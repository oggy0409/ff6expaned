#!/usr/bin/env python3
"""TECH v0.7 item/equipment architecture audit: per-concept mapping proposal (PROPOSAL ONLY, nothing implemented).
Concept data = locked Content_Data v1.3 (Weapons / Armor / Relics sheets). Vanilla references = audits/item_usage_audit.json
(regenerated from the clean Rev 1 ROM by tools/item_audit.py). -> audits/ITEM_MAPPING_PROPOSAL_v0.7.json"""
import json, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U = {int(r["id"], 16): r for r in json.load(open(os.path.join(HERE, "audits", "item_usage_audit.json")))["rows"]}

# (code, name, kind, slot, users, stats/effect (locked), locked source, option-A first candidate vanilla ID,
#  effect implementation note)
C = [
 ("EQ-W01", "Tempered Edge", "weapon", "sword", "Terra/Celes/Edgar/Locke", "Atk 188; Vigor +2; Eva +10", "Narshe forge quest", 0x15, "data"),
 ("EQ-W02", "Imperial Saber", "weapon", "sword", "Celes", "Atk 205; Magic +3; M.Eva +20", "Vector Annex chest", 0x19, "data"),
 ("EQ-W03", "Leo's Blade", "weapon", "sword", "Terra/Celes/Edgar/Locke", "Atk 218; Vigor +3; Stamina +3; Holy", "Celes arc rare branch", 0x11, "data (Holy = element bit $20)"),
 ("EQ-W04", "Raider Knife", "weapon", "knife", "Locke", "Atk 198; Speed +5; steal-on-hit", "Reconstruction chain", 0x05, "data (weapon special THIEFKNIFE, attacker effect $01)"),
 ("EQ-W05", "Sandpiercer", "weapon", "spear", "Edgar/Mog", "Atk 210; Wind; Speed +2", "Figaro Foundry", 0x20, "data; Jump x2 needs the spear ID range check C2:1512 (A: kept by staying in $1D-$24; B/C: extend check)"),
 ("EQ-W06", "Duncan Claw", "weapon", "claw", "Sabin", "Atk 214; Vigor +5; Stamina +3", "Master's Echo", 0x55, "data"),
 ("EQ-W07", "Moonless", "weapon", "ninja blade", "Shadow", "Atk 216; Speed +7; Eva +30", "Bandit's Hollow", 0x26, "data; Throw-able only if the Throw list handles the ID (A: yes; C: no unless added)"),
 ("EQ-W08", "Doma Edge", "weapon", "katana", "Cyan", "Atk 222; Vigor +5; Stamina +4", "Doma rebuilt smith", 0x2E, "data (Bushido flag)"),
 ("EQ-W09", "Darill's Dirk", "weapon", "knife", "Setzer/Locke", "Atk 202; Speed +4; Eva +20", "Sky Graveyard", 0x08, "data"),
 ("EQ-W10", "Magister Rod", "weapon", "rod", "Strago/Relm", "Atk 190; Magic +7; M.Eva +20", "Forgotten Age", 0x39, "data"),
 ("EQ-W11", "Concord Brush", "weapon", "brush", "Relm", "Atk 184; Magic +7; Speed +3", "Sanctuary of Concord", 0x3F, "data"),
 ("EQ-W12", "Gale Lance", "weapon", "spear", "Mog/Edgar", "Atk 218; Wind; Speed +4", "Beacon quest", 0x1F, "data; Jump x2 spear range as EQ-W05"),
 ("EQ-W13", "Echo Dagger", "weapon", "knife", "Gogo", "Atk 200; Vigor/Magic/Speed +3", "Cradle of Silence", 0x07, "data"),
 ("EQ-A01", "Royal Gear", "armor", "body", "Edgar/Sabin", "Def 84; MDef 60; Vig +4; Spd +2; Sta +3; Fire null", "Brass Colossus (Figaro arc)", 0x95, "data"),
 ("EQ-A02", "Imperial Mantle", "armor", "body", "Celes/Terra", "Def 78; MDef 72; Mag +4; M.Eva +20", "not specified in Armor sheet (placed by arc design)", 0x91, "data"),
 ("EQ-A03", "Magister Robe", "armor", "body", "Terra/Celes/Relm/Strago/Gogo", "Def 70; MDef 82; Mag +6; MP-oriented", "Archive Guardian (First Magi)", 0x97, "data (MP +12.5/25% relic bits)"),
 ("EQ-A04", "Ashen Mail", "armor", "body", "Edgar/Cyan/Setzer", "Def 88; MDef 52; Fire absorb; Ice weak", "not specified in Armor sheet (placed by arc design)", 0x8C, "data"),
 ("EQ-A05", "Concord Vest", "armor", "body", "Locke/Shadow/Gau/Mog/Gogo", "Def 76; MDef 62; Spd +4; Eva +20", "not specified in Armor sheet (placed by arc design)", 0x96, "data"),
 ("EQ-A06", "Doma Plate", "armor", "body", "Cyan/Edgar/Celes/Terra", "Def 92; MDef 58; Sta +5", "not specified in Armor sheet (placed by arc design)", 0x98, "data"),
 ("EQ-A07", "Falcon Jacket", "armor", "body", "Setzer/Locke/Shadow", "Def 74; MDef 60; Spd +5; Wind resist", "not specified in Armor sheet (placed by arc design)", 0x8E, "data"),
 ("EQ-A08", "Child's Ribbon", "armor", "helmet", "Terra/Relm/Celes", "Def 34; MDef 38; Mag +3; Sta +3; status resist subset", "not specified in Armor sheet (placed by arc design)", 0x70, "data (status immunity words)"),
 ("EQ-A09", "Doma Kabuto", "armor", "helmet", "Cyan", "Def 42; MDef 32; Vig +4; Sta +4", "not specified in Armor sheet (placed by arc design)", 0x7C, "data"),
 ("EQ-A10", "Engineer Goggles", "armor", "helmet", "Edgar/Setzer", "Def 36; MDef 30; Blind immunity; Spd +2", "not specified in Armor sheet (placed by arc design)", 0x79, "data"),
 ("EQ-A11", "Magi Circlet", "armor", "helmet", "magic users", "Def 36; MDef 44; Mag +5; M.Eva +10", "not specified in Armor sheet (placed by arc design)", 0x75, "data"),
 ("EQ-A12", "Concord Shield", "armor", "shield", "broad", "Def 54; MDef 48; Eva +20; M.Eva +20; Holy resist", "not specified in Armor sheet (placed by arc design)", 0x63, "data"),
 ("EQ-A13", "Ashguard", "armor", "shield", "heavy users", "Def 58; MDef 42; Fire absorb; Ice weak", "not specified in Armor sheet (placed by arc design)", 0x5F, "data"),
 ("EQ-R01", "Runic Crest", "relic", "relic", "Celes", "Mag +5; M.Eva +20; enhanced Runic (ASM, optional)", "Celes arc (Magitek Praetor)", 0xB9, "data + optional ASM (BAL-18 stat fallback)"),
 ("EQ-R02", "Maduin's Locket", "relic", "relic", "Terra", "Mag +6; Sta +3; longer Trance (ASM, optional)", "Terra arc (Magi-Eater)", 0xC2, "data + optional ASM (fallback MP +25%)"),
 ("EQ-R03", "Doma Crest", "relic", "relic", "Cyan", "Vig +5; Sta +5; Spd +2; faster Bushido (ASM, optional)", "Cyan arc (Miasma Regent)", 0xD4, "data + optional ASM"),
 ("EQ-R04", "Keepsake Ring", "relic", "relic", "Shadow/Relm", "blocks Doom/Zombie/instant death; Mag +3; Spd +3", "Shadow/Relm arc (Guiltshade)", 0xE1, "data (status immunity; Memento-Ring-like)"),
 ("EQ-R05", "Darill's Coin", "relic", "relic", "Setzer", "Spd +5; M.Eva +20; improved Slots (ASM, optional)", "Setzer arc (Sky Reaver)", 0xD6, "data + optional ASM"),
 ("EQ-R06", "Memorial Band", "relic", "relic", "all", "Sta +4; prevents Berserk/Confuse", "Vector memorial", 0xBE, "data"),
 ("EQ-R07", "Gale Pin", "relic", "relic", "all", "Spd +3; Wind resistance", "Coast beacon", 0xB7, "data"),
 ("EQ-R08", "Beastheart", "relic", "relic", "Gau", "Vig +4; Sta +4; Rage enhancement (ASM, optional)", "Gau side content", 0xB6, "data + optional ASM"),
 ("EQ-R09", "Painter's Lens", "relic", "relic", "Relm", "Mag +5; Sketch accuracy increase", "Relm extension", 0xC7, "data (RELIC_EFFECT3 INC_SKETCH_RATE, Beret's bit)"),
 ("EQ-R10", "Elder's Seal", "relic", "relic", "Strago", "Mag +5; MP +12.5%; Silence immunity", "Ancient lore", 0xB1, "data (MP_PLUS_12)"),
 ("EQ-R11", "Engineer's Badge", "relic", "relic", "Edgar", "Vig +3; Spd +3; Tools +10% (ASM, optional)", "Figaro", 0xE3, "data + optional ASM"),
 ("EQ-R12", "Master's Cord", "relic", "relic", "Sabin", "Vig +5; Sta +5; Blitz +10% (ASM, optional)", "Duncan", 0xD5, "data + optional ASM"),
 ("EQ-R13", "Legacy of the Magi", "relic", "relic", "Terra/Celes/Relm/Strago/Gogo", "Mag +7; M.Eva +30; MP +25%", "Vael Unbound (superboss)", 0xE2, "data (MP_PLUS_25)"),
]
NAMES = {int(l[:2], 16): l[9:21].strip().replace("~", " ") for l in open("/tmp/claude-0/items.txt")} if os.path.exists("/tmp/claude-0/items.txt") else {}
out = []
for k, (code, name, kind, slot, users, stats, src, a_id, eff) in enumerate(C):
    refs = {x: v for x, v in U[a_id]["refs"].items()}
    asm = "optional ASM" in eff
    out.append({
        "code": code, "concept": name, "kind": kind, "slot": slot, "users": users, "locked_stats": stats, "locked_source": src,
        "remains_true_equipment": True,
        "option_A": {"reuses_vanilla_id": f"{a_id:02X}", "vanilla_item": U[a_id]["name"].replace("~", " "),
                     "displaced_vanilla_refs": refs,
                     "note": "first candidate = same type/family, no hard-coded ID logic, fewest sources; final pick needs review"},
        "option_B": {"id": f"1{k:02X}", "note": "new 9-bit ID; every source type possible"},
        "option_C": {"id": f"1{k:02X}", "reuses_vanilla_id": None,
                     "delivery": "event give (chest / boss reward / quest step) at the locked source; not sold, not stealable/droppable/metamorph, not a Colosseum wager or prize"},
        "upgrade_or_evolution": "no (default); optional reforge-style delivery only with creative approval" if code in ("EQ-W01", "EQ-W04", "EQ-W08") else "no",
        "quest_or_key_reward": "equipment reward at locked source (not a key item)",
        "effect_implementation": eff,
        "risk": "medium" if (asm or "spear" in slot or "ninja" in slot) else "low-medium",
    })
json.dump({"_comment": "PROPOSAL ONLY - no item architecture implemented; see ITEM_ARCHITECTURE_DECISION_v0.7.md",
           "concepts": out}, open(os.path.join(HERE, "audits", "ITEM_MAPPING_PROPOSAL_v0.7.json"), "w"), indent=1)
print(len(out), "concepts written")
for o in out:
    a = o["option_A"]
    print(o["code"], o["concept"], "| A:", a["reuses_vanilla_id"], a["vanilla_item"], a["displaced_vanilla_refs"])
