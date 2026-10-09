#!/usr/bin/env python3
"""TECH v0.9.3 visual regression (S1-S4 + party state) on rendered frames, run on bsnes (accurate PPU) and snes9x.

Every scenario starts from New Game WITHOUT a party preset - the path of the v0.9.2 user guide (party right after
New Game = Terra + Wedge + Vicks, all three in Magitek armor), which is where the user runtime found the defects.
Run it on the v0.9.2 QA ROM for the BEFORE evidence (expected FAIL) and on the v0.9.3 QA ROM (expected PASS).

  N1  party normaliser: after each Celes-enabler hub entry no party member / record has Magitek status, Wedge / Vicks
      are not in the party, the party is P1 (Terra Locke Celes Edgar) when nobody but Terra was in it
  S1  map $1A2 palette: frame of the north room (RESET state) vs the same frame with vanilla palette $18 poked into
      the field palette buffers (reference = the source map's palette on the same tiles): BG mean colour distance,
      BG saturation ratio, BG contrast kept; colour RAM (bsnes CGRAM / snes9x buffer $7200) = v0.9.3 derived palette;
      sprite palette rows 0-6 = vanilla MapSpritePal 0-6 (no sprite palette corruption)
  S2  WoR dog: TEMP ROM COPY (test only) whose World-of-Ruin battle groups at the landing sector all point to the
      Lunaris formations $CB / $CA; New Game -> hub 'WoR aboard the Falcon' -> land -> walk until a battle: Magitek
      battle mode off, every monster pixel-exact vs its ROM graphics (MonsterGfxProp -> stencil -> tiles -> palette)
      at its formation position in every sampled frame; the dog's bounding box crop is saved
  S3  Praetor + Bit + Bit after the 70% reveal (QA-scaled $245 from the hub, and the locked $244): monster ATB held
      after the reveal (POKE); a bounded settle (<= 600 frames) lets the reveal / Reflect sprite effect finish (the
      first unsettled frame is saved as *_transient_before_settle.png); then every sampled frame without a battle
      message window over the Bits (>= 10 of 16):
      both Bits pixel-exact vs ROM data at their formation positions,
      and the two Bit crops (position-normalised) identical; Magitek battle mode off
  S4  E8 map states RESET / PRESERVE / BURN / GRAVES: BG1 tilemap RAM ($7F0000) = maps/celes_outer_v092/states.json,
      and rendered crops: memorial region differs none / tags / stone, archive region differs sealed / kept / burned;
      persistence: map exit -> world map -> re-entry (E1 path) and save -> power cycle -> Continue show the same
      pixels (equal to one frame of the in-session 64-frame series: tiles of this tileset are BG-animated) and tiles

usage: [FF6X_EMU=bsnes|snes9x] emu_visual_v093.py <qa.sfc> <qa.manifest.json> <out> [only=S1,S2,...]
writes <out>/VISUAL_REPORT_v093.json and screenshots / crops
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
EMU = os.environ.get("FF6X_EMU", "bsnes")
if EMU == "bsnes":
    import emu_bsnes
    emu_bsnes.use_bsnes()
import numpy as np
from PIL import Image
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, dump_sram, write_sram, continue_slot1
import emu_enablers_v092 as EN
from emu_celes_suite import walk, pos
from emu_menu_nav import Nav, ST
import gfx_compare_report as GC
from patches import celes_enablers_v092 as CE

CLEAN = os.path.join(HERE, "..", "Final Fantasy III (USA) (Rev 1).sfc")
MAP_PAL_PC = 0x2DC480
X0, Y0 = 120, 111                     # screen x of tile column 16 / screen y of tile row 14 with the player at (16,14)
ENGINE_COLOURS = {1, 2, 3} | set(range(121, 128))
MAGITEK_MODE = 0x64BA                 # btlgfx wMagitekModeEnabled (KNOWN_RISKS_v0.7.3 R19)
LUNARIS = 0x0CA


def shot(h, out, name):
    img = np.asarray(h.em.get_screen()).copy()
    Image.fromarray(img).save(os.path.join(out, name + ".png"))
    return img


def tile_box(tx, ty, w, hgt):
    x, y = X0 + (tx - 16) * 16, Y0 + (ty - 14) * 16
    return x, y, x + 16 * w, y + 16 * hgt


def crop(img, box):
    x0, y0, x1, y1 = box
    return img[y0:y1, x0:x1]


def series(h, boxes, frames=64):
    """crops of `boxes` over `frames` frames (BG tile animation cycles, map property 27): list of tuples of crops"""
    out = []
    for _ in range(frames):
        img = np.asarray(h.em.get_screen())
        out.append(tuple(crop(img, b).copy() for b in boxes))
        h.step(1)
    return out


def in_series(c, ser, k):
    return any(c.shape == s[k].shape and (c == s[k]).all() for s in ser)


def diff_frac(a, b):
    return float(np.mean(np.any(a != b, axis=2)))


def bg_colours(h):
    """field BG colours 0-127 as seen by the PPU (bsnes CGRAM) or the field palette buffer (snes9x)"""
    if hasattr(h, "cgram") and EMU == "bsnes":
        return h.cgram()[:256]
    return h.rbytes(0x7200, 256)


def sprite_colours(h):
    if hasattr(h, "cgram") and EMU == "bsnes":
        return h.cgram()[256:512]
    return h.rbytes(0x7300, 256)


def party_state(h):
    party = [i for i in range(16) if h.r8(0x1850 + i) & 7]
    return {"party": party, "magitek_records": [i for i in range(16) if h.r8(0x1614 + 37 * i) & 0x08],
            "party_magitek": [i for i in party if h.r8(0x1614 + 37 * i) & 0x08]}


def normalised(ps):
    return not ps["party_magitek"] and 14 not in ps["party"] and 15 not in ps["party"] and len(ps["party"]) >= 2


def calm_step(h, n=1, btn=()):
    """POKE (test only): world-map battle counter $1F6E/$1F6F held at 0 while walking (no random encounter)"""
    for _ in range(n):
        h.w8(0x1F6E, 0); h.w8(0x1F6F, 0)
        h.step(1, btn)


def wait_idle(h, n=2400):
    for _ in range(n):
        if h.idle():
            return True
        h.step(1)
    return False


def hold_step(h, n=1, mons=range(6)):
    for _ in range(n):
        for m in mons:
            h.w8(0x3218 + 8 + 2 * m, 0); h.w8(0x3219 + 8 + 2 * m, 0)
        h.step(1)


def message_window(scr):
    """the battle message window (top centre, blue) is drawn over the upper monsters while an action name is shown"""
    m = scr[12:36, 60:196].reshape(-1, 3).astype(int).mean(axis=0)
    return m[2] > 110 and m[2] > m[0] + 60


def expected_sprites(romb, Tb, h):
    """per formation slot: (index map, rgb) of the monster graphics from ROM and its screen origin"""
    fid = h.r16(0x3ED4)
    frec = romb[Tb["form"] + 15 * fid:Tb["form"] + 15 * fid + 15]
    exp = {}
    for s in range(6):
        mid = h.r16(0x2001 + 2 * s)
        if mid in (0xFFFF,) or mid >= 0x200:
            continue
        dd, tiles, palb = GC.decode_slot(romb, Tb, mid)
        idx, rgb = GC.render(tiles, palb, *dd["stencil_cols_rows"])
        exp[s] = {"mid": mid, "idx": idx, "rgb": rgb, "xy": ((frec[8 + s] >> 4) * 8, (frec[8 + s] & 15) * 8)}
    return fid, exp


def exact(scr, e):
    x, y = e["xy"]
    s5 = scr.astype(np.int32) >> 3
    win = s5[y:y + e["idx"].shape[0], x:x + e["idx"].shape[1]]
    if win.shape[:2] != e["idx"].shape:
        return False, -1
    bad = np.any(win != e["rgb"], axis=2) & (e["idx"] != 0)
    return not bad.any(), int(bad.sum())


def bit_crop(scr, e):
    x, y = e["xy"]
    c = scr[y:y + e["idx"].shape[0], x:x + e["idx"].shape[1]].copy()
    c[e["idx"] == 0] = 0                       # background removed: position-normalised opaque pixels only
    return c


def main(qa, manifest, out, only=None):
    os.makedirs(out, exist_ok=True)
    only = set(only.split("=")[1].split(",")) if only else {"N1", "S1", "S2", "S3", "S4"}
    q = Report(out)
    L = EN.evlabels(manifest)
    romb = open(qa, "rb").read()
    clean = open(CLEAN, "rb").read()
    Tb = GC.rom_tables(romb)
    states = json.load(open(os.path.join(HERE, "maps", "celes_outer_v092", "states.json")))
    pal_src = CE.load_palettes()["map_palettes"][0]
    exp_pal = CE.derive(clean[MAP_PAL_PC + 256 * 0x18:MAP_PAL_PC + 256 * 0x19], pal_src["transform"])
    van18 = clean[MAP_PAL_PC + 256 * 0x18:MAP_PAL_PC + 256 * 0x19]
    res = {"emulator": EMU, "rom": os.path.basename(qa)}
    h = T(qa)
    boot_new_game(h)
    wait_idle(h)
    st0 = h.em.get_state()
    res["new_game_party"] = party_state(h)

    def enter_outer(picks_list=()):
        h.em.set_state(st0); h.step(10)
        for p in picks_list:
            EN.hub(h, L, p)
        EN.hub(h, L, [1, 2, 2, 0])                      # Celes enablers -> More -> More -> Walk into the outer map
        h.step(500)
        ps = party_state(h)
        ps["leader_vehicle_bits"] = h.r8(0x0868) & 0x60    # object 0 ($0868 svv-----): 0 = on foot (no Magitek armor)
        walk(h, "UP", 13)
        h.step(60)
        return ps

    # ---------------------------------------------------------------- S1 palette (+ N1 for the walk-in entry)
    if "S1" in only or "N1" in only:
        ps = enter_outer()
        img = shot(h, out, "S1_1A2_reset")
        bgc, sprc = bg_colours(h), sprite_colours(h)
        st_room = h.em.get_state()
        for i in range(8, 242):                         # reference: vanilla $18 on the same tiles (engine colours kept)
            h.w8(0x7200 + i, van18[i]); h.w8(0x7400 + i, van18[i])
        h.step(6)
        ref = shot(h, out, "S1_reference_vanilla18")
        h.em.set_state(st_room)
        mask = np.ones(img.shape[:2], bool)
        mask[96:140, 104:152] = False                    # player sprite
        mask[100:130, 180:220] = False                   # survivor NPC
        lref = 0.3 * ref[..., 0] + 0.59 * ref[..., 1] + 0.11 * ref[..., 2]
        lit = mask & (lref >= 64)                        # lit BG pixels (floor / wall highlights): where colour is visible
        a, b = img[lit].astype(float), ref[lit].astype(float)
        dist = float(np.abs(a - b).mean())
        sat = lambda p: float((p.max(axis=1) - p.min(axis=1)).mean())
        lum = lambda p: float((0.3 * p[:, 0] + 0.59 * p[:, 1] + 0.11 * p[:, 2]).std())
        aa, bb = img[mask].astype(float), ref[mask].astype(float)
        s1 = {"lit_bg_pixels": int(lit.sum()), "lit_bg_mean_abs_rgb_distance_vs_vanilla18": round(dist, 1),
              "lit_bg_saturation": round(sat(a), 1), "lit_bg_saturation_vanilla18": round(sat(b), 1),
              "bg_luma_std": round(lum(aa), 1), "bg_luma_std_vanilla18": round(lum(bb), 1)}
        cdiff = [i for i in range(4, 121) if bgc[2 * i:2 * i + 2] != exp_pal[2 * i:2 * i + 2]]
        s1["bg_colours_not_v093_palette"] = cdiff[:12]
        van_spr = clean[0x268000:0x268000 + 7 * 32]       # vanilla MapSpritePal 0-6 (E6:8000)
        sdiff = [i for i in range(0, 7 * 16) if sprc[2 * i:2 * i + 2] != van_spr[2 * i:2 * i + 2] and i % 16]
        s1["sprite_colours_slots0_6_differing_from_vanilla"] = sdiff[:12]
        res["S1"] = s1
        if "S1" in only:
            q.check("S1a map $1A2 RESET frame vs the same frame in vanilla palette $18, lit BG pixels: visibly different "
                    "(mean RGB distance >= 12), grey / ash (saturation <= 50% of vanilla), still readable (BG luma contrast "
                    ">= 60% of vanilla)", dist >= 12 and sat(a) <= 0.5 * sat(b) and lum(aa) >= 0.6 * lum(bb), s1)
            q.check("S1b colour RAM BG rows = the v0.9.3 derived palette $30 (PPU CGRAM on bsnes / field buffer on snes9x)",
                    not cdiff, {"differing_colours": cdiff[:12]})
            q.check("S1c sprite palettes (party / NPC slots 0-6) = vanilla MapSpritePal 0-6: no sprite palette corruption "
                    "from the map palette", not sdiff, {"differing": sdiff[:12]})
        q.check("N1a walk-in entry: party normalised (no Magitek status in the party, Wedge / Vicks out, >= 2 members), "
                "Terra on foot (field vehicle none)", normalised(ps) and ps["leader_vehicle_bits"] == 0, ps)

    # ---------------------------------------------------------------- S4 E8 visible states
    if "S4" in only:
        reg = states["regions"]
        mem_box = tile_box(reg["memorial"]["x"], reg["memorial"]["y"], reg["memorial"]["w"], reg["memorial"]["h"])
        arc_box = tile_box(reg["archive"]["x"], reg["archive"]["y"], reg["archive"]["w"], reg["archive"]["h"])

        def tilemap(hh, r):                         # BG1 map layout buffer $7F:0000 (256 tiles per row)
            return [hh.r8(0x10000 + (r["y"] + j) * 256 + r["x"] + i) for j in range(r["h"]) for i in range(r["w"])]

        def want(region, state):
            return [int(t, 16) for row in states["states"][region][state]["rows"] for t in row.split()]
        seq = (("reset", [], "none", "sealed"), ("preserve", [[1, 2, 0, 1]], "tags", "kept"),
               ("burn", [[1, 2, 0, 0]], "tags", "burned"), ("graves", [[1, 2, 0, 1], [1, 2, 0, 2, 0]], "stone", "kept"))
        crops, tm, sers = {}, {}, {}
        for tag, picks, m, a_ in seq:
            enter_outer(picks)
            img = shot(h, out, f"S4_{tag}")
            crops[tag] = (crop(img, mem_box), crop(img, arc_box))
            sers[tag] = series(h, (mem_box, arc_box))
            Image.fromarray(crops[tag][0]).resize((128, 64), Image.NEAREST).save(os.path.join(out, f"S4_{tag}_memorial.png"))
            Image.fromarray(crops[tag][1]).resize((64, 64), Image.NEAREST).save(os.path.join(out, f"S4_{tag}_archive.png"))
            tm[tag] = {"memorial": tilemap(h, reg["memorial"]), "archive": tilemap(h, reg["archive"]),
                       "want": [want("memorial", m), want("archive", a_)]}
        res["S4_tilemap"] = {k: {"memorial": [f"{x:02X}" for x in v["memorial"]], "archive": [f"{x:02X}" for x in v["archive"]]}
                             for k, v in tm.items()}
        q.check("S4a BG1 tilemap RAM after each state = states.json (reset none/sealed, preserve tags/kept, burn "
                "tags/burned, graves stone/kept)", all([v["memorial"], v["archive"]] == v["want"] for v in tm.values()),
                res["S4_tilemap"])
        M = {k: c[0] for k, c in crops.items()}
        A = {k: c[1] for k, c in crops.items()}
        md = {"reset_vs_temp": diff_frac(M["reset"], M["preserve"]), "temp_vs_stone": diff_frac(M["preserve"], M["graves"]),
              "reset_vs_stone": diff_frac(M["reset"], M["graves"]), "temp_preserve_vs_temp_burn": 0.0 if in_series(M["burn"], sers["preserve"], 0) else 1.0}
        ad = {"sealed_vs_kept": diff_frac(A["reset"], A["preserve"]), "sealed_vs_burned": diff_frac(A["reset"], A["burn"]),
              "kept_vs_burned": diff_frac(A["preserve"], A["burn"]), "kept_preserve_vs_kept_graves": 0.0 if in_series(A["graves"], sers["preserve"], 1) else 1.0}
        res["S4_pixels"] = {"memorial": {k: round(v, 3) for k, v in md.items()}, "archive": {k: round(v, 3) for k, v in ad.items()}}
        q.check("S4b rendered memorial region (64 x 32 px): RESET / temporary tags / permanent stone pairwise differ in "
                ">= 60% of the pixels (the whole object changes, not a few edge pixels); the temporary memorial is the same "
                "in both branches",
                md["reset_vs_temp"] >= 0.6 and md["temp_vs_stone"] >= 0.6 and md["reset_vs_stone"] >= 0.6
                and md["temp_preserve_vs_temp_burn"] == 0, res["S4_pixels"]["memorial"])
        q.check("S4c rendered archive region (32 x 32 px): sealed / Preserve / Burn pairwise differ in >= 60% of the "
                "pixels; Graves keeps the retained archive", ad["sealed_vs_kept"] >= 0.6 and ad["sealed_vs_burned"] >= 0.6
                and ad["kept_vs_burned"] >= 0.6 and ad["kept_preserve_vs_kept_graves"] == 0, res["S4_pixels"]["archive"])
        # persistence 1: E1 path with Preserve + Graves: world map -> $1A2 -> exit -> world map -> re-entry
        h.em.set_state(st0); h.step(10)
        EN.hub(h, L, [1, 2, 0, 1]); EN.hub(h, L, [1, 2, 0, 2, 0])
        h.call_event(L["QaWor92"], frames=1); h.step(700)
        calm_step(h, 20, ("B",)); calm_step(h, 400)
        ps_wor = party_state(h)
        for _ in range(2):
            calm_step(h, 16, ("UP",)); calm_step(h, 20)
        calm_step(h, 700)
        first = (h.r16(0x82), pos(h))
        walk(h, "UP", 13); h.step(60)
        i1 = shot(h, out, "S4_persist_world_entry_1")
        t1 = (tilemap(h, reg["memorial"]), tilemap(h, reg["archive"]))
        walk(h, "DOWN", 13)
        for _ in range(3):
            calm_step(h, 16, ("DOWN",)); calm_step(h, 20)
        calm_step(h, 700)
        back = (h.r16(0x1F64) & 0x1FF, h.r8(0x1F60), h.r8(0x1F61))
        for _ in range(1):
            calm_step(h, 16, ("UP",)); calm_step(h, 20)
        calm_step(h, 700)
        second = (h.r16(0x82), pos(h))
        walk(h, "UP", 13); h.step(60)
        i2 = shot(h, out, "S4_persist_world_entry_2")
        t2 = (tilemap(h, reg["memorial"]), tilemap(h, reg["archive"]))
        pers1 = {"first_entry": first, "back_on_world": back, "second_entry": second,
                 "memorial_equal_to_in_session_graves": in_series(crop(i1, mem_box), sers["graves"], 0),
                 "archive_equal_to_in_session_graves": in_series(crop(i1, arc_box), sers["graves"], 1),
                 "re_entry_pixels_equal": in_series(crop(i2, mem_box), sers["graves"], 0) and in_series(crop(i2, arc_box), sers["graves"], 1),
                 "tilemaps": [[f"{x:02X}" for x in t1[0]], [f"{x:02X}" for x in t1[1]], t1 == t2]}
        res["S4_persist_world"] = pers1
        q.check("S4d Preserve + Graves via the World of Ruin entrance: stone memorial + retained archive drawn; exit to "
                "the world map and re-entry show the same pixels and tiles",
                first[0] == 0x1A2 and second[0] == 0x1A2 and back[0] == 1 and pers1["memorial_equal_to_in_session_graves"]
                and pers1["archive_equal_to_in_session_graves"] and pers1["re_entry_pixels_equal"] and t1 == t2
                and list(t1) == [want("memorial", "stone"), want("archive", "kept")], pers1)
        q.check("N1b WoR entry: party normalised", normalised(ps_wor), ps_wor)
        # persistence 2: save -> power cycle -> Continue -> walk in
        h.em.set_state(st0); h.step(10)
        EN.hub(h, L, [1, 2, 0, 1]); EN.hub(h, L, [1, 2, 0, 2, 0])
        wait_idle(h, 600); h.step(60)
        h.w8(0x1EB7, h.r8(0x1EB7) | 0x80)              # POKE (test only): "on a save point"
        nv = Nav(h)
        for _ in range(6):
            h.step(60); nv.open_main()
            if nv.state() == ST["MAIN"]:
                break
        nv.main_to("Save"); nv.wait(ST["SAVE_SELECT"], 400)
        h.press("A", 4, 60); h.press("A", 4, 200)
        blk, sram = dump_sram(h)
        h.close()
        h = T(qa)
        write_sram(h, blk, sram)
        continue_slot1(h)
        for t in range(3000):
            if h.idle():
                break
            h.step(1)
            if t % 200 == 199:
                h.press("B", 4, 10)
        h.step(30)
        h.call_event(L["QaOuter92"], frames=1); h.step(600)
        walk(h, "UP", 13); h.step(60)
        i3 = shot(h, out, "S4_persist_after_power_cycle")
        t3 = (tilemap(h, reg["memorial"]), tilemap(h, reg["archive"]))
        pers2 = {"memorial_equal": in_series(crop(i3, mem_box), sers["graves"], 0),
                 "archive_equal": in_series(crop(i3, arc_box), sers["graves"], 1),
                 "tiles": [[f"{x:02X}" for x in t3[0]], [f"{x:02X}" for x in t3[1]]]}
        res["S4_persist_power_cycle"] = pers2
        q.check("S4e save -> power cycle -> Continue -> walk in: stone memorial + retained archive, pixel-identical to "
                "the in-session Graves frame", pers2["memorial_equal"] and pers2["archive_equal"]
                and list(t3) == [want("memorial", "stone"), want("archive", "kept")], pers2)
        h.close()
        h = T(qa)
        boot_new_game(h); wait_idle(h)
        st0 = h.em.get_state()

    # ---------------------------------------------------------------- S3 Praetor + Bits
    if "S3" in only:
        for label, tag in (("QaPraetorS92", "245_scaled"), ("QaPraetorL92", "244_locked")):
            h.em.set_state(st0); h.step(10)
            EN.start_battle(h, L, label)
            ps = party_state(h)
            mt = h.r8(MAGITEK_MODE)
            mx = h.r16(EN.MAXHP + 2 * EN.PRAETOR)
            EN.set_hp(h, mx * 70 // 100 + 10)              # POKE: just above 70%
            EN.terra_fight(h)
            for _ in range(4):                              # (v0.9.2 path: Magitek command menu - confirm the target)
                if h.r8(0x2F2F) == 7:
                    break
                h.press("A", 8, 10); EN.run(h, 300)
            shown = h.r8(0x2F2F)
            hold_step(h, 240)                              # POKE: monster ATB held - no new action over the Bits
            for _ in range(60):                            # the reveal's queued Reflect: wait until its window is gone
                if not message_window(np.asarray(h.em.get_screen())):
                    break
                hold_step(h, 10)
            fid, exp = expected_sprites(romb, Tb, h)
            bits = [s for s in (1, 2) if s in exp]
            # settle: the reveal / queued Reflect play short sprite effects on a Bit (white outline frames; seen on bsnes).
            # Wait (bounded, 600 frames) until no window is up and both Bits are exact; then EVERY one of the 16 samples
            # must be exact. A persistent defect (v0.9.2: armor tiles) never settles, so it still fails all samples.
            settle, transient = 0, None
            for _ in range(60):
                scr = np.asarray(h.em.get_screen())
                if not message_window(scr) and all(exact(scr, exp[s])[0] for s in bits):
                    break
                if transient is None:
                    transient = scr.copy()
                    Image.fromarray(transient).save(os.path.join(out, f"S3_{tag}_transient_before_settle.png"))
                hold_step(h, 10); settle += 10
            frames, skipped, bad, same = 0, 0, {s: 0 for s in bits}, True
            first = None
            for k in range(16):
                hold_step(h, 10)
                scr = np.asarray(h.em.get_screen())
                if message_window(scr):                    # an action name window covers the Bits: not a sample
                    skipped += 1
                    continue
                frames += 1
                for s in bits:
                    ok, nbad = exact(scr, exp[s])
                    if not ok:
                        bad[s] += 1
                if len(bits) == 2:
                    c1, c2 = bit_crop(scr, exp[1]), bit_crop(scr, exp[2])
                    if c1.shape != c2.shape or (c1 != c2).any():
                        same = False
                    if first is None:
                        first = (c1, c2)
            img = shot(h, out, f"S3_{tag}_after_70")
            if first:
                pair = np.concatenate([first[0], np.zeros((first[0].shape[0], 4, 3), np.uint8), first[1]], axis=1)
                Image.fromarray(pair).resize((pair.shape[1] * 4, pair.shape[0] * 4), Image.NEAREST).save(
                    os.path.join(out, f"S3_{tag}_bit_crops.png"))
            ps_exact = exact(np.asarray(h.em.get_screen()), exp[0])[0] if 0 in exp else None
            r3 = {"formation": f"{fid:03X}", "shown_mask": f"{shown:02X}", "magitek_mode": mt, "party": ps,
                  "bit_frames_not_exact": {str(s): bad[s] for s in bits}, "sampled_frames": frames,
                  "frames_skipped_message_window": skipped, "settle_frames": settle,
                  "transient_seen_before_settle": transient is not None,
                  "bit_crops_identical": same, "praetor_exact_last_frame": ps_exact}
            res[f"S3_{tag}"] = r3
            q.check(f"S3 {tag}: Praetor + Bit + Bit after the 70% reveal (shown $07), Magitek battle mode off; both Bits "
                    "pixel-exact vs ROM graphics at their formation positions in all sampled frames; the two Bit crops "
                    "identical (>= 10 sampled frames without a message window over them)", shown == 7 and mt == 0 and len(bits) == 2
                    and frames >= 10 and not any(bad.values()) and same, r3)
            if tag == "245_scaled":
                q.check("N1c Praetor entry: party normalised", normalised(ps), ps)
            EN.finish_battle(h)

    # ---------------------------------------------------------------- S2 WoR dog (temp ROM copy)
    if "S2" in only:
        h.close()
        r = bytearray(romb)
        groups = set()
        x, y = 146, 204
        sec = 256 + (y >> 5) * 32 + (x >> 5) * 4
        for k in range(4):
            g = r[0x0F5400 + sec + k]
            groups.add(g)
        for g in groups:
            for j, f in enumerate((0xCB, 0xCA, 0xCB, 0xCA)):
                r[0x0F4800 + 8 * g + 2 * j] = f; r[0x0F4800 + 8 * g + 2 * j + 1] = 0
        tmp = os.path.join(out, "_tmp_wor_lunaris.sfc")
        open(tmp, "wb").write(r)
        h = T(tmp)
        boot_new_game(h); wait_idle(h)
        h.call_event(L["QaWor92"], frames=1); h.step(700)
        h.step(20, ("B",)); h.step(400)
        ps = party_state(h)
        got = False
        for k in range(400):
            h.step(16, (("LEFT", "RIGHT")[k % 2],)); h.step(4)
            sc = np.asarray(h.em.get_screen())[165:215].reshape(-1, 3).mean(axis=0)
            if sc[2] > sc[0] + 50 and sc[2] > 90:
                got = True
                break
        h.step(240)
        mt = h.r8(MAGITEK_MODE)
        fid, exp = expected_sprites(romb, Tb, h)
        bad = {s: 0 for s in exp}
        for k in range(12):
            hold_step(h, 10)
            scr = np.asarray(h.em.get_screen())
            for s in exp:
                if not exact(scr, exp[s])[0]:
                    bad[s] += 1
        img = shot(h, out, "S2_wor_lunaris_battle")
        for s, e in exp.items():
            if e["mid"] == LUNARIS:
                x0_, y0_ = e["xy"]
                c = img[y0_:y0_ + e["idx"].shape[0], x0_:x0_ + e["idx"].shape[1]]
                Image.fromarray(c).resize((c.shape[1] * 4, c.shape[0] * 4), Image.NEAREST).save(
                    os.path.join(out, f"S2_lunaris_slot{s}_crop.png"))
        r2 = {"battle": got, "formation": f"{fid:03X}", "monsters": {str(s): f"{e['mid']:03X}" for s, e in exp.items()},
              "magitek_mode": mt, "party": ps, "frames_not_exact_per_slot": {str(s): v for s, v in bad.items()}}
        res["S2"] = r2
        q.check("S2 World of Ruin encounter (Lunaris formation, temp ROM copy with the sector's battle groups pointed at "
                "$CB / $CA): Magitek battle mode off; every monster - the dog included - pixel-exact vs its ROM graphics "
                "at its formation position in all 12 sampled frames",
                got and fid in (0xCA, 0xCB) and any(e["mid"] == LUNARIS for e in exp.values()) and mt == 0
                and not any(bad.values()), r2)
        q.check("N1d WoR entry (dog run): party normalised", normalised(ps), ps)
        h.close()
        os.remove(tmp)
    rep = {"checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "VISUAL_REPORT_v093.json"), "w"), indent=1, default=str)
    print(f"VISUAL v0.9.3 [{EMU}]", "PASS" if rep["all_pass"] else "FAIL",
          f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
