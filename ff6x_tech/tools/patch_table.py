#!/usr/bin/env python3
"""Render exact PC/SNES patch tables (markdown) from build manifests."""
import sys, json
out = open(sys.argv[1], "w")
import os
out.write(f"# TECH {os.environ.get('TECH_VER', 'v0.3')} — exact patch tables (generated from build manifests)\n\n"
          "Long rows (>512 bytes) show length + SHA-1 of original/new; byte-exact data is in the `.manifest.json` "
          "and `.diff.csv` next to each ROM.\n")
for path in sys.argv[2:]:
    m = json.load(open(path)); i = m["identity"]
    out.write(f"\n## {i['target']} — `{path.split('/')[-1].replace('.manifest.json', '.sfc')}`\n\n"
              f"SHA-1 `{i['sha1']}` · CRC32 `{i['crc32']}` · SNES checksum `{i['snes_checksum']}` · "
              f"status: {i['status']}\n\n| ID | PC | SNES | Len | Original | New | Consumer / reason |\n|---|---|---|---|---|---|---|\n")
    for r in m["patches"]:
        orig = r.get("expected_original", "")
        new = r.get("new", "")
        clip = lambda s: s if len(s) <= 60 else s[:57] + "…"
        out.write(f"| {r['patch_id']} | {r['pc_start']}–{r['pc_end']} | {r['snes_start']}–{r['snes_end']} | {r['length']} "
                  f"| `{clip(orig)}` | `{clip(new)}` | {r.get('consumer','')} — {r.get('reason','')}"
                  + (f" (bytes changed: {r['bytes_changed']})" if r.get('bytes_changed') and r['length'] > 512 else "") + " |\n")
print("written", sys.argv[1])
