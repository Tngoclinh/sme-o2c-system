# ArchiMate 3.2 — mô hình chuẩn hóa

## 1. Modeling convention

ArchiMate được dùng để tạo cái nhìn tổng quan và liên kết các lớp; BPMN được dùng cho chi tiết luồng. Mỗi view phải ghi rõ stakeholder, concern và purpose. Tên phần tử là danh từ với active structure/object/service và động từ với process/function. Không dùng `Flow` thay cho mọi quan hệ.

Các quan hệ sử dụng:

- `Assignment`: actor/component/node thực hiện behavior.
- `Realization`: process/function hiện thực service; data object hiện thực business object; artifact hiện thực data object.
- `Serving`: service/component/layer dưới phục vụ behavior/layer trên.
- `Access`: behavior đọc/ghi passive structure.
- `Triggering`: quan hệ thời gian/nhân quả giữa behavior/event.
- `Flow`: truyền dữ liệu, tiền hoặc hàng hóa; luôn ghi nhãn đối tượng được truyền.
- `Influence`: driver/assessment/principle tác động goal/requirement.

## 2. Viewpoint A — Motivation

**Stakeholder:** chủ shop, kế toán, kho. **Concern:** tại sao thay đổi và thành công là gì. **Purpose:** quyết định/phê duyệt.

| Loại | Phần tử |
|---|---|
| Stakeholder | Chủ doanh nghiệp; Khách hàng; Kế toán; Kho; CSKH; IT |
| Driver | Tăng đơn online; giao thất bại/RTO; khó đối soát COD/QR; lệch tồn; kỳ vọng đổi/trả minh bạch |
| Assessment | Dữ liệu phân tán; thao tác lặp; không có correlation ID; trạng thái trộn; thiếu audit |
| Goal | G-01…G-05 trong TOGAF |
| Outcome | O-01 Đơn xuyên suốt; O-02 tiền giải thích được; O-03 tồn chính xác; O-04 return có kiểm soát; O-05 tích hợp phục hồi |
| Principle | P-01…P-06 |
| Requirement | FR-01…FR-13; NFR-01…NFR-09 |

Quan hệ cốt lõi: Stakeholder `Association` Driver; Driver/Assessment `Influence` Goal; Outcome `Realization` Goal; Principle `Influence` Requirement; Requirement `Realization` Outcome. View chỉ hiển thị nhóm requirement liên quan để tránh quá tải, còn matrix giữ quan hệ đầy đủ.

## 3. Viewpoint B — Business Process Cooperation

**Stakeholder:** vận hành, kho, kế toán, CSKH. **Concern:** ai làm gì và trao đổi gì. **Purpose:** thiết kế/coherence.

### 3.1 Active structure

| Business Actor | Business Role được gán |
|---|---|
| Khách hàng | Người mua |
| SME | Sales/CS, Warehouse, Accountant, Owner |
| Đơn vị vận chuyển | Carrier |
| PSP/Ngân hàng | Payment Provider |

### 3.2 Behavior và service

| Business Process | Business Service được hiện thực | Role thực hiện | Business Object được access |
|---|---|---|---|
| P1 Capture & Confirm Order | Order Placement Service | Người mua, Sales/CS | Order, Payment Instruction |
| P2 Reserve & Fulfill | Fulfillment Service | Warehouse | Order, Reservation, Stock Record |
| P3 Collect/Confirm Payment | Payment Service | Accountant + PSP | Payment, QR Reference, COD Receivable |
| P4 Deliver & Handle Failure | Delivery Tracking Service | Carrier + Sales/CS | Shipment, Delivery Attempt |
| P5 Return/Exchange & QC | Return/Exchange Service | Sales/CS + Warehouse | RMA, Returned Item, QC Result |
| P6 Reconcile & Close | Reconciliation Service | Accountant | Statement, Settlement, Discrepancy Case |

Business Event `Order submitted` triggers P1; `Payment confirmed/COD accepted` triggers P2; `Parcel handed over` triggers P4; `Delivery failed/Return requested` triggers P5 theo biến thể; `Statement received` triggers P6. Flow ghi nhãn `order`, `parcel`, `payment`, `statement`, không dùng flow không nhãn.

## 4. Viewpoint C — Application Usage

**Stakeholder:** product owner, architect, developer. **Concern:** component nào hỗ trợ process nào. **Purpose:** thiết kế target.

### 4.1 Component, function và service

| Application Component | Application Function | Application Service hiện thực | Phục vụ Business Process |
|---|---|---|---|
| Storefront/Backoffice | Customer/Admin Interaction | Order UI; Operations UI | P1–P6 |
| Order | Order Lifecycle | Order Management Service | P1, P2 |
| Inventory | Reservation & Stock Ledger | Inventory Service | P2, P5 |
| Payment | Payment Intent & Ledger | Payment Service | P1, P3, P5, P6 |
| Fulfillment/Shipping | Shipment Lifecycle | Shipping Service | P2, P4 |
| Return | RMA & Disposition | Return Service | P5 |
| Reconciliation/Reporting | Matching, Case & Analytics | Reconciliation Service; Reporting Service | P6 |
| Carrier Adapter | Carrier Translation | Carrier Integration Service | P2, P4, P6 |
| PSP Adapter | PSP Translation | PSP Integration Service | P3, P5, P6 |

Quan hệ: Component `Assignment` Function; Function `Realization` Application Service; Application Service `Serving` Business Process; Function `Access` Data Object. Giữa component chỉ dùng `Serving` khi cung cấp chức năng, `Flow` khi cần nhấn mạnh dữ liệu/sự kiện truyền.

### 4.2 Data Object và ownership

| Data Object | Owner | Trạng thái chính / quy tắc |
|---|---|---|
| Order | Order | DRAFT → PENDING_PAYMENT/CONFIRMED → FULFILLING → COMPLETED/CANCELLED; không chứa shipment state |
| Reservation | Inventory | ACTIVE → COMMITTED/RELEASED/EXPIRED |
| StockEntry | Inventory | Append-only: RESERVE, RELEASE, SHIP, RETURN_TO_QC, RESTOCK, QUARANTINE, ADJUST |
| Payment | Payment | PENDING → AUTHORIZED/PAID/FAILED/EXPIRED → PARTIALLY_REFUNDED/REFUNDED |
| PaymentEntry | Payment | Append-only expected/collected/settled/fee/refund/adjustment |
| Shipment | Fulfillment/Shipping | CREATED → HANDED_OVER → IN_TRANSIT → DELIVERED/FAILED → RETURNING/RETURNED |
| ShipmentEvent | Fulfillment/Shipping | external_event_id unique, raw status + canonical status |
| Return/RMA | Return | REQUESTED → APPROVED/REJECTED → IN_TRANSIT → RECEIVED → QC_PASSED/QC_FAILED → CLOSED |
| Statement/Settlement | Reconciliation | IMPORTED → MATCHED/PARTIAL/DISCREPANT → CLOSED |
| ReconciliationCase | Reconciliation | OPEN → INVESTIGATING → RESOLVED/WRITTEN_OFF |
| OutboxEvent/InboxEvent | Module phát/nhận | PENDING → SENT/PROCESSED/FAILED; idempotency key unique |

Business Object được Data Object tương ứng `Realization`; file CSV/PDF gốc được mô hình là Artifact hiện thực Data Object Statement.

## 5. Viewpoint D — Technology

**Stakeholder:** IT/vận hành, bảo mật. **Concern:** triển khai, kết nối, bảo vệ và phục hồi. **Purpose:** thiết kế target.

| ArchiMate element | Phần tử | Quan hệ/ý nghĩa |
|---|---|---|
| Node | Cloud VM / Container Host | `Composition` các runtime node logic nếu cần |
| Device | Hạ tầng compute do cloud cung cấp | Node được triển khai trên device; có thể ẩn ở logical view |
| System Software | Linux; Reverse Proxy; Python Runtime; PostgreSQL DBMS; Scheduler/Worker | `Assignment` technology function/service |
| Artifact | Application package; DB schema; statement file; backup; log | Package `Realization` Application Component/Data Object |
| Communication Network | Internet/VPC | Liên kết node và external nodes |
| Technology Service | TLS ingress; relational storage; scheduled execution; backup/restore; logging/monitoring | `Serving` Application Component |
| External Node | Carrier API; PSP API | Kết nối HTTPS qua adapters |

Deployment target là một modular monolith sau reverse proxy, PostgreSQL và worker dùng chung codebase. Prototype có thể dùng SQLite và mock Carrier/PSP, nhưng đây là simplification của prototype, không phải target production.

Security mapping: RBAC cho backoffice; TLS; secret từ environment/secret store; allow-list/signature/token cho callback; rate limit; log masking; DB backup và restore test. Thiết kế lưu inbox/outbox trong DB nên không cần message broker riêng ở quy mô giả định.

## 6. Viewpoint E — Implementation & Migration

**Stakeholder:** sponsor, project manager, architect. **Concern:** thứ tự đầu tư và dependency. **Purpose:** quyết định roadmap.

| Plateau | Work Package | Deliverable | Gap đóng |
|---|---|---|---|
| Baseline | — | Excel/Zalo/manual reconciliation | — |
| Transition 1 | WP0 Foundation | Platform, RBAC, audit, CI/test | Security/governance |
| Transition 1 | WP1 Order & Inventory | OMS, reservation, stock ledger | Order/inventory |
| Transition 1 | WP2 Payment & Shipping | QR/COD, adapters, webhook/outbox | Integration/payment |
| Transition 2 | WP3 Reconciliation | COD/QR matching và case | Financial control |
| Transition 2 | WP4 Reverse Logistics | RTO, RMA, QC, refund/exchange | Return/failure |
| Target | WP5 Hardening & Reporting | Dashboard, monitoring, backup, performance/security | Quality |
| Target | WP6 Pilot & Cutover | Pilot data, training, acceptance | Adoption |

Work Package `Realization` Deliverable; Deliverable `Realization` Plateau; Gap `Association` Work Package; Triggering thể hiện dependency WP0 → WP1 → WP2 → WP3/WP4 → WP5 → WP6.

## 7. Cross-layer trace mẫu

| Requirement | Business Process | Application Service/Component | Technology Service | Work Package |
|---|---|---|---|---|
| FR-02 | P2 | Inventory Service / Inventory | Relational storage | WP1 |
| FR-03 | P3 | Payment Service / Payment + PSP Adapter | TLS ingress, scheduled worker | WP2 |
| FR-07 | P4/P5 | Shipping + Return Service | Logging, outbox worker | WP4 |
| FR-10 | P6 | Reconciliation Service | File storage, relational storage | WP3 |
| NFR-02 | P3/P4 | Inbox/Outbox functions | Unique constraint, transaction | WP0/WP2 |
| NFR-05 | Tất cả | Backoffice + adapters | TLS, RBAC, rate limit, secret store | WP0/WP5 |

