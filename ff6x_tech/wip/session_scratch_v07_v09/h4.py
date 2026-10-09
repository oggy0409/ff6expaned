import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_menu_nav import Nav, ST
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/qa1/field_items.state','rb').read())
nv=Nav(h)
print([(s,hex(i),q) for s,i,q in h.inv()])
nv.open_main(); nv.main_to("Item"); nv.wait(ST["ITEM"])
print("state",hex(nv.state()), "cur",h.r8(0x4B))
nv.cursor_to(0)
h.press("A",4,20); print("after A", hex(nv.state()))
for _ in range(20): h.step(1)
print("state",hex(nv.state()))
nv.cursor_to(1); print("cur",h.r8(0x4B), hex(nv.state()))
h.press("A",4,40); print("after A2", hex(nv.state()))
h.step(30)
print([(s,hex(i),q) for s,i,q in h.inv()])
h.shot(S+'/h4.png')
