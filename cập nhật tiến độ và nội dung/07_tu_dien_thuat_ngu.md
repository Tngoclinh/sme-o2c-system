# Từ điển thuật ngữ dễ hiểu

Tài liệu này giải thích các thuật ngữ bằng ví dụ một cửa hàng bán áo trực tuyến. Khi viết báo cáo, nên dùng tiếng Việt trước và ghi thuật ngữ tiếng Anh trong ngoặc ở lần xuất hiện đầu tiên.

## 1. Thuật ngữ nghiệp vụ bán hàng

| Thuật ngữ | Giải thích dễ hiểu | Ví dụ |
|---|---|---|
| Order-to-Cash (O2C) | Toàn bộ quá trình từ khi nhận đơn đến khi nhận, kiểm tra và chốt xong tiền | Khách đặt áo → giao áo → nhận COD → đối chiếu tiền |
| COD | Khách trả tiền khi nhận hàng; người giao hàng thu hộ cửa hàng | Đơn 300.000 đồng, shipper thu 300.000 đồng khi giao |
| QR payment | Khách quét mã để chuyển tiền cho đơn hàng | Mã QR chứa đúng số tiền và mã tham chiếu của đơn |
| Đơn vị vận chuyển (carrier) | Công ty nhận kiện hàng từ shop và giao cho khách | GHN, GHTK hoặc đơn vị giả lập trong prototype |
| PSP/đơn vị thanh toán | Bên trung gian xử lý và thông báo giao dịch QR | Trong prototype là một dịch vụ giả lập gửi thông báo thanh toán |
| Payment intent | Bản ghi cho biết hệ thống đang chờ một khoản thanh toán cụ thể | Chờ 300.000 đồng cho đơn `ord_001` trong 15 phút |
| Mã tham chiếu (reference) | Mã dùng để biết một khoản tiền thuộc đơn nào | Nội dung chuyển khoản chứa `ord_001` |
| Settlement/quyết toán tiền | Tiền đã được bên giữ tiền chuyển thực tế về tài khoản shop | Đơn vị vận chuyển chuyển tổng COD của tuần cho shop |
| Fee/phí | Khoản bị trừ như phí giao hàng, phí thu hộ hoặc phí hoàn | Thu COD 300.000 đồng nhưng shop nhận 270.000 đồng sau phí |
| Refund/hoàn tiền | Trả lại tiền cho khách; được ghi như một giao dịch mới | Hoàn 300.000 đồng cho đơn QR bị trả hàng |
| Đối soát (reconciliation) | So sánh các nguồn dữ liệu để kiểm tra tiền có khớp hay không | So số phải thu, bảng kê đối tác và tiền vào ngân hàng |
| Đối soát ba chiều | So sánh ba nguồn thay vì chỉ hai nguồn | Sổ tiền nội bộ ↔ bảng kê vận chuyển/PSP ↔ sao kê ngân hàng |
| Chênh lệch (discrepancy) | Số tiền hoặc thông tin không khớp | Hệ thống dự kiến 300.000 đồng nhưng chỉ nhận 280.000 đồng |
| Công nợ COD | Tiền đơn vị vận chuyển đã thu hộ nhưng chưa chuyển cho shop | 5 đơn giao thành công nhưng COD chưa được chuyển |
| Aging/tuổi công nợ | Số ngày một khoản tiền vẫn chưa được giải quyết | COD đã chậm chuyển 7 ngày |

## 2. Thuật ngữ kho và đổi trả

| Thuật ngữ | Giải thích dễ hiểu | Ví dụ |
|---|---|---|
| Tồn khả dụng (available) | Số hàng hiện có thể bán ngay | Có 10 áo trong kho và chưa áo nào bị giữ |
| Giữ chỗ tồn kho (reservation) | Tạm dành hàng cho một đơn để người khác không mua mất | Đơn A đặt 2 áo, tồn khả dụng giảm từ 10 xuống 8 |
| Cam kết tồn (commit) | Xác nhận hàng đã được dùng cho đơn và chuẩn bị rời kho | Kho hoàn tất đóng gói 2 áo của đơn A |
| Giải phóng giữ chỗ (release) | Trả hàng đã tạm giữ về tồn khả dụng | Khách không trả QR đúng hạn nên 2 áo được bán lại |
| Sổ biến động tồn kho (inventory ledger) | Danh sách không xóa lịch sử, ghi từng lần tăng/giảm/chuyển trạng thái hàng | Giữ 2 áo, xuất 2 áo, nhận hoàn 2 áo, nhập lại 1 áo |
| Append-only/chỉ ghi thêm | Không sửa bản ghi cũ; nếu sai thì thêm bản ghi điều chỉnh | Không xóa lần xuất kho; thêm một bút toán đảo |
| QC/kiểm tra chất lượng | Kiểm tra hàng hoàn có còn bán được hay không | Áo còn tem và không rách thì đạt QC |
| Quarantine/khu cách ly | Nơi/trạng thái giữ hàng lỗi, chưa được phép bán | Áo bị bẩn được đưa vào khu cách ly |
| RTO/chuyển hoàn do giao thất bại | Hàng quay về shop vì chưa giao thành công cho khách | Khách từ chối nhận, shipper trả kiện về kho |
| Return/trả hàng sau giao | Khách đã nhận hàng rồi mới yêu cầu trả | Khách nhận áo nhưng sai kích thước và gửi trả |
| Exchange/đổi hàng | Khách trả sản phẩm cũ và nhận sản phẩm khác | Đổi áo size M thành size L |
| RMA/phiếu cho phép đổi trả | Mã hồ sơ theo dõi một yêu cầu đổi/trả | `RMA-001` gắn với đơn, lý do và danh sách áo trả |
| Disposition/hướng xử lý hàng | Quyết định cuối cùng sau QC | Nhập lại để bán, cách ly, sửa chữa hoặc hủy |

## 3. Thuật ngữ tích hợp hệ thống

| Thuật ngữ | Giải thích dễ hiểu | Ví dụ |
|---|---|---|
| API | “Cửa giao tiếp” để hai phần mềm gửi yêu cầu và nhận kết quả | Hệ thống shop gọi API tạo vận đơn |
| Endpoint | Một địa chỉ và hành động cụ thể của API | `POST /api/orders` dùng để tạo đơn |
| Webhook/callback | Đối tác chủ động gọi ngược về hệ thống khi có sự kiện | Đơn vị vận chuyển báo “đã giao thành công” |
| Payload | Phần dữ liệu được gửi trong một yêu cầu | Mã đơn, số tiền, trạng thái và thời gian |
| Adapter/bộ chuyển đổi | Bộ phận đổi dữ liệu riêng của đối tác sang dạng chung của hệ thống | `delivered` và `success` đều được đổi thành `DELIVERED` |
| Anti-corruption layer/lớp chống phụ thuộc | Adapter ngăn mô hình riêng của đối tác làm rối mô hình nội bộ | Đổi carrier không buộc sửa toàn bộ Order module |
| Idempotency/xử lý lặp an toàn | Gửi cùng yêu cầu nhiều lần vẫn chỉ tạo một kết quả nghiệp vụ | Webhook “đã trả tiền” đến 10 lần nhưng chỉ ghi tiền một lần |
| Idempotency key/khóa chống trùng | Mã duy nhất dùng để nhận biết yêu cầu đã xử lý | `external_event_id=pay_123` chỉ được ghi một lần |
| Inbox | Bảng lưu các sự kiện nhận từ bên ngoài trước khi xử lý | Lưu callback PSP để chống trùng và kiểm tra lại |
| Outbox | Bảng lưu việc cần gửi ra ngoài, để có thể gửi lại nếu lỗi | Lưu yêu cầu tạo vận đơn rồi worker gửi cho carrier |
| Retry/thử lại | Tự động thực hiện lại khi đối tác tạm thời lỗi | API carrier lỗi thì thử lại sau 1, 2, 4 phút |
| Exponential backoff/giãn cách tăng dần | Mỗi lần thử lại chờ lâu hơn lần trước | 1 phút → 2 phút → 4 phút, tránh gọi dồn dập |
| Worker/tiến trình xử lý nền | Chương trình chạy ngầm để xử lý outbox, báo cáo hoặc việc chậm | Worker gửi lại yêu cầu tạo vận đơn |
| Event/sự kiện | Thông tin cho biết một việc đã xảy ra | `PAYMENT_PAID`, `SHIPMENT_DELIVERED` |
| Correlation ID/mã liên kết | Mã giúp tìm toàn bộ log và thao tác của cùng một luồng | Từ tạo đơn đến webhook đều có `cor_001` |
| External reference/mã bên ngoài | Mã giao dịch/vận đơn do đối tác cấp | Mã vận đơn hoặc mã giao dịch ngân hàng |

## 4. Thuật ngữ kiến trúc và dữ liệu

| Thuật ngữ | Giải thích dễ hiểu | Ví dụ |
|---|---|---|
| Module/phân hệ | Một phần phần mềm chịu trách nhiệm cho một nhóm nghiệp vụ | Order quản lý đơn; Inventory quản lý tồn |
| Modular monolith/ứng dụng nguyên khối có phân hệ | Một ứng dụng được triển khai chung nhưng bên trong chia ranh giới rõ | Một server chạy Order, Inventory, Payment nhưng mỗi module có trách nhiệm riêng |
| Microservice | Mỗi phần nghiệp vụ là dịch vụ triển khai riêng | Order và Payment chạy trên hai dịch vụ độc lập |
| Single Source of Truth/nguồn dữ liệu chính | Chỉ một module có quyền quyết định dữ liệu của một miền | Chỉ Inventory quyết định số tồn |
| Transaction/giao dịch cơ sở dữ liệu | Nhóm thao tác hoặc cùng thành công, hoặc cùng thất bại | Tạo reservation và trừ tồn phải cùng thành công |
| Atomic/nguyên tử | Không có trạng thái “làm được một nửa” | Không thể tạo giữ chỗ nhưng quên giảm tồn khả dụng |
| Invariant/điều kiện luôn phải đúng | Quy tắc hệ thống không được phép vi phạm | Tồn khả dụng không được âm |
| Eventual consistency/nhất quán sau một khoảng ngắn | Các phần chưa đồng bộ ngay lập tức nhưng cuối cùng phải khớp | Tạo shipment xong vài giây sau mới nhận tracking code |
| State/trạng thái | Giai đoạn hiện tại của một đối tượng | Payment đang PENDING hoặc PAID |
| State transition/chuyển trạng thái | Quy tắc cho phép đi từ trạng thái này sang trạng thái khác | Không thể từ CANCELLED quay lại FULFILLING |
| Audit log/nhật ký kiểm toán | Lịch sử ai đã làm gì, khi nào và lý do | Kế toán A điều chỉnh phí lúc 10:00 với lý do cụ thể |
| RBAC/phân quyền theo vai trò | Quyền thao tác dựa trên vai trò người dùng | Nhân viên kho không được hoàn tiền |
| PII/dữ liệu cá nhân | Thông tin có thể nhận biết khách hàng | Tên, số điện thoại, địa chỉ |
| Masking/che dữ liệu | Ẩn một phần dữ liệu nhạy cảm khi hiển thị hoặc ghi log | `090****000` thay cho số đầy đủ |

## 5. Thuật ngữ mô hình và tài liệu

| Thuật ngữ | Giải thích dễ hiểu |
|---|---|
| TOGAF | Phương pháp tổ chức việc thiết kế kiến trúc: hiểu vấn đề, thiết kế hiện tại/đích, tìm khoảng thiếu và lập lộ trình |
| ArchiMate | Ngôn ngữ vẽ tổng quan mối liên hệ giữa con người, quy trình, phần mềm và hạ tầng |
| BPMN | Ký pháp vẽ chi tiết thứ tự công việc, người thực hiện, nhánh điều kiện và sự kiện |
| Baseline/hiện trạng | Cách doanh nghiệp đang làm trước khi có hệ thống mới |
| Target/kiến trúc đích | Cách hệ thống mong muốn hoạt động sau khi cải tiến |
| Gap/khoảng thiếu | Những gì phải bổ sung để đi từ hiện trạng đến đích |
| Work Package/gói công việc | Một nhóm việc có thể giao và nghiệm thu |
| Plateau/mốc kiến trúc | Trạng thái ổn định sau một nhóm gói công việc |
| Stakeholder/bên liên quan | Người hoặc tổ chức quan tâm, sử dụng hay chịu tác động bởi hệ thống |
| Concern/mối quan tâm | Vấn đề mà một bên liên quan muốn kiến trúc trả lời |
| ADR | Phiếu ghi lại một quyết định kiến trúc, các lựa chọn và hậu quả |
| Traceability/truy vết | Khả năng nối một yêu cầu đến mô hình, thiết kế và bài kiểm thử |

## 6. Thuật ngữ kiểm thử và chất lượng

| Thuật ngữ | Giải thích dễ hiểu | Ví dụ |
|---|---|---|
| FR/yêu cầu chức năng | Hệ thống phải làm được việc gì | Phải tạo được đơn và hoàn tiền |
| NFR/yêu cầu phi chức năng | Hệ thống phải tốt đến mức nào | Tra cứu nhanh, an toàn, không ghi trùng |
| p95 | 95% yêu cầu có thời gian phản hồi không vượt quá giá trị này | p95 dưới 2 giây nghĩa là ít nhất 95/100 lần trả lời dưới 2 giây |
| Virtual user/người dùng giả lập | Luồng tự động mô phỏng người dùng để thử tải | 50 người cùng tra cứu đơn |
| Happy path/luồng thuận lợi | Tình huống bình thường, mọi bước đều thành công | QR thành công và giao hàng thành công |
| Exception/ngoại lệ | Tình huống lỗi hoặc khác bình thường | Hết hàng, webhook lặp, giao thất bại |
| Risk score/điểm rủi ro | Xác suất xảy ra nhân mức ảnh hưởng | Xác suất 4 × ảnh hưởng 5 = 20 |
| Residual risk/rủi ro còn lại | Rủi ro còn tồn tại sau khi đã áp dụng biện pháp | Vẫn có thể mất kết nối đối tác dù đã retry |
| HTTP 403 | Người dùng đã đăng nhập nhưng không có quyền làm việc đó | CSKH cố điều chỉnh tiền và bị từ chối |
| HTTP 409 | Yêu cầu xung đột với trạng thái/dữ liệu hiện tại | Hủy đơn đã giao hoặc mua vượt tồn |

## 7. Ví dụ xuyên suốt một đơn hàng

Giả sử kho có 10 áo size M, giá 150.000 đồng/áo. Khách đặt 2 áo bằng QR:

1. Order module tạo `ord_001` với tổng tiền 300.000 đồng.
2. Inventory tạo reservation 2 áo; tồn khả dụng từ 10 còn 8.
3. Payment tạo payment intent và mã QR có reference `ord_001`.
4. PSP gửi webhook `pay_123 = PAID`. Inbox dùng `pay_123` để chống ghi trùng.
5. Kho đóng gói. Inventory ghi StockEntry xuất 2 áo và chuyển reservation thành `COMMITTED`.
6. Shipping ghi OutboxEvent yêu cầu tạo vận đơn. Worker gửi cho carrier và nhận tracking code.
7. Sau khi giao, kế toán so Payment Ledger 300.000 đồng với statement PSP 300.000 đồng và tiền ngân hàng 300.000 đồng. Ba nguồn khớp nên giao dịch được đóng.

Nếu webhook `pay_123` bị gửi lại 9 lần, hệ thống vẫn chỉ có một bút toán nhận tiền. Đây là ý nghĩa của “xử lý lặp an toàn”.

