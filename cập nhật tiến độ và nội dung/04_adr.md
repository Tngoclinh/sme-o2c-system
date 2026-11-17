# Architecture Decision Records

## ADR-01 — Modular monolith cho core O2C

- **Status:** Accepted.
- **Context:** Quy mô giả định 200–500 đơn/ngày, một nhóm nhỏ, nhiều transaction xuyên Order–Inventory–Payment; cần prototype và vận hành ít thành phần.
- **Decision drivers:** chi phí, transaction consistency, tốc độ phát triển, khả năng tách miền, observability.
- **Options:** microservices; serverless functions; modular monolith.
- **Decision:** một deployable modular monolith gồm các module Order, Inventory, Payment, Shipping, Return, Reconciliation; mỗi module sở hữu schema/table và public service/API nội bộ, không ghi chéo bảng.
- **Consequences tích cực:** triển khai đơn giản; transaction cục bộ; debug/tracing dễ; phù hợp SME.
- **Consequences tiêu cực:** scale theo cả ứng dụng; lỗi process có blast radius lớn hơn; cần dependency tests để tránh thành “big ball of mud”.
- **Trigger xem lại:** tải bền vững vượt khả năng scale-up, team độc lập cần release riêng, hoặc một module có profile tải/availability khác biệt đã đo được.
- **Trace:** P-06, NFR-01, NFR-07, WP0–WP2.

## ADR-02 — Atomic reservation + append-only inventory ledger

- **Status:** Accepted.
- **Context:** Oversell và nhập hàng hoàn lặp là rủi ro chính. Số tồn tổng hợp đơn thuần không giải thích được nguyên nhân thay đổi.
- **Decision drivers:** correctness, auditability, concurrency, khả năng sửa sai.
- **Options:** chỉ cập nhật `quantity`; distributed lock; reservation trong DB + ledger.
- **Decision:** PostgreSQL transaction khóa/compare-and-update bản ghi stock balance khi tạo reservation; unique `(order_id, sku)`; mọi thay đổi ghi StockEntry append-only; correction bằng entry đảo. Hàng hoàn vào `QC`, chỉ `RESTOCK` khi pass.
- **Invariant:** `on_hand = available + reserved + allocated + qc + quarantine`; các đại lượng không âm trừ adjustment được phê duyệt.
- **Consequences tích cực:** ngăn oversell, truy nguyên được, replay/report dễ.
- **Consequences tiêu cực:** nhiều bảng/entry hơn; cần transaction và index đúng; report cần aggregate.
- **Trigger xem lại:** contention DB đã được đo là bottleneck hoặc chuyển sang multi-warehouse.
- **Trace:** FR-02, FR-08, NFR-02, NFR-06, G-03.

## ADR-03 — Inbox/Outbox và idempotency cho PSP/ĐVVC

- **Status:** Accepted.
- **Context:** Callback có thể đến trễ, sai thứ tự hoặc lặp; GHN công bố cơ chế retry callback khi response không thành công. Gọi đối tác ngay trong transaction làm mất đồng bộ khi một phía commit và phía kia lỗi.
- **Decision drivers:** không mất sự kiện, không bút toán kép, phục hồi, audit.
- **Options:** gọi đồng bộ và retry trong request; message broker; transactional outbox + inbox trong DB.
- **Decision:** ghi domain change và OutboxEvent cùng transaction; worker gửi và retry exponential; inbound callback ghi InboxEvent với unique `(provider, external_event_id)` trước khi xử lý; xác thực signature/token, timestamp và mapping trạng thái; sự kiện quá ngưỡng vào manual queue.
- **Consequences tích cực:** at-least-once an toàn; không cần broker riêng; quan sát được backlog.
- **Consequences tiêu cực:** eventual consistency; phải có worker, retry policy, cleanup và ordering rule.
- **Trigger xem lại:** throughput/event latency vượt DB polling hoặc cần fan-out lớn; khi đó đánh giá broker nhưng giữ idempotent consumer.
- **Trace:** FR-03, FR-06, NFR-02, NFR-04, NFR-05.

## ADR-04 — Ledger và đối soát ba chiều cho COD/QR

- **Status:** Accepted.
- **Context:** Statement của carrier/PSP không đủ để chứng minh tiền thực nhận; sửa trực tiếp payment status làm mất audit và không biểu diễn phí/refund.
- **Decision drivers:** financial integrity, explainability, dispute handling, hai phương thức thanh toán.
- **Options:** status trên Order; match hai chiều statement–order; ledger + three-way reconciliation.
- **Decision:** Payment Ledger lưu entry EXPECTED, COLLECTED/PAID, SETTLED, FEE, REFUND, ADJUSTMENT; Reconciliation so khớp expected ledger ↔ provider statement ↔ bank settlement. Mismatch tạo case; adjustment cần actor, reason, evidence và approval.
- **Consequences tích cực:** giải thích được số dư/công nợ; hỗ trợ COD và QR; không che mất chênh lệch.
- **Consequences tiêu cực:** nhập statement và bank feed; matching phức tạp; cần quy tắc cut-off.
- **Trigger xem lại:** kết nối kế toán tổng hợp hoặc PSP hỗ trợ settlement real-time chuẩn hóa; vẫn giữ ledger là source of truth.
- **Trace:** FR-09…FR-13, NFR-06, NFR-08, G-02.

## Decision log

| ADR | Owner | Ngày | Bằng chứng cần giữ |
|---|---|---|---|
| ADR-01 | Architect/nhóm | 17/11/2026 | module dependency test, deployment diagram |
| ADR-02 | Inventory owner | 17/11/2026 | concurrent reservation test, ledger invariant |
| ADR-03 | Integration owner | 17/11/2026 | duplicate/out-of-order webhook test, retry log |
| ADR-04 | Kế toán + architect | 17/11/2026 | reconciliation fixture, balance equation |

