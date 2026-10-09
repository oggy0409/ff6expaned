import stable_retro as retro, numpy as np, warnings
warnings.filterwarnings('ignore')
from PIL import Image
BTN=["B","Y","SELECT","START","UP","DOWN","LEFT","RIGHT","A","X","L","R"]
class H:
    def __init__(s,rom):
        s.em=retro.RetroEmulator(rom); s.gd=retro.data.GameData(); s.em.configure_data(s.gd); s.f=0
    def close(s):
        import gc
        del s.em, s.gd
        gc.collect()
    def step(s,n=1,btn=()):
        mask=np.array([1 if b in btn else 0 for b in BTN],dtype=np.uint8)
        for _ in range(n): s.em.set_button_mask(mask); s.em.step(); s.f+=1
    def press(s,b,hold=4,rel=8): s.step(hold,(b,)); s.step(rel)
    def r8(s,a): s.gd.update_ram(); return s.gd.memory.extract(0x7E0000+a,'|u1')
    def r16(s,a): return s.r8(a)|s.r8(a+1)<<8
    def w8(s,a,v): s.gd.memory.assign(0x7E0000+a,'|u1',v)
    def shot(s,p): Image.fromarray(s.em.get_screen()).resize((512,448),Image.NEAREST).save(p)
    def evpc(s): return s.r8(0xE5)|s.r8(0xE6)<<8|s.r8(0xE7)<<16
