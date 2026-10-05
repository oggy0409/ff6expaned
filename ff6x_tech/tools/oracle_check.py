#!/usr/bin/env python3
"""DEV-ONLY: cross-check ff6x/eventasm.py encodings against the ca65 macros of the
Rev 1-verified everything8215/ff6 disassembly (needs cc65 + the disassembly).
usage: oracle_check.py <path-to-ff6-disassembly> <report.json>"""
import sys, os, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ff6x.eventasm import EventProgram
DIS, OUT = sys.argv[1], sys.argv[2]
CASES = [  # (project syntax, disassembly macro)
    ("dlg $0C0B", "dlg DLG_3083"),
    ("dlg $0001 bottom", "dlg DLG_1, BOTTOM"),
    ("if_switch B14A=1 -> R", "if_switch $014A=1, EventReturn"),
    ("if_switch B14A=0 -> R", "if_switch $014A=0, EventReturn"),
    ("set_switch B14A", "set_switch $014A"), ("clr_switch B14A", "clr_switch $014A"),
    ("set_switch N6F8", "set_switch $06F8"), ("clr_switch N6F9", "clr_switch $06F9"),
    ("call $CA5EA9", "call $ca5ea9"), ("choice R, R", "choice EventReturn, EventReturn"),
    ("battle 40", "battle 40"), ("give_item $E9", "give_item POTION"),
    ("hide_obj $11", "hide_obj NPC_2"), ("show_obj $10", "show_obj NPC_1"),
    ("load_map $0C7 16 27 UP", "load_map $0c7, {16, 27}, UP"),
    ("load_map $00C 15 47 DOWN Z_UPPER", "load_map $00c, {15, 47}, DOWN, {Z_UPPER}"),
    ("load_map $0C7 16 28 UP Z_UPPER NO_FADE_IN", "load_map $c7, {16, 28}, UP, {Z_UPPER, NO_FADE_IN}"),
    ("party_step DOWN 1", "obj_script SLOT_1\n move DOWN, 1\n end"),
    ("party_step UP 1", "obj_script SLOT_1\n move UP, 1\n end"),
    ("fade_in", "fade_in"), ("fade_out", "fade_out"), ("wait_fade", "wait_fade"), ("wait_15f", "wait_15f"),
    ("return", "return"),
]
HDR = "".join(f'.include "{f}"\n' for f in ["src/common/const.inc", "src/common/hardware.inc", "src/common/macros.inc",
      "src/event/event_cmd.mac", "src/sound/song_script.inc", "src/sound/sfx.inc", "src/gfx/map_sprite_gfx.inc",
      "src/gfx/map_sprite_pal.inc", "src/gfx/battle_bg.inc", "src/text/dlg.inc"])
body = '.segment "CODE"\nEventScript := $ca0000\nEventReturn := $ca5eb3\nDlg := $cd0000\n.scope OracleScope\nset_script_mode EVENT\n'
for _, m in CASES:
    body += m + "\n.byte $EE,$EE,$EE,$EE\n"
body += ".endscope\n"
d = tempfile.mkdtemp()
open(d + "/x.asm", "w").write(HDR + body)
open(d + "/x.cfg", "w").write("MEMORY { ROM: start=$0, size=$10000, fill=no; } SEGMENTS { CODE: load=ROM; }")
subprocess.run(["ca65", "-I", ".", "-I", "build/en", "-D", "LANG_EN=1", "-D", "ROM_VERSION=1", d + "/x.asm", "-o", d + "/x.o"], cwd=DIS, check=True)
subprocess.run(["ld65", "-C", d + "/x.cfg", "-o", d + "/x.bin", d + "/x.o"], check=True)
ref = open(d + "/x.bin", "rb").read().split(b"\xEE\xEE\xEE\xEE")[:-1]
rows, ok = [], True
for (src, mac), r in zip(CASES, ref):
    p = EventProgram(0xCA0000, {"B14A": 0x14A, "N6F8": 0x6F8, "N6F9": 0x6F9}, {}, {"R": 0xCA5EB3})
    p.parse(src); mine = p.assemble()
    same = mine == r
    ok &= same
    rows.append({"project": src, "macro": mac, "ca65": r.hex(" ").upper(), "eventasm": mine.hex(" ").upper(), "match": same})
json.dump({"all_match": ok, "cases": rows}, open(OUT, "w"), indent=1)
print("ORACLE", "PASS" if ok else "FAIL", f"{sum(r['match'] for r in rows)}/{len(rows)}")
