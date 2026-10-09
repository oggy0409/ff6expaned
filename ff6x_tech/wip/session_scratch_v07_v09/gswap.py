import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[2]
def battle(h):
    h.em.set_state(open(S+'/bt/equipped.state','rb').read()); h.step(30)
    h.run_event([0x88,0x00,0xF7,0xFF, 0x4D,0x01,0x3F], frames=1)
    for _ in range(900): h.step(1)
    while h.r8(0x2C)!=3: h.press("DOWN",8,24)
    h.press("A",8,60)
def inv_list(h): return [hex(h.r8(0x2686+5*s)) for s in range(8)]
h=T(sys.argv[1])
# knife slot in battle list
battle(h); print("list", inv_list(h))
k=[s for s in range(8) if h.r8(0x2686+5*s)==0x01][0]
# (1) hand-first: R hand then knife
h.press("UP",8,40); h.press("A",8,40)
for _ in range(k//1+1):
    pass
h.press("DOWN",8,30)
for _ in range(k): h.press("DOWN",8,20)   # rows: one item per row
h.shot(S+'/g1.png'); h.press("A",8,60); h.shot(S+'/g1b.png')
print("(1) hand-first R<-knife: R", hex(h.r8(0x2B86)), "L", hex(h.r8(0x2B9A)), "list", inv_list(h))
# (3) item-first: knife then R hand
battle(h)
for _ in range(k): h.press("DOWN",8,20)
h.press("A",8,40); h.press("UP",8,20)
for _ in range(k+1): h.press("UP",8,20)
h.shot(S+'/g3.png'); h.press("A",8,60)
print("(3) item-first knife->R: R", hex(h.r8(0x2B86)), "L", hex(h.r8(0x2B9A)), "list", inv_list(h))
