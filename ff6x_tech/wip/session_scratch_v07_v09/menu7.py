import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
from emu_menu_nav import Nav
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom); h.em.set_state(open(sys.argv[3],'rb').read())
nv=Nav(h)
def st(): return {'inv':[(s,hex(i),q) for s,i,q in h.inv()], 'terra':[hex(x) for x in h.eq(0)]}
nv.open_main(); nv.main_to('Equip'); nv.press('A','EQUIP_OPT')
print('equip opt cursor', h.r8(0x4B))
nv.cursor_lr(1); nv.press('A'); h.step(60)     # OPTIMUM
h.shot(out+'/optimum.png'); print('optimum', st())
nv.cursor_lr(3); nv.press('A'); h.step(60)     # EMPTY
h.shot(out+'/empty.png'); print('empty', st())
nv.cursor_lr(1); nv.press('A'); h.step(60)     # OPTIMUM again
print('optimum2', st())
nv.cursor_lr(2); nv.press('A','EQUIP_REMOVE'); nv.press('A'); h.step(30)   # RMOVE R-hand
h.shot(out+'/remove_rhand.png'); print('remove rhand', st())
print(nv.log)
