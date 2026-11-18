# Kế hoạch triển khai BTL Order-to-Cash cho SME thương mại điện tử

> Mốc ngày giữ theo kế hoạch gốc (tháng 11/2026). Trạng thái được cập nhật ngày 17/11/2026.

> Nếu chưa quen thuật ngữ, đọc `README.md` ở thư mục gốc và `07_tu_dien_thuat_ngu.md` trước. Trong kế hoạch, “đầu ra/Definition of Done” nghĩa là sản phẩm và điều kiện cụ thể để một task được coi là hoàn thành.

## 1. Đánh giá kế hoạch cũ

Kế hoạch cũ đã có đúng chuỗi đầu ra lớn: TOGAF/ArchiMate → BPMN → ADR → kiểm chứng → prototype → báo cáo. Tuy nhiên, nội dung chưa đủ phạm vi đề tài vì tập trung gần như hoàn toàn vào COD, chưa có luồng QR, chưa tách hàng bị từ chối khi giao với đổi/trả sau giao thành công, chưa có đối soát QR/hoàn tiền, và chưa định nghĩa tiêu chí hoàn thành cho từng task. Ba BPMN cũ cũng là ba biến thể của một quy trình giao hàng, nên chưa bao phủ đối soát tài chính.

## 2. Phạm vi và quy ước chung

- Trong phạm vi: đặt hàng; phí giao thu khách trong tổng đơn; giữ chỗ và sổ tồn kho; COD; QR; vận chuyển; giao thất bại/chuyển hoàn; đổi/trả sau giao; QC hàng hoàn; hoàn tiền QR; đối soát COD gross và QR; hóa đơn ĐVVC riêng; xử lý chênh lệch; báo cáo công nợ.
- Ngoài phạm vi: mua hàng từ nhà cung cấp, quản lý nhiều kho, khuyến mại phức tạp, sổ cái kế toán tổng hợp, tối ưu tuyến giao, marketplace đa người bán.
- Mỗi yêu cầu dùng một ID ổn định và phải truy vết ít nhất qua: TOGAF → ArchiMate → BPMN/API → kiểm thử.
- Quy mô 100–300 đơn/ngày, 01 website, 01 kho trung tâm và 01 ĐVVC theo tài liệu hướng dẫn II-B; tỷ lệ COD/giao thất bại nếu dùng chỉ là giả định kiểm thử, không trình bày như số liệu khảo sát.
- Chính sách chốt: ĐVVC chuyển đủ COD đã thu sau đối soát tháng; hóa đơn phí vận chuyển được shop thanh toán riêng; QR fee giả định bằng 0; tác nhân QR gọi chung là `Ngân hàng/Đơn vị cung cấp thanh toán QR`.

## 3. Kế hoạch đã hiệu chỉnh

| Task | Linh | Phương | Huyền | Deadline | Đầu ra/Definition of Done | Trạng thái |
|---|---|---|---|---|---|---|
| 1. Architecture Vision + Baseline/Target | Vision, phạm vi, mục tiêu, KPI | Baseline/Target Business & Data | Gap Application & Technology | 05/11 | Có stakeholder, scope, constraint, FR/NFR, baseline–target–gap và work package; bao phủ COD, QR, vận chuyển, đổi/trả, đối soát | Đã làm, đã chuẩn hóa lại |
| 2. ArchiMate | Motivation + Strategy + kiểm tra ID | Business + ánh xạ process/service/object | Application + Data + Technology + Implementation/Migration | 17/11 | 06 viewpoint có mục đích, stakeholder, phần tử và quan hệ đúng ngữ nghĩa; mỗi process được service ứng dụng phục vụ | Đã làm, đã đối chiếu slide |
| 3. BPMN 2.0 | BPMN-01 Order orchestration: COD/QR, giữ chỗ, xuất kho | BPMN-02 giao thất bại, chuyển hoàn, đổi/trả, QC và hoàn tiền | BPMN-03 đối soát COD/QR và xử lý chênh lệch | 19/11 | 03 collaboration diagram; pool/lane, message flow, gateway, timer/message event; mô tả trigger, pre/post-condition, ngoại lệ và dữ liệu | Đã có đặc tả/nguồn Mermaid; cần xuất BPMN bằng công cụ vẽ |
| 4. ADR | ADR-01 modular monolith | ADR-02 reservation + inventory ledger | ADR-03 idempotent webhook/outbox; cả nhóm chốt ADR-04 đối soát | 21/11 | Mỗi ADR có context, decision drivers, options, decision, consequences và trace tới NFR/risk | Đã soạn 04 ADR |
| 5. Kiểm chứng | Risk register 08 rủi ro | Quality scenario và thử nghiệm bất thường | Traceability toàn bộ yêu cầu, rà soát tính nhất quán trạng thái | 23/11 | Có owner/trigger/đối sách; test có dữ liệu vào và expected result; không còn ID mồ côi | Đã soạn; cần chạy proof khi có prototype |
| 6. Prototype minh họa | OpenAPI, dữ liệu và mã lỗi | Mock UI cho đơn, kho, đối soát, đổi/trả | Chạy E2E happy path QR và exception COD giao thất bại/hoàn | 29/11 | API contract; tối thiểu 05 màn hình; dữ liệu demo; 02 kịch bản có bằng chứng; không cần production deployment | Đã có đặc tả; chưa có chương trình chạy |
| 7. Báo cáo và thuyết trình | Tổng hợp TOGAF/ADR | Tổng hợp BPMN/kiểm chứng | Tổng hợp ArchiMate/prototype | 30/11 | Một bản LaTeX biên dịch được; mục lục, hình/bảng, tài liệu tham khảo chính thống, phụ lục truy vết; 10–12 slide và phân vai demo | Bản LaTeX và nguồn 12 slide đã có; cần chèn hình xuất cuối |

## 4. Phụ thuộc và thứ tự nghiệm thu

```text
FR/NFR + trạng thái chuẩn
        ↓
TOGAF/ArchiMate
        ↓
BPMN ─────→ API/UI prototype
  ↓               ↓
ADR ───────→ kiểm chứng
        ↓
   báo cáo hợp nhất
```

Không bắt đầu vẽ UI trước khi chốt trạng thái Order, Payment, Shipment, Return và Reconciliation; nếu không, cùng một tình huống sẽ có tên trạng thái khác nhau giữa sơ đồ và prototype.

## 5. Cấu trúc bàn giao

- `README.md`: hướng dẫn bắt đầu và thứ tự đọc cho người chưa biết nghiệp vụ.
- `07_tu_dien_thuat_ngu.md`: giải thích thuật ngữ bằng ví dụ cửa hàng bán áo.
- `00_ra_soat_va_quyet_dinh_sua.md`: phát hiện, mức độ và quyết định sửa.
- `01_togaf_chuan_hoa.md`: bản TOGAF dùng cho báo cáo.
- `02_archimate_chuan_hoa.md`: catalog/viewpoint ArchiMate dùng cho báo cáo.
- `03_bpmn.md`: ba quy trình BPMN và đặc tả.
- `04_adr.md`: bốn quyết định kiến trúc.
- `05_kiem_chung.md`: rủi ro, quality scenario, test và traceability.
- `06_prototype.md`: phạm vi prototype, API, UI và kịch bản demo.
- `08_doi_chieu_slide_va_de_bai.md`: ma trận đối chiếu slide, đề BTL và sản phẩm.
- `09_slide_bao_ve.md`: nội dung 12 slide bảo vệ.
- `bao_cao_tong_hop.tex`: bản LaTeX hợp nhất.

