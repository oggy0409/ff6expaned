# Hướng dẫn QA — TECH v0.4 MAP EXPANSION FOUNDATION

**ROM test:** `FF6X_Rev1_TECH_v0.4.0_MAP_TECH_QA.sfc`
SHA-1 `e1d5387a819e3db87ce572d35ca51a5f5c91b6f1` · CRC32 `EE846BD5`
(hoặc patch `…MAP_TECH_QA.bps` lên ROM Rev 1 sạch.) Dùng file `.srm` mới (New Game).

Bản này đổi **toàn bộ** bảng NPC / trigger / lối ra vào / rương / thuộc tính map / con trỏ layout của game sang vùng mới (F6–F7).
Vì vậy phần **regression vanilla (mục F)** quan trọng không kém 2 map mới.
Nội dung map mới là placeholder kỹ thuật (chữ "TECH A1", "TECH B1"…), không phải nội dung cuối.

Ô QA nằm trong đoạn mở đầu cưỡi Magitek → **không dùng để kiểm tra sprite sau khi load** (đã biết: sau load hiện sprite đi bộ — KNOWN_QA_ISSUE_v0.3.1). Cờ/flag sau load vẫn kiểm tra được.

---

## A. Vào game
1. New Game → xem mở đầu → khi điều khiển được ở phố Narshe.
2. Đi **lên 6 ô**, **sang trái 4 ô** (ô QA như bản v0.3.1).
3. Hộp: `TECH v0.4 QA ACCESS / Map test A (1A0) / Celes Annex / No (Save Point)`.

## B. Map mới A ($1A0)
1. Chọn **Map test A** → vào phòng thí nghiệm placeholder (hành lang dưới).
2. Đi khắp nơi: sảnh dưới → hành lang → phòng lớn phía bắc.
3. Ở sảnh dưới, hàng trên cùng của sảnh, sát tường trái có một **hốc 1 ô**: bước vào → `TECH v0.4: event trigger on map 1A0…` → bị đẩy ra phải 1 ô.
4. Phòng bắc: nói với **A1** (trái) → `…NPC data: relocated table F6… Visit the room to the north.`; nói với **A3** (phải) → `…second routed NPC…`.
5. Lúc này **không có A2** (chỗ phía dưới bên phải phòng trống).
**PASS:** không màn đen, không đi xuyên tường, hội thoại đúng.

## C. Map mới B ($1A1)
1. Đi lên **cửa giữa tường bắc** phòng A → sang phòng nhà gỗ (art nhà Narshe).
2. Nói với **B1** (góc trái) → `…Flag VISITED B is now ON.`; nói lại → `…Door: short entrance. Stairs: long entrance.`
3. Ra bằng **ô cầu thang/hốc bên phải phía dưới** → về sảnh dưới của A.
4. Lên phòng bắc: **A2 đã xuất hiện**. Nói A1 → `…flag VISITED B is ON. The new NPC (A2) appeared…`; nói A2.
5. Đi lại cửa bắc → B → bước **xuống ô cửa dưới** của B → về A ngay dưới cửa.
**PASS:** cả 2 kiểu lối ra (cửa/cầu thang) đúng chỗ, A2 chỉ hiện sau khi nói B1.

## D. Thoát + Save/Reset/Load
1. Từ A đi xuống cuối sảnh, bước qua **lối ra phía nam** → về Narshe, **ngay bên phải ô QA**.
2. Bước trái lên ô QA → chọn **No (Save Point)** (nháy xanh; lần đầu có hỏi về Save Point) → menu → **Save**.
3. **Reset** → **Continue**.
4. Bước phải 1 ô, trái 1 ô → **Map test A** → A2 vẫn hiện; A1 vẫn nói câu "VISITED B is ON".
**PASS:** flag giữ sau save/reset/load, không bị hỏi lặp khi đứng yên trên ô QA.

## E. Celes Annex (đã chuyển sang hệ thống map mới)
1. Ô QA → **Celes Annex** → làm lại nhanh: cửa bắc bị khoá → nói Vale → đánh (2 Guard) → về đúng chỗ, không đánh lại → mở rương +1 Potion → ra về Narshe (35,43).
**PASS:** giống hệt v0.3 (Vale và rương giờ chạy qua bảng vector, không còn dùng bridge).

## F. Regression vanilla (quan trọng)
1. Từ Narshe đi tiếp mở đầu như bình thường: lính gác, các trận Magitek, hang mỏ, boss, tỉnh dậy ở nhà Arvis, chạy trốn qua mỏ, gặp Locke/Moogle… chơi càng xa càng tốt (tối thiểu tới khi ra world map).
2. Chú ý: NPC đúng chỗ và đúng hội thoại, cửa/lối ra vào dẫn đúng map, trigger sự kiện chạy, rương đã mở không mở lại, save point hoạt động, world map vào/ra thành phố.
**PASS:** không lỗi so với game gốc.

---

## Báo kết quả
`TECH v0.4 PASS — map 1A0/1A1 entry/collision OK; routed NPCs OK; triggers OK; short+long entrances OK; A2 flag persistence after save/reset/load OK; Annex OK on v0.4 pipeline; vanilla opening regression OK (played to: …).`

Nếu FAIL: ghi mục (A–F), map/vị trí, chụp màn hình, emulator, file `.srm`/save state.
