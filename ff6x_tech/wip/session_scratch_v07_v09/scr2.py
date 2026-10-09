import sys, os, numpy as np
sys.path.insert(0,'tools')
import emu_monster_diff as M
from emu_harness import H
from PIL import Image
S=sys.argv[1]; f=int(sys.argv[2],16)
imgs=[]
for rom,x in ((S+'/final/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc',False) if False else (S+'/outall/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc',False),(S+'/final/FF6X_Rev1_TECH_v0.7.1_PRODUCTION.sfc',True)):
    M.XINIT=x
    h=H(rom); res=M.run_one(h, open(S+'/reg/start.state','rb').read(), f)
    imgs.append(np.asarray(h.em.get_screen()).copy()); h.close()
d=(imgs[0]!=imgs[1]).any(axis=2); ys,xs=np.nonzero(d); print('diff px',d.sum(), (ys.min(),ys.max(),xs.min(),xs.max()) if d.sum() else None)
Image.fromarray(np.concatenate(imgs,axis=1)).resize((1024,448)).save(S+'/scr_%03X.png'%f)
