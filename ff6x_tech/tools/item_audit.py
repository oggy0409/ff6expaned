#!/usr/bin/env python3
"""Rev 1 item-ID usage audit (machine-readable). Every vanilla 1-byte item
reference source that is table-driven is counted per item ID."""
import sys, json, re, os, collections
rom = open(sys.argv[1], 'rb').read(); DIS = sys.argv[2]; out = sys.argv[3]
pc = lambda s: s - 0xC00000
w16 = lambda a: rom[a] | rom[a+1] << 8
use = collections.defaultdict(lambda: collections.Counter())
# item names (D2:B300, 13 bytes: symbol + 12 chars, menu font)
def iname(i):
    b = rom[pc(0xD2B300) + 13*i + 1: pc(0xD2B300) + 13*i + 13]
    s = ''
    for x in b:
        if 0x80 <= x <= 0x99: s += chr(65 + x - 0x80)
        elif 0x9A <= x <= 0xB3: s += chr(97 + x - 0x9A)
        elif 0xB4 <= x <= 0xBD: s += chr(48 + x - 0xB4)
        elif x == 0xFF: s += ' '
        else: s += {0xBE:'!',0xBF:'?',0xC1:':',0xC3:"'",0xC4:'-',0xC5:'.',0xFE:' '}.get(x, '~')
    return s.strip()
# shops C4:7AC0 128 x 9
for s in range(128):
    rec = rom[pc(0xC47AC0) + 9*s: pc(0xC47AC0) + 9*s + 9]
    for it in rec[1:]:
        if it != 0xFF: use[it]['shop'] += 1
# treasure ED:82F4 ptrs (+ED8634), 5 bytes; type bit6 of byte3 = item
tp = [w16(pc(0xED82F4) + 2*i) for i in range(0x1A1)]
for m in range(0x1A0):
    for r in range(tp[m], tp[m+1], 5):
        a = pc(0xED8634) + r
        if rom[a+3] & 0x40: use[rom[a+4]]['chest'] += 1
# monster steal/drop CF:3000 384 x 4
for m in range(384):
    for k, kind in enumerate(('steal_rare', 'steal_common', 'drop_rare', 'drop_common')):
        it = rom[pc(0xCF3000) + 4*m + k]
        if it != 0xFF: use[it][kind] += 1
# metamorph C4:7F40 32 x 4
for g in range(32):
    for it in rom[pc(0xC47F40) + 4*g: pc(0xC47F40) + 4*g + 4]:
        if it != 0xFF: use[it]['metamorph'] += 1
# colosseum DF:B600 256 x 4 (index = wager item; byte2 = prize)
for i in range(256):
    rec = rom[pc(0xDFB600) + 4*i: pc(0xDFB600) + 4*i + 4]
    use[rec[2]]['colosseum_prize'] += 1
# starting equipment ED:7CA0, 22 bytes per char, offsets 15..20
for c in range(64):
    for off in range(15, 21):
        it = rom[pc(0xED7CA0) + 22*c + off]
        if it != 0xFF: use[it]['start_equip'] += 1
# event give/take item (names from ITEM enum)
enum = {}; n = -1
for l in open(os.path.join(DIS, 'src/common/const.inc')).read().split('.enum ITEM', 1)[1].split('.endenum')[0].splitlines():
    l = l.split(';=')[0] if ';=' in l else l
    m = re.match(r'\s+([A-Z0-9_]+)(\s*=\s*([A-Z0-9_]+))?', l)
    if not m: continue
    if m.group(3): enum[m.group(1)] = enum.get(m.group(3), 0); n = enum[m.group(1)]
    else: n += 1; enum[m.group(1)] = n
for l in open(os.path.join(DIS, 'src/event/event_main.asm')):
    m = re.search(r'\b(give_item|take_item)\s+([A-Z0-9_]+)', l.split(';')[0])
    if m and m.group(2) in enum: use[enum[m.group(2)]]['event_' + m.group(1)] += 1
rows = []
for i in range(256):
    u = dict(use[i]); tot = sum(u.values())
    rows.append({'id': f"{i:02X}", 'name': iname(i), 'refs': u, 'total_refs': tot})
res = {'sources': ['shop C4:7AC0', 'chest ED:82F4/ED:8634', 'steal/drop CF:3000', 'metamorph C4:7F40',
                   'colosseum prize DF:B600 (every item ID is also a wager index)', 'start equip ED:7CA0+15..20',
                   'event $80/$81 give/take'],
       'not_table_driven_yet': ['hard-coded ID compares in battle/menu ASM (Tools $A3-$AA, Throw, specials)',
                                'Colosseum wager index (all 256)', 'item data D8:5000 special-effect fields'],
       'rows': rows}
json.dump(res, open(out, 'w'), indent=1)
zero = [r for r in rows if r['total_refs'] == 0 and r['id'] != 'FF']
print('items with zero table/event refs:', len(zero))
for r in zero: print(' ', r['id'], r['name'])
