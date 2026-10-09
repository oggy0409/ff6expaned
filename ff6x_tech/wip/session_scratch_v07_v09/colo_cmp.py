import sys, os
sys.path.insert(0,'tools')
from emu_item_tech import T
from PIL import Image
S=sys.argv[1]; state=open(S+'/colo/field.state','rb').read()
HARNESS=[0x9A, 0x31,0x82,0x81,0xFF]                     # v0.7.1 QaColo7: colosseum ; party_step RIGHT 1 ; return
# vanilla CB:78D9 flow with RAM-relative branch targets: fade_out 8, wait, menu, if $1EE=0 -> FADE, battle, FADE: fade_in 4, wait
def vanilla(base):
    fade=base+12
    return [0x5A,0x08,0x5C,0x9A,0xC0,0xEE,0x01]+list((fade-0xCA0000).to_bytes(3,'little'))+[0xAF,0xFE][:1]+[0x59,0x04,0x5C]
def run(rom, script, tag):
    h=T(rom); h.em.set_state(state)
    h.run_event(script, frames=1)
    ims=[]; log=[]
    for t in range(3600):
        h.step(1)
        if t%30==0 and t>120 and t<700: h.press("A",4,4)
        if t%300==0:
            ims.append(Image.fromarray(h.em.get_screen())); log.append((t, f"{h.r8(0x26):02X}", f"{h.evpc():06X}", round(float(h.em.get_screen().mean()),1), f"bt={h.r16(0x3ED4):04X}"))
    print(tag, log)
    W=Image.new('RGB',(256*6,224*2))
    for k,im in enumerate(ims[:12]): W.paste(im,((k%6)*256,(k//6)*224))
    W.save(S+'/colo/'+tag+'.png'); h.close()
clean="/home/user/ff6expaned/Final Fantasy III (USA) (Rev 1).sfc"
qa=S+'/final/FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc'
run(clean, HARNESS, 'rev1_harness_script')
v=vanilla(0x7E6C00)
print('vanilla script', bytes(v).hex(' '))
run(clean, v, 'rev1_vanilla_flow')
run(qa, v, 'v071_vanilla_flow')
