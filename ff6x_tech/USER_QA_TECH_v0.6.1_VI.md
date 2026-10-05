# FFVI Expanded Edition — TECH v0.6.1 HOTFIX User QA (Tiếng Việt)

**ROM test:** `FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA.sfc`
SHA-1 `8a55707ff2b4cd1364fdabf75e91422ba90ff8bb` · CRC32 `289BD3B9`
(hoặc patch `FF6X_Rev1_TECH_v0.6.1_ENEMY_ASSET_QA.bps` lên ROM Rev 1 sạch). Kiểm tra hash trước. Dùng `.srm` mới (New Game).

**Vì sao v0.6 fail:** trận isolation cũ đặt chim test ở ô VRAM số 5 của formation `$008`. Khi party cưỡi **Magitek**,
đồ họa Magitek đè lên ô đó → con chim bên phải hiện thành mảnh giáp Magitek. **ROM gốc Rev 1 cũng bị y hệt** với Dark Wind
thật ở ô đó. Dữ liệu đồ họa `$182/$183` đúng (cùng record/tile/stencil với Dark Wind). v0.6.1 chỉ đổi bố cục trận test.

Ô QA: New Game → khi điều khiển được ở Narshe → đi **lên 6, trái 4** → `TECH v0.6.1 QA ACCESS`.

## A. Dark Wind isolation (mục chính của hotfix)
1. Ô QA → **More tests** → **Dark Wind isolation** → **Vanilla, clone, Vulture pal**.
   Trận có **3 con chim**, không có Leafer (chim bay vào sau vài giây; đợi đứng yên rồi so):
   | Vị trí | Quái | Mong đợi |
   |---|---|---|
   | **trên cùng bên trái** | Dark Wind gốc (`$028`) | Dark Wind bình thường |
   | **dưới bên trái** | `DW CLONE` (`$182`) | **giống hệt** con trên cùng (hình + màu) |
   | **giữa** | `DW VULPAL` (`$183`) | **cùng hình dáng** Dark Wind, chỉ khác màu (hồng/nâu loang) |
   Có thể mở lệnh tấn công để xem tên từng con khi chọn mục tiêu.
2. Ô QA → More tests → Dark Wind isolation → **Reference: 3x vanilla** → 3 con Dark Wind gốc cùng vị trí trên, cả 3 giống nhau.
   So với bước 1: con trên-trái và dưới-trái phải giống bước 2; con giữa chỉ khác màu.
3. Thắng hoặc chạy trốn đều được; chỉ cần nhìn rõ 3 con. Không có back attack ở 2 trận này.
   Nên làm khi party còn khỏe (dùng Tonic nếu HP thấp).

## B–F. Hồi quy nhanh (giống v0.6)
- **B/C Custom monster battle:** TESTCUBE A (khối thạch xanh) + TESTEYE B (mắt cam có gai) sắc nét; hạ 1 con, con kia giữ nguyên hình; thắng → `TECH v0.6.1: battle returned to the field correctly.` → về Narshe bình thường.
- **E Magic Points:** More tests → Magic Point test → Not yet (go equip) → trang bị Ramuh cho Terra → **Fight 3-MP battle (241)** → Bolt 30%, Poison 15%, Bolt 2 6%; **Fight 0-MP battle (240)** → % không đổi.
- **D Save/load:** No (Save Point) → Save → reset → Continue → mọi thứ giữ nguyên; trận custom vẫn đúng.
- **F Vanilla:** vài trận gốc (lính gác Narshe…), Map/Annex tests vẫn như v0.5/v0.6.
- Steal/Sketch/Control: **NOT TESTED** (Claude đã kiểm tra bằng poke RAM).

---
PASS mẫu:

`TECH v0.6.1 PASS — Dark Wind isolation: clone $182 identical to vanilla Dark Wind, $183 same shape with Vulture colours only; reference battle 3x vanilla OK; custom assets, Magic Points (241=3, 240=0), save/load and vanilla regression OK. Steal/Sketch/Control: NOT TESTED.`

Nếu FAIL: ghi trận, vị trí con chim sai, chụp màn hình, emulator, `.srm`/save state.
