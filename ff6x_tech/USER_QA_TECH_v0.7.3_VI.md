# FFVI Expanded Edition — TECH v0.7.3 Colosseum Visual / QA-state — User QA (Tiếng Việt, ngắn)

**ROM test:** `FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.sfc`
SHA-1 `3a784e0d3df817dd47d796f8b50b8ac34b143b31` · CRC32 `EB2923BA`
(hoặc patch `FF6X_Rev1_TECH_v0.7.3_ITEM_BANK_QA.bps` lên ROM Rev 1 sạch, CRC32 `C0FA0464`).
**Production không đổi:** `FF6X_Rev1_TECH_v0.7.2_PRODUCTION.sfc` (SHA-1 `f8f92c81…`) vẫn là bản production.

## Kết luận v0.7.2
Hai lỗi hình ảnh **là hành vi của game gốc Rev 1** khi vào Colosseum với đội mở đầu ở Narshe:
- Wedge / Biggs(Vicks) vô hình: Colosseum tìm nhân vật theo “actor = số bản ghi”. Wedge/Vicks là nhân vật
  tạm (bản ghi 14/15, actor $20/$21) nên không tìm thấy, do đó không có hình và không có tên.
- Terra có sprite thừa: Terra đang ở trạng thái **Magitek**, trận đấu bật “Magitek mode” và vẽ thêm hình áo giáp.

ROM Rev 1 sạch cho ra **đúng y hệt** (giống từng khung hình). Không phải lỗi engine vật phẩm. Chi tiết:
`COLOSSEUM_QA_STATE_v0.7.3.md`, ảnh trước/sau: `out/COLOSSEUM_VISUAL_v0.7.3_before_after.png`.

## Cách test (New Game)
Ô QA (Narshe: **lên 6, trái 4**) → `TECH v0.7.3 QA ACCESS` → `Item bank tests (v0.7.1)` →
`Shop / Colosseum / Battle` → `Colosseum (full battle)` → menu con:
1. `Get wager kit` → Elixir ×3, Fenix Down ×3, ThiefKnife, ValiantKnife.
2. `Fight: Terra/Locke/Celes/Edgar` → đội được **chuẩn hoá** tạm thời: Terra bỏ Magitek, Wedge/Vicks rời đội,
   Locke/Celes/Edgar vào đội → vào Colosseum → sau trận **trả lại** đội mở đầu (Terra lại cưỡi Magitek).

| # | Kiểm tra | PASS |
|---|---|---|
| V1 | Chọn **Terra** | Terra hiển thị bình thường, **không** có sprite thừa |
| V2 | Chọn **Locke**, **Celes**, **Edgar** (ít nhất 2) | đấu sĩ **hiện hình**, có tên + HP trong khung |
| V3 | Đòn đánh / hiệu ứng | hiển thị bình thường |
| V4 | Thắng / thua | thắng → nhận thưởng; thua → mất món cược |
| V5 | Về lại Narshe | màn hình sáng, điều khiển được; Terra lại trong Magitek; menu Party như cũ |
| V6 | Terra mang **QA Blade13D / QA Mail 13E / QA Charm13F** rồi đấu | vẫn mang đủ 3 món sau trận |
| V7 (nếu có save World of Ruin) | Colosseum **thật** (quầy tiếp tân), nhân vật thường | hiện hình bình thường, không sprite thừa |

Gợi ý: đối thủ của Elixir/Fenix Down là Cactrot (có thể thắng); ThiefKnife → Wart Puck.
Biggs/Wedge **không** dùng làm bằng chứng (nhân vật tạm, không tham gia Colosseum thật).
Các mục hồi quy v0.7.1/v0.7.2 không cần làm lại nếu không muốn (engine không đổi; emulator đã chạy lại tất cả).

---
PASS mẫu: `TECH v0.7.3 PASS — V1–V6 OK (Terra no extra sprite, Locke/Celes/Edgar visible, effects OK, win/loss/return OK, QA equipment kept)`.
