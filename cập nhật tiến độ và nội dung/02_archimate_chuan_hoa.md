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

#### Giải thích các phần tử Motivation

- **Stakeholder (bên liên quan)** là cá nhân, nhóm hoặc tổ chức có mối quan tâm đến kiến trúc hoặc chịu ảnh hưởng từ thay đổi.
- **Driver (động lực)** là yếu tố bên trong hoặc bên ngoài thúc đẩy tổ chức đặt mục tiêu và thay đổi cách vận hành.
- **Assessment (đánh giá)** là nhận định rút ra khi phân tích hiện trạng dưới góc độ một động lực.
- **Goal (mục tiêu)** mô tả định hướng hoặc trạng thái tổ chức muốn đạt tới.
- **Outcome (kết quả)** mô tả kết quả cụ thể có thể quan sát để đánh giá mức độ đạt mục tiêu.
- **Principle (nguyên tắc)** là quy tắc chung định hướng các quyết định kiến trúc.
- **Requirement (yêu cầu)** mô tả chức năng hoặc đặc tính mà hệ thống cần đáp ứng.
- **Constraint (ràng buộc)** xác định giới hạn về phạm vi, nguồn lực hoặc điều kiện mà thiết kế phải tuân theo.
- **Meaning (ý nghĩa)** giải thích một phần tử có ý nghĩa gì trong ngữ cảnh đang xét.
- **Value (giá trị)** thể hiện lợi ích, tầm quan trọng hoặc mức hữu ích của một kết quả đối với bên liên quan.

#### Quan hệ chính cần thể hiện

1. **Stakeholder — `Association` — Driver.** Chỉ ra bên nào quan tâm đến hoặc chịu tác động từ một động lực thay đổi.
2. **Driver — `Influence` → Assessment.** Động lực định hướng vấn đề cần xem xét khi phân tích hiện trạng.
3. **Assessment — `Influence` → Goal.** Nhận định về hiện trạng ảnh hưởng đến việc xác định mục tiêu hoặc mức ưu tiên của mục tiêu.
4. **Principle — `Influence` → Requirement.** Nguyên tắc chung định hướng cách đặt ra các yêu cầu cụ thể.
5. **Constraint — `Influence` → Requirement.** Ràng buộc ảnh hưởng đến phạm vi hoặc điều kiện mà yêu cầu phải đáp ứng.
6. **Requirement — `Realization` → Outcome.** Việc đáp ứng một hoặc nhiều yêu cầu góp phần tạo ra kết quả cụ thể.
7. **Outcome — `Realization` → Goal.** Kết quả đạt được thể hiện một phần hoặc toàn bộ mục tiêu ở mức cụ thể hơn.

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

#### Giải thích vai trò của các bên

- **Khách hàng → Người mua:** Đặt đơn, chọn COD hoặc QR, theo dõi giao hàng và gửi yêu cầu đổi/trả khi cần.
- **SME → Các vai trò nội bộ:** Bán hàng/CSKH kiểm tra thông tin đơn, hỗ trợ tra cứu và phối hợp giao lại. Kho chuẩn bị và kiểm hàng. Kế toán đối soát và xử lý chênh lệch. Chủ shop phê duyệt chính sách và theo dõi kết quả.
- **ĐVVC → Vai trò vận chuyển:** Nhận kiện, cập nhật từng lần giao và nhận chuyển hoàn. Với đơn COD giao thành công, shipper thu hộ cho ĐVVC.
- **Đơn vị QR → Vai trò cung cấp thanh toán QR:** Tạo yêu cầu thanh toán theo đơn và gửi kết quả để shop xác nhận giao dịch.

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

#### Giải thích quy trình, dịch vụ và đối tượng nghiệp vụ

**Business Process** là chuỗi việc thực hiện. **Business Role** cho biết ai tham gia hoặc chịu trách nhiệm. **Business Service** là công việc được cung cấp để người khác sử dụng. **Business Object** là thông tin nghiệp vụ mà quy trình cần đọc hoặc cập nhật.

- **P1 — Tiếp nhận và xác nhận đơn.** Khách gửi đơn trên website. Bán hàng/CSKH kiểm tra thông tin khi cần. Dịch vụ đặt hàng tiếp nhận yêu cầu và cho khách biết kết quả xác nhận. `Order` ghi mặt hàng, địa chỉ và tổng tiền. `Payment Instruction` ghi cách thanh toán đã chọn.
- **P2 — Giữ và chuẩn bị hàng.** Kho dùng thông tin đơn để chuẩn bị đúng hàng, đóng gói và bàn giao kiện. `Reservation` là phần hàng đã dành cho đơn trước khi xuất. `Stock Record` cho biết số còn bán được và số đang giữ. Đơn QR chỉ tiếp tục sang khâu chuẩn bị giao sau khi shop xác nhận đã thanh toán.
- **P3 — Xử lý thanh toán.** Với QR, Đơn vị QR tạo yêu cầu và gửi kết quả theo `QR Reference`, tức mã dùng để ghép giao dịch với đơn. Với COD, `COD Receivable` ghi số cần thu khi giao. Shipper thu hộ khi giao thành công và kế toán theo dõi khoản đã thu.
- **P4 — Giao hàng và xử lý giao thất bại.** ĐVVC cập nhật kết quả từng lần giao. Bán hàng/CSKH tra cứu và phối hợp giao lại theo chính sách. `Shipment` là hồ sơ của kiện gửi đi. `Delivery Attempt` ghi ngày, kết quả và lý do của một lần đi giao.
- **P5 — Đổi/trả và kiểm hàng quay về.** Bán hàng/CSKH hỗ trợ khách tra cứu, còn kho thực nhận và kiểm chất lượng. `RMA` là hồ sơ đổi/trả. `Returned Item` ghi mặt hàng trả về. `QC Result` cho biết hàng đủ điều kiện bán lại hay cần cách ly.
- **P6 — Đối soát và chốt kỳ.** Kế toán đối chiếu số phải thu, bảng kê đã thu và tiền đã vào tài khoản shop. `COD Remittance` là chứng từ ĐVVC chuyển tiền về. `Discrepancy Case` ghi khoản lệch và quá trình xử lý. `Carrier Invoice` là hóa đơn phí vận chuyển được kiểm và thanh toán riêng.

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

#### Giải thích từng phân hệ

Có thể đọc dòng Inventory theo ba bước. `Inventory` là **phân hệ Kho**. `Reservation & Stock Ledger` là **việc giữ hàng và ghi biến động tồn** bên trong phân hệ. `Inventory Service` là **khả năng kiểm tra và giữ hàng** mà quy trình xử lý đơn sử dụng.

- **Storefront/Backoffice:** Khách thao tác trên website. Nhân viên thao tác trên màn hình quản trị để tra cứu và xử lý đơn.
- **Order và Inventory:** Order quản lý vòng đời đơn. Inventory giữ số lượng hàng cho đơn, giải phóng hàng khi hủy trước xuất và ghi các lần xuất, nhập lại.
- **Payment:** Gắn yêu cầu QR với đơn và lưu xác nhận tiền. Với COD, phân hệ ghi số dự kiến thu và cập nhật khi có thông tin khoản thu.
- **Fulfillment/Shipping và Return:** Shipping quản lý vận đơn và tình trạng giao. Return quản lý hồ sơ hàng quay về, kết quả kiểm hàng và hướng xử lý.
- **Reconciliation/Reporting:** Ghép bảng kê với đơn và tiền thực nhận, mở hồ sơ chênh lệch và báo cáo công nợ hoặc hàng hoàn.
- **Carrier Adapter và QR Payment Adapter:** Chuyển thông tin giữa định dạng của hệ thống shop và định dạng của từng đối tác.

Quan hệ: Component `Assignment` Function; Function `Realization` Application Service; Application Service `Serving` Business Process; Function `Access` Data Object. Giữa component chỉ dùng `Serving` khi cung cấp chức năng, `Flow` khi cần nhấn mạnh dữ liệu/sự kiện truyền.

### 3.2 Application interface, collaboration và event

| Application Interface | Bên cung cấp → bên dùng | Dữ liệu/sự kiện chính |
|---|---|---|
| Orders/Operations API | Order/Inventory/Shipping → Storefront/Backoffice | order, reservation, shipment, return |
| Carrier API Adapter | Carrier Adapter ↔ ĐVVC | create shipment, status webhook, COD statement |
| QR Payment API Adapter | QR Payment Adapter ↔ Ngân hàng/Đơn vị QR | QR intent, payment/refund callback, statement |
| Statement/Invoice Import | Reconciliation ← Kế toán/đối tác | COD/QR statement, remittance reference và carrier invoice |
| Internal Module Contract | Component sở hữu → component cần dùng | lệnh đồng bộ trong transaction; domain event qua outbox |

#### Giải thích điểm trao đổi thông tin

- **Orders/Operations API** cho màn hình đặt hàng hoặc quản trị gửi yêu cầu tạo đơn và tra cứu thông tin. API là điểm để phần mềm khác gọi một chức năng.
- **Giao diện ĐVVC và Đơn vị QR** nhận lệnh tạo vận đơn hoặc tạo yêu cầu QR. Đối tác gửi lại kết quả bằng thông báo tự động, chẳng hạn “đã giao” hoặc “đã thanh toán”.
- **Statement/Invoice Import** là nơi kế toán đưa bảng kê thu tiền, mã chuyển khoản và hóa đơn phí vào hệ thống để đối chiếu.
- **Internal Module Contract** quy định các phân hệ trao đổi gì với nhau. Ví dụ, Order yêu cầu Inventory giữ hàng và nhận kết quả giữ thành công hay hết tồn.

Application Collaboration `Order Fulfillment` gồm Order + Inventory + Shipping; `Financial Closing` gồm Payment + Reconciliation. Application Event như `OrderConfirmed`, `StockReserved`, `ShipmentDelivered/Failed/Returned`, `PaymentConfirmed`, `MonthlyCODStatementImported`, `CODRemittanceReceived` và `CarrierInvoiceImported` kích hoạt function kế tiếp. Inbox/outbox bảo đảm sự kiện gửi lặp không tạo tác dụng kép.

### 3.3 Data Object — Dữ liệu mà ứng dụng xử lý

Trong ArchiMate 3.2, `Data Object` là phần tử cấu trúc thụ động của lớp Application. Nó biểu diễn dữ liệu đã được tổ chức để phần mềm xử lý. Ví dụ, **Đơn hàng** là khái niệm nghiệp vụ (`Business Object`), còn **bản ghi đơn hàng** mà phân hệ Order đọc và cập nhật là `Data Object`. [ArchiMate 3.2 Reference Cards — Application Layer Elements](https://barbierdarnal.com/Enterprise_Architect/Clinique/ArchiMate_3.2_Specification_notation.pdf)

Khi vẽ, dùng quan hệ `Access` từ chức năng ứng dụng đến đối tượng dữ liệu và ghi rõ thao tác đọc hoặc ghi.

| Chức năng ứng dụng (Application Function) | Đối tượng dữ liệu (Data Object) | Ví dụ truy cập (Access) |
|---|---|---|
| Order Lifecycle | `Order` | Ghi đơn mới và cập nhật trạng thái đơn. |
| Reservation & Stock Ledger | `Reservation`, `StockEntry` | Đọc thông tin giữ chỗ và ghi biến động tồn khi giữ, giải phóng hoặc nhập lại hàng. |
| Shipment Lifecycle | `Shipment`, `ShipmentEvent` | Ghi sự kiện giao và cập nhật trạng thái vận đơn. |
| Matching, Case & Analytics | `Statement/Remittance`, `ReconciliationCase` | Đọc bảng kê và chứng từ tiền chuyển để đối soát. Ghi hồ sơ nếu có chênh lệch. |

Danh mục đầy đủ, phân hệ chịu trách nhiệm, trạng thái và liên kết dữ liệu nằm ở [mục 5](#5-đối-tượng-dữ-liệu-và-liên-kết-quan-trọng).

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

#### Giải thích hạ tầng qua một lần cập nhật vận đơn

ĐVVC gửi thông báo “đã giao” qua kết nối HTTPS đến điểm tiếp nhận của hệ thống. Phần mềm trung gian nhận kết nối rồi chuyển thông báo đến ứng dụng. Máy chủ chạy ứng dụng và PostgreSQL lưu kết quả xử lý. Nhật ký giúp IT tìm nguyên nhân nếu thông báo lỗi, còn bản sao lưu giúp khôi phục dữ liệu.

- **Node và Device:** Node là tài nguyên dùng để chạy hệ thống, ví dụ máy ảo của shop. Device là thiết bị vật lý cung cấp tài nguyên tính toán.
- **System Software và Artifact:** Linux, môi trường chạy Python và PostgreSQL cung cấp nền vận hành. Gói ứng dụng, tệp bảng kê, nhật ký và bản sao lưu là những hiện vật cụ thể.
- **Communication Network và Path:** Internet hoặc mạng riêng nối các bên. Path mô tả một đường trao đổi cụ thể, ví dụ đường từ máy chủ ứng dụng đến cơ sở dữ liệu.
- **Technology Interface và Technology Service:** Địa chỉ kết nối là điểm truy cập. Khả năng mà hạ tầng cung cấp qua điểm đó là dịch vụ, ví dụ nhận kết nối bảo mật hoặc lưu dữ liệu.

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

#### Giải thích các bản ghi trong thực tế

- **`Order` → `Reservation` → `StockEntry`:** Mã đơn giúp tìm lượng hàng đã giữ. Mỗi lần giữ, giải phóng, xuất hoặc nhập lại tạo một dòng biến động riêng để giải thích vì sao số tồn thay đổi.
- **`Payment` và `PaymentEntry`:** `Payment` mô tả tình trạng thanh toán của đơn. `PaymentEntry` lưu từng mốc tiền như dự kiến thu, đã thu hoặc đã chuyển. Kế toán xem lại các mốc này khi kiểm tra tiền COD.
- **`Shipment`, `ShipmentEvent` và `Return/RMA`:** Vận đơn nhận nhiều thông báo theo từng lần giao. Hồ sơ hàng quay về nối mã đơn, mã vận đơn và kết quả kiểm hàng để kho biết phải nhập lại hay cách ly.
- **`Statement/Remittance`, `CarrierInvoice` và `ReconciliationCase`:** Bảng kê và chứng từ chuyển tiền dùng để kiểm tra số shop thực nhận. Hóa đơn phí được đối chiếu riêng. Nếu phát hiện lệch, hồ sơ chênh lệch giữ số tiền, chứng từ và kết quả xử lý.
- **`OutboxEvent` và `InboxEvent`:** Hộp thư gửi lưu thông báo cần gửi hoặc gửi lại. Hộp thư nhận ghi thông báo đã nhận để nhận biết lần gửi lặp.

Business Object được Data Object tương ứng `Realization`; file CSV/PDF gốc được mô hình là Artifact hiện thực Data Object Statement.

### 5.2 Kiến trúc dữ liệu theo ba mức của bài giảng

| Mức | Mục đích | Nội dung trong bài |
|---|---|---|
| Khái niệm (conceptual) | Cho nghiệp vụ thấy khái niệm chính | Customer đặt Order; Order có OrderLine và CustomerShippingCharge; Order có Payment và Shipment; Shipment có DeliveryAttempt; ĐVVC gửi CODStatement/CODRemittance và CarrierInvoice tách biệt; Payment/Shipment được đối soát trong ReconciliationCase |
| Logic (logical) | Chỉ ra thực thể, khóa và quan hệ không phụ thuộc DB | Các đối tượng trong catalog trên; `order_id` là mã xuyên suốt; `external_event_id` và `tracking_code/RMA` có ràng buộc duy nhất phù hợp |
| Vật lý (physical) | Chỉ ra cách lưu và bảo vệ | PostgreSQL schema theo module; transaction/unique constraint; ledger append-only; object storage cho chứng từ; index theo order/reference/time; backup và retention |

#### Ví dụ cùng một thông tin ở ba mức

Với đơn COD, **mức khái niệm** xác định đơn và vận đơn có liên quan đến khoản thu hộ. **Mức logic** dùng mã đơn, mã vận đơn và mã chuyển khoản để ghép các bản ghi. **Mức vật lý** xác định bảng nào lưu các mã này và dùng quy tắc kiểm tra nào để một thông báo lặp chỉ được xử lý một lần.

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

#### Giải thích từng bước chuyển đổi

**Plateau** mô tả trạng thái hệ thống đạt được. **Work Package** là nhóm việc để đi đến trạng thái đó. **Deliverable** là sản phẩm bàn giao có thể kiểm tra. **Gap** cho biết phần còn thiếu được gói việc xử lý.

- **WP-01:** Thống nhất mã liên kết và tên trạng thái. Bàn giao bộ quy ước cùng nền lưu trữ, phân quyền và nhật ký.
- **WP-02:** Nối website với phân hệ đơn và kho. Sau bước này, đơn mới được đưa vào hệ thống, kho có thể giữ hoặc giải phóng hàng và shop có thể ghi nhận lựa chọn COD/QR.
- **WP-03:** Nối ĐVVC với hệ thống và chạy được luồng giao thất bại, giao lại, nhận hoàn và kiểm hàng. Kho chỉ nhập lại hàng đủ điều kiện.
- **WP-04:** Kế toán kiểm được bảng kê, đối chiếu COD/QR với ngân hàng, theo dõi chênh lệch và xử lý hóa đơn vận chuyển riêng.
- **WP-05:** Chủ shop xem được báo cáo. IT theo dõi lỗi, kiểm tra sao lưu và khôi phục. Nhóm chạy thử toàn bộ luồng để nghiệm thu.

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

#### Giải thích chiến lược trong dự án

- **Resource:** Nguồn lực shop có thể dùng, ví dụ nhân viên kho, dữ liệu tồn và thỏa thuận với ĐVVC.
- **Capability:** Việc shop cần làm tốt, ví dụ kiểm hàng hoàn và cập nhật đúng số có thể bán.
- **Value Stream:** Các chặng tạo giá trị từ lúc khách gửi đơn đến lúc shop giao hàng và xác nhận tiền.
- **Course of Action:** Hướng đã chọn để đạt năng lực đó, ví dụ chuẩn hóa mã đơn và mã vận đơn để ghép được bảng kê COD.

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

#### Cách đọc một dòng truy vết

Ví dụ FR-08/09 yêu cầu đối soát COD và phát hiện chênh lệch. Kế toán thực hiện tại P6, dùng dịch vụ đối soát để ghép bảng kê với chứng từ ngân hàng. Hạ tầng lưu dữ liệu và chứng từ để tra lại. WP-04 là gói việc bàn giao khả năng này.

## Phụ lục C — Ý nghĩa và lý do cần từng Data Object

Phụ lục giải thích theo thứ tự của [bảng ở mục 5.1](#51-data-object-và-ownership). Mỗi Data Object đại diện cho một nhóm thông tin mà ứng dụng xử lý. Một số đối tượng xuất hiện cùng dòng trong bảng vì phục vụ cùng một công việc. Phần dưới giải thích riêng nhiệm vụ của từng đối tượng trong những dòng đó.

### C.1 Order — Đơn hàng

`Order` ghi khách đặt gì, số lượng bao nhiêu, chọn cách thanh toán nào và tổng số tiền phải trả. Phân hệ Đơn hàng cần bản ghi này để xác nhận đơn và cung cấp cùng một bộ thông tin cho kho, vận chuyển và kế toán. Ví dụ, đơn có tiền hàng 280.000 đồng và phí giao thu khách 20.000 đồng sẽ ghi tổng cộng 300.000 đồng. Với COD, đây là số tiền được gửi cho ĐVVC để thu khi giao.

### C.2 Reservation — Bản ghi giữ chỗ hàng

`Reservation` ghi mặt hàng, số lượng đã dành cho một đơn và tình trạng giữ chỗ. Phân hệ Kho cần biết phần hàng nào đã được hứa cho khách để tránh phân bổ một món hàng cho hai đơn. Ví dụ, kho còn ba sản phẩm có thể bán và giữ một sản phẩm cho đơn A. Hai sản phẩm còn lại vẫn có thể bán. Nếu đơn A bị hủy trước khi xuất, kho giải phóng phần đã giữ.

### C.3 StockEntry — Dòng ghi biến động tồn

`StockEntry` ghi **một lần biến động tồn**, gồm mặt hàng, số lượng, lý do và tham chiếu liên quan. Sổ biến động giữ lại các dòng cũ để kho lần theo vì sao số tồn thay đổi. Ví dụ, khi kiện quay về, kho ghi nhận hàng vào khu chờ kiểm. Sau khi xác nhận hàng đạt, kho ghi thêm một dòng nhập lại vào lượng có thể bán. Hai dòng giúp tra được hàng đã về lúc nào và được bán lại từ lúc nào.

### C.4 Payment — Hồ sơ thanh toán

`Payment` cho biết đơn được thanh toán theo phương thức nào và việc thanh toán đang ở trạng thái gì. Phân hệ Thanh toán cần hồ sơ riêng vì tiến độ tiền có thể khác tiến độ giao. Ví dụ, một đơn QR có thể đã được xác nhận thanh toán trong khi kho vẫn đang đóng gói. Với COD, kiện có thể đã giao và ĐVVC đã thu hộ trong khi shop còn chờ tiền về.

### C.5 PaymentEntry — Dòng ghi một mốc tiền

`PaymentEntry` ghi **một mốc tài chính**, gồm loại mốc, số tiền, thời điểm và mã tham chiếu. Phân hệ Thanh toán lưu từng dòng để giải thích số tiền đang ở đâu và kiểm tra lại khi có lệch. Ví dụ, một đơn COD có thể có ba dòng riêng cho khoản dự kiến thu 300.000 đồng, khoản ĐVVC báo đã thu 300.000 đồng và khoản đã xác nhận chuyển về shop. Ba dòng biểu diễn các mốc của cùng một khoản tiền.

### C.6 Shipment — Vận đơn

`Shipment` ghi mã vận đơn, bên vận chuyển và trạng thái hiện tại của kiện hàng. Phân hệ Vận chuyển cần mã này để ghép thông báo từ ĐVVC với kiện và đơn tương ứng. Ví dụ, khi kiện có mã VĐ-01 đã giao, Bán hàng/CSKH có thể tra mã đó để thông báo kết quả cho khách.

### C.7 ShipmentEvent — Sự kiện vận chuyển

`ShipmentEvent` ghi từng lần ĐVVC thông báo một thay đổi, kèm mã sự kiện, thời điểm và trạng thái đối tác gửi. Các dòng sự kiện giúp xem lại hành trình và nhận biết thông báo gửi lặp. Ví dụ, VĐ-01 giao thất bại vào buổi sáng và giao thành công vào hôm sau. `Shipment` cho biết trạng thái hiện tại là đã giao, còn hai `ShipmentEvent` giải thích kiện đã đi qua những lần giao nào.

### C.8 Return/RMA — Hồ sơ đổi, trả hoặc hàng hoàn

`Return` tập hợp thông tin về kiện quay về, gồm đơn hoặc vận đơn liên quan, mặt hàng, lý do và kết quả kiểm tra. `RMA` là mã hoặc hồ sơ cho phép và theo dõi yêu cầu đổi/trả sau giao. Phân hệ Đổi/trả cần hồ sơ để biết kiện nào đang chờ về, đã thực nhận và sẽ được xử lý ra sao. Ví dụ, kiện COD quay về vì giao thất bại được nhận theo mã vận đơn. Nếu khách đã nhận rồi mới yêu cầu trả, shop dùng hồ sơ RMA để theo dõi yêu cầu đó. Trong cả hai trường hợp, kho chỉ tăng lượng có thể bán sau khi thực nhận và kiểm tra đạt.

### C.9 Statement/Remittance — Bảng kê và chứng từ chuyển tiền

`Statement` là bảng kê của đối tác, cho biết họ báo đã thu hoặc đã xử lý giao dịch nào. `Remittance` lưu thông tin về khoản đối tác chuyển cho shop, chẳng hạn số tiền, kỳ và mã chuyển khoản. Kế toán cần hai nguồn này để so với số phải thu theo đơn và xác nhận tiền thực nhận bằng sao kê ngân hàng. Ví dụ, bảng kê tháng ghi nhiều vận đơn, còn ĐVVC chuyển một khoản tổng hợp. Kế toán dùng mã kỳ hoặc mã chuyển khoản để đối chiếu khoản tiền về với tổng các dòng thuộc kỳ đó.

### C.10 CarrierInvoice — Hóa đơn dịch vụ vận chuyển

`CarrierInvoice` ghi khoản phí shop phải trả ĐVVC, kỳ tính phí và tình trạng kiểm tra, phê duyệt hoặc thanh toán. Kế toán cần hồ sơ riêng vì đây là tiền **shop trả cho ĐVVC**, còn COD là tiền **ĐVVC thu hộ và chuyển về shop**. Ví dụ, ĐVVC chuyển đủ tiền COD đã thu trong tháng. Shop kiểm tra hóa đơn vận chuyển và thanh toán phí bằng một giao dịch riêng.

### C.11 ReconciliationCase — Hồ sơ chênh lệch đối soát

`ReconciliationCase` ghi khoản chưa khớp, số chênh lệch, chứng từ, người phụ trách và kết quả xử lý. Một hồ sơ riêng giúp theo dõi vấn đề qua nhiều lần kiểm tra đến khi có kết luận. Ví dụ, bảng kê ghi đã thu 300.000 đồng nhưng chứng từ của khoản cần đối chiếu chỉ cho thấy shop nhận 280.000 đồng. Kế toán mở hồ sơ thiếu 20.000 đồng và dùng mã kỳ hoặc mã chuyển khoản để xác minh với ĐVVC.

### C.12 OutboxEvent/InboxEvent — Bản ghi thông báo gửi và nhận

`OutboxEvent` lưu việc hệ thống **cần gửi đi** để có thể thử lại khi mất kết nối. Ví dụ, sau khi tạo yêu cầu vận đơn, ứng dụng lưu yêu cầu gửi ĐVVC vào hộp thư gửi. Nếu đối tác tạm thời chưa phản hồi, tiến trình nền có thể tiếp tục xử lý yêu cầu đó.

`InboxEvent` lưu thông báo hệ thống **đã nhận** để nhận biết và kiểm soát việc xử lý lặp. Ví dụ, nếu ĐVVC gửi cùng một thông báo “đã giao” hai lần với cùng mã sự kiện, ứng dụng nhận diện lần gửi lặp và chỉ áp dụng nghiệp vụ một lần. `InboxEvent` theo dõi việc tiếp nhận thông báo kỹ thuật, còn `ShipmentEvent` ghi thay đổi có ý nghĩa đối với hành trình vận đơn.

