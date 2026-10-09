#!/usr/bin/env python3
"""TECH v0.7.1 emulator QA suite (stable-retro / snes9x). Drives the real game through the event engine and
the real menus, asserting WRAM/SRAM after every step; screenshots go to <out>/.

usage: emu_item_qa.py <qa.sfc> <production.sfc> <clean_rev1.sfc> <out>
writes <out>/ITEM_QA_EMULATOR_REPORT.json
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_item_tech import T, ev_give, ev_take, ev_has, XBITS, XSIG
from emu_menu_nav import Nav, ST

SIG = bytes([0x58, 0x49, 0x01, 0xFE])
QA_IDS = (0x13D, 0x13E, 0x13F)


class Report:
    def __init__(self, out):
        self.out, self.checks, self.n = out, [], 0
        os.makedirs(out, exist_ok=True)

    def check(self, name, ok, detail=None):
        self.checks.append({"check": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name, "" if detail is None else json.dumps(detail, default=str)[:300])
        return ok

    def shot(self, h, tag):
        self.n += 1
        p = f"{self.n:03d}_{tag}.png"
        h.shot(os.path.join(self.out, p))
        return p


def boot_new_game(h):
    idle = 0
    for t in range(60000):
        if t % 20 == 0: h.press('START' if t < 400 else 'A', 4, 4)
        else: h.step(1)
        if t % 10 == 0:
            idle = idle + 1 if h.evpc() == 0xCA0000 else 0
            if idle >= 30: break
    h.step(120)


def inv16(h):
    return sorted((i, q) for s, i, q in h.inv())


def ext_slots(h):
    return [(s, i, q) for s, i, q in h.inv() if i >= 0x100]


def bits_consistent(h):
    """every inventory bit is on a non-empty slot holding a defined QA id; every equip bit on a non-$FF slot"""
    bad = []
    for s in range(256):
        if h.bit(s) and (h.r8(0x1869 + s) == 0xFF or (0x100 | h.r8(0x1869 + s)) not in QA_IDS):
            bad.append(("inv", s))
    for rec in range(16):
        for k in range(6):
            n = 256 + rec * 6 + k
            if h.bit(n) and h.r8(0x161F + rec * 37 + k) == 0xFF:
                bad.append(("eq", rec, k))
    return bad


def sram_blocks(h):
    h.gd.update_ram()
    return [k for k, v in h.gd.memory.blocks.items() if k != 0x7E0000 and len(v) == 0x2000]


def dump_sram(h):
    k = sram_blocks(h)[-1]
    return k, bytes(h.gd.memory.extract(k + i, "|u1") for i in range(0x2000))


def write_sram(h, k, data):
    for i, v in enumerate(data):
        h.gd.memory.assign(k + i, "|u1", v)


def slot_checksum(slot):
    return sum(slot[:0x9FE]) & 0xFFFF


def continue_slot1(h, frames=3000):
    """title -> Continue -> slot 1 -> confirm; returns when the field has control"""
    for t in range(frames):
        if t % 30 == 0 and t > 300:
            h.press("A" if t > 900 else "START", 4, 4)
        else:
            h.step(1)
        if t > 1200 and h.evpc() == 0xCA0000 and h.r8(0x26) == 0 and h.r16(0x1F64) & 0x1FF:
            break
    for _ in range(300):
        h.step(1)


def stats_block(h):
    g = h.r8
    return {"vigor": g(0x11A6), "speed": g(0x11A4), "stamina": g(0x11A2), "magpwr": g(0x11A0),
            "batpwr": g(0x11AC) + g(0x11AD), "defense": g(0x11BA), "mdef": g(0x11BB), "evade": g(0x11A8),
            "mblock": g(0x11AA)}


def equip_slot(nv, h, slot, list_index):
    """equip menu (state EQUIP_SLOT): pick `slot` (0-3) then list entry `list_index`"""
    nv.cursor_to(slot)
    nv.press("A", "EQUIP_LIST")
    nv.cursor_to(list_index)
    nv.press("A", "EQUIP_SLOT")


def main(rom, prod, clean, out):
    q = Report(out)
    h = T(rom)
    boot_new_game(h)
    q.check("A0 New Game writes the extension signature", h.rbytes(XSIG, 4) == SIG, h.rbytes(XSIG, 4).hex())
    q.check("A0 New Game: extended metadata zero", h.rbytes(XBITS, 44) == bytes(44))
    open(os.path.join(out, "newgame.state"), "wb").write(h.em.get_state())

    # ---------------------------------------------------------------- A: receive
    h.run_event(ev_give(0x13D) + ev_give(0x13E) + ev_give(0x13F) + [0x80, 0x3D, 0x80, 0xE9])
    ext = ext_slots(h)
    q.check("A1 GIVE_EXT_ITEM x3: three extended slots", sorted(i for _, i, _ in ext) == list(QA_IDS),
            [(s, f"{i:03X}", n) for s, i, n in ext])
    q.check("M0 vanilla Chocobo Brsh ($3D) kept separate from $13D",
            [(f"{i:03X}", n) for s, i, n in h.inv() if (i & 0xFF) == 0x3D] in ([("13D", 1), ("03D", 1)], [("03D", 1), ("13D", 1)]))
    st_items = h.em.get_state()
    open(os.path.join(out, "field_items.state"), "wb").write(st_items)

    # ---------------------------------------------------------------- B: names / descriptions / details
    nv = Nav(h)
    nv.open_main()
    nv.main_to("Item")
    nv.wait(ST["ITEM"])
    q.shot(h, "B_item_list")
    for k, i in enumerate(QA_IDS):
        nv.cursor_to(k)
        h.step(20)
        q.shot(h, f"B_item_desc_{i:03X}")
        h.press("A", 4, 20); h.press("A", 4, 60)          # A twice on the same slot -> item details
        q.shot(h, f"B_item_details_{i:03X}")
        h.press("B", 4, 40)
        nv.wait(ST["ITEM"])
    nv.back_to_main()

    # ---------------------------------------------------------------- C/D/E: equip three extended items
    nv.main_to("Equip")
    nv.press("A", "EQUIP_OPT")
    base = stats_block(h)
    nv.press("A", "EQUIP_SLOT")
    h.press("A", 4, 30); nv.wait(ST["EQUIP_LIST"]); q.shot(h, "C_rhand_list_preview")
    preview = stats_block(h)
    h.press("B", 4, 30); nv.wait(ST["EQUIP_SLOT"])
    equip_slot(nv, h, 0, 0)
    equip_slot(nv, h, 3, 0)
    q.shot(h, "C_equipped_blade_mail")
    nv.back_to_main()
    nv.main_to("Relic")
    nv.press("A", "RELIC_OPT")
    nv.press("A", "RELIC_SLOT")
    nv.cursor_to(0)
    nv.press("A", "RELIC_LIST")
    nv.cursor_to(0)
    h.press("A", 4, 30); h.step(60)
    q.shot(h, "C_relic_equipped")
    eq = h.eq(0)
    q.check("D1 three extended items equipped simultaneously (Terra: R-hand $13D, body $13E, relic1 $13F)",
            eq[0] == 0x13D and eq[3] == 0x13E and eq[4] == 0x13F, [f"{x:03X}" for x in eq])
    q.check("D2 equipped extended items left the inventory", not ext_slots(h), ext_slots(h))
    q.check("D3 bit field consistent", not bits_consistent(h), bits_consistent(h))
    nv.back_to_main()
    nv.main_to("Equip")
    nv.press("A", "EQUIP_OPT")
    after = stats_block(h)
    q.shot(h, "E_equip_screen_all_three")
    exp = {"vigor": base["vigor"] + 7, "stamina": base["stamina"] + 5, "speed": base["speed"] + 7,
           "magpwr": base["magpwr"] + 7, "evade": base["evade"] + 30, "mblock": base["mblock"] + 30}
    got = {k: after[k] for k in exp}
    q.check("E1 stat changes = QA definitions (Vig+7 blade, Sta+5 mail, Spd+7 Mag+7 Eva/MBlk+30 charm)", got == exp,
            {"base": base, "after": after, "expected": exp})
    q.check("E2 battle power uses the extended weapon (222)", after["batpwr"] - base["batpwr"] == 222 - 30,
            {"base_batpwr": base["batpwr"], "after_batpwr": after["batpwr"], "mithril_knife": 30})
    q.check("E3 equip-list stat preview shows the extended weapon (Vig +7, power +192)",
            preview["vigor"] == base["vigor"] + 7 and preview["batpwr"] == base["batpwr"] + 192,
            {"base": base, "preview": preview})
    three_state = h.em.get_state()
    open(os.path.join(out, "three_equipped.state"), "wb").write(three_state)

    # ---------------------------------------------------------------- remove / empty / optimum
    nv.cursor_lr(2)
    nv.press("A", "EQUIP_REMOVE")
    nv.cursor_to(0)
    h.press("A", 4, 40)
    q.check("D4 Remove R-hand: $13D back to the inventory, slot $FF",
            h.eq(0)[0] == 0xFF and [i for _, i, _ in ext_slots(h)] == [0x13D], ext_slots(h))
    h.press("B", 4, 30); nv.wait(ST["EQUIP_OPT"])
    nv.cursor_lr(3)
    h.press("A", 4, 60)
    q.check("D5 Empty: armor $13E back, relic untouched", h.eq(0)[3] == 0xFF and h.eq(0)[4] == 0x13F and
            sorted(i for _, i, _ in ext_slots(h)) == [0x13D, 0x13E], [(s, f"{i:03X}", n) for s, i, n in ext_slots(h)])
    q.check("D5 Empty: bit field consistent", not bits_consistent(h), bits_consistent(h))
    nv.cursor_lr(1)
    h.press("A", 4, 60)
    eq = h.eq(0)
    q.check("I1 Optimum picks the extended weapon and armor", eq[0] == 0x13D and eq[3] == 0x13E,
            [f"{x:03X}" for x in eq])
    q.check("I2 Optimum: no duplication (each QA item exactly once overall)",
            sorted([i for _, i, _ in ext_slots(h)] + [x for x in h.eq(0) if x >= 0x100]) == list(QA_IDS))
    q.shot(h, "I_optimum")
    nv.cursor_lr(3)
    h.press("A", 4, 60)                         # Empty again
    nv.back_to_main()
    nv.main_to("Relic")
    nv.press("A", "RELIC_OPT")
    nv.cursor_lr(1)
    nv.press("A", "RELIC_REMOVE")
    nv.cursor_to(0)
    h.press("A", 4, 40)
    q.check("D6 Relic remove: $13F back to the inventory",
            h.eq(0)[4] == 0xFF and sorted(i for _, i, _ in ext_slots(h)) == list(QA_IDS))
    nv.back_to_main()

    # ---------------------------------------------------------------- H: arrange / move
    before = inv16(h)
    nv.main_to("Item")
    nv.wait(ST["ITEM"])
    h.press("B", 4, 20)                        # item list -> USE/ARRANGE/RARE row
    if not nv.wait(ST["ITEM_OPT"]):
        raise RuntimeError("item options row not reached")
    nv.cursor_lr(1)
    h.press("A", 4, 90)
    nv.wait(ST["ITEM"])
    q.shot(h, "H_arrange")
    q.check("H1 Arrange keeps every item (9-bit ids and quantities)", inv16(h) == before,
            {"before": [(f"{i:03X}", n) for i, n in before], "after": [(f"{i:03X}", n) for i, n in inv16(h)]})
    q.check("H2 Arrange: bit field consistent", not bits_consistent(h), bits_consistent(h))
    order = [(s, f"{i:03X}") for s, i, n in h.inv()]
    exp_order = ["0E9", "001", "13D", "03D", "05A", "069", "084", "13E", "13F"]
    q.check("H3 Arrange order follows ItemIconTbl (consumable, dirk, sword, brush, shield, helmet, armor, armor, relic)",
            [i for _, i in order] == exp_order, order)
    if nv.state() == ST["ITEM_OPT"]:            # Arrange leaves the cursor on the USE/ARRANGE/RARE row
        nv.cursor_lr(0)
        nv.press("A", "ITEM")
    s0 = {s: i for s, i, n in h.inv()}
    nv.cursor_to(2)
    nv.press("A", "ITEM_MOVE")                  # pick slot 2 ($13D) for move
    nv.cursor_to(3)
    nv.press("A", "ITEM")                       # drop on slot 3 ($03D) -> swap
    h.step(20)
    s1 = {s: i for s, i, n in h.inv()}
    q.check("H4 item move/swap carries the high bits ($13D <-> $03D)", inv16(h) == before and not bits_consistent(h)
            and (s1[2], s1[3]) == (s0[3], s0[2]) == (0x03D, 0x13D),
            {"before": {k: f"{v:03X}" for k, v in s0.items()}, "after": {k: f"{v:03X}" for k, v in s1.items()}})
    q.shot(h, "H_after_swap")
    nv.back_to_main()
    nv.close()
    h.step(60)

    # ---------------------------------------------------------------- M: shop / colosseum
    inv_before = inv16(h)
    h.call_event(0xCB7552, frames=60)           # vanilla script "9B 48 FE": shop $48 sells DaVinci Brsh ($3E = alias of QA Mail $13E)
    nv.wait(ST["SHOP_OPT"], 600)
    q.shot(h, "M_shop_options")
    h.press("A", 4, 40)                         # BUY
    h.step(30)
    q.shot(h, "M_shop_buy_davinci_owned")
    owned = [h.r8(0x7E9DC9 - 0x7E0000 + k) for k in range(8)]
    q.check("M1 shop owned count: DaVinci Brsh ($3E) = 0 although QA Mail $13E is owned", owned[0] == 0, owned)
    h.press("B", 4, 30); nv.wait(ST["SHOP_OPT"])
    nv.cursor_lr(1)
    h.press("A", 4, 40)
    nv.wait(ST["SHOP_SELL"])
    q.shot(h, "M_shop_sell_list")
    ext_s = [s for s, i, n in ext_slots(h)]
    nv.cursor_to(ext_s[0])
    h.press("A", 4, 40)
    q.check("M2 an extended slot cannot be selected for Sell", nv.state() == ST["SHOP_SELL"] and inv16(h) == inv_before,
            {"state": f"{nv.state():02X}"})
    for _ in range(6):
        h.press("B", 4, 30)
    for _ in range(1500):
        h.step(1)
        if h.evpc() == 0xCA0000 and h.r16(0xE8) == 0: break
    h.step(60)
    q.check("M3 shop left the inventory unchanged", inv16(h) == inv_before)
    for _ in range(3000):
        if h.idle():
            break
        h.step(1)
    if not h.idle():
        q.shot(h, "M_not_idle_after_shop")
        print("not idle after shop:", f"{h.evpc():06X}", h.r16(0xE8), f"{nv.state():02X}")
    h.run_event([0x9A], frames=60)
    nv.wait(ST["COLO_ITEM"], 600)
    q.shot(h, "M_colosseum_list")
    ext_s = [s for s, i, n in ext_slots(h)]
    nv.cursor_to(ext_s[0])
    h.press("A", 4, 40)
    q.check("M4 an extended slot cannot be wagered", nv.state() == ST["COLO_ITEM"], f"{nv.state():02X}")
    for _ in range(3):
        h.press("B", 4, 30)
    for _ in range(1500):
        h.step(1)
        if h.evpc() == 0xCA0000 and h.r16(0xE8) == 0: break
    h.step(60)
    q.check("M5 colosseum left the inventory unchanged, nothing wagered", inv16(h) == inv_before and h.r8(0x0205) == 0xFF,
            {"0205": f"{h.r8(0x0205):02X}"})

    # ---------------------------------------------------------------- J: save -> power cycle -> load
    h.em.set_state(three_state)
    nv = Nav(h)
    nv.back_to_main()
    nv.close()
    h.step(60)
    h.run_event(ev_give(0x13D) + ev_give(0x13F))   # extended items in the inventory AND equipped
    pre = {"inv": inv16(h), "eq": h.eq(0), "bits": h.rbytes(XBITS, 44).hex()}
    q.check("J- pre-save state: extended items equipped and in the inventory",
            [i for i, n in pre["inv"] if i >= 0x100] == [0x13D, 0x13F] and pre["eq"][0] == 0x13D)
    h.w8(0x1EB7, h.r8(0x1EB7) | 0x80)           # "on a save point" (test only)
    nv.open_main()
    nv.main_to("Save")
    nv.wait(ST["SAVE_SELECT"], 400)
    h.press("A", 4, 60)
    h.press("A", 4, 200)
    q.shot(h, "J_saved")
    blk, sram = dump_sram(h)
    open(os.path.join(out, "sram_qa_save.bin"), "wb").write(sram)
    slot = sram[0:0xA00]
    q.check("J0 saved slot carries the signature and bits", slot[0x1D24 - 0x1600:0x1D28 - 0x1600] == SIG and
            slot[0x1CF8 - 0x1600:0x1D24 - 0x1600].hex() == pre["bits"])
    h.close()
    h2 = T(rom)
    write_sram(h2, blk, sram)
    continue_slot1(h2)
    q.shot(h2, "J_after_power_cycle_load")
    post = {"inv": inv16(h2), "eq": h2.eq(0), "bits": h2.rbytes(XBITS, 44).hex()}
    q.check("J1 save -> power cycle -> load preserves extended inventory, equipment and bits", post == pre,
            {"pre": str(pre)[:200], "post": str(post)[:200]})
    h2.close()

    # ---------------------------------------------------------------- L: legacy / garbage saves
    def load_with(romfile, slotbytes, tag):
        s = bytearray(sram)
        s[0:0xA00] = slotbytes
        c = slot_checksum(s[0:0xA00])
        s[0x9FE], s[0x9FF] = c & 0xFF, c >> 8
        hh = T(romfile)
        write_sram(hh, blk, bytes(s))
        continue_slot1(hh)
        q.shot(hh, tag)
        return hh

    legacy = bytearray(slot)
    for i in range(0x1CF8 - 0x1600, 0x1D28 - 0x1600):
        legacy[i] = (0xA5 + 37 * i) & 0xFF             # deterministic non-zero garbage, no signature
    hl = load_with(rom, legacy, "L_garbage_no_signature")
    q.check("L1 garbage + no signature: ZERO extended items/equipment, signature written",
            not [1 for s, i, n in hl.inv() if i >= 0x100] and all(x < 0x100 for x in hl.eq(0)) and
            hl.rbytes(XSIG, 4) == SIG and hl.rbytes(XBITS, 44) == bytes(44))
    q.check("L2 vanilla bytes of the legacy save preserved", all(
        hl.r8(0x1600 + i) == legacy[i] for i in range(0x9FE) if not (0x1CF8 - 0x1600 <= i < 0x1D28 - 0x1600)
        and not (0x0000 <= i < 0x0250) and i not in range(0x1EA0 - 0x1600, 0x1FFF - 0x1600)),
        "character records / volatile event area excluded (changed by gameplay after load)")
    hl.close()
    # genuine vanilla Rev 1 save
    hv = T(clean)
    boot_new_game(hv)
    hv.run_event([0x80, 0x3D, 0x80, 0x3E, 0x80, 0x3F, 0x80, 0xE9])
    hv.w8(0x1EB7, hv.r8(0x1EB7) | 0x80)
    nvv = Nav(hv)
    nvv.open_main(); nvv.main_to("Save"); nvv.wait(ST["SAVE_SELECT"], 400)
    hv.press("A", 4, 60); hv.press("A", 4, 200)
    vblk, vsram = dump_sram(hv)
    open(os.path.join(out, "sram_vanilla_save.bin"), "wb").write(vsram)
    vinv = sorted((hv.r8(0x1869 + s), hv.r8(0x1969 + s)) for s in range(256) if hv.r8(0x1869 + s) != 0xFF)
    hv.close()
    q.check("L3 vanilla save holds the Bushido-name bytes at $1CF8 (legacy layout)",
            vsram[0x1D24 - 0x1600:0x1D28 - 0x1600] != SIG, vsram[0x1CF8 - 0x1600:0x1D28 - 0x1600].hex())
    hq = T(rom)
    write_sram(hq, vblk, vsram)
    continue_slot1(hq)
    q.shot(hq, "L_vanilla_save_in_v071")
    q.check("L4 vanilla Rev 1 save in v0.7.1: zero phantom extended items, brushes stay vanilla",
            not [1 for s, i, n in hq.inv() if i >= 0x100] and inv16(hq) == vinv and hq.rbytes(XSIG, 4) == SIG,
            {"inv": [(f"{i:03X}", n) for i, n in inv16(hq)]})
    hq.close()

    # ---------------------------------------------------------------- QA save in the production ROM
    hp = T(prod)
    write_sram(hp, blk, sram)
    continue_slot1(hp)
    q.check("P1 QA save in the production ROM: undefined QA ids removed, never truncated to $3D-$3F",
            inv16(hp) == [x for x in pre["inv"] if x[0] < 0x100] and
            hp.eq(0)[0] == 0xFF and hp.eq(0)[3] == 0xFF and hp.eq(0)[4] == 0xFF and hp.rbytes(XBITS, 44) == bytes(44),
            {"inv": [(f"{i:03X}", n) for i, n in inv16(hp)], "eq": [f"{x:03X}" for x in hp.eq(0)]})

    rep = {"rom": os.path.basename(rom), "production": os.path.basename(prod), "checks": q.checks,
           "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "ITEM_QA_EMULATOR_REPORT.json"), "w"), indent=1)
    print("ITEM QA EMULATOR", "PASS" if rep["all_pass"] else "FAIL",
          f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:5])
