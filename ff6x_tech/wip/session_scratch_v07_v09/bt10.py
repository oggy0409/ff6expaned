import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]; O=S+'/bt/atk'; os.makedirs(O,exist_ok=True)
h=T(sys.argv[1]); h.em.set_state(open(S+'/bt/battle.state','rb').read())
h.step(30)
print("cursor", h.r8(0x2C))
h.press("A",8,30); h.press("A",8,10)
hp0=[h.r16(0x3BF4+x) for x in range(8,20,2)]
seq=[]
for t in range(400):
    h.step(1)
    v=h.r8(0x626A); seq.append(v)
    if t%6==0 and t<240: h.shot(O+f'/a{t:03d}.png')
hp1=[h.r16(0x3BF4+x) for x in range(8,20,2)]
import itertools
print([(k,len(list(g))) for k,g in itertools.groupby(seq)])
print("monster HP", hp0, hp1)
