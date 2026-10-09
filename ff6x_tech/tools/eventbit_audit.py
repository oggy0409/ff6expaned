"""Rev 1 event-bit / NPC-bit cross-reference audit.
Sources (all from the everything8215/ff6 disassembly, which reassembles
byte-identically to the Rev 1 CODE + EVENT regions):
  - event/world/vehicle/object scripts : switch / if_switch / set_switch /
    clr_switch / loop_until  (src/event/*.asm)
  - NPC visibility switches            : npc_prop (src/event/npc_prop.asm)
  - world-map modification table       : world_mode_ptr (src/world/world_mod.asm)
  - hard-coded ASM byte references      : $1E80-$1F5F (all non-event src)
  - initial NPC-bit table              : ROM C0:E0A0 (PC 0x00E0A0), 0x80 bytes
"""
import re,os,json,collections,sys
DIS='/home/claude/work/ff6dis'; ROM='/home/claude/work/rom/clean_rev1_reconstructed.sfc'
rom=open(ROM,'rb').read()
script=collections.defaultdict(list)
pat=re.compile(r'\b(if_switch|switch|set_switch|clr_switch|loop_until)\s+\$([0-9a-fA-F]{4})')
for f in ('src/event/event_main.asm','src/event/map_init_event.asm','src/event/event_trigger.asm'):
    for i,l in enumerate(open(os.path.join(DIS,f))):
        code=l.split(';')[0]
        for m in pat.finditer(code):
            script[int(m.group(2),16)].append(f"{f}:{i+1}:{m.group(1)}")
npc=collections.defaultdict(list)
for i,l in enumerate(open(os.path.join(DIS,'src/event/npc_prop.asm'))):
    m=re.search(r'npc_prop \{\d+, \d+\}, \$([0-9a-f]{4})',l)
    if m: npc[int(m.group(1),16)].append(f"npc_prop.asm:{i+1}")
world=collections.defaultdict(list)
for i,l in enumerate(open(os.path.join(DIS,'src/world/world_mod.asm'))):
    m=re.search(r'^\s+world_mode_ptr \$([0-9a-f]{4})',l)
    if m: world[int(m.group(1),16)].append(f"world_mod.asm:{i+1}")
asm=json.load(open(sys.argv[2] if len(sys.argv)>2 else '/home/claude/work/asm_eventbit_refs.json'))
GENERIC={0x1e80,0x1ea0,0x1ec0,0x1ee0,0x1f00,0x1f20,0x1f40}
asm_bytes=collections.defaultdict(list)
for k,v in asm.items():
    a=int(k,16)
    for s in v:
        idx=re.search(r'\$(?:7e|00|0)?'+k[2:]+r'\s*,\s*[xy]',s,re.I)
        if a in GENERIC and idx: continue          # generic script-driven accessor
        if 'sine_tbl' in s: continue               # data word, not an address
        asm_bytes[a].append(s)
        asm_bytes[a+1].append('(+1 conservative 16-bit) '+s)   # possible 16-bit access
def bit_ram(b): return 0x1E80+(b>>3)
rows=[]
for b in range(0x700):
    init = None
    if b>=0x300:
        t=rom[0x00E0A0:0x00E120]; o=b-0x300; init=(t[o>>3]>>(o&7))&1
    else: init=0   # InitEventSwitches clears $1E80-$1EDF on new game
    r={'bit':f"{b:03X}",'ram':f"{bit_ram(b):04X}.{b&7}",
       'range':'EVENT' if b<0x300 else 'NPC',
       'script_refs':len(script[b]),'npc_refs':len(npc[b]),'world_mod_refs':len(world[b]),
       'asm_byte_refs':len(asm_bytes.get(bit_ram(b),[])),'init':init}
    r['status']='FREE_CANDIDATE' if (r['script_refs']+r['npc_refs']+r['world_mod_refs']+r['asm_byte_refs'])==0 and init==0 else 'USED'
    rows.append(r)
json.dump({'rows':rows,'asm_byte_detail':{f"{k:04X}":v for k,v in sorted(asm_bytes.items()) if v}},open(sys.argv[1],'w'),indent=1)
free=[r['bit'] for r in rows if r['status']=='FREE_CANDIDATE']
fe=[x for x in free if int(x,16)<0x300]; fn=[x for x in free if int(x,16)>=0x300]
print('event-range free candidates:',len(fe)); print(' '.join(fe))
print('npc-range free candidates:',len(fn))
