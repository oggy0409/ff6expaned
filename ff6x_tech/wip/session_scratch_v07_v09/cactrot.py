import sys, os
sys.path.insert(0, "/home/user/ff6expaned/ff6x_tech/tools")
from emu_colosseum import *
from emu_item_qa import Report
S = os.path.dirname(os.path.abspath(__file__))
q = Report(S + "/cact")
for rom, ext in [("/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc", False), (S + "/f072a/FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.sfc", True)]:
    h = T(rom); h.ext_aware = ext; boot_new_game(h)
    h.run_event([0x80, 0xEE, 0x80, 0xEE, 0x80, 0xEE, 0x80, 0xF0, 0x80, 0xF0, 0x80, 0xF0])
    for item, f in [(0xEE, 0), (0xEE, 1), (0xEE, 2), (0xF0, 0), (0xF0, 1), (0xF0, 2)]:
        r = run_combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), item, f, False, S + "/cact", f"{item:02X}_{f}", q)
        print(os.path.basename(rom)[:12], hex(item), FIGHTERS[f], r.get("opponent"), r.get("returned_idle"), r.get("inventory"))
        h.run_event([0x88, 0x00, 0x7F, 0xFF, 0x8B, 0x00, 0xFF, 0x88, 0x0E, 0x7F, 0xFF, 0x8B, 0x0E, 0xFF, 0x88, 0x0F, 0x7F, 0xFF, 0x8B, 0x0F, 0xFF])
    h.close()
