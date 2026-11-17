1. Kiến trúc đề xuất  
1.  Bối cảnh giả định (ghi rõ trong báo cáo)  
* SME bán đồ quần áo, khoảng 200-500 đơn/ngày, bán qua website. Khoảng 70% đơn là COD, khoảng 15–20% đơn thất bại/hoàn. Đây là giả định, cần ghi rõ và có thể tìm nguồn tham khảo.  
* Hiện trạng (Baseline): nhập đơn bằng Excel/Zalo, tồn kho ghi tay, đối soát bằng file Excel bảng kê của ĐVVC vào cuối tháng.

Để bài toán đủ cụ thể, tôi đề xuất một SME bán lẻ trực tuyến với các giả định sau:

| Yếu tố | Giả định |
| ----- | ----- |
| Doanh nghiệp | Shop bán hàng (quần áo) trực tuyến |
| Các bộ phận nghiệp vụ | Bán hàng, kho, kế toán, chăm sóc khách hàng |
| Kênh bán | 1 website thương mại điện tử |
| Kho hàng | 1 kho trung tâm |
| Thanh toán | COD và chuyển khoản QR |
| Vận chuyển | 1 đối tác vận chuyển giả lập |
| Quy mô | Khoảng 200–500 đơn/ngày |
| Bất thường | Nhiều đơn giao thất bại, hoàn hàng và chậm đối soát |
| Hiện trạng | Quản lý đơn trên website, tồn kho bằng bảng tính, đối soát COD thủ công |

2. Stakeholders

| Stakeholder | Vai trò | Mối quan tâm chính |
| ----- | ----- | ----- |
| Chủ doanh nghiệp | Quyết định đầu tư, quản lý hoạt động | Chi phí, doanh thu, khả năng kiểm soát vận hành |
| Khách hàng | Đặt hàng, thanh toán, nhận hoặc trả hàng | Trạng thái đơn chính xác, xử lý thuận tiện |
| Nhân viên bán hàng/CSKH | Theo dõi và hỗ trợ đơn hàng | Tra cứu thông tin và xử lý ngoại lệ |
| **Nhân viên kho** | Xuất kho, tiếp nhận và kiểm tra hàng hoàn | Tồn kho chính xác, tránh nhập/xuất trùng |
| **Nhân viên kế toán** | Đối soát COD, kiểm tra thanh toán | Dòng tiền, chênh lệch, chứng từ |
| **Đơn vị vận chuyển** | Giao hàng, thu COD và chuyển hoàn | Trao đổi thông tin đơn và giao vận |
| (Bộ phận IT) | Quản trị và duy trì hệ thống | Tính sẵn sàng, bảo mật, khả năng bảo trì |

3. Yêu cầu chức năng và phi chức năng  
+ y/c chức năng:  
* **FR-01** Tiếp nhận (tạo & duyệt đơn) đơn COD \- KH tạo và theo dõi đơn hàng   
* **FR-02** Kiểm tra còn hàng \-\> Giữ chỗ tồn kho. (kiểm tra … )  
* **FR-03** Bàn giao đơn cho ĐVVC.  
* **FR-04** Nhận trạng thái giao (webhook: cơ chế bên ngoài gọi ngược vào hệ thống khi có sự kiện).  
* **FR-05** Xử lý giao thất bại (giao lại tối đa N lần hoặc hoàn).  
* **FR-06** Nhận hàng hoàn, kiểm (QC), nhập kho theo trạng thái.  
* **FR-07** Nhập bảng kê ĐVVC và đối soát tiền.   
* **FR-08** Xử lý chênh lệch.   
* **FR-09** Báo cáo công nợ phải thu từ ĐVVC.


Hết hàng ➝ không hoàn thành đơn hàng    
Còn hàng nhưng đơn vị vận chuyển không giao hàng thành công ➝ không hoàn thành đơn hàng    
Còn hàng, giao hàng thành công nhưng khách không chấp nhận hàng ➝ không hoàn thành đơn hàng    
Còn hàng và giao hàng thành công ➝ hoàn thành đơn hàn

+ y/c phi chức năng:

Các chỉ tiêu sau là mục tiêu thiết kế đề xuất của nhóm, cần được kiểm chứng ở mức prototype hoặc phân tích kiến trúc phù hợp.

| ID | Yêu cầu | Tiêu chí đề xuất |
| ----- | ----- | ----- |
| NFR-01 | Hiệu năng | 95% yêu cầu tra cứu đơn có thời gian phản hồi dưới 2 giây trong điều kiện tải giả định |
| NFR-02 | Tính sẵn sàng | Mục tiêu 99,5% trong thời gian vận hành được xác định |
| NFR-03 | Nhất quán dữ liệu | Không ghi nhận trùng một nghiệp vụ nhập hàng hoàn hoặc ghi nhận thanh toán do sự kiện gửi lặp |
| NFR-04 | Khả năng phục hồi tích hợp | Có cơ chế retry và đồng bộ lại khi hệ thống đối tác tạm thời không khả dụng |
| NFR-05 | Bảo mật | Xác thực, phân quyền theo vai trò và bảo vệ các giao diện quản trị |
| NFR-06 | Khả năng truy vết | Lưu các thao tác và sự kiện quan trọng kèm mã tham chiếu, thời điểm và nguồn phát sinh |
| NFR-07 | Khả năng bảo trì | Tách biệt logic quản lý đơn, tồn kho, vận chuyển và đối soát |
| NFR-08 | Toàn vẹn tài chính | Mọi chênh lệch COD phải được ghi nhận và có trạng thái xử lý rõ ràng |

4. Architecture Vision \- Giai đoạn này trả lời “vì sao làm, làm cho ai, phạm vi đến đâu, thành công trông như thế nào”   
+ Yêu cầu thực hiện kiến trúc (Request for Architecture Work)   
+   
+ Vision: 

Xây dựng kiến trúc một hệ thống Order-to-Cash tích hợp, hỗ trợ SME thương mại điện tử quản lý xuyên suốt quá trình đặt hàng, kiểm soát tồn kho, thanh toán, vận chuyển và đối soát.

Kiến trúc hướng tới việc đồng bộ thông tin giữa các bộ phận nghiệp vụ, giảm thao tác thủ công, hỗ trợ xử lý hiệu quả các trường hợp giao hàng thất bại và hoàn hàng, đồng thời nâng cao khả năng kiểm soát tiền COD và tính chính xác của tồn kho.

+ các nguyên tắc kiến trúc: (này cho thêm vô thui)

**Single Source of Truth:** Mỗi miền dữ liệu có một thành phần chịu trách nhiệm cập nhật chính.

**Separation of Concerns:** Quản lý đơn hàng, tồn kho, vận chuyển và đối soát có ranh giới nghiệp vụ riêng.

**Data Integrity:** Giao dịch kho và thanh toán phải có cơ chế bảo đảm toàn vẹn và chống xử lý trùng.

**Traceability:** Các thay đổi quan trọng được ghi nhận để kiểm toán và đối soát.

**Simplicity:** Ưu tiên kiến trúc có chi phí và mức độ phức tạp phù hợp quy mô SME.

5. Baseline/Target

| Khía cạnh Nghiệp vụ | Hiện trạng (Baseline) | Mục tiêu Kiến trúc (Target) | Gap (Khoảng trống cần giải quyết) | Gói công việc |
| :---- | :---- | :---- | :---- | :---- |
| **Quản lý đơn hàng** | Khách đặt qua web, nhân viên xuất file Excel hoặc chép tay qua Zalo để xử lý. | Đơn hàng đổ về hệ thống quản lý tập trung (OMS) tự động theo thời gian thực. | Cần module tiếp nhận đơn hàng, loại bỏ hoàn toàn thao tác xuất/nhập file thủ công. |  |
| **Quản lý tồn kho** | Ghi chép sổ sách hoặc trừ lùi trên file Excel; thường xuyên lệch số liệu khi hàng đang đi đường hoặc bị hoàn về. | Giữ chỗ (allocate) tồn kho ngay khi lên đơn. Tự động cộng lại tồn kho nếu đơn bị hủy hoặc nhập lại hàng hoàn thành công. | Cần cơ chế khóa tồn kho (inventory reservation) và đồng bộ trạng thái kho theo trạng thái vận chuyển ( Khả dụng, Giữ chỗ, Đã bàn giao ĐVVC, Đang hoàn về, Chờ kiểm QC, Hàng lỗi/cách ly) | WP1 |
| **Vận chuyển & Hàng hoàn**  | Không nắm được trạng thái real-time. Hàng hoàn về kho bị chất đống, kiểm đếm thủ công, dễ thất thoát. | Nhận Webhook trạng thái tự động từ ĐVVC. Quy trình nhập kho hàng hoàn (QC, phân loại lỗi/nguyên vẹn) được hệ thống hóa. | Cần tích hợp API/Webhook với ĐVVC và thiết kế quy trình QC riêng biệt cho hàng hoàn. | WP2,WP4 |
| **Thanh toán & Đối soát COD**  | Kế toán tải bảng kê Excel của ĐVVC vào cuối tháng, dò tay từng mã vận đơn để chốt công nợ. Chênh lệch khó tra cứu. | Hệ thống tự động import bảng kê ĐVVC, tự động khớp lệnh với mã đơn. Cảnh báo các đơn lệch tiền hoặc quá hạn đối soát. | Cần module đối soát COD, logic nhận diện chênh lệch (thừa/thiếu/trễ) và cơ chế đánh dấu trạng thái xử lý chênh lệch. | WP3,WP5 |
| Công nghệ và bảo mật | File Excel trên máy cá nhân, Zalo cá nhân; dữ liệu khách rải rác | Máy chủ ứng dụng, cơ sở dữ liệu quan hệ, nhật ký kiểm toán, phân quyền, mã hóa dữ liệu cá nhân | Không có nhật ký kiểm toán, phân quyền hay sao lưu; số điện thoại và địa chỉ khách không được bảo vệ | WP0 |

