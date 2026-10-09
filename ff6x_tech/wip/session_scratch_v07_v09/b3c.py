import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_item_battle import to_terra, bslot
S=sys.argv[1]
for rom in sys.argv[2:]:
    h=T(rom); h.em.set_state(open(S+'/bt/equipped.state','rb').read()); h.step(30)
    h.w8(0x161F,0x10); h.w8(0x1CF8+32, h.r8(0x1CF8+32)&0xFE)
    h.run_event([0x88,0x00,0xF7,0xFF,0x4D,0x01,0x3F], frames=1)
    for _ in range(900): h.step(1)
    to_terra(h)
    lst0=[bslot(h,s)[0] for s in range(10)]
    knife=lst0.index(0x01)
    h.step(30)
    for _ in range(6):
        if h.r8(0x2C)==3: break
        h.press("DOWN",8,24)
    h.press("A",8,60); h.press("UP",8,40); h.press("A",8,40)
    for _ in range(knife+1): h.press("DOWN",8,20)
    h.press("A",8,60)
    print(rom.split('/')[-1], "before", [hex(x) for x in lst0], "after", [hex(bslot(h,s)[0]) for s in range(10)], "hands", hex(h.r8(0x2B86)), hex(h.r8(0x2B9A)))
    h.close()
# --- continue to battle end on each ROM
for rom in sys.argv[2:]:
    h=T(rom); h.em.set_state(open(S+'/bt/equipped.state','rb').read()); h.step(30)
    h.w8(0x161F,0x10); h.w8(0x1CF8+32, h.r8(0x1CF8+32)&0xFE)
    h.run_event([0x88,0x00,0xF7,0xFF,0x4D,0x01,0x3F], frames=1)
    for _ in range(900): h.step(1)
    to_terra(h)
    knife=[bslot(h,s)[0] for s in range(10)].index(0x01)
    h.step(30)
    for _ in range(6):
        if h.r8(0x2C)==3: break
        h.press("DOWN",8,24)
    h.press("A",8,60); h.press("UP",8,40); h.press("A",8,40)
    for _ in range(knife+1): h.press("DOWN",8,20)
    h.press("A",8,60)
    for _ in range(3): h.press("B",8,30)
    print("after B: hands", hex(h.r8(0x2B86)), "2F30", h.r8(0x2F30))
    for t in range(6000):
        if t%16==0: h.step(4,("A",))
        else: h.step(1)
        if t>600 and h.idle(): break
    h.step(60)
    print(rom.split('/')[-1], "eq", [hex(h.r8(0x161F+k)) for k in range(6)], "inv", [(s,hex(i),q) for s,i,q in h.inv()])
    h.close()
