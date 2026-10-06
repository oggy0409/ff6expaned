import sys, os, hashlib, json
sys.path.insert(0, "/home/user/ff6expaned/ff6x_tech/tools")
from emu_colosseum import *
from emu_item_qa import Report
S = os.getcwd()
REV1 = "/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc"
roms = [("rev1", REV1, False), ("v060prod", "final/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc", False),
        ("v071prod", "final/FF6X_Rev1_TECH_v0.7.1_PRODUCTION.sfc", True),
        ("v072qa_direct", "out072/FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.sfc", True),
        ("v072prod", "out072/FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc", True)]
q = Report(S + "/c1diag")
for name, rom, ext in roms:
    h = T(rom); h.ext_aware = ext; boot_new_game(h)
    h.run_event(sum(([0x80, i] for i in WAGERS), []))
    fc0 = h.r8(0x1F6D)
    r = run_combo(h, lambda hh: hh.call_event(VANILLA_COLO, frames=1), 0xE9, 0, False, S + "/c1diag", name, q)
    fr = sorted(r.pop("battle_frames", {}).items(), key=lambda x: x[1])
    print(name, "rng1F6D_before", fc0, "inv", r.get("inventory")[:2], "t-first", [f[0][:6] for f in fr[:3]],
          "hp_terra", h.r16(0x1609), "status", hex(h.r8(0x1614)))
    h.close()
