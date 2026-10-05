"""N1xx-N3xx - TECH v0.5 MONSTER EXPANSION FOUNDATION (all v0.5 targets).

Monster IDs are already 9-bit in the Rev 1 engine (formation msb byte; 16-bit IDs in battle RAM;
$1FF = empty slot), but every monster-indexed table holds only 384 entries, so IDs $180+
would read the next table. This module:
  1. relocates the 384-entry monster tables (+ AI, names, graphics properties) into
     MONSTER_EXPANSION with 512 entries ($000-$1FF), vanilla entries byte-identical;
  2. relocates the formation tables (576 -> 1024 formations);
  3. retargets all 71 consumers (data/monster_relocation_v05.json) - operand bytes only;
  4. graphics-property slots: vanilla slots $180-$19F are esper/Imp graphics, so monsters
     $180-$1FE use slots $1A0-$21E; two hooks apply slot(id) = id < $180 ? id : id + $20
     (battle loader C1:2058, Sketch loader C2:F5F1);
  5. Rage/Veldt: unchanged engine policy (C2:4A09 skips IDs >= $100 for Rage learning,
     C2:49E9 skips them for Veldt registration); builder also forces the formation no-Veldt flag.
"""
import json, os
from ff6x.asm65816 import Asm
from ff6x.hirom import snes_to_pc, fmt_snes
from ff6x.monsters import MonsterSource, FormationSource, NEW_ID_MIN, NULL_ID

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELOC = json.load(open(os.path.join(HERE, "data", "monster_relocation_v05.json")))

IDS = 512
GFX_SLOTS = 0x21F                  # $000-$19F vanilla + $1A0-$21E for monsters $180-$1FE
GFX_REMAP = 0x20
FORMATIONS = 1024
ROUTER_ORG = 0xF01200
HOOK1 = (0xC12058, bytes.fromhex("BD 01 20 0A 0A 18 7D 01 20"))   # LDA $2001,X / ASL / ASL / CLC / ADC $2001,X
HOOK1_NEXT = (0xC12061, bytes.fromhex("AA BF 02 70 D2"))           # TAX / LDA MonsterGfxProp+2,X (retargeted)
HOOK2 = (0xC2F5F1, bytes.fromhex("BD 01 20 AA"))                   # LDA $2001,X / TAX
HOOK2_NEXT = (0xC2F5F5, bytes.fromhex("7B E2 20 22 C0 24 C1"))     # shorta0 / JSL LoadSketchMonsterGfx
COLO_SITE = (0xC22F75, bytes.fromhex("AE D4 3E E0 3E 02"))         # LDX wBattleID / CPX #$023E (BCC at C2:2F7B kept)
COLO_NEXT = (0xC22F7B, bytes.fromhex("90 0F AD 08 02"))
RAGE_GUARDS = [(0xC24A09, bytes.fromhex("BD 02 20 D0 0F")),         # LearnRage: skip if id >= $100
               (0xC249E9, bytes.fromhex("BD 02 20 D0 14")),         # Veldt registration: skip if id >= $100
               (0xC249E3, bytes.fromhex("89 02 D0 1F"))]            # formation no-Veldt flag ($2F4B bit 1)

TABLE_REGION = {
    "MONSTER_PROP": "MONX_PROP", "MONSTER_NAME": "MONX_NAME", "MONSTER_SPECIAL_NAME": "MONX_SPECIAL_NAME",
    "MONSTER_ITEMS": "MONX_ITEMS", "MONSTER_CONTROL": "MONX_CONTROL", "MONSTER_SKETCH": "MONX_SKETCH",
    "MONSTER_SPECIAL_ANIM": "MONX_SPECIAL_ANIM", "MONSTER_OVERLAP": "MONX_OVERLAP",
    "MONSTER_GFX_PROP": "MONX_GFX_PROP", "FORMATION_PROP": "FORMX_PROP", "FORMATION_MONSTERS": "FORMX_MONSTERS",
    "AI_SCRIPT_PTRS": "MONX_AI_PTRS", "AI_SCRIPT": "MONX_AI_SCRIPT",
}
PATCH_ID = {k: f"N1{i:02d}_{k}" for i, k in enumerate(TABLE_REGION, 1)}
DEFAULT = {"MONSTER_PROP": b"\x00" * 32, "MONSTER_NAME": b"\xFF" * 10, "MONSTER_SPECIAL_NAME": b"\xFF" * 10,
           "MONSTER_ITEMS": b"\xFF" * 4, "MONSTER_CONTROL": b"\xFF" * 4, "MONSTER_SKETCH": b"\xFF" * 2,
           "MONSTER_SPECIAL_ANIM": b"\x00", "MONSTER_OVERLAP": b"\x00", "MONSTER_GFX_PROP": b"\x00" * 5}
CONTENT_KEY = {"MONSTER_PROP": "prop", "MONSTER_NAME": "name", "MONSTER_SPECIAL_NAME": "special_name",
               "MONSTER_ITEMS": "items", "MONSTER_CONTROL": "control", "MONSTER_SKETCH": "sketch",
               "MONSTER_SPECIAL_ANIM": "special_anim", "MONSTER_OVERLAP": "overlap"}


def gfx_slot(mid):
    return mid if mid < NEW_ID_MIN else mid + GFX_REMAP


def vanilla_blob(clean, name):
    t = RELOC["tables"][name]
    a, b = snes_to_pc(int(t["old_base"], 16)), snes_to_pc(int(t["old_end"], 16))
    return bytes(clean[a:b + 1])


def region(rom, name):
    r = rom.alloc.region(TABLE_REGION[name], rom.target)
    return 0xC00000 + r["pc_start"], r["pc_end"] - r["pc_start"] + 1


def build_router(rom):
    a = Asm(ROUTER_ORG)
    a.label("MonsterGfxSlot5")          # .a16 .i16, X = slot*2; returns A = gfx_slot(id)*5 (caller: TAX)
    a.lda_abs_x(0x2001)
    a.cmp_imm16(NEW_ID_MIN)
    a.bcc("S1")
    a.adc_imm16(GFX_REMAP - 1)          # carry set -> +$20
    a.label("S1")
    a.pha()
    a.asl_a()
    a.asl_a()
    a.clc()
    a.adc_sr(0x01)
    a.plx()                             # discard (X is reloaded by the caller's TAX)
    a.rtl()
    a.label("MonsterGfxSlotSketch")     # .a16 .i16, X = slot*2; returns X = gfx_slot(id)
    a.lda_abs_x(0x2001)
    a.cmp_imm16(NEW_ID_MIN)
    a.bcc("S2")
    a.adc_imm16(GFX_REMAP - 1)
    a.label("S2")
    a.tax()
    a.rtl()
    a.label("ColosseumRangeCheck")      # .i16: C=1 only for colosseum battles $23E/$23F (vanilla: any id >= $23E)
    a.ldx_abs(0x3ED4)                   # wBattleID (as the replaced LDX)
    a.cpx_imm16(0x023E)
    a.bcc("C1")                         # < $23E -> C=0 -> caller's BCC: not colosseum
    a.cpx_imm16(0x0240)
    a.bcs("C2")
    a.sec()
    a.rtl()
    a.label("C2")
    a.clc()                             # >= $240 (new formations) -> not colosseum
    a.label("C1")
    a.rtl()
    code = a.assemble()
    rom.place("ENGINE_CODE", code, "MonsterGfxSlotRouters", "N300_GFX_SLOT_ROUTERS", at=ROUTER_ORG,
              reason="graphics-property slot remap (monsters $180-$1FE -> slots $1A0-$21E) + colosseum range check",
              consumer="JSL from C1:2058 (battle monster loader), C2:F5F1 (Sketch), C2:2F75 (colosseum detection)")
    for (site, exp), nxt in ((HOOK1, HOOK1_NEXT), (HOOK2, HOOK2_NEXT)):
        pc = snes_to_pc(nxt[0])
        if rom.clean[pc:pc + len(nxt[1])] != nxt[1]:
            raise SystemExit(f"N30x: context bytes after hook {fmt_snes(site)} mismatch")
    j1 = a.labels["MonsterGfxSlot5"]; j2 = a.labels["MonsterGfxSlotSketch"]
    jsl = lambda t: bytes([0x22, t & 0xFF, (t >> 8) & 0xFF, t >> 16])
    rom.patch(HOOK1[0], HOOK1[1], jsl(j1) + b"\xEA" * 5, "N301_GFX_SLOT_HOOK_BATTLE",
              consumer="LoadMonsterGfxProp (C1:204E) monster id*5 computation",
              reason="LDA $2001,X/ASL/ASL/CLC/ADC $2001,X -> JSL MonsterGfxSlot5 + 5x NOP", claim="MONSTER_GFX_HOOK_SITE_1")
    rom.patch(HOOK2[0], HOOK2[1], jsl(j2), "N302_GFX_SLOT_HOOK_SKETCH",
              consumer="battle animation init $0B (Sketch): monster id -> LoadSketchMonsterGfx",
              reason="LDA $2001,X/TAX -> JSL MonsterGfxSlotSketch", claim="MONSTER_GFX_HOOK_SITE_2")
    pc = snes_to_pc(COLO_NEXT[0])
    if rom.clean[pc:pc + len(COLO_NEXT[1])] != COLO_NEXT[1]:
        raise SystemExit("N303: context after colosseum check mismatch")
    j3 = a.labels["ColosseumRangeCheck"]
    rom.patch(COLO_SITE[0], COLO_SITE[1], jsl(j3) + b"\xEA\xEA", "N303_FORMATION_COLOSSEUM_RANGE",
              consumer="InitParty C2:2F75 colosseum detection (battle id >= $23E)",
              reason="LDX wBattleID/CPX #$023E -> JSL ColosseumRangeCheck + 2x NOP; colosseum iff $23E <= id < $240 so new formations $240-$3FF load normally",
              claim="FORMATION_COLOSSEUM_CHECK_SITE")
    return a.listing_text()


def retarget(rom, name, new_base, patch_id):
    t = RELOC["tables"][name]
    old = int(t["old_base"], 16)
    for c in t["consumers"]:
        snes = int(c["snes"], 16)
        ins = bytes.fromhex(c["bytes"])
        if bytes(rom.clean[snes_to_pc(snes):snes_to_pc(snes) + len(ins)]) != ins:
            raise SystemExit(f"{patch_id}: consumer bytes changed at {c['snes']}")
        if c["kind"] == "long":
            op = old + c["disp"]
            if ins[1:] != op.to_bytes(3, "little"): raise SystemExit(f"{patch_id}: operand mismatch {c['snes']}")
            new = (new_base + c["disp"]).to_bytes(3, "little")
        elif c["kind"] == "imm_bank":
            if ins[1] != old >> 16: raise SystemExit(f"{patch_id}: bank mismatch {c['snes']}")
            new = bytes([new_base >> 16])
        elif c["kind"] == "imm_near":
            v = (old & 0xFFFF) + c["disp"]
            if ins[1:3] != v.to_bytes(2, "little"): raise SystemExit(f"{patch_id}: near mismatch {c['snes']}")
            new = ((new_base & 0xFFFF) + c["disp"]).to_bytes(2, "little")
        else:
            raise SystemExit("unknown consumer kind")
        rom.patch(snes + 1, ins[1:1 + len(new)], new, patch_id,
                  consumer=f"{fmt_snes(snes)} opcode {ins[0]:02X} ({c['kind']}) reads {name}",
                  reason=f"{c['kind']} operand -> {fmt_snes(new_base)} + {c['disp']}", retarget=True)
    return len(t["consumers"])


def build(rom, target, alloc, meta, gfx_override=None):
    clean = rom.clean
    for snes, exp in RAGE_GUARDS:
        if clean[snes_to_pc(snes):snes_to_pc(snes) + len(exp)] != exp:
            raise SystemExit(f"N: Rage/Veldt guard assert failed at {fmt_snes(snes)}")
    notes = {"monsters": {}, "formations": {}}
    mons = [MonsterSource(os.path.join(HERE, "monsters", m)) for m in meta.get("monsters", [])]
    ids = [m.id for m in mons]
    if len(ids) != len(set(ids)): raise SystemExit("duplicate monster id")
    comp = {m.id: m.compile(clean) for m in mons}

    tables = {}
    # per-ID tables
    for name in CONTENT_KEY:
        t = RELOC["tables"][name]
        rs, cnt = t["record_size"], t["vanilla_count"]
        van = vanilla_blob(clean, name)[:rs * cnt]
        recs = [van[rs * i:rs * i + rs] for i in range(cnt)] + [DEFAULT[name]] * (IDS - cnt)
        for mid, c in comp.items():
            recs[mid] = c[CONTENT_KEY[name]]
            assert len(recs[mid]) == rs
        tables[name] = b"".join(recs)
    # graphics properties (slot layout)
    van = vanilla_blob(clean, "MONSTER_GFX_PROP")
    slots = [van[5 * i:5 * i + 5] for i in range(len(van) // 5)]            # 416 vanilla slots
    slots += [DEFAULT["MONSTER_GFX_PROP"]] * (GFX_SLOTS - len(slots))
    for mid, c in comp.items():
        gp = (gfx_override or {}).get(mid, c["gfx_prop"])   # TECH v0.6 custom assets (patches/enemy_v06.py)
        if gp is None:
            raise SystemExit(f"monster {mid:03X}: custom graphics but no enemy-asset gfx_prop")
        c["gfx_prop"] = gp
        slots[gfx_slot(mid)] = gp
    tables["MONSTER_GFX_PROP"] = b"".join(slots)
    # AI: vanilla scripts at their original offsets, then new scripts, then a default empty script
    van_ptrs = vanilla_blob(clean, "AI_SCRIPT_PTRS")
    ai_blob = bytearray(vanilla_blob(clean, "AI_SCRIPT"))
    ptrs = [van_ptrs[2 * i] | van_ptrs[2 * i + 1] << 8 for i in range(384)]
    default_off = len(ai_blob); ai_blob += b"\xFF\xFF"
    ptrs += [default_off] * (IDS - 384)
    for mid, c in sorted(comp.items()):
        ptrs[mid] = len(ai_blob); ai_blob += c["ai"]
        notes["monsters"][f"{mid:03X}"] = {"ai_offset": f"{ptrs[mid]:04X}", "ai": c["ai"].hex(" ").upper()}
    tables["AI_SCRIPT_PTRS"] = b"".join(p.to_bytes(2, "little") for p in ptrs)
    tables["AI_SCRIPT"] = bytes(ai_blob)
    # formations
    fp = vanilla_blob(clean, "FORMATION_PROP")[:4 * 576]
    fm = vanilla_blob(clean, "FORMATION_MONSTERS")[:15 * 576]
    fprops = [fp[4 * i:4 * i + 4] for i in range(576)] + [b"\x00" * 4] * (FORMATIONS - 576)
    fmons = [fm[15 * i:15 * i + 15] for i in range(576)] + [b"\x00" * 15] * (FORMATIONS - 576)
    for f in meta.get("formations", []):
        fs = FormationSource(os.path.join(HERE, "formations", f + ".json"))
        if not 0x240 <= fs.id < FORMATIONS: raise SystemExit(f"formation {fs.id:03X} must be in $240-$3FF")
        rec, aux = fs.compile(clean, set(ids))
        fmons[fs.id], fprops[fs.id] = rec, aux
        notes["formations"][f"{fs.id:03X}"] = {"monsters": rec.hex(" ").upper(), "aux": aux.hex(" ").upper()}
    tables["FORMATION_PROP"] = b"".join(fprops)
    tables["FORMATION_MONSTERS"] = b"".join(fmons) + b"\x00" * 16          # loader copies 16 bytes

    # static equivalence of vanilla entries
    for name in CONTENT_KEY:
        t = RELOC["tables"][name]; n = t["record_size"] * t["vanilla_count"]
        assert tables[name][:n] == vanilla_blob(clean, name)[:n], name
    assert tables["MONSTER_GFX_PROP"][:len(van)] == van
    assert tables["AI_SCRIPT"][:len(vanilla_blob(clean, "AI_SCRIPT"))] == vanilla_blob(clean, "AI_SCRIPT")
    assert tables["AI_SCRIPT_PTRS"][:768] == van_ptrs[:768]

    bases = {}
    for name, blob in tables.items():
        start, size = region(rom, name)
        if len(blob) > size: raise SystemExit(f"{name}: {len(blob)} bytes exceed {TABLE_REGION[name]}")
        rom.place(TABLE_REGION[name], blob, name.lower() + "_x", PATCH_ID[name], at=start,
                  reason=f"{name} relocated ({len(blob)} bytes); vanilla entries byte-identical; "
                         f"content: {sorted(f'{i:03X}' for i in comp) or 'none'}",
                  consumer=f"{len(RELOC['tables'][name]['consumers'])} retargeted consumers")
        bases[name] = start
        notes.setdefault("tables", {})[name] = {"snes": fmt_snes(start), "bytes": len(blob), "region_bytes": size}
    if bases["MONSTER_SPECIAL_NAME"] & 0xFFFF > 0x10000 - 10 * IDS or bases["MONSTER_NAME"] & 0xFFFF > 0x10000 - 10 * IDS:
        raise SystemExit("name tables must not cross a bank for 16-bit near arithmetic")
    notes["retargets"] = {n: retarget(rom, n, b, f"N200_RETARGET_{n}") for n, b in bases.items()}
    notes["router_listing"] = build_router(rom)

    # QA-only vanilla overrides (event battle group)
    qa = meta.get("qa_overrides")
    if qa:
        q = json.load(open(os.path.join(HERE, qa)))
        for g in q.get("event_battle_groups", []):
            grp = int(g["group"], 16); f1, f2 = int(g["formation_1"], 16), int(g["formation_2"], 16)
            a = 0xCF5000 + 4 * grp
            new = f1.to_bytes(2, "little") + f2.to_bytes(2, "little")
            rom.patch(a, bytes.fromhex(g["expect"]), new, g["patch_id"], consumer=g["consumer"],
                      reason=g["reason"], claim=g["claim"])
            notes["qa_event_battle_groups"] = notes.get("qa_event_battle_groups", []) + [
                {"group": f"${grp:02X}", "snes": fmt_snes(a), "new": new.hex(" ").upper()}]
    for mid, m in zip(ids, mons):
        notes["monsters"][f"{mid:03X}"].update({"name": m.monster["name"], "gfx_slot": f"{gfx_slot(mid):03X}",
                                                "gfx_prop": comp[mid]["gfx_prop"].hex(" ").upper(),
                                                "prop": comp[mid]["prop"].hex(" ").upper(),
                                                "items": comp[mid]["items"].hex(" ").upper()})
    ai_used = len(ai_blob); _, ai_cap = region(rom, "AI_SCRIPT")
    notes["capacity"] = {
        "monster_ids": "vanilla $000-$17F (384); new $180-$1FE (127); $1FF = engine null (empty formation slot)",
        "assigned_new_ids": [f"{i:03X}" for i in sorted(ids)],
        "formations": f"1024 ($000-$3FF); vanilla 576 ($000-$23F); new $240-$3FF (448); "
                      f"{len(meta.get('formations', []))} used",
        "ai_script_bytes": f"{ai_used} used of {ai_cap} (vanilla {len(vanilla_blob(clean, 'AI_SCRIPT'))})",
        "gfx_prop_slots": f"{GFX_SLOTS} ($000-$21E)",
        "palette_units": "vanilla table 768 x 16 B; highest used index $28F (4bpp: 2 units) - new palettes need a later relocation (7 consumers) or audited tail units",
    }
    return notes
