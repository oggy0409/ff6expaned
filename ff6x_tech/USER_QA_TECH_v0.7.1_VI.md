# FFVI Expanded Edition — TECH v0.7.1 Signature Equipment Bank — User QA (Tiếng Việt)

**ROM test:** `FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.sfc`
SHA-1 `c6ea2b3017e01da7a6049470215e35b962b345da` · CRC32 `65CF1731`
(hoặc patch `FF6X_Rev1_TECH_v0.7.1_ITEM_BANK_QA.bps` lên ROM Rev 1 sạch, SHA-1 `057ADA1C…`, CRC32 `C0FA0464`).
Kiểm tra hash trước. Dùng **New Game** với `.srm` mới (riêng bước L dùng save cũ).

**Cần kiểm tra gì:** ROM này có “ngân hàng trang bị mở rộng” (ID `$100-$13F`). Bản QA chỉ có 3 món thử nghiệm:

| ID | Tên trong game | Loại | Chỉ số |
|---|---|---|---|
| `$13D` | **QA Blade13D** | vũ khí (kiếm, hoạt ảnh của Epee) | Bat.Pwr 222, Hit 250, Vigor +7 |
| `$13E` | **QA Mail 13E** | áo giáp | Def 199, M.Def 177, Stamina +5 |
| `$13F` | **QA Charm13F** | relic | Speed +7, Mag.Pwr +7, Evade +30%, MBlock +30% |

Byte thấp của 3 món này trùng với **Chocobo Brsh / DaVinci Brsh / Magical Brsh** (`$3D/$3E/$3F`). Nếu ở đâu đó QA item
biến thành cây cọ (hoặc ngược lại) → **FAIL** (bị “cắt” ID).

**Ô QA:** New Game → khi điều khiển được ở Narshe → đi **lên 6, trái 4** → hộp thoại `TECH v0.7.1 QA ACCESS`:
- `Item bank tests (v0.7.1)` → menu thử vật phẩm
- `Monster/map tests (v0.6.1)` → các bài thử cũ của v0.6.1 (hồi quy)
- `No (Save Point)` → điểm save

Menu `Item bank tests`: `Get QA items 13D/13E/13F` · `Check / remove QA Blade13D` · `Shop / Colosseum / Battle`
(menu con: `Shop $48 (brushes)` · `Colosseum (wager list)` · `Battle: Terra w/o Magitek`).

## A. Nhận 3 món
1. Ô QA → Item bank tests → **Get QA items 13D/13E/13F** → thông báo “Got QA Blade13D, QA Mail 13E, QA Charm13F (extended) and vanilla items 3D/3E/3F.”
2. Mở Item: có **QA Blade13D ×1, QA Mail 13E ×1, QA Charm13F ×1** và **Chocobo Brsh ×1, DaVinci Brsh ×1, Magical Brsh ×1** — 6 dòng riêng, không gộp.
3. Lấy thêm lần nữa (bước ra rồi vào lại ô QA): mỗi món thành ×2, vẫn riêng với cây cọ.

## B. Tên / icon / mô tả
- Icon: QA Blade = icon kiếm, QA Mail = icon áo giáp, QA Charm = icon relic.
- Mô tả (dòng trên cùng khi trỏ vào): `QA weapon 13D / Bat.Pwr 222, Vigor 7 up` · `QA armor 13E / Def 199, MDef 177, Sta 5 up` · `QA relic 13F / Spd 7, Mag 7 up, Evade 30%`.
- Bấm A hai lần vào một món → trang chi tiết hiển thị đúng chỉ số.

## C. Vị trí trong giao diện
- Equip → Terra → R-Hand: danh sách có **QA Blade13D**. Body: **QA Mail 13E**. Relic → **QA Charm13F** ở danh sách relic.
- Không món nào xuất hiện sai ô (ví dụ QA Mail không có trong danh sách vũ khí).

## D. Trang bị / gỡ (và **3 món cùng lúc**)
1. Terra: R-Hand = QA Blade13D, Body = QA Mail 13E, Relic 1 = QA Charm13F → **cả 3 cùng được trang bị**; Item không còn 3 món đó (nếu chỉ có ×1).
2. Equip → **Remove** R-Hand → QA Blade13D về lại Item (đúng tên, không thành Chocobo Brsh).
3. Equip → **Empty** → vũ khí/giáp về Item; relic vẫn giữ. Relic → Remove → QA Charm13F về Item.

## E. Chỉ số thay đổi đúng
Khi Terra mang đủ 3 món (so với trước khi trang bị), trong màn Equip/Status:
Vigor **+7**, Speed **+7**, Stamina **+5**, Mag.Pwr **+7**, Evade **+30%**, MBlock **+30%**, Bat.Pwr rất cao (≈234),
Defense/M.Def tăng rất mạnh. Khi trỏ vào QA Blade13D trong danh sách R-Hand, phần xem trước cũng hiện Vigor/Bat.Pwr mới.

## F. Hoạt ảnh vũ khí / sát thương (trận thử)
1. Trang bị 3 món cho Terra. Ô QA → Item bank tests → Shop / Colosseum / Battle → **Battle: Terra w/o Magitek**
   (Terra tạm bỏ Magitek trong trận này, sau trận được trả lại).
2. Lượt của Terra → **Fight**: hoạt ảnh **kiếm kiểu Epee** (không phải cọ vẽ), sát thương lớn (≈145 lên lính gác).
3. Lượt của Terra → **Item** → di chuyển lên hàng R-Hand / L-Hand: R-Hand hiển thị **QA Blade13D**.
   - Chọn R-Hand rồi chọn Mithril Knife trong danh sách → **bị từ chối** (không đổi).
   - Chọn R-Hand rồi chọn L-Hand → hai tay **đổi chỗ** (cho phép). Sau trận: Equip hiện L-Hand = QA Blade13D, R-Hand = Buckler (không có ID lạ, không thành cọ).
   - Danh sách vật phẩm trong trận **không hiện** QA Mail/QA Charm (dòng trống, không dùng/ném được).
4. Thắng → về Narshe, Terra trở lại Magitek; trong Item, QA items vẫn đúng chỗ.

## G. Relic
Với QA Charm13F: Speed/Mag.Pwr/Evade/MBlock tăng như E; gỡ relic → các chỉ số trở về như cũ. QA Charm không có hiệu ứng đặc biệt.

## H. Arrange
Item → hàng trên → **Arrange**: QA Blade13D xếp cạnh vũ khí, QA Mail cạnh giáp, QA Charm cạnh relic; số lượng giữ nguyên, tên không đổi.
Di chuyển một món (chọn rồi thả vào vị trí khác) → tên vẫn đúng.

## I. Optimum
Equip → **Optimum** (khi QA Blade/QA Mail đang ở Item) → chọn QA Blade13D và QA Mail 13E; không nhân bản (mỗi món chỉ còn 1 bản ở nơi đúng).

## J. Save → reset/tắt máy → load
Ô QA → No (Save Point) → Save → **tắt/reset emulator** → Continue → vật phẩm mở rộng trong Item và trên người Terra giữ nguyên (tên, số lượng, chỉ số).

## K. Gỡ bằng event API mở rộng
Ô QA → Item bank tests → **Check / remove QA Blade13D**:
- Có QA Blade13D trong Item → `HAS EXT ITEM 13D: YES` → **Remove one (TAKE EXT ITEM)** → số lượng giảm 1.
- Không còn ở đâu → `HAS EXT ITEM 13D: NO`.
(Lưu ý: HAS tính cả món đang trang bị; TAKE chỉ lấy từ Item — xem KNOWN_RISKS R3.)

## L. Save cũ không có chữ ký → KHÔNG có vật phẩm “ma”
Load một save của v0.6.x hoặc ROM gốc Rev 1 (đã có Chocobo/DaVinci/Magical Brsh nếu được): **không** xuất hiện QA item nào;
cọ vẫn là cọ. Có thể save lại bình thường.

## M. Shop / Sell / Colosseum / Throw
1. Ô QA → … → **Shop $48 (brushes)** → Buy: số “đang có” của DaVinci Brsh **không** tính QA Mail 13E.
2. **Sell**: QA items là dòng trống, không chọn được; số lượng không đổi.
3. **Colosseum (wager list)**: QA items là dòng trống, không đặt cược được (thoát ra là được).
4. Trong trận: QA items không có trong Item/Throw.

## N. Vanilla không đổi
Cọ (`$3D/$3E/$3F`), đồ thường, mua bán, trận thường, menu Monster/map tests (v0.6.1: custom monster, Dark Wind, Magic Point, Map test A, Celes Annex) vẫn như trước.

---
PASS mẫu:

`TECH v0.7.1 PASS — A–N OK: 3 QA items received/stacked, names/icons/descriptions OK, all three equipped at once with correct stats, Remove/Empty/Optimum/Arrange OK, sword animation + damage in battle, R-hand replace refused / R<->L swap OK, save/reset/load OK, TAKE/HAS OK, old save has no phantom items, shop/sell/colosseum hide them, vanilla unchanged.`

Nếu FAIL: ghi bước (A–N), món nào, ảnh chụp màn hình, emulator + phiên bản, và gửi `.srm` / save state.
