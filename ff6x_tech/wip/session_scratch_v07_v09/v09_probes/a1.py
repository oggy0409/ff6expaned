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
print('sig', h.rbytes(0x1D24,4).hex(), 'xrare', h.rbytes(0x1E1D,6).hex(), 'trans', h.rbytes(0x1E36,10).hex())
open(OUT+'/boot.state','wb').write(h.em.get_state())
def menu(p): h.call_event(L['QaAccess6'],frames=1); return talk(h,p)
menu([0,0])
print('inv', [(s,hex(i),q) for s,i,q in h.inv()])
open(OUT+'/cons.state','wb').write(h.em.get_state())
nv=Nav(h); nv.open_main(); nv.main_to('Item'); nv.wait(ST['ITEM_OPT'] if False else 0x17,300); h.step(30)
h.shot(OUT+'/item_opt.png')
# choose "Use"? item option state: cursor 0 = Use
h.press('A',4,30); h.step(30); h.shot(OUT+'/item_list.png')
print('state', hex(h.r8(0x26)))
