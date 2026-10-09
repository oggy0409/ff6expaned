import sys, os, json
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_menu_nav import Nav, ST
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
O=S+'/o09'; OUT=S+'/v9'
qa=O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'
h=T(qa); h.em.set_state(open(OUT+'/cons.state','rb').read()); h.step(10)
hp=lambda: h.r16(0x1609)
h.w8(0x1609,10); h.w8(0x160A,0)
print('terra hp', hp(), 'max', h.r16(0x160B))
nv=Nav(h); nv.open_main(); nv.main_to('Item'); nv.wait(ST['ITEM']); h.step(30)
h.shot(OUT+'/a2_list.png')
print('cursor', h.r8(0x4B))
h.press('A',4,40); h.step(40); print('state after A', hex(h.r8(0x26))); h.shot(OUT+'/a2_target.png')
h.press('A',4,40); h.step(60); print('state after A2', hex(h.r8(0x26)), 'hp', hp(), 'qty', h.r8(0x1969))
h.shot(OUT+'/a2_used.png')
h.step(60); h.press('A',4,40); h.step(90); print('state after A3', hex(h.r8(0x26)), 'hp', hp(), 'qty', h.r8(0x1969))
h.shot(OUT+'/a2_used2.png')
h.press('A',4,40); h.step(90); print('again: hp', hp(), 'qty', h.r8(0x1969))
open(OUT+'/a2_end.state','wb').write(h.em.get_state())
