# FFVI Expanded Edition — TECH v0.7.2 Colosseum Hotfix — User QA (Tiếng Việt)

**ROM test:** `FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.sfc`
SHA-1 `1e2604acd9f0fc3d358a1bb4b40dc099d195dccc` · CRC32 `3D05456C`
(hoặc patch `FF6X_Rev1_TECH_v0.7.2_ITEM_BANK_QA.bps` lên ROM Rev 1 sạch, SHA-1 `057ADA1C…`, CRC32 `C0FA0464`).
Kiểm tra hash trước. Dùng **New Game** với `.srm` mới (riêng bước R-L dùng save cũ).

## Lỗi v0.7.1 và cách sửa (tóm tắt)
Màn hình đen ở Colosseum **không phải** do engine vật phẩm. Mục `Colosseum` trong **menu QA** của v0.7.1 chỉ chạy lệnh
mở menu Colosseum (`$9A`). Lệnh này tắt fade-in của map và nạp lại map. Script gốc của quầy tiếp tân còn phải gọi
**trận đấu** (`$AF`) hoặc **fade-in**, nhưng menu QA không gọi nên màn hình đen mãi. ROM Rev 1 sạch chạy đúng các byte
đó cũng bị đen y hệt. v0.7.2: mục QA gọi **đúng script gốc của quầy tiếp tân** (CB:78D9). Engine vật phẩm không đổi
một byte nào. Chi tiết: `COLOSSEUM_ROOT_CAUSE_v0.7.2.md`.

**Ô QA:** New Game → khi điều khiển được ở Narshe → đi **lên 6, trái 4** → hộp thoại `TECH v0.7.2 QA ACCESS`
→ `Item bank tests (v0.7.1)` → `Shop / Colosseum / Battle` → **`Colosseum (full battle)`** → menu con:
- `Fight (wager list)` → vào Colosseum (script gốc của quầy tiếp tân)
- `Get wager kit` → nhận đồ cược thường: **Elixir ×3, Fenix Down ×3, ThiefKnife, ValiantKnife**
  (New Game không có đồ). Elixir / Fenix Down đấu với **Cactrot** (thưởng Rename Card / Magicite, đội mở đầu
  có thể thắng); ThiefKnife / ValiantKnife đấu với đối thủ mạnh (thường thua → kiểm tra nhánh thua).
- `Cancel`

Mỗi lần chọn xong nhân vật bước sang phải 1 ô; bước lại vào ô QA để mở lại menu.

## C. Colosseum (bắt buộc, mới)
Mỗi lượt: Ô QA → … → `Colosseum (full battle)` → màn hình tối dần → **danh sách cược** → chọn 1 món → màn hình
“đối thủ ↔ đồ thưởng” → chọn **đấu sĩ** (trái/phải) → A.

| Bước | Kết quả đúng (PASS) |
|---|---|
| C1 vào trận | Vào trận đấu Colosseum (đấu trường, khán đài), **không đen màn hình** |
| C2 đấu sĩ | Đúng nhân vật đã chọn, hình hiển thị bình thường |
| C3 đối thủ | Đúng quái vật hiển thị ở màn “đối thủ ↔ thưởng” trước đó, hình bình thường |
| C4 trong trận | Trận tự chạy (Colosseum là trận tự động); bấm A/B/X/Y không làm treo |
| C5 thắng | Nhận **đồ thưởng** đã hiển thị; món cược mất |
| C6 thua | Món cược mất, không nhận thưởng (đúng như game gốc) |
| C7 về lại | Trở về Narshe, màn hình sáng lại, **điều khiển được** (nhân vật bước sang phải 1 ô) |
| C8 huỷ | Mở danh sách cược rồi bấm **B** (không cược) → màn hình sáng lại, điều khiển được |

Làm **ít nhất 3 tổ hợp** cược/đấu sĩ khác nhau, ví dụ: Elixir + Vicks, Fenix Down + Wedge, Elixir + Terra,
ThiefKnife + Vicks (đấu sĩ: Terra / Wedge / Vicks, chọn trái/phải). Kết quả thắng/thua do may rủi (giống game gốc):
C5 cần thắng ít nhất 1 lần (Elixir/Fenix Down vs Cactrot; nếu thua, lấy kit lần nữa và thử lại).
Sau khi thua, đấu sĩ có thể bị Wounded (giống game gốc): chọn đấu sĩ khác, hoặc hồi bằng Fenix Down trong menu Item.
Ngoài ra thử 1 lần với **Terra đang mang QA Blade13D / QA Mail 13E / QA Charm13F** (bước A, D của v0.7.1): sau
trận, 3 món đó vẫn nằm đúng trên người Terra, đúng tên, không biến thành cọ.
QA items **không** có trong danh sách cược (dòng trống, không chọn được), giống v0.7.1 M3.

## R. Hồi quy v0.7.1 (đã PASS ở v0.7.1, chạy lại nhanh)
Làm theo `USER_QA_TECH_v0.7.1_VI.md` (dùng ROM v0.7.2, hộp thoại giờ là `TECH v0.7.2 QA ACCESS`):

| Mục | Kiểm tra | v0.7.1 |
|---|---|---|
| R-A/B/C | nhận 3 QA item, tên/icon/mô tả, vị trí danh sách | A, B, C |
| R-D/E/G | trang bị cả 3 cùng lúc, Remove/Empty, chỉ số, relic | D, E, G |
| R-H | Arrange | H |
| R-I | Optimum (không nhân bản) | I |
| R-J | save → reset → load | J |
| R-F | trận thử: hoạt ảnh kiếm, sát thương, R-Hand thay bị từ chối, đổi R↔L | F |
| R-M | shop: số “đang có”, Sell (dòng trống) | M1, M2 |
| R-K | event GIVE/TAKE/HAS (Check / remove QA Blade13D) | K |
| R-L | save cũ (v0.6.x / Rev 1): không có QA item “ma” | L |
| R-N | vanilla, menu Monster/map tests (v0.6.1) | N |

---
PASS mẫu:

`TECH v0.7.2 PASS — Colosseum C1–C8 OK (combos: <món>/<đấu sĩ> ×3+, win + reward OK, loss OK, return + control OK, cancel OK, QA-equipped Terra keeps items) · v0.7.1 regression R-A…R-N OK.`

Nếu FAIL: ghi bước, món cược, đấu sĩ, đối thủ, ảnh chụp màn hình, emulator + phiên bản, và gửi `.srm` / save state.
