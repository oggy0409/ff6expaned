import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_item_battle import labels
from emu_item_qa import boot_new_game
from PIL import Image
rom, man, out = sys.argv[1:4]
L=labels(man)
h=T(rom); boot_new_game(h)
h.run_event([0x80,0xE9,0x80,0x01])           # give Potion + Mithril Knife (vanilla wagers)
st=h.em.get_state()
open(out+'/field.state','wb').write(st)
h.call_event(L["QaColo7"], frames=1)
ims=[]; log=[]
for t in range(1500):
    h.step(1)
    if t%30==0 and t>120: h.press("A",4,4)
    if t%75==0:
        ims.append(Image.fromarray(h.em.get_screen())); log.append((t, f"{h.r8(0x26):02X}", f"{h.evpc():06X}", h.r8(0x1EBD)>>6&1, f"{h.r8(0x0205):02X}", round(float(h.em.get_screen().mean()),1)))
for l in log: print(l)
W=Image.new('RGB',(256*5,224*((len(ims)+4)//5)))
for k,im in enumerate(ims): W.paste(im,((k%5)*256,(k//5)*224))
W.save(out+'/repro.png')
