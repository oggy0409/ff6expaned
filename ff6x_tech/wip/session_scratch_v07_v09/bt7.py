import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); h.em.set_state(open(O+'/battle.state','rb').read())
h.step(30)
while h.r8(0x2C)!=3: h.press("DOWN",8,24)
h.press("A",8,60)
h.press("UP",8,40); h.shot(O+'/j1.png')
h.press("A",8,40); h.press("DOWN",8,40); h.press("A",8,40)
print("R swap attempt", hex(h.r8(0x3CA8)), hex(h.r8(0x3CA9)), [hex(h.r8(0x2B86+k)) for k in range(5)], [hex(h.r8(0x2686+k)) for k in range(5)])
h.shot(O+'/j2.png')
h.press("UP",8,40); h.press("RIGHT",8,40); h.shot(O+'/j3.png')
h.press("A",8,40); h.press("DOWN",8,40); h.press("A",8,40); h.shot(O+'/j4.png')
print("L swap attempt", hex(h.r8(0x3CA8)), hex(h.r8(0x3CA9)), [hex(h.r8(0x2B9A+k)) for k in range(5)], [hex(h.r8(0x2686+k)) for k in range(5)])
