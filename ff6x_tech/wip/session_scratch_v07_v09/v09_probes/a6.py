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
for _ in range(6):
    if h.r8(0x2C)==3: break
    h.press('DOWN',8,24)
h.press('A',8,60); h.press('A',8,60); h.press('A',8,60); h.press('A',8,4)
open(OUT+'/a6_queued.state','wb').write(h.em.get_state())
prev=None
for t in range(500):
    h.step(1)
    v=(h.r8(0x1E36),h.r8(0x1E37),h.rbytes(0x11A0,16).hex(), h.r8(0xB5), h.r16(0x3A7D)&0xff, h.r8(0x3410), h.r8(0x3411))
    if v!=prev: print(t, v); prev=v
