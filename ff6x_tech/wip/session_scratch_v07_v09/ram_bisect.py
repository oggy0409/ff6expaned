import sys
sys.path.insert(0,'tools')
from emu_harness import H
S=sys.argv[1]
R71=S+'/outall/FF6X_Rev1_TECH_v0.7.1_CELES_TECH.sfc'
def ram(st):
    h=H(R71); h.em.set_state(open(st,'rb').read()); h.gd.update_ram()
    r=bytes(h.gd.memory.extract(0x7E0000+i,'|u1') for i in range(0x20000)); h.close(); return r
a=ram(S+'/reg/chest60.state'); b=ram(S+'/reg/chest71.state')
diffs=[i for i in range(0x20000) if a[i]!=b[i]]
def fires(addrs):
    h=H(R71); h.em.set_state(open(S+'/reg/chest60.state','rb').read())
    for i in addrs: h.gd.memory.assign(0x7E0000+i,'|u1',b[i])
    h.press("UP",2,8)
    ok=False
    for k in range(3):
        h.press("A",4,4)
        for t in range(60):
            h.step(1)
            if h.r8(0xBA): ok=True
    h.close(); return ok
groups={"dp":[i for i in diffs if i<0x100],"02xx":[i for i in diffs if 0x100<=i<0x600],"06xx":[i for i in diffs if 0x600<=i<0x1000],
 "10xx":[i for i in diffs if 0x1000<=i<0x1600],"16xx":[i for i in diffs if 0x1600<=i<0x2000],"hi":[i for i in diffs if i>=0x2000]}
groups={hex(i):[i] for i in groups["dp"]}
for k,g in groups.items():
    print(k, len(g), "fires" if fires(g) else "BLOCKED", [hex(x) for x in g][:20])
