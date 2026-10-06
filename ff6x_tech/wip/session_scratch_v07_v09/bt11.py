import sys, os, itertools
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/bt/ng.state','rb').read())
print("eq", [hex(x) for x in h.eq(0)])
h.call_event(0xFF0086, frames=1)
for t in range(900): h.step(1)
print("3CA8", hex(h.r8(0x3CA8)), "cursor", h.r8(0x2C))
h.press("A",8,30); h.press("A",8,10)
seq=[]
for t in range(400):
    h.step(1); seq.append(h.r8(0xB7))
print([(k,len(list(g))) for k,g in itertools.groupby(seq)])
