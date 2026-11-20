# Giải thích các phần tử Technology trong ArchiMate 3.2

Tài liệu này giải thích bốn dòng trong [mục 4 — Technology của bài Order-to-Cash](02_archimate_chuan_hoa.md#4-technology--hạ-tầng-và-vận-hành). Các tên máy, phần mềm và tệp cụ thể bên dưới dùng để minh họa cách vẽ. [Bộ thẻ tham chiếu ArchiMate 3.2 của The Open Group](https://barbierdarnal.com/Enterprise_Architect/Clinique/ArchiMate_3.2_Specification_notation.pdf#page=9)

| Phần tử | Câu hỏi giúp nhận biết | Ví dụ trong bài |
|---|---|---|
| **Node** | Ứng dụng chạy ở đâu? | Máy ảo chạy hệ thống đơn hàng của shop |
| **Device** | Thiết bị vật lý nào cung cấp tài nguyên tính toán? | Máy chủ vật lý ở trung tâm dữ liệu của nhà cung cấp cloud |
| **System Software** | Phần mềm nào tạo môi trường chạy, kết nối hoặc lưu dữ liệu? | Linux, Python Runtime, PostgreSQL |
| **Artifact** | Tệp hay gói cụ thể nào được triển khai, sử dụng hoặc tạo ra? | Gói triển khai ứng dụng, tệp bảng kê COD, tệp sao lưu |

## 1. Node — Môi trường chạy hệ thống

**Cloud VM** là máy ảo thuê trên cloud. Shop có thể triển khai ứng dụng Order-to-Cash lên máy ảo này để khách đặt hàng và nhân viên tra cứu đơn. Khi vẽ, có thể đặt tên Node là **Máy ảo chạy ứng dụng O2C**.

**Container Host** là máy hoặc môi trường dùng để chạy container. Container đóng gói ứng dụng cùng thành phần cần để chạy. Nếu nhóm chọn chạy bằng container, có thể ghi **Máy chủ chạy container O2C** làm Node. Một máy ảo cũng có thể làm máy chủ chạy container, nên chọn cách ghi theo mức chi tiết cần thể hiện.

Trong cột quan hệ, **Composition** biểu thị quan hệ toàn thể–bộ phận. Chỉ thêm quan hệ này khi sơ đồ thực sự mô tả các Node con là bộ phận của môi trường chạy lớn hơn. Nếu mục đích chỉ là chỉ ra nơi triển khai ứng dụng, một Node có tên rõ ràng là đủ.

## 2. Device — Thiết bị vật lý

Device trong dòng này là **phần cứng thật** có CPU, RAM và thiết bị lưu trữ. Ví dụ, một máy chủ vật lý tại trung tâm dữ liệu cung cấp tài nguyên cho máy ảo của shop. Nếu sơ đồ cần thể hiện cả hai mức, ghi **Máy chủ vật lý của nhà cung cấp cloud** là Device và **Máy ảo chạy O2C** là Node.

Ở góc nhìn logic, nhóm có thể chỉ vẽ máy ảo mà shop sử dụng. Thông số và vị trí máy chủ vật lý có thể nằm ngoài phạm vi thông tin shop quản lý.

## 3. System Software — Phần mềm nền hỗ trợ vận hành

| Tên trong ảnh | Là gì? Ví dụ trong hệ thống |
|---|---|
| **Linux** | Hệ điều hành của máy ảo. Linux quản lý tiến trình, tệp và kết nối mạng để ứng dụng có thể chạy. |
| **Reverse Proxy** | Phần mềm đứng trước ứng dụng để nhận kết nối và chuyển yêu cầu vào bên trong. Ví dụ, Nginx nhận thông báo HTTPS “đã giao” từ ĐVVC rồi chuyển yêu cầu đến ứng dụng O2C. |
| **Python Runtime** | Môi trường thực thi mã Python. Nó chạy mã của ứng dụng khi nhân viên mở trang tra cứu đơn. |
| **PostgreSQL DBMS** | Hệ quản trị cơ sở dữ liệu. PostgreSQL đọc, ghi và bảo vệ tính nhất quán của các bản ghi, chẳng hạn khi lưu một vận đơn hoặc cập nhật trạng thái giao. |
| **Scheduler / Worker** | Scheduler quyết định lúc nào một việc cần chạy. Worker thực hiện việc đó ở chế độ nền. Ví dụ, bộ lập lịch đánh thức tác vụ mỗi phút, còn worker của ứng dụng thử gửi lại yêu cầu tạo vận đơn đã lỗi. |

Bộ lập lịch dùng chung cho hạ tầng có thể được mô hình là **System Software**. Nếu worker chạy logic nghiệp vụ riêng của shop, phần hành vi đó thuộc **Application Function** và có thể được thực thi bởi tiến trình của ứng dụng. Cách phân loại phụ thuộc vai trò của phần mềm trong mô hình.

Trong cột quan hệ, **Assignment** cho biết phần tử nào thực hiện hành vi. Ví dụ, gán PostgreSQL cho **Technology Function** “Lưu giao dịch”. Chức năng này có thể hiện thực hóa **Technology Service** “Lưu trữ dữ liệu quan hệ” để ứng dụng sử dụng. [ArchiMate 101 — Lớp Technology](https://archimate-community.pages.opengroup.org/workgroups/archimate-101/)

## 4. Artifact — Hiện vật kỹ thuật cụ thể

| Tên trong ảnh | Là gì? Ví dụ trong hệ thống |
|---|---|
| **Application package** | Gói phần mềm mang mã chương trình ra môi trường chạy, chẳng hạn image container của ứng dụng O2C nếu sử dụng container. |
| **DB schema** | Cấu trúc dữ liệu quy định có bảng nào, cột nào và các bảng liên kết ra sao. Khi thể hiện Artifact, chọn một hiện vật cụ thể như tệp `schema.sql` hoặc tập lệnh tạo và cập nhật các bảng đơn hàng, vận đơn và đối soát. |
| **Statement file** | Tệp bảng kê từ đối tác. Ví dụ, `bang-ke-COD-2026-11.csv` do ĐVVC gửi, có mã vận đơn và số tiền đã thu hộ để kế toán đối chiếu. |
| **Backup** | Tệp sao lưu phục vụ khôi phục dữ liệu. Ví dụ, `o2c-2026-11-21.backup` chứa bản sao cơ sở dữ liệu tại thời điểm sao lưu. |
| **Log** | Tệp ghi sự kiện kỹ thuật. Ví dụ, `o2c.log` ghi thời điểm, mã vận đơn và kết quả khi hệ thống nhận thông báo “đã giao”. |

Trong cột quan hệ, **Realization** nối hiện vật cụ thể với phần tử mà nó hiện thực hóa. **Gói triển khai O2C** hiện thực hóa **Application Component** “Ứng dụng O2C”. **Tệp CSV bảng kê COD** là dạng vật lý có thể dùng để hiện thực hóa **Data Object** “Dữ liệu bảng kê COD”. Nếu hệ thống nhập và chuẩn hóa bảng kê, có thể mô tả riêng tệp gốc và dữ liệu đã nhập. [ArchiMate 101 — Data Object và Artifact](https://archimate-community.pages.opengroup.org/workgroups/archimate-101/)

## Đọc cả bốn phần tử trong một tình huống

Cuối tháng, kế toán nhận tệp bảng kê COD và đưa vào chức năng đối soát. **Máy ảo O2C** là Node chạy chức năng đó. Tài nguyên máy ảo đến từ **máy chủ vật lý** của nhà cung cấp cloud, tức Device. **Linux, Python Runtime và PostgreSQL** là System Software hỗ trợ chạy và lưu kết quả. **Tệp CSV mà ĐVVC gửi** là Artifact. Kế toán dùng các dòng đã nhập để so với số phải thu theo đơn và số tiền shop thực nhận qua ngân hàng.
