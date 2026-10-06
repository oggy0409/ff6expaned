import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
from emu_item_qa import boot_new_game, ext_slots, inv16
S=sys.argv[2]; O=S+'/bt'
h=T(sys.argv[1]); h.em.set_state(open(O+'/ng.state','rb').read())

def talk(h, picks, frames=3000, tag=None):
    picks=list(picks); last=-1; stable=0; t=0
    while t < frames:
        h.step(1); t+=1
        n=h.r8(0x56F)
        if n and picks:
            stable = stable+1 if n==last else 0; last=n
            if stable>=30:
                k=picks.pop(0)
                for _ in range(10):
                    if h.r8(0x56E)==k: break
                    h.press("DOWN" if h.r8(0x56E)<k else "UP",4,8)
                h.press("A",4,8); t+=12; stable=0; last=-1
        elif h.idle():
            return True
        elif t%40==0 and not n:
            h.press("A",4,4); t+=8
    return h.idle()

h.call_event(0xFF0000, frames=1)
print(talk(h,[0,0]), [(s,hex(i),q) for s,i,q in h.inv()], "pos", hex(h.evpc()))
h.call_event(0xFF0000, frames=1)
print(talk(h,[0,0]), [(s,hex(i),q) for s,i,q in h.inv()])
h.call_event(0xFF0000, frames=1)
print(talk(h,[0,1,0]), [(s,hex(i),q) for s,i,q in h.inv()], "bit14E", h.r8(0x1E80+0x14E//8)>>(0x14E&7)&1)
h.shot(O+'/after_talk.png')
open(O+'/given.state','wb').write(h.em.get_state())
