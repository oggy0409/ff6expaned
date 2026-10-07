# FFVI Expanded Edition — TECH v0.9.3 Visual State / VRAM Hotfix — User QA (Tiếng Việt, ~5–10 phút)

Chỉ kiểm lại 4 lỗi hình ảnh của v0.9.2 (V1–V4). Mọi thứ khác bạn đã PASS ở v0.9.2 (vật phẩm, cửa hàng, save,
Praetor 70% / 40% / Grounding Field, E5, E7, logic E8) **không cần làm lại**: các byte đó không đổi. Bản production /
celes-tech v0.9.1 cũng không đổi.

Nguyên nhân ngắn gọn (chi tiết trong `ROOT_CAUSE_VISUAL_v0.9.3.md`):
* **V2 / V3:** ngay sau New Game, đội là Terra + Wedge + Vicks, cả ba đều trong giáp Magitek. Hub QA v0.9.2 chỉ gỡ
  Magitek cho Terra, nên giáp của Wedge / Vicks đè lên ô VRAM của quái: đầu chó Lunaris và con Bit thứ hai. Giờ hub
  tự chuẩn hoá đội.
* **V1:** palette mới gần như trùng màu gốc.
* **V4:** các ô thay đổi trông như tường.

## ROM
| ROM | SHA-1 | CRC32 |
|---|---|---|
| `FF6X_Rev1_TECH_v0.9.3_VISUAL_STATE_VRAM_HOTFIX_QA.sfc` | `15af77fe9c01f54844fbcbbb0c5f1d65768d55f0` | `02DA7373` |

Hoặc patch `.bps` lên ROM Rev 1 sạch (CRC32 `C0FA0464`). Dùng **file `.srm` mới** (không dùng save của v0.9.2).

**Quan trọng:** làm đúng như lần trước — New Game rồi vào thẳng menu QA, **không** chọn Party preset. Đây chính là
đường đã gây lỗi.

Menu: Narshe, ô QA (**lên 6, trái 4**) → `TECH v0.9.3 QA ACCESS` → `Celes enablers v0.9.2`.

## Checklist
| # | Làm | PASS khi |
|---|---|---|
| H0 | New Game → ô QA → `Older QA (v0.9 tree) → More… → More… → Save Point` → **Save** | có save ở Narshe để quay lại sau H2 |
| H1 | `Celes enablers → More… → More… → Walk into the outer map`, đi **lên 13** ô | nền bản đồ (sàn, tường) màu **xám tro / thép**, rõ ràng khác màu hồng-nâu gốc, vẫn dễ nhìn. Đội là **Terra, Locke, Celes, Edgar**; Terra đi bộ bằng hình người (không còn giáp Magitek). Tường trên: **không có bia tưởng niệm**, cửa lưu trữ (phía trên bên phải) là **cửa song sắt đóng** |
| H2 | Reset → Continue save H0 → `Celes enablers → WoR aboard the Falcon` → **B** hạ cánh → đi lại (không đeo Moogle Charm) cho tới khi gặp quái. Nếu chưa gặp con chó, đi lên vùng **đất nâu** gần đó | menu trận đầu tiên là **Fight** (không phải **MagiTek**). Con chó **Lunaris** có **đầu đầy đủ**, thân nguyên vẹn, không có ô rác. Mọi quái khác cũng sạch |
| H3 | Reset → Continue → `Items v0.9.1 → Grant all 8 consumables` → `Celes enablers → Praetor battle (E2-E4) → QA-scaled`. Dùng **2 MagitekCell** lên Praetor | trận đánh với Fight / Terra Locke Celes Edgar (không có Wedge / Vicks). Khi Praetor ≤ 70%, **hai Suppressor Bit xuất hiện và giống hệt nhau** (không ô rác ở con bên phải). Một Bit có thể **loé thành viền trắng** trong chưa tới nửa giây khi nó niệm phép (Rflect): đó là hiệu ứng gốc của game, không phải lỗi. Hãy nhìn sau khi hết loé. (Tuỳ chọn) `Locked stats`: hai Bit cũng giống nhau khi hiện ra |
| H4 | `Celes enablers → More… → Outer map states (E8)`: lần lượt `More… → Reset all states` → `Walk into the outer map` (lên 13); rồi `Arc done + PRESERVE` → vào; rồi `Arc done + BURN` → vào; rồi `PRESERVE` + `More… → Graves Without Names done` → vào | **RESET:** tường trơn, cửa song sắt đóng. **PRESERVE:** bảng tên sáng (thẻ treo) ở trái + cửa lưu trữ **mở với các kệ hồ sơ** (thanh sáng ngang, có ánh nhấp nháy). **BURN:** bảng tên + cửa **cháy đen với đống đổ nát**. **GRAVES:** bảng tên được thay bằng **bia đá: 4 trụ đá sáng trên đế đinh tán**; cửa vẫn là kệ hồ sơ |
| H5 | Với PRESERVE + GRAVES: `Older QA → More… → More… → Save Point` → Save → **Reset** → Continue → `Walk into the outer map` | bia đá + kệ hồ sơ vẫn còn, giống hệt H4. (Tuỳ chọn) đi vào qua WoR (H2), ra rồi vào lại: vẫn như vậy |

Các ô của trạng thái E8 đều là ô cản: không đi vào trong tường được (builder kiểm tra cả 9 tổ hợp trạng thái).

---
Báo PASS mẫu: `TECH v0.9.3 PASS — H1 ash palette, H2 Lunaris clean, H3 both Bits identical, H4 4 states visible, H5 persists`.
Nếu FAIL: ghi số bước, kèm ảnh chụp màn hình và tên emulator.
