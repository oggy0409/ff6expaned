#!/usr/bin/env python3
"""TECH v0.5 monster-tech QA build - Claude-side EMULATOR suite (snes9x via stable-retro).
NOT user runtime QA. Phase 'save' / 'load' use no RAM writes. Phase 'cmds' pokes Terra's
status/commands ONLY to reach the Steal/Sketch/Control code paths (impossible in the
opening Magitek sequence) - documented as a poke test.

usage: emu_monster_tech.py save|load|cmds <rom> <outdir>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_harness import H
from emu_celes_suite import walk, idle, talk, pos, bit, item_count, obj_visible
from emu_qa_access import dialogs, boot_new_game, menu_save, sram_dump
from emu_map_tech import choose, grid_ok, ids as dlg_ids

R = {"steps": [], "pass": True}
SLOT_A, SLOT_B = 2, 3


def log(name, ok, **kw):
    R["steps"].append(dict(name=name, ok=bool(ok), **kw))
    if not ok: R["pass"] = False
    print(("PASS " if ok else "FAIL ") + name, kw if kw else "", flush=True)


def gil(h): return h.r8(0x1860) | h.r8(0x1861) << 8 | h.r8(0x1862) << 16
def in_battle(h): return h.r16(0x3BF4) != 0xFFFF
def mon_id(h, slot): return h.r16(0x2001 + 2 * slot)
def mon_hp(h, slot): return h.r16(0x3BF4 + 8 + 2 * slot)
def mon_maxhp(h, slot): return h.r16(0x3C1C + 8 + 2 * slot)
def inv(h): return {h.r8(0x1869 + i): h.r8(0x1969 + i) for i in range(256) if h.r8(0x1869 + i) != 0xFF}


def wait_battle(h, n=1500):
    for t in range(n):
        h.step(1)
        if in_battle(h) and t > 30 and mon_maxhp(h, SLOT_A) not in (0, 0xFFFF):
            h.step(200); return True
    return False


def close_submenus(h):
    """Config is Wait mode ($1D4D bit3): ATB stops while a battle sub-menu (e.g. an empty Magic
    list) is open. Inputs buffered during the battle transition can leave one open, so B twice."""
    h.press("B", 4, 16); h.press("B", 4, 16)


def observe_ai(h, out, frames=4000, tag="ai"):
    """Party idles (no input) - monsters act on their own. Bounded and safe: stops as soon as
    both AI-specific effects were seen, or any party member drops below 25 HP.
    TESTMOB A's script is the only source of Mute ($1B, status2 bit3 = $0800 in $3EE4),
    TESTMOB B's script is the only source of Slow ($19, status3 bit2 = $04 in $3EF8)."""
    mute = slow = False
    minhp = 9999
    close_submenus(h)
    for t in range(frames):
        h.step(1)
        if not mute and any(h.r16(0x3EE4 + 2 * k) & 0x0800 for k in range(3)):
            mute = True; h.shot(os.path.join(out, f"{tag}_mute_from_A.png"))
        if not slow and any(h.r8(0x3EF8 + 2 * k) & 0x04 for k in range(3)):
            slow = True; h.shot(os.path.join(out, f"{tag}_slow_from_B.png"))
        hp = [h.r16(0x3BF4 + 2 * k) for k in range(3)]
        minhp = min(minhp, *hp)
        if (mute and slow) or not in_battle(h) or minhp < 25:
            break
    return {"mute": mute, "slow": slow, "frames": t + 1, "min_party_hp": minhp}


def fight_to_end(h, out, tag, max_cycles=120):
    """Menu driver (Wait mode). One cycle: B,B (close any sub-menu, e.g. the empty opening Item
    list), UP until the command cursor ($2C, observed: 0 = MagiTek row) is on MagiTek, then
    A,A,A (MagiTek -> Fire Beam -> target). Slow presses: the battle menu drops inputs that
    arrive during window transitions. After both monsters are down, A advances the victory text."""
    killed_first = None
    def chk():
        nonlocal killed_first
        if in_battle(h) and killed_first is None:
            ha, hb = mon_hp(h, SLOT_A), mon_hp(h, SLOT_B)
            if ha == 0 and hb != 0: killed_first = "A"; h.shot(os.path.join(out, f"{tag}_A_down_B_alive.png"))
            elif hb == 0 and ha != 0: killed_first = "B"; h.shot(os.path.join(out, f"{tag}_B_down_A_alive.png"))
        return not in_battle(h) and h.r16(0x82) != 0xFFFF
    for c in range(max_cycles):
        alive = in_battle(h) and any(mon_hp(h, k) not in (0, 0xFFFF) for k in range(6))
        if alive:
            seq = ["B", "B"]
            for b in seq: h.press(b, 4, 26)
            for _ in range(3):
                if h.r8(0x2C) == 0: break
                h.press("UP", 4, 26)
            seq = ["A", "A", "A"]
        else:
            seq = ["A"]
        for b in seq:
            h.press(b, 4, 26)
            if chk(): return True, killed_first
        for _ in range(4):
            h.step(15)
            if chk(): return True, killed_first
    return False, killed_first


def choose_once(h, n_down, max_frames=1500):
    """Answer exactly one choice dialogue (no auto-advance of the following dialogue)."""
    for t in range(max_frames):
        h.step(1)
        if h.r8(0xBA):
            h.step(150); d0 = h.r16(0xD0)
            for _ in range(n_down): h.press("DOWN", 4, 10)
            h.press("A", 4, 20)
            for t2 in range(200):
                h.step(1)
                if h.r16(0xD0) != d0: break
            return [f"{d0:04X}"]
    return []


def start_qa_battle(h, out, tag, D):
    d = choose(h, out, tag + "_prompt", 0, max_frames=1500)
    ok = wait_battle(h)
    return d, ok


def phase_save(rom, out):
    D, man = dlg_ids(rom)
    h = H(rom)
    seen = boot_new_game(h, out)
    log("01 New Game -> first control map $013, vanilla opening dialogue", h.r16(0x82) == 0x013 and len(seen) >= 2, dlg=seen[:6])
    walk(h, "UP", 6); walk(h, "LEFT", 4)
    inv0, gil0 = inv(h), gil(h)
    d, ok = start_qa_battle(h, out, "02_qa", D)
    h.shot(os.path.join(out, "03_battle_start.png"))
    ids_ = (mon_id(h, SLOT_A), mon_id(h, SLOT_B))
    log("02 QA prompt -> Monster test battle -> event group $FE / formation $240 starts", ok and d[:2] == [D["qa5_prompt"], D["qa5_battle_intro"]],
        dlg=d)
    log("03 both new monster IDs loaded in the same formation (slots 2/3 = $180/$181)", ids_ == (0x180, 0x181),
        ids=[f"{i:03X}" for i in ids_])
    st = {"A_maxhp": mon_maxhp(h, SLOT_A), "B_maxhp": mon_maxhp(h, SLOT_B)}
    log("04 stats from relocated table: max HP A=90, B=140", st == {"A_maxhp": 90, "B_maxhp": 140}, **st)
    pal = [h.r8(0x8123 + k) for k in range(6)]
    R["btlgfx_palette_slots"] = pal
    ai = observe_ai(h, out, tag="05_ai")
    log("05 custom AI from expansion space: Mute (only in A's script) and Slow (only in B's script) land on the party; party safe",
        ai["mute"] and ai["slow"] and ai["min_party_hp"] >= 25, **ai)
    ok, first = fight_to_end(h, out, "06")
    d = dialogs(h, out, "07_after_battle"); idle(h); h.step(60)
    inv1, gil1 = inv(h), gil(h)
    gained = {f"{k:02X}": inv1.get(k, 0) - inv0.get(k, 0) for k in set(inv1) | set(inv0) if inv1.get(k, 0) != inv0.get(k, 0)}
    log("06 targeting/victory: one monster died first, battle ended, field resumed", ok and first in ("A", "B"), killed_first=first)
    log("07 battle return: map $013, QA message, party stepped to (35,43), control", h.r16(0x82) == 0x013 and pos(h) == (35, 43)
        and d == [D["qa5_battle_done"]], dlg=d, pos=pos(h))
    exp_items = {"F3", "F2", "E9", "E8"}
    log("08 gold +75 (30+45 from new stat records); drops only from the defined loot items", gil1 - gil0 == 75
        and set(gained) <= exp_items and sum(gained.values()) == 2, gil_delta=gil1 - gil0, items_gained=gained)
    walk(h, "LEFT", 1)
    d = choose(h, out, "09_qa_no", 2); idle(h); h.step(30)
    log("09 QA tile -> No (Save Point): Save allowed", bit(h, 0x1BF) and bit(h, 0x1B5), dlg=d)
    R["before_save"] = {"gil": gil(h), "inv": {f"{k:02X}": v for k, v in inv(h).items()}, "map": f"{h.r16(0x82):03X}", "pos": list(pos(h))}
    menu_save(h, out, "10")
    dumps = dict(sram_dump(h))
    sel = [k for k, dd in dumps.items() if dd[0x1860 - 0x1600:0x1863 - 0x1600] == bytes(h.r8(0x1860 + i) for i in range(3))
           and dd[0x1EA9 - 0x1600] == h.r8(0x1EA9)]
    log("10 menu Save wrote slot 1", bool(sel))
    if sel:
        open(os.path.join(out, "sram_slot1.bin"), "wb").write(dumps[sel[-1]])
        json.dump({"block": sel[-1], "before": R["before_save"]}, open(os.path.join(out, "save_phase.json"), "w"))
    json.dump(R, open(os.path.join(out, "monster_tech_save_phase.json"), "w"), indent=1)
    print("SAVE PHASE", "PASS" if R["pass"] else "FAIL")


def boot_load(h, out):
    sram = open(os.path.join(out, "sram_slot1.bin"), "rb").read()
    sp = json.load(open(os.path.join(out, "save_phase.json")))
    for i, v in enumerate(sram): h.gd.memory.assign(sp["block"] + i, "|u1", v)
    for t in range(1400):
        if t % 30 == 0 and t > 300: h.press("A" if t > 900 else "START", 4, 4)
        else: h.step(1)
        if h.r16(0x82) and h.evpc() == 0xCA0000 and t > 1000: break
    for t in range(1500):
        h.step(1)
        if t % 40 == 0: h.press("A", 4, 4)
        if h.r16(0x82) == 0x013 and h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and gil(h) == sp["before"]["gil"]: break
    h.step(120)
    return sp


def phase_load(rom, out):
    D, man = dlg_ids(rom)
    h = H(rom)
    sp = boot_load(h, out)
    h.shot(os.path.join(out, "11_after_load.png"))
    st = {"gil": gil(h), "inv": {f"{k:02X}": v for k, v in inv(h).items()}, "map": f"{h.r16(0x82):03X}", "pos": list(pos(h))}
    log("11 new process -> Continue slot 1: gil, inventory, map, position restored", st == sp["before"], loaded=st)
    walk(h, "RIGHT", 1); walk(h, "LEFT", 1)
    gil0 = gil(h)
    d, ok = start_qa_battle(h, out, "12_qa", D)
    log("12 re-enter QA battle after load: IDs $180/$181 again, HP 90/140", ok and (mon_id(h, SLOT_A), mon_id(h, SLOT_B)) == (0x180, 0x181)
        and (mon_maxhp(h, SLOT_A), mon_maxhp(h, SLOT_B)) == (90, 140))
    h.shot(os.path.join(out, "12_battle_again.png"))
    ok, first = fight_to_end(h, out, "13")
    d = dialogs(h, out, "13_after"); idle(h); h.step(60)
    log("13 second victory + return after load, gold +75", ok and h.r16(0x82) == 0x013 and gil(h) - gil0 == 75, gil_delta=gil(h) - gil0)
    # map / Annex regression via QA 'other tests'
    walk(h, "LEFT", 1)
    d = choose_once(h, 1)
    d2 = choose(h, out, "14_qa_mapA", 0); idle(h); h.step(90)
    log("14 QA 'Map/Annex tests' -> Map test A loads $1A0 (v0.4 pipeline)", h.r16(0x82) == 0x1A0 and pos(h) == (16, 27),
        map=f"{h.r16(0x82):03X}", dlg=d + d2)
    bad = grid_ok(h, man["notes"]["maps"]["1A0"]["runtime_grid"])
    log("14b map $1A0 grid", not bad, mismatches=bad[:5])
    walk(h, "UP", 13); walk(h, "LEFT", 6); talk(h, "LEFT"); d = dialogs(h, out, "15_A1")
    log("15 routed NPC A1 dialogue on v0.5 build", d[:1] in ([D["a1_first"]], [D["a1_after"]]), dlg=d)
    walk(h, "RIGHT", 6); walk(h, "DOWN", 15); idle(h); h.step(60)
    log("15b south exit to $013", h.r16(0x82) == 0x013, pos=pos(h))
    walk(h, "LEFT", 1)
    if pos(h) != (34, 43):
        walk(h, "RIGHT", 1); walk(h, "LEFT", 1)
    d = choose(h, out, "16_qa_other", 1)
    for t in range(300):
        h.step(1)
        if h.r8(0xBA): break
    d2 = choose(h, out, "16_qa_annex", 1); idle(h); h.step(90)
    log("16 Celes Annex via QA on v0.5 build: map $0C7 + Vale/chest visible", h.r16(0x82) == 0x0C7 and obj_visible(h, 0x10)
        and obj_visible(h, 0x11), map=f"{h.r16(0x82):03X}")
    walk(h, "UP", 11); walk(h, "LEFT", 3); talk(h, "LEFT"); d = dialogs(h, out, "17_vale")
    log("17 Vale dialogue (NPC vector) on v0.5 build", d == [D["vale_first"]], dlg=d)
    walk(h, "RIGHT", 3); walk(h, "DOWN", 13); idle(h); h.step(60)
    log("17b Annex exit -> $013 (35,43)", h.r16(0x82) == 0x013 and pos(h) == (35, 43), pos=pos(h))
    # vanilla opening battle regression (relocated monster + formation tables)
    walk(h, "RIGHT", 3); walk(h, "UP", 5)
    seen, battle, vids, vhp, won = [], False, None, None, False
    for t in range(3000):
        if in_battle(h) and any(mon_maxhp(h, k) not in (0, 0xFFFF) for k in range(6)):
            battle = True; h.step(120); h.shot(os.path.join(out, "18_vanilla_battle.png"))
            vids = [f"{mon_id(h, s):03X}" for s in range(6)]; vhp = [mon_maxhp(h, s) for s in range(6)]
            won, _ = fight_to_end(h, out, "18")
            break
        if h.r8(0xBA) and (not seen or seen[-1] != f"{h.r16(0xD0):04X}"):
            seen.append(f"{h.r16(0xD0):04X}")
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    for t in range(2000):
        if h.evpc() == 0xCA0000 and h.r8(0xBA) == 0 and not in_battle(h): break
        h.step(4, ("A",)) if t % 8 < 4 else h.step(4)
    idle(h); h.step(60)
    log("18 vanilla opening battle: Guard IDs/HP from relocated tables, victory, field control", battle and won and seen[:1] == ["000D"]
        and vids is not None and "000" in vids, monster_ids=vids, max_hp=vhp, dlg=seen[:4])
    json.dump(R, open(os.path.join(out, "monster_tech_load_phase.json"), "w"), indent=1)
    print("LOAD PHASE", "PASS" if R["pass"] else "FAIL")


# ---------------------------------------------------------------------------------------------
# phase 'cmds': POKE TEST. The opening Magitek party has no Steal/Sketch/Control, so Terra's
# status1 Magitek bit ($1614 bit3) is cleared and her commands ($1616-$1619) are set to
# Steal/Sketch/Control/Item right before the QA battle. Everything else is the normal QA path.
# Retries reuse an emulator snapshot with a different number of idle frames (RNG) - deterministic.
Y_OF = {SLOT_A: 12, SLOT_B: 14}


def menu_char(h): return h.r8(0x62CA)          # observed: party slot whose battle menu is open


def terra_menu(h):
    for i in range(40):
        if menu_char(h) == 0:
            h.step(20); return True
        h.press("Y", 4, 30); h.step(20)
    return False


def attempt(h, snap, out, tag, presses, ok_fn, frames=420, shots=(60, 100, 140, 200)):
    for delay in (0, 7, 11, 23, 31, 43, 59, 71):
        h.em.set_state(snap); h.step(delay)
        for b in presses: h.press(b, 4, 30)
        for t in range(frames):
            h.step(1)
            if t in shots: h.shot(os.path.join(out, f"{tag}_d{delay}_{t:03d}.png"))
            if ok_fn(): 
                h.step(30); h.shot(os.path.join(out, f"{tag}_result.png"))
                return True, delay
    return False, None


def phase_cmds(rom, out):
    D, man = dlg_ids(rom)
    h = H(rom)
    boot_new_game(h, out)
    walk(h, "UP", 6); walk(h, "LEFT", 4)
    h.w8(0x1614, h.r8(0x1614) & 0xF7)                       # POKE: Terra not Magitek
    for i, c in enumerate((0x05, 0x0D, 0x0E, 0x01)):         # POKE: Steal, Sketch, Control, Item
        h.w8(0x1616 + i, c)
    d, ok = start_qa_battle(h, out, "c01_qa", D)
    close_submenus(h)
    log("C01 QA battle with poked Terra: IDs $180/$181", ok and (mon_id(h, SLOT_A), mon_id(h, SLOT_B)) == (0x180, 0x181))
    st = {f"{k}": [f"{h.r8(0x3308 + Y_OF[s] + i):02X}" for i in range(2)] for k, s in (("A", SLOT_A), ("B", SLOT_B))}
    log("C02 battle steal slots loaded from relocated MonsterItems: A=E9/E8, B=F0/F2", st == {"A": ["E9", "E8"], "B": ["F0", "F2"]}, **st)
    tm = terra_menu(h)
    h.shot(os.path.join(out, "c03_terra_menu.png"))
    log("C03 Terra's battle menu shows Steal/Sketch/Control/Item", tm, menu_char=menu_char(h))
    snap = h.em.get_state()
    stolen = lambda s: (lambda: h.r8(0x3308 + Y_OF[s]) == 0xFF and h.r8(0x3309 + Y_OF[s]) == 0xFF)
    r = {}
    r["steal_B"] = attempt(h, snap, out, "c04_steal_B", ["A", "A"], stolen(SLOT_B))
    r["steal_A"] = attempt(h, snap, out, "c04_steal_A", ["A", "DOWN", "A"], stolen(SLOT_A))
    log("C04 Steal works on both new monsters (steal slots consumed, 'Stole ...' message)", r["steal_A"][0] and r["steal_B"][0],
        steal_A_delay=r["steal_A"][1], steal_B_delay=r["steal_B"][1])
    any_mute = lambda: any(h.r8(0x3EE5 + y) & 0x08 for y in (12, 14))
    any_slow = lambda: any(h.r8(0x3EF8 + y) & 0x04 for y in (12, 14))
    r["sketch_A"] = attempt(h, snap, out, "c05_sketch_A", ["DOWN", "A", "DOWN", "A"], any_mute, frames=600)
    r["sketch_B"] = attempt(h, snap, out, "c05_sketch_B", ["DOWN", "A", "A"], any_slow, frames=600)
    log("C05 Sketch works on both new monsters: A's sketch casts Mute, B's sketch casts Slow (MonsterSketch + gfx-slot hook)",
        r["sketch_A"][0] and r["sketch_B"][0], sketch_A_delay=r["sketch_A"][1], sketch_B_delay=r["sketch_B"][1])
    ctl = lambda s: (lambda: h.r8(0x32B9 + Y_OF[s]) == 0x00)   # observed: controller party slot
    r["control_B"] = attempt(h, snap, out, "c06_control_B", ["DOWN", "DOWN", "A", "A"], ctl(SLOT_B), frames=300, shots=())
    if r["control_B"][0]:
        terra_menu(h); h.shot(os.path.join(out, "c06_control_B_menu.png"))
    r["control_A"] = attempt(h, snap, out, "c06_control_A", ["DOWN", "DOWN", "A", "DOWN", "A"], ctl(SLOT_A), frames=300, shots=())
    if r["control_A"][0]:
        terra_menu(h); h.shot(os.path.join(out, "c06_control_A_menu.png"))
    log("C06 Control works on both new monsters (menu: A = Battle/Mute, B = Battle/Slow - see c06_*_menu.png)",
        r["control_A"][0] and r["control_B"][0], control_A_delay=r["control_A"][1], control_B_delay=r["control_B"][1])
    json.dump(R, open(os.path.join(out, "monster_tech_cmds_phase.json"), "w"), indent=1)
    print("CMDS PHASE (POKE TEST)", "PASS" if R["pass"] else "FAIL")


if __name__ == "__main__":
    ph, rom, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    {"save": phase_save, "load": phase_load, "cmds": phase_cmds}[ph](rom, out)
