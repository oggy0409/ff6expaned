#!/usr/bin/env python3
"""ART ASSET GATE v1.0 - runtime capture of map $1A2 on bsnes (accurate PPU), read-only.
For each E8 state (RESET / PRESERVE / BURN / GRAVES), from New Game (no preset) through the QA hub, as in the accepted
v0.9.3 visual suite: walk in (UP 13), then save
  <out>/<state>.png                     screenshot (256 x 224)
  <out>/<state>_vram.bin                VRAM 64 KiB
  <out>/<state>_cgram.bin               CGRAM 512 B
  <out>/<state>_tileset_wram.bin        WRAM $7F:C000-$7F:CFFF (tileset 1 / tileset 2 words as LoadTileset wrote them)
  <out>/<state>_bg1.bin                 BG1 map buffer $7F:0000, 32 rows x 32 tiles (row stride 256 in RAM)
  <out>/capture.json                    map id, player position, frame counters
Used by tools/art_gate_v10.py to verify every ROM-decoded export against the running game.
usage: FF6X_EMU=bsnes art_gate_capture_v10.py <qa.sfc> <out dir>
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import emu_bsnes
emu_bsnes.use_bsnes()
import numpy as np
from PIL import Image
from emu_item_tech import T
from emu_item_qa import boot_new_game
import emu_enablers_v092 as EN
from emu_celes_suite import walk, pos
from emu_visual_v093 import wait_idle

SEQ = (("reset", []), ("preserve", [[1, 2, 0, 1]]), ("burn", [[1, 2, 0, 0]]), ("graves", [[1, 2, 0, 1], [1, 2, 0, 2, 0]]))


def main(qa, out):
    os.makedirs(out, exist_ok=True)
    L = EN.evlabels(qa.replace(".sfc", ".manifest.json"))
    h = T(qa)
    boot_new_game(h)
    wait_idle(h)
    st0 = h.em.get_state()
    rep = {"rom": os.path.basename(qa), "emulator": "bsnes (accurate PPU)", "states": {}}
    for tag, picks in SEQ:
        h.em.set_state(st0); h.step(10)
        for p in picks:
            EN.hub(h, L, p)
        EN.hub(h, L, [1, 2, 2, 0])                  # Celes enablers -> More -> More -> Walk into the outer map
        h.step(500)
        walk(h, "UP", 13)
        h.step(60)
        img = np.asarray(h.em.get_screen()).copy()
        Image.fromarray(img).save(os.path.join(out, f"{tag}.png"))
        open(os.path.join(out, f"{tag}_vram.bin"), "wb").write(bytes(h.vram()))
        open(os.path.join(out, f"{tag}_cgram.bin"), "wb").write(bytes(h.cgram()))
        open(os.path.join(out, f"{tag}_tileset_wram.bin"), "wb").write(bytes(h.rbytes(0x1C000, 0x1000)))
        open(os.path.join(out, f"{tag}_bg1.bin"), "wb").write(
            bytes(h.r8(0x10000 + y * 256 + x) for y in range(32) for x in range(32)))
        rep["states"][tag] = {"map": f"{h.r16(0x82) & 0x1FF:03X}", "player_tile": list(pos(h)), "frame": h.f}
    h.close()
    json.dump(rep, open(os.path.join(out, "capture.json"), "w"), indent=1)
    print("CAPTURE", json.dumps(rep["states"]))


if __name__ == "__main__":
    main(*sys.argv[1:3])
