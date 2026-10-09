import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom)
h.em.set_state(open(sys.argv[3],'rb').read())
n=[0]
def shot(tag):
    n[0]+=1; h.shot(f"{out}/{n[0]:02d}_{tag}.png")
def p(b,w=30): h.press(b,4,w)
def st(): return {'inv':[(s,hex(i),q) for s,i,q in h.inv()], 'terra':[hex(x) for x in h.eq(0)]}
print('start', st())
p('X',60); p('DOWN'); p('DOWN'); p('A',60); p('A',60)   # equip menu Terra
p('A',40)                       # EQUIP -> slot select (R-hand)
p('A',60)                       # R-hand list
p('A',60); shot('after_equip_blade')
print('after R-hand', st())
p('DOWN'); p('DOWN'); p('DOWN')  # Body slot
p('A',60); shot('body_list'); p('A',60); shot('after_equip_mail')
print('after body', st())
p('B',40); p('B',40); p('B',60)   # back to main?
shot('back')
