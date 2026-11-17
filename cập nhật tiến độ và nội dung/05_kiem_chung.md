# Kiểm chứng kiến trúc

## Cách đọc tài liệu kiểm chứng

Thiết kế kiến trúc không chỉ cần “trông hợp lý” mà phải chỉ ra cách chứng minh. Tài liệu này có bốn phần:

1. **Risk register — danh sách rủi ro:** điều gì có thể sai, mức nguy hiểm và cách giảm rủi ro.
2. **Quality scenario — tình huống kiểm tra chất lượng:** đặt hệ thống vào một tình huống cụ thể và đo phản ứng.
3. **Test case — trường hợp kiểm thử:** dữ liệu ban đầu, hành động và kết quả mong đợi.
4. **Traceability — truy vết:** nối một yêu cầu đến mô hình, quyết định và bài kiểm thử để tránh viết yêu cầu nhưng không triển khai hoặc không kiểm tra.

Ví dụ: yêu cầu “không ghi tiền hai lần” được nối đến thiết kế Inbox, ADR-03 và bài kiểm thử gửi cùng webhook 10 lần.

## 1. Risk register

Thang điểm Probability (P) và Impact (I): 1–5; Score = P×I. Residual là điểm kỳ vọng sau kiểm soát.

- `P` là khả năng xảy ra: 1 là rất hiếm, 5 là rất thường xuyên.
- `I` là mức ảnh hưởng: 1 là nhỏ, 5 là rất nghiêm trọng.
- `Score` càng cao thì càng cần ưu tiên xử lý.
- `Prevent` là ngăn ngừa; `Detect` là phát hiện; `Recover` là khôi phục.
- `Residual` là điểm rủi ro còn lại sau khi đã áp dụng biện pháp.

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
Residual risk R-04/R-06 cần sponsor chấp nhận ở prototype vì không tích hợp carrier/PSP/bank thật.

## 2. Quality attribute scenarios

Mỗi dòng mô tả: ai/cái gì tạo ra tác động → hệ thống đang ở điều kiện nào → hệ thống phải phản ứng thế nào → đo bằng con số gì. `p95 < 2 giây` nghĩa là ít nhất 95 trong 100 lần gọi API phải trả lời dưới 2 giây, không phải mọi lần đều dưới 2 giây.

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

`Given–When–Then` có thể đọc là **Cho trước–Khi–Thì**. Ví dụ: cho trước kho còn 5 sản phẩm; khi 20 người cùng đặt mỗi người 1 sản phẩm; thì chỉ 5 người thành công và số tồn không âm.

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

Mỗi hàng bắt đầu từ một yêu cầu. Các cột sau trả lời yêu cầu đó phục vụ mục tiêu nào, nằm ở quy trình/phần mềm nào, chịu quyết định kiến trúc nào và được chứng minh bởi bài kiểm thử nào. Một yêu cầu không có bài kiểm thử là yêu cầu chưa có bằng chứng hoàn thành.

| Requirement | Goal | ArchiMate Business/Application | BPMN/API | ADR | Test |
|---|---|---|---|---|---|
| FR-01 | G-01,G-05 | P1 / Order Management | BPMN-01; Orders API | ADR-01 | TC-01 |
| FR-02 | G-04 | P2 / Inventory Service | BPMN-01; Reservations API | ADR-02 | TC-03, TC-10 |
| FR-03 | G-01 | P1/P3 / Order+Payment | BPMN-01; checkout API | ADR-01 | TC-01 |
| FR-04 | G-01,G-06 | P2/P4 / Shipping+Carrier Adapter | BPMN-01; Shipments API | ADR-03 | TC-04 |
| FR-05 | G-03,G-05 | P4 / Carrier Adapter | BPMN-01/02; Carrier Webhook | ADR-03 | TC-04, TC-09 |
| FR-06 | G-03 | P4/P5 / Shipping+Return | BPMN-02 | ADR-03 | TC-06, TC-09 |
| FR-07 | G-03,G-04 | P5 / Return+Inventory | BPMN-02; Returns/QC API | ADR-02 | TC-06 |
| FR-08 | G-02 | P6 / Reconciliation | BPMN-03; Statements API | ADR-04 | TC-05 |
| FR-09 | G-02,G-05 | P6 / Case Management | BPMN-03; Cases API | ADR-04 | TC-05 |
| FR-10 | G-05 | P1–P6 / audit+ledger | Tất cả API/event | ADR-02,03,04 | TC-02, TC-06, TC-09 |
| FR-11 | G-02,G-03 | P6 / Reporting | Dashboard API | ADR-04 | report fixture |
| FR-12 | G-05 | Business roles / Backoffice | Auth & admin API | ADR-01,03 | TC-07 |
| REQ-COD-01 | G-03 | P4/P5 / Shipping+Return | BPMN-02 | ADR-02,03 | TC-06, TC-09 |
| REQ-COD-02 | G-02 | P6 / Reconciliation | BPMN-03 | ADR-04 | TC-05 |
| REQ-COD-03 | G-04 | P5 / Return+Inventory | BPMN-02 | ADR-02 | TC-06 |
| EXT-01 | G-01,G-02 | P3 / Payment+PSP Adapter | BPMN-01; QR callback | ADR-03,04 | TC-01, TC-02, TC-10 |
| EXT-02 | G-03,G-04 | P5 / Return+Payment | BPMN-02; refund API | ADR-02,04 | TC-06 |
| EXT-03 | G-02 | P6 / Reconciliation | BPMN-03 | ADR-04 | settlement fixture |
| NFR-01 | G-01 | Technology/application view | Order query API | ADR-01 | QA-01 |
| NFR-02 | G-01 | Technology services | Health/backup | ADR-01 | TC-08 |
| NFR-03/04 | G-04,G-05 | Inbox/ledger/outbox | Webhooks, retry worker | ADR-02,03 | TC-02, TC-03, TC-04, TC-06 |
| NFR-05 | G-05 | TLS/RBAC/logging | Auth & webhook endpoints | ADR-03 | TC-07 |
| NFR-06/08 | G-02,G-04,G-05 | Ledger/audit | Adjustment/reconciliation | ADR-02,04 | TC-05, TC-06, TC-08 |
| NFR-07 | G-01 | Application ownership | Module contracts | ADR-01 | dependency test |

## 5. Exit criteria

`Exit criteria` là điều kiện để nhóm được phép kết luận phần thiết kế/prototype đã hoàn thành. Nếu bài kiểm thử quan trọng chưa đạt hoặc số tiền/tồn kho chưa giải thích được, nhóm không nên đánh dấu hoàn thành.

- Tất cả test critical TC-01…TC-07 pass; TC-08 có biên bản restore hoặc được ghi rõ là residual risk.
- Không có FR/NFR không ánh xạ đến ít nhất một model element và proof.
- State names trong tài liệu, API, UI và database giống nhau.
- Mọi mismatch tài chính/tồn kho đều thành case hoặc ledger entry; không “sửa tay” không audit.

