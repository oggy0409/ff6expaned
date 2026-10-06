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
# equip blade + mail as before
p('X',60); p('DOWN'); p('DOWN'); p('A',60); p('A',60); p('A',40); p('A',60); p('A',60)
p('DOWN'); p('DOWN'); p('DOWN'); p('A',60); p('A',60)
p('B',40); p('B',40); p('B',60); shot('main')
# relic menu
p('DOWN'); p('A',60); p('A',60); shot('relic_menu')
p('A',40); p('A',60); shot('relic_list'); p('A',60); shot('relic_equipped')
print('after relic', st())
open(out+'/three_equipped.state','wb').write(h.em.get_state())
p('B',40); p('B',40); p('B',60)
