import sys, os, numpy as np
sys.path.insert(0,'tools')
from emu_item_tech import T
S=sys.argv[1]; O=S+'/jump'; os.makedirs(O,exist_ok=True)
def run(rom, tag, epee=False):
    h=T(rom); h.em.set_state(open(S+'/bt/equipped.state','rb').read()); h.step(30)
    h.w8(0x1616, 0x16)                       # Terra command slot 1 := Jump
    if epee:
        h.w8(0x161F, 0x10); h.w8(0x1CF8+32, h.r8(0x1CF8+32) & 0xFE)   # vanilla Epee, ext bit cleared
    h.run_event([0x88,0x00,0xF7,0xFF, 0x4D,0x01,0x3F], frames=1)
    for _ in range(900): h.step(1)
    h.press("A",8,30); h.press("A",8,10)     # Jump -> target
    fr=[]
    for t in range(1600):
        h.step(1)
        if t%4==0: fr.append(np.asarray(h.em.get_screen()).copy())
    hp=[h.r16(0x3BF4+x) for x in range(8,20,2)]
    h.close(); return fr, hp
a,ha=run(S+'/out071c/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc','new')
b,hb=run(S+'/out071b/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc','old')
c,hc=run(S+'/out071c/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc','epee',True)
ab=[int((x!=y).any()) for x,y in zip(a,b)]; ac=[int((x!=y).any()) for x,y in zip(a,c)]
print("new!=old", ''.join(map(str,ab))); print("new!=epee", ''.join(map(str,ac))); print(ha,hb,hc)
from PIL import Image
idx=[i for i in range(len(a)) if ab[i]][:6]
W=Image.new('RGB',(256*3,224*max(1,len(idx))))
for r,i in enumerate(idx):
    for k,f in enumerate((a,b,c)): W.paste(Image.fromarray(f[i]),(256*k,224*r))
W.save(O+"/jump_cmp.png"); print(idx)
Image.fromarray(a[60]).save(O+"/a60.png"); Image.fromarray(a[200]).save(O+"/a200.png")
