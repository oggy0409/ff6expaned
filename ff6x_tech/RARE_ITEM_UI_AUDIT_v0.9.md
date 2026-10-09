# RARE ITEM UI AUDIT — TECH v0.9

## 1. Data

* Names: `GetRareItemNamePtr` (C3:8436) immediates re-pointed to **`XRareName`** (FA:5100, 52 × 13 B; ids 0-19 byte
  copies of CE:FBA0). Names are 13 characters (the two-column layout: x = 3 and x = 17), space `$FE`, `$FF` padding.
* Descriptions: `InitRareItemDesc` (C3:8339) immediates re-pointed to **`XRareDescPtr`** (FA:5090, 52 absolute bank-FA
  pointers; ids 0-19 byte copies of the vanilla strings) with base 0 — `LoadBigText` reads `[ptrs + 2·id]` then the
  text at `[0 + ptr]`.
* Count: `CountRareItems` call (C3:834C) → `XC3_RareCount`: total owned over all pages (shown top right).

## 2. List and pages

* `GetRareItemList` (C3:838E call) → `XRareList`: walks rare ids 0-51 in order and writes the entries of page
  `XRAREPAGE` (20 per page) to 7E:9D89, `$FF` padding and the `$FF` terminator at 7E:9D9D (vanilla buffer size).
* Opening the list (C3:26A0) → page 0.
* Paging (C3:2748, `UpdateRareItemCursor` call → `XC3_RarePage`), only when another page exists:
  * **Down on the last row** → next page, cursor wraps to the first row (vanilla wrap);
  * **Up on the first row** → previous page, cursor on the last row;
  * **R / L** → next / previous page, cursor kept.
  Otherwise the vanilla cursor movement (and wrap) is unchanged.
* A page change redraws the list and **restarts the description task** (`BigTextTask` state 0: clear + redraw). The
  vanilla task is only reset by a held direction button; without the reset an L / R flip drew the new description
  over the old one (found in emulator testing, fixed).

## 3. Evidence (`tools/emu_rare_v09.py`)

R4a list with the 5 key items (+ Terra's vanilla Pendant), count 6 · R4a' the cursor selects each key item's rare id
for the description (screenshots `R4_desc_20..24`) · R4c 52 owned: count 52, page 0 ids 0-19, Down → page 1 (20-39),
R → page 2 (40-51), R on the last page stays, L → page 1, Up on the first row → page 0 last row (screenshots
`R4_page0`, `R4_page1_down`, `R4_page2_R`).

## 4. Not changed

The Item menu option row (USE / ARRANGE / RARE), the 2 × 10 cursor layout, vanilla names / descriptions of rare ids
0-19, the vanilla event bits.
