"""TECH v0.4 map source packages (maps/<name>/), superset of ff6x/mapsrc.MapPackage.

Adds (without changing the frozen v0.3 compiler):
  * "compose" layers: a canvas filled with one tile plus rectangular blits copied
    from vanilla layouts (decompressed from the clean ROM) and optional per-tile
    overrides. Lets production reuse/consolidate vanilla room art in new maps.
  * BG2 layers built the same way (own new layout index), or a vanilla layout index.
  * long entrances (horizontal/vertical strips).
  * walkability proof for compose maps from the tile-property set:
    the region reachable from the arrival tile (exit tiles are terminal) must not
    touch the map border nor any canvas-fill tile, and every NPC / trigger / exit
    tile must be reachable.
"""
import json, os
from .lzss import decompress
from .hirom import snes_to_pc
from .mapsrc import MapPackage, MapError, load_tileprops, IMPASSABLE

SUBTILEMAP_PTRS = 0xD9CD90
SUBTILEMAP_BASE = 0xD9D1B0
VANILLA_LAYOUTS = 0x15E            # $000-$15D


def vanilla_layout(clean, index):
    if not 0 < index < VANILLA_LAYOUTS:
        raise MapError(f"vanilla layout {index:03X} out of range")
    p = snes_to_pc(SUBTILEMAP_PTRS) + 3 * index
    off = int.from_bytes(clean[p:p + 3], "little")
    return decompress(clean[snes_to_pc(SUBTILEMAP_BASE) + off:])


DIR_STEP = {"UP": (0, -1, 0x08), "RIGHT": (1, 0, 0x01), "DOWN": (0, 1, 0x04), "LEFT": (-1, 0, 0x02)}


def can_move(p1, p2, cur, dest, z):
    """Player movement rule (Rev 1 C0:4E35-4E9D): current tile byte-2 direction mask,
    destination counter/impassable (byte1 & 7 == 7), z-level / bridge rules.
    Returns new party z (1 upper / 2 lower) or None."""
    c1, d1 = p1[cur], p1[dest]
    if d1 & 7 == 7:
        return None
    if c1 & 4:                                   # current tile is a bridge
        if z & 1:
            if d1 & 2: return None
        else:
            if d1 & 1: return None
    else:
        if d1 & 3 != 3:
            if c1 & 3 == 3:
                if d1 & 4: return None
            elif (c1 & 3 ^ 3) & d1:
                return None
    if d1 & 4 or d1 & 3 in (0, 3):
        return z
    return d1 & 3


class MapPackageV4(MapPackage):
    def __init__(self, folder):
        j = lambda n: json.load(open(os.path.join(folder, n)))
        m = j("map.json")
        if "source" in m["bg1"]:
            super().__init__(folder)
            self.mode = "legend"
        else:
            self.folder, self.map = folder, m
            self.npcs = j("npcs.json")["npcs"]
            self.triggers = j("triggers.json")["triggers"]
            self.exits = j("exits.json")
            self.encounters = j("encounters.json")
            self.map_id = int(m["map_id"], 16)
            self.w, self.h = m["size_tiles"]
            self.mode = "compose"
        self.exits.setdefault("long_entrances", [])

    # ---------------------------------------------------------------- layers
    def _compose(self, clean, spec):
        w, h = self.w, self.h
        buf = bytearray([int(spec["fill"], 16)]) * (w * h)
        for b in spec["blits"]:
            src = vanilla_layout(clean, int(b["layout"], 16))
            lw, lh = b["layout_size"]
            if len(src) != lw * lh:
                raise MapError(f"layout {b['layout']} is {len(src)} bytes, not {lw}x{lh}")
            sx, sy, cw, ch = b["src"]
            dx, dy = b["dst"]
            if sx + cw > lw or sy + ch > lh or dx + cw > w or dy + ch > h:
                raise MapError("blit out of bounds")
            for y in range(ch):
                for x in range(cw):
                    buf[(dy + y) * w + dx + x] = src[(sy + y) * lw + sx + x]
        for x, y, t in spec.get("overrides", []):
            buf[y * w + x] = int(t, 16)
        return bytes(buf)

    def compile_layer(self, clean, layer):
        spec = self.map[layer]
        if layer == "bg1" and self.mode == "legend":
            return self.compile_bg1()
        if "compose" in spec:
            return self._compose(clean, spec["compose"])
        return None                                     # vanilla layout index only

    def fill_mask(self):
        """Canvas cells not covered by any BG1 blit (compose mode)."""
        spec = self.map["bg1"]["compose"]
        cov = [[False] * self.w for _ in range(self.h)]
        for b in spec["blits"]:
            sx, sy, cw, ch = b["src"]; dx, dy = b["dst"]
            for y in range(ch):
                for x in range(cw):
                    cov[dy + y][dx + x] = True
        return cov

    def exit_cells(self):
        cells = set()
        for e in self.exits["short_entrances"]:
            if int(e["map"], 16) == self.map_id:
                cells.add(tuple(e["src"]))
        for e in self.exits["long_entrances"]:
            if int(e["map"], 16) == self.map_id:
                x, y = e["src"]
                for k in range(e["length"] + 1):
                    cells.add((x, y + k) if e.get("vertical") else (x + k, y))
        return cells

    def movement_reach(self, clean, bg1=None):
        """Cells reachable by the player from the arrival tile under the engine movement
        rules (exit cells are terminal). Returns (cells, edges_by_cell)."""
        tp = int(self.map["tile_property_set"].split()[0], 16)
        p1, p2 = load_tileprops(clean, tp)
        bg1 = bg1 or self.compile_layer(clean, "bg1")
        exits = self.exit_cells()
        ax, ay = self.map["entry"]["arrive"]
        z0 = 1 if self.map["entry"].get("z", "lower") == "upper" else 2
        seen, cells, stack = set(), set(), [(ax, ay, z0)]
        while stack:
            x, y, z = stack.pop()
            if (x, y, z) in seen:
                continue
            seen.add((x, y, z)); cells.add((x, y))
            if (x, y) in exits:
                continue
            cur = bg1[y * self.w + x]
            for d, (dx, dy, mask) in DIR_STEP.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < self.w and 0 <= ny < self.h) or not (p2[cur] & 0x0F & mask):
                    continue
                nz = can_move(p1, p2, cur, bg1[ny * self.w + nx], z)
                if nz is not None:
                    stack.append((nx, ny, nz))
        return cells

    # -------------------------------------------------------------- validate
    def validate(self, clean):
        if self.mode == "legend":
            rep = super().validate(clean)
            floor = {(x, y) for y in range(self.h) for x in range(self.w) if self.walk_grid()[y][x]}
            mv = self.movement_reach(clean)
            if mv != floor:
                raise MapError(f"movement model disagrees with floor grid: unreachable {sorted(floor - mv)[:6]}, "
                               f"extra {sorted(mv - floor)[:6]}")
            rep["movement_model"] = "PASS (direction masks + z-level rules)"
            for c in self.exit_cells():
                if c not in floor:
                    raise MapError(f"exit cell {c} not on floor")
            for e in self.exits["long_entrances"]:
                if int(e["map"], 16) == self.map_id:
                    x, y = e["src"]
                    for k in range(e["length"] + 1):
                        cx, cy = (x, y + k) if e.get("vertical") else (x + k, y)
                        rep["grid"][cy] = rep["grid"][cy][:cx] + "L" + rep["grid"][cy][cx + 1:]
            rep["legend"] += ", L long entrance"
            return rep
        tp = int(self.map["tile_property_set"].split()[0], 16)
        p1, _ = load_tileprops(clean, tp)
        bg1 = self.compile_layer(clean, "bg1")
        passable = lambda x, y: p1[bg1[y * self.w + x]] != IMPASSABLE and (p1[bg1[y * self.w + x]] & 3)
        exits = self.exit_cells()
        fill = self.fill_mask()
        ax, ay = self.map["entry"]["arrive"]
        errs = []
        if not passable(ax, ay):
            errs.append("arrival tile not passable")
        seen = self.movement_reach(clean, bg1)
        for x, y in seen:
            if x in (0, self.w - 1) or y in (0, self.h - 1):
                errs.append(f"reachable tile on map border {x},{y}")
            if not fill[y][x]:
                errs.append(f"reachable tile {x},{y} is canvas fill (leak)")
        for n in self.npcs:
            if (n["x"], n["y"]) not in seen:
                errs.append(f"NPC {n['name']} not on reachable floor")
        for t in self.triggers:
            if int(t["map"], 16) == self.map_id and (t["x"], t["y"]) not in seen:
                errs.append(f"trigger {t['event']} not reachable")
        for c in exits:
            if c not in seen:
                errs.append(f"exit cell {c} not reachable")
        blocked = {(n["x"], n["y"]) for n in self.npcs}
        seen2, stack = set(), [(ax, ay)]
        while stack:
            x, y = stack.pop()
            if (x, y) in seen2 or (x, y) not in seen or (x, y) in blocked:
                continue
            seen2.add((x, y))
            if (x, y) in exits:
                continue
            stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        cut = (seen - blocked) - seen2
        if cut:
            errs.append(f"NPC placement isolates {sorted(cut)[:8]}")
        for n in self.npcs:
            if not any(nb in seen2 for nb in [(n["x"] + 1, n["y"]), (n["x"] - 1, n["y"]),
                                               (n["x"], n["y"] + 1), (n["x"], n["y"] - 1)]):
                errs.append(f"NPC {n['name']} cannot be talked to")
        if errs:
            raise MapError("walkability validation FAILED:\n  " + "\n  ".join(errs))
        marks = {(n["x"], n["y"]): "N" for n in self.npcs}
        marks.update({(t["x"], t["y"]): "T" for t in self.triggers if int(t["map"], 16) == self.map_id})
        marks.update({c: "X" for c in exits})
        marks[(ax, ay)] = "@"
        grid = ["".join(marks.get((x, y), "." if (x, y) in seen else "#") for x in range(self.w)) for y in range(self.h)]
        return {"status": "PASS", "mode": "compose", "reachable": len(seen), "tile_property_set": f"{tp:02X}",
                "grid": grid, "legend": "@ arrival, N npc, T trigger, X exit, . reachable floor, # other"}

    def walk_grid_runtime(self, clean):
        """Expected passability grid (for the emulator RAM check)."""
        tp = int(self.map["tile_property_set"].split()[0], 16)
        p1, _ = load_tileprops(clean, tp)
        bg1 = self.compile_layer(clean, "bg1")
        return ["".join("." if (p1[bg1[y * self.w + x]] != IMPASSABLE and p1[bg1[y * self.w + x]] & 3) else "#"
                        for x in range(self.w)) for y in range(self.h)]
