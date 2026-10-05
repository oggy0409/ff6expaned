#!/usr/bin/env python3
"""TECH v0.7.3: before/after contact sheet from the screenshots of tools/emu_colosseum_visual.py.

usage: colosseum_visual_sheet.py <emu_colosseum_visual out dir> <sheet.png>
"""
import glob, os, sys
from PIL import Image, ImageDraw

ROWS = [
    ("BEFORE  v0.7.2 QA, opening party (Terra in Magitek / Wedge / Vicks)",
     ["A_v072qa_Terra_battle", "A_v072qa_Wedge_battle", "A_v072qa_Vicks_battle"]),
    ("SAME STATE on clean Rev 1 (vanilla CB:78D9)  +  Rev 1 Terra with only Magitek cleared",
     ["B_rev1_Terra_battle", "B_rev1_Wedge_battle", "B_rev1_Vicks_battle", "C_rev1_terra_no_magitek_battle"]),
    ("AFTER  v0.7.3 QA, normalized party (Terra / Locke / Celes / Edgar / Terra with QA Blade+Mail+Charm)",
     ["E_v073qa_E1_terra_thiefknife_win_battle", "E_v073qa_E2_locke_elixir_battle", "E_v073qa_E3_celes_fenixdown_battle",
      "E_v073qa_E4_edgar_thiefknife_win_battle", "E_v073qa_E5_terra_QAequipped_win_battle"]),
    ("REAL COLOSSEUM  production v0.7.2, map $19D receptionist (Terra / Locke / Celes)",
     ["F_prod_v072_F1_terra_elixir_battle", "F_prod_v072_F2_locke_fenixdown_battle", "F_prod_v072_F3_celes_thiefknife_battle"]),
]
W, H, TOP = 256, 224, 14
SHOT = "_battle_c"      # ~260 frames after the battle starts (fighter, opponent, Magitek armor sprite, effects)


def main(src, dst):
    sheet = Image.new("RGB", (5 * W, len(ROWS) * (H + TOP)), (16, 16, 24))
    d = ImageDraw.Draw(sheet)
    for r, (title, names) in enumerate(ROWS):
        y = r * (H + TOP)
        d.text((4, y + 1), title, fill=(255, 255, 160))
        for c, n in enumerate(names):
            f = [g for suffix in (SHOT, "_battle_b", "_battle")
                 for g in glob.glob(os.path.join(src, f"*_{n.replace('_battle', suffix)}.png"))]
            if f:
                sheet.paste(Image.open(f[0]).convert("RGB").resize((W, H)), (c * W, y + TOP))
    sheet.save(dst)
    print("written", dst)


if __name__ == "__main__":
    main(*sys.argv[1:3])
