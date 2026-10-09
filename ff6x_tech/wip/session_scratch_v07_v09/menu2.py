import sys, os; sys.path.insert(0,'tools')
from emu_item_tech import *
rom, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
h=T(rom)
h.em.set_state(open(out+'/../menu1/field_items.state','rb').read())
n=[0]
def shot(tag):
    n[0]+=1; h.shot(f"{out}/{n[0]:02d}_{tag}.png")
def p(b,w=30): h.press(b,4,w)
p('X',60); p('A',60)           # item list
p('A',60); shot('details_13D')
p('B',40); p('DOWN',20); p('A',60); shot('details_13E')
p('B',40); p('DOWN',20); p('A',60); shot('details_13F')
p('B',40); p('B',40); p('B',60)  # back to main
p('DOWN'); p('DOWN'); p('A',60); shot('equip_charsel')
p('A',60); shot('equip_menu')
