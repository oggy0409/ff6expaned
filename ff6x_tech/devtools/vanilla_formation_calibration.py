#!/usr/bin/env python3
"""TECH v0.6.2 information only: run the formation-safety rules over all 576 VANILLA formations (never modified)
to calibrate the rules against the original game. -> audits/vanilla_formation_calibration_v062.json"""
import sys, os, json, collections
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, HERE)
import build
from ff6x.allocations import Allocations
from ff6x.romimage import load_clean_rom
from ff6x import formation_safety as FS
clean = load_clean_rom(sys.argv[1], json.load(open(os.path.join(HERE, "data", "baseline.json"))))
_, img, _, _ = build.build_target(clean, Allocations(os.path.join(HERE, "data", "allocations.json")), "production")
assert img[FS.FORM_PC:FS.FORM_PC + 576 * 15] == clean[0xF6200:0xF6200 + 576 * 15]
t = FS.load_vram_safety()
codes, per_f, slots_n = collections.Counter(), {}, 0
small_codes = collections.Counter()
for f in range(576):
    r = FS.check_formation(img, {"id": hex(f), "magitek_possible": True}, "report", t, path=f"vanilla ${f:03X}")
    slots_n += len(r["slots"])
    for i in r["issues"]:
        codes[i["code"]] += 1
    for s in r["slots"]:
        if not s["large"]:
            for i in r["issues"]:
                if i["msg"].startswith(f"slot {s['slot']} "): small_codes[i["code"]] += 1
    per_f[f"{f:03X}"] = {"status": r["status"], "vram_map": r["vram_map"], "issues": [i["code"] for i in r["issues"]]}
out = {"_comment": "information only - vanilla formations are not validated or changed by the builder; "
                   "Magitek conflicts are counted as if a Magitek party could meet every formation",
       "formations": 576, "slots": slots_n, "issue_counts_all": dict(sorted(codes.items())),
       "issue_counts_normal_size_sprites": dict(sorted(small_codes.items())), "per_formation": per_f}
json.dump(out, open(os.path.join(HERE, "audits", "vanilla_formation_calibration_v062.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "per_formation"}, indent=1))
