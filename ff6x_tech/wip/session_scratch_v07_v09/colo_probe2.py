import sys
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_menu_nav import Nav
from PIL import Image
S=sys.argv[1]
h=T("/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc"); h.em.set_state(open(S+'/colo/field.state','rb').read())
h.run_event([0x80,0x04])
h.call_event(0xCB78D9, frames=1)
nv=Nav(h)
print(nv.wait(0x72,400)); nv.cursor_to(2); print("cur",h.r8(0x4B)); h.press("A",4,10); print(nv.wait(0x76,400), hex(h.r8(0x205)))
ims=[Image.fromarray(h.em.get_screen())]
for b in ("DOWN","DOWN","RIGHT","UP","LEFT"):
    h.press(b,4,20); print(b, h.r8(0x4B), h.r8(0x4D), h.r8(0x4E)); ims.append(Image.fromarray(h.em.get_screen()))
W=Image.new('RGB',(256*6,224))
for k,im in enumerate(ims): W.paste(im,(k*256,0))
W.save(S+'/colo/probe2.png')
