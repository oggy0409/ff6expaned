import sys, numpy as np, hashlib
sys.path.insert(0,'tools')
import emu_monster_diff as M
from emu_harness import H
S=sys.argv[1]; f=int(sys.argv[2],16)
def shot(rom,x):
    M.XINIT=x; h=H(rom); M.run_one(h, open(S+'/reg/start.state','rb').read(), f)
    s=hashlib.sha1(h.em.get_screen().tobytes()).hexdigest(); h.close(); return s
ref=shot(S+'/outall/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc',False)
for r in sys.argv[3:]:
    print(r.split('/')[-1], shot(r,True)==ref)
