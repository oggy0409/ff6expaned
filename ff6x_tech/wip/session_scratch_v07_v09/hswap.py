import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/bt/equipped.state','rb').read()); h.step(30)
h.run_event([0x88,0x00,0xF7,0xFF, 0x4D,0x01,0x3F], frames=1)
for _ in range(900): h.step(1)
while h.r8(0x2C)!=3: h.press("DOWN",8,24)
h.press("A",8,60); h.press("UP",8,40); h.press("A",8,40); h.press("RIGHT",8,40); h.press("A",8,60)
h.shot(S+'/hswap1.png')
print("battle hands", hex(h.r8(0x2B86)), hex(h.r8(0x2B9A)))
for _ in range(3): h.press("B",8,30)
for t in range(6000):
    if t%16==0: h.step(4,("A",))
    else: h.step(1)
    if t>600 and h.idle(): break
h.step(60)
print("eq after", [hex(x) for x in h.eq(0)], "bits", [h.bit(256+k) for k in range(6)])
