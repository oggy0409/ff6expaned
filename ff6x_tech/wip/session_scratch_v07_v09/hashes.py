import hashlib, zlib, os, sys
out, clean = sys.argv[1], sys.argv[2]
def h(p):
    d = open(p, "rb").read()
    return hashlib.sha1(d).hexdigest(), "%08X" % (zlib.crc32(d) & 0xFFFFFFFF), len(d)
s, c, _ = h(clean)
lines = ["# TECH v0.9 hashes (SHA-1, CRC32, size). Input: Final Fantasy III (USA) (Rev 1).sfc SHA-1 %s CRC32 %s" % (s, c)]
names = sorted(f for f in os.listdir(out) if "_v0.9_" in f and not f.endswith(".png"))
names += [f"FF6X_Rev1_TECH_v0.8_{t}.sfc" for t in ("PRODUCTION", "CELES_TECH", "EQUIPMENT_QA")]
names += ["DELTA_v0.8_to_v0.9.csv"]
for n in names:
    a, b, l = h(os.path.join(out, n)); lines.append(f"{a}  {b}  {l}  {n}")
print("\n".join(lines))
