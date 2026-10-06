import sys, os, json
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_item_battle import labels, talk, to_terra, bslot
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
O=S+'/o09'; OUT=S+'/v9'
qa=O+'/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'
h=T(qa); h.em.set_state(open(OUT+'/a3_battle.state','rb').read()); h.step(10)
for _ in range(6):
    if h.r8(0x2C)==3: break
    h.press('DOWN',8,24)
h.press('A',8,60); h.shot(OUT+'/a4_items.png')
h.press('A',8,60); h.shot(OUT+'/a4_target.png')
hp0=[h.r16(0x3BF4+2*i) for i in range(4)]
h.press('A',8,10)
seq=[]
names=[]
for t in range(400):
    h.step(1)
    if t%20==0: h.shot(OUT+f'/a4_f{t:03d}.png')
print('hp before', hp0, 'after', [h.r16(0x3BF4+2*i) for i in range(4)])
print('list0', bslot(h,0), 'xheld', h.rbytes(0x1E36,8).hex())
open(OUT+'/a4_after.state','wb').write(h.em.get_state())
