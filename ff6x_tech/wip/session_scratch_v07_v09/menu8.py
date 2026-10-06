import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
from emu_menu_nav import Nav
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom); h.em.set_state(open(sys.argv[3],'rb').read())
nv=Nav(h)
def st(): return {'inv':[(s,hex(i),q) for s,i,q in h.inv()], 'terra':[hex(x) for x in h.eq(0)], 'bits': h.rbytes(0x1CF8,44).hex()}
print('start', st())
nv.open_main(); nv.main_to('Equip'); nv.press('A','EQUIP_OPT')
nv.cursor_lr(3); nv.press('A'); h.step(60)     # EMPTY
print('empty', st())
nv.cursor_lr(1); nv.press('A'); h.step(60)     # OPTIMUM
print('optimum', st())
