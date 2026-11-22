# Architecture Decision Records (ADR)

Mỗi ADR ghi một quyết định kiến trúc của hệ thống Order-to-Cash cho SME thương mại điện tử, biến thể B về COD và hàng hoàn. Đề bài yêu cầu ít nhất hai ADR, mỗi ADR so sánh ít nhất hai phương án theo tiêu chí, lý do chọn và đánh đổi. Ở đây, **Title** là tên phương án được chọn, **Reason** giải thích vì sao phương án đó phù hợp hơn theo các tiêu chí đã đặt ra, **Trade-offs** nêu phần phải đánh đổi. **Consequences** ghi những việc kéo theo khi áp dụng quyết định. Trạng thái **Đã chấp nhận trong thiết kế** ghi nhận lựa chọn của bài tập lớn. Kết quả chạy thử được ghi ở tài liệu kiểm chứng. [Đề bài BTL](../De_BTL_Kien_truc_HTTT_2026.pdf) · [Mẫu ADR của Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) · [Mẫu MADR](https://adr.github.io/madr/)

## ADR-01: Chọn cách tổ chức và triển khai ứng dụng

**Title:** Dùng modular monolith cho các phân hệ Order-to-Cash.

**Status:** Đã chấp nhận trong thiết kế. Rà soát kỹ thuật ngày 22/11/2026.

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

A ưu tiên tính nhất quán khi giữ hàng và giảm số thành phần nhóm phải vận hành. Phạm vi một kho và khối lượng dự kiến 100–300 đơn/ngày là căn cứ để bắt đầu với kiến trúc gọn. Số đơn theo ngày chưa phản ánh lượng truy cập đồng thời, webhook hoặc độ bận khi đối soát cuối kỳ. B phù hợp hơn nếu các miền có nhu cầu triển khai hoặc tăng tài nguyên độc lập đã được chứng minh.

### Trade-offs

Nhóm chấp nhận lịch phát hành chung và phạm vi ảnh hưởng rộng hơn khi tiến trình API gặp lỗi. Đổi lại, nhóm có thể kiểm thử luồng chính và triển khai thay đổi qua nhiều phân hệ trong cùng một phiên bản.

### Consequences

Mỗi phân hệ sở hữu bảng nghiệp vụ của mình. Có thể tách các bảng theo schema PostgreSQL để dễ quản lý, đồng thời kiểm tra phụ thuộc trong CI và dùng giao diện nội bộ khi cần dữ liệu từ phân hệ khác. Báo cáo liên miền có thể đọc từ bản chiếu dữ liệu dành riêng cho báo cáo. Phạm vi giao dịch cục bộ chỉ bao gồm thay đổi trên cùng cơ sở dữ liệu qua cùng giao dịch. Chốt giao dịch trước khi chờ HTTP từ đối tác. Khi cần bảo đảm yêu cầu có thể gửi lại, lưu `OutboxEvent` trong giao dịch theo [ADR-03](#adr-03-chọn-cách-gửi-và-nhận-thông-điệp-với-đối-tác).

Đánh giá lại khi phép thử NFR-01 với 50 người dùng ảo vượt mức thời gian hoặc tỷ lệ lỗi đã đặt và số đo chỉ ra một phân hệ cụ thể, hoặc khi chờ phát hành chung thường xuyên cản trở một phân hệ. Truy vết **AP-05, NFR-01, NFR-07, WP-01–WP-02**. [Yêu cầu và roadmap](01_togaf_chuan_hoa.md)

## ADR-02: Chọn cách giữ hàng và lưu lịch sử tồn kho

**Title:** Dùng giao dịch PostgreSQL để giữ hàng và ghi `StockEntry`.

**Status:** Đã chấp nhận trong thiết kế. Rà soát kỹ thuật ngày 22/11/2026.

**Context:** Hai khách có thể cùng đặt món cuối cùng. Một kiện hàng hoàn cũng có thể bị quét lại nhiều lần. Kho cần vừa giữ đúng số lượng, vừa giải thích được vì sao số tồn thay đổi sau mỗi lần giữ, xuất hoặc nhận hàng hoàn. [Yêu cầu và mô hình dữ liệu](01_togaf_chuan_hoa.md) · [Giải thích `Reservation` và `StockEntry`](02_archimate_chuan_hoa.md)

### Decision Drivers

1. **Đúng số lượng khi xử lý đồng thời:** Hai đơn không cùng giữ được một mặt hàng cuối cùng.
2. **Truy vết và xử lý lặp:** Tra lại được lý do biến động. Cùng một thao tác nhận hoàn chỉ tạo một thay đổi có hiệu lực.
3. **Chi phí vận hành:** Cân nhắc công sức quản trị cơ sở dữ liệu, xử lý tranh chấp và khôi phục.

### Considered Options

| Phương án | Xử lý đồng thời | Truy vết và xử lý lặp | Vận hành và đánh đổi |
|---|---|---|---|
| **A. PostgreSQL, chỉ lưu số tồn và giữ chỗ hiện tại** | Có thể dùng khóa dòng hoặc cập nhật có điều kiện để tránh giữ vượt tồn. | Xem được số dư và giữ chỗ hiện tại. Muốn lần lại từng lần tăng giảm phải thiết kế thêm lịch sử và khóa chống lặp cho từng thao tác. | Ít bảng và ít lượt ghi hơn B. Khi số liệu lệch, việc tìm nguyên nhân phụ thuộc vào chứng từ và nhật ký khác. |
| **B. PostgreSQL, lưu số tồn, giữ chỗ và sổ biến động** | Dùng cùng cơ chế của A. Giữ toàn bộ mặt hàng trong một giao dịch. Nếu một mặt hàng thiếu tồn, hoàn tác thao tác giữ cho cả đơn. | Ghi lý do, số lượng và tham chiếu của từng biến động. Dùng khóa nghiệp vụ để phát hiện thao tác lặp. | Mỗi biến động có thêm một lượt ghi lịch sử. Các giao dịch cùng sửa một dòng tồn vẫn có thể phải chờ. [PostgreSQL về khóa và giao dịch đồng thời](https://www.postgresql.org/docs/18/explicit-locking.html) |

### Decision

**Chọn phương án B cho kiến trúc đích.**

- **Giữ hàng trong một giao dịch.** `Inventory` cập nhật số dư, tạo hoặc cập nhật `Reservation` và thêm `StockEntry` trong cùng giao dịch. Tại mức mặc định `READ COMMITTED`, dùng một lệnh cập nhật có điều kiện từ số thực sự bán được, chẳng hạn `WHERE available >= :qty` nếu số khả dụng được lưu trên dòng đó. Đồng thời chuyển số lượng từ khả dụng sang giữ chỗ. Nếu giao dịch khác vừa cập nhật cùng dòng, PostgreSQL chờ rồi kiểm tra lại điều kiện trên bản ghi mới khi giao dịch trước đã chốt. Nếu không cập nhật được dòng tồn đã xác định, hoàn tác cả đơn. Nếu cần đọc trước để tính, dùng `SELECT ... FOR UPDATE` trong cùng giao dịch. [PostgreSQL về mức cô lập](https://www.postgresql.org/docs/18/transaction-iso.html)
- **Đơn có nhiều SKU.** Khóa hoặc cập nhật theo cùng một thứ tự SKU ở mọi luồng có thể chạm các dòng đó. Nếu PostgreSQL hủy giao dịch do khóa chéo (`40P01`) hoặc do lỗi tuần tự hóa (`40001`), thử lại toàn bộ giao dịch với giới hạn. Dùng `NOT NULL` và `CHECK` để bảo vệ số lượng không âm và kiểm tra tổng các nhóm nếu chúng nằm trên cùng dòng số dư. [PostgreSQL về khóa và deadlock](https://www.postgresql.org/docs/18/explicit-locking.html) · [Ràng buộc dữ liệu](https://www.postgresql.org/docs/18/ddl-constraints.html) · [Thử lại giao dịch](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html)
- **Lịch sử và chống ghi trùng.** Với một kho, `UNIQUE (order_id, sku)` định danh một bản ghi giữ tổng số lượng của mặt hàng trong đơn. Khi lượng giữ thay đổi hợp lệ, cập nhật bản ghi đó và thêm dòng lịch sử. Với hàng hoàn, đặt khóa duy nhất theo mã thao tác ổn định, dòng hàng và loại biến động nếu một thao tác ghi nhiều loại. Dùng khóa đó để trả lại kết quả của thao tác đã ghi. Chỉ chuyển từ chờ kiểm sang khả dụng khi kiểm hàng đạt và ghi `RESTOCK`. Tài khoản chạy ứng dụng tách khỏi tài khoản sở hữu bảng. Với bảng này, tài khoản ứng dụng chỉ đọc và thêm dòng `StockEntry`. Sửa sai bằng dòng điều chỉnh có lý do và tham chiếu. [PostgreSQL về quyền truy cập](https://www.postgresql.org/docs/18/ddl-priv.html)
- **QR sát giờ hết hạn.** Tác vụ hết hạn và xử lý xác nhận QR cùng kiểm tra trạng thái đơn và giữ chỗ trong giao dịch. Chỉ một bên được chuyển từ trạng thái đang chờ sang kết quả tương ứng. Nếu xác nhận thắng, giữ hàng cho khâu giao. Nếu hết hạn thắng, giải phóng tồn. Nếu tiền đến sau khi hủy, lưu dấu vết thanh toán và chuyển xác minh hoặc hoàn theo chính sách. [Kịch bản TC-10](05_kiem_chung.md)

### Reason

Cả A và B có thể kiểm soát tranh chấp tồn trên PostgreSQL. Tiêu chí quyết định là vừa giữ đúng số lượng, vừa lần được sự thay đổi qua từng mốc xuất hàng và nhận hoàn. B đáp ứng cả hai. So sánh SQLite và PostgreSQL nằm ở bảng công nghệ bên dưới vì đó là lựa chọn môi trường, còn bảng này so sánh cách lưu tồn kho.

### Trade-offs

Mỗi nghiệp vụ kho ghi thêm lịch sử và cần quản lý vòng đời dữ liệu. Tồn của mặt hàng bán chạy vẫn có thể gây tranh chấp khóa. Đổi lại, nhóm có dữ liệu để lần lại xuất kho, nhận hoàn, phân loại và điều chỉnh tồn.

### Consequences

Số lượng hàng vật lý trong kho bằng tổng hàng có thể bán, đang giữ, đã lấy chờ bàn giao, chờ kiểm và cách ly. Mỗi đơn vị chỉ thuộc một nhóm tại một thời điểm. Khi bàn giao, ghi xuất tồn vật lý và theo dõi kiện qua `Shipment`. Có thể kiểm tra số dư từng nhóm bằng số đầu kỳ cộng tổng biến động có dấu đến cùng mốc, tránh cộng trùng các lần chuyển giữa nhóm. Kiểm chứng giữ hàng đồng thời, nhận hoàn lặp và QR sát hạn trên PostgreSQL. Truy vết **FR-02, FR-07, FR-10, REQ-COD-03, NFR-03, NFR-06**, tình huống **TC-03, TC-06, TC-10**. [Kế hoạch kiểm chứng](05_kiem_chung.md)

## ADR-03: Chọn cách gửi và nhận thông điệp với đối tác

**Title:** Dùng `OutboxEvent`, `InboxEvent` và worker cho tích hợp bền vững, lấy mã QR qua HTTP đồng bộ.

**Status:** Đã chấp nhận trong thiết kế. Rà soát kỹ thuật ngày 22/11/2026.

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

**Chọn B làm cơ chế chính. Dùng A cho bước lấy mã QR để hiển thị.**

- **Yêu cầu gửi đi.** Lưu `OutboxEvent` cùng giao dịch với thay đổi nghiệp vụ cần gửi, như yêu cầu tạo vận đơn. Dùng lại mã chống trùng qua các lần gửi nếu đối tác hỗ trợ. Nếu mất phản hồi và đối tác thiếu cơ chế này, tra theo tham chiếu trước khi gửi lại hoặc chuyển xác minh. Lấy mã QR đồng bộ vì khách đang chờ kết quả. Gọi HTTP với giới hạn thời gian bên ngoài giao dịch dữ liệu, dùng tham chiếu ổn định theo đơn và áp dụng cùng quy trình xác minh nếu kết quả chưa rõ. [BPMN-01](03_bpmn.md) · [AWS về timeout và thử lại](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- **Worker.** Demo SQLite dùng một worker. Trên PostgreSQL, nếu chạy nhiều worker, dùng `FOR UPDATE SKIP LOCKED` để bỏ qua dòng đang bị khóa. Trong giao dịch ngắn, đánh dấu quyền xử lý có thời hạn rồi commit trước khi gửi HTTP. Dùng mã lượt nhận để worker cũ không ghi đè kết quả của lượt mới sau khi quyền xử lý hết hạn. Có thể lập chỉ mục theo trạng thái và thời điểm thử tiếp. [PostgreSQL về SKIP LOCKED](https://www.postgresql.org/docs/18/sql-select.html#SQL-FOR-UPDATE-SHARE)
- **Thông báo đến.** Xác thực theo hợp đồng đối tác, chẳng hạn HMAC và thời điểm ký nếu có. Phản hồi thành công theo quy ước đối tác sau khi `InboxEvent` đã được lưu bền. Ưu tiên khóa theo nguồn và mã sự kiện. Nếu thiếu mã sự kiện, chỉ dùng tổ hợp trường đã được xác nhận phân biệt sự kiện, chẳng hạn mã vận đơn, loại sự kiện và mã lần giao. Bỏ trường chỉ thay đổi theo lần gửi. Khi không thể phân biệt chắc chắn, lưu để xác minh. Xử lý tác dụng nghiệp vụ và đánh dấu thông báo đã xử lý trong cùng giao dịch. Dùng quy tắc chuyển trạng thái và phiên bản của đối tác nếu có. Ví dụ, thông báo «đang giao» đến sau «đã giao» được giữ để truy vết và không đưa trạng thái lùi. [AWS về xử lý thông điệp lặp và sai thứ tự](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)

### Reason

B giữ được dấu vết của yêu cầu giao vận qua lúc tiến trình dừng và phù hợp với quy mô, số đối tác giả định. A có lợi khi người dùng đang chờ mã QR, nhưng riêng việc thử lại trong yêu cầu HTTP không đáp ứng nhu cầu phục hồi tác vụ tạo vận đơn. C đáng cân nhắc khi có nhu cầu phân phối cho nhiều bên nhận hoặc số đo cho thấy cơ chế quét DB trở thành điểm nghẽn.

### Trade-offs

Hệ thống chấp nhận độ trễ xử lý nền. Outbox lưu được việc cần gửi và cho phép thử lại khi lỗi. Một yêu cầu có thể đến đối tác nhiều lần hoặc vẫn cần xác minh sau khi hết lượt thử. Hiệu quả nghiệp vụ như xử lý một lần chỉ đạt được trong phạm vi có mã chống trùng, quy tắc trạng thái và cách ghi dữ liệu phù hợp ở bên nhận. [AWS về transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) · [RabbitMQ về xác nhận gửi và nhận](https://www.rabbitmq.com/docs/confirms)

### Consequences

Thử lại lỗi tạm thời với khoảng chờ tăng dần và độ lệch ngẫu nhiên để tránh gửi dồn. Số lượt thử và thời hạn lưu hồ sơ cấu hình theo đối tác, cửa sổ gửi lại và yêu cầu truy vết. Kịch bản TC-04 cần cho phép ít nhất bốn lần gửi, kể cả lần đầu. Quá giới hạn hoặc lỗi không thể tự xử lý thì giao người xác minh. Theo dõi thời gian chờ, lượt thử và hồ sơ cần xử lý thủ công. Truy vết **FR-04, FR-05, FR-06, EXT-01, NFR-03, NFR-04, NFR-05**, tình huống **TC-04, TC-09**. [Kế hoạch kiểm chứng](05_kiem_chung.md)

## ADR-04: Chọn cách tổ chức dữ liệu đối soát COD

**Title:** Lưu các mốc tiền để đối soát COD ba chiều và quản lý hóa đơn vận chuyển riêng.

**Status:** Đã chấp nhận trong thiết kế. Rà soát kỹ thuật ngày 22/11/2026.

**Context:** Đối soát ba chiều trong dự án là so ba mốc tiền COD gồm số dự kiến thu theo đơn hoặc vận đơn, số ĐVVC báo đã thu và số thực nhận qua ngân hàng. Cả hai phương án dưới đây dùng cùng giả định nghiệp vụ của dự án. ĐVVC chuyển đủ số COD đã thu theo tháng, còn shop kiểm tra và thanh toán phí vận chuyển riêng. Nếu hợp đồng sau này quy định khấu trừ, cần xem lại ADR để lưu riêng COD đã thu, phí khấu trừ và tiền thực chuyển, rồi kiểm tra quan hệ giữa ba khoản theo chứng từ. [NFR-08 và REQ-COD-02](01_togaf_chuan_hoa.md) · [BPMN-03](03_bpmn.md)

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

Với COD, `PaymentEntry` ghi số dự kiến thu (`expected`), số ĐVVC báo đã thu (`collected`) và khoản thực chuyển đã xác nhận (`remitted`). Trước hết đối chiếu theo đơn hoặc vận đơn, sau đó so tổng kỳ với các giao dịch ngân hàng đã ghép. Giả định demo xác định kỳ theo ngày thu do ĐVVC ghi trên bảng kê, tính theo giờ Việt Nam. Khoản chuyển sau cuối tháng vẫn ghép về kỳ gốc theo mã kỳ hoặc tham chiếu chuyển khoản đã xác minh. Nếu bảng kê thiếu ngày thu hoặc thiếu tham chiếu đáng tin, chuyển xác minh thay vì tự gán theo ngày tiền về.

Đơn chuyển hoàn đã xác nhận chưa thu được loại khỏi số phải chuyển. Nếu ĐVVC báo đã thu đối với kiện hoàn, giữ chứng từ và mở `ReconciliationCase`. Giao hoặc hoàn một phần cần đối chiếu số được duyệt và ghi điều chỉnh hoặc hoàn tiền có chứng từ, giữ lại mốc ban đầu. Phí hoàn hàng, nếu có theo hợp đồng, được kiểm cùng `CarrierInvoice` theo vận đơn và biểu phí.

Lưu số tiền nguyên đồng bằng kiểu số nguyên, chẳng hạn `BIGINT` trên PostgreSQL. Khi dữ liệu cần phần lẻ, dùng `NUMERIC` có độ chính xác phù hợp. Khi nhập lại chứng từ, nhận diện file theo nguồn và mã lô hoặc dấu vân tay nội dung. Nhận diện dòng theo mã dòng do đối tác cấp hoặc khóa nghiệp vụ phân biệt đủ loại dòng và giao dịch. Sao kê dùng mã giao dịch trong phạm vi tài khoản. Bản bổ sung hoặc điều chỉnh hợp lệ có lịch sử riêng, để lần nhập lại không nhân đôi số liệu. [PostgreSQL về kiểu số](https://www.postgresql.org/docs/18/datatype-numeric.html) · [Quy tắc ghép dữ liệu BPMN-03](03_bpmn.md)

Với QR, yêu cầu thanh toán bằng tổng tiền đơn, gồm phí vận chuyển thu khách. Phí xử lý QR được giả định bằng 0 và vận đơn QR có số COD bằng 0. Shop kiểm tra khoản đã xác nhận thanh toán với bảng kê của Ngân hàng/Đơn vị cung cấp thanh toán QR và tiền thực nhận. Hoàn tiền và điều chỉnh có bản ghi riêng. [Mô hình dữ liệu thanh toán và đối soát](02_archimate_chuan_hoa.md) · [BPMN-03](03_bpmn.md)

### Reason

B giúp kế toán xử lý chênh lệch theo từng hồ sơ, giữ liên kết giữa số tiền và chứng từ. A khả thi với ít đơn hoặc khi dùng để kiểm tra độc lập một kỳ mẫu. Với biến thể B có nhiều giao thất bại và hàng hoàn, quy tắc ghép và lịch sử xử lý trong hệ thống giảm số bước phải dò lại giữa nhiều file.

### Trade-offs

Nhóm chấp nhận đầu tư nhập bảng kê, xác định cách đánh dấu kỳ, lập quy tắc ghép và xử lý trường hợp thiếu mã tham chiếu. Kế toán vẫn cần xác minh các khoản khó ghép. Lợi ích là có thể kiểm lại chính xác mỗi khoản lệch phát sinh ở bước nào.

### Consequences

Ví dụ, bảng kê xác nhận đã thu 300.000 đồng, ngân hàng ghi có 280.000 đồng và hóa đơn vận chuyển cùng kỳ là 20.000 đồng. Hai khoản 20.000 đồng trùng con số nhưng thuộc hai luồng hạch toán riêng. Shop vẫn theo dõi thiếu 20.000 đồng COD đến khi có chứng từ chuyển bù hoặc điều chỉnh được phê duyệt. Truy vết **FR-08 đến FR-11, REQ-COD-02, EXT-03, NFR-06, NFR-08**, tình huống **TC-05**. [Kịch bản demo COD](06_prototype.md) · [Kế hoạch kiểm chứng](05_kiem_chung.md)

## Công nghệ dùng cho demo và kiến trúc đích

Mốc đối chiếu tài liệu phát hành là **22/11/2026**. Các phiên bản ghi dưới đây là đề xuất cho môi trường kiểm chứng. Khi dựng demo, cố định phiên bản FastAPI đã thử và ghi lại bộ phụ thuộc để chạy lại cùng môi trường. Kiểm thử API trước khi nâng phiên bản. [Phạm vi prototype](06_prototype.md) · [FastAPI về ghim phiên bản](https://fastapi.tiangolo.com/deployment/versions/)

| Thành phần | Lựa chọn và căn cứ |
|---|---|
| **API và môi trường chạy** | Đề xuất Python **3.13** theo môi trường hiện có của dự án và FastAPI **0.165.0** cho prototype. FastAPI tạo mô tả OpenAPI từ API, thuận tiện cho demo luồng đặt hàng, callback và giao vận. Python 3.13 đang ở giai đoạn cập nhật bảo mật. [Vòng đời Python](https://devguide.python.org/versions/) · [Tính năng FastAPI](https://fastapi.tiangolo.com/features/) · [Ghi chú phát hành FastAPI](https://fastapi.tiangolo.com/release-notes/#01650-2026-11-18) |
| **Cơ sở dữ liệu đích** | Đề xuất PostgreSQL **18**, dùng bản cập nhật 18.x còn được hỗ trợ. Tại mốc đối chiếu, bản cập nhật là **18.7**, nhánh 18 được hỗ trợ đến tháng 11/2030. PostgreSQL 19 cũng đã phát hành. Các cơ chế khóa dòng, giao dịch và ràng buộc cần cho ADR-02 đã có trong nhánh 18. [Chính sách phiên bản PostgreSQL](https://www.postgresql.org/support/versioning/) · [Tài liệu PostgreSQL 18](https://www.postgresql.org/docs/18/explicit-locking.html) |
| **Cơ sở dữ liệu demo** | SQLite dùng một tệp cục bộ và chỉ có một giao dịch ghi đồng thời trên mỗi cơ sở dữ liệu. WAL cho phép đọc và ghi diễn ra đồng thời trong phần lớn trường hợp, với giới hạn một bên ghi. SQLite dùng cơ chế cấp quyền ghi thay cho khóa từng dòng của PostgreSQL. Có thể bắt đầu giao dịch đọc rồi ghi giữ tồn bằng `BEGIN IMMEDIATE` để xin quyền ghi sớm, đồng thời xử lý `SQLITE_BUSY` bằng thời gian chờ và thử lại có giới hạn. Ghi nhận phiên bản SQLite thực tế. Nếu bật WAL, dùng bản đã có bản vá WAL-Reset do SQLite công bố. Demo dùng một worker. Các phép thử về khóa dòng, giữ hàng đồng thời và nhiều worker chạy trên PostgreSQL. [SQLite về giao dịch](https://www.sqlite.org/lang_transaction.html) · [SQLite về WAL](https://www.sqlite.org/wal.html) |
| **Tích hợp và xử lý nền** | Dùng Ngân hàng/Đơn vị cung cấp thanh toán QR và ĐVVC giả lập cho demo. Worker đọc `OutboxEvent` từ cơ sở dữ liệu theo ADR-03. RabbitMQ là phương án đã đánh giá khi có nhu cầu phân phối sự kiện rộng hơn. [Kiến trúc ứng dụng](02_archimate_chuan_hoa.md) · [Prototype](06_prototype.md) |
| **Giao diện và hạ tầng** | Prototype đề xuất giao diện HTML/Bootstrap hoặc React tối giản. Kiến trúc đích mô tả máy ảo Linux, reverse proxy cho HTTPS và lưu chứng từ tập trung. Phiên bản giao diện, phần mềm proxy và nhà cung cấp hạ tầng sẽ được chốt theo môi trường triển khai. [Kiến trúc công nghệ](02_archimate_chuan_hoa.md) · [Phạm vi prototype](06_prototype.md) |

