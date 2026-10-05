#!/usr/bin/env python3
"""DEV-ONLY (TECH v0.7.1): exact Rev 1 instruction index.

Needs the everything8215/ff6 disassembly built with `make ROM_VERSION=1` (it reassembles the clean Rev 1 ROM
byte-for-byte: SHA-1 057ADA1C...). Every source line that emitted bytes is resolved through the ld65 .dbg file to
its absolute Rev 1 SNES address; lines whose first token is a 65816 mnemonic are decoded from the CLEAN ROM bytes
(the operand width is taken from the span size, so M/X state is never guessed).

usage: rev1_insn_index.py <disassembly dir> <clean_rev1.sfc> <out.tsv>
columns: snes  bytes  mnemonic  mode  operand(hex)  file:line  source
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ff6x.op65816 import OPCODES

MN = {mn for mn, _ in OPCODES.values()}


def kv(s):
    return {k: v.strip('"') for k, v in re.findall(r'(\w+)=("[^"]*"|[^,]+)', s)}


def main(dis, rom_path, out):
    rom = open(rom_path, "rb").read()
    dbg = os.path.join(dis, "build/en/rom/ff6-en.dbg")
    seg, span, files, lines = {}, {}, {}, []
    for l in open(dbg):
        t, _, rest = l.rstrip("\n").partition("\t")
        if t == "seg":
            d = kv(rest); seg[int(d["id"])] = d
        elif t == "span":
            d = kv(rest); span[int(d["id"])] = (int(d["seg"]), int(d["start"]), int(d["size"]))
        elif t == "file":
            d = kv(rest); files[int(d["id"])] = d["name"]
        elif t == "line":
            d = kv(rest)
            if "span" in d and d.get("type", "0") in ("0", "2"):
                lines.append((int(d["file"]), int(d["line"]), [int(x) for x in d["span"].split("+")]))
    src = {}
    def text(fid, ln):
        if fid not in src:
            try: src[fid] = open(os.path.join(dis, files[fid].lstrip("./")), errors="replace").read().split("\n")
            except OSError: src[fid] = []
        s = src[fid]
        return s[ln - 1] if 0 < ln <= len(s) else ""
    rows = {}
    for fid, ln, sps in lines:
        t = text(fid, ln)
        code = re.sub(r";.*", "", t)
        code = re.sub(r"^\s*(@?\w+:|:)\s*", "", code).strip()
        tok = code.split()[0].upper() if code.split() else ""
        if tok not in MN:
            continue
        for sid in sps:
            sg, st, sz = span[sid]
            sgd = seg[sg]
            if "ooffs" not in sgd or int(sgd["start"], 16) < 0xC00000:
                continue
            base = int(sgd["start"], 16)
            snes = base + st
            pc = int(sgd["ooffs"]) + st
            b = rom[pc:pc + sz]
            if not b:
                continue
            mn, mode = OPCODES[b[0]]
            opnd = int.from_bytes(b[1:], "little") if len(b) > 1 else None
            rows[snes] = (snes, b.hex(" ").upper(), mn, mode, "" if opnd is None else f"{opnd:0{2 * (len(b) - 1)}X}",
                          f"{files[fid]}:{ln}", t.strip())
    with open(out, "w") as f:
        for k in sorted(rows):
            r = rows[k]
            f.write(f"{r[0] >> 16:02X}:{r[0] & 0xFFFF:04X}\t" + "\t".join(r[1:]) + "\n")
    print(f"{len(rows)} instructions indexed -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
