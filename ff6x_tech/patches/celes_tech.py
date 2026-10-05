"""T300 - TECH v0.3 Celes "Echoes of the Empire" technical vertical slice.

Pipeline proven: Falcon interior (vanilla WoR) -> new map $0C7 -> NPC ->
expansion dialogue -> production flags -> event battle -> one-time reward
-> exit -> vanilla WoR. All content is placeholder.

Sources of truth: maps/celes_annex_tech/*, events/celes_annex_tech/*,
data/allocations.json (bits, regions, claims, table repacks).
"""
import json, os
from ff6x.eventasm import EventProgram
from ff6x.hirom import snes_to_pc, event_offset, npc_event_reachable, fmt_snes
from ff6x.lzss import compress_literal, decompress
from ff6x.mapsrc import MapPackage
from ff6x.tables import PackedTable, encode_npc
from patches import dialogue_hook

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_DIR = os.path.join(HERE, "maps", "celes_annex_tech")
EVT_DIR = os.path.join(HERE, "events", "celes_annex_tech")

SUBTILEMAP_PTRS = 0xD9CD90          # 3-byte offsets (+D9:D1B0)
SUBTILEMAP_BASE = 0xD9D1B0
NEW_LAYOUT_INDEX = 0x15F
BG2_LAYOUT_INDEX = 0x12A            # vanilla: 4096 x $01 (read-only reuse)
MAP_PROPS = 0xED8F00
MAP_INIT_EVENTS = 0xD1FA00
EVENT_RETURN = 0xCA5EB3
VANILLA_POST_BATTLE = (0xCA5EA9, bytes.fromhex("B7 40 B2 5E 00 B2 66 E5 02 FE"))   # if_b_switch $40 / call GameOver / return
BRIDGE_BASE = 0xCCE5EE
DIRS = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}
REACT = {"FACE_PLAYER": 0, "NONE": 4}


def messages():
    d = json.load(open(os.path.join(EVT_DIR, "dialogue.json")))
    return [(m["label"], m["text"]) for m in d["messages"]]


def build(rom, bits, dlg_ids, audit_report, qa=None):
    """qa: optional QA-harness callback (celes-qa target only). Production passes None."""
    notes = {}
    pkg = MapPackage(MAP_DIR)
    if pkg.map_id != 0x0C7:
        raise SystemExit("T300: unexpected map id")
    notes["walkability"] = pkg.validate(rom.clean)

    # ---- preconditions on vanilla data (read-only asserts) -------------------------------
    pc = snes_to_pc(VANILLA_POST_BATTLE[0])
    if rom.clean[pc:pc + 10] != VANILLA_POST_BATTLE[1]:
        raise SystemExit("T300: vanilla post-battle subroutine mismatch")
    for m in (0x0C7, 0x00C):
        p = snes_to_pc(MAP_INIT_EVENTS) + 3 * m
        if rom.clean[p:p + 3] != bytes.fromhex("B3 5E 00"):
            raise SystemExit(f"T300: map {m:03X} startup event is not EventReturn")
    bg2 = rom.clean[snes_to_pc(SUBTILEMAP_PTRS) + 3 * BG2_LAYOUT_INDEX: snes_to_pc(SUBTILEMAP_PTRS) + 3 * BG2_LAYOUT_INDEX + 3]
    bg2_data = decompress(rom.clean[snes_to_pc(SUBTILEMAP_BASE) + int.from_bytes(bg2, "little"):])
    if bg2_data != b"\x01" * 4096:
        raise SystemExit("T300: BG2 filler layout $12A is not 4096 x $01")

    # ---- events (F1) ----------------------------------------------------------------------
    prog = EventProgram(0xF10000, bits, dlg_ids, {"VanillaPostBattleCheck": VANILLA_POST_BATTLE[0],
                                                   "EventReturn": EVENT_RETURN})
    prog.parse(open(os.path.join(EVT_DIR, "events.evt")).read(), "events.evt")
    code = prog.assemble()
    unused = set(bits) - prog.bits_used
    if unused:
        raise SystemExit(f"T300: allocated bits never used: {unused}")
    rom.place("EVENT_EXPANSION", code, "celes_annex_tech_events", "T300_EVENTS", at=0xF10000,
              reason="Celes Annex TECH v0.3 event scripts (source events/celes_annex_tech/events.evt)",
              consumer="event interpreter via F1 pointers (triggers 24-bit, NPC bridges, choice/if jumps)")
    notes["event_listing"] = prog.listing_text()
    L = prog.labels

    # ---- NPC bridges (CA-CD reachable stubs) ----------------------------------------------
    bridges = {}
    for n in pkg.npcs:
        slot = n["bridge_slot"]
        addr = BRIDGE_BASE + 5 * slot
        stub = bytes([0xB2]) + event_offset(L[n["event"]]).to_bytes(3, "little") + bytes([0xFE])
        rom.patch(addr, b"\xFF" * 5, stub, "T301_NPC_BRIDGES",
                  consumer=f"NPC {n['name']} activation (18-bit NPC event pointer)",
                  reason=f"bridge: call {fmt_snes(L[n['event']])} ({n['event']}) then return",
                  claim="NPC_EVENT_BRIDGES")
        assert npc_event_reachable(addr)
        bridges[n["name"]] = addr

    # ---- layout (F5) + pointer slot $15F ------------------------------------------------
    bg1 = pkg.compile_bg1()
    lz = compress_literal(bg1)
    assert decompress(lz) == bg1
    lay = rom.place("MAP_LAYOUTS", lz, "celes_annex_bg1_lz", "T302_LAYOUT", at=0xF50000,
                    reason=f"BG1 layout {pkg.w}x{pkg.h} from maps/celes_annex_tech/layout_bg1.txt (literal LZSS)",
                    consumer="LoadMapTiles (C0:2883) via SubTilemap pointer $15F")
    off = lay - SUBTILEMAP_BASE
    slot_snes = SUBTILEMAP_PTRS + 3 * NEW_LAYOUT_INDEX
    rom.patch(slot_snes, b"\xFF\xFF\xFF", off.to_bytes(3, "little"), "T303_LAYOUT_PTR",
              consumer="LoadMapTiles C0:2883: LDA.l SubTilemapPtrs,X + #SubTilemap (24-bit add)",
              reason=f"layout index $15F -> {fmt_snes(lay)} (offset {off:06X} from D9:D1B0)",
              claim="LAYOUT_PTR_SLOT_15F")

    # ---- map properties row ---------------------------------------------------------------
    row = pkg.props_row(NEW_LAYOUT_INDEX, BG2_LAYOUT_INDEX, 0)
    rom.patch(MAP_PROPS + 33 * 0x0C7, bytes(33), row, "T304_MAP_PROPS",
              consumer="LoadMapProp C0:1CAD (33 bytes -> $0520-$0540)",
              reason="map $0C7 properties (map.json); tileset/palette from vanilla Magitek-lab map $112",
              claim="MAP_PROPS_0C7")

    # ---- packed tables ----------------------------------------------------------------------
    def repack(name, edits, pid=None):
        t = rom.alloc.table(name, rom.target)
        tbl = PackedTable(rom.clean, name, int(t["ptr_snes"], 16), int(t["data_end_snes"], 16),
                          t["record_size"], t["ptr_count"])
        for m, rec, label in edits:
            tbl.add(m, rec, label)
        new = tbl.serialize()
        rom.patch(int(t["ptr_snes"], 16), tbl.orig, new, pid or f"T305_REPACK_{name}",
                  consumer=f"{name} loader (pointer-relative; all consumers use the pointer table)",
                  reason="insert " + ", ".join(f"map {m:03X}:{l}" for m, _, l in edits) +
                         f"; slack {tbl.slack} -> {tbl.slack_after()} bytes", table=name)
        return {"slack_before": tbl.slack, "slack_after": tbl.slack_after(),
                "inserted": [{"map": f"{m:03X}", "label": l, "record": r.hex(" ").upper()} for m, l, r in tbl.inserted]}

    trig = []
    for t in pkg.triggers:
        ptr = event_offset(L[t["event"]])
        trig.append((int(t["map"], 16), bytes([t["x"], t["y"]]) + ptr.to_bytes(3, "little"), t["event"]))
    npcs = []
    for n in pkg.npcs:
        kw = dict(event_snes=bridges[n["name"]], switch=bits[n["switch"]], x=n["x"], y=n["y"],
                  gfx=int(n["gfx"].split()[0], 16), pal=n["pal"], speed=n["speed"],
                  react=REACT[n.get("react", "FACE_PLAYER")])
        if "anim" in n:
            a = n["anim"]
            kw["anim"] = (a["type"], int(a["frame"].split()[0], 16), a["speed"])
        else:
            kw["direction"] = DIRS[n["direction"]]
            kw["movement"] = 0
        npcs.append((pkg.map_id, encode_npc(**kw), n["name"]))
    ents = []
    for e in pkg.exits["short_entrances"]:
        w = int(e["dest_map"], 16) | (DIRS[e["facing"]] << 12) | (0x400 if "Z_UPPER" in e["flags"] else 0)
        ents.append((int(e["map"], 16), bytes([e["src"][0], e["src"][1], w & 0xFF, w >> 8, e["dest"][0], e["dest"][1]]),
                     f"exit->{e['dest_map']}"))
    # the new map must currently be empty in every table
    for name, size, ptrs in (("EVENT_TRIGGERS", 5, 417), ("NPC_PROPS", 9, 417), ("SHORT_ENTRANCES", 6, 513)):
        t = rom.alloc.table(name, rom.target)
        tb = PackedTable(rom.clean, name, int(t["ptr_snes"], 16), int(t["data_end_snes"], 16), size, ptrs)
        if tb.count(0x0C7):
            raise SystemExit(f"T300: map $0C7 already has {name} records")
    pid_trig = pid_ent = None
    if qa is not None:                       # QA harness only: extra trigger + exit redirect
        spec = qa(rom, L)
        trig += spec["triggers"]
        pid_trig = "Q305_REPACK_EVENT_TRIGGERS_QA"
        if spec.get("exit_override"):
            ents = spec["exit_override"](ents)
            pid_ent = "Q305_REPACK_SHORT_ENTRANCES_QA"
        notes["qa"] = spec.get("notes", {})
    notes["tables"] = {"EVENT_TRIGGERS": repack("EVENT_TRIGGERS", trig, pid_trig),
                       "NPC_PROPS": repack("NPC_PROPS", npcs),
                       "SHORT_ENTRANCES": repack("SHORT_ENTRANCES", ents, pid_ent)}
    notes["layout"] = {"index": "$15F", "snes": fmt_snes(lay), "raw_bytes": len(bg1), "lz_bytes": len(lz),
                       "pointer_slot": fmt_snes(slot_snes)}
    notes["map_props_row"] = row.hex(" ").upper()
    notes["bridges"] = {k: fmt_snes(v) for k, v in bridges.items()}
    notes["event_labels"] = {k: fmt_snes(v) for k, v in L.items()}
    notes["bits"] = {k: f"${v:03X}" for k, v in bits.items()}
    return notes
