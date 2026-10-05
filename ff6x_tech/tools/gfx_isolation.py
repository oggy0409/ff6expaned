#!/usr/bin/env python3
"""TECH v0.6 Phase A - TESTMOB B (Dark Wind graphics) isolation, Claude-side EMULATOR evidence.

Same start RAM state; battle injected with $11E0 = formation (as tools/emu_monster_diff.py):
  vanilla Rev 1 formation $008 (2 Leafer + 2 Dark Wind)       = reference
  QA ROM formation $242 ($008 with slot 5 = $182 exact clone)  = A1
  QA ROM formation $243 ($008 with slot 5 = $183 Vulture pal)  = A2
Records, per battle: monster IDs, per-slot palette numbers ($8117), loaded palettes ($8123),
per-slot sprite size ($812F), decoded 4bpp tile data of slots 4/5 from the btlgfx graphics
buffer (7E:AE3F, VRAM map 1 boxes (8,8) and (12,8)), and the CGRAM-source palette bytes.
Renders each slot-5 sprite from (tile buffer + palette bytes) to PNG and a side-by-side sheet.
usage: gfx_isolation.py <vanilla.sfc> <qa.sfc> <state> <outdir>   (runs each ROM in a subprocess)"""
import sys, os, json, hashlib, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def worker(rom, state, forms, out):
    from emu_harness import H
    import emu_monster_diff as MD
    import numpy as np
    from PIL import Image
    h = H(rom); snap = open(state, "rb").read()
    res = {}
    def m(a, n):
        h.gd.update_ram(); return bytes(h.gd.memory.extract(0x7E0000 + a + i, '|u1') for i in range(n))
    romb = open(rom, "rb").read()
    for f in forms:
        MD.run_one(h, snap, f)
        h.step(20)
        buf = m(0xAE3F, 0x2000)
        box = lambda x, y: b"".join(buf[x * 0x20 + (y + r) * 0x200: x * 0x20 + (y + r) * 0x200 + 4 * 0x20] for r in range(4))
        pals = [h.r16(0x8117 + 2 * k) for k in range(6)]
        # palette source: vanilla MonsterPal D2:7820 (vanilla ROM) or relocated FB:0000 (v0.6) - read from the ROM image
        palbase = 0x127820 if romb[0x01233E:0x012341] == bytes.fromhex("20 78 D2") else 0x3B0000
        def palbytes(p): return romb[palbase + 16 * p: palbase + 16 * p + 32]
        r = {"ids": [f"{h.r16(0x2001 + 2 * k):04X}" for k in range(6)], "pal_per_slot": [f"{p:04X}" for p in pals],
             "loaded_pals": [f"{h.r16(0x8123 + 2 * k):04X}" for k in range(3)],
             "size_cols_rows": {s: list(m(0x812F + 2 * s, 2)) for s in (4, 5)}}
        for s, (x, y) in ((4, (8, 8)), (5, (12, 8))):
            t = box(x, y)
            r[f"slot{s}_tiles_sha1"] = hashlib.sha1(t).hexdigest()
            pb = palbytes(pals[s])
            r[f"slot{s}_palette"] = pb.hex(" ").upper()
            img = np.zeros((32, 32, 3), np.uint8); used = set()
            for ty in range(4):
                for tx in range(4):
                    tile = t[(ty * 4 + tx) * 32:(ty * 4 + tx + 1) * 32]
                    for yy in range(8):
                        for xx in range(8):
                            b = 7 - xx
                            v = ((tile[2 * yy] >> b) & 1) | (((tile[2 * yy + 1] >> b) & 1) << 1) | \
                                (((tile[16 + 2 * yy] >> b) & 1) << 2) | (((tile[17 + 2 * yy] >> b) & 1) << 3)
                            used.add(v)
                            if v:
                                c = pb[2 * v] | pb[2 * v + 1] << 8
                                img[ty * 8 + yy, tx * 8 + xx] = [(c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3]
                            else:
                                img[ty * 8 + yy, tx * 8 + xx] = [64, 64, 96]
            r[f"slot{s}_colour_indices_used"] = sorted(used)
            Image.fromarray(img).resize((128, 128), Image.NEAREST).save(os.path.join(out, f"sprite_{os.path.basename(rom)[:12]}_{f:03X}_slot{s}.png"))
        h.step(580)
        Image.fromarray(h.em.get_screen()).resize((512, 448), Image.NEAREST).save(os.path.join(out, f"battle_{os.path.basename(rom)[:12]}_{f:03X}.png"))
        res[f"{f:03X}"] = r
    json.dump(res, open(os.path.join(out, f"iso_{os.path.basename(rom)[:12]}.json"), "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "--worker":
        worker(sys.argv[2], sys.argv[3], [int(x, 16) for x in sys.argv[4].split(",")], sys.argv[5]); sys.exit(0)
    van, qa, state, out = sys.argv[1:5]
    os.makedirs(out, exist_ok=True)
    for rom, forms in ((van, "008"), (qa, "008,242,243")):
        subprocess.check_call([sys.executable, __file__, "--worker", rom, state, forms, out])
    V = json.load(open(os.path.join(out, f"iso_{os.path.basename(van)[:12]}.json")))["008"]
    Q = json.load(open(os.path.join(out, f"iso_{os.path.basename(qa)[:12]}.json")))
    rep = {
        "A1_exact_clone": {
            "tiles_identical_to_vanilla_dark_wind": Q["242"]["slot5_tiles_sha1"] == V["slot5_tiles_sha1"] == V["slot4_tiles_sha1"],
            "palette_number_identical": Q["242"]["pal_per_slot"][5] == V["pal_per_slot"][5] == "0046",
            "palette_bytes_identical": Q["242"]["slot5_palette"] == V["slot5_palette"],
            "size_identical": Q["242"]["size_cols_rows"]["5"] == V["size_cols_rows"]["5"]},
        "A2_vulture_palette": {
            "tiles_identical_to_vanilla_dark_wind": Q["243"]["slot5_tiles_sha1"] == V["slot5_tiles_sha1"],
            "size_identical": Q["243"]["size_cols_rows"]["5"] == V["size_cols_rows"]["5"],
            "palette_number": Q["243"]["pal_per_slot"][5], "palette_bytes": Q["243"]["slot5_palette"]},
        "vanilla_008_in_v06_rom_identical": Q["008"] == V,
        "battle_screen_vs_vanilla_008_after_600f": {},
        "dark_wind_colour_indices_used": V["slot5_colour_indices_used"],
    }
    from PIL import Image, ImageChops
    tag_v0, tag_q0 = os.path.basename(van)[:12], os.path.basename(qa)[:12]
    ref = Image.open(os.path.join(out, f"battle_{tag_v0}_008.png")).convert("RGB")
    for f in ("008", "242", "243"):
        bb = ImageChops.difference(ref, Image.open(os.path.join(out, f"battle_{tag_q0}_{f}.png")).convert("RGB")).getbbox()
        rep["battle_screen_vs_vanilla_008_after_600f"][f] = "pixel-identical" if bb is None else f"differs only in box {[v // 2 for v in bb]} (256x224 coords)"
    json.dump({"report": rep, "vanilla": V, "qa": Q}, open(os.path.join(out, "GFX_ISOLATION_RESULT.json"), "w"), indent=1)
    from PIL import Image, ImageDraw
    tag_v, tag_q = os.path.basename(van)[:12], os.path.basename(qa)[:12]
    ims = [(f"vanilla Dark Wind (pal 046)", f"sprite_{tag_v}_008_slot5.png"), ("A1 clone $182 (pal 046)", f"sprite_{tag_q}_242_slot5.png"),
           ("A2 $183 Vulture pal 04A", f"sprite_{tag_q}_243_slot5.png")]
    W = Image.new("RGB", (3 * 150, 160), (30, 30, 40)); d = ImageDraw.Draw(W)
    for i, (t, p) in enumerate(ims):
        W.paste(Image.open(os.path.join(out, p)), (i * 150 + 11, 24)); d.text((i * 150 + 4, 6), t, fill=(255, 255, 255))
    W.save(os.path.join(out, "GFX_ISOLATION_SHEET.png"))
    print(json.dumps(rep, indent=1))
