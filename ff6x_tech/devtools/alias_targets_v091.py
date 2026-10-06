#!/usr/bin/env python3
"""TECH v0.9.1 one-shot manifest migration: the accepted v0.9 targets are frozen under new names
(production-v0.9 / celes-tech-v0.9 / item-tech-v0.9). Every allocation entry that lists the current
'production' / 'celes-tech' / 'item-tech' target also gets the frozen name, so the frozen builds keep
exactly the allocations they were accepted with (their SHA-1s are asserted by build.py).

Idempotent. usage: python3 devtools/alias_targets_v091.py data/allocations.json
"""
import json, sys

ALIAS = {"production": "production-v0.9", "celes-tech": "celes-tech-v0.9", "item-tech": "item-tech-v0.9"}


def walk(o, n):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "targets" and isinstance(v, list):
                for cur, frozen in ALIAS.items():
                    if cur in v and frozen not in v:
                        v.insert(v.index(cur) + 1, frozen)
                        n[0] += 1
            else:
                walk(v, n)
    elif isinstance(o, list):
        for x in o:
            walk(x, n)


def main(path):
    d = json.load(open(path))
    n = [0]
    walk(d, n)
    with open(path, "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print(f"{n[0]} target lists extended")


if __name__ == "__main__":
    main(sys.argv[1])
