import sys
sys.path.insert(0,'tools')
import emu_colosseum as C
from emu_item_tech import T
from emu_item_qa import boot_new_game, Report
from emu_item_battle import labels
from emu_menu_nav import Nav, ST
S=sys.argv[1]; qa=S+'/out072/FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.sfc'
L=labels(S+'/out072/FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.manifest.json')
q=Report(S+'/eqdbg')
h=T(qa); boot_new_game(h); h.run_event(sum(([0x80,i] for i in C.WAGERS),[]))
r=C.run_combo(h, lambda hh: hh.call_event(L["QaColo7"], frames=1), 0x04, 1, True, S+'/eqdbg', 'x', q)
print({k:v for k,v in r.items() if k!='battle_frames'})
nv=Nav(h); h.step(60); nv.open_main(); q.shot(h,'main'); nv.main_to("Equip"); h.step(60); q.shot(h,'char'); print(hex(nv.state()), h.r8(0x4B))
open(S+'/eqdbg/after.state','wb').write(h.em.get_state())
