import sys, os
sys.path.insert(0, "/home/user/ff6expaned/ff6x_tech/tools")
from emu_colosseum import *
from emu_celes_suite import talk, pos
from emu_item_qa import Report
S = os.path.dirname(os.path.abspath(__file__))
q = Report(S + "/recep")
rom, ext = sys.argv[1], sys.argv[2] == "1"
h = T(rom); h.ext_aware = ext; boot_new_game(h)
h.run_event(sum(([0x80, i] for i in WAGERS), []))
w = 0x19D | (0 << 12)
h.run_event([0xDA, 0x58, 0x6A, w & 0xFF, w >> 8, 23, 5, 0x00], frames=400)
h.step(120)
print("map", hex(h.r16(0x82)), "pos", pos(h), "idle", h.idle())
q.shot(h, "colomap")
def start(hh):
    ok = talk(hh, "UP"); print("talk", ok)
    for _ in range(200):
        hh.step(1)
    q.shot(hh, "dlg")
    hh.press("A", 4, 10)
r = run_combo(h, start, 0x04, 1, True, S + "/recep", "recep", q)
r.pop("battle_frames", None)
print(r)
