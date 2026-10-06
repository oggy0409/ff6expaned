import sys
def snes(pc): return f"{0xC0 + (pc >> 16):02X}:{pc & 0xFFFF:04X}" if pc < 0x400000 else f"{0x40 + (pc >> 16):02X}:{pc & 0xFFFF:04X}"
for kind in ("ITEM_BANK_QA", "PRODUCTION", "CELES_TECH"):
    a = open(f"{sys.argv[1]}/FF6X_Rev1_TECH_v0.7.1_{kind}.sfc", "rb").read()
    b = open(f"{sys.argv[2]}/FF6X_Rev1_TECH_v0.7.2_{kind}.sfc", "rb").read()
    assert len(a) == len(b)
    d = [i for i in range(len(a)) if a[i] != b[i]]
    runs = []
    for i in d:
        if runs and i <= runs[-1][1] + 4: runs[-1][1] = i
        else: runs.append([i, i])
    print(kind, len(d), "bytes in", len(runs), "runs")
    for s, e in runs:
        print(f"  PC {s:06X}-{e:06X}  SNES {snes(s)}  old {a[s:e+1][:24].hex(' ').upper()}  new {b[s:e+1][:24].hex(' ').upper()}")
