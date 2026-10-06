import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); h.em.set_state(open(O+'/battle.state','rb').read())
h.step(30)
snap=lambda: bytes(h.r8(a) for a in range(0x7A00,0x7C00))
before=[h.r8(0x7B80+i) for i in range(0)]
for k in range(3):
    m0={a:h.r8(a) for a in range(0x0000,0x0100)}
    h.press("DOWN",8,24)
    m1={a:h.r8(a) for a in range(0x0000,0x0100)}
    print("dp changed", [(hex(a),m0[a],m1[a]) for a in m0 if m0[a]!=m1[a]][:20])
    h.shot(O+f'/c{k}.png')
