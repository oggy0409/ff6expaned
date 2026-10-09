"""TECH v0.6.2 formation-safety validation for Expanded Edition formations (vanilla formations are never rewritten).

Two independent checks per formation, evaluated on the BUILT image (same bytes the game reads):

1. Screen layout. Each slot's sprite is decoded exactly as btlgfx does (MonsterGfxProp -> stencil -> tiles ->
   palette, clipped to the formation's VRAM-map box). Its opaque-pixel bounding box is placed at the formation
   position (x = (pos >> 4) * 8, y = (pos & 15) * 8; verified pixel-exact in v0.6.1) and compared with the visible
   battle field measured in snes9x (`VISIBLE`, see FORMATION_SAFETY_v0.6.2.md):
     left / top / right edge : margin < MIN_MARGIN (8 px) = ERROR, < PREFERRED_MARGIN (16 px) = WARNING
     bottom (window frame)   : crossing into the window (y > 150) = ERROR, margin < 8 px = WARNING
                               (vanilla puts ~20% of normal sprites 0-7 px above the window)
     party lane              : right edge beyond the vanilla maximum x = 167 = WARNING
   `layout_exception` {"slots": [...], "reason": "..."} downgrades edge ERRORs to WARNINGs for intentional
   large-boss compositions; it is refused for a slot whose sprite is not large (> 64 px or large stencil).

2. Magitek VRAM safety. With any party member in Magitek armor, the armor graphics overwrite the monster tile
   cells listed in data/vram_safety.json (rows 0-11, columns 12-15 of the 16x16 cell area, VRAM $6000-$7FFF).
   A sprite whose used cells hit that area renders as armor tiles (R13). Formation JSON must say
   `magitek_possible` (true/false) in enforce mode; true + conflict = ERROR with the list of VRAM maps that fit
   the same sprites without conflict (the author sets `vram_map` explicitly; nothing is chosen silently).

Modes: "enforce" (ERROR -> BuildError) for production targets; "report" for frozen QA/regression targets.
"""
import json, os
from .enemygfx import VRAM_MAPS, VRAM_MAP_POS

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VISIBLE = {"x_min": 8, "x_max": 247, "y_min": 4, "y_max": 150}     # inclusive; window frame starts at y = 151
MIN_MARGIN, PREFERRED_MARGIN, BOTTOM_MIN, BOTTOM_PREFERRED = 8, 16, 0, 8
PARTY_LANE_X = 167                                                     # vanilla maximum sprite right edge
LARGE_PX = 64

# relocated tables used by every v0.6-layout image (enemy_relocation_v06.json / monster_relocation_v05.json)
GFX_PROP_PC, STENCIL_PC, STENCIL_BANK_PC, PAL_PC, FORM_PC = 0x388000, 0x3B4000, 0x3B0000, 0x3B0000, 0x38A000
BASE_VANILLA, BASE_EXP = 0xE97000, 0xFB0000


class FormationSafetyError(ValueError):
    pass


def load_vram_safety():
    return json.load(open(os.path.join(HERE, "data", "vram_safety.json")))


def magitek_cells(table=None):
    t = table or load_vram_safety()
    return {(r, c) for r, c in t["magitek"]["conflict_cells_row_col"]}


def build_vram_safety_table(mask):
    """Derive the per-map/slot classification from the measured conflict mask (deterministic)."""
    maps = {}
    for vm in sorted(VRAM_MAPS):
        slots = []
        for s, ((bc, br), (bx, by)) in enumerate(zip(VRAM_MAPS[vm], VRAM_MAP_POS[vm])):
            box = {(by + r, bx + c) for r in range(br) for c in range(bc)}
            hit = box & mask
            if not hit:
                cls, cond = "safe", "any sprite that fits the box"
            elif (by, bx) in mask:
                cls, cond = "unsafe", "box origin is inside the Magitek area: every sprite conflicts"
            else:
                # largest sprite (cols x rows from the origin) that avoids the mask
                free_cols = min([c for (r, c) in mask if by <= r < by + br and bx <= c < bx + bc] or [bx + bc]) - bx
                free_rows = min([r for (r, c) in mask if by <= r < by + br and bx <= c < bx + bc] or [by + br]) - by
                cls = "sprite_dependent"
                cond = f"safe only if no used tile reaches the Magitek area (e.g. sprite <= {free_cols} columns wide)"
                if free_rows > 0 and free_rows < br:
                    cond += f" or <= {free_rows} rows tall"
            slots.append({"slot": s, "box_origin_col_row": [bx, by], "box_cols_rows": [bc, br],
                          "magitek_conflict_cells": len(hit), "magitek": cls, "condition": cond})
        maps[str(vm)] = {"slots": slots,
                         "magitek_all_slots_safe": all(x["magitek"] == "safe" for x in slots)}
    return maps


def _rgb(col):
    return ((col & 31) << 3, ((col >> 5) & 31) << 3, ((col >> 10) & 31) << 3)


def decode_sprite(img, mid, vmap, slot):
    """Sprite of monster `mid` as btlgfx draws it in (vmap, slot): opaque mask, colours, used cells."""
    gslot = mid if mid < 0x180 else mid + 0x20
    rec = img[GFX_PROP_PC + 5 * gslot:GFX_PROP_PC + 5 * gslot + 5]
    w = rec[0] | rec[1] << 8
    gidx, bpp3, large = w & 0x7FFF, bool(w & 0x8000), bool(rec[2] & 0x80)
    pal = ((rec[2] << 8) | rec[3]) & 0x3FF
    st_idx = rec[4] | ((rec[2] & 0x40) << 2)
    src = (BASE_EXP if rec[2] & 0x20 else BASE_VANILLA) + gidx * 8 - 0xC00000
    sp = img[STENCIL_PC] | img[STENCIL_PC + 1] << 8
    lp = img[STENCIL_PC + 2] | img[STENCIL_PC + 3] << 8
    if large:
        a = STENCIL_BANK_PC + lp + 32 * st_idx
        rows = [(img[a + 2 * k] << 8) | img[a + 2 * k + 1] for k in range(16)]
    else:
        a = STENCIL_BANK_PC + sp + 8 * st_idx
        rows = [img[a + k] << 8 for k in range(8)]
    n = 0
    while n < len(rows) and rows[n]:
        n += 1
    acc = 0
    for r in rows[:n]:
        acc |= r
    cols = max([c + 1 for c in range(16) if acc & (0x8000 >> c)] or [0])
    bc, br = VRAM_MAPS[vmap][slot]
    vis_cols, vis_rows = min(cols, bc), min(n, br)
    tsz = 24 if bpp3 else 32
    palb = img[PAL_PC + 16 * pal:PAL_PC + 16 * pal + 32]
    colours = [_rgb(palb[2 * i] | palb[2 * i + 1] << 8) for i in range(16)]
    W, H = vis_cols * 8, vis_rows * 8
    px = [[0] * W for _ in range(H)]
    cells, k = [], 0
    bx, by = VRAM_MAP_POS[vmap][slot]
    for r in range(n):
        for c in range(cols):
            if not rows[r] & (0x8000 >> c):
                continue
            t = img[src + k * tsz:src + (k + 1) * tsz]; k += 1
            if r >= vis_rows or c >= vis_cols:
                continue
            cells.append((by + r, bx + c))
            for y in range(8):
                for x in range(8):
                    b = 7 - x
                    v = ((t[2 * y] >> b) & 1) | (((t[2 * y + 1] >> b) & 1) << 1)
                    v |= ((t[16 + y] >> b) & 1) << 2 if bpp3 else (((t[16 + 2 * y] >> b) & 1) << 2) | (((t[17 + 2 * y] >> b) & 1) << 3)
                    px[r * 8 + y][c * 8 + x] = v
    return {"gfx_prop_record": rec.hex(" ").upper(), "large_stencil": large, "bpp": 3 if bpp3 else 4,
            "palette": pal, "stencil": st_idx, "cols": vis_cols, "rows": vis_rows, "clipped": (cols, n) != (vis_cols, vis_rows),
            "pixels": px, "colours": colours, "cells": cells}


def _issue(level, code, msg):
    return {"level": level, "code": code, "msg": msg}


def suggest_maps(img, slots, mask):
    """VRAM maps in which every used slot exists, its sprite fits the box unclipped, and no cell hits the mask."""
    out = []
    for vm in sorted(VRAM_MAPS):
        ok = True
        for s, mid in slots:
            if s >= len(VRAM_MAPS[vm]):
                ok = False; break
            full = decode_sprite(img, mid, 6, 0)               # map 6 slot 0 = 16x16 box: unclipped size
            bc, br = VRAM_MAPS[vm][s]
            if full["cols"] > bc or full["rows"] > br:
                ok = False; break
            if set(decode_sprite(img, mid, vm, s)["cells"]) & mask:
                ok = False; break
        if ok:
            out.append(vm)
    return out


def check_formation(img, fjson, mode, table=None, path="?"):
    table = table or load_vram_safety()
    mask = magitek_cells(table)
    fid = int(fjson["id"], 16)
    rec = img[FORM_PC + 15 * fid:FORM_PC + 15 * fid + 15]
    vmap = rec[0] >> 4
    issues, slots_out, used = [], [], []
    mp = fjson.get("magitek_possible")
    if mp is None:
        if mode == "enforce":
            issues.append(_issue("ERROR", "magitek_possible_missing",
                                 "formation must declare \"magitek_possible\": true/false (R13)"))
        mp_eval = True
    elif not isinstance(mp, bool):
        raise FormationSafetyError(f"{path}: magitek_possible must be true/false")
    else:
        mp_eval = mp
    exc = fjson.get("layout_exception") or {}
    exc_slots = set(exc.get("slots", []))
    if exc_slots and not str(exc.get("reason", "")).strip():
        issues.append(_issue("ERROR", "layout_exception_without_reason", "layout_exception needs a non-empty reason"))
    for s in range(6):
        mid = rec[2 + s] | (((rec[14] >> s) & 1) << 8)
        hidden = not rec[1] & (1 << s)
        if hidden and mid == 0x1FF:
            continue                    # empty slot; TECH v0.9.2: hidden-at-start members (shown later by AI) are checked too
        if s >= len(VRAM_MAPS[vmap]):
            issues.append(_issue("ERROR", "slot_not_in_vram_map", f"slot {s}: VRAM map {vmap} has no box for it"))
            continue
        sp = decode_sprite(img, mid, vmap, s)
        used.append((s, mid))
        pos = rec[8 + s]
        px0, py0 = (pos >> 4) * 8, (pos & 15) * 8
        opaque = [(x, y) for y, row in enumerate(sp["pixels"]) for x, v in enumerate(row) if v]
        if not opaque:
            issues.append(_issue("WARNING", "empty_sprite", f"slot {s} monster {mid:03X}: no opaque pixel"))
            continue
        x0 = px0 + min(x for x, _ in opaque); x1 = px0 + max(x for x, _ in opaque)
        y0 = py0 + min(y for _, y in opaque); y1 = py0 + max(y for _, y in opaque)
        m = {"left": x0 - VISIBLE["x_min"], "top": y0 - VISIBLE["y_min"],
             "right": VISIBLE["x_max"] - x1, "bottom": VISIBLE["y_max"] - y1}
        large = sp["large_stencil"] or sp["cols"] * 8 > LARGE_PX or sp["rows"] * 8 > LARGE_PX
        si = []
        for edge in ("left", "top", "right"):
            if m[edge] < MIN_MARGIN:
                si.append(_issue("ERROR", f"edge_{edge}", f"slot {s} monster {mid:03X}: {edge} margin {m[edge]} px < {MIN_MARGIN} px"
                                 + (" (touches/crosses the visible edge)" if m[edge] <= 0 else "")))
            elif m[edge] < PREFERRED_MARGIN:
                si.append(_issue("WARNING", f"edge_{edge}_preferred", f"slot {s} monster {mid:03X}: {edge} margin {m[edge]} px < preferred {PREFERRED_MARGIN} px"))
        if m["bottom"] < BOTTOM_MIN:
            si.append(_issue("ERROR", "edge_bottom_window", f"slot {s} monster {mid:03X}: sprite crosses into the battle window by {-m['bottom']} px"))
        elif m["bottom"] < BOTTOM_PREFERRED:
            si.append(_issue("WARNING", "edge_bottom_preferred", f"slot {s} monster {mid:03X}: bottom margin {m['bottom']} px above the window (< {BOTTOM_PREFERRED} px)"))
        if x1 > PARTY_LANE_X:
            si.append(_issue("WARNING", "party_lane", f"slot {s} monster {mid:03X}: right edge x={x1} beyond vanilla maximum {PARTY_LANE_X} (party sprites)"))
        if sp["clipped"]:
            si.append(_issue("WARNING", "clipped_by_vram_box", f"slot {s} monster {mid:03X}: sprite clipped to VRAM box {VRAM_MAPS[vmap][s]}"))
        if s in exc_slots:
            if not large:
                si.append(_issue("ERROR", "layout_exception_not_large", f"slot {s} monster {mid:03X}: layout_exception is only for large-boss sprites (> {LARGE_PX} px or large stencil)"))
            else:
                for x in si:
                    if x["level"] == "ERROR" and x["code"].startswith("edge_"):
                        x["level"] = "WARNING"; x["msg"] += f" [layout_exception: {exc['reason']}]"
        conflict = sorted(set(sp["cells"]) & mask)
        if conflict and mp_eval:
            lvl = "ERROR" if (mode == "enforce" or mp is True) else "WARNING"
            si.append(_issue(lvl, "magitek_vram_conflict",
                             f"slot {s} monster {mid:03X}: {len(conflict)} tile cell(s) in the Magitek VRAM area (map {vmap} slot {s})"))
        issues += si
        slots_out.append({"slot": s, "monster": f"{mid:03X}", "hidden_at_start": hidden, "position_byte": f"{pos:02X}", "origin_xy": [px0, py0],
                          "sprite_px": [sp["cols"] * 8, sp["rows"] * 8], "opaque_bbox": [x0, y0, x1, y1], "margins": m,
                          "large": large, "gfx_prop_record": sp["gfx_prop_record"], "palette": f"{sp['palette']:03X}",
                          "vram_box_origin_col_row": list(VRAM_MAP_POS[vmap][s]), "vram_box_cols_rows": list(VRAM_MAPS[vmap][s]),
                          "cells_used": len(sp["cells"]), "magitek_conflict_cells": [list(c) for c in conflict],
                          "status": "ERROR" if any(x["level"] == "ERROR" for x in si) else ("WARNING" if si else "OK")})
    rep = {"formation": f"{fid:03X}", "source": os.path.basename(path), "vram_map": vmap,
           "vram_map_magitek_all_slots_safe": table["vram_maps"][str(vmap)]["magitek_all_slots_safe"],
           "magitek_possible": mp, "layout_exception": exc or None, "slots": slots_out, "issues": issues}
    if any(x["code"] == "magitek_vram_conflict" for x in issues):
        rep["suggested_vram_maps"] = suggest_maps(img, used, mask)
    rep["status"] = "ERROR" if any(x["level"] == "ERROR" for x in issues) else ("WARNING" if issues else "OK")
    return rep


def check_target(img, formation_paths, mode):
    if mode not in ("enforce", "report"):
        raise FormationSafetyError(f"unknown formation_safety mode {mode!r}")
    table = load_vram_safety()
    reps = [check_formation(img, json.load(open(p)), mode, table, p) for p in formation_paths]
    res = {"mode": mode, "visible_field": VISIBLE, "rules": {"min_margin": MIN_MARGIN, "preferred_margin": PREFERRED_MARGIN,
           "bottom_min": BOTTOM_MIN, "bottom_preferred": BOTTOM_PREFERRED, "party_lane_x": PARTY_LANE_X, "large_px": LARGE_PX},
           "formations": reps,
           "errors": sum(x["level"] == "ERROR" for r in reps for x in r["issues"]),
           "warnings": sum(x["level"] == "WARNING" for r in reps for x in r["issues"])}
    if mode == "enforce" and res["errors"]:
        msgs = [f"${r['formation']}: {x['msg']}" + (f" -> Magitek-safe VRAM maps that fit: {r.get('suggested_vram_maps')}" if x["code"] == "magitek_vram_conflict" else "")
                for r in reps for x in r["issues"] if x["level"] == "ERROR"]
        raise FormationSafetyError("formation safety: " + "; ".join(msgs))
    return res
