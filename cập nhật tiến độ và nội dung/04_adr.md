# Architecture Decision Records (ADR)

Mỗi ADR ghi một quyết định kiến trúc của hệ thống Order-to-Cash cho SME thương mại điện tử, biến thể B về COD và hàng hoàn. Đề bài yêu cầu ít nhất hai ADR, mỗi ADR so sánh ít nhất hai phương án theo tiêu chí, lý do chọn và đánh đổi. Ở đây, **Title** là tên phương án được chọn, **Reason** giải thích vì sao phương án đó phù hợp hơn theo các tiêu chí đã đặt ra, **Trade-offs** nêu phần phải đánh đổi. **Consequences** ghi những việc kéo theo khi áp dụng quyết định. Trạng thái **Đã chấp nhận trong thiết kế** ghi nhận lựa chọn của bài tập lớn. Kết quả chạy thử được ghi ở tài liệu kiểm chứng. [Đề bài BTL](../De_BTL_Kien_truc_HTTT_2026.pdf) · [Mẫu ADR của Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) · [Mẫu MADR](https://adr.github.io/madr/)

## ADR-01: Chọn cách tổ chức và triển khai ứng dụng

**Title:** Dùng modular monolith cho các phân hệ Order-to-Cash.

**Status:** Đã chấp nhận trong thiết kế.

**Context:** Shop có một website, một kho trung tâm và một ĐVVC trong phạm vi mô hình. Mức 100–300 đơn/ngày là giả định thiết kế, còn tải đồng thời tại giờ cao điểm cần đo ở bước kiểm chứng. Nhóm cần triển khai được các luồng đặt đơn, giữ hàng, giao hàng, xử lý hàng hoàn và đối soát với ít thành phần vận hành. [Phạm vi và nguyên tắc AP-05](01_togaf_chuan_hoa.md)

### Decision Drivers

1. **Nhất quán dữ liệu:** Có thể giữ hàng và cập nhật đơn trong cùng một giao dịch khi nghiệp vụ yêu cầu.
2. **Triển khai và vận hành:** Số gói triển khai, dịch vụ cần theo dõi và mức công sức phục hồi khi có lỗi.
3. **Thay đổi và mở rộng:** Khả năng phát hành, tăng tài nguyên và giới hạn phạm vi ảnh hưởng theo từng phân hệ.

### Considered Options

| Phương án | Nhất quán dữ liệu | Triển khai và vận hành | Thay đổi, mở rộng và đánh đổi |
|---|---|---|---|
| **A. Modular monolith** | Các phân hệ có thể phối hợp qua giao diện nội bộ và dùng một giao dịch trên cùng cơ sở dữ liệu. | Một gói ứng dụng dùng chung, có API và tiến trình xử lý nền. Nhóm quản lý phiên bản và theo dõi luồng xử lý tập trung. | Dễ thay đổi một luồng đi qua nhiều phân hệ. Các phân hệ cùng phát hành, còn phần API tăng tài nguyên theo cả ứng dụng. Lỗi trong một tiến trình API có thể ảnh hưởng nhiều chức năng. |
| **B. Microservices theo miền** | Mỗi dịch vụ quản lý dữ liệu của mình. Các cập nhật đi qua nhiều dịch vụ cần quy tắc phối hợp, xử lý thất bại từng phần và thao tác bù khi cần. | Cần triển khai và quan sát nhiều dịch vụ, xử lý lỗi gọi mạng và quản lý tương thích giao diện giữa các dịch vụ. | Có thể phát hành và tăng tài nguyên độc lập cho phần giao vận hoặc đối soát. Đổi lại, cần theo dõi và kiểm thử nhiều trạng thái trung gian hơn. |

Tính độc lập khi triển khai và chi phí phối hợp dữ liệu phân tán được mô tả trong tài liệu kiến trúc của Microsoft. Việc áp dụng vào các phân hệ trên là phân tích của dự án. [Microsoft Azure Architecture Center — Microservices](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices)

### Decision

**Chọn phương án A.**

Tổ chức `Order`, `Inventory`, `Payment`, `Fulfillment/Shipping`, `Return` và `Reconciliation/Reporting` theo các phân hệ trong tài liệu ArchiMate. `Carrier Adapter` và `QR Payment Adapter` đảm nhiệm tích hợp đối tác. Mỗi phân hệ chịu trách nhiệm cập nhật dữ liệu của mình qua giao diện nội bộ. API và worker có thể chạy ở hai tiến trình cùng phiên bản của gói ứng dụng. [Mô hình Application Component](02_archimate_chuan_hoa.md)

### Reason

A ưu tiên giao dịch cục bộ cho các thay đổi liên quan đến đơn và tồn, đồng thời giảm số thành phần nhóm phải triển khai ở giai đoạn đầu. B phù hợp khi đã có nhu cầu phát hành độc lập hoặc tải của một miền khác biệt rõ rệt. Với quy mô giả định hiện tại, lợi ích đó chưa đủ để ưu tiên thêm cơ chế điều phối và phục hồi giữa các dịch vụ.

### Trade-offs

Nhóm chấp nhận lịch phát hành chung và phạm vi ảnh hưởng rộng hơn khi tiến trình API gặp lỗi. Đổi lại, nhóm có thể kiểm thử luồng chính và triển khai thay đổi qua nhiều phân hệ trong cùng một phiên bản.

### Consequences

Giữ ranh giới phân hệ bằng giao diện nội bộ và kiểm tra phụ thuộc trong mã nguồn. Đo tải và thời gian xử lý theo phân hệ trước khi xem xét tách dịch vụ. Truy vết **AP-05, NFR-01, NFR-07, WP-01–WP-02**.

## ADR-02: Chọn cách giữ hàng và lưu lịch sử tồn kho

**Title:** Dùng giao dịch PostgreSQL để giữ hàng và ghi `StockEntry`.

**Status:** Đã chấp nhận trong thiết kế.

**Context:** Hai khách có thể cùng đặt món cuối cùng. Một kiện hàng hoàn cũng có thể bị quét lại nhiều lần. Kho cần vừa giữ đúng số lượng, vừa giải thích được vì sao số tồn thay đổi sau mỗi lần giữ, xuất hoặc nhận hàng hoàn. [Yêu cầu và mô hình dữ liệu](01_togaf_chuan_hoa.md) · [Giải thích `Reservation` và `StockEntry`](02_archimate_chuan_hoa.md)

### Decision Drivers

1. **Đúng số lượng khi xử lý đồng thời:** Hai đơn không cùng giữ được một mặt hàng cuối cùng.
2. **Truy vết và xử lý lặp:** Tra lại được lý do biến động. Cùng một thao tác nhận hoàn chỉ tạo một thay đổi có hiệu lực.
3. **Chi phí vận hành:** Cân nhắc công sức quản trị cơ sở dữ liệu, xử lý tranh chấp và khôi phục.

### Considered Options

| Phương án | Xử lý đồng thời | Truy vết và xử lý lặp | Vận hành và đánh đổi |
|---|---|---|---|
| **A. PostgreSQL, chỉ lưu số tồn và giữ chỗ hiện tại** | Có thể dùng khóa dòng hoặc cập nhật có điều kiện để tránh giữ vượt tồn. | Xem được số dư và giữ chỗ hiện tại. Muốn lần lại từng lần tăng giảm phải thiết kế thêm lịch sử và khóa chống lặp cho từng thao tác. | Ít bảng và ít lượt ghi hơn C. Khi số liệu lệch, việc tìm nguyên nhân phụ thuộc vào chứng từ và nhật ký khác. |
| **B. SQLite với `Reservation` và `StockEntry`** | Có giao dịch. Ở chế độ WAL, việc đọc và ghi có thể diễn ra đồng thời, còn các giao dịch ghi lần lượt dùng quyền ghi. | Có thể lưu cùng nhóm bản ghi nghiệp vụ nếu triển khai đúng ràng buộc và quy tắc chống lặp. | Ít việc cài đặt, phù hợp demo cục bộ. Khi đơn hàng, kho và worker cùng ghi, các giao dịch có thể phải chờ hoặc thử lại. [SQLite — WAL và xử lý đồng thời](https://www.sqlite.org/wal.html#concurrency) |
| **C. PostgreSQL với `Reservation` và `StockEntry`** | Khóa các dòng số dư cần thay đổi hoặc cập nhật có điều kiện. Nếu một mặt hàng trong đơn thiếu tồn, hoàn tác thao tác giữ cho cả đơn. | Lưu lý do, số lượng và tham chiếu của từng biến động. Dùng khóa nghiệp vụ phù hợp để phát hiện thao tác lặp. | Phải vận hành dịch vụ PostgreSQL và thiết kế chỉ mục, giao dịch, sao lưu. Các yêu cầu cùng sửa một dòng tồn vẫn có thể chờ nhau. [PostgreSQL — Khóa](https://www.postgresql.org/docs/18/explicit-locking.html) · [Giao dịch đồng thời](https://www.postgresql.org/docs/18/transaction-iso.html) |

### Decision

**Chọn phương án C cho kiến trúc đích.**

`Inventory` cập nhật số dư, tạo hoặc cập nhật `Reservation` và thêm `StockEntry` trong một giao dịch. Trong phạm vi một kho, có thể dùng khóa duy nhất `(order_id, sku)` khi mỗi mặt hàng có một bản ghi giữ tổng số lượng theo đơn. Riêng thao tác kho như nhận hàng hoàn cần khóa chống lặp theo mã thao tác và dòng hàng tương ứng. Khi hàng quay về, ghi vào khu chờ kiểm tra chất lượng. Chỉ ghi `RESTOCK` và tăng tồn có thể bán khi hàng đạt kiểm tra. Khi sửa sai, bổ sung dòng điều chỉnh có lý do và tham chiếu đến dòng gốc. [PostgreSQL — Ràng buộc dữ liệu](https://www.postgresql.org/docs/18/ddl-constraints.html)

### Reason

A có thể ngăn bán vượt tồn, nhưng thiếu lịch sử từng lần biến động mà tình huống hàng hoàn yêu cầu. B đáp ứng nhu cầu trình diễn và có chi phí cài đặt thấp, song cơ chế xử lý ghi khác nền vận hành dự kiến. C đáp ứng đồng thời mục tiêu giữ hàng chính xác và kiểm tra nguồn gốc chênh lệch tồn.

### Trade-offs

Mỗi nghiệp vụ kho ghi thêm lịch sử và cần quản lý vòng đời dữ liệu. Tồn của mặt hàng bán chạy vẫn có thể gây tranh chấp khóa. Đổi lại, nhóm có dữ liệu để lần lại xuất kho, nhận hoàn, phân loại và điều chỉnh tồn.

### Consequences

Số lượng hàng vật lý trong kho bằng tổng hàng có thể bán, đang giữ, đã lấy chờ bàn giao, chờ kiểm và cách ly. Các số lượng này phải không âm. Mỗi đơn vị hàng chỉ thuộc một nhóm tại một thời điểm. Khi bàn giao, ghi xuất tồn vật lý và theo dõi kiện qua `Shipment`. Kiểm chứng trên PostgreSQL các tình huống nhiều khách tranh nhau lượng tồn còn ít, kho nhận hàng hoàn lặp và thông báo thanh toán QR đến sát lúc hết hạn giữ hàng. Truy vết **FR-02, FR-07, FR-10, REQ-COD-03, NFR-03, NFR-06**, tình huống **TC-03, TC-06, TC-10**. [Kế hoạch kiểm chứng](05_kiem_chung.md)

## ADR-03: Chọn cách gửi và nhận thông điệp với đối tác

**Title:** Dùng `OutboxEvent`, `InboxEvent` và worker để xử lý tích hợp.

**Status:** Đã chấp nhận trong thiết kế.

**Context:** Shop gửi yêu cầu tạo vận đơn và nhận thông báo giao hàng hoặc thanh toán QR. Mất kết nối khi chờ phản hồi có thể xảy ra sau khi đối tác đã xử lý yêu cầu. Một thông báo cũng có thể đến lặp hoặc sai thứ tự. Thiết kế cần phục hồi được các tình huống này. [FR-04 đến FR-06 và EXT-01](01_togaf_chuan_hoa.md)

### Decision Drivers

1. **Khôi phục sau lỗi:** Biết yêu cầu nào đang chờ, đã gửi hoặc cần xác minh.
2. **Chống xử lý trùng và sai thứ tự:** Tránh tạo vận đơn hoặc bút toán lặp, bảo vệ trạng thái mới hơn.
3. **Chi phí vận hành và độ trễ:** Số hạ tầng phải vận hành và thời gian chờ xử lý thông điệp.

### Considered Options

| Phương án | Khôi phục sau lỗi | Chống trùng và sai thứ tự | Vận hành, độ trễ và đánh đổi |
|---|---|---|---|
| **A. Gọi HTTP đồng bộ trực tiếp** | Khi mọi bên phản hồi bình thường, shop có kết quả ngay. Khi mất kết nối sau lúc đối tác xử lý, cần tra cứu trước khi gọi lại. | Vẫn cần mã yêu cầu ổn định và quy tắc chuyển trạng thái. Nếu chỉ thử lại trong lúc chờ HTTP thì yêu cầu còn dở có thể mất dấu khi tiến trình dừng. | Ít thành phần, phù hợp các thao tác cần phản hồi ngay như yêu cầu mã QR. Độ trễ của đối tác đi vào luồng đang chờ. |
| **B. Transactional outbox, inbox và worker đọc từ PostgreSQL** | Ghi yêu cầu cần gửi trong cùng giao dịch với thay đổi nghiệp vụ. Worker đọc việc đến hạn, xử lý lại và lưu số lần thử. | Inbox lưu khóa sự kiện từ đối tác. Khi xử lý, ghi tác dụng nghiệp vụ và trạng thái đã xử lý trong cùng giao dịch. Kiểm tra điều kiện chuyển trạng thái trước khi cập nhật. | Dùng cơ sở dữ liệu hiện có. Đổi lại, có độ trễ theo chu kỳ quét và cần theo dõi hàng đợi trong DB. [AWS Prescriptive Guidance — Transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) |
| **C. Transactional outbox và broker RabbitMQ, giữ inbox hoặc cơ chế chống trùng tương đương** | Worker chuyển sự kiện từ outbox sang broker. Broker có xác nhận khi nhận thông điệp và xác nhận từ trình xử lý. Outbox vẫn bảo vệ khoảng giữa ghi DB và phát thông điệp. | Trình nhận vẫn phải kiểm tra trùng và thứ tự vì thông điệp có thể được giao lại. Các xác nhận của broker có phạm vi riêng với việc ghi dữ liệu nghiệp vụ. | Có lợi khi nhiều bên cần nhận cùng một sự kiện hoặc cần tách tải xử lý. Đổi lại, cần thêm broker, cấu hình hàng đợi, theo dõi và phục hồi. [RabbitMQ — Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms) |

### Decision

**Chọn phương án B.**

Áp dụng cho tác vụ cần gửi bền vững, như tạo vận đơn, và tiếp nhận kết quả QR hoặc giao vận. Worker gửi lại với khoảng chờ tăng dần. Nếu đối tác hỗ trợ khóa chống tạo trùng, dùng cùng một mã qua các lần gửi. Nếu phản hồi chưa rõ và đối tác thiếu cơ chế đó, tra cứu theo mã tham chiếu trước khi gửi lại hoặc đưa vào danh sách cần kiểm tra. Thông báo đến được xác thực theo quy cách của đối tác rồi lưu vào `InboxEvent` với khóa theo nguồn và mã sự kiện nếu có. Nếu đối tác thiếu mã sự kiện, adapter xác định khóa ổn định từ dữ liệu đã xác thực theo hợp đồng tích hợp. Bước lấy mã QR để hiển thị có thể gọi trực tiếp theo luồng BPMN-01. [BPMN-01](03_bpmn.md)

### Reason

B giữ được dấu vết của yêu cầu giao vận qua lúc tiến trình dừng và phù hợp với quy mô, số đối tác giả định. A có lợi khi người dùng đang chờ mã QR, nhưng riêng việc thử lại trong yêu cầu HTTP không đáp ứng nhu cầu phục hồi tác vụ tạo vận đơn. C đáng cân nhắc khi có nhu cầu phân phối cho nhiều bên nhận hoặc số đo cho thấy cơ chế quét DB trở thành điểm nghẽn.

### Trade-offs

Hệ thống chấp nhận khoảng chờ trước khi xử lý đồng bộ xong với đối tác. Worker có thể gửi lại một thông điệp, vì vậy phải kiểm soát tác dụng nghiệp vụ ở cả bước gửi và bước nhận tùy khả năng của từng đối tác.

### Consequences

Theo dõi thời gian chờ, số lần thử và các thông điệp phải xử lý thủ công. Kiểm chứng tình huống đối tác lỗi, phản hồi muộn và gửi trùng. Truy vết **FR-04, FR-05, FR-06, EXT-01, NFR-03, NFR-04, NFR-05**, tình huống **TC-04, TC-09**. [Kế hoạch kiểm chứng](05_kiem_chung.md)

## ADR-04: Chọn cách tổ chức dữ liệu đối soát COD

**Title:** Lưu các mốc tiền để đối soát COD ba chiều và quản lý hóa đơn vận chuyển riêng.

**Status:** Đã chấp nhận trong thiết kế.

**Context:** Theo chính sách của đề tài, ĐVVC chuyển đủ tiền COD đã thu theo tháng. Shop kiểm tra và thanh toán hóa đơn vận chuyển riêng. Cả hai phương án dưới đây đều áp dụng chính sách đó. Câu hỏi cần quyết định là hệ thống nên quản lý đối chiếu ở mức nào để kế toán xác định được tiền thiếu ở khâu thu hay khâu chuyển. [Yêu cầu NFR-08 và REQ-COD-02](01_togaf_chuan_hoa.md) · [Quy trình BPMN-03](03_bpmn.md)

### Decision Drivers

1. **Phân biệt hai loại chênh lệch:** Tách số ĐVVC thu thiếu từ khách và số ĐVVC chuyển thiếu về shop.
2. **Truy vết và kiểm soát:** Tìm được chứng từ, người xử lý và lý do phê duyệt khi có lệch.
3. **Chi phí thực hiện:** Cân nhắc công sức xây dựng, công sức kế toán hằng tháng và xử lý khi dữ liệu đối tác sai hoặc thiếu.

### Considered Options

| Phương án | Phát hiện và phân loại chênh lệch | Truy vết và kiểm soát | Chi phí và đánh đổi |
|---|---|---|---|
| **A. Đối soát ba chiều bằng bảng tính có mẫu và phê duyệt theo kỳ** | Kế toán ghép số dự kiến thu, bảng kê thu hộ và sao kê. Hóa đơn có bảng riêng. Có thể phát hiện đủ hai loại lệch nếu dùng đúng mẫu và ghép đúng tham chiếu. | Cần quản lý phiên bản file, khóa kỳ đã duyệt và lưu bằng chứng điều chỉnh. Việc nối dòng chênh lệch về đơn và vận đơn phụ thuộc vào quy trình thao tác của kế toán. | Dễ bắt đầu, ít phải lập trình. Công sức kiểm tra và rủi ro ghép sai hoặc dùng nhầm phiên bản tăng khi có nhiều giao thất bại, hoàn hàng hoặc lượt chuyển bù. |
| **B. Đối soát ba chiều trong hệ thống từ các mốc `PaymentEntry`** | Hệ thống so số theo đơn với số thu trên bảng kê rồi so số đã thu của kỳ với số thực nhận ở ngân hàng. Khoản chưa ghép được được chuyển để kế toán kiểm tra. | Lưu bảng kê, tham chiếu giao dịch và `ReconciliationCase`. Quản lý hóa đơn bằng `CarrierInvoice` với luồng phê duyệt riêng. | Tốn công nhập dữ liệu, lập quy tắc ghép và xử lý ngoại lệ. Đổi lại, dễ truy lại một chênh lệch hoặc kiểm tra số liệu sau khi ĐVVC chuyển bù. |

### Decision

**Chọn phương án B.**

Với COD, `PaymentEntry` ghi từng mốc dự kiến thu (`expected`), ĐVVC báo đã thu (`collected`) và khoản thực chuyển được xác nhận (`remitted`). Đối chiếu theo hai bước. So số phải thu và số ĐVVC báo thu theo đơn hoặc vận đơn. Sau đó so tổng số phải chuyển theo bảng kê với giao dịch ngân hàng gắn với đúng kỳ. Đơn hoàn được xác nhận chưa thu tiền được loại khỏi số phải chuyển. Nếu chưa đủ chứng từ để xác minh, tiếp tục theo dõi chênh lệch trong `ReconciliationCase`. Kiểm tra `CarrierInvoice` theo mã vận đơn và biểu phí, rồi ghi nhận một giao dịch shop trả phí riêng.

Với QR, yêu cầu thanh toán bằng tổng tiền đơn, gồm phí vận chuyển thu khách. Phí xử lý QR được giả định bằng 0 và vận đơn QR có số COD bằng 0. Shop kiểm tra khoản đã xác nhận thanh toán với bảng kê của Ngân hàng/Đơn vị cung cấp thanh toán QR và tiền thực nhận. Hoàn tiền và điều chỉnh có bản ghi riêng. [Mô hình dữ liệu thanh toán và đối soát](02_archimate_chuan_hoa.md) · [BPMN-03](03_bpmn.md)

### Reason

B giúp kế toán xử lý chênh lệch theo từng hồ sơ, giữ liên kết giữa số tiền và chứng từ. A khả thi với ít đơn hoặc khi dùng để kiểm tra độc lập một kỳ mẫu. Với biến thể B có nhiều giao thất bại và hàng hoàn, quy tắc ghép và lịch sử xử lý trong hệ thống giảm số bước phải dò lại giữa nhiều file.

### Trade-offs

Nhóm chấp nhận đầu tư nhập bảng kê, xác định cách đánh dấu kỳ, lập quy tắc ghép và xử lý trường hợp thiếu mã tham chiếu. Kế toán vẫn cần xác minh các khoản khó ghép. Lợi ích là có thể kiểm lại chính xác mỗi khoản lệch phát sinh ở bước nào.

### Consequences

Ví dụ, bảng kê xác nhận đã thu 300.000 đồng, ngân hàng mới ghi có 280.000 đồng. Chênh lệch chuyển là 20.000 đồng. Nếu có hóa đơn vận chuyển 20.000 đồng cùng kỳ, hóa đơn được xử lý riêng và khoản thiếu COD vẫn cần theo dõi. Truy vết **FR-08 đến FR-11, REQ-COD-02, EXT-03, NFR-06, NFR-08**, tình huống **TC-05**. [Kịch bản demo COD](06_prototype.md) · [Kế hoạch kiểm chứng](05_kiem_chung.md)

## Công nghệ dùng cho demo và kiến trúc đích

Mốc đối chiếu tài liệu phát hành là **21/11/2026**. Các phiên bản dưới đây là đề xuất để triển khai và tái lập môi trường kiểm chứng. Phiên bản thực tế cần chốt cùng bộ phụ thuộc khi dựng prototype. [Phạm vi prototype](06_prototype.md)

| Thành phần | Lựa chọn và căn cứ |
|---|---|
| **API và môi trường chạy** | Đề xuất Python **3.13** theo môi trường hiện có của dự án và FastAPI **0.165.0** cho prototype. FastAPI tạo mô tả OpenAPI từ API, thuận tiện cho demo luồng đặt hàng, callback và giao vận. Python 3.13 đang ở giai đoạn cập nhật bảo mật. [Vòng đời Python](https://devguide.python.org/versions/) · [Tính năng FastAPI](https://fastapi.tiangolo.com/features/) · [Ghi chú phát hành FastAPI](https://fastapi.tiangolo.com/release-notes/#01650-2026-11-18) |
| **Cơ sở dữ liệu đích** | Đề xuất PostgreSQL **18**, dùng bản cập nhật 18.x còn được hỗ trợ. Tại mốc đối chiếu, bản cập nhật là **18.7**, nhánh 18 được hỗ trợ đến tháng 11/2030. PostgreSQL 19 cũng đã phát hành. Các cơ chế khóa dòng, giao dịch và ràng buộc cần cho ADR-02 đã có trong nhánh 18. [Chính sách phiên bản PostgreSQL](https://www.postgresql.org/support/versioning/) · [Tài liệu PostgreSQL 18](https://www.postgresql.org/docs/18/explicit-locking.html) |
| **Cơ sở dữ liệu demo** | SQLite cục bộ giúp chạy kịch bản minh họa gọn theo thiết kế prototype. Các thử nghiệm tranh chấp giữ hàng, khóa dòng và nhiều worker cần chạy lại trên PostgreSQL. Phiên bản SQLite cần ghi nhận theo thư viện thực tế đi kèm môi trường chạy. [SQLite — WAL](https://www.sqlite.org/wal.html) |
| **Tích hợp và xử lý nền** | Dùng Ngân hàng/Đơn vị cung cấp thanh toán QR và ĐVVC giả lập cho demo. Worker đọc `OutboxEvent` từ cơ sở dữ liệu theo ADR-03. RabbitMQ là phương án đã đánh giá khi có nhu cầu phân phối sự kiện rộng hơn. [Kiến trúc ứng dụng](02_archimate_chuan_hoa.md) · [Prototype](06_prototype.md) |
| **Giao diện và hạ tầng** | Prototype đề xuất giao diện HTML/Bootstrap hoặc React tối giản. Kiến trúc đích mô tả máy ảo Linux, reverse proxy cho HTTPS và lưu chứng từ tập trung. Phiên bản giao diện, phần mềm proxy và nhà cung cấp hạ tầng sẽ được chốt theo môi trường triển khai. [Kiến trúc công nghệ](02_archimate_chuan_hoa.md) · [Phạm vi prototype](06_prototype.md) |

