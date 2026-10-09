"""E1xx-E4xx - TECH v0.6 ENEMY ASSET + MAGIC POINT FOUNDATION (all v0.6 targets).

1. MonsterPal relocated to ENEMYX_PAL (1024 x 16-byte units; vanilla units $000-$2FF byte-identical,
   $300-$3FF for new palettes). 6 consumers retargeted.
2. MonsterStencil relocated to ENEMYX_STENCIL (header + 256 small + 191 large maps; vanilla maps
   byte-identical at the same indices, header pointers re-based). 7 symbolic consumers + 1 literal
   bank byte in the colosseum menu (C3:AFFD) retargeted.
3. Custom tile data in ENEMYX_GFX (FC:0000-FD:FFFF); graphics index base FB:0000 selected by
   MonsterGfxProp byte2 bit5 through a hook in AddMonsterGfxOffset (C1:20FF), which both monster
   loaders (battle C1:204E and summon/Sketch C1:24E9) use.
4. BattleMagicPoints relocated to FORMX_MAGIC_POINTS (1024 battles) and the battle-win bound
   C2:5D97 CPX #$0200 -> #$0400; vanilla $000-$1FF identical, $200-$23F = 0 (vanilla gives 0),
   $240-$3FF from formation sources (default 0).
"""
import json, os
from ff6x.asm65816 import Asm
from ff6x.hirom import snes_to_pc, fmt_snes
from ff6x.enemygfx import EnemyAsset, AssetError, VRAM_MAPS, SMALL, LARGE
from ff6x.monsters import FormationSource

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELOC = json.load(open(os.path.join(HERE, "data", "enemy_relocation_v06.json")))

PAL_UNITS, PAL_VANILLA = 1024, 768
SMALL_MAPS, LARGE_MAPS_MAX = 256, 191
STENCIL_SMALL_OFF, STENCIL_LARGE_OFF = 4, 4 + 8 * 256
GFX_BASE = 0xFB0000
ROUTER_ORG = 0xF01240
OFFSET_HOOK = (0xC120FF, bytes.fromhex("A5 64 18 69 00"))                  # AddMonsterGfxOffset: LDA $64/CLC/ADC #<MonsterGfx
OFFSET_REST = (0xC12104, bytes.fromhex("85 64 A5 65 69 70 85 65 A5 66 69 E9 85 66 60"))
MP_SITE = (0xC25D94, bytes.fromhex("AE D4 3E E0 00 02 B0 04"))            # LDX wBattleID / CPX #$0200 / BCS
MP_BATTLES = 1024
REGION = {"MONSTER_PAL": "ENEMYX_PAL", "MONSTER_STENCIL": "ENEMYX_STENCIL", "BATTLE_MAGIC_POINTS": "FORMX_MAGIC_POINTS"}
PATCH = {"MONSTER_PAL": "E101_MONSTER_PAL", "MONSTER_STENCIL": "E102_MONSTER_STENCIL",
         "BATTLE_MAGIC_POINTS": "E104_BATTLE_MAGIC_POINTS"}


def vanilla_blob(clean, name):
    t = RELOC["tables"][name]
    a, b = snes_to_pc(int(t["old_base"], 16)), snes_to_pc(int(t["old_end"], 16))
    return bytes(clean[a:b + 1])


class Prepared:
    pass


def prepare(rom, target, alloc, meta):
    """Compile custom assets and allocate palette units / stencils / graphics addresses.
    Returns a Prepared object whose .gfx_props feeds monster_v05.build()."""
    clean = rom.clean
    st = Prepared()
    st.assets, st.gfx_props, st.notes = {}, {}, {}
    van_st = vanilla_blob(clean, "MONSTER_STENCIL")
    sp = van_st[0] | van_st[1] << 8; lp = van_st[2] | van_st[3] << 8
    assert (sp, lp) == (0xA824, 0xAC24)
    st.small = [van_st[4 + 8 * i:12 + 8 * i] for i in range(128)]
    st.large = [van_st[0x404 + 32 * i:0x424 + 32 * i] for i in range(48)]
    st.pal_units = []                                  # new palettes (32 B each = 2 units), from unit $300
    st.gfx_blob = bytearray()
    greg = alloc.region("ENEMYX_GFX", target)
    st.gfx_start = 0xC00000 + greg["pc_start"]
    st.gfx_cap = greg["pc_end"] - greg["pc_start"] + 1
    for m in meta.get("monsters", []):
        folder = os.path.join(HERE, "monsters", m)
        g = json.load(open(os.path.join(folder, "graphics.json")))
        if not g.get("custom"):
            continue
        mid = int(json.load(open(os.path.join(folder, "monster.json")))["id"], 16)
        a = EnemyAsset(folder)
        # palette (dedupe)
        if a.palette in st.pal_units:
            pal = PAL_VANILLA + 2 * st.pal_units.index(a.palette)
        else:
            st.pal_units.append(a.palette); pal = PAL_VANILLA + 2 * (len(st.pal_units) - 1)
        if pal + 1 >= PAL_UNITS:
            raise SystemExit("ENEMYX_PAL: out of palette units")
        # stencil (reuse vanilla / earlier identical map, else allocate)
        lst, cap = (st.small, SMALL_MAPS) if a.kind == SMALL else (st.large, LARGE_MAPS_MAX)
        reused = a.stencil in lst
        if reused:
            sidx = lst.index(a.stencil)
        else:
            lst.append(a.stencil); sidx = len(lst) - 1
        if sidx >= cap:
            raise SystemExit(f"ENEMYX_STENCIL: no free {a.kind} stencil")
        # graphics (8-byte aligned; index = (addr - FB:0000) / 8)
        while len(st.gfx_blob) % 8:
            st.gfx_blob.append(0)
        addr = st.gfx_start + len(st.gfx_blob)
        st.gfx_blob += a.data
        if len(st.gfx_blob) > st.gfx_cap:
            raise SystemExit("ENEMYX_GFX full")
        gidx = (addr - GFX_BASE) // 8
        st.gfx_props[mid] = a.gfx_prop(gidx, pal, sidx)
        st.assets[mid] = a
        st.notes[f"{mid:03X}"] = {
            "source": os.path.relpath(a.image, HERE).replace(os.sep, "/"), "bpp": a.bpp, "stencil_kind": a.kind,
            "image_px": [a.w, a.h], "tiles_cols_rows": [a.cols, a.rows_used], "tile_count": a.tile_count,
            "data_bytes": len(a.data), "gfx_snes": fmt_snes(addr), "gfx_index": f"{gidx:04X}",
            "palette_index": f"{pal:03X}", "palette_snes": fmt_snes(0xC00000 + alloc.region("ENEMYX_PAL", target)["pc_start"] + 16 * pal),
            "palette_bgr555": a.palette[:32 if a.bpp == 4 else 16].hex(" ").upper(),
            "stencil_index": f"{sidx:02X}", "stencil_new": not reused, "stencil": a.stencil.hex(" ").upper(),
            "gfx_prop": st.gfx_props[mid].hex(" ").upper(), "empty_rows_filled": a.filled_gaps}
    return st


def check_vram_box(asset, vmap, slot, what):
    """Refuse a custom sprite larger than the formation's VRAM-map box for its slot (it would be clipped)."""
    boxes = VRAM_MAPS[vmap]
    if slot >= len(boxes):
        raise AssetError(f"{what}: slot {slot} has no box in VRAM map {vmap}")
    bc, br = boxes[slot]
    if asset.cols > bc or asset.rows_used > br:
        raise AssetError(f"{what}: {asset.cols}x{asset.rows_used} tiles exceeds VRAM box {bc}x{br} (map {vmap}, slot {slot})")
    return bc, br


def retarget(rom, name, new_base, patch_id):
    t = RELOC["tables"][name]
    old = int(t["old_base"], 16)
    for c in t["consumers"]:
        snes = int(c["snes"], 16)
        ins = bytes.fromhex(c["bytes"])
        if bytes(rom.clean[snes_to_pc(snes):snes_to_pc(snes) + len(ins)]) != ins:
            raise SystemExit(f"{patch_id}: consumer bytes changed at {c['snes']}")
        k = c["kind"]
        if k == "long":
            if ins[1:] != (old + c["disp"]).to_bytes(3, "little"): raise SystemExit(f"{patch_id}: operand {c['snes']}")
            new = (new_base + c["disp"]).to_bytes(3, "little")
        elif k == "long_bank":
            if ins[1:] != (old & 0xFF0000).to_bytes(3, "little"): raise SystemExit(f"{patch_id}: bank operand {c['snes']}")
            new = (new_base & 0xFF0000).to_bytes(3, "little")
        elif k == "imm_bank":
            if ins[1] != old >> 16: raise SystemExit(f"{patch_id}: bank imm {c['snes']}")
            new = bytes([new_base >> 16])
        elif k == "imm_near":
            if ins[1:3] != ((old & 0xFFFF) + c["disp"]).to_bytes(2, "little"): raise SystemExit(f"{patch_id}: near {c['snes']}")
            new = ((new_base & 0xFFFF) + c["disp"]).to_bytes(2, "little")
        else:
            raise SystemExit("unknown consumer kind")
        rom.patch(snes + 1, ins[1:1 + len(new)], new, patch_id,
                  consumer=f"{fmt_snes(snes)} opcode {ins[0]:02X} ({k}) reads {name}" + (f" [{c['manual']}]" if c.get("manual") else ""),
                  reason=f"{k} operand -> {fmt_snes(new_base)} + {c['disp']}", retarget=True)
    return len(t["consumers"])


def build_router(rom):
    a = Asm(ROUTER_ORG)
    a.label("EnemyGfxBase")          # .a8, DB=$7E, D=0 (btlgfx); $64-$66 = graphics offset (index*8)
    a.lda_abs(0x81AC)                # $81AC bit4 = MonsterGfxProp byte2 bit5 (written by both prop loaders)
    a.and_imm8(0x10)
    a.bne("EXP")
    a.lda_dp(0x64); a.clc(); a.adc_imm8(0x00); a.sta_dp(0x64)     # vanilla: + E9:7000 (MonsterGfx)
    a.lda_dp(0x65); a.adc_imm8(0x70); a.sta_dp(0x65)
    a.lda_dp(0x66); a.adc_imm8(0xE9); a.sta_dp(0x66)
    a.rtl()
    a.label("EXP")                   # expansion: + FB:0000
    a.lda_dp(0x66); a.clc(); a.adc_imm8(GFX_BASE >> 16); a.sta_dp(0x66)
    a.rtl()
    code = a.assemble()
    rom.place("ENGINE_CODE", code, "EnemyGfxBase", "E300_ENEMY_GFX_BASE_ROUTER", at=ROUTER_ORG,
              reason="graphics data base select: E9:7000 (vanilla) or FB:0000 (MonsterGfxProp byte2 bit5)",
              consumer="JSL from AddMonsterGfxOffset C1:20FF (battle loader fallthrough + summon/Sketch JMP)")
    pc = snes_to_pc(OFFSET_REST[0])
    if rom.clean[pc:pc + len(OFFSET_REST[1])] != OFFSET_REST[1]:
        raise SystemExit("E301: AddMonsterGfxOffset body mismatch")
    t = a.labels["EnemyGfxBase"]
    rom.patch(OFFSET_HOOK[0], OFFSET_HOOK[1], bytes([0x22, t & 0xFF, (t >> 8) & 0xFF, t >> 16, 0x60]),
              "E301_ENEMY_GFX_OFFSET_HOOK", consumer="AddMonsterGfxOffset (C1:20FF)",
              reason="LDA $64/CLC/ADC #$00 -> JSL EnemyGfxBase / RTS (rest of the vanilla routine becomes unreachable, unchanged)",
              claim="ENEMY_GFX_OFFSET_HOOK_SITE")
    return a.listing_text()


def build(rom, target, alloc, meta, st):
    clean = rom.clean
    notes = {"assets": st.notes}
    reg = lambda n: alloc.region(n, target)
    base = lambda n: 0xC00000 + reg(n)["pc_start"]
    # 1. palettes
    van_pal = vanilla_blob(clean, "MONSTER_PAL")
    assert len(van_pal) == 16 * PAL_VANILLA
    pal = bytearray(van_pal) + b"".join(st.pal_units)
    pal += b"\x00" * (16 * PAL_UNITS - len(pal))
    assert bytes(pal[:len(van_pal)]) == van_pal
    rom.place("ENEMYX_PAL", bytes(pal), "monster_pal_x", PATCH["MONSTER_PAL"], at=base("ENEMYX_PAL"),
              reason=f"MonsterPal relocated: units $000-$2FF vanilla, {2 * len(st.pal_units)} new units from $300",
              consumer="6 retargeted consumers")
    # 1b. empty palette slot shadow: LoadMonsterPal (C1:22D1) copies 32 bytes from MonsterPal + $FFFF*16
    #     (= base + $FFF0, X wraps to 0 after 16 bytes) for every unused battle palette slot.
    shadow = bytes(clean[snes_to_pc(0xD37810):snes_to_pc(0xD37810) + 16])
    rom.place("ENEMYX_PAL_EMPTY_SLOT", shadow, "monster_pal_empty_slot", "E101_MONSTER_PAL", at=base("ENEMYX_PAL_EMPTY_SLOT"),
              reason="16 vanilla bytes from D3:7810 (what vanilla reads for an empty palette slot at MonsterPal+$FFF0)",
              consumer="LoadMonsterPal empty-slot read (index $FFFF): keeps battle palette RAM identical to vanilla")
    # 2. stencils
    sb = base("ENEMYX_STENCIL")
    hdr = ((sb + STENCIL_SMALL_OFF) & 0xFFFF).to_bytes(2, "little") + ((sb + STENCIL_LARGE_OFF) & 0xFFFF).to_bytes(2, "little")
    small = b"".join(st.small) + b"\x00" * (8 * (SMALL_MAPS - len(st.small)))
    large = b"".join(st.large)
    stencil = hdr + small + large
    if len(stencil) > reg("ENEMYX_STENCIL")["pc_end"] - reg("ENEMYX_STENCIL")["pc_start"] + 1:
        raise SystemExit("ENEMYX_STENCIL overflow")
    van_st = vanilla_blob(clean, "MONSTER_STENCIL")
    assert stencil[4:4 + 0x400] == van_st[4:0x404] and stencil[STENCIL_LARGE_OFF:STENCIL_LARGE_OFF + 48 * 32] == van_st[0x404:0x404 + 48 * 32]
    rom.place("ENEMYX_STENCIL", stencil, "monster_stencil_x", PATCH["MONSTER_STENCIL"], at=sb,
              reason=f"MonsterStencil relocated: header -> {fmt_snes(sb + 4)}/{fmt_snes(sb + STENCIL_LARGE_OFF)}; "
                     f"{len(st.small)} small (128 vanilla) + {len(st.large)} large (48 vanilla) maps",
              consumer="8 retargeted consumers (7 symbolic + colosseum literal C3:AFFD)")
    # 3. graphics data
    if st.gfx_blob:
        rom.place("ENEMYX_GFX", bytes(st.gfx_blob), "enemy_gfx_data", "E103_ENEMY_GFX_DATA", at=st.gfx_start,
                  reason=f"custom enemy tile data for {sorted(f'{m:03X}' for m in st.assets)}",
                  consumer="LoadMonsterGfxTile via graphics index (base FB:0000)")
    # 4. Magic Points
    van_mp = vanilla_blob(clean, "BATTLE_MAGIC_POINTS")
    mp = bytearray(van_mp) + bytes(MP_BATTLES - len(van_mp))
    mp_notes = {}
    for f in meta.get("formations", []):
        fs = FormationSource(os.path.join(HERE, "formations", f + ".json"))
        mp[fs.id] = fs.magic_points
        mp_notes[f"{fs.id:03X}"] = fs.magic_points
        # VRAM box check for custom sprites (no clipping)
        rec, _aux = fs.compile(clean, set(st.assets) | {int(s["monster"], 16) for s in fs.f["slots"] if int(s["monster"], 16) >= 0x180})
        vmap = rec[0] >> 4
        for s in fs.f["slots"]:
            mid, k = int(s["monster"], 16), s["slot"]
            if mid in st.assets:
                bc, br = check_vram_box(st.assets[mid], vmap, k, f"{f}: monster {mid:03X}")
                st.notes[f"{mid:03X}"].setdefault("vram_boxes", {})[f] = f"map {vmap} slot {k}: box {bc}x{br}"
    assert bytes(mp[:512]) == van_mp and bytes(mp[512:576]) == bytes(64)
    rom.place("FORMX_MAGIC_POINTS", bytes(mp), "battle_magic_points_x", PATCH["BATTLE_MAGIC_POINTS"],
              at=base("FORMX_MAGIC_POINTS"),
              reason=f"BattleMagicPoints relocated (1024): $000-$1FF vanilla, $200-$23F = 0, new: {mp_notes or 'none'}",
              consumer="C2:5D9C LDA BattleMagicPoints,X (bound C2:5D97 now #$0400)")
    pc = snes_to_pc(MP_SITE[0])
    if rom.clean[pc:pc + len(MP_SITE[1])] != MP_SITE[1]:
        raise SystemExit("E105: magic point site mismatch")
    rom.patch(0xC25D98, b"\x00\x02", b"\x00\x04", "E105_MAGIC_POINTS_BOUND",
              consumer="battle win C2:5D97 CPX #$0200 / BCS (no magic points for battles >= bound)",
              reason="bound $0200 -> $0400: table covers all 1024 formations; $200-$23F hold 0 = vanilla result",
              claim="MAGIC_POINTS_BOUND_SITE")
    notes["retargets"] = {n: retarget(rom, n, base(REGION[n]), f"E200_RETARGET_{n}") for n in REGION}
    notes["router_listing"] = build_router(rom)
    notes["magic_points"] = mp_notes
    pal_reg = reg("ENEMYX_PAL")
    notes["capacity"] = {
        "palette_units": f"{PAL_UNITS} (vanilla 768); new units used {2 * len(st.pal_units)} of 256 (= {128 - len(st.pal_units)} more 16-colour palettes)",
        "stencils": f"small {len(st.small)}/{SMALL_MAPS}, large {len(st.large)}/{LARGE_MAPS_MAX}",
        "gfx_bytes": f"{len(st.gfx_blob)} used of {st.gfx_cap} in ENEMYX_GFX (FC:0000-FD:FFFF)",
        "magic_points": "1024 battles; new formations $240-$3FF: 0-255 MP each (formation source 'magic_points')",
    }
    return notes
