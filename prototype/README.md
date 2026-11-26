# Prototype Order-to-Cash: 1 kịch bản E2E + 1 ngoại lệ

## Chạy (khuyến nghị Python 3.13)
    pip install -r requirements.txt
    python run_demo.py                 # 2 kịch bản trên terminal
    python -m pytest -q                # test tự động
    python -m uvicorn app.main:app     # giao diện http://127.0.0.1:8000 , Swagger /docs

Reset dữ liệu: bấm lại nút kịch bản trên giao diện (tự xoá và nạp 10 sản phẩm).
Chỉ chạy trên máy cá nhân: endpoint /demo/run xoá dữ liệu và không yêu cầu đăng nhập.
Trang /docs liệt kê endpoint; body của 2 webhook chưa được mô tả trong Swagger.

## Kịch bản 1: E2E (QR)
Đặt đơn, giữ hàng → tạo QR 300.000 → callback gửi 2 lần, ghi tiền 1 lần → đóng gói →
worker tạo vận đơn → bàn giao → giao thành công (event cũ không làm lùi trạng thái) → đối soát MATCHED.

## Kịch bản 2: Ngoại lệ (COD, khách từ chối nhận)
Đặt đơn COD → đóng gói → ĐVVC lỗi 503, gửi lại thành công → bàn giao → khách từ chối →
chuyển hoàn → mở hồ sơ → nhận kiện (quét lần 2 bị chặn) → QC đạt → nhập lại kho →
Payment UNCOLLECTED, Order CANCELLED.

## Đối chiếu kiểm chứng (mức prototype, SQLite)
| Mã | Phần được minh hoạ |
|---|---|
| TC-01 | Luồng QR chính |
| TC-02 | Callback gửi lặp (demo gửi 2 lần, chưa gửi đủ 10 lần) |
| TC-04 | Retry (demo lỗi 1 lần, chưa lỗi đủ 3 lần) |
| TC-06 | Quét nhận hoàn 2 lần, chỉ một RESTOCK |
| TC-07 | CS gọi sai chức năng bị 403 và có audit (thử trên fulfill, chưa có API adjustment) |
| TC-09 | Một phần: event cũ đến sau DELIVERED |

Chưa làm: TC-03 (đặt hàng đồng thời, cần PostgreSQL theo ADR-02), TC-05, TC-08, TC-10,
QR hết hạn, huỷ đơn, hoàn tiền, đổi/trả sau giao, đối soát COD, hoá đơn ĐVVC,
backoff khi retry, kiểm quyền theo chủ đơn, xác thực người dùng thật.

## Khác với tài liệu (cần nhóm thống nhất)
1. 06 (DEMO-02): giao thất bại 2 lần. Bản này dùng "khách từ chối" nên chuyển hoàn ngay (BPMN-02).
   Luật 2 lần vẫn có trong code và có test.
2. Thêm POST /api/orders/{id}/handover (chưa có trong API catalog) theo BPMN-01 bước 5.
   Thêm POST /api/worker/run để chạy worker bằng tay.
3. DEMO-01 mô tả fulfill đi thẳng tới HANDED_OVER; bản này tách fulfill → worker → handover.
4. UNCOLLECTED được dùng ở 03 và 06 nhưng danh sách trạng thái Payment trong 02 (mục 5.1) chưa có.
5. 02 liệt kê StockEntry không có PICK; bản này thêm PICK để theo nhóm "chờ bàn giao" của ADR-02.
6. POST /api/reconciliation/batches nhận JSON thay cho upload file.
7. POST /api/returns trong bản này chỉ hỗ trợ RTO và vào thẳng trạng thái IN_TRANSIT.
