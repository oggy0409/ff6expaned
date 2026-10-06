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
print([(s,hex(i),q) for s,i,q in h.inv()])
open(out+'/field_items.state','wb').write(h.em.get_state())
h.press('X',4,30); h.step(60); h.shot(out+'/m0_main.png')
h.press('A',4,30); h.step(60); h.shot(out+'/m1_items.png')
