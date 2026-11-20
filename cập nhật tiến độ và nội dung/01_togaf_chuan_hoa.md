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
- Với COD, hệ thống gửi `COD amount` đúng bằng tổng tiền đơn. Khi giao thành công, shipper thu đúng số tiền này từ khách thay mặt ĐVVC. Cuối tháng ĐVVC lập bảng kê số đã thu; shop/ĐVVC đối chiếu sơ bộ với COD theo đơn, xử lý điểm chưa khớp rồi ĐVVC chuyển **toàn bộ tiền COD đã thu**. Tiền vào ngân hàng là nguồn thứ ba để shop kiểm tra và đóng kỳ.
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

Theo TOGAF ADM, mô tả hiện trạng và kiến trúc đích theo cùng phạm vi rồi đối chiếu các cấu phần tương ứng. Pha B xét nghiệp vụ, pha C xét dữ liệu và ứng dụng, pha D xét công nghệ. Kỹ thuật Gap Analysis xét cả cấu phần được giữ lại, cấu phần có ở đích nhưng thiếu ở hiện trạng và cấu phần hiện có vắng mặt ở đích. Với cấu phần vắng mặt ở đích, cần xác định đó là chủ đích loại bỏ hay một thiếu sót của thiết kế. Các bảng bên dưới tóm tắt kết quả đối chiếu cho phạm vi bài tập lớn. [The Open Group — TOGAF 10th Edition, A Pocket Guide, mục 5.3.2 và 6.2.3–6.2.5](https://studylib.net/doc/28508170/togaf10--1-)

Baseline dưới đây là kịch bản SME giả định của đề tài. Target mô tả cách vận hành và các cấu phần cần có. Cột Gap ghi chênh lệch giữa hai trạng thái. Cột WP chỉ ra gói công việc xử lý từng phần của khoảng thiếu. Xem phạm vi bàn giao và thứ tự thực hiện ở mục 7.

### 5.1 Nghiệp vụ (Business Architecture — pha B)

| Khía cạnh | Hiện trạng (Baseline) | Kiến trúc đích (Target) | Khoảng thiếu (Gap) | Gói công việc xử lý (WP) |
|---|---|---|---|---|
| Tiếp nhận và xử lý đơn | Khách đặt qua website. Nhân viên xuất Excel hoặc chép thông tin qua Zalo để chuyển đơn sang khâu xử lý. | Giữ kênh đặt hàng qua website. Đơn được chuyển thẳng vào luồng kiểm tra, xác nhận và bàn giao cho kho, với trạng thái theo dõi xuyên suốt. | **GAP-B01.** Thiếu luồng bàn giao đơn thống nhất giữa website và vận hành. Bỏ bước chép lại đơn khỏi quy trình thường ngày. | WP-02 |
| Giữ hàng và xử lý tồn | Kho ghi sổ hoặc trừ tồn trên Excel. Hàng đang giao và hàng đang hoàn khó theo dõi. | Giữ hàng khi xác nhận đơn. Giải phóng phần giữ chỗ nếu hủy trước xuất kho. Hàng quay về chỉ được cộng vào tồn khả dụng sau khi kho thực nhận và kiểm tra đạt. | **GAP-B02.** Thiếu quy tắc giữ, giải phóng và nhập lại hàng theo từng mốc nghiệp vụ. | WP-02 (giữ và giải phóng hàng) / WP-03 (nhập lại hàng hoàn) |
| Giao hàng và đổi/trả | Nhân viên tra cứu trạng thái giao thủ công. Kiện chuyển hoàn được kiểm đếm tại kho. Yêu cầu đổi/trả sau giao trao đổi qua tin nhắn. | Theo dõi từng lần giao và lý do thất bại. Xử lý giao lại hoặc chuyển hoàn theo chính sách. Kho nhận và kiểm hàng hoàn. Yêu cầu đổi/trả sau giao có hồ sơ riêng. | **GAP-B03.** Thiếu quy trình theo dõi từ lần giao thất bại hoặc yêu cầu đổi/trả đến khi nhận hàng, kiểm hàng và chốt hướng xử lý. | WP-03 |
| Thanh toán và đối soát | Kế toán dò bảng kê COD cuối tháng theo mã vận đơn. Giao dịch chuyển khoản khó gắn với đơn và hồ sơ lệch tiền khó tra cứu. | COD cuối tháng đối chiếu số phải thu, số ĐVVC báo đã thu và tiền thực chuyển. Hóa đơn phí ĐVVC được kiểm và thanh toán riêng. Với QR, xác nhận và đối soát giao dịch theo mã tham chiếu. Mỗi khoản lệch có người phụ trách và trạng thái xử lý. | **GAP-B04.** Thiếu quy trình đối chiếu COD đến bước xác nhận tiền vào ngân hàng, theo dõi trách nhiệm xử lý lệch và kiểm hóa đơn phí riêng. Thiếu luồng xác nhận và đối soát QR theo đơn. | WP-02 (xác nhận QR theo đơn) / WP-04 (đối soát COD/QR, xử lý lệch và hóa đơn phí) |

### 5.2 Dữ liệu (Data Architecture — pha C)

| Khía cạnh | Hiện trạng (Baseline) | Kiến trúc đích (Target) | Khoảng thiếu (Gap) | Gói công việc xử lý (WP) |
|---|---|---|---|---|
| Định danh, trạng thái và lịch sử | Mã đơn, vận đơn và chứng từ nằm rải rác. Trạng thái và lịch sử xử lý nằm trong file hoặc tin nhắn. | Mã đơn liên kết được với vận đơn, giao dịch và hồ sơ đổi/trả. Đơn, tồn, vận chuyển và thanh toán có trạng thái riêng. Thay đổi quan trọng có nguồn, thời điểm và người thực hiện. | **GAP-D01.** Thiếu quy ước định danh, liên kết dữ liệu, mô hình trạng thái riêng và lịch sử thay đổi có thể tra cứu. | WP-01 |
| Dữ liệu tồn kho và tài chính | Số tồn chủ yếu là số dư bảng tính. Số tiền theo đơn, bảng kê, sao kê và hóa đơn nằm ở các nguồn riêng. | Lưu giữ chỗ và từng biến động tồn. Phân biệt phí giao thu khách, khoản COD phải thu, số đã thu, số đã chuyển, giao dịch QR và hóa đơn phí ĐVVC. Liên kết được mỗi khoản với chứng từ tương ứng. | **GAP-D02.** Thiếu bản ghi chi tiết để giải thích biến động tồn, đối chiếu từng khoản tiền và phân biệt tiền khách trả với chi phí shop trả. | WP-02 (giữ chỗ và biến động tồn) / WP-03 (biến động hàng hoàn) / WP-04 (sổ tiền và chứng từ) |

### 5.3 Ứng dụng (Application Architecture — pha C)

| Khía cạnh | Hiện trạng (Baseline) | Kiến trúc đích (Target) | Khoảng thiếu (Gap) | Gói công việc xử lý (WP) |
|---|---|---|---|---|
| Đơn hàng và tồn kho | Website tiếp nhận đơn. Bảng tính và tin nhắn hỗ trợ xử lý tiếp theo. | Website chuyển đơn vào OMS. OMS phối hợp với phân hệ kho để kiểm tra, giữ và giải phóng hàng. Nhân viên tra cứu đơn trên giao diện quản trị. | **GAP-A01.** Thiếu kết nối website–OMS và chức năng phối hợp xử lý đơn với tồn kho. | WP-02 |
| Vận chuyển và hàng hoàn | Trạng thái giao được tra cứu thủ công. Kho ghi nhận kiện hoàn bằng thao tác rời rạc. | Phân hệ vận chuyển tạo vận đơn, nhận sự kiện từ ĐVVC và phục hồi khi tích hợp lỗi. Phân hệ đổi/trả liên kết kiện hoàn với hồ sơ kiểm hàng và cập nhật tồn một lần. | **GAP-A02.** Thiếu tích hợp ĐVVC, chuẩn hóa trạng thái, xử lý thông báo lặp và liên kết hồ sơ nhận hoàn với tồn kho. | WP-03 |
| QR, đối soát và báo cáo | Kế toán kiểm chuyển khoản hoặc ghép bảng kê thủ công. | Tích hợp Đơn vị QR để tạo mã và nhận kết quả đã xác thực. Phân hệ đối soát nhập bảng kê, ghép chứng từ với khoản tiền, tạo hồ sơ lệch và tổng hợp báo cáo giao thất bại, hàng hoàn, COD phải thu. | **GAP-A03.** Thiếu tích hợp xác nhận QR theo đơn và chức năng đối soát, xử lý lệch, báo cáo tập trung. | WP-02 (tích hợp QR) / WP-04 (đối soát và xử lý lệch) / WP-05 (báo cáo) |

### 5.4 Công nghệ (Technology Architecture — pha D)

| Khía cạnh | Hiện trạng (Baseline) | Kiến trúc đích (Target) | Khoảng thiếu (Gap) | Gói công việc xử lý (WP) |
|---|---|---|---|---|
| Hạ tầng và bảo vệ dữ liệu | Website nhận đơn, còn hồ sơ vận hành nằm trên máy cá nhân và trong ứng dụng nhắn tin. Theo giả định của bài, các hồ sơ này chưa có cơ chế kiểm soát và khôi phục tập trung. | Hạ tầng chạy ứng dụng và cơ sở dữ liệu tập trung, bảo vệ kết nối bằng HTTPS, giới hạn truy cập theo vai trò, ghi nhật ký, giám sát vận hành và sao lưu có kiểm tra khôi phục. | **GAP-T01.** Thiếu môi trường vận hành tập trung và các kiểm soát nhất quán về truy cập, truyền dữ liệu, nhật ký, giám sát và khôi phục. | WP-01 (hạ tầng và kiểm soát nền) / WP-05 (giám sát, sao lưu và kiểm tra khôi phục) |

### 5.5 Ma trận phân tích khoảng thiếu (Gap Analysis Matrix)

Đọc theo hàng để xem cấu phần hiện có sẽ được giữ lại hay rút khỏi kiến trúc đích. Đọc theo cột để xem mỗi cấu phần đích đã có từ trước hay cần bổ sung. Ma trận của The Open Group đặt **Baseline theo hàng**, **Target theo cột**, thêm hàng cuối **New** và cột cuối **Eliminated**. Nếu cấu phần cũ được thay bằng cấu phần khác, ghi phần cũ ở cột **Eliminated** và phần bổ sung ở hàng **New**, rồi dùng mã GAP để liên kết hai thay đổi. Hướng dẫn dùng nhãn **Included** cho cấu phần có ở cả hai trạng thái. [The Open Group — TOGAF 10th Edition, A Pocket Guide, mục 5.3.2](https://studylib.net/doc/28508170/togaf10--1-)

Mỗi bảng tóm tắt một miền. **Included** nghĩa là giữ lại, **New** nghĩa là bổ sung, **Eliminated** ghi phần chủ đích rút khỏi phạm vi vận hành. Nếu phát hiện một thành phần cần thiết bị bỏ sót ở đích, phải ghi nhận khoảng thiếu để xem xét đưa lại vào thiết kế. Dấu **—** là ô không có đối chiếu trực tiếp. Mã GAP dẫn về mô tả và gói công việc ở mục 5.1–5.4.

#### Nghiệp vụ (pha B)

| Baseline ↓ / Target → | Đặt hàng qua website | Bàn giao đơn và giữ hàng theo quy trình | Theo dõi giao, nhận và kiểm hàng hoàn | Đối soát COD/QR và kiểm phí riêng | Eliminated |
|---|---|---|---|---|---|
| Khách đặt hàng qua website | Included | — | — | — | — |
| Chép lại đơn để chuyển kho và trừ tồn thủ công | — | — | — | — | Bỏ thao tác này trong luồng thường ngày (GAP-B01, GAP-B02) |
| Tra cứu giao và xử lý hàng hoàn rời rạc | — | — | — | — | Bỏ cách theo dõi rời rạc (GAP-B03) |
| Dò bảng kê thủ công để chốt tiền | — | — | — | — | Bỏ cách chốt chỉ dựa vào dò bảng kê (GAP-B04) |
| **New** | — | Bàn giao đơn trực tiếp, giữ và giải phóng hàng theo mốc (GAP-B01, GAP-B02) | Theo dõi lần giao và hồ sơ hàng hoàn đến khi chốt (GAP-B02, GAP-B03) | Kiểm tiền thực nhận, xử lý khoản lệch và thanh toán hóa đơn phí riêng (GAP-B04) | — |

#### Dữ liệu (pha C)

| Baseline ↓ / Target → | Thông tin đơn, vận đơn và chứng từ | Mã liên kết, trạng thái và lịch sử | Sổ biến động tồn, sổ tiền và hồ sơ phí | Eliminated |
|---|---|---|---|---|
| Thông tin đơn, vận đơn và chứng từ ở nhiều nguồn | Included | — | — | — |
| **New** | — | Mã liên kết, trạng thái riêng và lịch sử thay đổi (GAP-D01) | Bản ghi giữ hàng, nhập hoàn, khoản thu, tiền chuyển và phí ĐVVC (GAP-D02) | — |

#### Ứng dụng (pha C)

| Baseline ↓ / Target → | Website | Quản lý đơn và kho | Quản lý giao và đổi/trả | Xác nhận QR, đối soát và báo cáo | Eliminated |
|---|---|---|---|---|---|
| Website nhận đơn | Included | — | — | — | — |
| Excel và tin nhắn dùng để xử lý đơn, tồn và theo dõi ngoại lệ | — | — | — | — | Rút khỏi vai trò công cụ xử lý chính (GAP-A01, GAP-A02) |
| Công cụ ghép bảng kê thủ công | — | — | — | — | Rút khỏi vai trò công cụ đối soát chính (GAP-A03) |
| **New** | — | Phần mềm quản lý đơn kết nối với website và kho (GAP-A01) | Tích hợp ĐVVC và ghi nhận hàng hoàn (GAP-A02) | Kết nối Đơn vị QR, ghép chứng từ, theo dõi chênh lệch và lập báo cáo (GAP-A03) | — |

#### Công nghệ (pha D)

| Baseline ↓ / Target → | Hạ tầng ứng dụng và lưu dữ liệu tập trung | Kiểm soát truy cập, giám sát và khôi phục | Eliminated |
|---|---|---|---|
| Máy cá nhân làm nơi lưu chính của hồ sơ vận hành | — | — | Rút vai trò nơi lưu chính của máy cá nhân (GAP-T01) |
| **New** | Môi trường chạy ứng dụng, cơ sở dữ liệu và nơi lưu chứng từ chung (GAP-T01) | Kết nối bảo mật, phân quyền, nhật ký, giám sát và sao lưu có kiểm tra khôi phục (GAP-T01) | — |

## 6. Kiến trúc đích (Target Architecture)

Ở trạng thái đích, khách vẫn đặt hàng trên website. Đơn được đưa thẳng vào hệ thống quản lý đơn của shop (OMS). Nhân viên bán hàng/CSKH tra cứu được tiến độ, kho biết hàng nào cần giữ hoặc xuất, và kế toán lần theo được số tiền từ đơn hàng đến sao kê.

### 6.1 Nghiệp vụ — Một đơn hàng được xử lý thế nào?

1. **Đặt đơn và giữ hàng.** Shop kiểm tra số hàng có thể bán và giữ đúng số lượng cho đơn. Nếu hủy trước khi xuất kho, shop giải phóng phần đã giữ để bán cho khách khác.
2. **Chọn cách trả tiền.** Với đơn có tiền hàng 280.000 đồng và phí giao thu khách 20.000 đồng, tổng tiền là 300.000 đồng. Nếu khách chọn COD, shipper thu đúng 300.000 đồng khi giao thành công, thay mặt đơn vị vận chuyển (ĐVVC). Nếu khách chọn QR, Đơn vị QR tạo yêu cầu thanh toán 300.000 đồng. Shop chờ xác nhận thanh toán rồi mới giao, và vận đơn có số COD bằng 0.
3. **Giao hàng và xử lý hàng quay về.** Kho đóng gói và bàn giao cho ĐVVC. Nếu giao thất bại, shop phối hợp giao lại hoặc chuyển hoàn. Nếu khách đã nhận hàng rồi mới yêu cầu đổi/trả, shop mở hồ sơ riêng. Hàng quay về chỉ được đưa lại vào số có thể bán sau khi kho thực nhận và kiểm tra đạt.
4. **Kiểm tiền và chốt kỳ.** Với COD, kế toán so số phải thu theo đơn, số ĐVVC báo đã thu và tiền thực chuyển vào tài khoản shop. ĐVVC chuyển đủ tiền đã thu theo kỳ tháng. Với QR, kế toán ghép giao dịch theo mã tham chiếu với bảng kê Đơn vị QR và tiền vào ngân hàng. Khoản lệch có hồ sơ theo dõi. Shop kiểm tra và thanh toán hóa đơn phí ĐVVC riêng.

### 6.2 Dữ liệu — Cần lưu gì để tra lại?

Mỗi đơn có mã để tìm các vận đơn, giao dịch, hồ sơ đổi/trả và chứng từ liên quan. Đơn, hàng trong kho, vận chuyển và thanh toán có trạng thái riêng. Ví dụ, một đơn COD có thể đã giao nhưng shop vẫn đang chờ ĐVVC chuyển tiền.

Sổ kho ghi từng lần giữ, giải phóng, xuất và nhập lại hàng. Hồ sơ tiền ghi riêng số phải thu, số đã thu, số đã chuyển và khoản hoàn tiền nếu có. Phí giao thu khách nằm trong tổng đơn. Hóa đơn phí vận chuyển của shop có hồ sơ riêng và được liên kết với chứng từ thanh toán.

### 6.3 Ứng dụng — Ai dùng phần nào?

| Phần của hệ thống | Công việc hỗ trợ |
|---|---|
| Website và màn hình quản trị | Khách đặt và theo dõi đơn. Nhân viên bán hàng/CSKH xem trạng thái để hỗ trợ khách. |
| Quản lý đơn và kho | Tiếp nhận đơn, giữ hàng, hướng dẫn kho chuẩn bị đơn và lưu biến động tồn. |
| Vận chuyển và đổi/trả | Gửi yêu cầu tạo vận đơn cho ĐVVC, nhận kết quả giao, theo dõi kiện quay về và lưu kết quả kiểm hàng. |
| Thanh toán, đối soát và báo cáo | Nhận thông báo QR, ghi khoản COD, so bảng kê với tiền thực nhận và theo dõi các khoản lệch. |

### 6.4 Công nghệ — Hệ thống chạy và được bảo vệ ra sao?

Các phân hệ chạy chung trên một ứng dụng. Dữ liệu nghiệp vụ được lưu trong cơ sở dữ liệu PostgreSQL và chứng từ được lưu ở nơi lưu trữ tập trung. Hệ thống phân quyền theo công việc, ghi lịch sử thay đổi và dùng kết nối HTTPS khi trao đổi với đối tác.

Khi ĐVVC hoặc Đơn vị QR tạm thời không phản hồi, tác vụ gửi đi được lưu để thử lại. IT theo dõi lỗi, sao lưu dữ liệu và kiểm tra khả năng khôi phục.

## 7. Lộ trình triển khai (Roadmap)

Mỗi Plateau mô tả trạng thái vận hành đạt được sau khi hoàn thành các gói công việc của mốc đó. Lộ trình đi từ nền tảng và xử lý đơn–tồn đến giao hàng, xử lý hàng hoàn và chốt đối soát.

| Plateau | Work package | Phạm vi và kết quả bàn giao | Phụ thuộc |
|---|---|---|---|
| 1 — Đơn và tồn vận hành trên nền tảng chung | WP-01 — Chuẩn hóa dữ liệu và trạng thái | Chuẩn hóa mã liên kết đơn, vận đơn, giao dịch và hồ sơ đổi/trả. Định nghĩa trạng thái từng loại, thông tin cần ghi trong lịch sử và thiết lập môi trường ứng dụng, cơ sở dữ liệu, HTTPS, phân quyền và nhật ký nền. | — |
| 1 — Đơn và tồn vận hành trên nền tảng chung | WP-02 — Quản lý đơn, tồn kho và thanh toán tại checkout | Kết nối website với OMS và phân hệ kho. Cho phép tra cứu đơn, giữ hàng, giải phóng giữ chỗ và ghi biến động tồn. Ghi số COD phải thu theo đơn. Tích hợp tạo QR và xác nhận kết quả thanh toán theo mã tham chiếu. | WP-01 |
| 2 — Theo dõi giao hàng và xử lý hàng hoàn | WP-03 — Vận chuyển và đổi/trả | Tạo vận đơn và nhận trạng thái từ ĐVVC, có xử lý sự kiện lặp và lỗi tích hợp. Theo dõi giao lại hoặc chuyển hoàn, tiếp nhận hồ sơ đổi/trả, kiểm hàng và cập nhật biến động tồn hàng hoàn đúng một lần. | WP-02 |
| 3 — Đối soát và kiểm soát vận hành | WP-04 — Đối soát COD/QR và hóa đơn vận chuyển | Lập sổ và liên kết chứng từ tài chính. Đối chiếu số COD theo đơn, bảng kê đã thu và tiền vào tài khoản shop theo tháng. Đối soát QR theo giao dịch, theo dõi người phụ trách và trạng thái khoản lệch. Kiểm tra và ghi nhận thanh toán hóa đơn ĐVVC riêng. | WP-02, WP-03 |
| 3 — Đối soát và kiểm soát vận hành | WP-05 — Báo cáo và vận hành thử | Báo cáo đơn giao thất bại, hàng hoàn và COD phải thu. Bổ sung giám sát, cảnh báo, sao lưu và kiểm tra khôi phục. Kiểm thử hiệu năng, bảo mật và chạy thử toàn luồng. | WP-04 |

## 8. Quản trị và điều kiện nghiệm thu

- Mọi thay đổi trạng thái phải tuân state machine và phát audit/event.
- Không merge API nếu thiếu authorization, idempotency rule và error contract tương ứng.
- Kế toán phê duyệt mapping statement; kho phê duyệt inventory disposition; chủ shop phê duyệt KPI và residual risk.
- Kiến trúc được chấp nhận khi 03 BPMN, 04 ADR, traceability matrix và 02 kịch bản prototype nhất quán với catalog này.

