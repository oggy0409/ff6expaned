import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_item_qa import boot_new_game, ext_slots, inv16
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); boot_new_game(h)
open(O+'/ng.state','wb').write(h.em.get_state())
print("latch", h.r8(0x1E80+0x1B5//8)>>(0x1B5&7)&1, "pos", h.r8(0x1FC0) if False else '')
# start the QA access event
x=h.r16(0xE8)
h.call_event(0xFF0000, frames=1)
for t in range(400):
    h.step(1)
    if t%40==0: h.shot(O+f'/d{t:03d}.png')
