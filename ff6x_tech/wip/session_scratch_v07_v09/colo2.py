import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_menu_nav import Nav, ST
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/qa1/field_items.state','rb').read())
nv=Nav(h)
h.call_event(0xCB7552, frames=60)
print("shop", nv.wait(ST["SHOP_OPT"],600))
nv.cursor_lr(1); h.press("A",4,40); print("sell", nv.wait(ST["SHOP_SELL"]))
nv.cursor_to(0); h.press("A",4,40); print("after A on ext", hex(nv.state()))
for i in range(6):
    h.press("B",4,30); print("B", hex(nv.state()), hex(h.evpc()), h.r16(0xE8))
for t in range(1500):
    h.step(1)
    if h.evpc()==0xCA0000 and h.r16(0xE8)==0: break
print(t, hex(h.evpc()), h.r16(0xE8), hex(nv.state()))
h.shot(S+'/colo2.png')
