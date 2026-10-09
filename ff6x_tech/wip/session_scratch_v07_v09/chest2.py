import sys
sys.path.insert(0,'tools')
from emu_harness import H
h=H(sys.argv[1]); h.em.set_state(open(sys.argv[2],'rb').read())
h.press("UP",2,8)
log=[]
for k in range(3):
    h.press("A",4,4)
    for t in range(60):
        h.step(1)
        log.append((h.f, hex(h.evpc()), h.r8(0xBA), h.r16(0xE8)))
for t in range(300):
    h.step(1)
    if t%20==0: log.append((h.f, hex(h.evpc()), h.r8(0xBA), h.r16(0xE8), hex(h.r8(0x26))))
import itertools
prev=None
for l in log:
    if l[1:]!=prev: print(l); prev=l[1:]
h.shot(sys.argv[3])
