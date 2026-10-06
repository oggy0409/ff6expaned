import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); h.em.set_state(open(O+'/battle.state','rb').read())
h.step(30)
while h.r8(0x2C)!=3: h.press("DOWN",8,24)
print("62CA", h.r8(0x62CA), "3010", h.r16(0x3010), "bits", [h.bit(256+k) for k in range(6)], "1E3E", h.r8(0x1E3E))
vals=[]
h.step(8,("A",))
for t in range(80):
    h.step(1); v=h.r8(0x1E3E)
    if not vals or vals[-1][1]!=v: vals.append((t,v))
print(vals, "62CA", h.r8(0x62CA))
