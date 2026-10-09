#!/usr/bin/env python3
"""Rev 1 map-capacity audit (machine-readable). Reads only the clean ROM plus
event-script cross-references from the Rev 1-verified disassembly source."""
import sys, json, re, os
rom = open(sys.argv[1], 'rb').read(); DIS = sys.argv[2]; out = sys.argv[3]
pc = lambda s: s - 0xC00000
w16 = lambda a: rom[a] | rom[a+1] << 8
def ptr_tbl(base_snes, n, rel_snes=None):
    b = pc(base_snes); return [w16(b + 2*i) for i in range(n)]
N = 0x1A0
T = {
 'event_triggers': (0xC40000, 0xC40000, 5),
 'npcs':           (0xC41A10, 0xC41A10, 9),
 'short_entrances':(0xDFBB00, 0xDFBB00, 6),
 'long_entrances': (0xEDF480, 0xEDF480, 7),
}
counts = {}
ptrcount = {}
for k, (pb, rel, sz) in T.items():
    # count pointer entries: table ends where data starts (first pointer value)
    first = w16(pc(pb)); n_ptr = first // 2
    ptrcount[k] = n_ptr
    p = ptr_tbl(pb, n_ptr)
    counts[k] = [((p[i+1] - p[i]) // sz) if i + 1 < n_ptr else None for i in range(n_ptr)]
# entrance destinations
dest = {}
def scan_ent(k, mapoff, sz):
    pb = T[k][0]; p = ptr_tbl(pb, ptrcount[k])
    for m in range(ptrcount[k] - 1):
        for r in range(p[m], p[m+1], sz):
            a = pc(pb) + r; mw = w16(a + mapoff) & 0x1FF
            dest.setdefault(mw, []).append(f"{k}:map{m:03X}")
scan_ent('short_entrances', 2, 6); scan_ent('long_entrances', 3, 7)
# map startup (init) events: 24-bit, 512 slots
init = [(rom[pc(0xD1FA00)+3*i] | rom[pc(0xD1FA00)+3*i+1] << 8 | rom[pc(0xD1FA00)+3*i+2] << 16) + 0xCA0000 for i in range(512)]
EVENT_RETURN = None
# event-script load_map references (decimal map ids in source)
lm = {}
for i, l in enumerate(open(os.path.join(DIS, 'src/event/event_main.asm'))):
    m = re.search(r'\bload_map(?:_vehicle)?\s+(\$?[0-9a-fA-F]+)\s*,', l.split(';')[0])
    if m:
        v = m.group(1); mid = int(v[1:], 16) if v.startswith('$') else int(v)
        lm.setdefault(mid & 0x1FF, []).append(i + 1)
mp = pc(0xED8F00)
rows = []
from collections import Counter
initc = Counter(init)
for m in range(N):
    props = rom[mp + 33*m: mp + 33*m + 33] if m < 415 else b''
    rows.append({'map': f"{m:03X}",
                 'props_present': m < 415,
                 'props_all_zero': (props == bytes(33)) if props else None,
                 'props_hex': props.hex(),
                 'npcs': counts['npcs'][m] if m < len(counts['npcs']) else None,
                 'event_triggers': counts['event_triggers'][m] if m < len(counts['event_triggers']) else None,
                 'short_entrances': counts['short_entrances'][m] if m < len(counts['short_entrances']) else None,
                 'long_entrances': counts['long_entrances'][m] if m < len(counts['long_entrances']) else None,
                 'init_event': f"{init[m]:06X}", 'init_event_shared_by': initc[init[m]],
                 'incoming_entrances': dest.get(m, []),
                 'event_load_map_refs': len(lm.get(m, [])),
                 'event_load_map_lines': lm.get(m, [])[:10]})
cands = ['0C7','0DE','0DF','0E0','0E3','0E4','0E5','0E6','11E']
res = {'pointer_entries': ptrcount, 'map_prop_entries': 415, 'map_init_event_slots': 512,
       'map_index_bits': 9, 'special_map_ids': {'0x1FF': 'return to parent map (entrance code cmp #$01FF)', '0x000-0x002': 'world maps (entrance code cmp #$0003)'},
       'rows': rows, 'community_free_candidates': [r for r in rows if r['map'] in cands]}
json.dump(res, open(out, 'w'), indent=1)
print('pointer entries', ptrcount)
print('map  prop0 npc trg sEnt lEnt init     shr inRefs loadmapRefs')
for r in res['community_free_candidates']:
    print(r['map'], r['props_all_zero'], r['npcs'], r['event_triggers'], r['short_entrances'], r['long_entrances'], r['init_event'], r['init_event_shared_by'], len(r['incoming_entrances']), r['event_load_map_refs'], r['incoming_entrances'][:4])
