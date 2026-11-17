# Prototype minh họa

## 1. Mục tiêu và non-goal

Prototype chứng minh hai lát cắt: (1) QR happy path từ order đến handover; (2) COD giao thất bại → RTO → QC → restock và reconciliation case. Không xây production UI, tích hợp NAPAS/GHN thật, HA cluster, general ledger hay hóa đơn điện tử.

Stack đề xuất: FastAPI modular monolith, SQLite cho demo (PostgreSQL là target), HTML/Bootstrap hoặc React tối giản, mock PSP và mock Carrier, scheduler cho outbox. API contract theo OpenAPI; OpenAPI là mô tả giao diện HTTP độc lập ngôn ngữ theo [OpenAPI Specification](https://spec.openapis.org/oas/v3.1).

## 2. Module và dữ liệu tối thiểu

| Module | Bảng/aggregate chính | Invariant |
|---|---|---|
| Order | orders, order_lines | total = sum(line); transition hợp lệ |
| Inventory | stock_balances, reservations, stock_entries | không âm; entry append-only |
| Payment | payments, payment_entries | external_ref unique theo provider |
| Shipping | shipments, shipment_events | event unique; state không rollback bởi event cũ |
| Return | returns, return_items, qc_results | restock chỉ sau QC pass |
| Reconciliation | statements, statement_lines, cases | batch/hash unique; adjustment có reason/actor |
| Integration | inbox_events, outbox_events | idempotency key unique |

Mọi bảng nghiệp vụ có `id`, `created_at`, `updated_at/version`; event/ledger có `correlation_id`, `source`, `external_ref`.

## 3. API catalog

### 3.1 Endpoint

| Method/path | Role | Request chính | Success | Lỗi chính |
|---|---|---|---|---|
| `POST /api/orders` | Customer/CS | customer, address, lines, payment_method | 201 Order | 400 validation, 409 out-of-stock |
| `GET /api/orders/{id}` | Customer/CS | path id | 200 OrderDetail | 403/404 |
| `POST /api/orders/{id}/cancel` | Customer/CS | reason | 200 | 409 invalid state |
| `POST /api/orders/{id}/payments/qr-intents` | Customer | idempotency key | 201 QR intent | 409 state |
| `POST /api/webhooks/psp` | PSP | event_id, ref, amount, status, signature | 200 accepted/duplicate | 401 signature, 422 mapping |
| `POST /api/orders/{id}/fulfill` | Warehouse | picked lines | 202 shipment pending | 403/409 |
| `POST /api/webhooks/carrier` | Carrier | event_id, tracking, status, occurred_at | 200 | 401/422 |
| `POST /api/returns` | Customer/CS | order_id, type, lines, reason | 201 RMA | 409 ineligible |
| `POST /api/returns/{id}/receive` | Warehouse | tracking, received lines | 200 | 409 duplicate/mismatch |
| `POST /api/returns/{id}/qc` | Warehouse | item results, disposition | 200 | 409 state |
| `POST /api/payments/{id}/refunds` | Accountant | amount, return_id, reason | 202 | 403/409/422 |
| `POST /api/reconciliation/batches` | Accountant | provider, batch_id, file | 202 | 409 duplicate, 422 schema |
| `GET /api/reconciliation/cases` | Accountant/Owner | status, aging | 200 paged list | 403 |
| `POST /api/reconciliation/cases/{id}/resolve` | Accountant | resolution, evidence, adjustment | 200 | 403/409 |
| `GET /api/reports/o2c` | Owner/Accountant | date range | 200 metrics | 403 |
| `GET /health` | Public/internal | — | 200 | 503 dependency |

### 3.2 Ví dụ tạo đơn

```json
{
  "customer": {"name": "Nguyen An", "phone": "0900000000"},
  "shipping_address": {"line1": "1 Dai Co Viet", "city": "Ha Noi"},
  "payment_method": "QR",
  "lines": [{"sku": "TSHIRT-BLACK-M", "quantity": 2, "unit_price": 150000}]
}
```

```json
{
  "id": "ord_001",
  "status": "PENDING_PAYMENT",
  "payment_status": "PENDING",
  "reservation_id": "res_001",
  "total": 300000,
  "currency": "VND",
  "correlation_id": "cor_001"
}
```

### 3.3 Error contract

```json
{
  "error": {
    "code": "INVENTORY_INSUFFICIENT",
    "message": "Không đủ tồn khả dụng cho SKU TSHIRT-BLACK-M",
    "details": {"sku": "TSHIRT-BLACK-M", "requested": 2, "available": 1},
    "correlation_id": "cor_001"
  }
}
```

Quy ước: 400 input sai; 401 chưa/xác thực callback sai; 403 thiếu quyền; 404 không tồn tại hoặc không được thấy; 409 xung đột state/idempotency/tồn; 422 payload đúng JSON nhưng sai nghiệp vụ/mapping; 429 rate limit; 500 lỗi nội bộ; 503 phụ thuộc không sẵn sàng. Không trả stack trace hay PII trong lỗi.

## 4. Mock UI

| Màn hình | Vai trò | Thành phần bắt buộc |
|---|---|---|
| Dashboard O2C | Owner | orders, delivered/failure/RTO/return rate, COD aging, QR settled, open cases |
| Order detail | CS/Warehouse | timeline riêng Order/Payment/Shipment/Return; correlation/external refs; actions theo state |
| Inventory | Warehouse | on-hand/available/reserved/QC/quarantine và stock-entry history |
| Return & QC | CS/Warehouse | eligibility, RMA, scan tracking, item QC, restock/quarantine/exchange |
| Reconciliation workbench | Accountant | upload batch, match summary, case filters, evidence, resolve/adjust approval |
| Integration monitor | IT | inbox/outbox status, retry count, last error, replay action có quyền |

UI không gộp một badge duy nhất cho toàn bộ order; hiển thị bốn badge Order, Payment, Shipment và Return để tránh trạng thái mâu thuẫn.

## 5. Kịch bản demo

### DEMO-01 — QR happy path

1. Seed SKU quantity 10; tạo order quantity 2 bằng QR.
2. Kiểm tra Order `PENDING_PAYMENT`, Reservation `ACTIVE`, available còn 8.
3. Mở QR intent có amount 300000 và reference `ord_001`.
4. Mock PSP gửi callback hợp lệ hai lần; UI cho thấy Payment `PAID` và chỉ một PaymentEntry có hiệu lực.
5. Kho fulfill; outbox gọi mock carrier; shipment có tracking và `HANDED_OVER`; reservation `COMMITTED`.
6. Import PSP statement + bank settlement khớp; batch `MATCHED`, không có case.

### DEMO-02 — COD thất bại/RTO và chênh lệch

1. Tạo COD order, fulfill, expected COD 300000.
2. Carrier gửi `delivery_failed` hai lần; lần đầu retry, lần hai `RETURNING`; gửi lặp event lần hai để chứng minh idempotency.
3. Kho nhận RTO, QC pass; một StockEntry `RETURN_TO_QC` và một `RESTOCK`; COD expected đóng `UNCOLLECTED`.
4. Import carrier statement có phí hoàn sai 20000; engine tạo `ReconciliationCase WRONG_RETURN_FEE`.
5. Kế toán đính chứng từ và resolve bằng adjustment được phê duyệt; dashboard cập nhật case closed.

## 6. Security và dữ liệu demo

- Role: `customer`, `cs`, `warehouse`, `accountant`, `owner`, `it_admin`.
- Kiểm tra object/function authorization theo OWASP API Security Top 10 2023; CS không được adjustment, kho không được refund, customer chỉ thấy order của mình.
- Callback mock dùng HMAC header + timestamp; secret trong environment; test replay và signature sai.
- Dữ liệu demo là giả, không dùng số điện thoại/địa chỉ thật; log mask phone/address/token.

## 7. Acceptance checklist

- Swagger/OpenAPI mở được; ví dụ request chạy được.
- DEMO-01 và DEMO-02 có ảnh/video/log và ID truy vết.
- TC-02, TC-03, TC-05, TC-06, TC-07 pass tự động.
- Balance inventory/payment khớp trước và sau từng demo.
- Có hướng dẫn reset seed data; không cần production deployment.

