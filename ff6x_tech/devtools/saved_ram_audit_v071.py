#!/usr/bin/env python3
"""DEV-ONLY (TECH v0.7.1): evidence for SAVED_RAM_AUDIT_v0.7.1.md from the exact Rev 1 instruction index
(devtools/rev1_insn_index.py; everything8215/ff6 ROM_VERSION=1 is byte-identical to the clean ROM).

For each audited saved-RAM range it lists
  direct   - every instruction whose operand address lies inside the range (abs / abs,X / abs,Y / long / long,X
             in bank $7E or bank-less absolute; immediates excluded),
  indexed  - every indexed instruction whose base lies in the 256 bytes below the range start (a table that
             could be indexed into the range), for manual review,
  near     - block moves (MVN/MVP) and their source/destination banks (checked by hand: none target $1Cxx/$1Exx).
usage: saved_ram_audit_v071.py <insn.tsv> <out.json>"""
import json, sys

RANGES = {"EXT_BITS_AND_SIGNATURE": (0x1CF8, 0x1D27), "AUDITED_FREE": (0x1E1D, 0x1E3F)}
ADDR_MODES = {"abs", "absx", "absy", "absl", "abslx"}


def main(tsv, out):
    rows = [l.rstrip("\n").split("\t") for l in open(tsv)]
    res = {"_comment": __doc__.split("\n")[0], "ranges": {}}
    for name, (a, b) in RANGES.items():
        direct, indexed = [], []
        for f in rows:
            snes, by, mn, mode, opd = f[0], f[1], f[2], f[3], f[4]
            if mode not in ADDR_MODES or not opd:
                continue
            v = int(opd, 16)
            if mode in ("absl", "abslx"):
                if v >> 16 != 0x7E:
                    continue
                v &= 0xFFFF
            rec = {"snes": snes, "bytes": by, "insn": f"{mn} {mode} {opd}", "src": f"{f[5]} {f[6].strip()[:70]}"}
            if a <= v <= b:
                direct.append(rec)
            elif mode in ("absx", "absy", "abslx") and a - 0x100 <= v < a:
                indexed.append(rec)
        res["ranges"][name] = {"start": f"{a:04X}", "end": f"{b:04X}", "direct": direct, "indexed_below": indexed}
        print(name, "direct", len(direct), "indexed-below", len(indexed))
    res["block_moves"] = [{"snes": f[0], "bytes": f[1], "src": f"{f[5]} {f[6].strip()[:70]}"}
                          for f in rows if f[2] in ("MVN", "MVP")]
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:3])
