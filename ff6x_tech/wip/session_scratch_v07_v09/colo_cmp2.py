import sys, os, json
sys.path.insert(0,'tools')
from emu_item_tech import T
from PIL import Image
S=sys.argv[1]; state=open(S+'/colo/field.state','rb').read()
def run(rom, tag, xinit):
    h=T(rom); h.em.set_state(state)
    if xinit:
        for a in range(0x1CF8,0x1D24): h.w8(a,0)
        for i,v in enumerate((0x58,0x49,0x01,0xFE)): h.w8(0x1D24+i,v)
    h.call_event(0xCB78D9, frames=1)
    ims=[]; log=[]
    for t in range(5400):
        h.step(1)
        if t%30==0 and 120<t<700: h.press("A",4,4)
        if t%400==0:
            ims.append(Image.fromarray(h.em.get_screen())); log.append((t, f"{h.r8(0x26):02X}", f"{h.evpc():06X}", round(float(h.em.get_screen().mean()),1), f"bt={h.r16(0x3ED4):04X}"))
        if t>2000 and h.idle(): break
    inv=[(s,h.r8(0x1869+s),h.r8(0x1969+s)) for s in range(256) if h.r8(0x1869+s)!=0xFF]
    print(tag, log, "final", h.idle(), round(float(h.em.get_screen().mean()),1), "inv", [(s,f"{i:02X}",q) for s,i,q in inv])
    W=Image.new('RGB',(256*7,224*2))
    for k,im in enumerate(ims[:14]): W.paste(im,((k%7)*256,(k//7)*224))
    W.save(S+'/colo/'+tag+'.png'); h.close()
run("/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc", 'rev1_cb78d9', False)
run(S+'/final/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc', 'v060_cb78d9', False)
run(S+'/final/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc', 'v071qa_cb78d9', True)
