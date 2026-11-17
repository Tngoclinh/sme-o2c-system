# BPMN 2.0 — ba quy trình Order-to-Cash

> Các sơ đồ dưới đây là blueprint hiển thị trong Markdown. Khi vẽ bằng bpmn.io/Visual Paradigm phải dùng đúng ký pháp BPMN 2.0: pool cho participant độc lập, lane cho vai trò nội bộ, sequence flow chỉ trong một pool và message flow giữa các pool. Không nối sequence flow xuyên pool.

## 1. BPMN-01 — Đặt hàng, thanh toán COD/QR và fulfillment

### 1.1 Đặc tả

| Thuộc tính | Nội dung |
|---|---|
| Trigger | Customer submit order |
| Pool | Khách hàng; SME O2C; PSP; ĐVVC |
| Lane SME | Storefront/Order; Payment; Inventory; Warehouse/Shipping |
| Pre-condition | SKU có dữ liệu tồn và phương thức thanh toán hợp lệ |
| End success | Shipment `HANDED_OVER`, Order `FULFILLING`; QR `PAID` hoặc COD receivable `EXPECTED` |
| End alternate | Order `CANCELLED`; reservation được release; payment intent expired/failed |
| Data | Order, Reservation, Payment, Shipment, OutboxEvent |
| Requirement | FR-01…FR-06, NFR-02, NFR-04 |

### 1.2 Blueprint

```mermaid
flowchart LR
  subgraph C[Pool: Khách hàng]
    C0((Bắt đầu)) --> C1[Nhập giỏ hàng, địa chỉ, COD/QR] --> C2[Gửi đơn]
    C8[Quét QR] --> C9[Nhận xác nhận/tracking]
  end
  subgraph S[Pool: SME O2C]
    S1[Validate đơn] --> G1{Đủ tồn?}
    G1 -- Không --> Sx[Hủy đơn / báo hết hàng]
    G1 -- Có --> S2[Atomic reservation]
    S2 --> G2{Phương thức?}
    G2 -- COD --> S3[Tạo COD receivable EXPECTED]
    G2 -- QR --> S4[Tạo Payment Intent + reference]
    S5[Catch message: payment.paid] --> S6[Confirm Order]
    S4 -. timer hết hạn .-> S7[Expire intent; release reservation]
    S3 --> S6
    S6 --> S8[Pick & pack] --> S9[Commit stock / tạo shipment] --> S10[Outbox tạo vận đơn]
    S11[Nhận tracking code] --> Se((Kết thúc))
  end
  subgraph P[Pool: PSP]
    P1[Hiển thị/xử lý QR] --> P2[Callback có chữ ký + external_ref]
  end
  subgraph L[Pool: ĐVVC]
    L1[Nhận yêu cầu tạo vận đơn] --> L2[Trả tracking code]
  end
  C2 -. Order message .-> S1
  S4 -. QR payload .-> C8
  C8 -. Payment request .-> P1
  P2 -. Payment callback .-> S5
  Sx -. Out-of-stock .-> C9
  S7 -. Payment expired .-> C9
  S10 -. Create shipment .-> L1
  L2 -. Shipment response .-> S11
  S11 -. Confirmation .-> C9
```

### 1.3 Gateway/event bắt buộc khi vẽ BPMN

- XOR `Đủ tồn?` và `Phương thức?`.
- Intermediate message catch `payment.paid`; không coi việc khách mở QR là đã trả tiền.
- Interrupting timer boundary trên subprocess `Chờ thanh toán QR`; khi hết hạn phải expire payment intent và release reservation.
- Service task webhook phải xác thực chữ ký/token và idempotency key trước khi ghi payment ledger.
- Message flow đến ĐVVC; outbox retry nằm trong pool SME, không vẽ sequence flow đi xuyên pool.

## 2. BPMN-02 — Giao thất bại/RTO và đổi-trả sau giao

### 2.1 Đặc tả

| Thuộc tính | Nội dung |
|---|---|
| Trigger A | Carrier gửi `delivery_failed` hoặc `delivery_refused` |
| Trigger B | Customer tạo return/exchange request sau `DELIVERED` |
| Pool | Khách hàng; SME O2C; ĐVVC/PSP |
| Lane SME | Shipping/CSKH; Return; Warehouse/QC; Payment/Inventory |
| Pre-condition | Có Order + Shipment; với return phải còn trong policy giả định |
| End success | Retry scheduled, hoặc RTO/Return được nhận–QC–restock/quarantine và tiền/đơn được điều chỉnh |
| End alternate | Return rejected có lý do; discrepancy/manual case nếu hàng/tiền không khớp |
| Requirement | FR-07…FR-09, NFR-02, NFR-06, NFR-08 |

### 2.2 Blueprint

```mermaid
flowchart TD
  E0((Message start)) --> G0{Loại sự kiện?}
  G0 -- Giao thất bại --> A1[Ghi delivery attempt idempotent]
  A1 --> G1{Còn lượt giao và khách đồng ý?}
  G1 -- Có --> A2[Đặt lịch giao lại] --> Ea((Chờ lần giao mới))
  G1 -- Không --> A3[Yêu cầu chuyển hoàn / Shipment RETURNING]
  G0 -- Return/Exchange request --> B1[Kiểm tra eligibility]
  B1 --> G2{Hợp lệ?}
  G2 -- Không --> Bx[Từ chối, ghi lý do] --> Ex((Kết thúc))
  G2 -- Có --> B2[Tạo RMA + hướng dẫn gửi hàng]
  A3 --> C1[ĐVVC trả kiện]
  B2 --> C1
  C1 --> C2[Kho scan tracking/RMA, nhận vào QC]
  C2 --> G3{QC result?}
  G3 -- Bán lại được --> C3[StockEntry RESTOCK]
  G3 -- Lỗi/hỏng --> C4[StockEntry QUARANTINE]
  C3 --> G4{Nguồn và yêu cầu?}
  C4 --> G4
  G4 -- QR chưa giao/RTO hoặc trả hàng --> D1[Tạo refund theo approval]
  G4 -- COD đã thu, trả hàng --> D2[Tạo nghĩa vụ hoàn tiền thủ công/chuyển khoản]
  G4 -- Đổi hàng --> D3[Reserve SKU thay thế + tạo shipment mới]
  G4 -- COD chưa thu/RTO --> D4[Đóng COD expected = uncollected]
  D1 --> D5[Nhận refund callback]
  D2 --> D6[Record payout reference]
  D3 --> D7[Link replacement order]
  D4 --> D8[Đóng RMA/RTO]
  D5 --> D8
  D6 --> D8
  D7 --> D8
  D8 --> Ee((Kết thúc))
```

### 2.3 Quy tắc nghiệp vụ

- `Delivery refusal/RTO` xảy ra trước khi hoàn tất giao; `Customer return/exchange` xảy ra sau `DELIVERED`. Hai khái niệm không dùng chung một trạng thái Order.
- Policy prototype: tối đa 02 delivery attempts; return request trong 07 ngày; các con số là giả định cấu hình.
- Chỉ restock sau khi scan đúng tracking/RMA và QC pass. QC fail vào quarantine, không tăng available-to-promise.
- Refund là một payment transaction mới tham chiếu giao dịch gốc, không sửa/xóa payment entry cũ.
- Message/callback lặp từ carrier/PSP phải bị khử trùng theo external event ID.

## 3. BPMN-03 — Đối soát COD/QR và xử lý chênh lệch

### 3.1 Đặc tả

| Thuộc tính | Nội dung |
|---|---|
| Trigger | Carrier/PSP statement và bank settlement được nhận theo kỳ |
| Pool | Carrier/PSP/Bank; SME O2C |
| Lane SME | Import/Validation; Matching Engine; Accountant; Reporting |
| Pre-condition | Expected ledger đã có order_id, external_ref, amount và payment method |
| End success | Batch closed; các dòng matched hoặc có case có owner/SLA |
| Data | Statement, StatementLine, PaymentEntry, Shipment, Settlement, ReconciliationCase |
| Requirement | FR-10…FR-13, NFR-06, NFR-08 |

### 3.2 Blueprint

```mermaid
flowchart LR
  X0((Message start)) --> X1[Nhận statement/settlement]
  X1 --> X2[Hash file + kiểm schema/trùng batch]
  X2 --> G0{Hợp lệ?}
  G0 -- Không --> X3[Reject/quarantine file + thông báo] --> Xe((Kết thúc lỗi))
  G0 -- Có --> X4[Normalize external reference, fee, amount]
  X4 --> X5[3-way match: expected ledger ↔ statement ↔ bank]
  X5 --> G1{Kết quả?}
  G1 -- Exact match --> X6[Post settlement/fee entries]
  G1 -- Partial/missing/duplicate/unknown --> X7[Tạo ReconciliationCase]
  X7 --> X8[Kế toán điều tra với chứng từ]
  X8 --> G2{Resolution?}
  G2 -- Đối tác sửa/chuyển bù --> X9[Import adjustment settlement]
  G2 -- Mapping sai nội bộ --> X10[Post adjustment có approval]
  G2 -- Chưa xử lý --> X11[Giữ OPEN + aging/SLA]
  X9 --> X12[Re-match]
  X10 --> X12
  X12 --> G1
  X6 --> X13[Cập nhật aging/dashboard]
  X11 --> X13
  X13 --> G3{Còn case mở?}
  G3 -- Không --> X14[Close batch]
  G3 -- Có --> X15[Close processing run, batch PARTIAL]
  X14 --> Ee((Kết thúc))
  X15 --> Ee
```

### 3.3 Luật matching

1. Khóa ưu tiên: provider + external transaction/tracking reference; không match chỉ bằng số tiền.
2. COD expected = số phải thu khách; carrier statement = COD collected − carrier fees; bank settlement = tiền thực nhận. Phí phải là entry riêng.
3. QR expected/paid/refund lấy từ Payment Ledger; PSP statement và bank settlement là hai nguồn độc lập.
4. Tolerance prototype bằng 0 VND; mọi lệch tiền tạo case. Có thể cấu hình tolerance sau nếu nghiệp vụ phê duyệt.
5. File trùng được nhận biết bằng provider + batch_id và hash; dòng trùng bằng provider + external_ref + entry_type.

## 4. Checklist chuẩn BPMN

- Mỗi process có một start event và các end event rõ nghĩa.
- Gateway chia nhánh có điều kiện gắn trên outgoing sequence flow; nhánh default được đánh dấu.
- Message event dùng cho callback/statement; timer event dùng cho QR expiry, retry và SLA.
- Data object liên kết bằng data association, không dùng sequence flow.
- Pool black-box của PSP/ĐVVC vẫn đủ message flow; không mô tả quy trình nội bộ không biết của đối tác.
- Tên task theo cấu trúc động từ + đối tượng; tên event là điều đã xảy ra.

Tham chiếu: [OMG BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2/PDF).

