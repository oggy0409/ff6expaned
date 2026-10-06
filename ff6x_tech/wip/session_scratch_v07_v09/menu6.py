import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom)
h.em.set_state(open(sys.argv[3],'rb').read())
n=[0]
def shot(tag):
    n[0]+=1; h.shot(f"{out}/{n[0]:02d}_{tag}.png")
def p(b,w=30): h.press(b,4,w); print(b, 'state', hex(h.r8(0x26)))
p('X',60); p('DOWN'); p('DOWN'); p('A',60); p('A',60); p('A',40); p('A',60); p('A',60)
p('DOWN'); p('DOWN'); p('DOWN'); p('A',60); p('A',60)
shot('a'); p('B',40); shot('b1'); p('B',40); shot('b2')
