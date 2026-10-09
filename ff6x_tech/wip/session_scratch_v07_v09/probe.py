import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/bt/equipped.state','rb').read()); h.step(30)
h.run_event([0x88,0x00,0xF7,0xFF, 0x4D,0x01,0x3F], frames=1)
for _ in range(900): h.step(1)
while h.r8(0x2C)!=3: h.press("DOWN",8,24)
h.press("A",8,60)
def snap(): return {a:h.r8(a) for a in list(range(0x7A00,0x7C00))+list(range(0x8900,0x8A00))}
for b in ("DOWN","DOWN","RIGHT","UP","UP","UP"):
    s0=snap(); h.press(b,8,30); s1=snap()
    print(b, [(hex(a),s0[a],s1[a]) for a in s0 if s0[a]!=s1[a]][:12])
