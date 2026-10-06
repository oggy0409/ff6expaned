import sys; sys.path.insert(0,'tools')
from emu_item_tech import *
h=T(sys.argv[1])
idle=0
for t in range(60000):
    if t % 20 == 0: h.press('START' if t < 400 else 'A', 4, 4)
    else: h.step(1)
    if t % 10 == 0:
        idle = idle + 1 if h.evpc() == 0xCA0000 else 0
        if idle >= 30: break
for _ in range(120): h.step(1)
print('e8',h.r16(0xE8),'pc',hex(h.evpc()))
print('bits',h.rbytes(XBITS,48).hex())
print('inv',[(s,hex(i),q) for s,i,q in h.inv()][:10])
ok=h.run_event([0x80,0xE9])
print('ran',ok,'e8',h.r16(0xE8),'pc',hex(h.evpc()))
print('bits',h.rbytes(XBITS,48).hex())
print('inv',[(s,hex(i),q) for s,i,q in h.inv()][:10])
ok=h.run_event([0x66,0x3D,0x01])
print('ran',ok,'e8',h.r16(0xE8),'pc',hex(h.evpc()))
print('bits',h.rbytes(XBITS,48).hex())
print('inv',[(s,hex(i),q) for s,i,q in h.inv()][:10])
