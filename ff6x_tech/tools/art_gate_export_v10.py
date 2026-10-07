#!/usr/bin/env python3
"""ART ASSET GATE v1.0 - export driver (called by tools/art_gate_v10.py). Read-only: no ROM is written.

Outputs (in <out>/ART_ASSET_GATE_v1.0/):
  MAP_1A2_CURRENT.png               annotated full map (RESET state = current), BG1 + BG2, grid, coordinates, E8 regions
  MAP_1A2_CURRENT_1X.png            same render, 1:1, no annotation (512 x 512)
  MAP_1A2_METATILE_IDS.png          the map with every BG1 metatile id printed
  MAP_1A2_STATES.png                E8 regions in every state: ROM render vs running game (bsnes)
  MAP_1A2_RUNTIME_<STATE>.png       bsnes screenshots
  TILESET_1A2_8X8_IDS.png           VRAM BG tiles $000-$2FF with ids, source gfx set:index, usage colour code
  METATILES_1A2_16X16_IDS.png       BG1 tileset (metatiles $00-$FF) with ids + collision; BG2 sheet as *_BG2_*
  PALETTE_1A2.png                   map palette $30 (8 rows x 16), row ids, CGRAM index, BGR555, engine colours
  *.json                            the same data machine-readable; MEMORIAL_REGION.json, ARCHIVE_REGION.json
  VANILLA_REFERENCE/                candidate crops + per-candidate JSON + source-map previews + contact sheet
  VERIFICATION_v1.0.json            ROM decode vs running game (VRAM, CGRAM, tileset WRAM, BG1 buffer, pixels)
"""
import json, os, sys, hashlib
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "tools"))
import numpy as np
from PIL import Image, ImageDraw
from ff6x import fieldgfx as F
from ff6x.hirom import snes_to_pc
from art_gate_v10 import (MapGfx, render_map, meta_idx, to_rgb, word_img, annotate_map, label_grid, save, scale,
                          passability, wdesc, font, nm, QA_SUBTILEMAP_PTRS, MAP, ENGINE_COLOURS, STATES_JSON,
                          CANDIDATES_JSON, tile_key_set)

WINDOW_TILES = range(0x2E0, 0x2FC)          # TfrWindowGfx: 28 dialog-window tiles -> VRAM word $2E00 (wallpaper dependent)
SCREEN_OFF = (136, 113)
SPRITE_CELLS = {(16, 13), (16, 14), (21, 13)}  # party leader at (16,14) (16x24 sprite), survivor NPC at (21,14)                     # map pixel = screen pixel + this, player at tile (16,14) (emu_visual_v093 X0/Y0)
STATE_SEQ = (("reset", "none", "sealed"), ("preserve", "tags", "kept"), ("burn", "tags", "burned"), ("graves", "stone", "kept"))
COL = {"map": (60, 220, 90), "state": (255, 150, 40), "tileset": (230, 210, 60), "anim": (80, 200, 255),
       "window": (230, 60, 60), "free": None}
BITS = {"EXP_CELES_DONE": "$0E9", "EXP_CELES_RECORDS_PRESERVED": "$0EA", "EXP_CELES_RECORDS_CHOSEN": "$0EB",
        "EXP_GRAVES_DONE": "$0EC"}


def sha1(b):
    return hashlib.sha1(b).hexdigest()


def hexrows(rows):
    return [[int(t, 16) for t in r.split()] for r in rows]


def apply_states(lay, states, mem, arc):
    lay = bytearray(lay)
    for region, st in (("memorial", mem), ("archive", arc)):
        r = states["regions"][region]
        for j, row in enumerate(hexrows(states["states"][region][st]["rows"])):
            for i, t in enumerate(row):
                lay[(r["y"] + j) * 32 + r["x"] + i] = t
    return bytes(lay)


# ---------------------------------------------------------------------------------------------------- verification
def verify(mg, qa, cap, states):
    rep = {"emulator": "bsnes (accurate PPU), tools/art_gate_capture_v10.py", "states": {}}
    frames = [F.apply_anim(mg.vram0, qa, mg.anim, f) for f in range(4)]
    tw = None
    for tag, mem, arc in STATE_SEQ:
        g = lambda n: open(os.path.join(cap, f"{tag}_{n}"), "rb").read()
        v, cg, tw, bg1 = g("vram.bin"), g("cgram.bin"), g("tileset_wram.bin"), g("bg1.bin")
        bad_tiles = [t for t in range(0x300) if t not in WINDOW_TILES
                     and not any(fr[t * 32:t * 32 + 32] == v[t * 32:t * 32 + 32] for fr in frames)]
        ws = [tw[2 * i] | tw[2 * i + 1] << 8 for i in range(0x800)]
        ts1_ok = all(ws[q * 256 + t] == mg.ts1[t][q] for t in range(256) for q in range(4))
        ts2_ok = all(ws[0x400 + q * 256 + t] == mg.ts2[t][q] for t in range(256) for q in range(4))
        cgw = [cg[2 * i] | cg[2 * i + 1] << 8 for i in range(128)]
        cg_bad = [i for i in range(128) if cgw[i] != mg.pal[i] and i not in ENGINE_COLOURS]
        want = apply_states(mg.lay1, states, mem, arc)
        bg_ok = bytes(bg1) == want
        # pixels: screen vs ROM render (4 BG animation phases), E8 regions must be exact in one phase
        shot = np.asarray(Image.open(os.path.join(cap, f"{tag}.png")).convert("RGB"))
        best = None
        regions = {}
        for f in range(4):
            mgf = mg.with_frame(f)
            full = render_map(mgf, lay1=want)
            view = full[SCREEN_OFF[1]:SCREEN_OFF[1] + 224, SCREEN_OFF[0]:SCREEN_OFF[0] + 256]
            inner = (slice(8, 215), slice(8, 248))      # outside: blank lines 0-7 / 215-223, masked 8-px columns at both edges
            eq = float(np.mean(np.all(view[inner] == shot[inner], axis=2)))
            if best is None or eq > best:
                best = eq
                neq = ~np.all(view == shot, axis=2)
                neq[:8] = False; neq[215:] = False; neq[:, :8] = False; neq[:, 248:] = False
                cells = sorted({((x + SCREEN_OFF[0]) // 16, (y + SCREEN_OFF[1]) // 16) for y, x in zip(*np.nonzero(neq))})
            for region in ("memorial", "archive"):
                r = states["regions"][region]
                x0, y0 = r["x"] * 16 - SCREEN_OFF[0], r["y"] * 16 - SCREEN_OFF[1]
                a = shot[y0:y0 + 16 * r["h"], x0:x0 + 16 * r["w"]]
                b = full[r["y"] * 16:(r["y"] + r["h"]) * 16, r["x"] * 16:(r["x"] + r["w"]) * 16]
                regions[region] = regions.get(region, False) or bool((a == b).all())
        rep["states"][tag] = {"memorial_state": mem, "archive_state": arc,
                              "vram_tiles_000_2FF_not_matching_rom": [f"{t:03X}" for t in bad_tiles],
                              "tileset_bg1_equal": ts1_ok, "tileset_bg2_equal": ts2_ok,
                              "cgram_colours_not_matching_rom_excl_engine": cg_bad,
                              "bg1_buffer_equal_layout_plus_states_json": bg_ok,
                              "screen_pixels_equal_to_rom_render_fraction": round(best, 4),
                              "differing_map_cells_xy": [list(map(int, c)) for c in cells],
                              "differing_cells_only_sprite_cells": set(cells) <= SPRITE_CELLS,
                              "e8_region_pixels_exact": regions}
    s = rep["states"]
    rep["all_pass"] = all(not x["vram_tiles_000_2FF_not_matching_rom"] and x["tileset_bg1_equal"] and x["tileset_bg2_equal"]
                          and not x["cgram_colours_not_matching_rom_excl_engine"] and x["bg1_buffer_equal_layout_plus_states_json"]
                          and all(x["e8_region_pixels_exact"].values()) and x["differing_cells_only_sprite_cells"]
                          for x in s.values())
    rep["notes"] = ["VRAM tiles $2E0-$2FB are the dialog-window graphics (TfrWindowGfx, wallpaper dependent); excluded.",
                    "Animated tiles $280-$29F are compared against all 4 animation frames.",
                    "CGRAM colours 1-3 and 121-127 are engine-managed (not from the map palette); excluded.",
                    "Screen fraction is measured inside x 8-247, y 8-214 (the game blanks lines 0-7 / 215-223 and the outer 8-px columns); every differing pixel lies in the cells of the two sprites on screen: the party leader (16,13-14) and the survivor NPC (21,13). The E8 regions are pixel-exact."]
    return rep


# ---------------------------------------------------------------------------------------------------- usage
def usage(mg, states, vanilla_maps_same_ts):
    used_map_bg1 = set(mg.lay1)
    state_ids = {int(t, 16) for reg in states["states"].values() for st in reg.values() for r in st["rows"] for t in r.split()}
    used_map_bg2 = set(mg.lay2) if mg.lay2 else set()
    tiles_map = {}
    for t in sorted(used_map_bg1 | state_ids):
        for w in mg.ts1[t]:
            tiles_map.setdefault(w & 0x3FF, set()).add(("bg1", t, w >> 10 & 7))
    for t in sorted(used_map_bg2):
        for w in mg.ts2[t]:
            tiles_map.setdefault(w & 0x3FF, set()).add(("bg2", t, w >> 10 & 7))
    tiles_ts = {}
    for name, ts in (("bg1", mg.ts1), ("bg2", mg.ts2)):
        for t in range(256):
            for w in ts[t]:
                tiles_ts.setdefault(w & 0x3FF, set()).add((name, t, w >> 10 & 7))
    return {"bg1_on_map": used_map_bg1, "bg1_states": state_ids, "bg2_on_map": used_map_bg2,
            "tiles_map": tiles_map, "tiles_ts": tiles_ts, "vanilla_bg1": vanilla_maps_same_ts}


def tile_class(t, u, anim):
    if t in WINDOW_TILES:
        return "window"
    if t in u["tiles_map"]:
        return "map"
    if any(t in a["tiles"] for a in anim):
        return "anim"
    if t in u["tiles_ts"]:
        return "tileset"
    return "free"


# ---------------------------------------------------------------------------------------------------- sheets
def tile_rgb(mg, t, row):
    px = mg.tiles[t].astype(np.int16)
    if row is None:
        g = (px * 16).clip(0, 255).astype(np.uint8)
        return np.stack([g, g, g], axis=-1)
    idx = np.where(px == 0, -1, px + row * 16)
    return to_rgb(mg, idx)


def sheet_tiles(mg, u, out):
    cells, labels, subs, marks, rows_json = [], [], [], [], []
    for t in range(0x300):
        uses = sorted(u["tiles_map"].get(t, set()) or u["tiles_ts"].get(t, set()))
        row = uses[0][2] if uses else None
        cells.append(scale(tile_rgb(mg, t, row), 4))
        src = mg.vsrc.get(t)
        cls = tile_class(t, u, mg.anim)
        labels.append(f"{t:03X}")
        if cls == "window":
            subs.append("window")
        elif cls == "anim":
            a = [x for x in mg.anim if t in x["tiles"]][0]
            subs.append(f"anim{a['slot']}")
        else:
            subs.append(f"{src[1]:02X}:{src[2]:02X}" if src else "-")
        marks.append(COL[cls])
        rows_json.append({"tile": f"{t:03X}", "vram_word": f"{t * 16:04X}", "class": cls,
                          "source": ({"gfx_slot": src[0] + 1, "gfx_set": f"{src[1]:02X}", "gfx_set_name": nm("gfx", src[1]),
                                      "tile_in_set": f"{src[2]:02X}"} if src and cls not in ("window", "anim") else None),
                          "anim_record": ([x["slot"] for x in mg.anim if t in x["tiles"]] or [None])[0],
                          "palette_rows_used": sorted({x[2] for x in u["tiles_ts"].get(t, set())}),
                          "used_by_metatiles_on_1A2": sorted({f"{x[0]}:{x[1]:02X}" for x in u["tiles_map"].get(t, set())}),
                          "used_by_tileset_metatiles": len(u["tiles_ts"].get(t, set())),
                          "sha1_4bpp": sha1(bytes(mg.vram[t * 32:t * 32 + 32]))[:12]})
    title = ("MAP $1A2 - VRAM BG1/BG2 8x8 tiles $000-$2FF (id = tile number in the BG tilemap word, 10 bits). Drawn x4 with the "
             "palette row of their first use; grey = no palette use.\nsub-label = source gfx set:tile (slot1 $36 -> $000-$0FF, slot2 $37 -> "
             "$100-$17F, slot3 $38 -> $180-$1FF, slot4 $3A -> $200-$2DF), animN = BG animation record N, window = dialog window.\n"
             "border: GREEN used on map $1A2 (incl. E8 states)  YELLOW only in tilesets $22/$43  CYAN BG animation  RED engine window  none = unreferenced")
    img = label_grid(cells, 32, 32, labels, subs, title=title, marks=marks, fsz=11)
    save(img, os.path.join(out, "TILESET_1A2_8X8_IDS.png"))
    return rows_json


def sheet_metatiles(mg, u, ts, tsid, out, fname, layer):
    cells, labels, subs, marks, js = [], [], [], [], []
    on_map = u["bg1_on_map"] if layer == "bg1" else u["bg2_on_map"]
    for t in range(256):
        idx = meta_idx(mg, ts, t)
        cells.append(scale(to_rgb(mg, idx), 3))
        pa = passability(mg.tp1[t], mg.tp2[t])
        labels.append(f"{t:02X} {'X' if pa['impassable'] else 'o'}")
        in_state = layer == "bg1" and t in u["bg1_states"] and t not in on_map
        subs.append(f"{pa['byte1']}/{pa['byte2']}")
        marks.append(COL["map"] if t in on_map else (COL["state"] if in_state else None))
        js.append({"id": f"{t:02X}", "words": {q: wdesc(ts[t][k]) for k, q in enumerate(("TL", "TR", "BL", "BR"))},
                   "collision_tile_prop_set_24": pa if layer == "bg1" else None,
                   "on_1A2_map": t in on_map, "in_e8_states": layer == "bg1" and t in u["bg1_states"],
                   "used_by_vanilla_maps_with_this_tileset": sorted(u["vanilla_bg1"].get(t, [])) if layer == "bg1" else None})
    title = (f"MAP $1A2 - {layer.upper()} tileset ${tsid:02X} ({nm('tileset', tsid)}): 256 metatiles (16x16), id = byte in the map "
             f"layout. Drawn x3, both priorities.\nlabel: id + X impassable / o passable (tile property set $24, byte1 & 7 == 7). "
             f"sub-label: property byte1/byte2.\nborder: GREEN on map $1A2 (RESET layout)  ORANGE only in an E8 state  none = not on $1A2")
    if layer == "bg2":
        title = title.replace("label: id + X impassable / o passable (tile property set $24, byte1 & 7 == 7). sub-label: property byte1/byte2.",
                              "label: id (+ BG1 property of the same id; BG2 has no own collision).")
    img = label_grid(cells, 16, 48, labels, subs, title=title, marks=marks, fsz=11)
    save(img, os.path.join(out, fname))
    return js


def sheet_palette(mg, clean, out):
    van = F.palette(clean, 0x18, F.MAP_PAL_VANILLA)
    f, fs = font(11), font(9)
    sw, rh = 52, 58
    W, H = 110 + 16 * sw, 120 + 2 * 8 * rh + 40
    im = Image.new("RGB", (W, H), (24, 24, 28))
    d = ImageDraw.Draw(im)
    d.multiline_text((6, 4), "MAP $1A2 BG palette = map palette $30 (QA ROM table F7:A000 + 256 x $30; derived from vanilla $18 MAGITEK_FACTORY,\n"
                     "palettes/v093: desaturate 0.75, tint 0.95/1.00/1.08, gain 1.04). 8 rows x 16 colours = CGRAM $00-$7F (BG).\n"
                     "index 0 of each row = transparent (row 0 colour 0 = backdrop). ENG = engine-managed (overwritten at runtime: 1-3, 121-127).\n"
                     "label: CGRAM index (hex) / BGR555 (hex, 0bbbbbgg gggrrrrr)", fill=(235, 235, 235), font=font(12))
    js = []
    for block, (pal, name, y0) in enumerate(((mg.pal, "$30 (v0.9.3, accepted)", 90), (van, "vanilla $18 (source, reference only)", 90 + 8 * rh + 30))):
        d.text((6, y0 - 18), name, fill=(255, 220, 120), font=font(12))
        for r in range(8):
            d.text((6, y0 + r * rh + 14), f"row {r}", fill=(255, 255, 255), font=f)
            d.text((6, y0 + r * rh + 28), f"pal {r}", fill=(170, 200, 255), font=fs)
            for c in range(16):
                i = r * 16 + c
                x, y = 100 + c * sw, y0 + r * rh
                rgb = F.bgr555_rgb(pal[i])
                d.rectangle([x, y, x + sw - 4, y + 30], fill=rgb, outline=(0, 0, 0))
                if c == 0:
                    d.line([x, y, x + sw - 4, y + 30], fill=(255, 0, 0), width=1)
                if i in ENGINE_COLOURS:
                    d.text((x + 2, y + 2), "ENG", fill=(255, 40, 40), font=fs)
                d.text((x, y + 31), f"{i:02X}", fill=(255, 255, 255), font=fs)
                d.text((x, y + 42), f"{pal[i]:04X}", fill=(170, 200, 255), font=fs)
                if block == 0:
                    js.append({"cgram_index": f"{i:02X}", "row": r, "col": c, "bgr555": f"{pal[i]:04X}", "rgb888": list(rgb),
                               "vanilla_18_bgr555": f"{van[i]:04X}", "transparent": c == 0,
                               "engine_managed": i in ENGINE_COLOURS})
    im.save(os.path.join(out, "PALETTE_1A2.png"))
    return js


# ---------------------------------------------------------------------------------------------------- regions
def region_json(mg, states, region, cap, out, frames_mg):
    r = states["regions"][region]
    x, y, w, h = r["x"], r["y"], r["w"], r["h"]
    sts = {}
    for st, d in states["states"][region].items():
        rows = hexrows(d["rows"])
        cells = []
        for j, row in enumerate(rows):
            for i, t in enumerate(row):
                cells.append({"x": x + i, "y": y + j, "metatile": f"{t:02X}",
                              "words": {q: wdesc(mg.ts1[t][k]) for k, q in enumerate(("TL", "TR", "BL", "BR"))},
                              "collision": passability(mg.tp1[t], mg.tp2[t])})
        sts[st] = {"rows": d["rows"], "event_bits": d["bits"], "look": d["look"], "cells": cells,
                   "all_impassable": all(c["collision"]["impassable"] for c in cells)}
    ctx = {}
    for name, yy in (("row_above", y - 1), ("row_below", y + h)):
        ctx[name] = [{"x": xx, "y": yy, "metatile": f"{mg.lay1[yy * 32 + xx]:02X}",
                      "collision": passability(mg.tp1[mg.lay1[yy * 32 + xx]], mg.tp2[mg.lay1[yy * 32 + xx]])}
                     for xx in range(x - 1, x + w + 1)]
    ctx["left_column"] = [{"x": x - 1, "y": yy, "metatile": f"{mg.lay1[yy * 32 + x - 1]:02X}"} for yy in range(y, y + h)]
    ctx["right_column"] = [{"x": x + w, "y": yy, "metatile": f"{mg.lay1[yy * 32 + x + w]:02X}"} for yy in range(y, y + h)]
    current = "none" if region == "memorial" else "sealed"
    return {
        "map": "1A2", "map_name": "Vector Outer Ward (QA enabler map, TECH v0.9.2/0.9.3)", "region": region.upper(),
        "layer": "BG1", "tileset_bg1": "22 (MAGITEK_LAB_1_BG1)", "tile_property_set": "24",
        "bounding_rect_metatiles": {"x": x, "y": y, "w": w, "h": h, "x_end_incl": x + w - 1, "y_end_incl": y + h - 1},
        "bounding_rect_pixels_map": {"x": x * 16, "y": y * 16, "w": w * 16, "h": h * 16},
        "dimensions": {"metatiles": [w, h], "pixels": [w * 16, h * 16], "tiles_8x8": [w * 2, h * 2]},
        "screen_rect_when_player_at_16_14": {"x": x * 16 - SCREEN_OFF[0], "y": y * 16 - SCREEN_OFF[1], "w": w * 16, "h": h * 16},
        "trigger_tile": r["trigger"], "trigger_collision": passability(mg.tp1[mg.lay1[r["trigger"][1] * 32 + r["trigger"][0]]],
                                                                      mg.tp2[mg.lay1[r["trigger"][1] * 32 + r["trigger"][0]]]),
        "role": r["role"],
        "current_state_reset": current, "current_tile_ids_reset": states["states"][region][current]["rows"],
        "compiled_layout_tile_ids": [" ".join(f"{mg.lay1[(y + j) * 32 + x + i]:02X}" for i in range(w)) for j in range(h)],
        "states": sts,
        "state_selection": ("startup event EvOuterInit -> EvOuterMem: EXP_GRAVES_DONE -> stone, else EXP_CELES_DONE -> tags, else none"
                            if region == "memorial" else
                            "startup event EvOuterInit -> EvOuterArc: EXP_CELES_RECORDS_CHOSEN = 0 -> sealed, else "
                            "EXP_CELES_RECORDS_PRESERVED = 1 -> kept, else burned"),
        "event_bits": BITS, "draw_mechanism": "event cmd $73 (set_tiles BG1, immediate redraw) in the map startup event; "
                                              "source of truth maps/celes_outer_v092/states.json (builder-asserted)",
        "surroundings": ctx,
        "constraints": ["every state tile must be impassable (builder runs the movement model for all 9 memorial x archive combinations)",
                        f"trigger tile {tuple(r['trigger'])} (row {y + h}, floor) must stay walkable and reachable",
                        "art may not change rows outside the region unless the region is redefined in states.json and the event",
                        "accepted architecture: do not change the event bits or the state selection (E8 ACCEPTED)"],
        "accepted_status": "E8 state / persistence architecture ACCEPTED; placeholder art REJECTED for production (v0.9.3 user runtime)",
        "images": {st: f"REGION_{region.upper()}_{st}.png" for st in states["states"][region]},
    }


def region_images(mg, states, out, cap):
    for region in ("memorial", "archive"):
        r = states["regions"][region]
        for st in states["states"][region]:
            lay = bytearray(mg.lay1)
            for j, row in enumerate(hexrows(states["states"][region][st]["rows"])):
                for i, t in enumerate(row):
                    lay[(r["y"] + j) * 32 + r["x"] + i] = t
            x0, y0 = r["x"] - 2, r["y"] - 1
            img = render_map(mg, lay1=bytes(lay), x0=x0, y0=y0, w=r["w"] + 4, h=r["h"] + 3)
            ids = [[lay[(y0 + j) * 32 + x0 + i] for i in range(r["w"] + 4)] for j in range(r["h"] + 3)]
            a = annotate_map(img, 6, ids=ids, coord=False,
                             boxes=[(2, 1, r["w"], r["h"], (255, 150, 40), f"{region} {st} ({r['x']},{r['y']}) {r['w']}x{r['h']}")])
            save(a, os.path.join(out, f"REGION_{region.upper()}_{st}.png"))


def states_sheet(mg, states, cap, out):
    f = font(12)
    rows = []
    for tag, mem, arc in STATE_SEQ:
        lay = apply_states(mg.lay1, states, mem, arc)
        shot = np.asarray(Image.open(os.path.join(cap, f"{tag}.png")).convert("RGB"))
        ren = render_map(mg, lay1=lay)
        cols = []
        for region, st in (("memorial", mem), ("archive", arc)):
            r = states["regions"][region]
            mx0 = max((r["x"] - 1) * 16, SCREEN_OFF[0] + 8)          # stay inside the visible (unmasked) screen
            mx1 = min((r["x"] + r["w"] + 1) * 16, SCREEN_OFF[0] + 248)
            my0, my1 = (r["y"] - 1) * 16, (r["y"] + r["h"] + 1) * 16
            b = ren[my0:my1, mx0:mx1]
            a = shot[my0 - SCREEN_OFF[1]:my1 - SCREEN_OFF[1], mx0 - SCREEN_OFF[0]:mx1 - SCREEN_OFF[0]]
            cols.append((f"{region}: {st}", scale(b, 4), scale(a, 4)))
        rows.append((tag, cols, shot))
    W = 20 + sum(c[1].shape[1] * 2 + 30 for c in rows[0][1]) + 256 * 2 + 20
    H = 40 + sum(max(c[1].shape[0] for c in r[1]) + 40 for r in rows)
    im = Image.new("RGB", (W, max(H, 40 + 4 * (448 + 40))), (24, 24, 28))
    d = ImageDraw.Draw(im)
    d.text((10, 8), "MAP $1A2 E8 regions per state: left = ROM render (states.json), right = bsnes screenshot crop; last column = full "
                    "bsnes frame (player at 16,14). Placeholder art REJECTED for production - reference only.", fill=(235, 235, 235), font=f)
    y = 40
    for tag, cols, shot in rows:
        x = 10
        hh = max(c[1].shape[0] for c in cols)
        d.text((x, y), tag.upper(), fill=(255, 220, 120), font=font(14))
        for lab, ren, sc in cols:
            d.text((x, y + 18), lab, fill=(255, 255, 255), font=f)
            im.paste(Image.fromarray(ren), (x, y + 36))
            im.paste(Image.fromarray(sc), (x + ren.shape[1] + 6, y + 36))
            x += ren.shape[1] * 2 + 30
        im.paste(Image.fromarray(scale(shot, 2)), (x, y + 36))
        y += max(hh, 448) + 60
    im = im.crop((0, 0, W, y))
    im.save(os.path.join(out, "MAP_1A2_STATES.png"))


# ---------------------------------------------------------------------------------------------------- vanilla refs
def vanilla_refs(clean, mg1a2, out):
    cands = json.load(open(CANDIDATES_JSON))["candidates"]
    vd = os.path.join(out, "VANILLA_REFERENCE")
    os.makedirs(os.path.join(vd, "maps"), exist_ok=True)
    have = tile_key_set(mg1a2.tiles[:0x2E0])        # $1A2 VRAM tiles (not window) incl. flips
    cache, index, contact = {}, [], []
    for c in cands:
        m = int(c["map"], 16)
        mg = cache.get(m) or cache.setdefault(m, MapGfx(clean, m))
        x, y, w, h = c["rect"]
        img = render_map(mg, x0=x, y0=y, w=w, h=h)
        ids = [[mg.lay1[(y + j) * mg.w1 + x + i] for i in range(w)] for j in range(h)]
        ids2 = [[mg.lay2[((y + j) % mg.h2) * mg.w2 + (x + i) % mg.w2] for i in range(w)] for j in range(h)] if mg.lay2 else None
        a = annotate_map(img, 3, ids=ids, coord=False)
        fn = f"{c['id']}_{c['category']}_MAP{m:03X}_{x}_{y}_{w}x{h}.png"
        save(a, os.path.join(vd, fn))
        save(img, os.path.join(vd, fn.replace(".png", "_1x.png")))
        # 8x8 words of the BG1 metatiles in the rect, and how many unique 8x8 graphics are not in $1A2's VRAM
        words, uniq = [], {}
        for j in range(h):
            row = []
            for i in range(w):
                t = ids[j][i]
                q = mg.ts1[t]
                row.append({"metatile": f"{t:02X}", "words": [f"{x_:04X}" for x_ in q],
                            "collision": passability(mg.tp1[t], mg.tp2[t])})
                for wd in q:
                    tt = wd & 0x3FF
                    if tt < 768:
                        uniq[tt] = mg.tiles[tt]
            words.append(row)
        blank = [t for t, px in uniq.items() if not px.any()]
        missing = [t for t, px in uniq.items() if px.any() and px.tobytes() not in have]
        pal_rows = sorted({wd >> 10 & 7 for r in words for cell in r for wd in (int(v, 16) for v in cell["words"])})
        same_gfx = [g for g in mg.p["gfx"] if g in mg1a2.p["gfx"]]
        info = mg.info()
        rec = {"id": c["id"], "category": c["category"], "label": c["label"], "source_map": f"{m:03X}",
               "rect_metatiles": {"x": x, "y": y, "w": w, "h": h}, "layer": "BG1 ids (BG2 ids listed separately)",
               "tileset_bg1": info["tileset_bg1"], "tileset_bg1_name": info["tileset_bg1_name"],
               "tileset_bg2": info["tileset_bg2"], "gfx_sets": info["gfx_sets"], "gfx_set_names": info["gfx_set_names"],
               "palette_id": info["palette"], "palette_name": info["palette_name"],
               "palette_rows_used_bg1": pal_rows, "tile_prop_set": info["tile_prop_set"],
               "layout_bg1": info["layout_bg1"], "layout_bg1_name": info["layout_bg1_name"],
               "metatile_ids_bg1": [" ".join(f"{t:02X}" for t in r) for r in ids],
               "metatile_ids_bg2": [" ".join(f"{t:02X}" for t in r) for r in ids2] if ids2 else None,
               "tiles_8x8_bg1": words,
               "unique_8x8_tiles": len(uniq), "unique_8x8_blank": len(blank),
               "unique_8x8_not_in_1A2_vram": len(missing),
               "shares_gfx_sets_with_1A2": [f"{g:02X}" for g in same_gfx],
               "reuse_note": ("all non-blank 8x8 graphics already in $1A2 VRAM (metatile definitions + palette only)"
                              if not missing else f"{len(missing)} new 8x8 tiles would have to be added to a $1A2 graphics set; "
                              f"colours must be remapped to the $1A2 palette rows"),
               "png": fn, "png_1x": fn.replace(".png", "_1x.png"),
               "caveat": "static ROM render of BG1 + BG2 (no NPCs / event tile changes / BG3); BG animation shown in frame 1"}
        json.dump(rec, open(os.path.join(vd, fn.replace(".png", ".json")), "w"), indent=1)
        index.append({k: rec[k] for k in ("id", "category", "label", "source_map", "rect_metatiles", "tileset_bg1", "tileset_bg1_name",
                                          "gfx_sets", "palette_id", "palette_name", "unique_8x8_tiles", "unique_8x8_not_in_1A2_vram",
                                          "shares_gfx_sets_with_1A2", "png")})
        contact.append((c, img))
    for m, mg in cache.items():
        im = render_map(mg)
        k = 1
        save(annotate_map(im, k, grid=True, coord=True), os.path.join(vd, "maps", f"MAP_{m:03X}_{nm('layout', mg.p['layout_bg1'])}.png"))
    json.dump({"source_rom": "Final Fantasy III (USA) (Rev 1) - clean", "candidates": index}, open(os.path.join(vd, "INDEX.json"), "w"), indent=1)
    md = ["# Vanilla FFVI art references (ART ASSET GATE v1.0)", "",
          "Source: clean *Final Fantasy III (USA) (Rev 1)* ROM. Each crop is a static BG1+BG2 render of the rectangle (metatile "
          "units of the source map's BG1); NPCs, BG3 and event-time tile changes are not drawn. These are **candidates only**: "
          "nothing is chosen for implementation. Per-candidate detail (every metatile id, its four 8x8 BG words = tile number, "
          "palette row, priority, flips, and collision) is in the matching `.json`.", "",
          "`new 8x8` = unique non-blank 8x8 graphics of the crop that are **not** already in $1A2's VRAM (compared pixel-wise, flips "
          "included). 0 means the look can be rebuilt from graphics $1A2 already loads (new metatile definitions only).", "",
          "| id | category | source map | rect x,y,w,h | tileset BG1 | gfx sets | palette | unique 8x8 | new 8x8 | crop |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in index:
        rc = r["rect_metatiles"]
        md.append(f"| {r['id']} | {r['category'].replace('_', ' ')} | ${r['source_map']} | {rc['x']},{rc['y']},{rc['w']},{rc['h']} | "
                  f"${r['tileset_bg1']} {r['tileset_bg1_name']} | {' '.join('$' + g for g in r['gfx_sets'])} | ${r['palette_id']} "
                  f"{r['palette_name']} | {r['unique_8x8_tiles']} | {r['unique_8x8_not_in_1A2_vram']} | `{r['png']}` |")
    md += ["", "Labels:", ""] + [f"* **{r['id']}** - {r['label']}" for r in index]
    md += ["", "`maps/`: full static render of every source map (1 px = 1 px, grid = metatiles, numbers = BG1 coordinates).",
           "`VANILLA_REFERENCE_CONTACT.png`: all crops grouped by category."]
    open(os.path.join(vd, "INDEX.md"), "w").write("\n".join(md) + "\n")
    # contact sheet by category
    cats = ["temporary_memorial", "permanent_memorial", "archive_preserve", "archive_burn"]
    f = font(12)
    blocks = []
    for cat in cats:
        items = [(c, im) for c, im in contact if c["category"] == cat]
        blocks.append((cat, items))
    W = 1800
    y = 40
    layout = []
    for cat, items in blocks:
        x, rowh = 10, 0
        layout.append(("title", cat, 10, y))
        y += 22
        for c, im in items:
            k = 2 if im.shape[1] * 2 <= 700 and im.shape[0] * 2 <= 520 else 1
            iw, ih = im.shape[1] * k, im.shape[0] * k
            if x + iw > W - 10:
                x, y = 10, y + rowh + 30
                rowh = 0
            layout.append(("img", (c, scale(im, k)), x, y))
            x += iw + 16
            rowh = max(rowh, ih)
        y += rowh + 40
    canvas = Image.new("RGB", (W, y), (24, 24, 28))
    d = ImageDraw.Draw(canvas)
    d.text((10, 10), "ART ASSET GATE v1.0 - vanilla FFVI references (clean Rev 1 ROM, static BG1+BG2 render). Candidates only: "
                     "nothing is chosen for implementation. Labels: INDEX.md", fill=(235, 235, 235), font=font(14))
    for kind, obj, x, yy in layout:
        if kind == "title":
            d.text((x, yy), obj.upper().replace("_", " "), fill=(255, 220, 120), font=font(16))
        else:
            c, im = obj
            canvas.paste(Image.fromarray(im), (x, yy + 16))
            d.text((x, yy), f"{c['id']}  ${c['map']}", fill=(255, 255, 255), font=f)
    canvas.save(os.path.join(vd, "VANILLA_REFERENCE_CONTACT.png"))
    return index


# ---------------------------------------------------------------------------------------------------- capacity
def capacity(mg, u, qa, clean, prod, celes):
    # metatile ids of tileset $22 not on $1A2 (layout + states), and their collision
    free_meta = [t for t in range(256) if t not in u["bg1_on_map"] and t not in u["bg1_states"]]
    free_meta_imp = [t for t in free_meta if mg.tp1[t] & 7 == 7]
    unused_anywhere = [t for t in free_meta if not u["vanilla_bg1"].get(t)]
    blank_ts = [t for t in range(256) if all((w & 0x3FF) == (mg.ts1[0][0] & 0x3FF) for w in mg.ts1[t])]
    # 8x8 tile slots
    per_slot = {}
    for slot, (lo, hi) in enumerate(((0x000, 0x100), (0x100, 0x180), (0x180, 0x200), (0x200, 0x2E0))):
        rng = range(lo, hi)
        per_slot[f"slot{slot + 1}_gfx_{mg.p['gfx'][slot]:02X}"] = {
            "vram_tiles": f"{lo:03X}-{hi - 1:03X}", "count": hi - lo,
            "referenced_by_tilesets_22_43": sum(1 for t in rng if t in u["tiles_ts"]),
            "used_on_1A2_incl_states": sum(1 for t in rng if t in u["tiles_map"]),
            "unreferenced_by_tilesets": sum(1 for t in rng if t not in u["tiles_ts"] and t not in range(0x280, 0x2C0)),
            "free_if_cloned_for_1A2": sum(1 for t in rng if t not in u["tiles_map"] and t not in range(0x280, 0x2C0))}
    def ptr_free(tbl, n, size):
        out = []
        for i in range(n):
            p = snes_to_pc(tbl) + size * i
            if clean[p:p + size] == b"\xff" * size:
                out.append(i)
        return out
    gfx_free = ptr_free(F.MAP_GFX_PTRS, 85, 3)
    ts_free = ptr_free(F.TILESET_PTRS, 85, 3)
    tp_free = ptr_free(F.TILEPROP_PTRS, 64, 2)
    fe = {n: (set(r[0x3E0000:0x3F0000]) == {0xFF}) for n, r in (("qa_v093", qa), ("production_v091", prod), ("celes_tech_v091", celes))}
    return {
        "metatiles_tileset_22": {"total": 256, "on_1A2_layout": len(u["bg1_on_map"]), "in_e8_states_only": len(u["bg1_states"] - u["bg1_on_map"]),
                                 "not_on_1A2": len(free_meta), "not_on_1A2_and_impassable_in_prop_set_24": len(free_meta_imp),
                                 "not_on_1A2_and_unused_by_every_vanilla_map_with_tileset_22": len(unused_anywhere),
                                 "ids_not_on_1A2_impassable": [f"{t:02X}" for t in free_meta_imp],
                                 "ids_unused_anywhere": [f"{t:02X}" for t in unused_anywhere]},
        "vram_8x8_slots": per_slot,
        "engine_reserved_vram": {"280-29F": "BG animation records 0-7 (animated, 4 frames)", "2A0-2BF": "BG animation records 8-15 (static Frame1)",
                                 "2E0-2FB": "dialog window graphics (TfrWindowGfx, 28 tiles)", "300+": "BG3 (word $3000+)"},
        "pointer_tables_free_entries_rev1": {"map_gfx (DF:DA00, 3 B, base DF:DB00)": gfx_free,
                                             "tileset (DF:BA00, 3 B, base DE:0000)": ts_free,
                                             "tile_props (D9:CD10, 2 B, bank D9 only)": tp_free},
        "rom_space": {"GRAPHICS_RESERVED_FE FE:0000-FE:FFFF reserved, all $FF": fe,
                      "MAP_LAYOUTS F5 free tail (QA v0.9.3)": "F5:168A-F5:FFFF (59766 B)",
                      "bank D9 $FF runs (tile props must stay in bank D9: 16-bit offsets, fixed bank)":
                          ["D9:9A51 (762 B)", "D9:A569 (663 B, directly below the tile property data)", "D9:CC4C (196 B)"]},
    }


def vanilla_usage_ts(clean, ts_id):
    use = {}
    for m in range(F.VANILLA_MAPS):
        d = F.decode_props(F.map_props(clean, m))
        if d["tileset_bg1"] != ts_id or d["layout_bg1"] == 0:
            continue
        for t in set(F.layout(clean, d["layout_bg1"])):
            use.setdefault(t, set()).add(f"{m:03X}")
    return use


# ---------------------------------------------------------------------------------------------------- main
def main(qa_path, clean_path, cap, out_root):
    out = os.path.join(out_root, "ART_ASSET_GATE_v1.0")
    os.makedirs(out, exist_ok=True)
    qa, clean = open(qa_path, "rb").read(), open(clean_path, "rb").read()
    prod = open(os.path.join(os.path.dirname(qa_path), "FF6X_Rev1_TECH_v0.9.1_PRODUCTION.sfc"), "rb").read()
    celes = open(os.path.join(os.path.dirname(qa_path), "FF6X_Rev1_TECH_v0.9.1_CELES_TECH.sfc"), "rb").read()
    states = json.load(open(STATES_JSON))
    mg = MapGfx(qa, MAP, layout_ptrs=QA_SUBTILEMAP_PTRS)
    ver = verify(mg, qa, cap, states)
    json.dump(ver, open(os.path.join(out, "VERIFICATION_v1.0.json"), "w"), indent=1)
    print("VERIFY", ver["all_pass"], json.dumps({k: (v["screen_pixels_equal_to_rom_render_fraction"], v["e8_region_pixels_exact"]) for k, v in ver["states"].items()}))
    van = vanilla_usage_ts(clean, mg.p["tileset_bg1"])
    u = usage(mg, states, van)
    # map renders
    reset = apply_states(mg.lay1, states, "none", "sealed")
    full = render_map(mg, lay1=reset)
    save(full, os.path.join(out, "MAP_1A2_CURRENT_1X.png"))
    boxes = []
    for region, col in (("memorial", (255, 150, 40)), ("archive", (80, 200, 255))):
        r = states["regions"][region]
        boxes.append((r["x"], r["y"], r["w"], r["h"], col, f"{region.upper()} ({r['x']},{r['y']}) {r['w']}x{r['h']}"))
        boxes.append((r["trigger"][0], r["trigger"][1], 1, 1, (255, 60, 60), "trigger"))
    boxes.append((16, 12, 1, 1, (255, 60, 60), "console"))
    save(annotate_map(full, 2, boxes=boxes), os.path.join(out, "MAP_1A2_CURRENT.png"))
    ids = [[reset[y * 32 + x] for x in range(32)] for y in range(32)]
    save(annotate_map(full, 2, ids=ids, boxes=boxes), os.path.join(out, "MAP_1A2_METATILE_IDS.png"))
    for tag, _, _ in STATE_SEQ:
        Image.open(os.path.join(cap, f"{tag}.png")).save(os.path.join(out, f"MAP_1A2_RUNTIME_{tag.upper()}.png"))
    states_sheet(mg, states, cap, out)
    region_images(mg, states, out, cap)
    # sheets + json
    tiles_js = sheet_tiles(mg, u, out)
    m1 = sheet_metatiles(mg, u, mg.ts1, mg.p["tileset_bg1"], out, "METATILES_1A2_16X16_IDS.png", "bg1")
    m2 = sheet_metatiles(mg, u, mg.ts2, mg.p["tileset_bg2"], out, "METATILES_1A2_BG2_16X16_IDS.png", "bg2")
    pal_js = sheet_palette(mg, clean, out)
    info = mg.info()
    json.dump({"map": info, "vram_tiles": tiles_js}, open(os.path.join(out, "TILESET_1A2_8X8.json"), "w"), indent=1)
    json.dump({"tileset_bg1": info["tileset_bg1"], "tileset_bg1_rom": f"{mg.ts1_addr:06X}", "metatiles_bg1": m1,
               "tileset_bg2": info["tileset_bg2"], "tileset_bg2_rom": f"{mg.ts2_addr:06X}", "metatiles_bg2": m2},
              open(os.path.join(out, "METATILES_1A2.json"), "w"), indent=1)
    json.dump({"palette": "30", "table": f"{mg.pal_base:06X}", "colours": pal_js}, open(os.path.join(out, "PALETTE_1A2.json"), "w"), indent=1)
    layers = {"map": info,
              "bg1": {"layout": info["layout_bg1"], "size_metatiles": [mg.w1, mg.h1], "tileset": info["tileset_bg1"],
                      "rows_reset_state": [" ".join(f"{t:02X}" for t in reset[y * 32:(y + 1) * 32]) for y in range(32)],
                      "priority_words_used_on_map": sorted({w >> 13 & 1 for t in u["bg1_on_map"] for w in mg.ts1[t]})},
              "bg2": {"layout": info["layout_bg2"], "name": info["layout_bg2_name"], "size_metatiles": [mg.w2, mg.h2],
                      "tileset": info["tileset_bg2"], "metatile_ids_used": sorted(f"{t:02X}" for t in u["bg2_on_map"]),
                      "note": "vanilla all-transparent filler (read-only reuse, as in the accepted Annex): BG2 draws nothing"},
              "bg3": {"layout": info["layout_bg3"], "note": "no BG3 layer on $1A2"},
              "sprites": "party / NPCs (Vale sprite palette slot 7, E7) are OBJ - not part of the BG art",
              "animation": [{"record": a["slot"], "tiles": [f"{t:03X}" for t in a["tiles"]], "animated": a["animated"],
                             "speed": a["speed"], "frames_E6": [f"E6:{p:04X}" for p in a["frames"]]} for a in mg.anim]}
    json.dump(layers, open(os.path.join(out, "MAP_1A2_LAYERS.json"), "w"), indent=1)
    for region in ("memorial", "archive"):
        rj = region_json(mg, states, region, cap, out, None)
        rj["runtime_verified_pixels_exact"] = {t: v["e8_region_pixels_exact"][region] for t, v in ver["states"].items()}
        json.dump(rj, open(os.path.join(out, f"{region.upper()}_REGION.json"), "w"), indent=1)
    cap_js = capacity(mg, u, qa, clean, prod, celes)
    json.dump(cap_js, open(os.path.join(out, "CAPACITY_1A2.json"), "w"), indent=1)
    idx = vanilla_refs(clean, mg, out)
    # documents (art/gate_v1.0) and the exporter source
    import shutil
    for fn in sorted(os.listdir(os.path.join(HERE, "art", "gate_v1.0"))):
        shutil.copy(os.path.join(HERE, "art", "gate_v1.0", fn), os.path.join(out, fn))
    td = os.path.join(out, "TOOLS")
    os.makedirs(td, exist_ok=True)
    for src in ("tools/art_gate_v10.py", "tools/art_gate_export_v10.py", "tools/art_gate_capture_v10.py", "ff6x/fieldgfx.py",
                "art/vanilla_reference_candidates_v1.0.json"):
        shutil.copy(os.path.join(HERE, src), os.path.join(td, os.path.basename(src)))
    # file manifest
    files = []
    for root, _, fs in os.walk(out):
        for fn in sorted(fs):
            p = os.path.join(root, fn)
            files.append({"file": os.path.relpath(p, out), "sha1": sha1(open(p, "rb").read()), "bytes": os.path.getsize(p)})
    json.dump({"generator": "tools/art_gate_v10.py + tools/art_gate_export_v10.py (+ tools/art_gate_capture_v10.py on bsnes)",
               "inputs": {"qa_rom": {"file": os.path.basename(qa_path), "sha1": sha1(qa)},
                          "clean_rom": {"file": os.path.basename(clean_path), "sha1": sha1(clean)},
                          "production": sha1(prod), "celes_tech": sha1(celes)},
               "files": sorted(files, key=lambda x: x["file"])}, open(os.path.join(out_root, "ART_ASSET_GATE_FILES.json"), "w"), indent=1)
    print("EXPORT", out, len(files), "files;", len(idx), "vanilla candidates")
    print("CAPACITY", json.dumps(cap_js)[:1500])
