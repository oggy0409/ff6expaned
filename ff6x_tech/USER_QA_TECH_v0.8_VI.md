# FFVI Expanded Edition — TECH v0.8 Signature Equipment (39 món) — User QA (Tiếng Việt, ~20–30 phút)

Một lượt QA duy nhất cho toàn bộ 39 món trang bị `$100-$126`. Emulator phía Claude đã chạy hết (xem
`REGRESSION_REPORT_v0.8.md`); bước này là **USER RUNTIME QA** trên emulator/phần cứng của bạn.

## ROM
| ROM | SHA-1 | CRC32 | Dùng cho |
|---|---|---|---|
| `FF6X_Rev1_TECH_v0.8_EQUIPMENT_QA.sfc` | `498d62c47477a91d6df7b4619f76bb03e7a1fbb5` | `4A8A7533` | **toàn bộ checklist bên dưới** |
| `FF6X_Rev1_TECH_v0.8_PRODUCTION.sfc` | `1091d0779c5278f40c6e74648dbfb8cb2ce6818b` | `2F5FB45A` | bước 10 (tùy chọn) |

Hoặc patch `.bps` tương ứng lên ROM Rev 1 sạch (CRC32 `C0FA0464`).

## Cách vào menu QA
New Game → Narshe: ô QA (**lên 6, trái 4**) → `TECH v0.8 QA ACCESS` → `Equipment v0.8 (39 items)`:
* `Grant all 39` — nhận 39 món (mỗi món 1 cái).
* `Party presets` — đội test (Terra luôn dẫn đầu, đã ra khỏi Magitek):
  P1 Terra/Locke/Celes/Edgar · P2 Terra/Sabin/Cyan/Shadow · `More…` P3 Terra/Setzer/Strago/Relm ·
  P4 Terra/Mog/Gau/Gogo · `More…` P5 Terra/Umaro/Celes/Locke · `Opening party (Magitek)` (trả lại đội mở đầu).
* `By type / Remove / Smith` → `Grant by type` (13 vũ khí / 13 giáp-mũ-khiên / 13 relic) · `Remove all 39 (inventory)` ·
  `More…` → `Test battle (guards)` · `Boss battle (Whelk)` · `Smith purchase demo`.

Lưu ý: tên hiển thị tối đa **12 ký tự** (giới hạn của game gốc). 18 tên dài được rút gọn có chủ đích (vd.
`TemperedEdge`, `ImperialSabr`, `LegacyofMagi`); tên đầy đủ nằm ở dòng mô tả (xem `KNOWN_RISKS_v0.8.md` R21).

## Checklist
| # | Làm | PASS khi |
|---|---|---|
| 1 | `Grant all 39` → mở **Item** | 39 món mới, mỗi món đúng tên + icon; **không** có tên vanilla lạ (Dirk, MithrilKnife, Chocobo Brsh…) thay vào; mô tả 2 dòng đọc được. Bấm thử mô tả của 5–6 món |
| 2 | `Party presets` → P1. **Equip** Terra: `Leo's Blade` + `Concord Shld` + `ChildsRibbon` + `MagisterRobe`; **Relic**: `MaduinLocket` + `LegacyofMagi` | Bat.Pwr / Defense / Mag.Pwr / MBlock… đổi theo `EQUIPMENT_MASTER_TABLE_v0.8.md`; tên đúng trong ô trang bị |
| 3 | P1: Locke `Raider Knife` + `FalconJacket` + `MemorialBand` + `Gale Pin`; Celes `ImperialSabr` + `Ashguard` + `Magi Circlet` + `ImperialMntl` + `Runic Crest`; Edgar `Gale Lance` + `Eng. Goggles` + `Royal Gear` + `Eng. Badge` | mặc được hết; món đã mặc biến khỏi Item, món khác vẫn còn |
| 4 | Ma trận (kiểm tra nhanh): Locke **không** thấy `Doma Edge`; P2 → Cyan thấy `Doma Edge` / `Doma Kabuto` / `Doma Crest`; P3 → Relm thấy `ConcordBrush` / `PaintersLens`; P4 → Gau / Umaro (P5) **không** thấy vũ khí/khiên mới | đúng như `EQUIP_MATRIX_v0.8.csv` |
| 5 | Đội P1 (bước 2–3) → `Test battle (guards)` → Fight bằng cả 4 người | đòn đánh có hình vũ khí bình thường (giống vũ khí mẫu: Excalibur, ThiefKnife, Enhancer, Aura Lance), **không** đánh tay không, **không** ra hình cọ vẽ (Brush); thắng → về Narshe, sáng màn hình, điều khiển được |
| 6 | Sau trận: Equip của 4 người | vẫn đúng các món đã mặc; Item không mất / không nhân đôi |
| 7 | `Boss battle (Whelk)` với đội P1 | vào trận, đánh được, về lại field; trang bị không đổi |
| 8 | **Equip → Optimum** (Terra) rồi **Empty**; **Item → Arrange** | Optimum chọn món **mạnh nhất** Terra mặc được ở mỗi ô (Bat.Pwr/Defense cao nhất — đã sửa lỗi xếp hạng ở v0.8), không nhân đôi/mất món; danh sách Equip xếp từ mạnh đến yếu; Empty trả các món về Item với **đúng tên**; Arrange giữ nguyên 39 món + số lượng |
| 9 | **Save** (ô Save Point/menu QA) → **Reset** → **Continue** | toàn bộ món trong Item và trên người giữ nguyên |
| 10 | (tùy chọn) mở save bước 9 bằng ROM **PRODUCTION** | mọi món `$100-$126` giữ nguyên (cả đang mặc) |
| 11 | `Older tests` → `Item bank tests (v0.7.1)` → `Shop / Colosseum / Battle` → `Shop 48` → **Sell** | các món mới **không** chọn bán được (không thể bán), Item không đổi |
| 12 | Như trên → `Colosseum (full battle)` → `Get wager kit` → `Fight` (đội preset, Terra đang mặc đồ mới) | danh sách cược **không** cho chọn món mới; trận Colosseum chạy, về lại Narshe; trang bị giữ nguyên |
| 13 | `Smith purchase demo`: `Buy TemperedEdge` khi chưa đủ GP | "you need 18000 GP", không mất GP |
| 14 | `Get 20000 GP (QA)` → `Buy` (nếu đã có Tempered Edge thì `Remove all 39` trước và tháo nó ra) | nhận đúng 1 `TemperedEdge`, trừ 18000 GP; mua lần nữa → "already own", không trừ GP |
| 15 | `Remove all 39 (inventory)` | các món mới trong Item biến mất (món đang mặc vẫn ở trên người) |
| 16 | (tùy chọn) Genji Glove / Gauntlet / Offering / Dragoon Boots nếu bạn có save sau | vũ khí mới dùng 2 tay / đánh 4 lần / Jump bình thường; **sau khi đổi relic Genji/Gauntlet, xem lại 2 tay** (game gốc tự sắp xếp lại tay khi rời menu Relic) |

Relic có hiệu ứng ASM đặc biệt (Runic Crest, Maduin's Locket, Doma Crest, Darill's Coin, Beastheart, Engineer's Badge,
Master's Cord) **chỉ có chỉ số** ở v0.8 (BAL-18 fallback, `FALLBACK_EFFECTS_v0.8.md`) — không phải lỗi.

---
Báo PASS mẫu: `TECH v0.8 PASS — 1–15 OK (39 names/icons/desc, equip+stats, matrix, battle anim, boss, Optimum/Empty/Arrange, save/load, Sell/Colosseum exclusion, smith)`.
Nếu FAIL: ghi số bước + món (`$1xx` hoặc tên) + ảnh chụp màn hình.
