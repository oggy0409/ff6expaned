#!/usr/bin/env python3
"""TECH v0.9 handoff verification: rebuild every target from this workspace and check the accepted baseline.

usage: handoff_verify_v09.py <clean Rev 1 .sfc> <empty output dir> [packaged out/ dir to compare against]

1. clean input = SHA-1 057ADA1C... / CRC32 C0FA0464 (the builder also refuses anything else)
2. `build.py --target all` into <output dir> (the builder asserts every pinned SHA-1, v0.1 ... v0.9)
3. the three accepted v0.9 ROMs have exactly the accepted SHA-1 / CRC32
4. their BPS and IPS applied to the clean ROM give the same bytes
5. optional: every v0.9 file in the packaged out/ dir is byte-identical to the rebuild
Prints one line per check and exits 1 on any failure. Stdlib only.
"""
import hashlib, os, subprocess, sys, zlib

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from ff6x.patchfmt import apply_bps, apply_ips  # noqa: E402

CLEAN = ("057ada1c641e3e0b3ca34e6e4f4eb1b05a87143a", "C0FA0464")
ACCEPTED = {  # TECH v0.9 - ACCEPTED / USER RUNTIME QA PASS
    "FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA": ("e1136805cc792e11dbffab15e87df0f327a6a12e", "D8183069"),
    "FF6X_Rev1_TECH_v0.9_PRODUCTION": ("99cd74dfac5b91756120992dd1560534b40c66c3", "FF753A76"),
    "FF6X_Rev1_TECH_v0.9_CELES_TECH": ("e4c0703189fbde9b2df4ca972bfc801778aa6899", "3067CF9B"),
}


def ident(b):
    return hashlib.sha1(b).hexdigest(), "%08X" % (zlib.crc32(b) & 0xFFFFFFFF)


def main(clean_path, out, packaged=None):
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(("PASS " if cond else "FAIL ") + name + (f"  {detail}" if detail else ""))

    clean = open(clean_path, "rb").read()
    check("clean Rev 1 input", ident(clean) == CLEAN, "%s %s" % ident(clean))
    os.makedirs(out, exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, "build.py"), clean_path, "--target", "all", "--out", out],
                       capture_output=True, text=True)
    open(os.path.join(out, "build_log.txt"), "w").write(r.stdout + r.stderr)
    n = r.stdout.count("STATIC PASS")
    check("build.py --target all (pinned SHA-1s asserted by the builder)", r.returncode == 0, f"{n} targets STATIC PASS")
    for base, exp in ACCEPTED.items():
        p = os.path.join(out, base + ".sfc")
        rom = open(p, "rb").read() if os.path.exists(p) else b""
        check(f"{base}.sfc accepted hash", ident(rom) == exp, "%s %s" % ident(rom))
        check(f"{base}.bps -> clean = ROM", rom and apply_bps(clean, open(p[:-4] + ".bps", "rb").read()) == rom)
        check(f"{base}.ips -> clean = ROM", rom and apply_ips(clean, open(p[:-4] + ".ips", "rb").read()) == rom)
        if packaged:
            for f in sorted(os.listdir(packaged)):
                if f.startswith(base + "."):
                    a = open(os.path.join(packaged, f), "rb").read()
                    b = open(os.path.join(out, f), "rb").read() if os.path.exists(os.path.join(out, f)) else None
                    check(f"packaged out/{f} == rebuild", a == b)
    print("HANDOFF VERIFY " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:4]))
