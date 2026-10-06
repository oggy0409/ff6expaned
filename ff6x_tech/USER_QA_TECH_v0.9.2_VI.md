# FFVI Expanded Edition — TECH v0.9.1 Item Alignment + v0.9.2 Celes Enablers — User QA (Tiếng Việt, ~25–30 phút)

Một lượt QA duy nhất cho cả hai mốc: **A. v0.9.1** (căn chỉnh dữ liệu vật phẩm theo D-16 .. D-20: số hồi chính xác,
4 cửa hàng tái thiết, Magitek Cell, Darill's Coin) và **B. v0.9.2** (các enabler E1–E9 cho arc Celes, **chỉ có trong ROM
QA**, đồ họa giữ chỗ). Phía Claude đã chạy emulator đầy đủ (`REGRESSION_REPORT_v0.9.2.md`); bước này là **USER RUNTIME
QA**. Chưa có cốt truyện Celes / CONTENT v1.0 — mọi chữ "QA E…" là chữ kiểm thử.

## ROM
| ROM | SHA-1 | CRC32 | Dùng cho |
|---|---|---|---|
| `FF6X_Rev1_TECH_v0.9.2_ITEM_ALIGNMENT_CELES_ENABLERS_QA.sfc` | `697a25e886e843ad356d98cdfb078fcba7c8615f` | `7EA0481F` | **toàn bộ checklist** |
| `FF6X_Rev1_TECH_v0.9.1_PRODUCTION.sfc` | `2dc73bfbbcf4657eb59eec93bd614181ecdc817c` | `01AE6F84` | bước 14 (tùy chọn) |
| `FF6X_Rev1_TECH_v0.9_CONSUMABLE_RARE_QA.sfc` (bản v0.9 đã duyệt) | `e1136805cc792e11dbffab15e87df0f327a6a12e` | `D8183069` | bước 13 (save cũ) |

Hoặc patch `.bps` tương ứng lên ROM Rev 1 sạch (CRC32 `C0FA0464`).

## Vào menu QA
New Game → Narshe: ô QA (**lên 6, trái 4**) → `TECH v0.9.2 QA ACCESS`:
* `Items v0.9.1` → `Grant all 8 consumables` (×5 mỗi món) · `Reconstruction shops` (`Rebuilt Mobliz (80)` · `Reopened
  Narshe Forge (81)` · `More…` → `Rebuilt Doma (82)` · `Figaro Foundry (83/84)` · `Toggle Celes arc done`) · `More…` →
  `Consumable test battle` · `Party presets` · `Get 50000 GP (QA)`.
* `Celes enablers v0.9.2` → `WoR aboard the Falcon (E1)` · `Praetor battle (E2-E4)` · `More…` → `Outer map states (E8)` ·
  `Party presets (E5)` · `More…` → `Walk into the outer map` · `Vale visible on/off`.
* `Older QA (v0.9 tree)` = nguyên menu v0.9 đã duyệt (Consumables v0.9 / Rare items v0.9 / More… → Stress / save,
  Equipment v0.8, More… → Older tests · **Save Point**).

Bản đồ thử `$1A2` (Vector Outer Ward, lối vào ở (16,27)): đi **lên 13** là tới hàng giữa (16,14). Từ đó: **trái 6, lên 2**
= bảng tưởng niệm (memorial) · **phải 4, lên 2** = cửa lưu trữ (archive) · **lên 2** = bàn điều khiển Praetor ·
người sống sót (survivor) đứng ngay bên phải ô (20,14) · Vale ở (11,13) (nói chuyện từ (11,14), quay lên). Lối ra: từ
lối vào đi **xuống 2**.

## Checklist
**Mẹo:** ngay khi tới ô QA lần đầu, `Older QA → More… → More… → Save Point` → **Save** (slot riêng). Bước 11 đưa
đội sang World of Ruin và không có đường về Narshe: xong bước 11 thì Reset → **Continue** save đó để làm tiếp.

| # | Làm | PASS khi |
|---|---|---|
| **A. v0.9.1 vật phẩm** | | |
| 1 | `Items v0.9.1` → `Grant all 8 consumables` → mở **Item** | 8 món ×5; mô tả: Gaia Tonic = một đồng minh, 1500 HP + Regen; AetherFlask = 100 MP; Iron Ration = 600 HP; Remedy+ = như Remedy + Zombie; MagitekCell = một kẻ địch, Lightning + không thuộc tính |
| 2 | `Older QA → Consumables v0.9 → More… → Field-use setup (P1)` → Item: **Iron Ration** cho Terra, **Gaia Tonic** cho Locke (dùng Phoenix Ash trước nếu Locke KO), **AetherFlask** cho Celes | Iron Ration hồi **đúng 600** (hoặc tới tối đa) và **không** chữa Poison; Gaia Tonic hồi **1500** (tối đa); Aether hồi **100 MP** (tối đa); mỗi món giảm 1 |
| 3 | `Items → More… → Consumable test battle`. Trong trận: **Gaia Tonic** cho một người | chỉ chọn **một** người; số hồi hiện **1500**; sau đó HP người đó tự hồi từng chút (Regen, khoảng 80 mỗi lần — **không** bao giờ 1500) |
| 4 | Cùng trận: **Null Dust** (con trỏ mặc định ở kẻ địch — dời con trỏ sang người vừa có Regen); **Iron Ration** / **AetherFlask** cho một người | Null Dust chỉ một mục tiêu, Regen của người đó biến mất (HP ngừng tự hồi); số hiện **600** / **100** |
| 5 | Cùng trận: **MagitekCell** lên một lính; **BeaconFlare** lên cả nhóm | MagitekCell: một mục tiêu, hoạt ảnh tia sét Magitek, số **800**, không tốn MP; BeaconFlare: Fire lên mọi lính. Thắng trận, số lượng đúng |
| 6 | `Items → Reconstruction shops` → `Rebuilt Mobliz (80)` → Buy | Iron Ration (300), Remedy, Fenix Down, Gaia Tonic (2000), Gaia Gear. Mua được, trừ GP đúng (`Get 50000 GP` nếu thiếu) |
| 7 | `Reopened Narshe Forge (81)` → Buy; `More… → Rebuilt Doma (82)` → Buy | 81: Flame Sabre, Blizzard, ThunderBlade, Gold Shld, Diamond Shld — **không có** TemperedEdge. 82: Forged, Tempest, Murasame, Ninja Gear, Head Band, Fire Skean, Water Edge, Bolt Edge — **không có** Doma Edge. Không có đồ tối thượng |
| 8 | `Older QA → Consumables v0.9 → More… → More… → Remove all 8` (về 0 MagitekCell). `Items → Reconstruction shops → More… → Figaro Foundry (83/84)` → Buy | **Chưa** xong arc: chỉ đồ nghề của Edgar (6 món), **không** có MagitekCell |
| 9 | `Toggle Celes arc done` (hiện "arc DONE") → `Figaro Foundry` → Buy MagitekCell | MagitekCell (1500; 750 nếu Edgar dẫn đầu) xuất hiện cuối danh sách; số lượng mua tối đa **3** (không lên được 4); mua 3, thoát, vào lại → **không** mua thêm được. Sell 1 → mua lại được đúng 1. MagitekCell bán được (½ giá). `Toggle` lần nữa → Foundry lại chỉ có đồ nghề |
| 10 | `Older QA → More… → Equipment v0.8 → Grant all 39`; `Items → More… → Party presets → More… → Terra Setzer Strago Relm` → Equip → **Relic**: Darill'sCoin cho Setzer | chỉ số khi chọn: **Magic +2** (cùng Speed +5); mô tả ghi Magic +2 |
| **B. v0.9.2 enabler Celes** | | |
| 11 | `Celes enablers → WoR aboard the Falcon (E1)`. (Nên) đang bay: mở menu → Relic → **Moogle Charm** (QA vừa tặng) cho người dẫn đầu, tránh gặp quái WoR. Bấm **B** để hạ cánh, đi **lên 2** ô | vào bản đồ `$1A2` (màu xám tro / sắt / ngà — palette mới). Đi **xuống 2** → ra lại World of Ruin **cạnh tàu Falcon đang đậu**; bước lên tàu + **A** → bay lại được |
| 12 | `Items → Grant all 8 consumables` (cần ≥5 MagitekCell) → `Celes enablers → Praetor battle → QA-scaled (4780 HP, weak)`. Chỉ dùng **MagitekCell** lên Praetor | lúc đầu **chỉ có Praetor** (đánh trước, không có pincer/back/side). Cell 1: **1200**. Cell 2: **1200** → **2 Suppressor Bit xuất hiện** (≤70%). Cell 3: **1200** → Praetor **đổi màu** (overload ≤40%, Haste) và **Grounding Field** bật. Cell 4: chỉ **400** |
| 13a | Tiếp trận 12: chờ **3 lượt Praetor** (đánh các Bit hoặc dùng Potion cho đồng đội — **không** đánh Praetor), rồi Cell 5 | Cell 5 lại **1200** (Grounding Field hết hạn; nếu vẫn 400 thì chờ thêm một lượt Praetor) → Praetor chết, mọi Bit biến mất, về Narshe. Vào lại trận QA-scaled: mọi thứ bắt đầu lại từ đầu (Praetor một mình, màu gốc, Cell 1 = 1200) |
| 13b | (Tùy chọn) `Praetor battle → Locked stats (47800 HP)` | trận bắt đầu bình thường, chỉ Praetor; chạy trốn / thua đều được (đây chỉ là chỉ số khoá thật) |
| 14 | `Celes enablers → More… → Party presets (E5)` → `Terra Locke Celes Edgar` → `More… → Walk into the outer map` → nói chuyện với **survivor** | 2 câu: câu gốc + câu của **LOCKE**. Lặp lại với `Terra Celes Edgar Sabin` → câu của **EDGAR**; với `Terra Celes only` → chỉ câu gốc + "line dropped" |
| 15 | `Celes enablers → More… → More… → Vale visible on/off` (bật) → vào bản đồ | Vale xuất hiện ở (11,13), màu khác NPC thường (palette mới); nói chuyện được. Tắt lại → Vale biến mất |
| 16 | `More… → Outer map states (E8)` → `Arc done + PRESERVE` → vào bản đồ, đọc memorial + archive | tường memorial = **tag wall tạm**, archive = **retained** (hình ô khác lúc chưa có trạng thái). `Arc done + BURN` → archive **burned**; `More… → Graves Without Names done` → memorial **bằng đá**; `Reset all states` → về "no memorial / sealed" |
| 17 | Đặt `PRESERVE` + `Graves`. `Older QA → More… → More… → Save Point` → **Save** → Reset → **Continue** → vào bản đồ | memorial bằng đá + archive retained vẫn còn sau khi tắt/mở máy |
| **Save / hồi quy v0.9** | | |
| 18 | Bước 1–17 xong: Save → Reset → Continue | vật phẩm, số lượng, trang bị, GP, key item giữ nguyên |
| 19 | Mở một save **v0.9** cũ (file `.srm` từ lượt QA v0.9, đổi tên cho khớp ROM v0.9.2) | mọi món v0.9 (39 trang bị, 8 vật phẩm tiêu hao, key item, đồ đang mặc) giữ nguyên; một Gaia Tonic cũ giờ hồi **1500** (hiệu ứng mới). (Tùy chọn) save này mở bằng ROM PRODUCTION v0.9.1 cũng giữ nguyên |
| 20 | Hồi quy nhanh: `Older QA → Rare items v0.9 → Grant all 5` → Item → RARE; `Older QA → More… → Stress / save → More… → Colosseum` | 5 key item, mô tả Triune Sigil mới (dấu ấn riêng của Triune Sentinel); Colosseum không cho cược vật phẩm mới, trận chạy và quay về Narshe |

Ghi chú:
* Đồ họa Praetor (Guardian), Bit (Spit Fire), màu overload, bản đồ `$1A2` và Vale đều là **placeholder** (D-14).
* Trận **QA-scaled** (`$245`, 1/10 HP, tấn công 1) chỉ để QA tay; trận khoá thật là `$244` (bước 13b).
* MagitekCell giới hạn 3 **khi mua**; `Grant all 8` của QA cho 5 (đúng: quà sự kiện không bị giới hạn, `KNOWN_RISKS_v0.9.2.md` R51).
* Figaro Foundry giảm nửa giá khi Edgar dẫn đầu (quy tắc vanilla): MagitekCell 750.

---
Báo PASS mẫu: `TECH v0.9.2 PASS — 1–20 OK (exact 1500/600/100, Regen, Null Dust, Magitek Cell 800/1200/400, shops 80-84 + cap 3, Darill's Coin Mag+2, WoR→$1A2→Falcon, Praetor 70%/40%/Grounding, E5/E7/E8 + persistence, save v0.9 → v0.9.2)`.
Nếu FAIL: ghi số bước + ảnh chụp màn hình (+ số liệu thấy trên màn hình).
