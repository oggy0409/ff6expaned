import sys
sys.path.insert(0,'tools')
import emu_monster_diff as M, emu_celes_suite as CS
from emu_harness import H
S=sys.argv[1]; O=S+'/outall'
for r in sys.argv[2:]:
    h=H(r); snap=open(S+'/reg/start.state','rb').read()
    h.em.set_state(snap)
    if "v0.7.1" in r or "var" in r:
        for a in range(0x1CF8,0x1D24): h.w8(a,0)
        for i,v in enumerate((0x58,0x49,0x01,0xFE)): h.w8(0x1D24+i,v)
    h.step(2)
    for i, v in enumerate([0x4D, 0xFE, 0x3F, 0xFE]): h.gd.memory.assign(CS.SCRIPT_RAM + i, '|u1', v)
    CS.inject(h, CS.SCRIPT_RAM)
    ev=[]
    for t in range(400):
        if t < 26: h.w8(0x11E0, 0); h.w8(0x11E1, 0)
        h.step(1)
        st=(h.r16(0x3ED4)==0 and h.r16(0x3BF4)!=0xFFFF, h.r8(0x2C7) if False else None)
        ev.append((h.r16(0x3ED4), h.r16(0x3BF4)!=0xFFFF, h.r8(0x3219), h.r8(0x3221)))
    first=[i for i,e in enumerate(ev) if e[0]==0 and e[1] and i>26][:1]
    atb=[(i,e[2],e[3]) for i,e in enumerate(ev) if i in range(first[0], first[0]+12)]
    print(r, 'start frame', first, atb)
    h.close()
