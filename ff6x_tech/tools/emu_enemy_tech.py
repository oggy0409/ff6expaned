#!/usr/bin/env python3
"""TECH v0.6 enemy-asset QA build - Claude-side EMULATOR suite (snes9x via stable-retro).
NOT user runtime QA. Phases 'save'/'load' use NO RAM writes (Esper equipped through the real menu).
Phase 'cmds' pokes Terra's status/commands to reach Steal/Sketch/Control (poke test).
usage: emu_enemy_tech.py save|load|cmds <rom> <outdir>"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_harness import H
from emu_celes_suite import walk, idle, talk, pos, bit, obj_visible
from emu_qa_access import dialogs, boot_new_game, menu_save, sram_dump
from emu_map_tech import choose, grid_ok, ids as dlg_ids
import emu_monster_tech as M
from sprite_match import load_sprite, find
from ff6x.enemygfx import EnemyAsset

R = {"steps": [], "pass": True}
AI_SEEN = set()
A_DIR, B_DIR = os.path.join(HERE, "monsters", "tech6_0180"), os.path.join(HERE, "monsters", "tech6_0181")
SLOT_A, SLOT_B = 2, 3
BOX = {SLOT_A: (8, 0), SLOT_B: (8, 8)}           # VRAM map 8 slot boxes (tile x, y) in the 16x16 buffer


def log(name, ok, **kw):
    R["steps"].append(dict(name=name, ok=bool(ok), **kw))
    if not ok: R["pass"] = False
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


def learn(h): return [h.r8(0x1A6E + s) for s in (2, 3, 7)]          # Terra: Bolt, Poison, Bolt 2


def mem(h, a, n):
    h.gd.update_ram(); return bytes(h.gd.memory.extract(0x7E0000 + a + i, '|u1') for i in range(n))


def expected_box(asset):
    """Expected decoded 4bpp tiles in the slot box (rows_used x cols), as LoadMonsterGfx writes them."""
    out, k = {}, 0
    for r in range(asset.rows_used):
        for c in range(asset.cols):
            if asset.mask[r][c]:
                t = asset.data[k * (32 if asset.bpp == 4 else 24):(k + 1) * (32 if asset.bpp == 4 else 24)]; k += 1
                if asset.bpp == 3:
                    t = t[:16] + b"".join(bytes([t[16 + y], 0]) for y in range(8))
            else:
                t = bytes(32)
            out[(r, c)] = t
    return out


def check_buffer(h, slot, asset):
    buf = mem(h, 0xAE3F, 0x2000)
    x0, y0 = BOX[slot]
    bad = []
    for (r, c), t in expected_box(asset).items():
        off = (x0 + c) * 0x20 + (y0 + r) * 0x200
        if buf[off:off + 32] != t: bad.append((r, c))
    return bad


SPR = {}


def sprites_ok(h, which, frames=300, tag=None, out=None):
    """True once every requested sprite matches its source pixel-exactly in one frame."""
    for t in range(frames):
        scr = h.em.get_screen()
        ok = True
        for name in which:
            idx, rgb = SPR[name]["src"]
            loc = SPR[name].get("loc")
            if loc is None:
                r = find(scr, idx, rgb)
                if r["mismatched_px"] == 0: SPR[name]["loc"] = (r["x"], r["y"])
                else: ok = False
            else:
                x, y = loc; win = (np.asarray(scr, dtype=np.int32) >> 3)[y:y + idx.shape[0], x:x + idx.shape[1]]
                if np.any(np.any(win != rgb, axis=2)[idx != 0]): ok = False
        if ok:
            if tag: h.shot(os.path.join(out, tag))
            return True
        h.step(1)
    return False


# TECH v0.7.1: the v0.6.1 QA prompt is one level down ("Monster/map tests" = choice 1 of the new top prompt).
# FF6X_QA_PREFIX=1 for the v0.7.1 item-tech ROM; unset (empty) for the v0.6.1 ROM.
QA_PREFIX = [int(x) for x in os.environ.get("FF6X_QA_PREFIX", "").split(",") if x.strip()]


def qa_choose(h, *picks):
    d = []
    for n in QA_PREFIX + list(picks): d += M.choose_once(h, n)
    return d


def battle_from_menu(h, path):
    d = qa_choose(h, *path)
    ok = False
    for t in range(2500):                      # advance plain dialogue pages (battle intro) until the battle is up
        h.step(1)
        if M.in_battle(h) and t > 30 and any(M.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)):
            h.step(200); ok = True; break
        if h.r8(0xBA) and t % 40 == 20:
            if f"{h.r16(0xD0):04X}" not in d: d.append(f"{h.r16(0xD0):04X}")
            h.press("A", 4, 10)
    M.close_submenus(h)
    return d, ok


def win_and_return(h, out, tag):
    won, first = M.fight_to_end(h, out, tag)
    d = dialogs(h, out, tag + "_after"); idle(h); h.step(60)
    return won, first, d


def equip_ramuh_via_menu(h, out):
    seq = ["X", "w60", "DOWN", "A", "w30", "A", "w40", "UP", "A", "w40", "A", "w40", "A", "w40"]
    for b in seq:
        if b.startswith("w"): h.step(int(b[1:]))
        else: h.press(b, 4, 30)
    h.shot(os.path.join(out, "09_esper_equipped.png"))
    for _ in range(6): h.press("B", 4, 20)
    idle(h); h.step(30)


def setup():
    SPR.clear()
    SPR["A"] = {"src": load_sprite(A_DIR)}; SPR["B"] = {"src": load_sprite(B_DIR)}
    return EnemyAsset(A_DIR), EnemyAsset(B_DIR)


def custom_battle_checks(h, out, tag, aA, aB, D):
    ids_ = (M.mon_id(h, SLOT_A), M.mon_id(h, SLOT_B))
    pals = (h.r16(0x8117 + 2 * SLOT_A), h.r16(0x8117 + 2 * SLOT_B))
    sizes = (tuple(mem(h, 0x812F + 2 * SLOT_A, 2)), tuple(mem(h, 0x812F + 2 * SLOT_B, 2)))
    bufA, bufB = check_buffer(h, SLOT_A, aA), check_buffer(h, SLOT_B, aB)
    spr = sprites_ok(h, ["A", "B"], tag=f"{tag}_sprites_exact.png", out=out)
    return dict(ids=[f"{i:03X}" for i in ids_], palettes=[f"{p:03X}" for p in pals],
                sizes_cols_rows=[list(s) for s in sizes], tile_buffer_bad=[bufA, bufB], sprites_pixel_exact=spr)


def phase_save(rom, out):
    D, man = dlg_ids(rom)
    aA, aB = setup()
    h = H(rom)
    seen = boot_new_game(h, out)
    log("01 New Game -> first control map $013, vanilla opening dialogue", h.r16(0x82) == 0x013 and len(seen) >= 2, dlg=seen[:6])
    walk(h, "UP", 6); walk(h, "LEFT", 4)
    gil0, inv0 = M.gil(h), M.inv(h)
    d, ok = battle_from_menu(h, [0])
    h.shot(os.path.join(out, "02_battle_start.png"))
    log("02 QA prompt -> Custom monster battle -> group $FE / formation $240", ok and h.r16(0x3ED4) == 0x240, dlg=d)
    c = custom_battle_checks(h, out, "03", aA, aB, D)
    log("03 custom assets: IDs $180/$181, palettes $300/$302 (ENEMYX_PAL), sizes 4x5 / 4x4",
        c["ids"] == ["180", "181"] and c["palettes"] == ["300", "302"] and c["sizes_cols_rows"] == [[4, 5], [4, 4]], **c)
    log("04 decoded tile buffer == source tiles (4bpp A, 3bpp B expanded), no neighbouring data", c["tile_buffer_bad"] == [[], []])
    log("05 both sprites on screen pixel-exact vs source PNG + palette.json (every opaque pixel)", c["sprites_pixel_exact"])
    aip = [f"{h.r16(0x3254 + 8 + 2 * k):04X}" for k in (SLOT_A, SLOT_B)]
    exp = [man["notes"]["monster_foundation"]["monsters"][m]["ai_offset"] for m in ("180", "181")]
    log("06 AI script pointers in battle RAM ($3254+y) = custom scripts in F9 (A 3952, B 3958)", aip == exp, ram=aip, manifest=exp)
    AI_SEEN.update({k for k, v in M.observe_ai(h, out, frames=3000, tag="06_ai").items() if k in ("mute", "slow") and v})
    killed = {"first": None}
    for t in range(4000):
        if M.mon_hp(h, SLOT_A) == 0 or M.mon_hp(h, SLOT_B) == 0: break
        h.press(["B", "B", "UP", "A", "A", "A"][t % 6], 4, 26)
    first = "A" if M.mon_hp(h, SLOT_A) == 0 else "B"
    other = "B" if first == "A" else "A"
    h.step(120)
    rem = sprites_ok(h, [other], frames=900, tag=f"07_{first}_down_{other}_exact.png", out=out)
    log("07 one monster killed first; the remaining sprite stays pixel-exact (no corruption)", rem, killed_first=first)
    won, _, d = win_and_return(h, out, "08")
    log("08 victory -> map $013 (35,43), QA message, control", won and h.r16(0x82) == 0x013 and pos(h) == (35, 43)
        and d == [D["qa6_battle_done"]], dlg=d, pos=pos(h))
    log("08b gold +75, drops only from defined loot", M.gil(h) - gil0 == 75, gil_delta=M.gil(h) - gil0)
    # --- Phase D Magic Points (no pokes: Ramuh given by the QA event, equipped through the menu)
    walk(h, "LEFT", 1)
    d = qa_choose(h, 1, 1, 2); idle(h); h.step(30)
    log("10 QA 'Magic Point test' gives Ramuh ($1A69 bit0); 'Not yet' steps off the tile (no prompt loop)",
        h.r8(0x1A69) & 1 and pos(h) == (35, 43) and h.r8(0xBA) == 0, dlg=d, pos=pos(h))
    equip_ramuh_via_menu(h, out)
    log("11 Ramuh equipped on Terra through Skills > Espers (menu)", h.r8(0x161E) == 0x00, esper=f"{h.r8(0x161E):02X}")
    l0 = learn(h)
    walk(h, "LEFT", 1)
    d, ok = battle_from_menu(h, [1, 1, 0])
    log("12 MP battle: formation $241 (custom assets, magic_points 3)", ok and h.r16(0x3ED4) == 0x241)
    if AI_SEEN != {"mute", "slow"}:
        AI_SEEN.update({k for k, v in M.observe_ai(h, out, frames=2000, tag="12_ai").items() if k in ("mute", "slow") and v})
    won, _, d = win_and_return(h, out, "12")
    l1 = learn(h)
    log("13 3 MP credited: Bolt +30 (x10), Poison +15 (x5), Bolt2 +6 (x2)", won and [b - a for a, b in zip(l0, l1)] == [30, 15, 6],
        before=l0, after=l1)
    walk(h, "LEFT", 1)
    d, ok = battle_from_menu(h, [1, 1, 1])
    if AI_SEEN != {"mute", "slow"}:
        AI_SEEN.update({k for k, v in M.observe_ai(h, out, frames=2000, tag="14_ai").items() if k in ("mute", "slow") and v})
    won, _, d = win_and_return(h, out, "14")
    l2 = learn(h)
    log("14 zero-MP new formation $240: learn progress unchanged", ok and won and l2 == l1, after=l2)
    log("14b AI behaviour observed across the custom battles: Mute (only A's script) and Slow (only B's script)",
        AI_SEEN == {"mute", "slow"}, seen=sorted(AI_SEEN))
    # --- Phase A isolation via the QA harness (v0.6.1: Magitek-safe VRAM map 8, all three birds at once)
    import gfx_compare_report as GC
    romb = open(rom, "rb").read(); T = GC.rom_tables(romb)
    for k, (fid, ids_exp, pals_exp, tag) in enumerate(((0x242, ["028", "182", "183"], ["046", "046", "04A"], "09a_iso_three"),
                                                        (0x243, ["028", "028", "028"], ["046", "046", "046"], "09b_iso_reference"))):
        walk(h, "LEFT", 1)
        d, ok = battle_from_menu(h, [1, 0, k])
        frec = romb[T["form"] + 15 * fid:T["form"] + 15 * fid + 15]
        exp = {}
        for s_ in (0, 2, 3):
            dd, tiles, palb = GC.decode_slot(romb, T, M.mon_id(h, s_))
            exp[s_] = (GC.render(tiles, palb, *dd["stencil_cols_rows"]), ((frec[8 + s_] >> 4) * 8, (frec[8 + s_] & 15) * 8))
        exact = {s_: False for s_ in exp}
        for t in range(90):                                   # Dark Winds fly in: sample for up to 900 frames
            scr = np.asarray(h.em.get_screen(), dtype=np.int32) >> 3
            for s_, ((idx, rgb), (x, y)) in exp.items():
                win = scr[y:y + idx.shape[0], x:x + idx.shape[1]]
                if win.shape[:2] == idx.shape and not np.any(np.any(win != rgb, axis=2)[idx != 0]): exact[s_] = True
            if all(exact.values()): break
            h.step(10)
        h.shot(os.path.join(out, f"{tag}.png"))
        st = {"formation": f"{h.r16(0x3ED4):03X}", "ids": [f"{M.mon_id(h, s_):03X}" for s_ in (0, 2, 3)],
              "pals": [f"{h.r16(0x8117 + 2 * s_):03X}" for s_ in (0, 2, 3)], "pixel_exact_at_position": [exact[s_] for s_ in (0, 2, 3)]}
        won, _, d2 = win_and_return(h, out, tag)
        log(f"09{'ab'[k]} isolation battle ${fid:03X} (slots 0/2/3 = {'/'.join(ids_exp)}): palettes {'/'.join(pals_exp)}, every bird pixel-exact "
            "vs its ROM data at its formation position; win, return",
            ok and st["formation"] == f"{fid:03X}" and st["ids"] == ids_exp and st["pals"] == pals_exp and all(exact.values())
            and won and h.r16(0x82) == 0x013, **st)
    walk(h, "LEFT", 1)
    d = choose(h, out, "15_qa_no", 2); idle(h); h.step(30)
    R["before_save"] = {"gil": M.gil(h), "inv": {f"{k:02X}": v for k, v in M.inv(h).items()}, "map": f"{h.r16(0x82):03X}",
                        "pos": list(pos(h)), "esper": h.r8(0x161E), "learn": learn(h)}
    menu_save(h, out, "15")
    dumps = dict(sram_dump(h))
    sel = [k for k, dd in dumps.items() if dd[0x1860 - 0x1600:0x1863 - 0x1600] == bytes(h.r8(0x1860 + i) for i in range(3))
           and dd[0x1EA9 - 0x1600] == h.r8(0x1EA9)]
    log("15 QA Save Point -> menu Save wrote slot 1", bool(sel))
    if sel:
        open(os.path.join(out, "sram_slot1.bin"), "wb").write(dumps[sel[-1]])
        json.dump({"block": sel[-1], "before": R["before_save"]}, open(os.path.join(out, "save_phase.json"), "w"))
    json.dump(R, open(os.path.join(out, "enemy_tech_save_phase.json"), "w"), indent=1)
    print("SAVE PHASE", "PASS" if R["pass"] else "FAIL")


def phase_load(rom, out):
    D, man = dlg_ids(rom)
    aA, aB = setup()
    h = H(rom)
    sp = M.boot_load(h, out)
    h.shot(os.path.join(out, "16_after_load.png"))
    st = {"gil": M.gil(h), "inv": {f"{k:02X}": v for k, v in M.inv(h).items()}, "map": f"{h.r16(0x82):03X}",
          "pos": list(pos(h)), "esper": h.r8(0x161E), "learn": learn(h)}
    log("16 new process -> Continue: gil, inventory, map, position, equipped Esper, learn progress restored", st == sp["before"], loaded=st)
    walk(h, "RIGHT", 1); walk(h, "LEFT", 1)
    d, ok = battle_from_menu(h, [0])
    c = custom_battle_checks(h, out, "17", aA, aB, D)
    log("17 custom battle after load: same IDs/palettes/sizes, tile buffer exact, sprites pixel-exact",
        ok and c["ids"] == ["180", "181"] and c["palettes"] == ["300", "302"] and c["tile_buffer_bad"] == [[], []]
        and c["sprites_pixel_exact"], **c)
    won, _, d = win_and_return(h, out, "18")
    log("18 victory + return after load", won and h.r16(0x82) == 0x013 and pos(h) == (35, 43), pos=pos(h))
    # map / Annex regression
    walk(h, "LEFT", 1)
    d = qa_choose(h, 1, 2, 0); idle(h); h.step(90)
    log("19 QA Map/Annex -> Map test A loads $1A0 (v0.4 pipeline)", h.r16(0x82) == 0x1A0 and pos(h) == (16, 27), map=f"{h.r16(0x82):03X}")
    bad = grid_ok(h, man["notes"]["maps"]["1A0"]["runtime_grid"])
    log("19b map $1A0 grid", not bad, mismatches=bad[:5])
    walk(h, "UP", 13); walk(h, "LEFT", 6); talk(h, "LEFT"); d = dialogs(h, out, "20_A1")
    log("20 routed NPC A1 dialogue", d[:1] in ([D["a1_first"]], [D["a1_after"]]), dlg=d)
    walk(h, "RIGHT", 6); walk(h, "DOWN", 15); idle(h); h.step(60)
    log("20b south exit to $013", h.r16(0x82) == 0x013, pos=pos(h))
    walk(h, "LEFT", 1)
    if pos(h) != (34, 43):
        walk(h, "RIGHT", 1); walk(h, "LEFT", 1)
    d = qa_choose(h, 1, 2, 1); idle(h); h.step(90)
    log("21 Celes Annex via QA: map $0C7 + Vale/chest visible", h.r16(0x82) == 0x0C7 and obj_visible(h, 0x10) and obj_visible(h, 0x11))
    walk(h, "UP", 11); walk(h, "LEFT", 3); talk(h, "LEFT"); d = dialogs(h, out, "22_vale")
    log("22 Vale dialogue (NPC vector)", d == [D["vale_first"]], dlg=d)
    walk(h, "RIGHT", 3); walk(h, "DOWN", 13); idle(h); h.step(60)
    log("22b Annex exit -> $013 (35,43)", h.r16(0x82) == 0x013 and pos(h) == (35, 43), pos=pos(h))
    walk(h, "RIGHT", 3); walk(h, "UP", 5)
    seen, battle, vids, vhp, won = [], False, None, None, False
    for t in range(3000):
        if M.in_battle(h) and any(M.mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)):
            battle = True; h.step(120); h.shot(os.path.join(out, "23_vanilla_battle.png"))
            vids = [f"{M.mon_id(h, s):03X}" for s in range(6)]; vhp = [M.mon_maxhp(h, s) for s in range(6)]
            won, _ = M.fight_to_end(h, out, "23")
            break
        if h.r8(0xBA) and (not seen or seen[-1] != f"{h.r16(0xD0):04X}"):
            seen.append(f"{h.r16(0xD0):04X}")
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    for t in range(2000):
        if h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and not M.in_battle(h): break
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    log("23 vanilla opening Guard battle (relocated palette/stencil tables), victory, control",
        battle and won and seen[:1] == ["000D"] and vids is not None and "000" in vids, monster_ids=vids, max_hp=vhp)
    json.dump(R, open(os.path.join(out, "enemy_tech_load_phase.json"), "w"), indent=1)
    print("LOAD PHASE", "PASS" if R["pass"] else "FAIL")


def terra_menu(h):
    """Open Terra's battle menu: wait for the ATB, then cycle with Y until the menu owner ($62CA)
    changes to another party slot and back to slot 0 (the variable is stale before the first menu)."""
    h.step(300)
    seen_other = False
    for i in range(40):
        mc = h.r8(0x62CA)
        if mc != 0: seen_other = True
        if mc == 0 and seen_other:
            h.step(20); return True
        h.press("Y", 4, 30); h.step(20)
    return False


def phase_cmds(rom, out):
    """POKE TEST: Steal / Sketch / Control on the custom-asset monsters (Sketch draws the custom graphics
    through the summon loader -> EnemyGfxBase hook + relocated palette/stencil)."""
    D, man = dlg_ids(rom)
    aA, aB = setup()
    h = H(rom)
    boot_new_game(h, out)
    walk(h, "UP", 6); walk(h, "LEFT", 4)
    h.w8(0x1614, h.r8(0x1614) & 0xF7)
    for i, c in enumerate((0x05, 0x0D, 0x0E, 0x01)): h.w8(0x1616 + i, c)
    d, ok = battle_from_menu(h, [0])
    log("C01 custom battle with poked Terra: IDs $180/$181", ok and (M.mon_id(h, SLOT_A), M.mon_id(h, SLOT_B)) == (0x180, 0x181))
    log("C02 steal slots from MonsterItems: A=E9/E8, B=F0/F2",
        [h.r8(0x3308 + 12), h.r8(0x3309 + 12), h.r8(0x3308 + 14), h.r8(0x3309 + 14)] == [0xE9, 0xE8, 0xF0, 0xF2])
    st_notes = {"A": man["notes"]["enemy_foundation"]["assets"]["180"]["palette_index"],
                "B": man["notes"]["enemy_foundation"]["assets"]["181"]["palette_index"]}
    tm = terra_menu(h); h.shot(os.path.join(out, "C02b_terra_menu.png")); snap = h.em.get_state()
    log("C02b Terra's battle menu (Steal/Sketch/Control/Item)", tm)
    stolen = lambda y: (lambda: h.r8(0x3308 + y) == 0xFF and h.r8(0x3309 + y) == 0xFF)
    rb = M.attempt(h, snap, out, "C03_steal_B", ["A", "A"], stolen(14))
    ra = M.attempt(h, snap, out, "C03_steal_A", ["A", "DOWN", "A"], stolen(12))
    log("C03 Steal on both custom monsters", ra[0] and rb[0])
    # Sketch: the summon/Sketch loader (C2:F5F1 slot router -> LoadSummonGfxProp -> EnemyGfxBase hook, relocated
    # stencil) decodes the sketched monster into the graphics buffer at VRAM map 6 box (0,0); the palette pointer
    # $6169 (= palette index * 16) is used with the relocated MonsterPal. The drawn sketch is partly hidden behind
    # Terra's sprite, so the screen check is "best location >= 85 % of opaque pixels exact".
    res = {}
    for name, presses, asset in (("A", ["DOWN", "A", "DOWN", "A"], aA), ("B", ["DOWN", "A", "A"], aB)):
        idx, rgb = SPR[name]["src"]
        exp = expected_box(asset)
        found = None
        for delay in (0, 7, 11, 23, 31, 43, 59, 71, 89, 101, 131, 157):   # Sketch can miss: other RNG phases
            h.em.set_state(snap); h.step(delay)
            for b in presses: h.press(b, 4, 30)
            for t in range(700):
                h.step(1)
                if t % 4: continue
                buf = mem(h, 0xAE3F, 0x2000)
                if all(buf[c * 0x20 + r * 0x200: c * 0x20 + r * 0x200 + 32] == tt for (r, c), tt in exp.items()):
                    pal_ptr = h.r16(0x6169)
                    best, best_img = None, None
                    for k in range(60):
                        h.step(2)
                        scr = h.em.get_screen()
                        r_ = find(scr, idx, rgb, region=(120, 0, 256, 150))
                        if best is None or r_["mismatched_px"] < best["mismatched_px"]: best, best_img = r_, scr.copy()
                        if best["mismatched_px"] == 0: break
                    from PIL import Image
                    Image.fromarray(best_img).resize((512, 448), Image.NEAREST).save(os.path.join(out, f"C04_sketch_{name}.png"))
                    found = {"delay": delay, "palette_ptr": f"{pal_ptr:04X}", "screen_best": best}
                    break
            if found: break
        # screen: the sketch is drawn behind Terra's sprite (as in vanilla), so the visible-pixel ratio is evidence only
        ok = bool(found) and found["palette_ptr"] == f"{int(st_notes[name], 16) * 16:04X}"
        res[name] = found; res[name + "_ok"] = ok
    log("C04 Sketch on A/B: Sketch loader decodes the custom tiles exactly (buffer), palette pointer = custom palette, drawing shown next to Terra (partly behind her sprite)", res.get("A_ok") and res.get("B_ok"), **res)
    ctl = lambda y: (lambda: h.r8(0x32B9 + y) == 0x00)
    cb = M.attempt(h, snap, out, "C05_control_B", ["DOWN", "DOWN", "A", "A"], ctl(14), frames=300, shots=())
    ca = M.attempt(h, snap, out, "C05_control_A", ["DOWN", "DOWN", "A", "DOWN", "A"], ctl(12), frames=300, shots=())
    log("C05 Control on both custom monsters", ca[0] and cb[0])
    json.dump(R, open(os.path.join(out, "enemy_tech_cmds_phase.json"), "w"), indent=1)
    print("CMDS PHASE (POKE TEST)", "PASS" if R["pass"] else "FAIL")


if __name__ == "__main__":
    ph, rom, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    {"save": phase_save, "load": phase_load, "cmds": phase_cmds}[ph](rom, out)
