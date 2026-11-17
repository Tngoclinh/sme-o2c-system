# Nguồn sơ đồ

- `bpmn_01_order_payment_fulfillment.mmd`: luồng chính đặt hàng, COD/QR, giữ hàng và bàn giao.
- `bpmn_02_failed_delivery_return.mmd`: ngoại lệ giao thất bại, RTO, đổi/trả và QC.
- `bpmn_03_reconciliation.mmd`: đối soát COD/QR và xử lý chênh lệch.

Các tệp Mermaid giúp review logic và theo dõi thay đổi bằng Git. Chúng **không thay thế file BPMN 2.0 chính thức**. Trước khi nộp, vẽ lại trong Camunda Modeler, Bizagi hoặc bpmn.io và lưu các file `.bpmn` tại đây. Tương tự, lưu file mô hình `.archimate` cùng ảnh PDF/SVG được xuất từ Archi.

