#!/usr/bin/env python3
"""TECH v0.6.2: run the formation-safety validator (enforce mode) on formations/examples/*.json.

Each example is compiled with the normal FormationSource compiler and written, in memory only, into a copy of the
production image at its own formation ID ($3F0-$3F6, inside the relocated 1024-entry formation table; never part
of any build target). Writes <out>/EXAMPLES_REPORT.json and one preview PNG per example.
usage: formation_safety_examples.py <clean_rev1.sfc> <out_dir>"""
import sys, os, json, glob
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import build
from ff6x.allocations import Allocations
from ff6x.romimage import load_clean_rom
from ff6x.monsters import FormationSource
from ff6x import formation_safety as FS
from ff6x.formation_preview import render


def run(clean, out_dir=None):
    alloc = Allocations(os.path.join(HERE, "data", "allocations.json"))
    _, img, _, _ = build.build_target(clean, alloc, "production")
    res = {}
    for p in sorted(glob.glob(os.path.join(HERE, "formations", "examples", "*.json"))):
        fs = FormationSource(p)
        rec, _aux = fs.compile(clean, set())
        a = FS.FORM_PC + 15 * fs.id
        im = img[:a] + rec + img[a + 15:]
        rep = FS.check_formation(im, fs.f, "enforce", path=p)
        name = os.path.basename(p)[:-5]
        if out_dir:
            render(im, rep, os.path.join(out_dir, name + ".png")); rep["preview"] = name + ".png"
        res[name] = rep
    return res


if __name__ == "__main__":
    base = json.load(open(os.path.join(HERE, "data", "baseline.json")))
    clean = load_clean_rom(sys.argv[1], base)
    os.makedirs(sys.argv[2], exist_ok=True)
    res = run(clean, sys.argv[2])
    json.dump(res, open(os.path.join(sys.argv[2], "EXAMPLES_REPORT.json"), "w"), indent=1)
    for k, r in res.items():
        print(k, r["status"], "map", r["vram_map"], r.get("suggested_vram_maps", ""), [i["code"] for i in r["issues"]])
