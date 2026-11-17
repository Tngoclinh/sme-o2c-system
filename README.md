# Hướng dẫn đọc bộ tài liệu BTL Order-to-Cash

## 1. Đề tài này làm gì?

Hệ thống được thiết kế cho một cửa hàng bán quần áo trực tuyến. Hệ thống theo dõi toàn bộ hành trình của một đơn hàng:

1. Khách đặt hàng.
2. Hệ thống kiểm tra và tạm giữ hàng trong kho.
3. Khách chọn trả tiền khi nhận hàng (COD) hoặc quét mã QR.
4. Kho đóng gói và giao kiện hàng cho đơn vị vận chuyển.
5. Hệ thống theo dõi giao thành công, giao thất bại hoặc hàng bị trả về.
6. Nếu khách đổi/trả, kho kiểm tra lại chất lượng hàng và quyết định nhập lại hay cách ly.
7. Kế toán kiểm tra số tiền đáng lẽ phải nhận với bảng kê và số tiền thực sự vào ngân hàng.

Tên tiếng Anh **Order-to-Cash (O2C)** có thể hiểu đơn giản là **“từ lúc nhận đơn đến lúc nhận và kiểm tra xong tiền”**.

## 2. Nên đọc theo thứ tự nào?

| Thứ tự | Tài liệu | Đọc để hiểu |
|---:|---|---|
| 1 | `07_tu_dien_thuat_ngu.md` | Các từ chuyên ngành xuất hiện trong bài |
| 2 | `01_togaf_chuan_hoa.md` | Vì sao cần hệ thống, hệ thống phải làm gì và lộ trình xây dựng |
| 3 | `02_archimate_chuan_hoa.md` | Các bộ phận nghiệp vụ, phần mềm và hạ tầng liên hệ với nhau ra sao |
| 4 | `03_bpmn.md` | Từng quy trình chạy theo thứ tự nào và xử lý ngoại lệ thế nào |
| 5 | `04_adr.md` | Vì sao nhóm chọn phương án kiến trúc hiện tại |
| 6 | `05_kiem_chung.md` | Làm cách nào chứng minh thiết kế hoạt động đúng |
| 7 | `06_prototype.md` | Bản thử nghiệm cần có màn hình, API và kịch bản demo nào |
| 8 | `08_doi_chieu_slide_va_de_bai.md` | Từng yêu cầu trong slide/đề đã được đặt ở đâu và còn việc gì phải làm bằng công cụ vẽ |
| 9 | `09_slide_bao_ve.md` | Kịch bản 12 slide để làm PowerPoint và phân vai bảo vệ |

Thư mục `diagrams/` lưu nguồn Mermaid để review logic bằng Git. Trước khi nộp, nhóm cần bổ sung nguồn `.bpmn` và `.archimate` xuất từ công cụ đúng chuẩn như checklist trong tài liệu `08`.

## 3. Ba tình huống quan trọng nhất

### Tình huống A — Khách thanh toán QR thành công

Khách đặt 2 áo → hệ thống tạm giữ 2 áo → khách quét QR → ngân hàng/đơn vị thanh toán báo đã nhận tiền → kho đóng gói → đơn vị vận chuyển nhận hàng → kế toán đối chiếu giao dịch QR với tiền vào ngân hàng.

### Tình huống B — Đơn COD giao không thành công

Khách đặt hàng COD → kho giao kiện hàng cho đơn vị vận chuyển → giao thất bại → giao lại theo quy định → vẫn thất bại → kiện hàng quay về kho → kho kiểm tra → hàng tốt thì nhập lại → khoản COD được đóng là “chưa thu được”.

### Tình huống C — Khách trả hàng sau khi đã nhận

Khách đã nhận và trả tiền → yêu cầu trả hoặc đổi hàng → cửa hàng duyệt yêu cầu → khách gửi hàng về → kho kiểm tra chất lượng → hàng tốt thì nhập lại, hàng lỗi thì cách ly → kế toán hoàn tiền hoặc tạo đơn đổi hàng.

## 4. Quy ước trình bày

- Thuật ngữ tiếng Việt được ưu tiên. Tiếng Anh được giữ trong ngoặc để đối chiếu với tài liệu chuẩn và công cụ vẽ.
- Các mã `FR` là yêu cầu chức năng, tức hệ thống phải làm được việc gì.
- Các mã `NFR` là yêu cầu chất lượng, tức hệ thống phải nhanh, an toàn và đáng tin cậy đến mức nào.
- Các mã `ADR` là quyết định kiến trúc và lý do chọn quyết định đó.
- Các mã `TC` là trường hợp kiểm thử.
- Quy mô 100–300 đơn/ngày, 01 website, 01 kho và 01 ĐVVC là giả định thiết kế được nêu trong tài liệu hướng dẫn đề II-B. Số lần giao lại là chính sách có thể cấu hình.

