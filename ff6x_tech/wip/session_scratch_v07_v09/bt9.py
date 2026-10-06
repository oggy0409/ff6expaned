import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); h.em.set_state(open(O+'/battle.state','rb').read())
inv0=h.inv(); eq0=h.eq(0)
# synthetic "stolen" items placed where the battle sees empty slots (slot 1/2 are extended in the field)
for s,(i,q) in ((1,(0xE9,3)),(2,(0x01,1))):
    for k,v in enumerate((i,0x80,0x41,q,0xFF)): h.w8(0x2686+5*s+k,v)
b7=[]; hp=[]
for t in range(6000):
    if t%16==0: h.step(4,("A",))
    else: h.step(1)
    v=h.r8(0xB7)
    if not b7 or b7[-1]!=v: b7.append(v)
    if t%300==0: h.shot(O+f'/f{t:05d}.png')
    if h.idle() and t>600: break
print("t",t,"b7 values", sorted(set(b7)))
h.step(120)
print("inv before", [(s,hex(i),q) for s,i,q in inv0])
print("inv after ", [(s,hex(i),q) for s,i,q in h.inv()])
print("eq", [hex(x) for x in eq0], [hex(x) for x in h.eq(0)], "status", hex(h.r8(0x1614)))
h.shot(O+'/after_battle.png')
open(O+'/after_battle.state','wb').write(h.em.get_state())
