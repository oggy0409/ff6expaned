# QA TECH v0.2 — Hướng dẫn test (Event + Dialogue Expansion Proof)

ROM test: `FF6X_Rev1_TECH_v0.2.0_EVTEST.sfc`
SHA-1 `0258a0fc122bb109e7ca343dda61c58af2e921fb` · CRC32 `32725A65`
(Hoặc tự patch `…EVTEST.bps` lên ROM Rev 1 sạch — BPS sẽ từ chối nếu ROM sai.)

Emulator khuyên dùng: Mesen2 / bsnes / Snes9x. Save SRAM (.srm) của Rev 1 dùng chung được.

## Test 1 — Boot & vanilla text
1. Boot ROM → New Game.
2. Xem đoạn mở đầu Narshe ("1000 years have passed…", Vicks/Wedge).
**PASS:** chữ hiển thị bình thường, không lỗi/garbled, không treo.

## Test 2 — NPC mở rộng (trigger chính)
1. Chơi tới **Lâu đài Figaro lần đầu (World of Balance), ban ngày** — hoặc load save có sẵn ở đó.
2. Lên **sân thượng/tường thành bên phải**, tìm NPC tại toạ độ (44,21)
   — người vốn nói *"Weapons and items manufactured here are sent to South Figaro."*
3. Nói chuyện lần 1.

**PASS khi thấy đúng thứ tự:**
- Hộp 1: `TECH v0.2 EVENT TEST / This line is stored in bank F3. / Test event bit #255 is now ON.`
- Hộp 2: câu vanilla *"Weapons and items manufactured here are sent to South Figaro."*
- Điều khiển nhân vật bình thường sau đó.

4. Nói chuyện lần 2.
**PASS:** Hộp 1 đổi thành `… Test event bit #255 is still ON. / The flag state was kept.` rồi câu vanilla.

## Test 3 — Save / Reset / Load (flag persistence)
1. Sau Test 2, ra khỏi lâu đài và **save trên World Map** (Menu → Save).
2. **Reset** máy → **Load** save đó.
3. Quay lại nói chuyện với NPC.
**PASS:** hiện câu `… is still ON …` (không quay lại câu "now ON").

## Test 4 — Ổn định
- Mở/đóng menu, đánh 2–3 trận, nói chuyện vài NPC khác, ra/vào lâu đài.
**PASS:** không treo, chữ vanilla đúng.

## (Tuỳ chọn) Test production branch
`FF6X_Rev1_TECH_v0.2.0_FOUNDATION.sfc` — phải chơi giống hệt vanilla Rev 1
(không còn EXPTEST ở lệnh Fight/MagiTek).

## Báo kết quả
Gửi một dòng, ví dụ:
`TECH v0.2 PASS — new line OK; vanilla line OK; flag kept after save/reset/load; no freeze.`
Nếu FAIL: chụp màn hình + ghi bước bị lỗi + emulator đang dùng.

Lưu ý: nếu tới Figaro mà NPC không có mặt (đang cảnh đêm/cháy lâu đài), hãy dùng save trước đó — NPC chỉ xuất hiện khi bit NPC `$30B` bật.

Nếu lúc đó không ra World Map được (đang giữa sự kiện cốt truyện): cứ save ở lần save kế tiếp, reset/load, và kiểm tra lại NPC ở lần quay lại Figaro sau này (NPC xuất hiện lại khi bit `$30B` bật). Flag `#255` không bị game vanilla đụng tới nên vẫn phải còn ON.
