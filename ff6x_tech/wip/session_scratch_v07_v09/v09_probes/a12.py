import sys, os
sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech/tools'); sys.path.insert(0,'/home/user/ff6expaned/ff6x_tech')
from emu_item_tech import T
from emu_item_qa import Report, boot_new_game, inv16
from emu_item_battle import labels, talk, bslot
from emu_equip_battle_v08 import finish_battle
from emu_cons_battle_v09 import choose_item, run_action, start
S='/tmp/claude-0/-home-user-ff6expaned/50190d0f-15ac-56a1-947a-50a94afc6a25/scratchpad'
QA=S+'/o09/FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc'; L=labels(QA[:-4]+'.manifest.json')
q=Report(S+'/v9/a12')
h=T(QA); boot_new_game(h)
def menu(p): h.call_event(L['QaAccess6'],frames=1); talk(h,p)
menu([2,0,0]); menu([0,2,2,1,0])
inv0=inv16(h)
start(h,L)
entry=next(s for s in range(256) if bslot(h,s)[0]==0x27 and bslot(h,s)[1]&1)
print('entry', entry, bslot(h,entry))
choose_item(h,entry); run_action(h,q,'x',700)
print('after action list', [bslot(h,s) for s in range(entry,entry+2)])
finish_battle(h)
inv1=inv16(h)
print('diff+', [(hex(i),n) for i,n in inv1 if (i,n) not in inv0]); print('diff-', [(hex(i),n) for i,n in inv0 if (i,n) not in inv1])
