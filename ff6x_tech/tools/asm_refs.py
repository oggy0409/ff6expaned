import re,os,collections,json
pat=re.compile(r'\$(?:7e|00|0)?(1e[89a-f][0-9a-f]|1f[0-5][0-9a-f])\b',re.I)
refs=collections.defaultdict(list)
for root,_,fs in os.walk('src'):
    for f in fs:
        if not f.endswith(('.asm','.inc')): continue
        p=os.path.join(root,f)
        if p.startswith('src/event/'): continue
        for i,l in enumerate(open(p,errors='replace')):
            code=l.split(';')[0]
            for m in pat.finditer(code):
                refs[int(m.group(1),16)].append(f"{p}:{i+1}: {code.strip()}")
json.dump({hex(k):v for k,v in sorted(refs.items())},open('/home/claude/work/asm_eventbit_refs.json','w'),indent=1)
for k in sorted(refs): print(hex(k),len(refs[k]),refs[k][0][:110])
