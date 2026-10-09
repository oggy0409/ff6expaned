import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_menu_nav import Nav, ST
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/qa1/field_items.state','rb').read())
nv=Nav(h)
h.call_event(0xCB7552, frames=60)
print("shop", nv.wait(ST["SHOP_OPT"],600))
for _ in range(6): h.press("B",4,30)
for t in range(3000):
    h.step(1)
    if t%100==0: print(t, hex(h.evpc()), h.r16(0xE8), hex(h.r8(0x26)), hex(h.r16(0xE5)))
