import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom)
idle=0
for t in range(60000):
    if t % 20 == 0: h.press('START' if t < 400 else 'A', 4, 4)
    else: h.step(1)
    if t % 10 == 0:
        idle = idle + 1 if h.evpc() == 0xCA0000 else 0
        if idle >= 30: break
for _ in range(120): h.step(1)
h.run_event(ev_give(0x13D)+ev_give(0x13E)+ev_give(0x13F)+[0x80,0x3D,0x80,0xE9])
open(out+'/field_items.state','wb').write(h.em.get_state())
n=[0]
def shot(tag):
    n[0]+=1; h.shot(f"{out}/{n[0]:02d}_{tag}.png")
def p(b,w=30): h.press(b,4,w)
p('X',60); p('DOWN'); p('DOWN'); p('A',60); p('A',60)   # equip menu, Terra
p('A',40); shot('slot_select')                            # EQUIP option -> slot select
p('A',60); shot('rhand_list')                             # R-hand list
for k in range(8):
    shot(f'list_pos{k}')
    p('DOWN',20)
print('rec0 equip', [hex(x) for x in h.eq(0)])
