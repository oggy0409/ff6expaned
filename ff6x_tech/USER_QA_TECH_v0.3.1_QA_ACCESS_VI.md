# Hướng dẫn QA — TECH v0.3.1 CELES TECH QA ACCESS

> **QA HARNESS ONLY — NOT A PRODUCTION BASELINE.**
> ROM này chỉ để test slice Celes Annex của TECH v0.3 **từ New Game**, không cần save World of Ruin/Falcon.
> Bản TECH v0.3.0 đã nộp **không thay đổi**.

**ROM:** `FF6X_Rev1_TECH_v0.3.1_CELES_TECH_QA_ACCESS.sfc`
SHA-1 `bf443c85dc448c0a86169f58dce43d77684c36f5` · CRC32 `B982BC11`
(hoặc patch `…QA_ACCESS.bps` lên ROM Rev 1 sạch — BPS tự từ chối nếu ROM nguồn sai.)

Emulator: Mesen2 / bsnes / Snes9x. **Xoá hoặc dùng file `.srm` riêng** cho ROM này (không cần save cũ).

Ký hiệu: ô = 1 bước đi. "Ô QA" = ô kích hoạt test.

---

## A. Vào game + regression mở đầu
1. Boot → **New Game** → xem cảnh mở đầu (Terra, Wedge, Vicks trên Magitek).
2. Khi điều khiển được ở phố Narshe: mở menu (X) → đóng.
**PASS:** hội thoại vanilla mở đầu hiển thị đúng; menu mở có mục **Save bị mờ** (bình thường).

## B. Tới ô QA
1. Từ vị trí bắt đầu, đi **lên 6 ô** (tới quảng trường nhỏ), rồi **sang trái 4 ô** — tới góc trái quảng trường.
2. Hộp thoại xuất hiện: `TECH v0.3 QA ACCESS / Enter Celes Annex test? / Yes / No`.
   - Nếu chưa thấy: đi sang phải 1 ô rồi quay lại trái 1 ô.

## C. Kiểm tra "No" + Save Point
1. Chọn **No** → màn hình nháy xanh (save point vanilla). Lần đầu sẽ hỏi `Want info about Save Points?` → chọn gì cũng được.
2. Đứng yên vài giây.
3. Mở menu.
**PASS:** hộp thoại QA **không tự mở lại** khi đứng yên; trong menu mục **Save sáng (dùng được)**.

## D. Vào Annex
1. Đi sang phải 1 ô, quay lại trái 1 ô → hộp thoại QA → chọn **Yes**.
2. Đi hết các chỗ đi được: hành lang dưới → phòng giữa → cửa hẹp phía bắc → phòng trên.
**PASS:** vào map mới (phòng thí nghiệm Magitek placeholder), không màn đen, không đi xuyên tường/ra vùng đen, không kẹt.

## E. Cửa bị khoá + Vale (3 trạng thái hội thoại)
1. Đi thẳng lên cửa hẹp phía bắc **trước khi** nói với Vale → `The door is sealed. (Talk to VALE first.)` → bị đẩy lùi 1 ô.
2. Nói với **VALE (placeholder)** (bên trái phòng giữa) → `…This text is from bank F3. / Annex flag STARTED is now ON…`
3. Nói lại → `…Annex flag STARTED is still ON. / Go north through the door…`

## F. Battle
1. Đi lên cửa bắc → `TECH v0.3: Annex defenses activate!` → trận đánh.
   **Lưu ý bản QA:** đối thủ là **2 Guard** (trận mở đầu vanilla), không phải Mega Armor + ProtoArmor như bản v0.3 — để party New Game thắng được. Luồng event battle giữ nguyên.
2. Thắng (dùng Fight / Magitek bình thường).
**PASS:** quay về đúng map, hiện `Defenses are down. / Annex flag BATTLE DONE is ON.`, nhân vật tự bước lên 1 ô, điều khiển bình thường. Bước lùi lại vào ô cửa → **không** đánh lại.

## G. Reward (một lần)
1. Phòng trên: đứng ngay dưới rương, nhìn lên, bấm A → `…Received 1 Potion. / Annex flag COMPLETE is ON.` → rương biến mất.
2. Bấm A lại / đi vào ô cũ của rương / xem menu Item.
**PASS:** chỉ +1 Potion, một lần duy nhất.
3. Nói lại với Vale → `…Annex flag COMPLETE is ON. TECH slice finished…`
   (Câu này vẫn ghi "return to the Falcon" — giữ nguyên chữ v0.3, bình thường trong bản QA.)

## H. Thoát về Narshe + Save
1. Đi xuống cuối hành lang, bước xuống ô thoát → về **Narshe, ngay bên phải ô QA**, nhìn sang trái.
2. Bước trái 1 ô lên ô QA → chọn **No** (nháy xanh) → mở menu → **Save** vào 1 slot.
**PASS:** về đúng chỗ, điều khiển bình thường, save thành công.

## I. Reset / Load / vào lại
1. **Reset** emulator (hoặc tắt hẳn rồi mở lại) → **Continue** → chọn slot vừa save.
2. Đứng yên vài giây ở ô QA.
3. Bước phải 1 ô, trái 1 ô → **Yes** → vào lại Annex.
**PASS:** load về đúng ô QA, hộp thoại **không** tự mở liên tục; trong Annex: Vale nói câu "COMPLETE", rương vẫn mất, cửa bắc **không** đánh lại, số Potion **không** tăng.

## J. Regression vanilla sau QA
1. Thoát Annex → từ Narshe đi sang phải 3 ô về đường chính rồi đi **lên phía bắc** theo cốt truyện.
2. Gặp cảnh lính gác (`GUARD: Imperial Magitek Armor?…`) → trận đánh vanilla → tiếp tục vài bước.
**PASS:** hội thoại & trận đánh vanilla bình thường, không garbled, không treo, điều khiển trở lại.

---

## Báo kết quả
Nếu ổn, gửi:

`TECH v0.3.1 QA ACCESS PASS — map entry/collision OK; Vale 3 dialogue states OK; sealed door OK; battle + return OK, no loop; Potion one-time; COMPLETE persists after save/reset/load; re-entry OK; vanilla dialogue/battle OK.`

Nếu FAIL: ghi mục (A–J), chụp màn hình, emulator đang dùng, gửi file `.srm` / save state nếu được.

### Ghi chú
- Đây là harness QA: **không dùng làm nền cho bản production**. Các bản v0.3.0 (production / celes-tech) giữ nguyên hash.
- Ô QA chỉ có trong ROM này. Ngoài ô QA, Narshe mở đầu vẫn không save được (như vanilla).
- Kết quả PASS của bản này sẽ được ghi là bằng chứng runtime cho **luồng v0.3** (map/event/dialogue/flag/reward/persistence); riêng đội hình quái của trận battle khác bản v0.3 (Guard ×2 thay cho Mega Armor + ProtoArmor).
