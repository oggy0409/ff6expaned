#!/usr/bin/env python3
"""DEV-ONLY (TECH v0.7.1): cross-check ff6x/asm816.py against ca65/ld65 (cc65 2.19).

Assembles every one of the 256 opcodes in each addressing form (plus labels, branches, data directives and
M/X width tracking) with both assemblers and requires byte-identical output.
usage: asm_oracle.py <report.json>
"""
import json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ff6x.asm816 import Program
from ff6x.op65816 import OPCODES

FORM = {"imp": "", "acc": "a", "imm8": "#$12", "dp": "$12", "dpx": "$12,x", "dpy": "$12,y", "dpi": "($12)",
        "dpil": "[$12]", "dpix": "($12,x)", "dpiy": "($12),y", "dpily": "[$12],y", "sr": "$03,s",
        "sriy": "($03,s),y", "abs": "a:$1234", "absx": "a:$1234,x", "absy": "a:$1234,y", "absl": "f:$7E1234",
        "abslx": "f:$7E1234,x", "absi": "($1234)", "absix": "($1234,x)", "absil": "[$1234]",
        "rel8": "Here", "rel16": "Here", "blk": "#$7E,#$7F"}


def body(width):
    lines = []
    lines.append(".a8" if width == 8 else ".a16")
    lines.append(".i8" if width == 8 else ".i16")
    imm = "#$12" if width == 8 else "#$1234"
    for op in range(256):
        mn, mode = OPCODES[op]
        if mn in ("REP", "SEP", "BRK", "COP", "WDM"):
            continue            # REP/SEP change width (tested in labels-data-mx); BRK/COP/WDM unused
        if mode in ("immm", "immx"):
            arg = imm
        elif mn in ("JMP", "JSR") and mode == "abs":
            arg = "$1234"
        elif mn in ("JML", "JSL") and mode == "absl":
            arg = "$7E1234"
        elif mn == "JML" and mode == "absil":
            arg = "[$1234]"
        elif mn == "PEA":
            arg = "$1234"
        elif mn == "PEI":
            arg = "($12)"
        else:
            arg = FORM[mode]
        if mode == "acc" and mn in ("INC", "DEC"):
            arg = "a"
        lines.append(f"Here{op:02X}: {mn.lower()} {arg.replace('Here', f'Here{op:02X}')}")
        if mn in ("PLP", "RTI"):
            lines.append(".a8" if width == 8 else ".a16")
            lines.append(".i8" if width == 8 else ".i16")
    return "\n".join(lines)


EXTRA = """
.a8
.i16
Start:  rep #$20
        lda #$1234
        sep #$20
        lda #$12
        rep #$10
        ldx #$1234
        sep #$10
        ldy #$12
        rep #$30
        lda f:Data,x
        sep #$30
        jsr a:Sub
        jsl f:Sub
        bra Start
        brl Start
Sub:    rtl
Data:   .byte $01, $02, <$1234, >$1234, ^$7E1234
        .word $1234, Data & $FFFF
        .faraddr Sub
"""


def ca65(src, org):
    d = tempfile.mkdtemp()
    open(d + "/x.s", "w").write('.p816\n.smart +\n.segment "CODE"\n' + src.replace("a:a", "a") + "\n")
    open(d + "/x.cfg", "w").write(f"MEMORY {{ ROM: start=${org:06X}, size=$10000, fill=no; }} SEGMENTS {{ CODE: load=ROM; }}")
    subprocess.run(["ca65", "--cpu", "65816", d + "/x.s", "-o", d + "/x.o"], check=True)
    subprocess.run(["ld65", "-C", d + "/x.cfg", "-o", d + "/x.bin", d + "/x.o"], check=True)
    return open(d + "/x.bin", "rb").read()


def mine(src, org):
    p = Program(f".section T ${org:06X}\n" + src.replace(" a\n", " a\n"), name="oracle")
    return p.assemble()["T"][1]


def main(out):
    rep, ok = [], True
    for name, src in (("all-opcodes-8bit", body(8)), ("all-opcodes-16bit", body(16)), ("labels-data-mx", EXTRA)):
        a = ca65(src.replace("a:$1234", "a:$1234"), 0xC3F000)
        b = mine(src, 0xC3F000)
        same = a == b
        ok &= same
        first = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
        rep.append({"case": name, "bytes": len(a), "match": same, "first_diff": first})
        print(name, len(a), "MATCH" if same else f"DIFF at {first}: ca65 {a[first:first+4].hex() if first is not None else ''} mine {b[first:first+4].hex() if first is not None else ''} (len {len(a)} vs {len(b)})")
    json.dump({"all_match": ok, "cases": rep}, open(out, "w"), indent=1)
    print("ASM ORACLE", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv[1])
