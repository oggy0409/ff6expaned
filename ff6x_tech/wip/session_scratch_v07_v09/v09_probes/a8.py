import sys, os, json
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
O=S+'/o09'; OUT=S+'/v9'
qa=O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'
L=labels(O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.manifest.json')
h=T(qa); h.em.set_state(open(OUT+'/cons.state','rb').read()); h.step(10)
inv=lambda: [(s,hex(i),q) for s,i,q in h.inv()]
gp=lambda: h.r8(0x1860)|h.r8(0x1861)<<8|h.r8(0x1862)<<16
nv=Nav(h)
h.call_event(L['QaShop80'],frames=60); nv.wait(ST['SHOP_OPT'],600)
nv.cursor_lr(1); h.press('A',4,40); nv.wait(ST['SHOP_SELL']); h.step(20); h.shot(OUT+'/a8_sell.png')
res=[]
for s in range(8):
    nv.cursor_to(s); h.press('A',4,40); h.step(10)
    st=nv.state(); res.append((s,hex(st)))
    if st!=ST['SHOP_SELL']:
        h.shot(OUT+f'/a8_sellq{s}.png'); h.press('B',4,30); nv.wait(ST['SHOP_SELL'])
print('select results', res)
# sell one Iron Ration (slot 4)
nv.cursor_to(4); h.press('A',4,40); h.step(20); g0=gp(); h.press('A',4,40); h.step(40)
print('gp', g0, '->', gp(), 'inv', inv()); h.shot(OUT+'/a8_sold.png')
for _ in range(6): h.press('B',4,30)
for _ in range(3000):
    if h.idle(): break
    h.step(1)
print('idle', h.idle(), hex(h.evpc()), h.r16(0xE8), hex(h.r8(0x26))); h.shot(OUT+'/a8_exit.png')
# rare
def menu(p): h.call_event(L['QaAccess6'],frames=1); return talk(h,p)
menu([1,2,2,0])
print('rare bits', h.rbytes(0x1EBA,4).hex(), 'xrare', h.rbytes(0x1E1D,6).hex())
open(OUT+'/a8_rarefill.state','wb').write(h.em.get_state())
h.step(60); nv.open_main(); nv.main_to('Item'); nv.wait(ST['ITEM']); h.step(20); h.press('B',4,20); nv.wait(ST['ITEM_OPT']); h.step(20); h.shot(OUT+'/a8_opt.png'); print('opt', hex(h.r8(0x26)), h.r8(0x4B), h.r8(0x4D), h.r8(0x4E))
for _ in range(2): h.press('RIGHT',4,16)
print('opt2', h.r8(0x4B), h.r8(0x4D)); h.press('A',4,60); h.step(30)
h.shot(OUT+'/a8_rare_p0.png'); print('state', hex(h.r8(0x26)), 'list', h.rbytes(0x9D89,21).hex(), 'page', h.r8(0x1E3D), 'count', h.r8(0x64))
for _ in range(9): h.press('DOWN',4,12)
h.shot(OUT+'/a8_rare_row9.png'); print('row', h.r8(0x4E), 'idx', h.r8(0x4B))
h.press('DOWN',4,30); h.step(20); h.shot(OUT+'/a8_rare_p1.png'); print('page', h.r8(0x1E3D), 'list', h.rbytes(0x9D89,21).hex(), 'row', h.r8(0x4E))
h.press('R',4,30); h.step(20); h.shot(OUT+'/a8_rare_p2.png'); print('page', h.r8(0x1E3D), 'list', h.rbytes(0x9D89,21).hex())
h.press('R',4,30); h.step(20); print('page (no 4th)', h.r8(0x1E3D))
h.press('L',4,30); h.step(20); print('page after L', h.r8(0x1E3D))
h.press('UP',4,30); h.step(20); print('UP at row', h.r8(0x4E), 'page', h.r8(0x1E3D))
