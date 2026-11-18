---
marp: true
title: Order-to-Cash cho SME thương mại điện tử — biến thể II-B COD
paginate: true
---

# Order-to-Cash cho SME thương mại điện tử

## Biến thể II-B: nhiều đơn COD giao thất bại/hoàn

- Nhóm: …
- Học phần IT4350
- Mục tiêu: quản lý đơn–tồn–giao–tiền xuyên suốt và giải thích được mọi chênh lệch

---

# 1. Bối cảnh và vấn đề

- SME giả định: 01 website, 01 kho trung tâm, 01 ĐVVC, 100–300 đơn/ngày.
- Dữ liệu hiện nằm rời ở website, bảng tính, tin nhắn và bảng kê.
- Ba lỗi lớn: bán vượt tồn; hàng hoàn nhập sai; tiền COD thiếu/chậm nhưng không biết đơn nào.
- Phạm vi: đặt hàng, COD/QR, tồn, vận chuyển, đối soát, đổi/trả.

**Thông điệp:** “Đã giao” chưa chắc “đã nhận tiền”; “hàng đã về” chưa chắc “được bán lại”.

---

# 2. Mục tiêu và yêu cầu trọng tâm

- G-01 quản lý đơn thống nhất.
- G-02 đối soát COD ba chiều.
- G-03 quản lý hàng hoàn nhất quán.
- G-04 tồn kho chính xác.
- G-05 truy vết; G-06 dễ mở rộng.

Biến thể II-B:

- REQ-COD-01: giao thất bại → giao lại/RTO → nhận hoàn/QC.
- REQ-COD-02: COD gross theo đơn ↔ ĐVVC báo thu ↔ tiền gross chuyển về.
- REQ-COD-03: chỉ tăng tồn sau khi nhận thật và QC đạt; chống ghi trùng.

---

# 3. TOGAF: hiện trạng → kiến trúc đích

| Hiện trạng | Kiến trúc đích | Khoảng thiếu |
|---|---|---|
| Đơn xuất file | OMS là nguồn chính | vòng đời, mã liên kết |
| Tồn bảng tính | reservation + stock ledger | chống bán vượt, QC |
| Theo dõi giao thủ công | adapter + webhook + RTO | mapping, retry |
| Dò COD cuối kỳ | ledger + đối soát ba chiều | expected, case |

Lộ trình: WP-01 chuẩn hóa → WP-02 đơn/tồn → WP-03 giao/hoàn → WP-04 đối soát → WP-05 kiểm soát vận hành.

---

# 4. Motivation và Strategy

- Driver: đơn online tăng, giao thất bại, lệch tồn, COD khó đối soát.
- Capability cần có: điều phối đơn, kiểm soát tồn, xử lý ngoại lệ giao, QC hàng hoàn, đối soát COD, truy vết.
- Value stream: tiếp nhận → xác nhận/giữ hàng → xuất/giao → xử lý hoàn → đối soát/đóng.
- Hướng chọn: chuẩn hóa trạng thái, kiến trúc gọn cho SME, tích hợp chống trùng, ledger/case cho tiền và tồn.

> Chèn hình ArchiMate Motivation + Strategy ở đây.

---

# 5. Business Architecture

- Vai trò: khách hàng, CSKH, kho, kế toán, chủ shop, ĐVVC, Ngân hàng/Đơn vị cung cấp thanh toán QR.
- Quy trình P1–P6: nhận đơn, giữ/xuất hàng, thanh toán, giao, hoàn/QC, đối soát.
- Business service: đặt hàng, fulfillment, thanh toán, theo dõi giao, đổi/trả, đối soát.
- Trạng thái Order, Payment, Shipment và Return được tách riêng.

> Chèn hình Business Process Cooperation; dùng đường Serving/Access/Triggering đúng nghĩa.

---

# 6. Application và Data Architecture

- Modular monolith gồm Order, Inventory, Payment, Shipping, Return, Reconciliation/Reporting.
- Carrier Adapter và QR Payment Adapter cách ly định dạng đối tác.
- Inbox/outbox + idempotency key chống xử lý webhook lặp.
- `grand total = tiền hàng + phí giao khách trả`; `order_id`/reference nối đơn–giao–tiền.
- COD remittance và carrier invoice là hai luồng riêng; không net-off phí giao vào COD.
- Data theo ba mức: conceptual → logical → PostgreSQL schema/constraint/index/backup.

> Chèn hình Application Usage + ERD logic.

## 7. Technology triển khai

- Reverse proxy/TLS → ứng dụng modular monolith + worker → PostgreSQL/object storage.
- Internet/VPC, HTTPS path và private DB path được chỉ rõ.
- Dịch vụ hạ tầng: lưu giao dịch, chạy lịch retry, log/monitor, backup/restore.
- Prototype dùng mock ĐVVC và mock Đơn vị QR; production target dùng adapter thật.

Lý do chưa dùng microservice/broker: quy mô nhỏ, nhóm ít người; chưa có bằng chứng tải cần độ phức tạp đó.

---

# 8. BPMN luồng chính

**Happy path QR/COD:**

1. Khách tạo đơn và chọn COD/QR.
2. Inventory giữ chỗ nguyên tử.
3. QR intent hoặc COD receivable đều bằng grand total; QR fee giả định bằng 0.
4. Kho đóng gói, bàn giao; ĐVVC cập nhật trạng thái.
5. Vận đơn QR có COD=0; COD giao thành công chờ bảng kê và remittance tháng.

> Chèn BPMN-01; chỉ ra pool/lane, message event, gateway và timer QR.

---

# 9. BPMN ngoại lệ II-B

**Giao thất bại và chuyển hoàn:**

- Mỗi lần giao tạo DeliveryAttempt kèm lý do.
- Còn lượt và khách xác nhận → lên lịch giao lại.
- Hết lượt/từ chối → RTO; hàng về khu QC, chưa cộng hàng bán được.
- Scan lặp cùng tracking/RMA → no-op.
- QC đạt → RESTOCK; không đạt → QUARANTINE.

> Chèn BPMN-02; nhấn mạnh REQ-COD-01 và REQ-COD-03.

---

# 10. ADR và trade-off

| Quyết định | Phương án chọn | Đánh đổi |
|---|---|---|
| ADR-01 | Modular monolith | dễ triển khai, phải giữ ranh giới module |
| ADR-02 | Reservation + stock ledger | đúng tồn, nhiều bút toán hơn |
| ADR-03 | Inbox/outbox + idempotency | phục hồi tốt, cần worker/monitor |
| ADR-04 | COD gross + carrier invoice riêng | không nhầm phí với thiếu COD; quản lý hai chu kỳ tháng |

Mỗi ADR so sánh ít nhất hai phương án và truy ngược tới NFR/risk.

---

# 11. Kiểm chứng và prototype

- 08 rủi ro có xác suất, ảnh hưởng, owner và biện pháp.
- TC-03: 20 yêu cầu tranh 5 sản phẩm → đúng 5 thành công, tồn không âm.
- TC-06: quét hàng RTO hai lần → chỉ một lần nhận/QC/restock.
- TC-05: COD phải thu/đã thu 500k, chỉ chuyển 480k và invoice riêng 20k → vẫn mở case thiếu remittance 20k.
- Demo: happy QR E2E + COD giao thất bại/RTO.

> Chèn ảnh màn hình timeline đơn, nhận hoàn và case đối soát.

---

# 12. Kết luận và bước tiếp theo

- Thiết kế bám TOGAF chọn lọc A–F và đủ các lớp ArchiMate theo bài giảng.
- Trọng tâm II-B được xử lý bằng state tách biệt, chống trùng, QC trước restock và đối soát COD ba chiều.
- Kiến trúc đủ gọn cho SME nhưng có adapter và ranh giới module để mở rộng.
- Bước tiếp: hoàn thiện file `.archimate`, `.bpmn`, prototype và bằng chứng test; pilot theo WP-01…WP-05.

**Câu hỏi thảo luận:** Nếu thêm ĐVVC thứ hai, thành phần nào thay đổi và phần nào giữ nguyên?

