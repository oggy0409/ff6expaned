import sys, os, numpy as np
sys.path.insert(0,'tools')
import emu_monster_diff as M
from emu_harness import H
from PIL import Image
S=sys.argv[1]; O=S+'/outall'
imgs=[]
for r,lag in (('v0.6.0',0),('v0.7.1',0),('v0.7.1',1)):
    M.LAG=lag; M.D1=30
    h=H(f'{O}/FF6X_Rev1_TECH_{r}_PRODUCTION.sfc'); snap=open(S+'/reg/start.state','rb').read()
    res=M.run_one(h, snap, 0)
    imgs.append(np.asarray(h.em.get_screen()).copy()); h.close()
d=(imgs[0]!=imgs[1]).any(axis=2); ys,xs=np.nonzero(d); print('diff px lag0',d.sum(), (ys.min(),ys.max(),xs.min(),xs.max()) if d.sum() else None)
d=(imgs[0]!=imgs[2]).any(axis=2); ys,xs=np.nonzero(d); print('diff px lag1',d.sum(), (ys.min(),ys.max(),xs.min(),xs.max()) if d.sum() else None)
Image.fromarray(np.concatenate(imgs,axis=1)).resize((256*3*2,448)).save(S+'/reg/scr_cmp.png')
