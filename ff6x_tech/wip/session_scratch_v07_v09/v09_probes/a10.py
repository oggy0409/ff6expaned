import sys
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_item_qa import boot_new_game
from emu_item_battle import labels, talk
from emu_cons_battle_v09 import choose_item
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
rom=S+'/o09/FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc'
L=labels(S+'/o09/FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.manifest.json')
h=T(rom); boot_new_game(h)
h.call_event(L['QaAccess6'],frames=1); talk(h,[0,1,1])
h.run_event([0x80,0x27,0x80,0xE9])
h.call_event(L['QaTestBtl8'],frames=1)
for _ in range(900): h.step(1)
for _ in range(80):
    if h.r8(0x62CA)==3: break
    h.press('Y',4,30); h.step(30)
h.step(30)
for _ in range(8):
    if h.r8(0x2C)==1: break
    h.press('DOWN',8,24)
h.press('A',8,60); h.shot(S+'/v9/a10_v08_throw.png')
for _ in range(3): h.press('B',8,30)
for _ in range(8):
    if h.r8(0x2C)==3: break
    h.press('DOWN',8,24)
h.press('A',8,60); h.shot(S+'/v9/a10_v08_item.png')
