# FFVI Expanded Edition — TECH v0.6 User QA (Tiếng Việt)

**ROM test:** `FF6X_Rev1_TECH_v0.6.0_ENEMY_ASSET_QA.sfc`
SHA-1 `14d179cfa61e720aa81ea9c4be518df1e13212fa` · CRC32 `F13B490B`
(hoặc patch `…ENEMY_ASSET_QA.bps` lên ROM Rev 1 sạch). Kiểm tra hash trước. Dùng `.srm` mới (New Game).

Ô QA: New Game → khi điều khiển được ở Narshe → đi **lên 6, trái 4**.
Menu: `Custom monster battle / More tests / No (Save Point)`; `More tests` → `Dark Wind isolation / Magic Point test / Map/Annex tests`.

**Thứ tự nên làm:** B → C → E (Magic Point) → D (save/load) → A (Dark Wind) → F.
Party mở đầu yếu dần sau nhiều trận: nếu HP thấp, dùng **Tonic** nhận được từ quái (Menu > Item). Ai bị Wounded thì không nhận MP.
Đầu game nếu lỡ mở Item khi túi trống sẽ thấy khung trống, thời gian đứng (Wait mode) — bấm B (game gốc cũng vậy).

## B. Trận custom graphics
1. Ô QA → **Custom monster battle**.
2. Kiểm tra:
   - **TESTCUBE A** (trái-dưới): khối thạch **xanh dương**, 2 râu vàng, 2 mắt trắng, miệng đỏ, má xanh lá.
   - **TESTEYE B** (trên): **con mắt cam/đỏ** có 4 gai vàng, tròng xanh lá, đồng tử đen dọc.
   - Hình sắc nét, không tile rác, không mảnh vỡ, không màu lạ, không nhấp nháy.
3. Chọn mục tiêu từng con (tên đúng: TESTCUBE A / TESTEYE B).

## C. Battle behavior + return
1. Hạ **một con trước**, để con kia đánh thêm vài lượt → hình con còn lại **vẫn y nguyên**.
2. Thắng → `TECH v0.6: battle returned to the field correctly.` → về Narshe bên phải ô QA, điều khiển bình thường, không lặp trận.
   (+75 Gil, đồ rơi: Tonic/Potion/Antidote/Eyedrop.)

## E. Magic Points
1. Ô QA → More tests → **Magic Point test** → hộp `QA: Ramuh added. Equip it first.` → chọn **Not yet (go equip)** (party bước sang phải 1 ô).
2. Menu → **Skills** → TERRA (?????) → **Espers** → Ramuh → A → A (trang bị). Kiểm tra Terra còn sống (không Wounded).
3. Xem Skills > Magic: chưa có Bolt / Poison (hoặc ghi lại % hiện tại).
4. Về ô QA → More tests → Magic Point test → **Fight 3-MP battle (241)** → thắng.
   → Skills > Magic: **Bolt 30%, Poison 15%, Bolt 2 6%** (tăng thêm đúng chừng đó nếu đã có sẵn).
5. Ô QA → More tests → Magic Point test → **Fight 0-MP battle (240)** → thắng → % **không đổi**.

## D. Save/load
1. Ô QA → **No (Save Point)** → Menu → **Save** → Reset/tắt emulator → **Continue**.
2. Gil, đồ, Ramuh vẫn trang bị, % học phép giữ nguyên.
3. Ô QA → Custom monster battle lần nữa → 2 hình **giống hệt** lần đầu → thắng.

## A. Dark Wind isolation (so sánh)
1. Ô QA → More tests → **Dark Wind isolation** → **Exact clone (pal 046)**.
   Trận = 2 Leafer + 2 chim Dark Wind (chim bay vào sau vài giây). Con chim **bên phải** là bản sao `$182`
   (tên `DW CLONE`): phải **giống hệt** Dark Wind gốc bên cạnh.
2. Lặp lại với **Vulture palette (04A)**: con chim bên phải (`DW VULPAL`) **cùng hình dáng** nhưng màu loang lổ —
   đây chính là cấu hình TESTMOB B của v0.5 → xác nhận lỗi chỉ do palette.
   (Nếu party yếu, có thể thua/chạy trốn ở mục này; chỉ cần nhìn thấy 2 con chim.)

## F. Vanilla regression
- Đánh vài trận vanilla (lính gác Narshe, các trận Magitek trong mỏ, boss Whelk nếu được): tên/hình/màu quái đúng như gốc.
- Ô QA → More tests → Map/Annex tests → Map test A / Celes Annex: vẫn như v0.4/v0.5.

**Steal / Sketch / Control:** party Magitek không có → ghi **NOT TESTED** (Claude đã kiểm tra bằng poke RAM trong emulator, kể cả Sketch vẽ hình custom).

---
PASS mẫu:

`TECH v0.6 PASS — enemy graphics routing/custom assets render correctly; TESTMOB B issue isolated/resolved (palette-only); custom palettes OK; new-formation Magic Points work (241 = 3 MP); zero-MP case works (240); save/load and vanilla graphics/Esper regression OK. Steal/Sketch/Control: NOT TESTED.`

Nếu FAIL: ghi mục, trận/vị trí, chụp màn hình, emulator, file `.srm`/save state.
