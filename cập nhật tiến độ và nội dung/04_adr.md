# Architecture Decision Records

## ADR là gì và đọc thế nào?

ADR (Architecture Decision Record) là **phiếu ghi quyết định kiến trúc**. Mỗi phiếu trả lời:

1. Nhóm đang gặp vấn đề gì (`Context` — bối cảnh)?
2. Điều gì quan trọng khi lựa chọn (`Decision drivers` — tiêu chí quyết định)?
3. Có những phương án nào (`Options`)?
4. Nhóm chọn gì và vì sao (`Decision`)?
5. Lựa chọn mang lại lợi ích và bất lợi gì (`Consequences`)?
6. Khi nào cần xem xét lại quyết định (`Trigger xem lại`)?

ADR không khẳng định phương án được chọn là tốt nhất cho mọi hệ thống; nó chỉ chứng minh phương án đó hợp lý với quy mô và ràng buộc của đề tài.

## ADR-01 — Modular monolith cho core O2C

**Nói đơn giản:** Chạy các phân hệ trong một ứng dụng để dễ làm và dễ vận hành, nhưng vẫn chia ranh giới Order, Kho, Thanh toán… thật rõ trong mã nguồn.

- **Status:** Accepted.
- **Context:** Quy mô giả định theo đề II-B là 100–300 đơn/ngày, một nhóm nhỏ, nhiều transaction xuyên Order–Inventory–Payment; cần prototype và vận hành ít thành phần.
- **Decision drivers:** chi phí, transaction consistency, tốc độ phát triển, khả năng tách miền, observability.
- **Options:** microservices; serverless functions; modular monolith.
- **Decision:** một deployable modular monolith gồm các module Order, Inventory, Payment, Shipping, Return, Reconciliation; mỗi module sở hữu schema/table và public service/API nội bộ, không ghi chéo bảng.
- **Consequences tích cực:** triển khai đơn giản; transaction cục bộ; debug/tracing dễ; phù hợp SME.
- **Consequences tiêu cực:** scale theo cả ứng dụng; lỗi process có blast radius lớn hơn; cần dependency tests để tránh thành “big ball of mud”.
- **Trigger xem lại:** tải bền vững vượt khả năng scale-up, team độc lập cần release riêng, hoặc một module có profile tải/availability khác biệt đã đo được.
- **Trace:** AP-05, NFR-01, NFR-07, WP-01–WP-02.

## ADR-02 — Atomic reservation + append-only inventory ledger

**Nói đơn giản:** Khi khách đặt hàng, thao tác giữ hàng phải hoàn tất trọn vẹn; mọi lần hàng tăng/giảm đều được ghi vào sổ lịch sử và không xóa bản ghi cũ.

- **Status:** Accepted.
- **Context:** Oversell và nhập hàng hoàn lặp là rủi ro chính. Số tồn tổng hợp đơn thuần không giải thích được nguyên nhân thay đổi.
- **Decision drivers:** correctness, auditability, concurrency, khả năng sửa sai.
- **Options:** chỉ cập nhật `quantity`; distributed lock; reservation trong DB + ledger.
- **Decision:** PostgreSQL transaction khóa/compare-and-update bản ghi stock balance khi tạo reservation; unique `(order_id, sku)`; mọi thay đổi ghi StockEntry append-only; correction bằng entry đảo. Hàng hoàn vào `QC`, chỉ `RESTOCK` khi pass.
- **Invariant:** `on_hand = available + reserved + allocated + qc + quarantine`; các đại lượng không âm trừ adjustment được phê duyệt.
- **Consequences tích cực:** ngăn oversell, truy nguyên được, replay/report dễ.
- **Consequences tiêu cực:** nhiều bảng/entry hơn; cần transaction và index đúng; report cần aggregate.
- **Trigger xem lại:** contention DB đã được đo là bottleneck hoặc chuyển sang multi-warehouse.
- **Trace:** FR-02, FR-07, REQ-COD-03, NFR-03, NFR-06, G-04.

## ADR-03 — Inbox/Outbox và idempotency cho Đơn vị QR/ĐVVC

**Nói đơn giản:** Lưu thông điệp nhận vào và cần gửi ra trong cơ sở dữ liệu. Nếu mạng lỗi hoặc đối tác gửi lặp, hệ thống có thể thử lại mà không tạo đơn, vận đơn hay khoản tiền trùng.

- **Status:** Accepted.
- **Context:** Callback có thể đến trễ, sai thứ tự hoặc lặp; GHN công bố cơ chế retry callback khi response không thành công. Gọi đối tác ngay trong transaction làm mất đồng bộ khi một phía commit và phía kia lỗi.
- **Decision drivers:** không mất sự kiện, không bút toán kép, phục hồi, audit.
- **Options:** gọi đồng bộ và retry trong request; message broker; transactional outbox + inbox trong DB.
- **Decision:** ghi domain change và OutboxEvent cùng transaction; worker gửi và retry exponential; inbound callback ghi InboxEvent với unique `(provider, external_event_id)` trước khi xử lý; xác thực signature/token, timestamp và mapping trạng thái; sự kiện quá ngưỡng vào manual queue.
- **Consequences tích cực:** at-least-once an toàn; không cần broker riêng; quan sát được backlog.
- **Consequences tiêu cực:** eventual consistency; phải có worker, retry policy, cleanup và ordering rule.
- **Trigger xem lại:** throughput/event latency vượt DB polling hoặc cần fan-out lớn; khi đó đánh giá broker nhưng giữ idempotent consumer.
- **Trace:** FR-04, FR-05, FR-06, EXT-01, NFR-03, NFR-04, NFR-05.

## ADR-04 — Đối soát COD gross và hóa đơn vận chuyển tách riêng

**Nói đơn giản:** Tiền khách trả và chi phí giao hàng của shop là hai luồng khác nhau. ĐVVC chuyển đủ tiền COD đã thu; hóa đơn phí vận chuyển được kiểm tra và thanh toán riêng, không trừ vào COD.

- **Status:** Accepted.
- **Context:** Shop thu của khách `grand_total = tiền hàng sau giảm giá + phí vận chuyển thu khách`. ĐVVC vừa thu hộ COD vừa cung cấp dịch vụ giao hàng, nên nếu trừ phí thẳng vào COD sẽ khó phân biệt thiếu tiền với chi phí. Bảng kê đối tác một mình cũng không chứng minh tiền thực nhận.
- **Decision drivers:** toàn vẹn tài chính, dễ giải thích, kiểm soát chênh lệch, đúng chính sách hóa đơn tháng và hai phương thức thanh toán.
- **Options:** (1) ĐVVC net-off phí vào COD; (2) chỉ lưu trạng thái đã thanh toán trên Order; (3) chuyển đủ COD gross, hóa đơn vận chuyển tách riêng và ledger + three-way reconciliation.
- **Decision:** chọn phương án 3. Payment Ledger lưu `EXPECTED`, `COLLECTED/PAID`, `REMITTED`, `REFUND`, `ADJUSTMENT`; không ghi carrier invoice vào Payment Ledger. COD theo tháng: shop so sơ bộ expected theo đơn ↔ ĐVVC báo đã thu, xử lý mismatch; ĐVVC chuyển gross; bank credit hoàn thành đối soát ba chiều và đóng kỳ. CarrierInvoice được so riêng với shipment/tracking và biểu phí, sau đó shop thanh toán bằng dòng tiền ra riêng. QR intent bằng grand total, Đơn vị QR callback/bảng kê, giả định phí QR bằng 0; vận đơn QR có COD amount bằng 0. Mismatch tạo case; adjustment cần actor, reason, evidence và approval.
- **Invariant:** `COD expected = COD collected = COD remitted + COD discrepancy`; `QR expected = QR paid = bank credited + QR discrepancy`; carrier invoice không xuất hiện trong hai phương trình này.
- **Consequences tích cực:** biết khách đã trả đủ hay chưa; không nhầm phí ĐVVC thành thiếu COD; dễ kiểm tra hóa đơn/thanh toán riêng; hỗ trợ COD và QR.
- **Consequences tiêu cực:** phải quản lý hai chu kỳ tháng độc lập (COD remittance và carrier invoice); cần import bảng kê, hóa đơn, bank feed và quy tắc cut-off.
- **Trigger xem lại:** hợp đồng ĐVVC đổi sang net-off bắt buộc hoặc kết nối kế toán tổng hợp; khi đó tạo ADR mới và vẫn giữ các entry tách biệt.
- **Trace:** FR-08, FR-09, FR-10, FR-11, REQ-COD-02, EXT-03, NFR-06, NFR-08, G-02.

## Decision log

| ADR | Owner | Ngày | Bằng chứng cần giữ |
|---|---|---|---|
| ADR-01 | Architect/nhóm | 17/11/2026 | module dependency test, deployment diagram |
| ADR-02 | Inventory owner | 17/11/2026 | concurrent reservation test, ledger invariant |
| ADR-03 | Integration owner | 17/11/2026 | duplicate/out-of-order webhook test, retry log |
| ADR-04 | Kế toán + architect | 17/11/2026 | reconciliation fixture, balance equation |

