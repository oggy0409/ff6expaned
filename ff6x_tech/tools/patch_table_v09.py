#!/usr/bin/env python3
"""TECH v0.9: PATCH_TABLE_v0.9.md + out/DELTA_v0.8_to_v0.9.csv from the built ROMs and manifests.

usage: patch_table_v09.py <dir with the v0.8 + v0.9 ROMs / manifests> <out PATCH_TABLE md> <delta csv>
"""
import csv, hashlib, json, os, sys

V9 = {"production": "FF6X_Rev1_TECH_v0.9_PRODUCTION", "celes-tech": "FF6X_Rev1_TECH_v0.9_CELES_TECH",
      "item-tech": "FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA"}
V8 = {"production": "FF6X_Rev1_TECH_v0.8_PRODUCTION", "celes-tech": "FF6X_Rev1_TECH_v0.8_CELES_TECH",
      "item-tech": "FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA"}


def snes(pc):
    return f"{0xC0 + (pc >> 16):02X}:{pc & 0xFFFF:04X}"


def owner_map(man):
    """pc -> owning patch id (smallest covering record wins)"""
    recs = sorted(((int(r["pc_start"], 16), int(r["pc_end"], 16), r["patch_id"], r) for r in man["patches"]
                   if r["patch_id"] != "P000_EXPAND_4MIB"), key=lambda x: x[1] - x[0])
    return recs


def classify(pc, recs, tables):
    for a, b, pid, r in recs:
        if a <= pc <= b:
            if pid == "I101_ITEM_TABLES":
                for name, t in tables.items():
                    ts = (int(t["snes"].replace(":", ""), 16) & 0x3FFFFF)
                    if ts <= pc < ts + t["length"]:
                        return f"FA {name}"
            return pid
    if 0xFFDC <= pc <= 0xFFDF:
        return "checksum"
    return "?"


def main(d, out_md, out_csv):
    rows, summ = [], {}
    for k in ("production", "celes-tech", "item-tech"):
        a = open(os.path.join(d, V8[k] + ".sfc"), "rb").read()
        b = open(os.path.join(d, V9[k] + ".sfc"), "rb").read()
        man = json.load(open(os.path.join(d, V9[k] + ".manifest.json")))
        recs = owner_map(man)
        tables = man["notes"]["item_bank"]["tables"]
        cnt = {}
        for i in range(len(b)):
            if a[i] != b[i]:
                c = classify(i, recs, tables)
                cnt[c] = cnt.get(c, 0) + 1
                rows.append((k, f"{i:06X}", snes(i), f"{a[i]:02X}", f"{b[i]:02X}", c))
        summ[k] = cnt
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["target", "pc", "snes", "v0.8", "v0.9", "owner"]); w.writerows(rows)
    md = ["# TECH v0.9 — exact patch tables (generated from build manifests, `tools/patch_table_v09.py`)", "",
          "## Delta v0.8 → v0.9 (every changed byte: `out/DELTA_v0.8_to_v0.9.csv`)", ""]
    for k in summ:
        tot = sum(summ[k].values())
        md += [f"### {k}: {V8[k]} → {V9[k]} — **{tot} bytes**", "", "| bytes | owner |", "|---|---|"]
        for c, n in sorted(summ[k].items(), key=lambda x: -x[1]):
            md.append(f"| {n} | {c} |")
        md.append("")
    md += ["Owners: `I1xx` = v0.7.1 item engine records (tables, engine code, stub claims, retargets, hooks whose JSR/JMP "
           "operand moved with the re-assembled stubs), `V9xx` = TECH v0.9 hook sites (patches/item_v09_hooks.py), `Q7xx` "
           "= QA harness. Nothing outside the declared item regions, the v0.9 hook sites, the metadata and the checksum "
           "changes (selftest 48).", "",
           "## Full patch tables of the three v0.9 ROMs", "",
           "Long rows (>512 bytes) show length + SHA-1 of the new bytes; byte-exact data is in the `.manifest.json` / "
           "`.diff.csv` next to each ROM.", ""]
    for k, f in V9.items():
        man = json.load(open(os.path.join(d, f + ".manifest.json")))
        idt = man["identity"]
        md += [f"## {k} — `{f}.sfc`", "",
               f"SHA-1 `{idt['sha1']}` · CRC32 `{idt['crc32']}` · SNES checksum `{idt['snes_checksum']}` · status: {idt['status']}", "",
               "| ID | PC | SNES | Len | Original | New | Consumer / reason |", "|---|---|---|---|---|---|---|"]
        for r in man["patches"]:
            orig, new = r.get("expected_original", ""), r.get("new", "")
            if r["length"] > 512:
                orig = f"{r['length']} B" if orig else ""
                new = f"{r['length']} B sha1 {hashlib.sha1(new.encode()).hexdigest()[:12]}"
            elif len(new) > 60:
                new = new[:57] + " …"
                orig = orig[:57] + " …" if len(orig) > 60 else orig
            md.append(f"| {r['patch_id']} | {r['pc_start']}–{r['pc_end']} | {r['snes_start']}–{r['snes_end']} | {r['length']} | "
                      f"`{orig}` | `{new}` | {r['consumer']} — {r['reason']} |".replace("\n", " "))
        md.append("")
    open(out_md, "w").write("\n".join(md))
    print({k: sum(v.values()) for k, v in summ.items()})


if __name__ == "__main__":
    main(*sys.argv[1:4])
