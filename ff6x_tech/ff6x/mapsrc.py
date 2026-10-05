"""Map source package compiler (maps/<name>/).

Compiles layout_bg1.txt + legend (map.json) to a BG1 tile layout, validates
walkability against the vanilla tile-property set read from the clean ROM,
and builds the 33-byte map property row. Pure stdlib.
"""
import json, os
from .lzss import decompress
from .hirom import snes_to_pc

TILEPROP_PTRS = 0xD9CD10     # 16-bit offsets (+D9:A800), 42 sets
TILEPROP_BASE = 0xD9A800
IMPASSABLE = 0xF7


class MapError(Exception):
    pass


def load_tileprops(clean, index):
    off = clean[snes_to_pc(TILEPROP_PTRS) + 2 * index] | clean[snes_to_pc(TILEPROP_PTRS) + 2 * index + 1] << 8
    d = decompress(clean[snes_to_pc(TILEPROP_BASE) + off:])
    if len(d) != 512:
        raise MapError("tile property set must decompress to 512 bytes")
    return d[:256], d[256:]          # byte1 plane, byte2 plane


class MapPackage:
    def __init__(self, folder):
        self.folder = folder
        j = lambda n: json.load(open(os.path.join(folder, n)))
        self.map = j("map.json"); self.npcs = j("npcs.json")["npcs"]
        self.triggers = j("triggers.json")["triggers"]; self.exits = j("exits.json")
        self.encounters = j("encounters.json")
        self.map_id = int(self.map["map_id"], 16)
        self.w, self.h = self.map["size_tiles"]
        rows = [l.rstrip("\n") for l in open(os.path.join(folder, self.map["bg1"]["source"]))
                if not l.startswith("#")]
        rows = [r for r in rows if r.strip() != ""]
        if len(rows) != self.h or any(len(r) != self.w for r in rows):
            raise MapError(f"layout must be {self.w}x{self.h} characters (got {len(rows)} rows, "
                           f"widths {sorted(set(len(r) for r in rows))})")
        self.rows = rows

    def tile_at(self, x, y):
        ch = self.rows[y][x]
        leg = self.map["legend"].get(ch)
        if leg is None:
            raise MapError(f"unknown legend char {ch!r} at {x},{y}")
        t = leg["tile"]
        if isinstance(t, list):
            k = (x + y) % 2 if leg.get("pattern", "").startswith("checker") else x % 2
            t = t[k]
        return int(t, 16), leg["role"]

    def compile_bg1(self):
        return bytes(self.tile_at(x, y)[0] for y in range(self.h) for x in range(self.w))

    def walk_grid(self):
        roles = set(self.map["walkable_roles"])
        return [[self.tile_at(x, y)[1] in roles for x in range(self.w)] for y in range(self.h)]

    def validate(self, clean):
        """Static walkability proof. Returns a report dict; raises on failure."""
        tp_index = int(self.map["tile_property_set"].split()[0], 16)
        p1, p2 = load_tileprops(clean, tp_index)
        walk = self.walk_grid()
        errs, notes = [], []
        bg1 = self.compile_bg1()
        for y in range(self.h):
            for x in range(self.w):
                t = bg1[y * self.w + x]
                passable = p1[t] != IMPASSABLE and (p1[t] & 0x03)
                if walk[y][x] and not passable:
                    errs.append(f"floor tile {t:02X} at {x},{y} is impassable in tile-property set")
                if not walk[y][x] and passable:
                    errs.append(f"non-floor tile {t:02X} at {x},{y} is PASSABLE (p1={p1[t]:02X}) -> leak")
                if walk[y][x] and (x in (0, self.w - 1) or y in (0, self.h - 1)):
                    errs.append(f"floor on map border at {x},{y}")
        # connectivity from arrival
        ax, ay = self.map["entry"]["arrive"]
        if not walk[ay][ax]:
            errs.append("arrival tile is not floor")
        seen, stack = set(), [(ax, ay)]
        while stack:
            x, y = stack.pop()
            if (x, y) in seen or not (0 <= x < self.w and 0 <= y < self.h) or not walk[y][x]:
                continue
            seen.add((x, y))
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        floor = {(x, y) for y in range(self.h) for x in range(self.w) if walk[y][x]}
        if floor - seen:
            errs.append(f"unreachable floor tiles: {sorted(floor - seen)[:8]}")
        for n in self.npcs:
            if (n["x"], n["y"]) not in floor:
                errs.append(f"NPC {n['name']} not on floor")
        for t in self.triggers:
            if int(t["map"], 16) == self.map_id and (t["x"], t["y"]) not in floor:
                errs.append(f"trigger {t['event']} not on floor")
        for e in self.exits["short_entrances"]:
            if int(e["map"], 16) == self.map_id and tuple(e["src"]) not in floor:
                errs.append("exit not on floor")
        # NPCs must not cut the floor graph (softlock check): remove NPC tiles and re-flood
        blocked = {(n["x"], n["y"]) for n in self.npcs}
        seen2, stack = set(), [(ax, ay)]
        while stack:
            x, y = stack.pop()
            if (x, y) in seen2 or (x, y) not in floor or (x, y) in blocked:
                continue
            seen2.add((x, y)); stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        cut = (floor - blocked) - seen2
        if cut:
            errs.append(f"NPC placement isolates floor tiles {sorted(cut)[:8]}")
        for n in self.npcs:   # every NPC must have a reachable neighbour to talk from
            if not any(nb in seen2 for nb in [(n["x"] + 1, n["y"]), (n["x"] - 1, n["y"]),
                                               (n["x"], n["y"] + 1), (n["x"], n["y"] - 1)]):
                errs.append(f"NPC {n['name']} cannot be talked to")
        if errs:
            raise MapError("walkability validation FAILED:\n  " + "\n  ".join(errs))
        grid = []
        marks = {(n["x"], n["y"]): "N" for n in self.npcs}
        marks.update({(t["x"], t["y"]): "T" for t in self.triggers if int(t["map"], 16) == self.map_id})
        marks.update({tuple(e["src"]): "X" for e in self.exits["short_entrances"] if int(e["map"], 16) == self.map_id})
        marks[(ax, ay)] = "@"
        for y in range(self.h):
            grid.append("".join(marks.get((x, y), "." if walk[y][x] else "#") for x in range(self.w)))
        return {"status": "PASS", "floor_tiles": len(floor), "reachable": len(seen),
                "tile_property_set": f"{tp_index:02X}", "grid": grid,
                "legend": "@ arrival, N npc, T trigger, X exit, . floor, # impassable"}

    def props_row(self, bg1_layout, bg2_layout, bg3_layout):
        b = self.map["properties"]["bytes"]
        hexs = lambda s: bytes.fromhex(s)
        row = bytearray()
        row += hexs(b["00_title"]) + hexs(b["01_flags"]) + hexs(b["02_bg3prio_battlebg"]) + hexs(b["03"])
        row += hexs(b["04_tile_prop_set"]) + hexs(b["05_random_battles"]) + hexs(b["06_window_mask"])
        row += hexs(b["07_12_gfx_sets"])
        v = bg1_layout | (bg2_layout << 10) | (bg3_layout << 20)
        row += v.to_bytes(4, "little")
        row += hexs(b["17_sprite_overlay"]) + hexs(b["18_21_bg23_shift"]) + hexs(b["22_parallax"])
        row += hexs(b["23_bg12_size"]) + hexs(b["24_bg3_size"]) + hexs(b["25_palette"]) + hexs(b["26_pal_anim"])
        row += hexs(b["27_bg_anim"]) + hexs(b["28_song"]) + hexs(b["29"]) + hexs(b["30_map_w"])
        row += hexs(b["31_map_h"]) + hexs(b["32_color_math"])
        if len(row) != 33:
            raise MapError(f"property row is {len(row)} bytes, expected 33")
        return bytes(row)
