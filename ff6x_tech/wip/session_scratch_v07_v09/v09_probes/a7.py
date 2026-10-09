import sys, os, json
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_item_qa import boot_new_game
from emu_item_battle import labels, talk
from emu_menu_nav import Nav, ST
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
O=S+'/o09'; OUT=S+'/v9'
qa=O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'
L=labels(O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.manifest.json')
h=T(qa); boot_new_game(h)
def menu(p): h.call_event(L['QaAccess6'],frames=1); return talk(h,p)
menu([0,0]); open(OUT+'/cons.state','wb').write(h.em.get_state())
inv=lambda: [(s,hex(i),q) for s,i,q in h.inv()]
gp=lambda: h.r8(0x1860)|h.r8(0x1861)<<8|h.r8(0x1862)<<16
nv=Nav(h)
h.run_event([0x9B,0x80],frames=60); nv.wait(ST['SHOP_OPT'],600); h.shot(OUT+'/a7_opt.png')
h.press('A',4,40); h.step(30); h.shot(OUT+'/a7_buy.png')
print('owned', [h.r8(0x9DC9+k) for k in range(8)], 'list', h.rbytes(0x9D89,8).hex(), 'prices', [h.r16(0x9F09+2*k) for k in range(8)], 'state', hex(h.r8(0x26)))
h.press('A',4,40); h.step(20); h.shot(OUT+'/a7_qty.png'); print('state', hex(h.r8(0x26)), 'sel', h.r8(0x28))
h.press('UP',4,20); h.step(10); print('sel', h.r8(0x28)); h.shot(OUT+'/a7_qty2.png')
g0=gp(); h.press('A',4,40); h.step(40); print('gp', g0, '->', gp(), 'inv', inv()[:3]); h.shot(OUT+'/a7_bought.png')
open(OUT+'/a7_shop.state','wb').write(h.em.get_state())
