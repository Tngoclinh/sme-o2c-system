# Ma trận đối chiếu slide học phần và yêu cầu BTL

## 1. Kết luận rà soát

Bộ tài liệu hiện đi đúng hướng thiết kế kiến trúc doanh nghiệp: bắt đầu từ động lực và yêu cầu, mô tả hiện trạng–đích–khoảng thiếu, liên kết Business–Data–Application–Technology, quyết định bằng ADR, rồi kiểm chứng bằng quy trình, rủi ro và test. Sau khi hiệu chỉnh, bộ mã yêu cầu đã khớp tài liệu hướng dẫn II-B.

Điểm cần hiểu rõ: Markdown hiện là **đặc tả và nguồn nội dung**. Trước khi nộp, nhóm vẫn phải xuất hình bằng công cụ có ký pháp chuẩn: Archi/ArchiMate Tool cho ArchiMate và Camunda Modeler/Bizagi/bpmn.io cho BPMN. Không nên chụp Mermaid rồi gọi đó là BPMN 2.0 chính thức.

## 2. Đối chiếu theo chương bài giảng

| Nguồn học | Nội dung phải thể hiện | Vị trí trong bộ tài liệu | Kết quả |
|---|---|---|---|
| Chapter 1 — Introduction | Business–Data–Application–Technology liên kết và phục vụ mục tiêu | `01`, `02`, ma trận truy vết `05` | Đạt |
| Chapter 2 — Architecture Framework | ADM lặp, Requirements Management, Baseline/Target/Gap, roadmap | `01` mục 1–8 | Đạt theo phạm vi chọn lọc A–F của đề; không cần chép mọi biểu mẫu ADM |
| Chapter 2.1 — ArchiMate | Active/passive structure, behavior, service; quan hệ đúng nghĩa | `02` mục 1 và các viewpoint | Đạt về catalog/quan hệ; cần xuất sơ đồ chuẩn |
| Chapter 3 — Business Architecture | Actor, Role, Interface, Process, Event, Service, Object, Contract, Representation, Product | `02` mục 4; `03` | Đạt |
| Chapter 4 — Application Architecture | Component, Collaboration, Interface, Function/Process/Event/Service, Data Object | `02` mục 5 | Đạt |
| Chapter 4 — Data Architecture | Conceptual/logical/physical, ownership, lifecycle, security, information value chain | `02` mục 5.3–5.4 | Đạt ở mức thiết kế; cần vẽ ERD logic nếu giảng viên yêu cầu hình |
| Chapter 5 — Technology Architecture | Node, Device, System Software, Artifact, Network, Path, Interface, Technology behavior/service | `02` mục 6 | Đạt |
| Chapter 6 — Motivation | Stakeholder, Driver, Assessment, Goal, Outcome, Principle, Requirement, Constraint, Meaning, Value | `02` mục 2 | Đạt |
| Chapter 7 — Strategy | Resource, Capability, Value Stream, Course of Action | `02` mục 3 | Đạt |
| Chapter 8 — Implementation & Migration | Work Package, Deliverable, Event, Plateau, Gap | `01` mục 5–7; `02` mục 7 | Đạt |
| Chapter 9 — Case Study | Đi từ motivation/strategy qua các lớp, gap và migration | Toàn bộ `01`–`06` | Đạt về cấu trúc |

## 3. Đối chiếu trực tiếp đề BTL

| Yêu cầu chấm | Bằng chứng | Trạng thái |
|---|---|---|
| Bối cảnh, stakeholder, FR/NFR | `01` mục 1–4 | Đạt; dùng đúng FR-01…12, NFR-01…08 |
| Architecture Vision | `01` mục 2 | Đạt |
| Baseline/Target/Gap | `01` mục 5 | Đạt |
| Roadmap chuyển đổi | `01` mục 7; `02` mục 7 | Đạt, gồm WP-01…05 và ba giai đoạn |
| ArchiMate Motivation | `02` mục 2 | Đạt |
| ArchiMate Business | `02` mục 4 | Đạt |
| ArchiMate Application | `02` mục 5 | Đạt |
| ArchiMate Technology | `02` mục 6 | Đạt |
| Data object và liên kết quan trọng | `02` mục 5.3–5.4 | Đạt |
| Các bước migration | `02` mục 7 | Đạt |
| Tối thiểu 02 BPMN, có luồng chính và ngoại lệ | `03` có 03 quy trình | Đạt về logic; cần xuất file BPMN 2.0 |
| Tối thiểu 02 ADR, mỗi ADR so ≥2 phương án | `04` có 04 ADR | Đạt |
| Trace tối thiểu 03 yêu cầu | `05` mục 4 trace toàn bộ | Đạt |
| Thử một kịch bản bất thường/thay đổi | `05` TC-02…TC-10 | Đạt về thiết kế test; cần ảnh/log chạy thật khi có prototype |
| Danh sách 6–8 rủi ro | `05` mục 1 có đúng 08 | Đạt |
| Minh họa 01 E2E + 01 ngoại lệ | `06` happy QR và COD failed/RTO | Đạt về đặc tả; cần mockup/chương trình và ảnh demo |
| Báo cáo 25–35 trang chính | `bao_cao_tong_hop.tex` | Có nguồn; phải biên dịch và kiểm số trang cuối |
| Nguồn sơ đồ | Mermaid trong `03`; catalog trong `02` | Chưa hoàn tất chuẩn công cụ; cần lưu `.archimate` và `.bpmn` trước khi nộp |
| Bộ ADR | `04_adr.md` | Đạt |
| Prototype | `06_prototype.md` | Mới là thiết kế, chưa phải chương trình chạy |
| Slide 10–12 trang | `09_slide_bao_ve.md` có 12 slide | Đạt về nội dung; cần đưa vào PowerPoint/Canva |

## 4. Kiểm tra riêng biến thể II-B

| Yêu cầu biến thể | Cách thiết kế xử lý | Bằng chứng |
|---|---|---|
| REQ-COD-01 giao thất bại/hoàn | Lưu từng DeliveryAttempt; retry theo policy; hết lượt chuyển RTO; nhận và QC | `03` BPMN-02, `05` TC-06/09 |
| REQ-COD-02 đối soát COD | Theo tháng so COD gross theo đơn, ĐVVC báo đã thu và tiền gross chuyển về; carrier invoice kiểm/thanh toán riêng, không net-off | `03` BPMN-03, ADR-04, TC-05 |
| REQ-COD-03 tồn hàng hoàn | Chỉ RESTOCK sau nhận vật lý + QC đạt; scan/event lặp là no-op | ADR-02, BPMN-02, TC-06 |

Chính sách tài chính đã chốt: phí vận chuyển thu khách nằm trong grand total; COD thì ĐVVC thu đúng grand total, QR thì Ngân hàng/Đơn vị cung cấp thanh toán QR thu grand total và vận đơn có COD bằng 0. Giả định không có phí QR. ĐVVC xuất hóa đơn dịch vụ riêng cuối tháng để shop kiểm tra và thanh toán.

## 5. Việc bắt buộc trước khi nộp

1. Vẽ và lưu nguồn ít nhất 04 view ArchiMate bắt buộc cùng một view migration; xuất PNG/PDF để chèn LaTeX.
2. Vẽ 03 quy trình bằng BPMN 2.0, lưu `.bpmn`, kiểm tra pool/lane, message flow, event và gateway.
3. Làm mockup hoặc prototype tối thiểu theo `06`; chạy happy QR và COD giao thất bại/hoàn, chụp bằng chứng.
4. Biên dịch LaTeX, sửa overflow, đánh số hình/bảng và giữ phần chính trong 25–35 trang.
5. Chuyển `09` thành 10–12 slide trực quan, hạn chế chữ, tập nói và phân vai trả lời ADR/trade-off.

