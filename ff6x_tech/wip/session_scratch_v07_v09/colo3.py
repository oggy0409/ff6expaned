import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_menu_nav import Nav, ST
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/qa1/field_items.state','rb').read())
nv=Nav(h)
r=h.run_event([0x9A], frames=60)
print("ret",r, hex(nv.state()))
for t in range(600):
    h.step(1)
    if t%60==0: print(t, hex(h.evpc()), h.r16(0xE8), hex(nv.state()))
h.shot(S+'/colo3.png')
