"""Dev-only: resolve symbol references in the everything8215 ff6 disassembly
(ca65 .dbg) to absolute SNES addresses. Not used by the builder."""
import re, sys, collections
def kv(s):
    d = {}
    for part in re.findall(r'(\w+)=("[^"]*"|[^,]+)', s):
        d[part[0]] = part[1].strip('"')
    return d
class Dbg:
    def __init__(self, path):
        self.seg, self.span, self.line, self.file, self.sym = {}, {}, {}, {}, {}
        self.syms_by_name = collections.defaultdict(list)
        for l in open(path):
            t, _, rest = l.rstrip('\n').partition('\t')
            if t not in ('seg', 'span', 'line', 'file', 'sym'): continue
            d = kv(rest); i = int(d['id'])
            getattr(self, t)[i] = d
            if t == 'sym': self.syms_by_name[d['name']].append(d)
    def addr_of_span(self, sid):
        sp = self.span[sid]; sg = self.seg[int(sp['seg'])]
        return int(sg['start'], 16) + int(sp['start']), int(sp['size'])
    def line_addrs(self, lid):
        ln = self.line[lid]
        if 'span' not in ln: return []
        return [self.addr_of_span(int(s)) for s in ln['span'].split('+')]
    def line_src(self, lid):
        ln = self.line[lid]; f = self.file[int(ln['file'])]['name']
        try: txt = open('/home/claude/work/ff6dis/' + f.lstrip('./'), errors='replace').read().split('\n')[int(ln['line']) - 1]
        except Exception: txt = '?'
        return f, int(ln['line']), txt.strip()
    def seg_syms(self, segname):
        sid = [k for k, v in self.seg.items() if v['name'] == segname][0]
        return [s for s in self.sym.values() if s.get('seg') == str(sid) and s.get('type') == 'lab']
    def refs(self, name):
        out = []
        for s in self.syms_by_name[name]:
            for r in s.get('ref', '').split('+'):
                if r: out.append(int(r))
        return sorted(set(out))
