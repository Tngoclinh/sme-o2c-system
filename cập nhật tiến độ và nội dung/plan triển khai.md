# Kế hoạch triển khai BTL Order-to-Cash cho SME thương mại điện tử

> Mốc ngày giữ theo kế hoạch gốc (tháng 11/2026). Trạng thái được cập nhật ngày 17/11/2026.

## 1. Đánh giá kế hoạch cũ

Kế hoạch cũ đã có đúng chuỗi đầu ra lớn: TOGAF/ArchiMate → BPMN → ADR → kiểm chứng → prototype → báo cáo. Tuy nhiên, nội dung chưa đủ phạm vi đề tài vì tập trung gần như hoàn toàn vào COD, chưa có luồng QR, chưa tách hàng bị từ chối khi giao với đổi/trả sau giao thành công, chưa có đối soát QR/hoàn tiền, và chưa định nghĩa tiêu chí hoàn thành cho từng task. Ba BPMN cũ cũng là ba biến thể của một quy trình giao hàng, nên chưa bao phủ đối soát tài chính.

## 2. Phạm vi và quy ước chung

- Trong phạm vi: đặt hàng; giữ chỗ và sổ tồn kho; COD; QR; vận chuyển; giao thất bại/chuyển hoàn; đổi/trả sau giao; QC hàng hoàn; hoàn tiền QR; đối soát COD và QR; xử lý chênh lệch; báo cáo công nợ.
- Ngoài phạm vi: mua hàng từ nhà cung cấp, quản lý nhiều kho, khuyến mại phức tạp, sổ cái kế toán tổng hợp, tối ưu tuyến giao, marketplace đa người bán.
- Mỗi yêu cầu dùng một ID ổn định và phải truy vết ít nhất qua: TOGAF → ArchiMate → BPMN/API → kiểm thử.
- Các con số 200–500 đơn/ngày, tỷ lệ COD và giao thất bại là giả định thiết kế, không trình bày như số liệu khảo sát.

## 3. Kế hoạch đã hiệu chỉnh

| Task | Linh | Phương | Huyền | Deadline | Đầu ra/Definition of Done | Trạng thái |
|---|---|---|---|---|---|---|
| 1. Architecture Vision + Baseline/Target | Vision, phạm vi, mục tiêu, KPI | Baseline/Target Business & Data | Gap Application & Technology | 05/11 | Có stakeholder, scope, constraint, FR/NFR, baseline–target–gap và work package; bao phủ COD, QR, vận chuyển, đổi/trả, đối soát | Đã làm, đã chuẩn hóa lại |
| 2. ArchiMate | Motivation + kiểm tra ID | Business + ánh xạ process/service/object | Application + Technology + Implementation/Migration | 17/11 | 05 viewpoint có mục đích, stakeholder, phần tử và quan hệ đúng ngữ nghĩa; mỗi process được service ứng dụng phục vụ | Đã làm, đã chuẩn hóa lại |
| 3. BPMN 2.0 | BPMN-01 Order orchestration: COD/QR, giữ chỗ, xuất kho | BPMN-02 giao thất bại, chuyển hoàn, đổi/trả, QC và hoàn tiền | BPMN-03 đối soát COD/QR và xử lý chênh lệch | 19/11 | 03 collaboration diagram; pool/lane, message flow, gateway, timer/message event; mô tả trigger, pre/post-condition, ngoại lệ và dữ liệu | Chưa làm |
| 4. ADR | ADR-01 modular monolith | ADR-02 reservation + inventory ledger | ADR-03 idempotent webhook/outbox; cả nhóm chốt ADR-04 đối soát | 21/11 | Mỗi ADR có context, decision drivers, options, decision, consequences và trace tới NFR/risk | Chưa làm |
| 5. Kiểm chứng | Risk register 08 rủi ro | Quality scenario và thử nghiệm bất thường | Traceability ≥ 06 yêu cầu, rà soát tính nhất quán trạng thái | 23/11 | Có owner/trigger/đối sách; test có dữ liệu vào và expected result; không còn ID mồ côi | Chưa làm |
| 6. Prototype minh họa | OpenAPI, dữ liệu và mã lỗi | Mock UI cho đơn, kho, đối soát, đổi/trả | Chạy E2E happy path QR và exception COD giao thất bại/hoàn | 29/11 | API contract; tối thiểu 05 màn hình; dữ liệu demo; 02 kịch bản có bằng chứng; không cần production deployment | Chưa làm |
| 7. Báo cáo và thuyết trình | Tổng hợp TOGAF/ADR | Tổng hợp BPMN/kiểm chứng | Tổng hợp ArchiMate/prototype | 30/11 | Một bản LaTeX biên dịch được; mục lục, hình/bảng, tài liệu tham khảo chính thống, phụ lục truy vết; slide và phân vai demo | Chưa làm |

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

- `00_ra_soat_va_quyet_dinh_sua.md`: phát hiện, mức độ và quyết định sửa.
- `01_togaf_chuan_hoa.md`: bản TOGAF dùng cho báo cáo.
- `02_archimate_chuan_hoa.md`: catalog/viewpoint ArchiMate dùng cho báo cáo.
- `03_bpmn.md`: ba quy trình BPMN và đặc tả.
- `04_adr.md`: bốn quyết định kiến trúc.
- `05_kiem_chung.md`: rủi ro, quality scenario, test và traceability.
- `06_prototype.md`: phạm vi prototype, API, UI và kịch bản demo.
- `bao_cao_tong_hop.tex`: bản LaTeX hợp nhất.

