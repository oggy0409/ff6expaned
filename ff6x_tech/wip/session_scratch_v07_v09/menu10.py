import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
from emu_menu_nav import Nav
import numpy as np
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom); h.em.set_state(open(sys.argv[3],'rb').read())
nv=Nav(h)
nv.open_main(); nv.main_to('Equip'); nv.press('A','EQUIP_OPT')
print('cursor', h.r8(0x4B))
nv.cursor_lr(3)
print('before A', h.r8(0x1869), h.r8(0x1969), 'state', hex(h.r8(0x26)))
mask=np.zeros(12,dtype=np.uint8); mask[8]=1
prev=None
for f in range(80):
    h.em.set_button_mask(mask if f<4 else np.zeros(12,dtype=np.uint8)); h.em.step()
    cur=(h.r8(0x1869),h.r8(0x1969),h.r8(0x1CF8),h.r8(0x161F),h.r8(0x1622), h.r8(0x26), h.r8(0x4B))
    if cur!=prev: print(f,[hex(x) for x in cur]); prev=cur
print('--- now RIGHT presses')
for k in range(4):
    for f in range(30):
        h.em.set_button_mask(np.array([0,0,0,0,0,0,0,1 if f<4 else 0,0,0,0,0],dtype=np.uint8)); h.em.step()
        cur=(h.r8(0x1869),h.r8(0x1969),h.r8(0x1CF8),h.r8(0x161F),h.r8(0x1622), h.r8(0x26), h.r8(0x4B))
        if cur!=prev: print(k,f,[hex(x) for x in cur]); prev=cur
