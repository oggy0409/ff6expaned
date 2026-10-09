# FFVI Expanded Edition — TECH v0.9 Consumables + Rare/Key Items — User QA (Tiếng Việt, ~20–30 phút)

Một lượt QA duy nhất cho toàn bộ v0.9: 8 vật phẩm tiêu hao `$127-$12E`, cửa hàng mở rộng, bán đồ, 5 vật phẩm hiếm (key
item) + sức chứa ≥32, save/load và di trú save cũ. Phía Claude đã chạy emulator đầy đủ (xem `REGRESSION_REPORT_v0.9.md`);
bước này là **USER RUNTIME QA** trên emulator/phần cứng của bạn.

## ROM
| ROM | SHA-1 | CRC32 | Dùng cho |
|---|---|---|---|
| `FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc` | `e1136805cc792e11dbffab15e87df0f327a6a12e` | `D8183069` | **toàn bộ checklist** |
| `FF6X_Rev1_TECH_v0.9_PRODUCTION.sfc` | `99cd74dfac5b91756120992dd1560534b40c66c3` | `FF753A76` | bước 13 (tùy chọn) |

Hoặc patch `.bps` tương ứng lên ROM Rev 1 sạch (CRC32 `C0FA0464`).

## Vào menu QA
New Game → Narshe: ô QA (**lên 6, trái 4**) → `TECH v0.9 QA ACCESS`:
* `Consumables v0.9` → `Grant all 8 (x5 each)` · `Consumable shops` (Rebuilt general store / Rebuilt late store / Get
  20000 GP) · `More…` → `Battle test (guards)` · `Field-use setup (P1)` · `More…` → `Remove all 8` · `Party presets`.
* `Rare items v0.9` → `Grant all 5 key items` · `Remove all 5` · `More…` → `Toggle one key item` · `Check Triune Sigil` ·
  `More…` → `Fill all 52 (3 pages)` · `Clear QA fill`.
* `More…` → `Stress / save (v0.9)` (`Grant everything`, `Save Point`, `More…` → `Battle`, `Colosseum`, `Migration
  info`) · `Equipment v0.8 (39 items)` (menu QA v0.8 cũ) · `More…` → `Older tests` · `Save Point`.

Tên hiển thị tối đa 12 ký tự (vật phẩm) / 13 ký tự (vật phẩm hiếm): `AetherFlask`, `BeaconFlare`, `MagitekCell`,
`Darill'sToken` là dạng rút gọn có chủ đích.

## Checklist
| # | Làm | PASS khi |
|---|---|---|
| 1 | `Consumables v0.9` → `Grant all 8` → mở **Item** | 8 món: Gaia Tonic, AetherFlask, Phoenix Ash, Null Dust, Iron Ration, Remedy+, BeaconFlare, MagitekCell, mỗi món ×5, mô tả 2 dòng đúng; **Null Dust / BeaconFlare / MagitekCell màu xám** (chỉ dùng trong trận) |
| 2 | `Consumables → More… → Field-use setup (P1)` → Item → **Remedy+** cho Terra | Terra hết Poison/Blind/Imp, Remedy+ còn 4 |
| 3 | Item → **Phoenix Ash** cho Locke (đang KO) | Locke sống lại với khoảng nửa HP; dùng Phoenix Ash cho người còn sống → **không** dùng được |
| 4 | Sau một trận (HP hụt) hoặc ngay: **Gaia Tonic**, **Iron Ration**, **AetherFlask** cho một người | HP/MP tăng (tối đa), số lượng giảm 1; khi HP đầy → không dùng được, không mất món. Bấm **Null Dust** trong menu → không có màn chọn người |
| 5 | Item → **Arrange** | đủ 8 món + số lượng (và đồ v0.8 nếu có), không mất/không nhân đôi |
| 6 | `Consumables → More… → Battle test (guards)`. Trong trận: **Item** | danh sách có 8 món mới đúng tên + số lượng; **không có** món trang bị đặc biệt v0.8 nào. Để dùng: chọn món → **A hai lần** → chọn mục tiêu → A |
| 7 | Dùng **Gaia Tonic** (cả đội), **BeaconFlare** (mọi kẻ địch), **Null Dust** (một lính) | khung tên ở trên ghi đúng tên món; Gaia Tonic: hiệu ứng như Potion, cả đội hồi ~120 HP; BeaconFlare: hiệu ứng Fire 2, mọi lính mất HP; Null Dust: không lỗi; số lượng giảm |
| 8 | Thắng trận → mở Item | số lượng = trước trận trừ số đã dùng; không có kiếm Blossom/katana lạ xuất hiện |
| 9 | `Consumable shops` → `Rebuilt general store` → **Buy** Gaia Tonic | danh sách 8 món (3 món mới + Potion, Tincture, Fenix Down, Remedy, Tent) có giá; Owned = số đang có, Equipped 0; mua xong trừ đúng GP, cộng đúng số |
| 10 | Cùng cửa hàng → **Sell** | Gaia Tonic / Null Dust / Iron Ration / Remedy+ bán được (½ giá); AetherFlask / Phoenix Ash / BeaconFlare / MagitekCell **không** chọn được. `Rebuilt late store` có Remedy+ đứng đầu |
| 11 | `Rare items v0.9` → `Grant all 5` → Item → **RARE** | Pendant (của Terra) + Darill'sToken, Concord Sigil, Cinder Sigil, Triune Sigil, Broken Seal; mô tả đúng từng món; số đếm 6. `Remove all 5` / `Toggle` / `Check Triune Sigil` hoạt động |
| 12 | `Rare items → More… → More… → Fill all 52` → Item → RARE | số đếm 52; trang 1 = 20 món gốc; **Xuống ở hàng cuối** → trang 2 (key items + QA Rare 25…); **R / L** đổi trang; trang 3 kết thúc ở QA Rare 51; mô tả không bị chồng chữ. Sau đó `Clear QA fill` |
| 13 | `More… → Stress / save` → `Grant everything` → `Party presets` (P1) → mặc vài món v0.8 → `Save Point` → **Save** → Reset → **Continue** | toàn bộ: 39 món trang bị, 8 vật phẩm tiêu hao, 5 key item, đồ đang mặc giữ nguyên. (Tùy chọn) mở save này bằng ROM **PRODUCTION**: vẫn giữ nguyên |
| 14 | (Tùy chọn) mở một save **v0.8** cũ bằng ROM v0.9 | mọi món v0.8 (kể cả đang mặc) giữ nguyên, không bị xoá |
| 15 | `Stress → More… → Colosseum` | không đặt cược được vật phẩm tiêu hao / trang bị đặc biệt; trận chạy và quay về Narshe |
| 16 | (Hồi quy nhanh) `More… → Equipment v0.8` → mặc 1 vũ khí đặc biệt → `Battle test` → Fight | đòn đánh/hình vũ khí như v0.8 |

Ghi chú: trong danh sách Item/Throw của trận, dòng của kiếm katana gốc (vd. Blossom) có chữ `DIRK` phía sau — đây là lỗi
nhỏ có sẵn của bản Rev 1 gốc (cũng có ở v0.8 đã duyệt), không phải lỗi v0.9 (`KNOWN_RISKS_v0.9.md` R37).
Mọi thông số (hiệu ứng, giá, nguồn nhận) của 8 vật phẩm và 5 key item là **DERIVED** (chỉ tên là locked) — xem
`CONSUMABLE_MASTER_TABLE_v0.9.md` / `RARE_ITEM_MASTER_TABLE_v0.9.md` nếu muốn chỉnh.

---
Báo PASS mẫu: `TECH v0.9 PASS — 1–16 OK (8 consumables field/battle, shops buy/sell, rare 5 + 52/3 pages, save/load, migration, Colosseum exclusion)`.
Nếu FAIL: ghi số bước + món (`$1xx` / rare id hoặc tên) + ảnh chụp màn hình.
