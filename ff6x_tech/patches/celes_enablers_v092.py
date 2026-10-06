"""TECH v0.9.2 Celes enablers (QA targets only; meta "celes_enablers": True).

E2-E4  battle AI extension (asm/celes_v092/ai_ext.s): FC/FB index >= $40 routed to new routines; HP-percent
       condition, Lightning hit counter / Grounding Field, Overload (Defense + palette), field tick.
E6/E7  palette relocation: MapPal (ED:C480, 48 x 256 B, consumer C0:266D) -> MAPX_MAP_PAL F7:A000 with new map palettes
       from index $30; MapSpritePal (E6:8000, 32 x 32 B, consumers C0:50EE / C0:AA21) -> MAPX_SPRITE_PAL F7:E000 with
       new sprite palettes from index $20. Vanilla entries byte-identical (asserted). New palettes are DERIVED from
       vanilla palettes by the documented transform in palettes/v092/palettes.json (D-14 placeholders).
The map / event / monster / formation parts of the enablers are ordinary source packages (maps/celes_outer_v092,
events/celes_enablers_v092, monsters/qa92_*, formations/qa92_0244.json) built by the existing builders.
"""
import json, os
from ff6x.asm816 import Program
from ff6x.hirom import snes_to_pc, fmt_snes

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PAL, MAP_PAL_N = 0xEDC480, 48
SPR_PAL, SPR_PAL_N = 0xE68000, 32
MON_PAL = 0xD27820                      # vanilla MonsterPal (16 B units); the v0.6 relocation keeps units byte-exact
NEW_MAP_PAL, NEW_SPR_PAL = 0xF7A000, 0xF7E000
CONSUMERS = [("V9210_MAPPAL_OPERAND", 0xC0266D, MAP_PAL, NEW_MAP_PAL, "LoadMapPal C0:265C (LDA f:MapPal,X)"),
             ("V9211_SPRPAL_OPERAND_INIT", 0xC050EE, SPR_PAL, NEW_SPR_PAL, "InitSpritePal C0:50E9 (LDA f:MapSpritePal,X)"),
             ("V9212_SPRPAL_OPERAND_EV60", 0xC0AA21, SPR_PAL, NEW_SPR_PAL, "event cmd $60 C0:A9FA (LDA f:MapSpritePal,X)")]
HOOKS = [("V9201_AI_COND_DISPATCH", 0xC21A91, "AD 2D 3A 0A AA FC 55 1D", "jsr XE2_Cond",
          "AI command $FC dispatch C2:1A91", "conditions >= $40 -> TECH v0.9.2 AI extension (vanilla < $40 unchanged)"),
         ("V9202_AI_MISC_DISPATCH", 0xC21E5E, "A5 B6 0A AA A5 B8 7C 09 1F", "jmp XE2_Misc",
          "battle command $30 (AI $FB) C2:1E5E", "misc effects >= $40 -> TECH v0.9.2 AI extension (vanilla < $40 unchanged)")]


def bgr(c):
    return c & 31, (c >> 5) & 31, (c >> 10) & 31


def derive(raw, t):
    """16-bit BGR555 colours -> transformed colours. desaturate f (toward luma), per-channel tint (r, g, b), gain.
    Colour 0 of each 16-colour row is kept (transparent / backdrop)."""
    out = bytearray(raw)
    for i in range(len(raw) // 2):
        if i % 16 == 0:
            continue
        c = raw[2 * i] | raw[2 * i + 1] << 8
        r, g, b = bgr(c)
        y = 0.30 * r + 0.59 * g + 0.11 * b
        f = t.get("desaturate", 0.0)
        r, g, b = (v + (y - v) * f for v in (r, g, b))
        tr, tg, tb = t.get("tint", [1, 1, 1])
        k = t.get("gain", 1.0)
        r, g, b = (max(0, min(31, int(round(v * m * k)))) for v, m in ((r, tr), (g, tg), (b, tb)))
        n = r | g << 5 | b << 10
        out[2 * i], out[2 * i + 1] = n & 0xFF, n >> 8
    return bytes(out)


def load_palettes():
    return json.load(open(os.path.join(HERE, "palettes", "v092", "palettes.json")))


def palettes(rom, notes):
    clean = rom.clean
    src = load_palettes()
    mp = bytearray(clean[snes_to_pc(MAP_PAL):snes_to_pc(MAP_PAL) + 256 * MAP_PAL_N])
    for p in sorted(src["map_palettes"], key=lambda p: int(p["index"], 16)):
        i = int(p["index"], 16)
        if i != len(mp) // 256:
            raise SystemExit(f"map palette {p['index']}: indices must continue from ${MAP_PAL_N:02X} without gaps")
        b = int(p["from_vanilla_map_palette"], 16)
        mp += derive(clean[snes_to_pc(MAP_PAL) + 256 * b:snes_to_pc(MAP_PAL) + 256 * b + 256], p["transform"])
    if len(mp) > 0x4000 or len(mp) // 256 > 0x3F:
        raise SystemExit("MAPX_MAP_PAL: at most 63 palettes (16 KiB, 6-bit map property index)")
    sp = bytearray(clean[snes_to_pc(SPR_PAL):snes_to_pc(SPR_PAL) + 32 * SPR_PAL_N])
    for p in sorted(src["sprite_palettes"], key=lambda p: int(p["index"], 16)):
        i = int(p["index"], 16)
        if i != len(sp) // 32:
            raise SystemExit(f"sprite palette {p['index']}: indices must continue from ${SPR_PAL_N:02X} without gaps")
        b = int(p["from_vanilla_sprite_palette"], 16)
        sp += derive(clean[snes_to_pc(SPR_PAL) + 32 * b:snes_to_pc(SPR_PAL) + 32 * b + 32], p["transform"])
    assert bytes(mp[:256 * MAP_PAL_N]) == clean[snes_to_pc(MAP_PAL):snes_to_pc(MAP_PAL) + 256 * MAP_PAL_N]
    assert bytes(sp[:32 * SPR_PAL_N]) == clean[snes_to_pc(SPR_PAL):snes_to_pc(SPR_PAL) + 32 * SPR_PAL_N]
    rom.place("MAPX_MAP_PAL", bytes(mp), "map_pal_x", "V9213_MAP_PAL", at=NEW_MAP_PAL,
              reason=f"MapPal relocated: 48 vanilla palettes byte-exact + {len(mp) // 256 - MAP_PAL_N} new (palettes/v092)",
              consumer="LoadMapPal (operand C0:266D retargeted)")
    rom.place("MAPX_SPRITE_PAL", bytes(sp), "sprite_pal_x", "V9214_SPRITE_PAL", at=NEW_SPR_PAL,
              reason=f"MapSpritePal relocated: 32 vanilla palettes byte-exact + {len(sp) // 32 - SPR_PAL_N} new",
              consumer="InitSpritePal / event cmd $60 (operands C0:50EE, C0:AA21 retargeted)")
    for pid, site, old, new, cons in CONSUMERS:
        rom.patch(site, old.to_bytes(3, "little"), new.to_bytes(3, "little"), pid, consumer=cons,
                  reason=f"long operand {fmt_snes(old)} -> {fmt_snes(new)} (relocated palette table, vanilla entries identical)")
    notes["palettes"] = {"map_palettes": len(mp) // 256, "sprite_palettes": len(sp) // 32,
                         "new_map": {p["index"]: derive(clean[snes_to_pc(MAP_PAL) + 256 * int(p["from_vanilla_map_palette"], 16):
                                                              snes_to_pc(MAP_PAL) + 256 * int(p["from_vanilla_map_palette"], 16) + 32],
                                                        p["transform"]).hex(" ").upper() + " ..." for p in src["map_palettes"]},
                         "new_sprite": {p["index"]: sp[32 * int(p["index"], 16):32 * int(p["index"], 16) + 32].hex(" ").upper()
                                        for p in src["sprite_palettes"]}}


def overload_palette(rom):
    """Praetor overload placeholder palette: derived from the vanilla monster palette units (16 colours, 4bpp)."""
    t = load_palettes()["monster_overload"]
    u = int(t["from_vanilla_monster_palette"], 16)
    a = snes_to_pc(MON_PAL) + 16 * u
    return derive(rom.clean[a:a + 32], t["transform"])


def ai_extension(rom, notes):
    src = open(os.path.join(HERE, "asm", "celes_v092", "ai_ext.s")).read()
    pal = overload_palette(rom)
    src += "\n.section XE_F0 $F04000\nXE_OverloadPal:\n" + "".join(
        f"        .byte {', '.join(f'${b:02X}' for b in pal[k:k + 16])}\n" for k in range(0, 32, 16))
    prog = Program(src, {}, "celes_v092")
    secs = prog.assemble()
    f0 = secs["XE_F0"]
    rom.place("ENGINE_CODE", f0[1], "XE_AI_EXT", "V9203_AI_EXT_CODE", at=f0[0],
              reason="TECH v0.9.2 AI extension routines (asm/celes_v092/ai_ext.s)", consumer="JSL from XE2_Cond / XE2_Misc")
    c2org, c2 = secs["XE_C2"]
    rom.patch(c2org, b"\xFF" * len(c2), c2, "V9204_AI_EXT_C2_STUBS", claim="ITEMX_C2_STUBS",
              consumer="JSR / JMP from the AI dispatch hooks", reason="same-bank stubs in audited vanilla padding ($FF)")
    syms = dict(prog.symbols)
    notes["ai_ext"] = {"code": f"{fmt_snes(f0[0])} ({len(f0[1])} B)", "c2_stubs": f"{fmt_snes(c2org)} ({len(c2)} B)",
                       "overload_palette": pal.hex(" ").upper(), "listing": {n: prog.listing(n) for n in secs}, "hooks": []}
    for pid, site, expect, asm, cons, reason in HOOKS:
        e = bytes.fromhex(expect)
        hp = Program(f".section H ${site:06X}\n.a8\n.i8\n{asm}\n", syms, pid)
        new = hp.assemble()["H"][1]
        new += b"\xEA" * (len(e) - len(new))
        rom.patch(site, e, new, pid, consumer=cons, reason=reason)
        notes["ai_ext"]["hooks"].append({"id": pid, "snes": fmt_snes(site), "original": expect, "new": new.hex(" ").upper()})


def build(rom, target, alloc, meta):
    notes = {}
    palettes(rom, notes)
    ai_extension(rom, notes)
    return notes
