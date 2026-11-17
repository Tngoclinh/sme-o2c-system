# Kiểm chứng kiến trúc

## 1. Risk register

Thang điểm Probability (P) và Impact (I): 1–5; Score = P×I. Residual là điểm kỳ vọng sau kiểm soát.

| ID | Rủi ro / trigger | P | I | Score | Prevent/Detect/Recover | Owner | Residual |
|---|---|---:|---:|---:|---|---|---:|
| R-01 | Hai đơn giữ cùng tồn cuối | 4 | 5 | 20 | Atomic reservation, unique key, concurrency test; release timeout | Inventory | 6 |
| R-02 | Webhook payment/shipment lặp | 5 | 5 | 25 | Inbox unique key, idempotent handler, audit; replay an toàn | Integration | 5 |
| R-03 | Webhook giả mạo/sửa payload | 3 | 5 | 15 | TLS, signature/token, timestamp/replay window, rate limit, secret rotation | Security/IT | 6 |
| R-04 | Callback mất hoặc sai thứ tự | 4 | 4 | 16 | Outbox/inbox, state transition guard, polling reconciliation, manual queue | Integration | 8 |
| R-05 | Hàng RTO/return nhập kho hai lần hoặc chưa QC đã bán | 4 | 5 | 20 | Scan tracking/RMA unique, QC state, StockEntry append-only, quarantine | Warehouse | 6 |
| R-06 | COD/QR settlement thiếu, trùng hoặc sai phí | 4 | 5 | 20 | 3-way matching, batch hash, case + aging, approval adjustment | Accountant | 8 |
| R-07 | Lộ PII/API quản trị vượt quyền | 3 | 5 | 15 | RBAC, BOLA/BFLA tests, mask log, least data, audit access | IT | 6 |
| R-08 | DB/VM lỗi làm mất dữ liệu | 2 | 5 | 10 | Backup hằng ngày, restore drill, health check, transaction log, RPO/RTO | IT | 6 |
| R-09 | Modular monolith bị phụ thuộc chéo | 3 | 3 | 9 | Module API, ownership table, dependency test/code review | Architect | 4 |
| R-10 | Chính sách retry/return bị hard-code | 3 | 3 | 9 | Config có version/effective date, audit thay đổi, test boundary | Product owner | 4 |

Residual risk R-04/R-06 cần sponsor chấp nhận ở prototype vì không tích hợp carrier/PSP/bank thật.

## 2. Quality attribute scenarios

| ID | Source/Stimulus | Environment | Response | Measure | Proof |
|---|---|---|---|---|---|
| QA-01 | 50 users tra cứu order | Normal load, 10k orders | API trả đúng quyền | p95 <2s, errors <1% | k6/JMeter report |
| QA-02 | PSP gửi cùng callback 10 lần | Normal operation | Một payment entry, 10 inbox receipts hoặc 1 receipt + duplicate count | Effective entries = 1 | TC-02 |
| QA-03 | 20 requests reserve SKU còn 5 | Concurrent | 5 thành công, 15 out-of-stock | available ≥0, no duplicate reservation | TC-03 |
| QA-04 | Carrier API lỗi 5xx 3 lần | Partner outage | Outbox retry, không mất request; sau đó success | 1 shipment external, retry count=3 | TC-04 |
| QA-05 | Statement thiếu một COD payment | Reconciliation run | Mở discrepancy case | Case có owner, amount, source refs | TC-05 |
| QA-06 | Warehouse scan cùng RTO hai lần | Return receiving | Lần hai trả duplicate/no-op | 1 RECEIVE/QC entry | TC-06 |
| QA-07 | CSKH gọi endpoint adjustment | Authenticated but wrong role | Deny và audit | HTTP 403, no ledger change | TC-07 |
| QA-08 | Restore backup gần nhất | Recovery drill | Ứng dụng đọc được order/ledger | RPO ≤24h, RTO mục tiêu ≤4h | TC-08 |

## 3. Test cases

| TC | Given | When | Then |
|---|---|---|---|
| TC-01 Happy QR | SKU available=10 | Tạo order 2 SKU, trả QR, callback valid, ship | Reservation commit; Payment PAID; Shipment HANDED_OVER; IDs truy vết cùng order |
| TC-02 Duplicate payment | Payment PENDING | Gửi cùng external_event_id 10 lần | 01 PAID entry; các lần sau 200/no-op; audit duplicate |
| TC-03 Oversell | available=5 | 20 request song song mỗi request quantity=1 | Đúng 5 success; 15 conflict; balance invariant đúng |
| TC-04 Outbox recovery | Carrier mock fail 3 lần | Worker retry | Lần 4 tạo đúng 01 shipment; không duplicate external order |
| TC-05 COD discrepancy | Expected 500k, statement 480k, bank 480k | Run reconciliation | Case MISSING_20K/WRONG_FEE; batch PARTIAL; không tự điều chỉnh ledger |
| TC-06 RTO duplicate | Shipment RETURNED | Scan cùng tracking hai lần | Một RETURN_TO_QC; sau QC pass một RESTOCK |
| TC-07 Authorization | User role CS | POST adjustment | 403; security audit có user/action |
| TC-08 Backup restore | Có backup demo | Restore vào DB sạch | Counts/checksum Order, StockEntry, PaymentEntry khớp |
| TC-09 Out-of-order shipment | Shipment IN_TRANSIT | DELIVERED đến trước PICKED_UP rồi event cũ đến | Giữ DELIVERED; event cũ được lưu nhưng không rollback state |
| TC-10 QR timeout race | Timer expire và callback gần đồng thời | Hai handler chạy | Chỉ một kết quả hợp lệ theo DB lock; nếu paid thắng không release stock; nếu expired thắng callback vào case/refund policy |

## 4. Traceability matrix

| Requirement | Goal | ArchiMate Business/Application | BPMN/API | ADR | Test |
|---|---|---|---|---|---|
| FR-01 | G-01 | P1 / Order Management | BPMN-01; Orders API | ADR-01 | TC-01 |
| FR-02 | G-03 | P2 / Inventory Service | BPMN-01; Reservations API | ADR-02 | TC-03, TC-10 |
| FR-03 | G-01,G-02 | P3 / Payment + PSP Adapter | BPMN-01; Payment Intents/Webhook | ADR-03,04 | TC-01,02,10 |
| FR-04 | G-02 | P3 / Payment | BPMN-01; COD receivable | ADR-04 | TC-05 |
| FR-05 | G-01 | P2 / Shipping | BPMN-01; Shipments API | ADR-01,03 | TC-04 |
| FR-06 | G-05 | P4 / Carrier Adapter | BPMN-01/02; Carrier Webhook | ADR-03 | TC-04,09 |
| FR-07 | G-04 | P4/P5 / Shipping+Return | BPMN-02 | ADR-02,03 | TC-06,09 |
| FR-08 | G-04 | P5 / Return+Inventory | BPMN-02; Returns/QC API | ADR-02 | TC-06 |
| FR-09 | G-02,G-04 | P5 / Payment | BPMN-02; Refund API | ADR-03,04 | TC-01 extension |
| FR-10 | G-02 | P6 / Reconciliation | BPMN-03; Statements API | ADR-04 | TC-05 |
| FR-11 | G-02 | P6 / Reconciliation | BPMN-03 | ADR-04 | TC-01 + settlement fixture |
| FR-12 | G-02 | P6 / Case Management | BPMN-03; Cases API | ADR-04 | TC-05,07 |
| FR-13 | G-01…G-04 | P6 / Reporting | Dashboard API | ADR-04 | report fixture |
| NFR-01 | G-01 | Technology/application view | Order query API | ADR-01 | QA-01 |
| NFR-02 | G-03,G-05 | Inbox/ledger | Webhooks | ADR-02,03 | TC-02,03,06 |
| NFR-03/04 | G-05 | Technology services | Health/outbox | ADR-01,03 | TC-04,08 |
| NFR-05/09 | G-05 | TLS/RBAC/logging | Auth & webhook endpoints | ADR-03 | TC-07 |
| NFR-06/08 | G-02,G-03 | Ledger/audit | Adjustment/reconciliation | ADR-02,04 | TC-05,06,08 |
| NFR-07 | G-01 | Application ownership | Module contracts | ADR-01 | dependency test |

## 5. Exit criteria

- Tất cả test critical TC-01…TC-07 pass; TC-08 có biên bản restore hoặc được ghi rõ là residual risk.
- Không có FR/NFR không ánh xạ đến ít nhất một model element và proof.
- State names trong tài liệu, API, UI và database giống nhau.
- Mọi mismatch tài chính/tồn kho đều thành case hoặc ledger entry; không “sửa tay” không audit.

