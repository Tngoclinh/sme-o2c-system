# TOGAF — kiến trúc Order-to-Cash cho SME thương mại điện tử

## 1. Request for Architecture Work

| Thuộc tính | Nội dung |
|---|---|
| Sponsor | Chủ doanh nghiệp SME |
| Vấn đề | Dữ liệu đơn–tồn–giao–tiền phân tán; giao thất bại/hoàn đáng kể; đối soát COD thủ công; QR chưa gắn chắc với đơn; đổi/trả làm lệch tồn và tiền |
| Mục tiêu | Thiết kế kiến trúc đích và lộ trình cho Order-to-Cash xuyên suốt, có kiểm soát ngoại lệ và truy vết tài chính |
| Phạm vi tổ chức | Bán hàng/CSKH, kho, kế toán, IT; khách hàng, ĐVVC và PSP/ngân hàng là bên ngoài |
| Phạm vi hệ thống | Website + OMS, Inventory, Payment, Shipping, Return, Reconciliation, Reporting |
| Ràng buộc | 01 website, 01 kho, 01 ĐVVC và 01 PSP giả lập; 200–500 đơn/ngày; ngân sách và nhân lực SME |
| Deliverable | TOGAF, 05 ArchiMate viewpoint, 03 BPMN, 04 ADR, risk/traceability, prototype và báo cáo |
| Giả định | 70% COD và 15–20% giao thất bại/hoàn chỉ là giả định để stress-test thiết kế; không phải số liệu ngành |

## 2. Architecture Vision

Xây dựng một nền tảng Order-to-Cash tích hợp, trong đó mỗi đơn hàng có thể được truy vết từ lúc tạo đơn, giữ chỗ tồn kho, thanh toán COD/QR, giao nhận, đổi/trả đến khi tiền và tồn kho được đối soát. Kiến trúc ưu tiên đơn giản, khả năng kiểm toán và xử lý lặp an toàn, phù hợp quy mô SME.

### 2.1 Phạm vi

Trong phạm vi: đặt hàng, xác nhận QR/COD, reservation, pick-pack-handover, shipment tracking, retry/RTO, đổi/trả, QC, refund, COD/QR reconciliation, dispute và báo cáo.

Ngoài phạm vi: procurement, multi-warehouse, marketplace, dynamic pricing, general ledger, route optimization, production-grade HA và tích hợp pháp lý hóa đơn điện tử.

### 2.2 Stakeholder và concern

| Stakeholder | Concern | View/đầu ra trả lời |
|---|---|---|
| Chủ doanh nghiệp | Chi phí, tiền về, tỷ lệ thất bại/hoàn | Vision, KPI, roadmap, dashboard |
| Khách hàng | Đơn đúng, thanh toán an toàn, đổi/trả rõ ràng | BPMN-01/02, UI trạng thái |
| CSKH | Tra cứu và xử lý ngoại lệ | Business/Application view, API/UI |
| Kho | Reservation, xuất/nhập/QC không trùng | Inventory ledger, BPMN-01/02 |
| Kế toán | COD/QR, phí, refund, chênh lệch | BPMN-03, reconciliation view |
| IT/vận hành | Bảo mật, phục hồi, vận hành đơn giản | Technology view, ADR, risk |
| ĐVVC | Tạo vận đơn, trạng thái, COD, chuyển hoàn | Adapter contract, webhook |
| PSP/ngân hàng | QR reference, callback, settlement/refund | Payment Adapter, reconciliation |

### 2.3 Goal, outcome và KPI

| Goal | Outcome/KPI thiết kế |
|---|---|
| G-01 Tự động hóa O2C | ≥95% đơn hợp lệ đi qua không cần nhập lại dữ liệu trong prototype |
| G-02 Kiểm soát tiền COD/QR | 100% payment/settlement có order_id và external_ref; chênh lệch thành case |
| G-03 Tồn kho chính xác | Không oversell trong test đồng thời; mọi thay đổi có StockEntry |
| G-04 Kiểm soát giao thất bại và đổi/trả | 100% RTO/return có shipment/return record, QC và disposition |
| G-05 Truy vết và phục hồi | Callback lặp không tạo bút toán kép; sự kiện lỗi được retry hoặc xử lý thủ công |

## 3. Architecture Principles

| Principle | Hệ quả thiết kế |
|---|---|
| P-01 Single Source of Truth theo miền | Order, Inventory, Payment, Shipment, Return và Reconciliation có component sở hữu rõ ràng |
| P-02 Ledger cho kho và tiền | Không sửa lịch sử; ghi bút toán đảo/điều chỉnh có tham chiếu |
| P-03 Idempotent at-least-once integration | Callback có external_event_id; unique constraint; retry an toàn |
| P-04 API-first và anti-corruption layer | Mô hình đối tác không rò vào domain; contract mô tả bằng OpenAPI |
| P-05 Security and privacy by design | RBAC, tối thiểu dữ liệu, TLS, secret ngoài mã nguồn, audit log |
| P-06 SME simplicity | Modular monolith + PostgreSQL; chưa tách microservice/broker nếu chưa có bằng chứng tải |

## 4. Yêu cầu

### 4.1 Functional requirements

| ID | Yêu cầu | Acceptance tóm tắt |
|---|---|---|
| FR-01 | Tạo/xác nhận/hủy và tra cứu đơn | Order có dòng hàng, tổng tiền, địa chỉ và trạng thái hợp lệ |
| FR-02 | Giữ chỗ/giải phóng/cam kết tồn | Atomic reservation; không âm available-to-promise |
| FR-03 | QR theo từng đơn | Sinh payment intent + QR/reference; chỉ xác nhận sau callback/poll đã xác thực |
| FR-04 | COD | Gắn số tiền phải thu vào shipment/COD ledger |
| FR-05 | Fulfillment và bàn giao | Pick/pack/handover tạo shipment và tracking code |
| FR-06 | Nhận trạng thái ĐVVC | Map trạng thái qua adapter; sự kiện lặp không tạo side effect kép |
| FR-07 | Giao thất bại/RTO | Retry theo policy; hết lượt thì chuyển hoàn và theo dõi hàng về |
| FR-08 | Đổi/trả sau giao | RMA, lý do, loại đổi/trả, deadline, QC và disposition |
| FR-09 | Hoàn tiền QR | Refund có tham chiếu payment/return, trạng thái và approval |
| FR-10 | Đối soát COD | Expected COD ↔ statement ĐVVC ↔ bank settlement |
| FR-11 | Đối soát QR | Payment ledger ↔ PSP statement ↔ bank settlement/refund |
| FR-12 | Chênh lệch và dispute | Tạo case, owner, bằng chứng, resolution và audit trail |
| FR-13 | Báo cáo | Aging COD, settlement QR, failure/RTO/return, inventory quarantine |

### 4.2 Non-functional requirements

| ID | Thuộc tính | Stimulus–response–measure |
|---|---|---|
| NFR-01 | Performance efficiency | Với 50 virtual users và dữ liệu demo, p95 GET order <2s, error <1% |
| NFR-02 | Reliability | Khi webhook gửi lặp 10 lần, chỉ một ShipmentEvent/PaymentEntry có hiệu lực |
| NFR-03 | Availability | Mục tiêu production đề xuất 99,5%/tháng; prototype chứng minh health check và restart không mất dữ liệu |
| NFR-04 | Recoverability | Lỗi đối tác được retry exponential; quá ngưỡng vào danh sách xử lý; không mất request |
| NFR-05 | Security | RBAC theo vai trò; xác minh chữ ký/token callback; rate limit; bí mật trong environment |
| NFR-06 | Auditability | Mọi thay đổi tài chính/tồn có actor/source/time/correlation_id và ledger/audit entry |
| NFR-07 | Maintainability | Module không ghi trực tiếp bảng của module khác; dependency test kiểm tra ranh giới |
| NFR-08 | Financial integrity | Tổng settlement + fee + refund + open discrepancy giải thích được expected amount |
| NFR-09 | Privacy | Log che số điện thoại/địa chỉ; API chỉ trả trường theo quyền |

Các thuộc tính chất lượng tham chiếu ISO/IEC 25010:2023; giá trị ngưỡng là mục tiêu do nhóm chọn.

## 5. Baseline, Target và Gap

| Miền | Baseline | Target | Gap | Work package |
|---|---|---|---|---|
| Business | Excel/Zalo, xử lý ngoại lệ tùy người | Quy trình chuẩn order–pay–ship–return–reconcile | Thiếu ownership, SLA và state model | WP1, WP4 |
| Order | Đơn web xuất file | OMS là nguồn sự thật của Order | Thiếu lifecycle và correlation | WP1 |
| Inventory | Trừ lùi bảng tính | Reservation + append-only ledger + QC/quarantine | Dễ oversell, nhập hoàn trùng | WP1, WP4 |
| COD | Dò bảng kê cuối kỳ | COD ledger + 3-way reconciliation + aging | Không biết expected/settled/disputed | WP3 |
| QR | Chuyển khoản khó gắn đơn | Payment intent/reference/callback/refund/reconciliation | Thiếu adapter và settlement model | WP2, WP3 |
| Shipping | Theo dõi thủ công | API + signed/idempotent webhook + RTO | Thiếu mapping và retry | WP2, WP4 |
| Return/Exchange | Chat rời rạc | RMA + eligibility + QC + disposition + refund/exchange | Không truy vết reverse flow | WP4 |
| Data | Trạng thái trộn lẫn | State machine riêng và ID xuyên suốt | Không có canonical model | WP0, WP1 |
| Technology | File/máy cá nhân | Web app modular monolith, PostgreSQL, object storage, audit/monitoring | Thiếu bảo mật, backup, observability | WP0, WP5 |

## 6. Target Architecture tóm tắt

- Business: năm value stream step — Capture Order, Collect/Commit Payment, Fulfill & Deliver, Handle Return, Reconcile & Close.
- Data: Order, Reservation/StockEntry, Payment/PaymentEntry, Shipment/ShipmentEvent, Return/RMA, Statement/ReconciliationCase.
- Application: Web/Backoffice, Order, Inventory, Payment, Fulfillment/Shipping, Return, Reconciliation/Reporting và adapters.
- Technology: reverse proxy, application runtime, PostgreSQL, object/file storage, scheduler/outbox worker, logging/monitoring; đối tác ngoài qua HTTPS.

## 7. Roadmap

| Plateau | Work package | Khả năng đạt được | Phụ thuộc |
|---|---|---|---|
| Transition 1 | WP0 Foundation | Auth/RBAC, DB, audit, correlation, CI/test | Không |
| Transition 1 | WP1 Order & Inventory | Order + reservation + ledger + fulfillment cơ bản | WP0 |
| Transition 1 | WP2 Payment & Shipping Integration | QR/COD, adapters, webhook/outbox | WP1 |
| Transition 2 | WP3 Reconciliation | COD/QR statements, 3-way match, discrepancy | WP2 |
| Transition 2 | WP4 Exception & Reverse Logistics | failed delivery/RTO, RMA, QC, refund/exchange | WP2, WP3 |
| Target | WP5 Hardening & Reporting | dashboard, security, backup, monitoring, performance | WP3, WP4 |
| Target | WP6 Pilot & Cutover | data setup, training, parallel reconciliation, acceptance | WP5 |

## 8. Governance và acceptance

- Mọi thay đổi trạng thái phải tuân state machine và phát audit/event.
- Không merge API nếu thiếu authorization, idempotency rule và error contract tương ứng.
- Kế toán phê duyệt mapping statement; kho phê duyệt inventory disposition; chủ shop phê duyệt KPI và residual risk.
- Kiến trúc được chấp nhận khi 03 BPMN, 04 ADR, traceability matrix và 02 kịch bản prototype nhất quán với catalog này.

