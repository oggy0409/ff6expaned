# FFVI Expanded Edition — TECH v0.5 User QA (Tiếng Việt)

**ROM test:** `FF6X_Rev1_TECH_v0.5.0_MONSTER_TECH_QA.sfc`
SHA-1 `416d5d9fbd88751e8fbd5ab4290dbb51fff3e69f` · CRC32 `381E6EE5`
(hoặc patch `…MONSTER_TECH_QA.bps` lên ROM Rev 1 sạch). Kiểm tra hash trước khi chạy. Dùng `.srm` mới (New Game).

Bản này chuyển **toàn bộ** bảng quái (chỉ số, tên, AI, đồ, Control, Sketch, đồ hoạ) và bảng formation sang vùng mới F8–F9.
Vì vậy phần vanilla (A, E) quan trọng không kém 2 quái mới. 2 quái mới là placeholder kỹ thuật (mượn hình quái vanilla).

Ô QA vẫn nằm trong đoạn mở đầu cưỡi Magitek → không dùng để kiểm tra sprite field sau khi load (KNOWN_QA_ISSUE_v0.3.1).
Đầu game túi đồ trống: nếu lỡ mở **Item** trong trận sẽ thấy khung trống và thời gian đứng (Wait mode) — bấm **B** để thoát (game gốc cũng vậy, không phải lỗi).

## A. Boot / vanilla
1. New Game → xem dialogue đầu game → khi điều khiển được ở phố Narshe.
2. **Đánh ít nhất 2 trận vanilla đầu Narshe** trước khi vào QA (ví dụ đi lên phía bắc tới lính gác — trận Guard; hoặc làm ở mục E).
3. Tên quái (Guard, Leafer, Vomammoth…), sprite, palette, hành vi phải như game gốc. Không freeze / màn đen.

## B. Vào battle TECH v0.5
1. Từ chỗ bắt đầu điều khiển: đi **lên 6 ô**, **sang trái 4 ô** (ô QA như v0.4).
2. Hộp: `TECH v0.5 QA ACCESS / Monster test battle / Map/Annex tests / No (Save Point)` → chọn **Monster test battle**.
3. Thông báo `TECH v0.5: TESTMOB A + B / New monster IDs 180 and 181. / Formation 240.` → vào trận.

Kiểm tra:
| | Quái bên trái-dưới | Quái bên trên |
|---|---|---|
| Tên (khi chọn mục tiêu) | **TESTMOB A** (ID $180) | **TESTMOB B** (ID $181) |
| Sprite | hình **Leafer** (thỏ trong bụi lá xanh) | hình **Dark Wind** (chim) |
| Palette | màu gốc của Leafer | **màu Vulture** (nâu/vàng nhạt, KHÁC màu Dark Wind gốc) |
| AI | đánh thường + thỉnh thoảng **Mute** | đánh thường + thỉnh thoảng **Slow** |

- Cả 2 quái đều xuất hiện, không sprite rác / tile lỗi.
- Để party đứng yên một lúc: phải thấy cửa sổ tên chiêu **Mute** và **Slow** (mỗi chiêu chỉ do 1 con dùng). Quái rất yếu, party không chết.

## C. Battle behavior
1. Target riêng từng con (tên đúng khi đưa con trỏ qua mỗi con).
2. Hạ **một con trước** (Fire Beam đủ mạnh), để con còn lại hành động thêm vài lượt.
3. Đánh thắng. Thưởng: **+75 Gil** (30 + 45) và tối đa 2 món đồ trong: Tonic, Potion, Antidote, Eyedrop.
4. Sau trận: thông báo `TECH v0.5: battle returned to the field correctly.` → về Narshe **ngay bên phải ô QA**, điều khiển bình thường, **không lặp trận**.

**Steal / Sketch / Control:** party Magitek đầu game không có các lệnh này → ghi **NOT TESTED** (không tính là fail).
Claude đã kiểm tra bằng poke RAM trong emulator (Steal: Potion/Tonic – Fenix Down/Antidote; Sketch A → Mute, B → Slow; Control A = Battle/Mute, B = Battle/Slow).

## D. Save/load
1. Bước trái lên ô QA → **No (Save Point)** → menu → **Save**.
2. Reset / tắt emulator → **Continue**.
3. Gil và đồ vừa nhận còn nguyên.
4. Bước phải 1, trái 1 → **Monster test battle** lần nữa → 2 quái giống hệt lần đầu (tên/hình/màu/AI), thắng, về đúng chỗ.

## E. Vanilla regression
1. Ô QA → **Map/Annex tests** → **Map test A (1A0)** → đi một vòng, nói NPC A1 → ra lối nam. Rồi **Celes Annex** → nói Vale → ra (đã PASS ở v0.4, chỉ kiểm tra không hỏng).
2. Chơi tiếp mở đầu như bình thường: lính gác, các trận Magitek ở mỏ, **boss Whelk**, chạy trốn qua mỏ cùng Locke/Moogle… càng xa càng tốt.
3. Kiểm tra tên quái vanilla, hình/màu, thưởng sau trận; nếu có Locke: thử **Steal** một quái vanilla.
4. Nói vài NPC vanilla.

## F. Báo ngay nếu thấy
- tên quái bị lấy nhầm (vanilla hoặc TESTMOB),
- sprite/palette của quái vanilla bị đổi,
- quái mới biến thành monster khác / hiện hình esper,
- target sai, battle freeze khi một quái chết,
- reward/drop sai item, gil sai,
- save/load lỗi,
- Gau/Rage/Veldt bất thường (nếu chơi tới đó).

---
PASS mẫu:

`TECH v0.5 PASS — new monster IDs 0x180/0x181 load together correctly; names/graphics/palettes/stats/AI OK; battle targeting/victory/return OK; save/load OK; vanilla monster battles/regression OK (played to: …). Steal/Sketch/Control: NOT TESTED.`

Nếu FAIL: ghi mục (A–F), trận/vị trí, chụp màn hình, emulator, file `.srm` / save state.
