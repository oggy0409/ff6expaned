"""TECH v0.4 target builder: accepted engine layer + map foundation + source packages.

Targets:
  production  : dialogue hook (P100/P101, diagnostic only) + map foundation (M1xx-M3xx)
  celes-tech  : production + package celes_annex_tech (accepted v0.3 slice sources, unchanged)
  map-tech    : celes-tech + package map_tech_v04 (two proof maps) + package qa_access_v04 (QA HARNESS)

Packages live in events/<pkg>/package.json (+ events.evt, dialogue.json, optional records.json)
and reference map packages in maps/<name>/.
"""
import json, os
from ff6x.eventasm import EventProgram
from ff6x.hirom import snes_to_pc, event_offset, fmt_snes
from ff6x.lzss import compress_literal, decompress
from ff6x.mapsrc4 import MapPackageV4
from ff6x.tables import encode_npc
from ff6x.text import encode_dialogue, line_widths, FONT_WIDTH_SNES, LINE_LIMIT_PX
from patches import dialogue_hook, map_foundation

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKAGES = {
    "production": [],
    "celes-tech": ["celes_annex_tech"],
    "map-tech": ["celes_annex_tech", "map_tech_v04", "qa_access_v04"],
}
DIRS = {"UP": 0, "RIGHT": 1, "DOWN": 2, "LEFT": 3}
REACT = {"FACE_PLAYER": 0, "NONE": 4}
MAP_INIT_EVENTS = 0xD1FA00
EVENT_RETURN_PTR = bytes.fromhex("B3 5E 00")
VANILLA_EXTERNALS = {"EventReturn": 0xCA5EB3, "VanillaPostBattleCheck": 0xCA5EA9, "VanillaSavePoint": 0xCC9AEB,
                     "VanillaColosseum": 0xCB78D9}
VANILLA_ASSERTS = [(0xCA5EA9, bytes.fromhex("B7 40 B2 5E 00 B2 66 E5 02 FE")),   # post-battle check
                   (0xCC9AEB, bytes.fromhex("C0 B5 81 B3 5E 00")),                 # SavePoint head
                   # TECH v0.7.2: vanilla Colosseum sequence (receptionist "With pleasure." branch _cb78d9):
                   # fade_out 8 / wait_fade / colosseum_menu ($9A) / if $1EE=0 -> CB:7972 / if $1EF=0 -> CB:796C
                   (0xCB78D9, bytes.fromhex("5A 08 5C 9A C0 EE 01 72 79 01 C0 EF 01 6C 79 01")),
                   (0xCB796C, bytes.fromhex("AF B2 72 79 01 FE")),               # colosseum_battle ($AF) / call fade-in
                   (0xCB7972, bytes.fromhex("59 04 5C FE"))]                     # fade_in 4 / wait_fade / return


def load_pkg(name):
    d = os.path.join(HERE, "events", name)
    cfg = json.load(open(os.path.join(d, "package.json")))
    cfg["dir"] = d
    cfg["messages"] = [(m["label"], m["text"]) for m in json.load(open(os.path.join(d, "dialogue.json")))["messages"]]
    rp = os.path.join(d, "records.json")
    cfg["records"] = json.load(open(rp)) if os.path.exists(rp) else {}
    cfg["map_pkgs"] = [MapPackageV4(os.path.join(HERE, m)) for m in cfg.get("maps", [])]
    return cfg


def entrance_word(dest_map, facing, flags):
    return int(dest_map, 16) | (DIRS[facing] << 12) | (0x400 if "Z_UPPER" in flags else 0) \
        | (0x800 if "SHOW_TITLE" in flags else 0)


def short_rec(e):
    w = entrance_word(e["dest_map"], e["facing"], e.get("flags", []))
    return bytes([e["src"][0], e["src"][1], w & 0xFF, w >> 8, e["dest"][0], e["dest"][1]])


def long_rec(e):
    w = entrance_word(e["dest_map"], e["facing"], e.get("flags", []))
    ln = e["length"] | (0x80 if e.get("vertical") else 0)
    if not 0 <= e["length"] <= 0x7F:
        raise SystemExit("long entrance length 0..127")
    return bytes([e["src"][0], e["src"][1], ln, w & 0xFF, w >> 8, e["dest"][0], e["dest"][1]])


def dialogue(rom, pkgs, diag):
    """Production messages via the accepted P101 table; QA-package strings placed in
    QA_HARNESS (Q401) with their pointer slots appended (still contiguous IDs)."""
    prod = [diag] + [m for p in pkgs if not p.get("qa") for m in p["messages"]]
    qa = [m for p in pkgs if p.get("qa") for m in p["messages"]]
    qa_pid = next((p.get("dlg_patch", "Q401_QA_DLG") for p in pkgs if p.get("qa")), "Q401_QA_DLG")
    labels = [l for l, _ in prod + qa]
    if len(labels) != len(set(labels)):
        raise SystemExit("duplicate dialogue labels across packages")
    table, count, ids = dialogue_hook.build_dialogue_table(rom, prod)
    if qa:
        fw = rom.clean[snes_to_pc(FONT_WIDTH_SNES):snes_to_pc(FONT_WIDTH_SNES) + 256]
        ptrs = bytearray()
        at = 0xFF0800                     # QA_HARNESS: events at FF:0000, QA text at FF:0800+
        for k, (label, text) in enumerate(qa):
            data = encode_dialogue(text)
            lw = line_widths(data, fw)
            if max(lw) > LINE_LIMIT_PX or len(lw) > 4:
                raise SystemExit(f"Q401: '{label}' would wrap: {lw}")
            n = count + k
            s = rom.place("QA_HARNESS", data, f"qa_dlg_{0x1000 + n:04X}_{label}", qa_pid, at=at,
                          reason=f"QA dialogue ${0x1000 + n:04X}: {text!r}",
                          consumer="field text renderer via $C9/$CB set by P100 hook")
            at = s + len(data)
            ptrs += bytes([s & 0xFF, (s >> 8) & 0xFF, s >> 16, 0])
            ids[label] = 0x1000 + n
        rom.place("DIALOGUE_PTRS", bytes(ptrs), "qa_dlg_ptr_slots", qa_pid, at=0xF30000 + 4 * count,
                  reason=f"pointer slots for QA IDs ${0x1000 + count:04X}+", consumer="P100 hook")
        count += len(qa)
    hook = dialogue_hook.build_hook(rom, table, count)
    return ids, hook


def build(rom, target, alloc, diag, packages=None, ext_items=False):
    notes = {}
    for snes, exp in VANILLA_ASSERTS:
        if rom.clean[snes_to_pc(snes):snes_to_pc(snes) + len(exp)] != exp:
            raise SystemExit(f"v0.4: vanilla assert failed at {fmt_snes(snes)}")
    pkgs = [load_pkg(n) for n in (packages if packages is not None else PACKAGES[target])]
    ids, notes["hook_listing"] = dialogue(rom, pkgs, diag)
    notes["dialogue_ids"] = {k: f"${v:04X}" for k, v in ids.items()}
    audit = json.load(open(os.path.join(HERE, "audits", "eventbit_audit.json")))
    bits = alloc.event_bits(target, audit)
    ro = alloc.vanilla_ref_bits(target)
    names = dict(bits); names.update(ro)

    # ---- events -----------------------------------------------------------------------------
    labels = dict(VANILLA_EXTERNALS)
    used = set()
    notes["event_listings"] = {}
    for p in pkgs:
        org = int(p["event_org"], 16)
        prog = EventProgram(org, bits, ids, dict(labels), readonly_bits=ro, ext_items=ext_items)
        prog.parse(open(os.path.join(p["dir"], "events.evt")).read(), f"{p['name']}/events.evt")
        code = prog.assemble()
        for k in prog.labels:
            if k in labels:
                raise SystemExit(f"duplicate event label {k}")
        labels.update(prog.labels)
        used |= prog.bits_used
        rom.place(p["event_region"], code, f"{p['name']}_events", p["event_patch"], at=org,
                  reason=f"{p['name']} event scripts ({len(code)} bytes) from events/{p['name']}/events.evt",
                  consumer="event interpreter via 24-bit trigger pointers, NPC vectors, call/jump operands")
        notes["event_listings"][p["name"]] = prog.listing_text()
    unused = set(bits) - used
    npc_switch_used = set()

    # ---- maps -------------------------------------------------------------------------------
    content = {"records": {k: [] for k in ("EVENT_TRIGGERS", "NPC_PROPS", "SHORT_ENTRANCES", "LONG_ENTRANCES")},
               "props": {}, "layouts": {}, "vectors": [], "vector_labels": []}
    notes["maps"] = {}
    for p in pkgs:
        for mp in p["map_pkgs"]:
            m = mp.map_id
            if m >= 0x1FE or m < 3:
                raise SystemExit(f"map {m:03X}: IDs $000-$002 (world) and $1FE/$1FF (engine previous/parent) are not assignable")
            rep = mp.validate(rom.clean)
            p_init = snes_to_pc(MAP_INIT_EVENTS) + 3 * m
            if rom.clean[p_init:p_init + 3] != EVENT_RETURN_PTR:
                raise SystemExit(f"map {m:03X}: startup event is not EventReturn")
            lay = {}
            for layer in ("bg1", "bg2"):
                spec = mp.map.get(layer, {})
                idx = int(spec.get("layout_index", "0"), 16)
                data = mp.compile_layer(rom.clean, layer)
                if data is not None:
                    lz = compress_literal(data)
                    assert decompress(lz) == data
                    s = rom.place("MAP_LAYOUTS", lz, f"layout_{idx:03X}_{mp.map_id:03X}_{layer}", p["layout_patch"],
                                  reason=f"map {m:03X} {layer.upper()} layout ${idx:03X} ({mp.w}x{mp.h}, literal LZSS {len(lz)} B)",
                                  consumer=f"LoadMapTiles via MAPX_SUBTILEMAP_PTRS[${idx:03X}]")
                    if idx in content["layouts"]:
                        raise SystemExit(f"layout index {idx:03X} assigned twice")
                    content["layouts"][idx] = s
                    lay[layer] = (idx, fmt_snes(s), len(lz))
                else:
                    lay[layer] = (idx, "vanilla", 0)
            bg1i, bg2i = lay["bg1"][0], lay["bg2"][0]
            if m in content["props"]:
                raise SystemExit(f"map {m:03X} defined twice")
            content["props"][m] = mp.props_row(bg1i, bg2i, 0)
            for n in mp.npcs:
                vi = len(content["vectors"])
                content["vectors"].append(labels[n["event"]])
                content["vector_labels"].append(f"{mp.map_id:03X}:{n['name']}->{n['event']}")
                sw = names[n["switch"]]
                npc_switch_used.add(n["switch"])
                kw = dict(event_snes=0xCA0000 + map_foundation.NPC_VECTOR_FLAG + vi, switch=sw, x=n["x"], y=n["y"],
                          gfx=int(n["gfx"].split()[0], 16), pal=n["pal"], speed=n["speed"],
                          react=REACT[n.get("react", "FACE_PLAYER")])
                if "anim" in n:
                    a = n["anim"]
                    kw["anim"] = (a["type"], int(a["frame"].split()[0], 16), a["speed"])
                else:
                    kw["direction"] = DIRS[n["direction"]]
                    kw["movement"] = 0
                rec = encode_npc(**kw)
                if rec[4] & 0x80:
                    raise SystemExit("routed NPC must not be a special NPC")
                content["records"]["NPC_PROPS"].append((m, rec, f"{n['name']} (vector #{vi})"))
            for t in mp.triggers:
                content["records"]["EVENT_TRIGGERS"].append(
                    (int(t["map"], 16), bytes([t["x"], t["y"]]) + event_offset(labels[t["event"]]).to_bytes(3, "little"), t["event"]))
            for e in mp.exits["short_entrances"]:
                content["records"]["SHORT_ENTRANCES"].append((int(e["map"], 16), short_rec(e), f"exit->{e['dest_map']}"))
            for e in mp.exits["long_entrances"]:
                content["records"]["LONG_ENTRANCES"].append((int(e["map"], 16), long_rec(e), f"long->{e['dest_map']}"))
            notes["maps"][f"{m:03X}"] = {"package": p["name"], "walkability": rep, "layouts": lay,
                                         "runtime_grid": mp.walk_grid_runtime(rom.clean),
                                         "props_row": content["props"][m].hex(" ").upper()}
        # cross-map records (QA access etc.)
        for t in p["records"].get("triggers", []):
            content["records"]["EVENT_TRIGGERS"].append(
                (int(t["map"], 16), bytes([t["x"], t["y"]]) + event_offset(labels[t["event"]]).to_bytes(3, "little"), t["event"]))
        for o in p["records"].get("short_entrance_overrides", []):
            hit = [i for i, (m, r, l) in enumerate(content["records"]["SHORT_ENTRANCES"])
                   if m == int(o["map"], 16) and list(r[:2]) == o["src"]]
            if len(hit) != 1:
                raise SystemExit(f"{p['name']}: override target {o['map']} {o['src']} not found exactly once")
            i = hit[0]
            content["records"]["SHORT_ENTRANCES"][i] = (int(o["map"], 16), short_rec(o), f"exit->{o['dest_map']} (QA override)")
    unused -= {n for n in npc_switch_used}
    if unused:
        raise SystemExit(f"allocated bits never used: {sorted(unused)}")

    # ---- reserved vanilla tiles for cross-map triggers must be free ---------------------------
    vt = map_foundation.vanilla_tables(rom.clean)
    for m, rec, label in content["records"]["EVENT_TRIGGERS"]:
        if m < 0x19F:
            for r in vt["EVENT_TRIGGERS"].records[m]:
                if r[:2] == rec[:2]:
                    raise SystemExit(f"{label}: vanilla trigger already on map {m:03X} {rec[0]},{rec[1]}")
            for r in vt["SHORT_ENTRANCES"].records[m]:
                if r[:2] == rec[:2]:
                    raise SystemExit(f"{label}: vanilla entrance on map {m:03X} {rec[0]},{rec[1]}")

    fnotes, bases = map_foundation.build(rom, content)
    notes["map_foundation"] = fnotes

    # ---- QA-only overrides of content bytes (QA packages) ------------------------------------
    for p in pkgs:
        for o in p["records"].get("byte_overrides", []):
            a = labels[o["label"]] + o["offset"]
            exp, new = bytes.fromhex(o["expect"]), bytes.fromhex(o["new"])
            rom.override(a, exp, new, o["patch_id"], o["owner"], consumer=o["consumer"], reason=o["reason"])
    notes["labels"] = {k: fmt_snes(v) for k, v in labels.items() if v >= 0xF00000}
    notes["bits"] = {k: f"${v:03X}" for k, v in names.items()}
    return notes
