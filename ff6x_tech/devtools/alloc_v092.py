#!/usr/bin/env python3
"""TECH v0.9.2 manifest additions (idempotent). usage: python3 devtools/alloc_v092.py data/allocations.json

* D-21 production event bits (names reserved permanently; first user = the v0.9.2 QA target item-tech):
  EXP_HOPE_EMPIRE $0E0, EXP_CELES_STARTED $0E8, EXP_CELES_DONE $0E9, EXP_CELES_RECORDS_PRESERVED $0EA,
  EXP_CELES_RECORDS_CHOSEN $0EB (beat: records choice made), EXP_GRAVES_DONE $0EC (Graves Without Names done);
  NPC bit NPC_CELES_VALE_OUTER $6F0. All FREE_CANDIDATE in audits/eventbit_audit.json (checked by the builder).
* vanilla read-only refs CASE_CHAR_xx $1A0-$1AD (event cmd $DE party case word; vanilla scripts read them the same way).
* regions (QA target only): MAPX_MAP_PAL F7:A000-F7:DFFF (MapPal relocated, 64 palettes), MAPX_SPRITE_PAL
  F7:E000-F7:FFFF (MapSpritePal relocated, 256 entries); MAPX_SPARE no longer lists item-tech.
* vanilla claims (QA target only): QA_EVENT_BATTLE_GROUP_FA (CF:53E8-EB), MAP_INIT_EVENTS_NEW (D1:FEDD-D1:FFFF:
  the MapInitEvent slots of maps $19F-$1FF, all EventReturn in Rev 1), ITEMX_C2_STUBS already covers C2:6780-67FF.
"""
import json, sys

T = ["item-tech"]
BITS = [("0E0", "EXP_HOPE_EMPIRE", "event", "D-21 Hope flag 'Hope: Empire' (first of the 8 Hope flags, packed byte $1E9C)"),
        ("0E8", "EXP_CELES_STARTED", "event", "D-21 Celes arc started"),
        ("0E9", "EXP_CELES_DONE", "event", "D-21 Celes arc complete (Figaro Foundry Magitek Cell, memorial)"),
        ("0EA", "EXP_CELES_RECORDS_PRESERVED", "event", "D-21 records choice: 1 = Preserve, 0 = Burn (valid once RECORDS_CHOSEN)"),
        ("0EB", "EXP_CELES_RECORDS_CHOSEN", "event", "D-21 beat bit: the records choice was made"),
        ("0EC", "EXP_GRAVES_DONE", "event", "D-21 beat bit: Graves Without Names complete (stone memorial, D-07/D-08)"),
        ("6F0", "NPC_CELES_VALE_OUTER", "npc", "D-21 NPC bit: Vale visible on the Vector outer map")]


def main(path):
    d = json.load(open(path))
    eb = d["event_bits"]
    have = {b["name"] for b in eb["allocated"]}
    for bit, name, kind, st in BITS:
        if name not in have:
            eb["allocated"].append({"bit": bit, "name": name, "kind": kind, "default": 0,
                                    "status": f"TECH v0.9.2 (approved D-21): {st} - reserved permanently", "targets": list(T)})
    ro = {b["name"] for b in eb["vanilla_read_only_refs"]}
    chars = ["TERRA", "LOCKE", "CYAN", "SHADOW", "EDGAR", "SABIN", "CELES", "STRAGO", "RELM", "SETZER", "MOG", "GAU",
             "GOGO", "UMARO"]
    for i, c in enumerate(chars):
        n = f"CASE_CHAR_{c}"
        if n not in ro:
            eb["vanilla_read_only_refs"].append({"bit": f"{0x1A0 + i:03X}", "name": n, "kind": "event", "access": "read",
                "targets": list(T), "owner": "vanilla event command $DE (EventCmd_de C0:B40B) writes $1EB4-$1EB5 = characters in the active party",
                "use": "TECH v0.9.2 party-conditional dialogue (E5): party_case then if_switch CASE_CHAR_x"})
    eb.setdefault("vanilla_qa_write_refs", [])
    if not any(b["name"] == "QA_VANILLA_AIRSHIP_AVAILABLE" for b in eb["vanilla_qa_write_refs"]):
        eb["vanilla_qa_write_refs"].append({"bit": "1B9", "name": "QA_VANILLA_AIRSHIP_AVAILABLE", "kind": "event",
            "access": "qa_write", "targets": list(T),
            "owner": "vanilla: $1EB7 bit 1, set by the story scripts once the airship is owned; world/move.asm C:2069 lets the party board the parked airship with A only when it is set",
            "use": "TECH v0.9.2 QA HARNESS ONLY (qa_access_v092 QaWor92): emulate 'the Falcon is owned' so the tester can walk back to the parked airship and board it after leaving the Vector Outer Ward (E1). Production content never writes it."})
    names = {r["name"] for r in d["regions"]}
    for r in d["regions"]:
        if r["name"] == "MAPX_SPARE" and "item-tech" in r["targets"]:
            r["targets"].remove("item-tech")
            r["purpose"] += " (TECH v0.9.2: the QA target item-tech uses F7:A000-F7:FFFF for the relocated palettes.)"
    i = [k for k, r in enumerate(d["regions"]) if r["name"] == "MAPX_SPARE"][0]
    new = [{"name": "MAPX_MAP_PAL", "snes_start": "F7A000", "snes_end": "F7DFFF", "status": "active", "targets": list(T),
            "no_bank_cross": True, "purpose": "TECH v0.9.2 QA: MapPal relocated (48 vanilla palettes byte-exact + new map "
            "palettes from index $30); consumer C0:266D (LoadMapPal)"},
           {"name": "MAPX_SPRITE_PAL", "snes_start": "F7E000", "snes_end": "F7FFFF", "status": "active", "targets": list(T),
            "no_bank_cross": True, "purpose": "TECH v0.9.2 QA: MapSpritePal relocated (32 vanilla palettes byte-exact + "
            "new sprite palettes from index $20); consumers C0:50EE (InitSpritePal), C0:AA21 (event cmd $60)"}]
    for r in reversed(new):
        if r["name"] not in names:
            d["regions"].insert(i + 1, r)
    cl = {c["name"] for c in d["vanilla_space_claims"]}
    for c in [{"name": "QA_EVENT_BATTLE_GROUP_FA", "snes_start": "CF53E8", "snes_end": "CF53EB", "targets": list(T),
               "purpose": "QA only (TECH v0.9.2): event battle group $FA (unreferenced, audited like $FB-$FE) -> Praetor formation $244",
               "consumer": "event cmd $4D in qa_access_v092"},
              {"name": "QA_EVENT_BATTLE_GROUP_F9", "snes_start": "CF53E4", "snes_end": "CF53E7", "targets": list(T),
               "purpose": "QA only (TECH v0.9.2): event battle group $F9 (unreferenced, audited like $FB-$FE) -> manual-QA scaled Praetor formation $245",
               "consumer": "event cmd $4D in qa_access_v092"},
              {"name": "MAP_INIT_EVENTS_NEW", "snes_start": "D1FEDD", "snes_end": "D1FFFF", "targets": list(T),
               "purpose": "TECH v0.9.2: MapInitEvent pointers of the new map ids $19F-$1FF (Rev 1: all EventReturn CA:5EB3, "
                          "asserted per slot by patches/map_v04.py before a map package sets its startup event)",
               "consumer": "map load startup event (C0 LoadMap, $11FA bit 7)"}]:
        if c["name"] not in cl:
            d["vanilla_space_claims"].append(c)
    with open(path, "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1])
