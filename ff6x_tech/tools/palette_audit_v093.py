#!/usr/bin/env python3
"""TECH v0.9.3 palette audit: follows map $1A2's palette from the ROM to the PPU on bsnes (accurate PPU).
For the v0.9.2 and the v0.9.3 QA ROM (New Game, hub walk-in): map property byte 25 (palette index), RAM $0539, the field
palette buffers $7E7200 / $7E7400, the PPU CGRAM rows 0-7 (BG) and 8-15 (sprites) are compared with the palette table
entry in the ROM (relocated table F7:A000) and with the documented transform of that ROM's source file.
usage: palette_audit_v093.py <v0.9.2 qa.sfc> <v0.9.3 qa.sfc> <out json>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import emu_bsnes
emu_bsnes.use_bsnes()
from emu_item_tech import T
from emu_item_qa import boot_new_game
import emu_enablers_v092 as EN
from patches import celes_enablers_v092 as CE
ENGINE = {1, 2, 3} | set(range(121, 128))


def colours(b):
    return [b[2 * i] | b[2 * i + 1] << 8 for i in range(len(b) // 2)]


def run(qa, transform):
    rom = open(qa, "rb").read()
    clean = open(os.path.join(HERE, "..", "Final Fantasy III (USA) (Rev 1).sfc"), "rb").read()
    L = EN.evlabels(qa.replace(".sfc", ".manifest.json"))
    h = T(qa)
    boot_new_game(h)
    EN.hub(h, L, [1, 2, 2, 0]); h.step(600)
    idx = h.r8(0x0539)
    table = rom[0x37A000 + 256 * idx:0x37A000 + 256 * idx + 256]
    derived = CE.derive(clean[0x2DC480 + 256 * 0x18:0x2DC480 + 256 * 0x19], transform)
    buf1, buf2, cg = h.rbytes(0x7200, 256), h.rbytes(0x7400, 256), h.cgram()
    d = lambda a, b: [i for i in range(1, 128) if i not in ENGINE and i % 16 and a[2 * i:2 * i + 2] != b[2 * i:2 * i + 2]]
    def sat(b):
        v = []
        for c in colours(b)[1:128]:
            r, g, bl = c & 31, (c >> 5) & 31, (c >> 10) & 31
            if r + g + bl >= 24:
                v.append(max(r, g, bl) - min(r, g, bl))
        return round(sum(v) / len(v), 2)
    out = {"rom": os.path.basename(qa), "map": f"{h.r16(0x82):03X}", "ram_0539_palette_index": f"{idx:02X}",
           "table_entry_eq_documented_transform": table == derived,
           "buffer_7200_vs_table_diff": d(buf1, table), "buffer_7400_vs_table_diff": d(buf2, table),
           "cgram_bg_vs_table_diff": d(cg[:256], table),
           "engine_managed_colours": sorted(ENGINE),
           "lit_colour_saturation_5bit": {"palette": sat(table), "vanilla_18": sat(clean[0x2DC480 + 256 * 0x18:0x2DC480 + 256 * 0x19])},
           "transform": transform}
    h.close()
    return out


if __name__ == "__main__":
    q92, q93, out = sys.argv[1:4]
    t92 = json.load(open(os.path.join(HERE, "palettes", "v092", "palettes.json")))["map_palettes"][0]["transform"]
    t93 = json.load(open(os.path.join(HERE, "palettes", "v093", "palettes.json")))["map_palettes"][0]["transform"]
    rep = {"v0.9.2": run(q92, t92), "v0.9.3": run(q93, t93)}
    json.dump(rep, open(out, "w"), indent=1)
    print(json.dumps(rep, indent=1))
