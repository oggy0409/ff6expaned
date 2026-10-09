# QA TECH v0.3 — Celes Annex technical vertical slice (hướng dẫn test)

**ROM test:** `FF6X_Rev1_TECH_v0.3.0_CELES_TECH.sfc`
SHA-1 `e0196eb30fc03cf076c0d1306b0c09b664f7b2a4` · CRC32 `3E6B68E2`
(hoặc patch `FF6X_Rev1_TECH_v0.3.0_CELES_TECH.bps` lên ROM Rev 1 sạch — BPS sẽ từ chối nếu ROM sai.)

**Cần:** một save **World of Ruin đã có phi thuyền Falcon**. Save `.srm` của Rev 1 / các bản TECH trước dùng chung được.
Emulator: Mesen2 / bsnes / Snes9x.

Toàn bộ nội dung là placeholder kỹ thuật (chữ "TECH v0.3", "VALE (placeholder)", tile phòng thí nghiệm Magitek). Không phải script/art cuối.

---

## A. Regression vanilla
1. Boot → Load save WoR.
2. Đọc vài hộp thoại vanilla (NPC bất kỳ), mở/đóng menu, đánh 1 trận thường trên world map.
**PASS:** chữ đúng, không garbled, không treo.

## B. Vào Annex
1. Lên Falcon → xuống **khoang trong** (cầu thang từ boong xuống).
2. Từ chỗ xuống cầu thang, đi sang **trái 4 ô và xuống 2 ô** — ô kích hoạt ở toạ độ **(13,46)**, sát tường trái phòng trên.
3. Hiện hộp: `TECH v0.3: Annex test map. / Enter the Annex? / Yes / No`.
   - Chọn **No** trước → vẫn ở Falcon, điều khiển bình thường.
   - Bước ra rồi bước lại, chọn **Yes** → vào map mới.
4. Đi hết mọi chỗ đi được: hành lang dưới → phòng giữa → cửa hẹp phía bắc → phòng trên.
**PASS:** không màn đen, không đi xuyên tường/ra khoảng đen, không có chỗ bị kẹt, camera ổn.

## C. NPC + hội thoại mở rộng + flag
1. Đi thẳng lên cửa hẹp phía bắc **trước khi** nói với Vale → hộp `The door is sealed. (Talk to VALE first.)` và bị đẩy lùi 1 ô.
2. Nói với **VALE (placeholder)** (người đứng bên trái phòng giữa) → `...This text is from bank F3. / Annex flag STARTED is now ON...`
3. Nói lại → `...Annex flag STARTED is still ON. / Go north through the door...`
**PASS:** đúng nội dung, đúng thứ tự.

## D. Battle
1. Đi lên cửa hẹp phía bắc → `TECH v0.3: Annex defenses activate!` → trận **Mega Armor + ProtoArmor**.
2. Thắng.
**PASS:** quay về đúng map, hiện `Defenses are down. / Annex flag BATTLE DONE is ON.`, nhân vật tự bước lên 1 ô vào phòng trên, điều khiển bình thường; bước lại vào ô cửa **không** đánh lại.
(Tuỳ chọn: chạy trốn cũng tính là xong bước battle trong bản TECH — ghi lại nếu thấy. Thua → Game Over như vanilla.)

## E. Reward
1. Phòng trên: rương ở giữa. Đứng ngay dưới rương, nhìn lên, bấm A.
2. Hộp `TECH v0.3 placeholder reward: / Received 1 Potion. / Annex flag COMPLETE is ON.` → rương biến mất.
3. Bấm A lại / đi vào ô cũ của rương / mở menu Item.
**PASS:** chỉ +1 Potion một lần duy nhất.

## F. Persistence (save / reset / load)
1. Nói với Vale → `...Annex flag COMPLETE is ON. TECH slice finished...`
2. Đi xuống cuối hành lang, bước xuống ô thoát → về Falcon ngay cạnh ô kích hoạt.
3. Ra world map → **Save** → **Reset** → **Load**.
4. Vào lại Annex (Yes).
**PASS:** rương vẫn mất, Vale nói câu "COMPLETE", cửa không đánh lại, số Potion không tăng.

## G. Thoát / vanilla flow
1. Thoát Annex, lên boong, cất cánh Falcon, đi vài nơi WoR khác, nói chuyện vài NPC, đánh thêm 1 trận.
**PASS:** không lỗi Falcon/world map, không kẹt điều khiển.

---

## Báo kết quả
Nếu ổn, gửi:

`TECH v0.3 PASS — map entry/exit OK; expanded dialogue OK; production flag persists; battle returns correctly; reward is one-time; save/load OK; unrelated vanilla dialogue/battle flow OK.`

Nếu FAIL: ghi bước (A–G), chụp màn hình, emulator đang dùng, và nếu được thì gửi file `.srm` / save state.

### Ghi chú
- Không save được bên trong Annex (không có save point) — đúng thiết kế, giống dungeon vanilla.
- Các bit test `$14A/$14B/$14C/$6F8/$6F9` được giữ riêng vĩnh viễn cho bản TECH, không ảnh hưởng nội dung thật sau này.
