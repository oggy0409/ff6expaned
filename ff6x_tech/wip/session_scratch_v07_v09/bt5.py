import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); h.em.set_state(open(O+'/battle.state','rb').read())
h.step(30)
while h.r8(0x2C)!=3: h.press("DOWN",8,24)
h.press("A",8,60); h.shot(O+'/i0.png')
open(O+'/itemmenu.state','wb').write(h.em.get_state())
m0={a:h.r8(a) for a in range(0x0000,0x0100)}
h.press("UP",8,40); h.shot(O+'/i1.png')
m1={a:h.r8(a) for a in range(0x0000,0x0100)}
print("dp changed", [(hex(a),m0[a],m1[a]) for a in m0 if m0[a]!=m1[a]][:20])
h.press("A",8,40); h.shot(O+'/i2.png')
print("hands after A", hex(h.r8(0x3CA8)), hex(h.r8(0x3CA9)), [hex(h.r8(0x2B86+k)) for k in range(5)], [hex(h.r8(0x2B9A+k)) for k in range(5)])
h.press("DOWN",8,40); h.press("A",8,40); h.shot(O+'/i3.png')
print("after drop", hex(h.r8(0x3CA8)), hex(h.r8(0x3CA9)), [hex(h.r8(0x2B86+k)) for k in range(5)], [[hex(h.r8(0x2686+5*s+k)) for k in range(5)] for s in range(3)])
h.press("B",8,40); h.press("B",8,40); h.shot(O+'/i4.png')
