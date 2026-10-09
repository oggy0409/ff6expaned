import sys
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_menu_nav import Nav, ST
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
O=S+'/o09'; OUT=S+'/v9'
h=T(O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'); h.em.set_state(open(OUT+'/a8_rarefill.state','rb').read())
nv=Nav(h); h.step(60); nv.open_main(); nv.main_to('Item'); nv.wait(ST['ITEM']); h.step(20); h.press('B',4,20); nv.wait(ST['ITEM_OPT']); h.step(20)
for _ in range(2): h.press('RIGHT',4,16)
h.press('A',4,60); h.step(120)
print([hex(h.r16(0x3249+2*i)) for i in range(20)])
print('data', [hex(h.r8(0x374A+2*i)) for i in range(20)])
print('states', [hex(h.r8(0x3649+2*i)) for i in range(20)])
h.step(4,('R',))
for t in range(12):
    h.step(1); print(t, 'st', hex(h.r8(0x3659)), 'posx', h.r16(0x33C9+0x10), 'page', h.r8(0x1E3D), 'buf', h.rbytes(0xA271,8).hex(), 'txt', h.rbytes(0x9EC9,6).hex())
