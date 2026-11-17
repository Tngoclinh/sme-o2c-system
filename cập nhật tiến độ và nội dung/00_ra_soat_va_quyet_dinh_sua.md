# Rà soát TOGAF và ArchiMate

## 1. Kết luận

Hai tệp gốc đã chọn hướng kiến trúc hợp lý cho SME: modular monolith, cơ sở dữ liệu quan hệ, sổ tồn kho, adapter đơn vị vận chuyển, webhook và module đối soát. Tuy vậy, chúng **chưa thể coi là hoàn chỉnh theo phạm vi đề tài**. Bản chuẩn hóa đi kèm sửa các điểm quan trọng dưới đây; hai tệp gốc `togaf.md` và `archimate.md` được giữ làm lịch sử, còn `01_togaf_chuan_hoa.md` và `02_archimate_chuan_hoa.md` là bản dùng để nộp.

## 2. Phát hiện và quyết định sửa

| ID | Mức độ | Phát hiện | Ảnh hưởng | Quyết định sửa |
|---|---|---|---|---|
| RV-01 | Critical | FR chỉ mô tả COD, trong khi đề tài có COD/QR | Thiếu một nhánh thanh toán và đối soát | Thêm Payment component, Payment Transaction, QR callback/polling, timeout, refund và đối soát QR |
| RV-02 | Critical | “Khách không chấp nhận hàng khi giao” bị gọi là hoàn hàng; chưa có đổi/trả sau giao | Trộn RTO với reverse logistics | Tách Delivery Refusal/RTO và Customer Return/Exchange; thêm Return Authorization, QC và disposition |
| RV-03 | High | Chưa có mục tiêu/KPI, scope, out-of-scope, constraint và Request for Architecture Work hoàn chỉnh | Architecture Vision khó nghiệm thu | Bổ sung charter, G-01…G-05, KPI và acceptance |
| RV-04 | High | Baseline–Target–Gap thiếu QR, đổi/trả, dữ liệu và quản trị; WP của Order còn trống | Roadmap không bao phủ scope | Viết lại gap matrix và WP0…WP6 |
| RV-05 | High | ArchiMate dùng “Flow” để thay cho quan hệ phục vụ/hiện thực hóa và chưa có Application Service/Function | Sai mức trừu tượng, khó truy vết Business ↔ Application | Thêm Application Service/Function; dùng Assignment, Realization, Serving, Access, Triggering/Flow đúng mục đích |
| RV-06 | High | Technology coi “máy chủ ứng dụng” vừa là Node vừa ghi `(Device)` và “lưu trữ/sao lưu” chỉ là service | Lẫn phần tử cấu trúc và hành vi | Mô hình VM là Node, DBMS/reverse proxy/runtime là System Software, file/backup là Artifact, các khả năng cung cấp ra là Technology Service |
| RV-07 | Medium | Motivation chỉ có G-02/G-03, thiếu khách hàng, QR, đổi/trả và goal–outcome đầy đủ | Nhiều yêu cầu không có động lực | Hoàn chỉnh stakeholder, driver, assessment, goal, outcome, principle, requirement |
| RV-08 | Medium | Trạng thái Order chứa trạng thái giao; StockEntry chứa “trạng thái tồn” | Mô hình dữ liệu dễ tạo trạng thái mâu thuẫn | Tách state machine Order, Payment, Shipment, Return; StockEntry là bút toán với reason/location/status |
| RV-09 | Medium | “Đối soát 3 chiều” chưa nói rõ ba nguồn | Không kiểm thử được | Định nghĩa: expected receivable/Payment Ledger ↔ carrier/PSP statement ↔ bank settlement |
| RV-10 | Medium | NFR chưa có cách đo, điều kiện và nguồn bằng chứng | Không thể chứng minh | Chuẩn hóa theo stimulus–environment–response–measure và gắn test/ADR |
| RV-11 | Low | Markdown dùng cấp tiêu đề và bảng không đồng nhất; ảnh base64 làm tệp rất lớn | Khó bảo trì/biên dịch | Tạo bản chuẩn hóa nhẹ; ảnh gốc vẫn được bảo toàn trong tệp cũ |

## 3. Cơ sở chuẩn dùng để rà soát

- TOGAF Standard, 10th Edition được dùng để tổ chức Vision, các miền Business/Data/Application/Technology, gap và implementation roadmap.
- ArchiMate 3.2 được dùng cho phần tử và quan hệ; ArchiMate là mô hình tổng quan, còn BPMN 2.0.2 được dùng cho chi tiết quy trình.
- ISO/IEC 25010:2023 được dùng làm khung phân loại chất lượng; các con số NFR là mục tiêu do nhóm đặt và phải kiểm chứng.
- BPMN 2.0.2 của OMG được dùng cho collaboration, pool/lane, message flow, gateway và event.
- VietQRPay/NAPAS là căn cứ cho QR merchant-presented, mã tham chiếu giao dịch và đối soát; prototype mô phỏng PSP, không tuyên bố tích hợp trực tiếp NAPAS.

## 4. Tài liệu tham khảo chính

1. The Open Group, [Understanding the TOGAF Standard](https://help.opengroup.org/hc/en-us/articles/32726995273362-Understanding-the-TOGAF-Standard).
2. The Open Group, [ArchiMate 3 Certification Q&A — current specification 3.2](https://help.opengroup.org/hc/en-us/articles/32115890396562-ArchiMate-Certification-Exam-Q-As).
3. The Open Group ArchiMate Community, [ArchiMate 101](https://archimate-community.pages.opengroup.org/workgroups/archimate-101/).
4. OMG, [BPMN 2.0.2 Specification](https://www.omg.org/spec/BPMN/2.0.2/PDF).
5. ISO, [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html).
6. NAPAS Developer, [VietQRPay](https://developer.napas.com.vn/vi/product/introduce/viet-qr-pay).
7. GHN, [Callback trạng thái đơn hàng](https://api.ghn.vn/home/docs/detail?id=84).
8. OWASP, [API Security Top 10 — 2023](https://api-security.owasp.org/editions/2023/en/0x11-t10/).

