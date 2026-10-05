#!/usr/bin/env python3
"""FF6 Expanded Edition - deterministic Rev 1 builder.

usage: python build.py <clean_rev1.sfc> [--target <name>|all] [--out DIR]

The master ROM is opened read-only and never written. Every build starts from
it, fails closed on hash mismatch, and emits ROM + IPS + BPS + manifests.
"""
import argparse, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ff6x import FRAMEWORK_VERSION
from ff6x.allocations import Allocations
from ff6x.hirom import pc_to_snes, fmt_snes
from ff6x.patchfmt import make_ips, apply_ips, make_bps, apply_bps
from ff6x.romimage import RomImage, load_clean_rom, sha1, crc32, md5, BuildError

BUILD_VERSION = "0.7.2"

TARGETS = {
    # ---- TECH v0.7.2 (current): v0.7.1 signature equipment bank + Colosseum QA-harness hotfix ----------
    "production":  {"file": f"FF6X_Rev1_TECH_v{BUILD_VERSION}_PRODUCTION", "version": BUILD_VERSION, "kind": "v07",
                    "packages": [], "monsters": [], "formations": [], "ext_item_sources": [],
                    "status": "PRODUCTION BRANCH v0.7.2 - accepted v0.6.1 foundation + extended item engine (ids $100-$13F, no item content)"},
    "celes-tech":  {"file": f"FF6X_Rev1_TECH_v{BUILD_VERSION}_CELES_TECH", "version": BUILD_VERSION, "kind": "v07",
                    "packages": ["celes_annex_tech"], "monsters": [], "formations": [], "ext_item_sources": [],
                    "status": "production v0.7.2 + accepted Celes Annex slice"},
    "item-tech":   {"file": f"FF6X_Rev1_TECH_v{BUILD_VERSION}_ITEM_BANK_QA", "version": BUILD_VERSION, "kind": "v07",
                    "packages": ["celes_annex_tech", "map_tech_v04", "qa_access_v071"],
                    "monsters": ["tech6_0180", "tech6_0181", "tech6_0182", "tech6_0183"],
                    "formations": ["tech6_0240", "tech6_0241", "tech61_0242", "tech61_0243"],
                    "qa_overrides": "formations/qa_v061.json", "qa_harness": True,
                    "ext_item_sources": ["items/qa_v071/qa_items.json"],
                    "formation_safety": "report",
                    "formation_safety_reason": "v0.6.1 QA formations carried unchanged for regression ($242 slot 0 known non-blocking)",
                    "status": "TECH v0.7.2 QA BUILD (v0.7.1 signature equipment bank proof + Colosseum QA-harness hotfix) - USER RUNTIME QA PENDING"},
    # ---- TECH v0.6.x frozen (accepted baselines, must reproduce exactly) ----------------------------
    "production-v0.6.0": {"file": "FF6X_Rev1_TECH_v0.6.0_PRODUCTION", "version": "0.6.0", "kind": "v06", "meta_target": "production",
                    "packages": [], "monsters": [], "formations": [],
                    "status": "TECH v0.6 production branch (engine of accepted v0.6.1) - regression rebuild",
                    "expect_sha1": "26ebd7d3b1a16bfae94625cead054edc34a1a5b6", "expect_crc32": "C9DB005B"},
    "celes-tech-v0.6.0": {"file": "FF6X_Rev1_TECH_v0.6.0_CELES_TECH", "version": "0.6.0", "kind": "v06", "meta_target": "celes-tech",
                    "packages": ["celes_annex_tech"], "monsters": [], "formations": [],
                    "status": "TECH v0.6 celes-tech - regression rebuild",
                    "expect_sha1": "a7ae5d4c1c49ce5cfcbca65de943678b86923fce", "expect_crc32": "E2BDA3B1"},
    "monster-tech-v0.6.1": {"file": "FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA", "version": "0.6.1", "kind": "v06", "meta_target": "monster-tech",
                    "packages": ["celes_annex_tech", "map_tech_v04", "qa_access_v061"],
                    "monsters": ["tech6_0180", "tech6_0181", "tech6_0182", "tech6_0183"],
                    "formations": ["tech6_0240", "tech6_0241", "tech61_0242", "tech61_0243"],
                    "qa_overrides": "formations/qa_v061.json",
                    "status": "ACCEPTED BASELINE TECH v0.6.1 (runtime verified QA build: enemy graphics routing, custom assets, Magic Points) - regression rebuild",
                    "qa_harness": True,
                    "expect_sha1": "8a55707ff2b4cd1364fdabf75e91422ba90ff8bb", "expect_crc32": "289BD3B9",
                    "formation_safety": "report",
                    "formation_safety_reason": "frozen accepted QA baseline; $242 slot 0 (x=8) is the known non-blocking placement issue that motivated the v0.6.2 rules"},
    "monster-tech-v0.6.0": {"file": "FF6X_Rev1_TECH_v0.6.0_ENEMY_ASSET_QA", "version": "0.6.0", "kind": "v06", "meta_target": "monster-tech",
                    "packages": ["celes_annex_tech", "map_tech_v04", "qa_access_v06"],
                    "monsters": ["tech6_0180", "tech6_0181", "tech6_0182", "tech6_0183"],
                    "formations": ["tech6_0240", "tech6_0241", "tech6_0242", "tech6_0243"],
                    "qa_overrides": "formations/qa_v06.json", "qa_harness": True, "formation_safety": "report",
                    "status": "TECH v0.6.0 QA build as user-tested (NOT accepted: isolation battles used formation $008 VRAM map 1, which the Magitek party's sprites overlap) - regression rebuild",
                    "expect_sha1": "14d179cfa61e720aa81ea9c4be518df1e13212fa", "expect_crc32": "F13B490B"},
    # ---- accepted baselines / regression (must reproduce exactly) ---------------------------
    "production-v0.5.0": {"file": "FF6X_Rev1_TECH_v0.5.0_PRODUCTION", "version": "0.5.0", "kind": "v05", "meta_target": "production",
                    "packages": [], "monsters": [], "formations": [],
                    "status": "TECH v0.5 production branch - regression rebuild",
                    "expect_sha1": "34ad5625ed08f791ca98ccde6a1dbf4ba4744cec", "expect_crc32": "844CC192"},
    "celes-tech-v0.5.0": {"file": "FF6X_Rev1_TECH_v0.5.0_CELES_TECH", "version": "0.5.0", "kind": "v05", "meta_target": "celes-tech",
                    "packages": ["celes_annex_tech"], "monsters": [], "formations": [],
                    "status": "TECH v0.5 celes-tech - regression rebuild",
                    "expect_sha1": "3805944217af91e7b360225d3e73dd2afdd714a7", "expect_crc32": "239DD0DF"},
    "monster-tech-v0.5.0": {"file": "FF6X_Rev1_TECH_v0.5.0_MONSTER_TECH_QA", "version": "0.5.0", "kind": "v05", "meta_target": "monster-tech",
                    "packages": ["celes_annex_tech", "map_tech_v04", "qa_access_v05"],
                    "monsters": ["tech_0180", "tech_0181"], "formations": ["tech_0240"],
                    "qa_overrides": "formations/qa_v05.json", "qa_harness": True,
                    "status": "ACCEPTED BASELINE TECH v0.5 (runtime verified QA build) - regression rebuild",
                    "expect_sha1": "416d5d9fbd88751e8fbd5ab4290dbb51fff3e69f", "expect_crc32": "381E6EE5"},
    "production-v0.4.0": {"file": "FF6X_Rev1_TECH_v0.4.0_PRODUCTION", "version": "0.4.0", "kind": "v04", "meta_target": "production",
                    "packages": [], "status": "TECH v0.4 production branch - regression rebuild",
                    "expect_sha1": "0181dbaa133b679e04bfa4fd7349292fc2e5f32a", "expect_crc32": "2EB2033F"},
    "celes-tech-v0.4.0": {"file": "FF6X_Rev1_TECH_v0.4.0_CELES_TECH", "version": "0.4.0", "kind": "v04", "meta_target": "celes-tech",
                    "packages": ["celes_annex_tech"], "status": "TECH v0.4 celes-tech - regression rebuild",
                    "expect_sha1": "51587eaef3837d797e05cc58b8f535f6369fb8c3", "expect_crc32": "B4E71558"},
    "map-tech-v0.4.0": {"file": "FF6X_Rev1_TECH_v0.4.0_MAP_TECH_QA", "version": "0.4.0", "kind": "v04", "meta_target": "map-tech",
                    "packages": ["celes_annex_tech", "map_tech_v04", "qa_access_v04"], "qa_harness": True,
                    "status": "ACCEPTED BASELINE TECH v0.4 (runtime verified QA build) - regression rebuild",
                    "expect_sha1": "e1d5387a819e3db87ce572d35ca51a5f5c91b6f1", "expect_crc32": "EE846BD5"},
    "celes-tech-v0.3.0": {"file": "FF6X_Rev1_TECH_v0.3.0_CELES_TECH", "version": "0.3.0", "kind": "v03", "meta_target": "celes-tech",
                    "status": "ACCEPTED BASELINE TECH v0.3 (runtime verified) - regression rebuild",
                    "expect_sha1": "e0196eb30fc03cf076c0d1306b0c09b664f7b2a4", "expect_crc32": "3E6B68E2"},
    "production-v0.3.0": {"file": "FF6X_Rev1_TECH_v0.3.0_PRODUCTION", "version": "0.3.0", "kind": "v03", "meta_target": "production",
                    "status": "TECH v0.3 production branch - regression rebuild",
                    "expect_sha1": "0eda0bab925f8b6f1c840c20523f9413cb586ec3", "expect_crc32": "8D05263F"},
    "celes-qa-v0.3.1": {"file": "FF6X_Rev1_TECH_v0.3.1_CELES_TECH_QA_ACCESS", "version": "0.3.1", "kind": "v03", "meta_target": "celes-qa",
                    "status": "QA HARNESS ONLY (v0.3.1) - regression rebuild", "qa_harness": True,
                    "expect_sha1": "bf443c85dc448c0a86169f58dce43d77684c36f5", "expect_crc32": "B982BC11"},
    "evtest":      {"file": "FF6X_Rev1_TECH_v0.2.0_EVTEST_REBUILD", "version": "0.2.0", "kind": "evtest",
                    "status": "REGRESSION ONLY - must equal accepted TECH v0.2",
                    "expect_sha1": "0258a0fc122bb109e7ca343dda61c58af2e921fb", "expect_crc32": "32725A65"},
    "legacy-v0.1": {"file": "FF6X_Rev1_TECH_v0.1_LEGACY_REBUILD", "version": "0.1", "kind": "legacy",
                    "status": "REGRESSION ONLY - must equal accepted TECH v0.1",
                    "expect_sha1": "c412f12938f9f4bd9c7e3f857572d3b773bab649",
                    "expect_crc32": "DA88A7DE"},
}

RESERVED_DIAGNOSTIC = ("reserved_out_of_range", "EXPANSION DIALOGUE ERROR:{n}ID OUT OF RANGE.")

EVTEST_MESSAGES = [
    RESERVED_DIAGNOSTIC,
    ("evtest_first", "TECH v0.2 EVENT TEST{n}This line is stored in bank F3.{n}Test event bit #255 is now ON."),
    ("evtest_again", "TECH v0.2 EVENT TEST{n}Test event bit #255 is still ON.{n}The flag state was kept."),
]


def build_target(clean, alloc, target):
    rom = RomImage(clean, alloc, target)
    notes = {}
    meta = TARGETS[target]
    kind = meta["kind"]
    if kind == "legacy":
        from patches import legacy_v01
        rom.expand()
        legacy_v01.build(rom)
    elif kind in ("v04", "v05", "v06", "v07"):
        from patches import core, map_v04
        rom.expand()
        core.p001_build_metadata(rom, meta.get("meta_target", target), meta["version"])
        notes.update(map_v04.build(rom, target, alloc, RESERVED_DIAGNOSTIC, packages=meta["packages"],
                                   ext_items=(kind == "v07")))
        if kind == "v05":
            from patches import monster_v05
            notes["monster_foundation"] = monster_v05.build(rom, target, alloc, meta)
        elif kind in ("v06", "v07"):
            from patches import monster_v05, enemy_v06
            prep = enemy_v06.prepare(rom, target, alloc, meta)
            notes["monster_foundation"] = monster_v05.build(rom, target, alloc, meta, gfx_override=prep.gfx_props)
            notes["enemy_foundation"] = enemy_v06.build(rom, target, alloc, meta, prep)
        if kind == "v07":
            from patches import item_v071
            notes["item_bank"] = item_v071.build(rom, target, alloc, meta)
    else:
        from patches import core, dialogue_hook
        rom.expand()
        core.p001_build_metadata(rom, meta.get("meta_target", target), meta["version"])
        if kind == "evtest":
            from patches import evtest
            table, count, ids = dialogue_hook.build_dialogue_table(rom, EVTEST_MESSAGES)
            notes["hook_listing"] = dialogue_hook.build_hook(rom, table, count)
            notes["event_listing"], _ = evtest.build(rom, ids)
            notes["dialogue_ids"] = {k: f"${v:04X}" for k, v in ids.items()}
        else:   # v0.3 regression targets (accepted code path, frozen)
            mt = meta["meta_target"]
            msgs = [RESERVED_DIAGNOSTIC]
            slice_ = mt in ("celes-tech", "celes-qa")
            if slice_:
                from patches import celes_tech
                msgs += celes_tech.messages()
            table, count, ids = dialogue_hook.build_dialogue_table(rom, msgs)
            notes["hook_listing"] = dialogue_hook.build_hook(rom, table, count)
            notes["dialogue_ids"] = {k: f"${v:04X}" for k, v in ids.items()}
            qa = None
            if mt == "celes-qa":            # QA HARNESS ONLY (never production)
                from patches import qa_access
                qa_ids = qa_access.add_dialogue(rom, count)
                notes["qa_dialogue_ids"] = {k: f"${v:04X}" for k, v in qa_ids.items()}
                qa = qa_access.make_qa(qa_ids, alloc.vanilla_ref_bits(target))
            if slice_:
                audit = json.load(open(os.path.join(HERE, "audits", "eventbit_audit.json")))
                bits = alloc.event_bits(target, audit)
                notes.update(celes_tech.build(rom, bits, ids, audit, qa=qa))
    chk = rom.fix_checksum()
    out = bytes(rom.buf)
    if kind in ("v06", "v07"):       # TECH v0.6.2 formation safety (layout + Magitek VRAM) on the built image; enforce = fail closed
        from ff6x import formation_safety
        paths = [os.path.join(HERE, "formations", f + ".json") for f in meta.get("formations", [])]
        rom.formation_safety = formation_safety.check_target(out, paths, meta.get("formation_safety", "enforce"))
    # independent checksum self-check
    if (sum(out) & 0xFFFF) != chk or (int.from_bytes(out[0xFFDC:0xFFDE], "little") ^ chk) != 0xFFFF:
        raise BuildError("checksum self-check failed")
    if out[0xFFD5] != 0x31 or out[0xFFD7] != 0x0C or out[0xFFDB] != 0x01:
        raise BuildError("header bytes changed unexpectedly")
    return rom, out, chk, notes


def write_outputs(clean, rom, out, chk, notes, target, outdir):
    meta = TARGETS[target]
    os.makedirs(outdir, exist_ok=True)
    base = os.path.join(outdir, meta["file"])
    ips, bps = make_ips(clean, out), make_bps(clean, out)
    if apply_ips(clean, ips) != out:
        raise BuildError("IPS round-trip failed")
    if apply_bps(clean, bps) != out:
        raise BuildError("BPS round-trip failed")
    ranges = rom.changed_ranges()
    with open(base + ".sfc", "wb") as f: f.write(out)
    with open(base + ".ips", "wb") as f: f.write(ips)
    with open(base + ".bps", "wb") as f: f.write(bps)
    ident = {"target": target, "status": meta["status"], "build_version": meta["version"],
             "framework_version": FRAMEWORK_VERSION, "size": len(out), "sha1": sha1(out), "crc32": crc32(out),
             "md5": md5(out), "snes_checksum": f"{chk:04X}", "snes_complement": f"{chk ^ 0xFFFF:04X}",
             "ips": {"file": os.path.basename(base + ".ips"), "sha1": sha1(ips)},
             "bps": {"file": os.path.basename(base + ".bps"), "sha1": sha1(bps)},
             "input": {"sha1": sha1(clean), "crc32": crc32(clean)},
             "static_pass": True, "qa_harness_only": bool(meta.get("qa_harness")), "runtime": {"legacy-v0.1": "VERIFIED (as TECH v0.1)", "evtest": "VERIFIED (as TECH v0.2)", "celes-tech-v0.3.0": "VERIFIED (TECH v0.3 accepted via v0.3.1 QA harness)", "celes-qa-v0.3.1": "VERIFIED (user QA of v0.3.1)", "map-tech-v0.4.0": "VERIFIED (TECH v0.4 accepted)", "celes-tech-v0.4.0": "VERIFIED via map-tech v0.4 QA", "production-v0.4.0": "engine of accepted v0.4", "monster-tech-v0.5.0": "VERIFIED (TECH v0.5 accepted)", "celes-tech-v0.5.0": "engine of accepted v0.5", "production-v0.5.0": "engine of accepted v0.5", "monster-tech-v0.6.1": "VERIFIED (TECH v0.6.1 accepted)", "production-v0.6.0": "engine of accepted v0.6.1", "celes-tech-v0.6.0": "engine of accepted v0.6.1 + accepted Annex slice", "monster-tech-v0.6.0": "NOT ACCEPTED (superseded by v0.6.1)"}.get(target, "PENDING USER QA")}
    diff = {"identity": ident,
            "patches": rom.records,
            "placements": [{"region": r, "label": l, "patch_id": p, "pc_start": f"{a:06X}", "pc_end": f"{b:06X}",
                            "snes_start": fmt_snes(pc_to_snes(a)), "snes_end": fmt_snes(pc_to_snes(b))}
                           for r, a, b, l, p in rom.placements],
            "changed_ranges_vs_expanded_baseline": [
                {"pc_start": f"{a:06X}", "pc_end": f"{b:06X}", "snes_start": fmt_snes(pc_to_snes(a)),
                 "snes_end": fmt_snes(pc_to_snes(b)), "length": b - a + 1,
                 "original": bytes(rom.baseline_byte(x) for x in range(a, b + 1)).hex(" ").upper() if b - a < 256 else "<long>",
                 "new": out[a:b + 1].hex(" ").upper() if b - a < 256 else "<long>", "owners": o}
                for a, b, o in ranges],
            "notes": notes}
    with open(base + ".manifest.json", "w") as f:
        json.dump(diff, f, indent=1, sort_keys=False)
    with open(base + ".diff.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pc_start", "pc_end", "snes_start", "snes_end", "length", "owners", "original", "new"])
        w.writerow(["300000", "3FFFFF", "F0:0000", "FF:FFFF", 0x100000, "P000_EXPAND_4MIB", "<absent>", "FF fill (baseline for rows below)"])
        for d in diff["changed_ranges_vs_expanded_baseline"]:
            w.writerow([d["pc_start"], d["pc_end"], d["snes_start"], d["snes_end"], d["length"],
                        ";".join(d["owners"]), d["original"], d["new"]])
    return ident


def write_formation_safety(out, rep, target, outdir):
    """<file>.formation_safety.json + formation_preview/<file>__F<id>.png (separate from the accepted manifests)."""
    from ff6x.formation_preview import render
    meta = TARGETS[target]
    os.makedirs(os.path.join(outdir, "formation_preview"), exist_ok=True)
    rep = dict(rep, target=target, mode_reason=meta.get("formation_safety_reason"))
    for r in rep["formations"]:
        png = os.path.join("formation_preview", f"{meta['file']}__F{r['formation']}.png")
        render(out, r, os.path.join(outdir, png))
        r["preview"] = png
    with open(os.path.join(outdir, meta["file"] + ".formation_safety.json"), "w") as f:
        json.dump(rep, f, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clean_rom")
    ap.add_argument("--target", default="all", choices=list(TARGETS) + ["all"])
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--preview-only", action="store_true",
                    help="build in memory, write only formation-safety reports + preview PNGs (no ROM/patch files)")
    a = ap.parse_args()
    with open(os.path.join(HERE, "data", "baseline.json")) as f:
        baseline = json.load(f)
    try:
        clean = load_clean_rom(a.clean_rom, baseline)
        alloc = Allocations(os.path.join(HERE, "data", "allocations.json"))
        targets = list(TARGETS) if a.target == "all" else [a.target]
        summary = []
        for t in targets:
            rom, out, chk, notes = build_target(clean, alloc, t)
            exp = TARGETS[t].get("expect_sha1")
            if exp and sha1(out) != exp:
                raise BuildError(f"{t}: SHA-1 {sha1(out)} != expected {exp}")
            fs_rep = getattr(rom, "formation_safety", None)
            if fs_rep is not None and fs_rep["formations"]:
                write_formation_safety(out, fs_rep, t, a.out)
            if a.preview_only:
                print(f"[{t}] formation safety: {len(fs_rep['formations']) if fs_rep else 0} formation(s), "
                      f"{fs_rep['errors'] if fs_rep else 0} error(s), {fs_rep['warnings'] if fs_rep else 0} warning(s) (preview only)")
                continue
            ident = write_outputs(clean, rom, out, chk, notes, t, a.out)
            summary.append(ident)
            print(f"[{t}] STATIC PASS  {TARGETS[t]['file']}.sfc")
            print(f"    SHA-1 {ident['sha1']}  CRC32 {ident['crc32']}  SNES checksum {ident['snes_checksum']}")
        if a.preview_only:
            return
        with open(os.path.join(a.out, "BUILD_SUMMARY.json"), "w") as f:
            json.dump(summary, f, indent=1)
    except (BuildError, ValueError, SystemExit) as e:
        print("BUILD FAILED:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
