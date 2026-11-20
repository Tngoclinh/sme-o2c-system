# ArchiMate 3.2 — mô hình chuẩn hóa

## Cách hiểu ArchiMate mà không cần biết ký pháp trước

ArchiMate là ngôn ngữ dùng để vẽ **bức tranh tổng thể**, không phải để mô tả từng bước chi tiết. Hãy hình dung mô hình có ba tầng:

1. **Tầng nghiệp vụ:** ai làm việc gì, ví dụ nhân viên kho đóng gói hàng.
2. **Tầng ứng dụng:** phần mềm nào hỗ trợ công việc đó, ví dụ phân hệ Kho cung cấp chức năng giữ hàng.
3. **Tầng công nghệ:** phần mềm chạy trên hạ tầng nào, ví dụ ứng dụng chạy trên máy chủ và PostgreSQL.

Theo đề bài, tài liệu trình bày lần lượt **Motivation → Business → Application → Technology → Đối tượng dữ liệu và liên kết quan trọng → Các bước chuyển đổi**. BPMN mô tả từng bước của quy trình. Phần Strategy và bảng truy vết mẫu nằm ở cuối để tham khảo thêm.

### Quy ước đọc mô hình

“Phần tử” là một hộp trên sơ đồ; “quan hệ” là đường nối giữa các hộp. Không nên nối các hộp chỉ vì chúng “có liên quan”, mà phải chọn đúng ý nghĩa của đường nối.

ArchiMate được dùng để tạo cái nhìn tổng quan và liên kết các lớp; BPMN được dùng cho chi tiết luồng. Mỗi view phải ghi rõ stakeholder, concern và purpose. Tên phần tử là danh từ với active structure/object/service và động từ với process/function. Không dùng `Flow` thay cho mọi quan hệ.

Các quan hệ sử dụng:

- `Assignment` — **giao thực hiện:** ai hoặc thành phần nào thực hiện một công việc. Ví dụ nhân viên kho thực hiện đóng gói.
- `Realization` — **hiện thực hóa:** cách làm cụ thể tạo ra một dịch vụ/kết quả bên ngoài. Ví dụ quy trình đối soát hiện thực dịch vụ đối soát.
- `Serving` — **phục vụ:** một dịch vụ cung cấp khả năng cho bên khác. Ví dụ dịch vụ Kho phục vụ quy trình xử lý đơn.
- `Access` — **truy cập dữ liệu:** một công việc đọc hoặc ghi đối tượng dữ liệu nào.
- `Triggering` — **kích hoạt/trước sau:** việc A xảy ra làm việc B bắt đầu.
- `Flow` — **luồng truyền:** dữ liệu, tiền hoặc hàng đi từ đâu đến đâu; phải ghi rõ thứ được truyền.
- `Influence` — **tác động:** một động lực hoặc nguyên tắc ảnh hưởng đến mục tiêu/yêu cầu.

## 1. Motivation — Động lực và mục tiêu

Góc nhìn này trả lời “tại sao phải làm hệ thống”. Ví dụ, việc dữ liệu bị phân tán là đánh giá hiện trạng; nó thúc đẩy mục tiêu kiểm soát tiền và tồn kho; mục tiêu sau đó được chuyển thành các yêu cầu cụ thể.

**Stakeholder:** chủ shop, kế toán, kho. **Concern:** tại sao thay đổi và thành công là gì. **Purpose:** quyết định/phê duyệt.

| Loại | Phần tử |
|---|---|
| Stakeholder | Chủ doanh nghiệp; Khách hàng; Nhân viên bán hàng/CSKH; Nhân viên kho; Nhân viên kế toán; Đơn vị vận chuyển; Ngân hàng/Đơn vị cung cấp thanh toán QR; Bộ phận IT/vận hành hệ thống |
| Driver | Tăng đơn online; giao thất bại/RTO; khó đối soát COD/QR; lệch tồn; kỳ vọng đổi/trả minh bạch |
| Assessment | Dữ liệu phân tán; thao tác lặp; không có correlation ID; trạng thái trộn; thiếu audit |
| Goal | G-01…G-06 trong TOGAF |
| Outcome | O-01 Đơn xuyên suốt; O-02 tiền COD giải thích được; O-03 hàng hoàn có kiểm soát; O-04 tồn chính xác; O-05 thay đổi truy vết được; O-06 tích hợp dễ mở rộng |
| Principle | AP-01…AP-05 |
| Requirement | FR-01…FR-12; NFR-01…NFR-08; REQ-COD-01…03; EXT-01…03 |
| Constraint | C-01 01 website; C-02 01 kho trung tâm; C-03 01 ĐVVC; C-04 100–300 đơn/ngày; C-05 nguồn lực SME; C-06 đối tác ngoài được mock trong prototype |
| Meaning | “Đã giao” không đồng nghĩa “đã nhận tiền”; “hàng đã về” không đồng nghĩa “hàng có thể bán”; “phí khách trả trong đơn” không đồng nghĩa “hóa đơn phí ĐVVC của shop” |
| Value | Giảm nhập lại dữ liệu; giảm tiền COD treo; tránh bán hàng hoàn chưa QC; ngoại lệ có người chịu trách nhiệm |

Quan hệ cốt lõi: Stakeholder `Association` Driver; Driver/Assessment `Influence` Goal; Outcome `Realization` Goal; Principle/Constraint `Influence` Requirement; Requirement `Realization` Outcome. Meaning giải thích đối tượng và Value mô tả lợi ích. View chỉ hiển thị nhóm requirement liên quan để tránh quá tải, còn matrix giữ quan hệ đầy đủ.

Trong mọi view, `Ngân hàng/Đơn vị cung cấp thanh toán QR` là một External Actor/Node tổng quát, có thể là ngân hàng có API, cổng thanh toán, PSP hoặc mock. Thành phần này tạo/quản lý QR và thông báo kết quả; không phải ĐVVC và không được mô hình như một module nội bộ của shop.

## 2. Business — Nghiệp vụ và phối hợp quy trình

Góc nhìn này trả lời “bộ phận nào phối hợp với bộ phận nào”. `Actor` là người/tổ chức; `Role` là vai trò họ đảm nhiệm; `Process` là chuỗi công việc; `Service` là giá trị mà quy trình cung cấp cho bên khác.

**Stakeholder:** vận hành, kho, kế toán, CSKH. **Concern:** ai làm gì và trao đổi gì. **Purpose:** thiết kế/coherence.

### 2.1 Active structure

| Business Actor | Business Role được gán |
|---|---|
| Khách hàng | Người mua |
| SME | Bán hàng/CSKH, Warehouse, Accountant, Owner |
| Đơn vị vận chuyển | Carrier |
| Ngân hàng/Đơn vị cung cấp thanh toán QR | QR Payment Provider |

Business Interface gồm `Website đặt hàng`, `Backoffice vận hành`, `Điểm bàn giao/nhận hoàn` và `Kênh tích hợp ĐVVC/Đơn vị QR`. Contract gồm chính sách bán/đổi trả, biểu phí/thỏa thuận dịch vụ ĐVVC và quy tắc thanh toán. Representation gồm xác nhận đơn, nhãn vận chuyển, biên bản nhận hoàn, bảng kê COD, hóa đơn phí vận chuyển và bảng kê QR. Product cung cấp cho khách hàng là `Dịch vụ mua hàng trực tuyến và giao tận nơi`.

Business Flow tiền được tách rõ: với COD, khách trả cho shipper thu hộ, ĐVVC tổng hợp và chuyển tiền vào tài khoản ngân hàng của shop cuối tháng; `Carrier Invoice Payment` là dòng tiền shop trả ĐVVC theo hóa đơn tháng. ĐVVC phải chuyển đủ COD gross sau đối soát sơ bộ; CarrierInvoice không được net-off vào dòng COD. Với QR, Ngân hàng/Đơn vị QR thu grand total, giả định phí bằng 0 và ĐVVC không thu thêm tại cửa.

### 2.2 Behavior và service

| Business Process | Business Service được hiện thực | Role thực hiện | Business Object được access |
|---|---|---|---|
| P1 Capture & Confirm Order | Order Placement Service | Người mua, Bán hàng/CSKH | Order, Payment Instruction |
| P2 Reserve & Fulfill | Fulfillment Service | Warehouse | Order, Reservation, Stock Record |
| P3 Collect/Confirm Payment | Payment Service | Accountant + Đơn vị QR/ĐVVC | Payment, QR Reference, COD Receivable |
| P4 Deliver & Handle Failure | Delivery Tracking Service | Carrier + Bán hàng/CSKH | Shipment, Delivery Attempt |
| P5 Return/Exchange & QC | Return/Exchange Service | Bán hàng/CSKH + Warehouse | RMA, Returned Item, QC Result |
| P6 Reconcile & Close | Reconciliation Service | Accountant | COD Statement, QR Statement, COD Remittance, Carrier Invoice, Discrepancy Case |

Business Event `Order submitted` triggers P1; `Payment confirmed/COD accepted` triggers P2; `Parcel handed over` triggers P4; `Delivery failed/Return requested` triggers P5 theo biến thể; `Statement received` triggers P6. Flow ghi nhãn `order`, `parcel`, `payment`, `statement`, không dùng flow không nhãn.

## 3. Application — Ứng dụng hỗ trợ nghiệp vụ

Góc nhìn này trả lời “phần mềm nào hỗ trợ quy trình nào”. `Component` có thể hiểu là phân hệ phần mềm; `Function` là logic bên trong; `Application Service` là chức năng mà phân hệ cung cấp cho phần khác sử dụng.

**Stakeholder:** product owner, architect, developer. **Concern:** component nào hỗ trợ process nào. **Purpose:** thiết kế target.

### 3.1 Component, function và service

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
| QR Payment Adapter | QR Provider Translation | QR Payment Integration Service | P3, P5, P6 |

Quan hệ: Component `Assignment` Function; Function `Realization` Application Service; Application Service `Serving` Business Process; Function `Access` Data Object. Giữa component chỉ dùng `Serving` khi cung cấp chức năng, `Flow` khi cần nhấn mạnh dữ liệu/sự kiện truyền.

### 3.2 Application interface, collaboration và event

| Application Interface | Bên cung cấp → bên dùng | Dữ liệu/sự kiện chính |
|---|---|---|
| Orders/Operations API | Order/Inventory/Shipping → Storefront/Backoffice | order, reservation, shipment, return |
| Carrier API Adapter | Carrier Adapter ↔ ĐVVC | create shipment, status webhook, COD statement |
| QR Payment API Adapter | QR Payment Adapter ↔ Ngân hàng/Đơn vị QR | QR intent, payment/refund callback, statement |
| Statement/Invoice Import | Reconciliation ← Kế toán/đối tác | COD/QR statement, remittance reference và carrier invoice |
| Internal Module Contract | Component sở hữu → component cần dùng | lệnh đồng bộ trong transaction; domain event qua outbox |

Application Collaboration `Order Fulfillment` gồm Order + Inventory + Shipping; `Financial Closing` gồm Payment + Reconciliation. Application Event như `OrderConfirmed`, `StockReserved`, `ShipmentDelivered/Failed/Returned`, `PaymentConfirmed`, `MonthlyCODStatementImported`, `CODRemittanceReceived` và `CarrierInvoiceImported` kích hoạt function kế tiếp. Inbox/outbox bảo đảm sự kiện gửi lặp không tạo tác dụng kép.

## 4. Technology — Hạ tầng và vận hành

Góc nhìn này cho biết ứng dụng được triển khai ở đâu. Máy chủ là nơi chạy; PostgreSQL là phần mềm quản trị cơ sở dữ liệu; file cài đặt, file bảng kê và file sao lưu là các “hiện vật” cụ thể. Dịch vụ công nghệ là khả năng hạ tầng cung cấp, ví dụ lưu dữ liệu hoặc sao lưu–khôi phục.

**Stakeholder:** IT/vận hành, bảo mật. **Concern:** triển khai, kết nối, bảo vệ và phục hồi. **Purpose:** thiết kế target.

| ArchiMate element | Phần tử | Quan hệ/ý nghĩa |
|---|---|---|
| Node | Cloud VM / Container Host | `Composition` các runtime node logic nếu cần |
| Device | Hạ tầng compute do cloud cung cấp | Node được triển khai trên device; có thể ẩn ở logical view |
| System Software | Linux; Reverse Proxy; Python Runtime; PostgreSQL DBMS; Scheduler/Worker | `Assignment` technology function/service |
| Artifact | Application package; DB schema; statement file; backup; log | Package `Realization` Application Component/Data Object |
| Communication Network | Internet/VPC | Liên kết node và external nodes |
| Path | HTTPS path; DB connection path; backup path | Nối các node và ghi rõ kiểu truyền |
| Technology Interface | Public HTTPS endpoint; private DB endpoint; backup endpoint | Điểm truy cập technology service |
| Technology Service | TLS ingress; relational storage; scheduled execution; backup/restore; logging/monitoring | `Serving` Application Component |
| External Node | Carrier API; QR Payment Provider API | Kết nối HTTPS qua adapters |

Deployment target là một modular monolith sau reverse proxy, PostgreSQL và worker dùng chung codebase. Prototype có thể dùng SQLite, mock Carrier và mock Ngân hàng/Đơn vị cung cấp thanh toán QR, nhưng đây là simplification của prototype, không phải target production.

Technology Function gồm terminate TLS, execute application, persist transaction, schedule retry, collect log và backup/restore. Technology Process `Nightly Backup` tạo Artifact backup; Technology Event `Health Check Failed` kích hoạt cảnh báo/khởi động lại. Security mapping: RBAC cho backoffice; TLS; secret từ environment/secret store; allow-list/signature/token cho callback; rate limit; log masking; DB backup và restore test. Thiết kế lưu inbox/outbox trong DB nên không cần message broker riêng ở quy mô giả định.

## 5. Đối tượng dữ liệu và liên kết quan trọng

### 5.1 Data Object và ownership

Mỗi loại dữ liệu có đúng một phân hệ chịu trách nhiệm chính. Trạng thái Đơn hàng, Thanh toán, Vận chuyển và Đổi trả được tách riêng vì một đơn có thể đã giao thành công nhưng khoản tiền vẫn chưa được đối soát.

| Data Object | Owner | Trạng thái chính / quy tắc |
|---|---|---|
| Order | Order | Lưu item subtotal, customer shipping charge và grand total; DRAFT → PENDING_PAYMENT/CONFIRMED → FULFILLING → COMPLETED/CANCELLED; không chứa shipment state |
| Reservation | Inventory | ACTIVE → COMMITTED/RELEASED/EXPIRED |
| StockEntry | Inventory | Append-only: RESERVE, RELEASE, SHIP, RETURN_TO_QC, RESTOCK, QUARANTINE, ADJUST |
| Payment | Payment | PENDING → AUTHORIZED/PAID/FAILED/EXPIRED → PARTIALLY_REFUNDED/REFUNDED |
| PaymentEntry | Payment | Append-only expected/collected/paid/remitted/refund/adjustment; giả định không có QR fee và không ghi carrier invoice vào đây |
| Shipment | Fulfillment/Shipping | CREATED → HANDED_OVER → IN_TRANSIT → DELIVERED/FAILED → RETURNING/RETURNED |
| ShipmentEvent | Fulfillment/Shipping | external_event_id unique, raw status + canonical status |
| Return/RMA | Return | REQUESTED → APPROVED/REJECTED → IN_TRANSIT → RECEIVED → QC_PASSED/QC_FAILED → CLOSED |
| Statement/Remittance | Reconciliation | COD/QR statement và tiền chuyển về: IMPORTED → MATCHED/PARTIAL/DISCREPANT → CLOSED |
| CarrierInvoice | Reconciliation | Hóa đơn phí vận chuyển tháng: RECEIVED → VERIFIED/DISPUTED → APPROVED → PAID; tách khỏi COD remittance |
| ReconciliationCase | Reconciliation | OPEN → INVESTIGATING → RESOLVED/WRITTEN_OFF |
| OutboxEvent/InboxEvent | Module phát/nhận | PENDING → SENT/PROCESSED/FAILED; idempotency key unique |

Business Object được Data Object tương ứng `Realization`; file CSV/PDF gốc được mô hình là Artifact hiện thực Data Object Statement.

### 5.2 Kiến trúc dữ liệu theo ba mức của bài giảng

| Mức | Mục đích | Nội dung trong bài |
|---|---|---|
| Khái niệm (conceptual) | Cho nghiệp vụ thấy khái niệm chính | Customer đặt Order; Order có OrderLine và CustomerShippingCharge; Order có Payment và Shipment; Shipment có DeliveryAttempt; ĐVVC gửi CODStatement/CODRemittance và CarrierInvoice tách biệt; Payment/Shipment được đối soát trong ReconciliationCase |
| Logic (logical) | Chỉ ra thực thể, khóa và quan hệ không phụ thuộc DB | Các đối tượng trong catalog trên; `order_id` là mã xuyên suốt; `external_event_id` và `tracking_code/RMA` có ràng buộc duy nhất phù hợp |
| Vật lý (physical) | Chỉ ra cách lưu và bảo vệ | PostgreSQL schema theo module; transaction/unique constraint; ledger append-only; object storage cho chứng từ; index theo order/reference/time; backup và retention |

Vòng đời dữ liệu: tạo → sử dụng/chia sẻ qua API/event → đối soát → lưu giữ → ẩn/xóa theo chính sách. Owner nghiệp vụ phê duyệt định nghĩa và chất lượng; application owner chịu ghi đúng; IT chịu backup, quyền truy cập, mã hóa đường truyền và log. Business Object được `Realization` bởi Data Object; thuật ngữ nghiệp vụ nối tới trường dữ liệu, quy trình tới subject area và KPI tới measure đúng theo information value chain trong slide Data Architecture.

## 6. Các bước chuyển đổi (Implementation & Migration)

Góc nhìn này là bản đồ triển khai. `Work Package` là một gói việc có thể giao và nghiệm thu; `Plateau` là một mốc mà kiến trúc đã đạt trạng thái ổn định tạm thời.

**Stakeholder:** sponsor, project manager, architect. **Concern:** thứ tự đầu tư và dependency. **Purpose:** quyết định roadmap.

| Plateau | Work Package | Deliverable | Gap đóng |
|---|---|---|---|
| Baseline | — | Hiện trạng bốn miền tại [TOGAF, mục 5](01_togaf_chuan_hoa.md#5-hiện-trạng-kiến-trúc-đích-và-khoảng-thiếu-baseline-target-gap) | — |
| Giai đoạn 1 | WP-01 Chuẩn hóa dữ liệu và trạng thái | Từ điển dữ liệu, state model, RBAC, audit/correlation, nền tảng DB | GAP-D01, nền tảng GAP-D02 và GAP-T01 |
| Giai đoạn 1 | WP-02 Order + Inventory | OMS, reservation, stock ledger, chọn COD/QR | GAP-B01, GAP-B02, GAP-A01, phần QR tại checkout của GAP-A03 |
| Giai đoạn 2 | WP-03 Shipping + Returns | Adapter, webhook/outbox, failed delivery/RTO, nhận hoàn/QC/đổi trả | GAP-B03, GAP-A02 |
| Giai đoạn 3 | WP-04 COD Reconciliation | COD ledger, bảng kê/remittance tháng, three-way match, carrier invoice tách riêng, discrepancy case; mở rộng QR | GAP-B04, phần tài chính và đối soát của GAP-D02/GAP-A03 |
| Target | WP-05 Reporting & Operational Controls | Dashboard, cảnh báo, backup/restore, monitoring, kiểm thử và pilot | Phần báo cáo và vận hành của GAP-A03/GAP-T01 |

Implementation Event gồm `M1 chuẩn hóa được phê duyệt`, `M2 đơn–tồn chạy thử`, `M3 luồng giao/hoàn chạy E2E`, `M4 đối soát COD đạt kiểm thử` và `M5 nghiệm thu pilot`. Work Package `Realization` Deliverable; Deliverable `Realization` Plateau; Gap `Association` Work Package; Triggering thể hiện dependency WP-01 → WP-02 → WP-03 → WP-04 → WP-05.

## Phụ lục A — Strategy

Góc nhìn Strategy trong bài giảng nối mục tiêu kinh doanh với năng lực cần có trước khi đi xuống quy trình và phần mềm. `Resource` là nguồn lực; `Capability` là khả năng tổ chức làm tốt một việc; `Value Stream` là chuỗi bước tạo giá trị; `Course of Action` là hướng hành động được chọn.

**Stakeholder:** chủ shop, quản lý vận hành, kiến trúc sư. **Concern:** phải xây năng lực nào và ưu tiên ra sao. **Purpose:** lập kế hoạch năng lực.

| Loại | Phần tử |
|---|---|
| Resource | Nhân viên bán hàng/CSKH; nhân viên kho; kế toán; dữ liệu đơn–tồn–giao–tiền; hợp đồng ĐVVC/Đơn vị QR; nền tảng ứng dụng |
| Capability | C-01 Điều phối đơn; C-02 Kiểm soát tồn; C-03 Quản lý giao và ngoại lệ; C-04 Nhận/QC hàng hoàn; C-05 Đối soát COD; C-06 Truy vết và báo cáo |
| Value Stream | VS1 Tiếp nhận đơn → VS2 Xác nhận tiền/giữ hàng → VS3 Xuất và giao → VS4 Xử lý thất bại/hoàn → VS5 Đối soát và đóng đơn |
| Course of Action | COA-01 Chuẩn hóa dữ liệu/trạng thái; COA-02 Xây O2C tích hợp nhưng gọn; COA-03 Tích hợp phục hồi/chống trùng; COA-04 Đối soát bằng ledger/case |

Course of Action `Realization` Capability; Resource được `Assignment` cho Capability; Capability `Serving` Value Stream; Value Stream `Realization` Value. C-05 hiện thực G-02, C-04/C-02 hiện thực G-03/G-04, C-06 hiện thực G-05 và cách dùng adapter hỗ trợ G-06.

## Phụ lục B — Truy vết giữa các lớp

| Requirement | Business Process | Application Service/Component | Technology Service | Work Package |
|---|---|---|---|---|
| FR-02 | P2 | Inventory Service / Inventory | Relational storage, transaction | WP-02 |
| FR-04/05 | P2/P4 | Shipping Service / Carrier Adapter | TLS ingress, scheduled worker | WP-03 |
| FR-07, REQ-COD-03 | P5 | Return + Inventory Service | Unique constraint, relational storage | WP-03 |
| FR-08/09, REQ-COD-02 | P6 | Reconciliation Service | File/object + relational storage | WP-04 |
| NFR-03/04 | P3/P4/P5 | Inbox/Outbox functions | Unique constraint, transaction, scheduler | WP-01/WP-03 |
| NFR-05 | Tất cả | Backoffice + adapters | TLS, RBAC, rate limit, secret store | WP-01/WP-05 |

