import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from PIL import Image
S=sys.argv[2]
h=T(sys.argv[1]); h.em.set_state(open(S+'/bt/equipped.state','rb').read()); h.step(30)
h.run_event([0x88,0x00,0xF7,0xFF, 0x4D,0x01,0x3F], frames=1)
for _ in range(900): h.step(1)
while h.r8(0x2C)!=3: h.press("DOWN",8,24)
h.press("A",8,90)
ims=[]
for b in ("-","DOWN","DOWN","DOWN","UP","UP","UP","RIGHT"):
    if b!="-": h.press(b,8,40)
    print(b, "row", h.r8(0x894F), "col", h.r8(0x894B), "7b99", h.r8(0x7B99))
    ims.append(Image.fromarray(h.em.get_screen()))
W=Image.new('RGB',(256*4,224*2))
for k,im in enumerate(ims): W.paste(im,((k%4)*256,(k//4)*224))
W.save(S+'/probe2.png')
