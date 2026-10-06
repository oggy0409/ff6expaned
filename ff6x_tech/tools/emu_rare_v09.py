#!/usr/bin/env python3
"""TECH v0.9 emulator checks, part 3: FF6X rare / key items (stable-retro / snes9x).

  R0 tables: XRareName / XRareDescPtr / XRareDescText for the 52 logical rare ids (0-19 byte copies of the vanilla
     names / descriptions, 20-24 the locked key items, 25-51 QA fillers in the QA ROM only), XRareDef
  R1 New Game: rare block zero + valid signature
  R2 event API GIVE_RARE / HAS_RARE / TAKE_RARE ($69 / $6E / $6D) for every one of the 32 FF6X ids (QA ROM) and the
     20 vanilla ids (= vanilla event bits $1D0-$1E3); undefined ids ignored; vanilla bits outside $1D0-$1E3 untouched
  R3 QA menus: grant all 5 / remove all 5 / toggle each / HAS check (Triune Sigil)
  R4 Rare Items menu (real menus): the 5 key items listed with their names and descriptions; 52 owned -> 3 pages
     (20 / 20 / 12); Down on the last row / Up on the first row / R / L turn the page; count = 52
  R5 save -> power cycle -> Continue: rare items preserved
  R6 legacy Rev 1 save with garbage in $1E1D-$1E22: no phantom rare item; v0.8 save (item bank signature, no rare
     block): no phantom; a corrupted rare block (signature mismatch) is cleared
  R7 production ROM: only the 5 locked ids (20-24) are defined, 25-51 ignored; the QA save's fillers are dropped
     on load, the 5 key items kept

usage: emu_rare_v09.py <qa.sfc> <qa.manifest.json> <production.sfc> <clean_rev1.sfc> <out>
writes <out>/RARE_ITEM_REPORT.json
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, dump_sram, write_sram, continue_slot1
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
from emu_equip_stress_v08 import save_menu
from patches import item_v071 as IV, item_v09 as I9

PROD = json.load(open(os.path.join(HERE, "items/production_v09/rare_items.json")))["rare_items"]
QA = json.load(open(os.path.join(HERE, "items/qa_v09/qa_rare_items.json")))["rare_items"]
XRARE, XRSIG = 0x1E1D, 0x1E21
SW = 0x152                                       # QA_V09_HAS_RARE


def pc(a):
    return a - 0xC00000


def ev_grare(i): return [0x69, i]
def ev_trare(i): return [0x6D, i]
def ev_hrare(i, sw): return [0x6E, i, sw & 0xFF, sw >> 8]


def owned(h):
    out = [k for k in range(20) if h.r8(0x1E80 + ((0x1D0 + k) >> 3)) >> ((0x1D0 + k) & 7) & 1]
    out += [20 + k for k in range(32) if h.r8(XRARE + (k >> 3)) >> (k & 7) & 1]
    return out


def ff6x(h):
    return [i for i in owned(h) if i >= 20]


def has(h, i):
    h.w8(0x1E80 + (SW >> 3), h.r8(0x1E80 + (SW >> 3)) & ~(1 << (SW & 7)))
    h.run_event(ev_hrare(i, SW))
    return h.r8(0x1E80 + (SW >> 3)) >> (SW & 7) & 1


def sig_ok(h):
    r = [h.r8(XRARE + k) for k in range(4)]
    return h.r8(XRSIG) == 0x52 and h.r8(XRSIG + 1) == (r[0] ^ r[1] ^ r[2] ^ r[3] ^ 0xA5)


def menu(h, L, picks):
    h.call_event(L["QaAccess6"], frames=1)
    return talk(h, picks)


def open_rare(h):
    nv = Nav(h)
    for _ in range(6):
        h.step(60); nv.open_main()
        if nv.state() == ST["MAIN"]:
            break
    nv.main_to("Item"); nv.wait(ST["ITEM"]); h.step(20)
    h.press("B", 4, 20); nv.wait(ST["ITEM_OPT"]); h.step(20)
    for _ in range(2):
        h.press("RIGHT", 4, 16)
    h.press("A", 4, 60); h.step(40)
    return nv


def page_list(h):
    return [h.r8(0x9D89 + k) for k in range(20) if h.r8(0x9D89 + k) != 0xFF]


def main(qa, manifest, prod, clean, out):
    q = Report(out)
    L = labels(manifest)
    rom = open(qa, "rb").read()
    prom = open(prod, "rb").read()
    van = open(clean, "rb").read()
    res = {}
    # ------------------------------------------------------------------ R0 tables
    def name(r, j):
        return r[pc(I9.T_RNAME) + 13 * j:pc(I9.T_RNAME) + 13 * j + 13]

    def desc(r, j):
        p = r[pc(I9.T_RDPTR) + 2 * j] | r[pc(I9.T_RDPTR) + 2 * j + 1] << 8
        a = pc(0xFA0000 | p); d = bytearray()
        while r[a] != 0:
            d.append(r[a]); a += 1
        return bytes(d)
    vptr = [van[pc(I9.VAN_RDPTR) + 2 * j] | van[pc(I9.VAN_RDPTR) + 2 * j + 1] << 8 for j in range(20)]

    def vdesc(j):
        a = pc(I9.VAN_RDTXT) + vptr[j]; d = bytearray()
        while van[a] != 0:
            d.append(van[a]); a += 1
        return bytes(d)
    t_van = all(name(rom, j) == van[pc(I9.VAN_RNAME) + 13 * j:pc(I9.VAN_RNAME) + 13 * j + 13] and desc(rom, j) == vdesc(j)
                for j in range(20))
    t_ff6x = all(name(rom, r["rare_id"]).rstrip(b"\xFF") == IV.menu_encode(r["display_name"], 0xFE) and
                 desc(rom, r["rare_id"]) == IV.menu_encode(r["desc"], 0xFF) for r in PROD + QA)
    q.check("R0a 52 rare names / descriptions: ids 0-19 byte copies of the vanilla rare items, 20-24 the locked key "
            "items, 25-51 the QA fillers", t_van and t_ff6x)
    q.check("R0b XRareDef: QA ROM defines FF6X ids 20-51 (32 = capacity), production only 20-24 (the 5 locked key "
            "items; no QA filler in production)",
            rom[pc(I9.T_RDEF):pc(I9.T_RDEF) + 4] == b"\xFF\xFF\xFF\xFF" and
            prom[pc(I9.T_RDEF):pc(I9.T_RDEF) + 4] == b"\x1F\x00\x00\x00" and
            all(prom[pc(I9.T_RNAME) + 13 * j:pc(I9.T_RNAME) + 13 * j + 13] == b"\xFF" * 13 for j in range(25, 52)))
    # ------------------------------------------------------------------ R1
    h = T(qa)
    boot_new_game(h)
    st_new = h.em.get_state()
    van0 = [i for i in owned(h) if i < 20]
    q.check("R1 New Game: rare block XRARE = 0 with a valid signature, no FF6X rare item owned (vanilla: the opening "
            "gives Terra's Pendant, rare id 19)", h.rbytes(XRARE, 4) == bytes(4) and sig_ok(h) and ff6x(h) == [] and
            van0 == [19], {"block": h.rbytes(XRARE, 6).hex(), "vanilla_owned": van0})
    # ------------------------------------------------------------------ R2 event API
    ev0 = h.rbytes(0x1E80, 0x80)
    bad = []
    h.run_event(ev_trare(19))                                    # start from nothing owned (restored below)
    for i in range(52):
        h0 = has(h, i)
        h.run_event(ev_grare(i)); h1 = has(h, i); o1 = i in owned(h)
        h.run_event(ev_trare(i)); h2 = has(h, i); o2 = i in owned(h)
        if not (h0 == 0 and h1 == 1 and o1 and h2 == 0 and not o2 and sig_ok(h)):
            bad.append((i, h0, h1, o1, h2, o2))
    ev1 = h.rbytes(0x1E80, 0x80)
    other = [k for k in range(0x400) if k != SW and not 0x1D0 <= k <= 0x1E3 and (ev0[k >> 3] ^ ev1[k >> 3]) >> (k & 7) & 1]
    q.check("R2a GIVE_RARE / HAS_RARE / TAKE_RARE for all 52 logical ids (32 FF6X ids 20-51 + vanilla 0-19): owned "
            "after GIVE, HAS = 1, not owned after TAKE, HAS = 0, rare-block signature valid", not bad, bad)
    q.check("R2b no event bit outside the vanilla rare-item bits $1D0-$1E3 (and the QA result switch) changed",
            not other, other[:10])
    h.run_event(ev_grare(52) + ev_grare(200) + ev_trare(60))
    q.check("R2c ids >= 52 are ignored (no WRAM change)", owned(h) == [] and sig_ok(h))
    h.run_event(ev_grare(3))
    q.check("R2d GIVE_RARE 3 = the vanilla 'Fish' bit $1D3 (vanilla rare item)",
            h.r8(0x1E80 + (0x1D3 >> 3)) >> (0x1D3 & 7) & 1 == 1 and owned(h) == [3])
    h.run_event(ev_trare(3) + ev_grare(19))
    h.run_event(ev_grare(20) + ev_grare(20))
    a = 20 in owned(h)
    h.run_event(ev_trare(20))
    q.check("R2e key items are one-time states (no count): GIVE twice -> owned, one TAKE -> not owned",
            a and 20 not in owned(h) and sig_ok(h))
    # ------------------------------------------------------------------ R3 QA menus
    h.em.set_state(st_new); h.step(10)
    menu(h, L, [1, 0])
    q.check("R3a QA 'Grant all 5 key items': rare ids 20-24 owned", ff6x(h) == [20, 21, 22, 23, 24], owned(h))
    menu(h, L, [1, 2, 1])
    q.check("R3b QA 'Check Triune Sigil' (HAS_RARE 23 -> switch)", h.r8(0x1E80 + (SW >> 3)) >> (SW & 7) & 1 == 1)
    st_keys = h.em.get_state()
    menu(h, L, [1, 1])
    q.check("R3c QA 'Remove all 5'", ff6x(h) == [] and 19 in owned(h), owned(h))
    tog = {}
    for k, path in enumerate(([1, 2, 0, 0], [1, 2, 0, 1], [1, 2, 0, 2, 0], [1, 2, 0, 2, 1], [1, 2, 0, 2, 2])):
        menu(h, L, path); a = 20 + k in owned(h)
        menu(h, L, path); b = 20 + k in owned(h)
        tog[20 + k] = (a, b)
    q.check("R3d QA 'Toggle' each key item: given when not owned, removed when owned",
            all(v == (True, False) for v in tog.values()), tog)
    # ------------------------------------------------------------------ R4 menu
    h.em.set_state(st_keys); h.step(10)
    nv = open_rare(h)
    q.shot(h, "R4_rare_5_keys")
    p0 = page_list(h)
    q.check("R4a Rare Items menu with the 5 key items: list = Pendant (vanilla 19) + rare ids 20-24, item count 6",
            p0 == [19, 20, 21, 22, 23, 24] and h.r8(0x64) == 6, {"list": p0, "count": h.r8(0x64)})
    descs = {}
    for k in range(5):
        e = k + 1                                                 # list entry (entry 0 = Pendant)
        for _ in range(12):
            if h.r8(0x4E) >= e // 2:
                break
            h.press("DOWN", 4, 16)
        for _ in range(4):
            if h.r8(0x4D) == e % 2:
                break
            h.press("RIGHT" if h.r8(0x4D) < e % 2 else "LEFT", 4, 16)
        h.step(90)
        q.shot(h, f"R4_desc_{20 + k}")
        descs[20 + k] = h.r8(0x9D89 + h.r8(0x4B))
    q.check("R4a' cursor on each key item selects its rare id for the description (LoadBigText index)",
            descs == {20 + k: 20 + k for k in range(5)}, descs)
    nv.back_to_main(); nv.close(); h.step(30)
    menu(h, L, [1, 2, 2, 0])                                      # fill all 52
    q.check("R4b QA 'Fill all 52': 20 vanilla + 32 FF6X rare ids owned", owned(h) == list(range(52)), len(owned(h)))
    st_full = h.em.get_state()
    nv = open_rare(h)
    pages = {0: page_list(h)}
    cnt = h.r8(0x64)
    q.shot(h, "R4_page0")
    for _ in range(9):
        h.press("DOWN", 4, 12)
    h.press("DOWN", 4, 30); h.step(30)
    pages["down"] = (h.r8(0x1E3D), page_list(h), h.r8(0x4E))
    q.shot(h, "R4_page1_down")
    h.press("R", 4, 30); h.step(90)
    pages["R"] = (h.r8(0x1E3D), page_list(h))
    q.shot(h, "R4_page2_R")
    h.press("R", 4, 30); h.step(30)
    pages["R_last"] = h.r8(0x1E3D)
    h.press("L", 4, 30); h.step(30)
    pages["L"] = h.r8(0x1E3D)
    for _ in range(9):
        if h.r8(0x4E) == 0:
            break
        h.press("UP", 4, 12)
    h.press("UP", 4, 30); h.step(30)
    pages["up"] = (h.r8(0x1E3D), h.r8(0x4E))
    nv.back_to_main(); nv.close(); h.step(30)
    res["pages"] = pages
    q.check("R4c 52 rare items: count 52; page 0 = ids 0-19, Down on row 10 -> page 1 (ids 20-39, cursor on row 1), "
            "R -> page 2 (ids 40-51), R on the last page stays, L -> page 1, Up on row 1 -> page 0 (cursor on row 10)",
            cnt == 52 and pages[0] == list(range(20)) and pages["down"] == (1, list(range(20, 40)), 0) and
            pages["R"] == (2, list(range(40, 52))) and pages["R_last"] == 2 and pages["L"] == 1 and pages["up"] == (0, 9),
            {k: v for k, v in pages.items()})
    # ------------------------------------------------------------------ R5 save / load
    h.em.set_state(st_full); h.step(10)
    blk, sram = save_menu(h)
    h.close()
    h2 = T(qa); write_sram(h2, blk, sram); continue_slot1(h2)
    q.check("R5 save -> power cycle -> Continue: all 52 rare items (incl. the 32 FF6X ids) preserved, signature valid",
            owned(h2) == list(range(52)) and sig_ok(h2), len(owned(h2)))
    h2.close()
    # ------------------------------------------------------------------ R7 production
    hp = T(prod); write_sram(hp, blk, sram); continue_slot1(hp)
    po = owned(hp)
    q.check("R7a the QA save in the PRODUCTION ROM: the 20 vanilla and 5 locked key items kept, the 27 QA fillers "
            "(undefined in production) dropped on load", po == list(range(25)) and sig_ok(hp), po)
    hp.run_event(ev_grare(30) + ev_grare(51))
    q.check("R7b production: GIVE_RARE of an undefined FF6X id (30, 51) is ignored", owned(hp) == list(range(25)))
    hp.close()
    # ------------------------------------------------------------------ R6 legacy / v0.8 saves
    hv = T(clean); boot_new_game(hv)
    for k in range(6):
        hv.w8(XRARE + k, [0xFF, 0x13, 0x00, 0x80, 0x52, 0x7C][k])  # POKE: garbage in the (vanilla-unused) bytes
    vblk, vsram = save_menu(hv)
    hv.close()
    hq = T(qa); write_sram(hq, vblk, vsram); continue_slot1(hq)
    q.check("R6a legacy Rev 1 save with garbage in $1E1D-$1E22: no phantom rare item (rare block cleared, signed)",
            ff6x(hq) == [] and sig_ok(hq), {"block": hq.rbytes(XRARE, 6).hex()})
    hq.close()
    h8 = T(os.path.join(os.path.dirname(qa), "FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc"))
    boot_new_game(h8)
    for k in range(6):
        h8.w8(XRARE + k, [0x1F, 0x00, 0x00, 0x00, 0x00, 0x00][k])  # POKE: key-item bits without a valid signature
    b8, s8 = save_menu(h8)
    h8.close()
    hq = T(qa); write_sram(hq, b8, s8); continue_slot1(hq)
    q.check("R6b v0.8 save (item bank signature, rare bytes never written by v0.8, here POKEd without a valid rare "
            "signature): no phantom rare item", ff6x(hq) == [] and sig_ok(hq), {"block": hq.rbytes(XRARE, 6).hex()})
    hq.close()
    rep = {"rom": os.path.basename(qa), "checks": q.checks, "results": res, "all_pass": all(c["pass"] for c in q.checks)}
    json.dump(rep, open(os.path.join(out, "RARE_ITEM_REPORT.json"), "w"), indent=1, default=str)
    print("RARE ITEMS", "PASS" if rep["all_pass"] else "FAIL", f"{sum(c['pass'] for c in q.checks)}/{len(q.checks)}")


if __name__ == "__main__":
    main(*sys.argv[1:6])
