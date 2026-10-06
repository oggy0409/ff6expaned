import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
from emu_menu_nav import Nav
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom); h.em.set_state(open(sys.argv[3],'rb').read())
nv=Nav(h)
nv.open_main(); nv.main_to('Equip'); nv.press('A','EQUIP_OPT')
nv.cursor_lr(3); nv.press('A'); h.step(60)     # EMPTY
nv.cursor_lr(1)
import numpy as np
mask=np.array([0]*12,dtype=np.uint8); mask[8]=1
prev=None
for f in range(40):
    h.em.set_button_mask(mask if f<4 else np.zeros(12,dtype=np.uint8)); h.em.step()
    cur=(h.r8(0x1869),h.r8(0x1969),h.r8(0x1CF8),h.r8(0x161F),h.r8(0x1622), h.r8(0x26))
    if cur!=prev: print(f,[hex(x) for x in cur]); prev=cur
