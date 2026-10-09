import sys, hashlib, json
sys.path.insert(0,'tools')
import emu_monster_diff as M
from emu_harness import H
S=sys.argv[1]
forms=json.load(open(S+'/emu_final/mon_cmp.json'))['screen_diffs']
snap=open(S+'/reg/start.state','rb').read()
def shots(rom,x,d1):
    M.XINIT=x; M.D1=d1; h=H(rom); out={}
    for f in forms:
        r=M.run_one(h, snap, int(f,16)); out[f]=(hashlib.sha1(h.em.get_screen().tobytes()).hexdigest(), r.get('gfx_buffer_sha1'), r.get('pal_bytes'))
    h.close(); return out
a=shots(S+'/outall/FF6X_Rev1_TECH_v0.6.0_PRODUCTION.sfc',False,4)
b=shots(S+'/final/FF6X_Rev1_TECH_v0.7.1_PRODUCTION.sfc',True,5)
same=[f for f in forms if a[f][0]==b[f][0]]
print("screen identical with +1 frame:", len(same), "of", len(forms), [f for f in forms if f not in same])
json.dump({"formations":forms,"identical_at_plus_1_frame":same},open(S+'/emu_final/screen_plus1.json','w'))
