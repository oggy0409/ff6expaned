import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from PIL import Image
S=sys.argv[1]
h=T("/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc"); h.em.set_state(open(S+'/colo/field.state','rb').read())
h.run_event([0x80,0x04,0x80,0x08,0x80,0x09])
print([(s,hex(h.r8(0x1869+s))) for s in range(6)])
h.call_event(0xCB78D9, frames=1)
prev=None; ims=[]
for t in range(700):
    h.step(1)
    st=(h.r8(0x26), h.r8(0x4B))
    if st!=prev: print(t, f"st={st[0]:02X} cur={st[1]}"); prev=st; ims.append(Image.fromarray(h.em.get_screen()))
    if t in (150,250,350,450): h.press("A",4,4)
W=Image.new('RGB',(256*5,224*2))
for k,im in enumerate(ims[:10]): W.paste(im,((k%5)*256,(k//5)*224))
W.save(S+'/colo/probe.png')
