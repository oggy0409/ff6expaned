"""M1xx-M3xx - TECH v0.4 MAP EXPANSION FOUNDATION (engine layer, all v0.4 targets).

1. Relocate the per-map tables from vanilla space into MAP_EXPANSION (F6-F7):
     event triggers, NPC properties, short entrances, long entrances, treasure
     -> 513 pointers each (maps $000-$1FF + end marker), same record formats;
     map properties -> 512 rows; layout (SubTilemap) pointers -> 1024 entries.
   Vanilla records are copied unchanged; content records are appended per map.
   The vanilla tables are left in place untouched (dead data) -> fully reversible.
2. Retarget every consumer (90 long-addressed instructions, list generated from the
   Rev 1 disassembly debug info: data/map_relocation_v04.json). Only the 3 operand
   bytes change; each original instruction is asserted against the clean ROM.
3. NPC event routing: NPC records hold an 18-bit event pointer (CA:0000-CD:FFFF).
   Non-special NPCs whose field is $3xxxx (bank CD = dialogue data; no vanilla
   non-special NPC uses it - audited: 0 of 1904) are routed through a 24-bit vector
   table (MAPX_NPC_EVENT_VECTORS) by a JSL hook in InitNPCs (C0:52E6). Every
   vanilla NPC takes the unchanged path (AND #$03 / STA $088B,Y).
"""
import json, os
from ff6x.asm65816 import Asm
from ff6x.hirom import snes_to_pc, fmt_snes
from ff6x.maptables import RelocTable

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELOC = json.load(open(os.path.join(HERE, "data", "map_relocation_v04.json")))

MAP_IDS = 512
PACKED = [  # name, region, patch id, rel_to_data
    ("EVENT_TRIGGERS", "MAPX_EVENT_TRIGGERS", "M101_MAPX_EVENT_TRIGGERS", False),
    ("NPC_PROPS", "MAPX_NPC_PROPS", "M102_MAPX_NPC_PROPS", False),
    ("SHORT_ENTRANCES", "MAPX_SHORT_ENTRANCES", "M103_MAPX_SHORT_ENTRANCES", False),
    ("LONG_ENTRANCES", "MAPX_LONG_ENTRANCES", "M104_MAPX_LONG_ENTRANCES", False),
    ("TREASURE", "MAPX_TREASURE", "M105_MAPX_TREASURE", True),
]
LAYOUT_SLOTS = 1024
VANILLA_LAYOUT_SLOTS = 0x15F          # $000-$15E copied (350 layouts + END entry $15E)
ROUTER_ORG = 0xF01100
ROUTER_SITE = 0xC052E6
ROUTER_SITE_ORIG = bytes.fromhex("29 03 99 8B 08")       # AND #$03 / STA $088B,Y
ROUTER_SITE_PRE = (0xC052E2, bytes.fromhex("BF 12 1A C4"))  # LDA NPCProp::EventPtr+2,X (retargeted)
EVENT_RETURN = 0xCA5EB3
NPC_VECTOR_FLAG = 0x30000


def vanilla_tables(clean):
    out = {}
    for name, _, _, rel in PACKED:
        t = RELOC["tables"][name]
        out[name] = RelocTable.parse(clean, name, int(t["ptr"], 16), t["ptrs"], t["rec"], rel,
                                     int(t["end"], 16), MAP_IDS)
    return out


def region_range(rom, region):
    r = rom.alloc.region(region, rom.target)
    return 0xC00000 + r["pc_start"], r["pc_end"] - r["pc_start"] + 1


def retarget(rom, name, new_ptr, new_data, patch_id):
    t = RELOC["tables"][name]
    old = {"ptr": int(t["ptr"], 16) if t.get("ptr") else None,
           "data": int(t["data"], 16) if t.get("data") else None}
    new = {"ptr": new_ptr, "data": new_data}
    done = []
    for c in t["consumers"]:
        snes = int(c["snes"], 16)
        ins = bytes.fromhex(c["bytes"])
        op = int(c["operand"], 16)
        if op != old[c["base"]] + c["disp"] or ins[1:] != op.to_bytes(3, "little"):
            raise SystemExit(f"{patch_id}: consumer record inconsistent at {c['snes']}")
        nop = new[c["base"]] + c["disp"]
        rom.patch(snes + 1, ins[1:], nop.to_bytes(3, "little"), patch_id,
                  consumer=f"{fmt_snes(snes)} opcode {ins[0]:02X} (long,X) reads {name}",
                  reason=f"operand {fmt_snes(op)} -> {fmt_snes(nop)} ({c['base']} base + {c['disp']})",
                  claim=None, table=None, retarget=True)
        done.append(c["snes"])
    return done


def build_router(rom, npc_base, vec_base, vec_count):
    a = Asm(ROUTER_ORG)
    a.label("NpcEventRouter")       # entry .a8 .i16; A = record byte 2; X = record offset; Y = object
    a.and_imm8(0x03)                # displaced: AND #$03
    a.cmp_imm8(0x03)
    a.bne("Store")                  # bits 0-2 -> vanilla
    a.lda_long_x(npc_base + 4)      # NPCProp::SpecialNPC (bit 7)
    a.bmi("Special3")               # special NPC: field is not an event pointer -> vanilla
    a.rep(0x20)
    a.lda_abs_y(0x0889)             # vector index (record bytes 0-1, already stored)
    a.cmp_imm16(vec_count)
    a.bcs("Invalid")
    a.phx()
    a.pha()
    a.asl_a()
    a.clc()
    a.adc_sr(0x01)                  # index * 3
    a.tax()
    a.pla()
    a.lda_long_x(vec_base)          # event address bits 0-15
    a.sta_abs_y(0x0889)
    a.sep(0x20)
    a.lda_long_x(vec_base + 2)      # event bank
    a.sec()
    a.sbc_imm8(0xCA)                # engine adds #^EventScript ($CA) when starting the event
    a.sta_abs_y(0x088B)
    a.plx()
    a.rtl()
    a.label("Invalid")              # .a16: out-of-range vector -> EventReturn (CA:5EB3)
    a.lda_imm16(EVENT_RETURN & 0xFFFF)
    a.sta_abs_y(0x0889)
    a.sep(0x20)
    a.lda_imm8(0x00)
    a.sta_abs_y(0x088B)
    a.rtl()
    a.label("Special3")
    a.lda_imm8(0x03)
    a.label("Store")
    a.sta_abs_y(0x088B)             # displaced: STA $088B,Y
    a.rtl()
    code = a.assemble()
    rom.place("ENGINE_CODE", code, "NpcEventRouter", "M300_NPC_EVENT_ROUTER", at=ROUTER_ORG,
              reason="NPC event router: vanilla NPCs unchanged; non-special NPCs with event field $3xxxx -> vector table",
              consumer="JSL from C0:52E6 (InitNPCs)")
    pre = bytes(rom.clean[snes_to_pc(ROUTER_SITE_PRE[0]):snes_to_pc(ROUTER_SITE_PRE[0]) + 4])
    if pre != ROUTER_SITE_PRE[1]:
        raise SystemExit("M300: InitNPCs instruction before the router site mismatch")
    jsl = bytes([0x22, ROUTER_ORG & 0xFF, (ROUTER_ORG >> 8) & 0xFF, ROUTER_ORG >> 16, 0xEA])
    rom.patch(ROUTER_SITE, ROUTER_SITE_ORIG, jsl, "M300_NPC_EVENT_ROUTER",
              consumer="InitNPCs C0:52E6 (after LDA NPCProp::EventPtr+2,X)",
              reason="AND #$03 / STA $088B,Y -> JSL F0:1100 / NOP (router re-executes both for vanilla NPCs)",
              claim="NPC_EVENT_ROUTER_SITE")
    return a.listing_text()


def build(rom, content):
    """content: dict with optional keys
         records: {TABLE: [(map, bytes, label)]}, replace: {TABLE: [(map, idx, bytes, label)]}
         props: {map: 33-byte row}, layouts: {index: snes}, vectors: [snes], vector_labels: [str]
    """
    notes = {"tables": {}}
    vt = vanilla_tables(rom.clean)
    vanilla_runs = {k: [list(r) for r in v.records] for k, v in vt.items()}
    bases = {}
    for name, region, pid, rel in PACKED:
        t = vt[name]
        for m, rec, label in content.get("records", {}).get(name, []):
            t.add(m, rec, label)
        for m, idx, rec, label in content.get("replace", {}).get(name, []):
            t.replace(m, idx, rec, label)
        if name == "NPC_PROPS":
            for m in range(MAP_IDS):
                if len(t.records[m]) > 32:
                    raise SystemExit(f"{pid}: map {m:03X} has {len(t.records[m])} NPCs (engine limit 32, objects $10-$2F)")
        start, size = region_range(rom, region)
        blob = t.serialize(size)
        rom.place(region, blob, name.lower() + "_x", pid, at=start,
                  reason=f"{name}: {t.vanilla_count} vanilla records (maps $000-${t.vanilla_maps - 1:03X}) + "
                         f"{len(t.inserted)} content records; 513 pointers",
                  consumer=f"{len(RELOC['tables'][name]['consumers'])} retargeted consumers")
        ptr_base = start
        data_base = start + 2 * (MAP_IDS + 1)
        bases[name] = (ptr_base, data_base)
        notes["tables"][name] = {"snes": fmt_snes(start), "bytes_used": t.used, "capacity_bytes": size,
                                 "records": t.count, "vanilla_records": t.vanilla_count,
                                 "record_capacity": t.capacity_records(),
                                 "inserted": [{"map": f"{m:03X}", "label": l, "record": r.hex(" ").upper()}
                                              for m, l, r in t.inserted]}
        # static equivalence: every vanilla map keeps exactly its vanilla records (+ appended content)
        for m in range(t.vanilla_maps):
            n = len(vanilla_runs[name][m])
            if t.records[m][:n] != vanilla_runs[name][m] and not content.get("replace", {}).get(name):
                raise SystemExit(f"{pid}: vanilla records of map {m:03X} changed")
    # map properties (512 rows)
    mp = RELOC["tables"]["MAP_PROPS"]
    old = snes_to_pc(int(mp["data"], 16))
    rows = [bytes(rom.clean[old + 33 * m: old + 33 * m + 33]) for m in range(mp["rows"])]
    rows += [bytes(33)] * (MAP_IDS - mp["rows"])
    for m, row in sorted(content.get("props", {}).items()):
        if len(row) != 33:
            raise SystemExit("M106: property row must be 33 bytes")
        if m < mp["rows"] and rows[m] != bytes(33) and not content.get("props_overwrite_ok", {}).get(m):
            raise SystemExit(f"M106: map {m:03X} has a non-blank vanilla property row")
        rows[m] = row
    start, size = region_range(rom, "MAPX_MAP_PROPS")
    rom.place("MAPX_MAP_PROPS", b"".join(rows), "map_props_x", "M106_MAPX_MAP_PROPS", at=start,
              reason=f"512 x 33-byte rows: vanilla $000-$19E copied; content rows {sorted(f'{m:03X}' for m in content.get('props', {}))}",
              consumer="LoadMapProp C0:1CAD (LDA.l MapProp,X; X = map*33)")
    bases["MAP_PROPS"] = (None, start)
    # layout pointers (1024 x 3)
    st = RELOC["tables"]["SUBTILEMAP_PTRS"]
    sp = snes_to_pc(int(st["ptr"], 16))
    ent = [bytes(rom.clean[sp + 3 * i: sp + 3 * i + 3]) for i in range(VANILLA_LAYOUT_SLOTS)]
    filler = ent[0]
    ent += [filler] * (LAYOUT_SLOTS - VANILLA_LAYOUT_SLOTS)
    for idx, snes in sorted(content.get("layouts", {}).items()):
        if idx < VANILLA_LAYOUT_SLOTS or idx >= LAYOUT_SLOTS:
            raise SystemExit(f"M107: layout index {idx:03X} not in $15F-$3FF")
        off = snes - 0xD9D1B0
        ent[idx] = off.to_bytes(3, "little")
    start, size = region_range(rom, "MAPX_SUBTILEMAP_PTRS")
    rom.place("MAPX_SUBTILEMAP_PTRS", b"".join(ent), "subtilemap_ptrs_x", "M107_MAPX_SUBTILEMAP_PTRS", at=start,
              reason=f"1024 layout pointers: vanilla $000-$15E copied, unassigned = entry $000 value; "
                     f"content {sorted(f'{i:03X}' for i in content.get('layouts', {}))}",
              consumer="LoadMapTiles C0:2883 (BG1/BG2/BG3, 10-bit index * 3)")
    bases["SUBTILEMAP_PTRS"] = (start, None)
    # NPC event vectors
    vecs = content.get("vectors", [])
    vstart, vsize = region_range(rom, "MAPX_NPC_EVENT_VECTORS")
    if 3 * len(vecs) > vsize:
        raise SystemExit("M108: too many NPC event vectors")
    if vecs:
        blob = b"".join(v.to_bytes(3, "little") for v in vecs)
        rom.place("MAPX_NPC_EVENT_VECTORS", blob, "npc_event_vectors", "M108_NPC_EVENT_VECTORS", at=vstart,
                  reason="NPC event vectors: " + ", ".join(f"#{i}={fmt_snes(v)} ({l})" for i, (v, l)
                                                            in enumerate(zip(vecs, content.get("vector_labels", [])))),
                  consumer="M300 router (LDA.l vectors,X)")
    # retarget consumers
    notes["retargets"] = {}
    for name, (pb, db) in bases.items():
        notes["retargets"][name] = retarget(rom, name, pb, db, f"M200_RETARGET_{name}")
    notes["router_listing"] = build_router(rom, bases["NPC_PROPS"][0], vstart, len(vecs))
    notes["vectors"] = [{"index": i, "snes": fmt_snes(v)} for i, v in enumerate(vecs)]
    notes["capacity"] = {
        "map_ids": "512 slots ($000-$1FF); $1FE/$1FF reserved by the engine (previous/parent map); "
                   "vanilla uses $000-$19E; new IDs $19F-$1FD (95) usable",
        "layout_indices": f"1024 ($000-$3FF); vanilla $000-$15D + END $15E; new $15F-$3FF (673)",
        "npc_event_vectors": f"{vsize // 3} slots ({len(vecs)} used)",
        **{k: f"{v['record_capacity']} records ({v['records']} used, vanilla {v['vanilla_records']})"
           for k, v in notes["tables"].items()}}
    return notes, bases
