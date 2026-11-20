# TOGAF — kiến trúc Order-to-Cash cho SME thương mại điện tử

## Cách đọc chương này

TOGAF có thể hiểu là một phương pháp giúp nhóm trả lời bốn câu hỏi:

1. **Vì sao phải xây hệ thống?** — xem phần Tầm nhìn kiến trúc.
2. **Hệ thống phải làm được gì?** — xem yêu cầu chức năng và yêu cầu chất lượng.
3. **Hiện tại khác mục tiêu ở đâu?** — xem bảng Hiện trạng–Đích–Khoảng thiếu.
4. **Nên xây theo thứ tự nào?** — xem Lộ trình.

Trong tài liệu, từ tiếng Anh được giữ lại để đối chiếu với chuẩn. Ví dụ, `Baseline` nghĩa là hiện trạng, `Target` nghĩa là kiến trúc đích, còn `Gap` là khoảng thiếu cần khắc phục. Có thể xem toàn bộ thuật ngữ tại `07_tu_dien_thuat_ngu.md`.

## 1. Phiếu yêu cầu thực hiện kiến trúc (Request for Architecture Work)

Đây là “đề bài chính thức” của công việc thiết kế: ai yêu cầu, vấn đề là gì, phạm vi đến đâu và nhóm phải bàn giao những gì. Nó giúp tránh tình trạng mỗi thành viên hiểu đề tài theo một hướng khác nhau.

| Thuộc tính | Nội dung |
|---|---|
| Sponsor | Chủ doanh nghiệp SME |
| Vấn đề | Dữ liệu đơn–tồn–giao–tiền phân tán; giao thất bại/hoàn đáng kể; đối soát COD thủ công; QR chưa gắn chắc với đơn; đổi/trả làm lệch tồn và tiền |
| Mục tiêu | Thiết kế kiến trúc đích và lộ trình cho Order-to-Cash xuyên suốt, có kiểm soát ngoại lệ và truy vết tài chính |
| Phạm vi tổ chức | Bán hàng/CSKH, kho, kế toán, IT; khách hàng, ĐVVC và Ngân hàng/Đơn vị cung cấp thanh toán QR là bên ngoài |
| Phạm vi hệ thống | Website + OMS, Inventory, Payment, Shipping, Return, Reconciliation, Reporting |
| Ràng buộc | 01 website, 01 kho trung tâm, 01 ĐVVC và 01 Ngân hàng/Đơn vị cung cấp thanh toán QR giả lập; 100–300 đơn/ngày; ngân sách và nhân lực SME |
| Deliverable | TOGAF, 06 ArchiMate viewpoint, 03 BPMN, 04 ADR, risk/traceability, prototype, báo cáo và 12 slide |
| Giả định | 70% COD và 15–20% giao thất bại/hoàn chỉ là giả định để stress-test thiết kế; không phải số liệu ngành |

## 2. Tầm nhìn kiến trúc (Architecture Vision)

Xây dựng một nền tảng Order-to-Cash tích hợp, trong đó mỗi đơn hàng có thể được truy vết từ lúc tạo đơn, giữ chỗ tồn kho, thanh toán COD/QR, giao nhận, đổi/trả đến khi tiền và tồn kho được đối soát. Kiến trúc ưu tiên đơn giản, khả năng kiểm toán và xử lý lặp an toàn, phù hợp quy mô SME.

### 2.1 Phạm vi

Trong phạm vi: đặt hàng, xác nhận QR/COD, reservation, pick-pack-handover, shipment tracking, retry/RTO, đổi/trả, QC, refund, COD/QR reconciliation, dispute và báo cáo.

Ngoài phạm vi: procurement, multi-warehouse, marketplace, dynamic pricing, general ledger, route optimization, production-grade HA và tích hợp pháp lý hóa đơn điện tử.

### 2.2 Bên liên quan (stakeholder) và mối quan tâm (concern)

“Bên liên quan” không chỉ là người dùng phần mềm mà còn gồm các đối tác trao đổi hàng hóa, tiền và dữ liệu với shop. Bảng dưới đây xác định rõ mỗi bên làm gì trong luồng Order-to-Cash và điều họ cần hệ thống bảo đảm.

| Stakeholder | Vai trò/chức năng | Mối quan tâm chính |
|---|---|---|
| Chủ doanh nghiệp | Quyết định đầu tư; phê duyệt chính sách bán hàng, phí vận chuyển, lộ trình triển khai và các điều chỉnh tài chính quan trọng; theo dõi KPI | Chi phí, doanh thu, dòng tiền COD, hiệu quả vận chuyển và khả năng kiểm soát hoạt động |
| Khách hàng | Đặt hàng; chọn COD hoặc QR; thanh toán, nhận hàng; theo dõi đơn và yêu cầu đổi/trả | Thông tin đơn chính xác, thanh toán an toàn, không bị thu trùng, giao hàng và đổi/trả thuận tiện |
| Nhân viên bán hàng/CSKH | Kiểm tra thông tin đơn khi cần, theo dõi trạng thái, hỗ trợ khách tra cứu đơn và phối hợp giao lại khi giao thất bại | Thông tin đơn chính xác, dễ tra cứu và hỗ trợ khách kịp thời |
| Nhân viên kho | Lấy–đóng gói–bàn giao hàng; nhận hàng chuyển hoàn/đổi trả; quét mã, kiểm tra chất lượng và quyết định nhập lại hoặc cách ly | Tồn kho chính xác, tránh xuất/nhập trùng và không bán hàng hoàn khi chưa QC đạt |
| Nhân viên kế toán | Đối soát COD/QR; kiểm tra bảng kê và tiền vào ngân hàng; mở, điều tra và theo dõi hồ sơ chênh lệch; kiểm hóa đơn ĐVVC và thực hiện thanh toán đã được phê duyệt | Dòng tiền, công nợ, chênh lệch, chứng từ đầy đủ và việc không khấu trừ nhầm phí ĐVVC vào COD |
| Đơn vị vận chuyển | Nhận yêu cầu giao; giao hàng; thu đúng COD; cập nhật trạng thái, giao lại/chuyển hoàn; lập bảng kê, chuyển đủ COD gross và xuất hóa đơn phí riêng theo tháng | Dữ liệu vận đơn/COD chính xác, trao đổi trạng thái tin cậy và quy trình đối soát–thanh toán đúng kỳ |
| Ngân hàng/Đơn vị cung cấp thanh toán QR | Nhận yêu cầu tạo và quản lý QR Payment Intent; xử lý thanh toán; gửi callback/bảng kê; tiếp nhận yêu cầu hoàn tiền từ shop và thông báo kết quả | Mã tham chiếu và số tiền chính xác, callback an toàn/chống trùng, trạng thái giao dịch và đối soát rõ ràng |
| Bộ phận IT/vận hành hệ thống | Quản trị người dùng/phân quyền; duy trì tích hợp; giám sát lỗi, retry, sao lưu–khôi phục và bảo mật hệ thống | Tính sẵn sàng, bảo mật, khả năng phục hồi, truy vết và dễ bảo trì |

### 2.3 Mục tiêu, kết quả và chỉ số đo (Goal, Outcome, KPI)

Mục tiêu chỉ có ý nghĩa khi đo được. Ví dụ, “tồn kho chính xác” được kiểm tra bằng việc chạy nhiều yêu cầu mua cùng lúc và xác nhận số tồn không bao giờ âm.

| Goal | Outcome/KPI thiết kế |
|---|---|
| G-01 Quản lý đơn hàng thống nhất | ≥95% đơn hợp lệ đi qua luồng mà không phải nhập lại dữ liệu trong prototype |
| G-02 Cải thiện đối soát COD | 100% khoản COD dự kiến được so với bảng kê ĐVVC và tiền thực nhận; lệch tiền thành hồ sơ xử lý |
| G-03 Quản lý hàng hoàn nhất quán | 100% đơn giao thất bại/hoàn có shipment, lần giao, phiếu nhận hoàn và kết quả kiểm hàng |
| G-04 Bảo đảm tồn kho chính xác | Không bán vượt tồn trong kiểm thử đồng thời; chỉ tăng hàng bán được sau khi nhận hàng thật và QC đạt |
| G-05 Có thể truy vết | Thay đổi quan trọng có mã tham chiếu, thời điểm, nguồn và người/hệ thống thực hiện |
| G-06 Dễ mở rộng | Có thể thêm ĐVVC hoặc nhà cung cấp thanh toán QR qua adapter mà không sửa logic lõi của đơn, kho và đối soát |

## 3. Nguyên tắc kiến trúc (Architecture Principles)

Nguyên tắc kiến trúc là các quy tắc nhóm phải tuân thủ trong suốt quá trình thiết kế và lập trình. Chẳng hạn, “mỗi miền có một nguồn dữ liệu chính” nghĩa là chỉ phân hệ Kho được quyền quyết định số tồn; phân hệ Đơn hàng phải hỏi Kho thay vì tự sửa số lượng.

| Principle | Hệ quả thiết kế |
|---|---|
| AP-01 Nguồn dữ liệu có thẩm quyền (Single Source of Truth) | Order, Inventory, Payment, Shipment, Return và Reconciliation có component sở hữu rõ ràng |
| AP-02 Tách trạng thái nghiệp vụ | Trạng thái đơn, giao hàng, thanh toán và đổi/trả không bị gộp thành một trạng thái mơ hồ |
| AP-03 Truy vết thay đổi | Không xóa/sửa lịch sử tiền và tồn; điều chỉnh phải có bút toán, người thực hiện và mã tham chiếu |
| AP-04 Tích hợp có thể phục hồi | Sự kiện có mã chống trùng; có retry, đồng bộ lại và hàng đợi xử lý thủ công |
| AP-05 Đơn giản phù hợp SME | Modular monolith + PostgreSQL; chỉ tách dịch vụ/broker khi có nhu cầu đo được |

Các quy tắc kỹ thuật bổ sung để hiện thực nguyên tắc trên: API qua adapter để mô hình đối tác không rò vào lõi; RBAC/TLS/che dữ liệu nhạy cảm; ledger chỉ ghi thêm cho tiền và tồn kho.

### 3.1 Chính sách tiền hàng và phí vận chuyển được chọn

`Ngân hàng/Đơn vị cung cấp thanh toán QR` là tên tổng quát cho ngân hàng có API/callback, cổng thanh toán, PSP hoặc dịch vụ mock trong prototype. Thành phần này tạo và quản lý QR, sau đó thông báo kết quả cho shop. Thiết kế không khẳng định NAPAS trực tiếp callback cho shop.

- `Tiền khách phải trả = tiền hàng sau giảm giá + phí vận chuyển thu của khách`. Phí vận chuyển hiển thị ở checkout và nằm trong tổng đơn.
- Shop cấu hình phí vận chuyển thu khách ít nhất bằng chi phí vận chuyển ước tính, có thể cộng một mức đệm nhỏ để hạn chế phải bù; đây là chính sách giá của shop, không phải phí do ĐVVC tự cộng khi giao.
- Với COD, hệ thống gửi `COD amount` đúng bằng tổng tiền đơn. Cuối tháng ĐVVC lập bảng kê số đã thu; shop/ĐVVC đối chiếu sơ bộ với COD theo đơn, xử lý điểm chưa khớp rồi ĐVVC chuyển **toàn bộ tiền COD đã thu**. Tiền vào ngân hàng là nguồn thứ ba để shop kiểm tra và đóng kỳ.
- Với QR, Ngân hàng/Đơn vị cung cấp thanh toán QR tạo Payment Intent bằng đúng tổng tiền đơn, gồm cả phí vận chuyển thu khách. ĐVVC nhận vận đơn có `COD amount = 0` và không thu thêm tiền tại cửa.
- Giả định bài tập: Đơn vị QR không thu phí. Phí dịch vụ vận chuyển không được khấu trừ vào tiền COD; cuối tháng ĐVVC xuất hóa đơn phí riêng và shop thanh toán riêng.
- Vì vậy phải tách `Customer Shipping Charge` (khoản khách trả trong đơn) với `Carrier Shipping Expense/Invoice` (chi phí shop phải trả ĐVVC). Không dùng phí vận chuyển để làm giảm trạng thái `PAID` của khách.

## 4. Yêu cầu hệ thống

### 4.1 Yêu cầu chức năng — hệ thống phải làm được gì

| ID | Yêu cầu | Acceptance tóm tắt |
|---|---|---|
| FR-01 | Tạo và theo dõi đơn hàng | Đơn có dòng hàng, tổng tiền, địa chỉ và lịch sử trạng thái hợp lệ |
| FR-02 | Kiểm tra và giữ chỗ tồn khi xác nhận đơn | Giữ chỗ nguyên tử; không để số có thể bán bị âm |
| FR-03 | Chọn COD hoặc QR | Tổng khách trả gồm tiền hàng và phí vận chuyển thu khách; COD gửi đúng tổng này cho ĐVVC, QR tạo intent đúng tổng này và vận đơn có COD bằng 0 |
| FR-04 | Tạo yêu cầu giao và theo dõi ĐVVC | Tạo shipment/tracking; nhận và chuẩn hóa trạng thái từ ĐVVC |
| FR-05 | Ghi nhận giao thành công hoặc thất bại | Mỗi lần giao có kết quả, thời điểm, lý do và mã tham chiếu |
| FR-06 | Quản lý giao lại và chuyển hoàn | Giao lại theo chính sách; hết lượt chuyển RTO và theo dõi hàng về |
| FR-07 | Nhận, kiểm và cập nhật tồn hàng hoàn | Quét nhận một lần; QC; chỉ RESTOCK khi hàng thực nhận và đạt chất lượng |
| FR-08 | Đối soát COD dự kiến với COD thực tế | Theo kỳ tháng, so ba nguồn: tổng COD theo đơn, ĐVVC báo đã thu và toàn bộ tiền COD doanh nghiệp thực nhận; không trừ hóa đơn vận chuyển |
| FR-09 | Phát hiện và ghi nhận chênh lệch COD | Mở case có số tiền, nguyên nhân, owner, bằng chứng và trạng thái xử lý |
| FR-10 | Lưu lịch sử trạng thái đơn/tồn/thanh toán | Mỗi thay đổi có nguồn, thời điểm, actor và correlation/reference ID |
| FR-11 | Báo cáo giao thất bại, hàng hoàn và COD phải thu | Lọc theo thời gian/trạng thái; tổng số khớp với dữ liệu chi tiết |
| FR-12 | Phân quyền theo vai trò | Khách hàng, CSKH, kho, kế toán và chủ shop chỉ dùng đúng chức năng được cấp |

### 4.1.1 Yêu cầu bắt buộc của biến thể II-B COD

| ID | Yêu cầu biến thể | Acceptance tóm tắt |
|---|---|---|
| REQ-COD-01 | Luồng giao thất bại và hoàn hàng | Theo dõi đủ lần giao, quyết định giao lại/RTO, nhận hoàn và QC |
| REQ-COD-02 | Đối soát COD ba chiều | Theo tháng so expected COD gross ↔ ĐVVC báo đã thu ↔ gross remittance; carrier invoice tách riêng; thiếu chứng từ hoặc lệch tiền phải được gắn cờ |
| REQ-COD-03 | Tồn kho hàng hoàn chính xác | Chưa nhận và QC thì không tăng hàng có thể bán; sự kiện/scan lặp không tăng tồn nhiều lần |

### 4.1.2 Phần mở rộng để phủ đủ phạm vi đề tài

Các mã `EXT` bổ sung cho phạm vi chung COD/QR và đổi trả, không thay thế bộ FR chính thức của biến thể II-B.

| ID | Yêu cầu mở rộng | Acceptance tóm tắt |
|---|---|---|
| EXT-01 | Thanh toán QR theo từng đơn | Đơn vị QR sinh intent/reference đúng tổng đơn gồm phí giao khách trả; chỉ ghi PAID sau callback/poll đã xác thực; giả định phí QR bằng 0 |
| EXT-02 | Đổi/trả sau giao và hoàn tiền | RMA, điều kiện đổi/trả, QC, đổi hàng hoặc refund có phê duyệt và tham chiếu |
| EXT-03 | Đối soát QR | So payment ledger ↔ bảng kê Đơn vị QR ↔ tiền vào ngân hàng/refund; không có phí QR trong giả định; lệch thành case |

### 4.2 Yêu cầu chất lượng — hệ thống phải hoạt động tốt đến mức nào

Ví dụ, “có chức năng tra cứu đơn” là yêu cầu chức năng. “Ít nhất 95% lần tra cứu trả kết quả trong dưới 2 giây” là yêu cầu chất lượng. Các yêu cầu chất lượng phải có con số hoặc bằng chứng kiểm tra, không nên chỉ viết chung chung như “hệ thống nhanh và an toàn”.

| ID | Thuộc tính | Stimulus–response–measure |
|---|---|---|
| NFR-01 | Hiệu năng | Với dữ liệu demo và 50 người dùng ảo, ít nhất 95% yêu cầu tra cứu đơn dưới 2 giây, lỗi dưới 1% |
| NFR-02 | Tính sẵn sàng | Mục tiêu vận hành 99,5%/tháng; prototype có health check và khởi động lại không mất dữ liệu |
| NFR-03 | Nhất quán/chống ghi trùng | Gửi cùng sự kiện 10 lần vẫn chỉ có một lần nhận hoàn hoặc một bút toán thanh toán có hiệu lực |
| NFR-04 | Khả năng phục hồi tích hợp | Đối tác lỗi được retry có giãn cách; quá ngưỡng vào danh sách xử lý; có thể đồng bộ lại |
| NFR-05 | Bảo mật | Xác thực, RBAC cho giao diện quản trị; kiểm tra callback; TLS; bí mật ngoài mã nguồn |
| NFR-06 | Khả năng truy vết | Thay đổi quan trọng có mã tham chiếu, thời điểm, nguồn, actor và correlation ID |
| NFR-07 | Khả năng bảo trì | Tách logic đơn, tồn, vận chuyển và đối soát; module không ghi trực tiếp bảng của module khác |
| NFR-08 | Toàn vẹn tài chính | Tiền khách trả, tiền COD ĐVVC chuyển và hóa đơn phí vận chuyển được ghi tách biệt; mọi chênh lệch có hồ sơ và trạng thái xử lý |

Các thuộc tính chất lượng tham chiếu ISO/IEC 25010:2023; giá trị ngưỡng là mục tiêu do nhóm chọn.

## 5. Hiện trạng, kiến trúc đích và khoảng thiếu (Baseline, Target, Gap)

Bảng này đọc từ trái sang phải: doanh nghiệp đang làm thế nào → muốn làm thế nào → còn thiếu thành phần nào → giao phần thiếu đó cho gói công việc nào.

| Miền | Baseline | Target | Gap | Work package |
|---|---|---|---|---|
| Business | Excel/Zalo, xử lý ngoại lệ tùy người | Quy trình chuẩn order–pay–ship–return–reconcile | Thiếu ownership, SLA và state model | WP-01, WP-03 |
| Order | Đơn web xuất file | OMS là nguồn sự thật của Order | Thiếu lifecycle và correlation | WP-01, WP-02 |
| Inventory | Trừ lùi bảng tính | Reservation + append-only ledger + QC/quarantine | Dễ oversell, nhập hoàn trùng | WP-01, WP-02, WP-03 |
| COD | Dò bảng kê cuối kỳ | COD ledger + đối soát ba chiều theo tháng; nhận đủ COD gross | Không biết expected/collected/remitted/disputed | WP-04 |
| QR | Chuyển khoản khó gắn đơn | QR intent/reference/callback/refund/reconciliation qua Đơn vị QR | Thiếu adapter và settlement model | WP-02, WP-04 |
| Phí ĐVVC | Có thể bị trộn vào tiền COD | Hóa đơn phí vận chuyển riêng; shop kiểm tra và thanh toán riêng, không net-off COD | Chưa tách customer charge và carrier expense | WP-04, WP-05 |
| Shipping | Theo dõi thủ công | API + signed/idempotent webhook + RTO | Thiếu mapping và retry | WP-03 |
| Return/Exchange | Chat rời rạc | RMA + eligibility + QC + disposition + refund/exchange | Không truy vết reverse flow | WP-03 |
| Data | Trạng thái trộn lẫn | State machine riêng và ID xuyên suốt | Không có canonical model | WP-01 |
| Technology | File/máy cá nhân | Web app modular monolith, PostgreSQL, object storage, audit/monitoring | Thiếu bảo mật, backup, observability | WP-01, WP-05 |

## 6. Target Architecture tóm tắt

- Business: năm value stream step — Capture Order, Collect/Commit Payment, Fulfill & Deliver, Handle Return, Reconcile & Close; tiền COD và hóa đơn vận chuyển là hai luồng độc lập.
- Data: Order/CustomerShippingCharge, Reservation/StockEntry, Payment/PaymentEntry, Shipment/ShipmentEvent, CarrierInvoice, Return/RMA, Statement/ReconciliationCase.
- Application: Web/Backoffice, Order, Inventory, Payment, Fulfillment/Shipping, Return, Reconciliation/Reporting và adapters.
- Technology: reverse proxy, application runtime, PostgreSQL, object/file storage, scheduler/outbox worker, logging/monitoring; đối tác ngoài qua HTTPS.

## 7. Lộ trình triển khai (Roadmap)

Không nên xây mọi thứ cùng lúc. Nhóm làm nền tảng và dữ liệu đơn–tồn trước, sau đó mới tích hợp thanh toán/vận chuyển, rồi mới đối soát và xử lý đổi trả. Thứ tự này giảm việc phải sửa lại các phần đã làm.

| Plateau | Work package | Khả năng đạt được | Phụ thuộc |
|---|---|---|---|
| Giai đoạn 1 — Chuẩn hóa nền | WP-01 Chuẩn hóa dữ liệu và trạng thái | Mã dùng chung, state model, RBAC, audit/correlation, nền tảng DB | Không |
| Giai đoạn 1 — Đơn và tồn | WP-02 Order + Inventory | Order, reservation, stock ledger, fulfillment cơ bản, QR/COD selection | WP-01 |
| Giai đoạn 2 — Giao và hoàn | WP-03 Shipping + Returns | Adapter ĐVVC, webhook/outbox, giao thất bại, RTO, nhận hoàn/QC, đổi trả | WP-01, WP-02 |
| Giai đoạn 3 — Đối soát | WP-04 COD Reconciliation | COD ledger, bảng kê/remittance tháng, đối soát ba chiều, case; hóa đơn ĐVVC tách riêng; mở rộng đối soát QR | WP-02, WP-03 |
| Giai đoạn 3 — Kiểm soát | WP-05 Reporting & Operational Controls | Báo cáo, cảnh báo, backup/restore, monitoring, performance/security test và pilot | WP-04 |

## 8. Quản trị và điều kiện nghiệm thu

- Mọi thay đổi trạng thái phải tuân state machine và phát audit/event.
- Không merge API nếu thiếu authorization, idempotency rule và error contract tương ứng.
- Kế toán phê duyệt mapping statement; kho phê duyệt inventory disposition; chủ shop phê duyệt KPI và residual risk.
- Kiến trúc được chấp nhận khi 03 BPMN, 04 ADR, traceability matrix và 02 kịch bản prototype nhất quán với catalog này.

