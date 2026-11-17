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

## ADR-03 — Inbox/Outbox và idempotency cho PSP/ĐVVC

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

## ADR-04 — Ledger và đối soát ba chiều cho COD/QR

**Nói đơn giản:** Không chỉ gắn nhãn “đã thanh toán” lên đơn. Hệ thống phải có sổ ghi từng khoản phải thu, đã thu, phí, đã chuyển và hoàn tiền; sau đó so sánh với bảng kê đối tác và ngân hàng.

- **Status:** Accepted.
- **Context:** Statement của carrier/PSP không đủ để chứng minh tiền thực nhận; sửa trực tiếp payment status làm mất audit và không biểu diễn phí/refund.
- **Decision drivers:** financial integrity, explainability, dispute handling, hai phương thức thanh toán.
- **Options:** status trên Order; match hai chiều statement–order; ledger + three-way reconciliation.
- **Decision:** Payment Ledger lưu entry EXPECTED, COLLECTED/PAID, SETTLED, FEE, REFUND, ADJUSTMENT; Reconciliation so khớp expected ledger ↔ provider statement ↔ bank settlement. Mismatch tạo case; adjustment cần actor, reason, evidence và approval.
- **Consequences tích cực:** giải thích được số dư/công nợ; hỗ trợ COD và QR; không che mất chênh lệch.
- **Consequences tiêu cực:** nhập statement và bank feed; matching phức tạp; cần quy tắc cut-off.
- **Trigger xem lại:** kết nối kế toán tổng hợp hoặc PSP hỗ trợ settlement real-time chuẩn hóa; vẫn giữ ledger là source of truth.
- **Trace:** FR-08, FR-09, FR-10, FR-11, REQ-COD-02, EXT-03, NFR-06, NFR-08, G-02.

## Decision log

| ADR | Owner | Ngày | Bằng chứng cần giữ |
|---|---|---|---|
| ADR-01 | Architect/nhóm | 17/11/2026 | module dependency test, deployment diagram |
| ADR-02 | Inventory owner | 17/11/2026 | concurrent reservation test, ledger invariant |
| ADR-03 | Integration owner | 17/11/2026 | duplicate/out-of-order webhook test, retry log |
| ADR-04 | Kế toán + architect | 17/11/2026 | reconciliation fixture, balance equation |

