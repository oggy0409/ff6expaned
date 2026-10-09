import sys
sys.path.insert(0, "/home/user/ff6expaned/ff6x_tech/tools")
from emu_colosseum import *
from emu_menu_nav import Nav, ST
def gt(h): return ((h.r8(0x21B)*60+h.r8(0x21C))*60+h.r8(0x21D))*60+h.r8(0x21E)
def go(rom, ext):
    h = T(rom); h.ext_aware = ext; boot_new_game(h); out=[("boot", h.f, gt(h))]
    h.run_event(sum(([0x80, i] for i in WAGERS), [])); out.append(("give", h.f, gt(h)))
    nv = Nav(h)
    h.call_event(VANILLA_COLO, frames=1); out.append(("call", h.f, gt(h)))
    nv.wait(ST["COLO_ITEM"], 600); out.append(("menu", h.f, gt(h)))
    h.step(60); out.append(("menu+60", h.f, gt(h)))
    nv.cursor_to(0); h.press("A", 4, 10); nv.wait(0x76, 600); out.append(("fighter", h.f, gt(h)))
    nv.cursor_lr(0); h.step(4, ("A",)); out.append(("A", h.f, gt(h)))
    print(rom.split('/')[-1], [(n, f, g, f - g) for n, f, g in out])
go("final/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc", False)
go("out072/FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc", True)
go("final/FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA.sfc", False)
