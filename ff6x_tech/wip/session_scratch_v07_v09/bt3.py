import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_item_qa import boot_new_game, ext_slots, inv16, equip_slot
from emu_menu_nav import Nav, ST
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); h.em.set_state(open(O+'/given.state','rb').read())
nv=Nav(h); h.step(120)
nv.open_main(); nv.main_to("Equip"); nv.press("A","EQUIP_OPT"); nv.press("A","EQUIP_SLOT")
equip_slot(nv,h,0,0); equip_slot(nv,h,3,0)
nv.back_to_main(); nv.main_to("Relic"); nv.press("A","RELIC_OPT"); nv.press("A","RELIC_SLOT")
nv.cursor_to(0); nv.press("A","RELIC_LIST"); nv.cursor_to(0); h.press("A",4,30); h.step(60)
nv.back_to_main(); nv.close(); h.step(60)
print([hex(x) for x in h.eq(0)], [(s,hex(i),q) for s,i,q in h.inv()], hex(h.r8(0x1614)))
open(O+'/equipped.state','wb').write(h.em.get_state())
h.call_event(0xFF0086, frames=1)
seen=set(); b7=[]
for t in range(900):
    h.step(1)
    if t%60==0: h.shot(O+f'/b{t:04d}.png')
print("3CA8", hex(h.r8(0x3CA8)), hex(h.r8(0x3CA9)), "3B68", h.r8(0x3B68), h.r8(0x3B69), "list R", [hex(h.r8(0x2B86+k)) for k in range(5)])
print("items", [[hex(h.r8(0x2686+5*s+k)) for k in range(5)] for s in range(7)])
open(O+'/battle.state','wb').write(h.em.get_state())
