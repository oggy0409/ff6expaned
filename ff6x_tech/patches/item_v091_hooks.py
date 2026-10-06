"""TECH v0.9.1 hook table (same format as patches/item_v09_hooks.py): the vanilla bytes the v0.9.1 item data alignment
changes in addition to the v0.7.1 / v0.8 / v0.9 hooks. None of these sites overlaps an earlier hook (asserted by the
builder through the clean-byte check of every hook site).

  V9101  C2:13FA  ExecCmd command dispatch         item-action context cleared before every battle command
  V9102  C2:0BD3  CalcTargetDmg element test      fixed heal (Gaia Tonic 1500, Iron Ration 600) + hybrid Magitek Cell
  V9103  C3:8CD1  _c38ccd field HP / MP amount     fixed heal in the field menu
  V9104  C3:B836  _c3b82f shop buy maximum         per-item purchase cap (Magitek Cell: owned + bought <= 3)
  V9105  C3:B83E  _b83e   shop "too many" test     same cap
  V9106  C2:4418  MagicStatusEffect Vanish cancel  Vanish removal kept for Null Dust / Beacon Flare
Only extended consumables carry a fixed amount / hybrid element / cap; every vanilla item keeps its vanilla path.
"""
from patches.item_v09_hooks import H

HOOKS = [
    H("V9101_EXECCMD", "C213FA", "A5 B5 0A AA", "jsl XJ_ExecCmd", "ExecCmd C2:13D3 (LDA $B5 / ASL / TAX)",
      "TECH v0.9.1: the item-action context (XFIXAMT / XHYBEL / XVANOK) is cleared before EVERY battle command "
      "(v0.9 XB_Dispatch only sees AI-translated commands)", mode=".a8\n.i8"),
    H("V9102_ELEM_TEST", "C20BD3", "AD A1 11", "jsr XC2_ElemA", "CalcTargetDmg C2:0BD3 (LDA $11A1 element test)",
      "TECH v0.9.1: extended-consumable fixed heal / hybrid split applied to $F0 before the element block "
      "(hybrid: vanilla element block skipped, A = 0)", mode=".a8\n.i8"),
    H("V9103_FIELD_AMOUNT", "C38CD1", "85 B2 64 B3", "jsl XJ_FixPow", "_c38ccd C3:8CCD (field HP / MP amount)",
      "TECH v0.9.1: zb2 = power, or the fixed HP amount of an extended consumable"),
    H("V9104_SHOP_MAX", "C3B836", "A9 63 38", "jsr XC3_ShopCap", "_c3b82f C3:B82F (buy quantity maximum)",
      "TECH v0.9.1: purchase cap of the current shop entry (XShopCap; vanilla 99)"),
    H("V9105_SHOP_TOOMANY", "C3B83E", "A5 69 C9 63", "jsr XC3_ShopTooMany", "_b83e C3:B83E (too many test)",
      "TECH v0.9.1: owned >= cap of the current shop entry -> 'too many'", pad=True),
    H("V9106_VANISH_RM", "C24418", "A5 B3 30 04 A9 10 14 F4", "jsr XC2_VanTrb", "MagicStatusEffect C2:4406",
      "TECH v0.9.1: an extended consumable whose record removes Vanish (Null Dust, Beacon Flare) keeps that removal "
      "(vanilla items: unchanged)", mode=".a8\n.i16", pad=True),
]
