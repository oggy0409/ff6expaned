import sys, os, json
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_item_battle import labels, talk, to_terra, bslot
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
O=S+'/o09'; OUT=S+'/v9'
qa=O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'
L=labels(O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.manifest.json')
h=T(qa); h.em.set_state(open(OUT+'/cons.state','rb').read()); h.step(10)
h.w8(0x1609,10); h.w8(0x160A,0)
h.call_event(L['QaConsBtl9'],frames=1)
for _ in range(900): h.step(1)
to_terra(h); h.step(30)
h.shot(OUT+'/a3_menu.png')
print('list', [bslot(h,s) for s in range(10)])
print('cmd cursor', h.r8(0x2C))
open(OUT+'/a3_battle.state','wb').write(h.em.get_state())
