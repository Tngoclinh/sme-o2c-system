"""Hai kịch bản demo. Mỗi bước gọi API thật (in-process) và tự kiểm tra kết quả."""
import threading
from fastapi.testclient import TestClient
from . import db, mocks
from .main import app

_lock = threading.Lock()
SKU = db.SKU

class Runner:
    def __init__(self):
        self.client, self.steps, self.order_id = TestClient(app), [], None

    def call(self, method, path, role=None, json=None, hook=None, headers=None):
        h = dict(headers or {})
        if hook:
            body, h = mocks.signed(hook, json)
            r = self.client.request(method, path, content=body, headers=h)
        else:
            if role:
                h["X-Role"] = role
            r = self.client.request(method, path, json=json, headers=h)
        self.calls.append({"request": f"{method} {path}", "actor": role or f"{hook} (webhook)",
                           "body": json, "status": r.status_code, "response": r.json()})
        return r.status_code, r.json()

    def step(self, title, actor, fn):
        self.calls, checks = [], []
        def check(label, actual, expected):
            checks.append({"label": label, "expected": expected, "actual": actual, "ok": actual == expected})
        error = None
        try:
            fn(check)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
        ok = error is None and all(c["ok"] for c in checks)
        order = self.client.get(f"/api/orders/{self.order_id}", headers={"X-Role": "owner"}).json() if self.order_id else None
        stock = self.client.get(f"/api/inventory/{SKU}", headers={"X-Role": "owner"}).json()
        self.steps.append({"title": title, "actor": actor, "ok": ok, "error": error, "checks": checks,
                           "calls": self.calls, "order": order, "stock": stock})
        if not ok:
            raise StopIteration

    def get_order(self):
        return self.call("GET", f"/api/orders/{self.order_id}", "cs")[1]

    def stock(self):
        return self.call("GET", f"/api/inventory/{SKU}", "warehouse")[1]

    def create(self, method):
        def fn(check):
            code, o = self.call("POST", "/api/orders", "customer", {
                "customer": {"name": "Khach Demo", "phone": "0900000000"},
                "shipping_address": {"line1": "Dia chi gia", "city": "Ha Noi"},
                "payment_method": method, "customer_shipping_charge": 20000,
                "lines": [{"sku": SKU, "quantity": 2}]})
            self.order_id = o["id"]
            check("HTTP", code, 201)
            check("Tổng đơn = 280.000 + 20.000", o["grand_total"], 300000)
            check("Order", o["status"], "PENDING_PAYMENT" if method == "QR" else "CONFIRMED")
            check("Reservation", o["reservations"][0]["status"], "ACTIVE")
            s = self.stock()
            check("Tồn khả dụng", s["available"], 8)
            check("Tồn đang giữ", s["reserved"], 2)
        return fn

    def ship(self, cod, fail_first=False):
        oid = lambda: self.order_id
        def pack(check):
            code, o = self.call("POST", f"/api/orders/{oid()}/fulfill", "warehouse",
                                {"picked_lines": [{"sku": SKU, "quantity": 2}]})
            check("HTTP 202 Accepted", code, 202)
            check("Shipment chờ worker", o["shipment"]["status"], "PENDING")
            check("COD gửi ĐVVC", o["shipment"]["cod_amount"], cod)
        self.step("Kho lấy và đóng gói, lưu yêu cầu vận đơn vào outbox", "Nhân viên kho", pack)
        def send(check):
            if fail_first:
                mocks.carrier.fail_next = 1
                r = self.call("POST", "/api/worker/run", "it_admin")[1]["processed"][0]
                check("Lần 1: ĐVVC lỗi, yêu cầu vẫn chờ", r["status"], "PENDING")
            r = self.call("POST", "/api/worker/run", "it_admin")[1]["processed"][0]
            check("Gửi thành công", r["status"], "SENT")
            check("Số lần gửi", r["attempts"], 2 if fail_first else 1)
            check("Số vận đơn phía ĐVVC", len(mocks.carrier.shipments), 1)
        self.step("Worker gửi yêu cầu tạo vận đơn" + (" (lần đầu ĐVVC lỗi 503)" if fail_first else ""), "Worker + ĐVVC", send)
        def hand(check):
            code, o = self.call("POST", f"/api/orders/{oid()}/handover", "warehouse")
            check("Shipment", o["shipment"]["status"], "HANDED_OVER")
            check("Reservation", o["reservations"][0]["status"], "COMMITTED")
            check("Tồn vật lý sau xuất", self.stock()["on_hand"], 8)
        self.step("Bàn giao kiện, ghi xuất kho", "Nhân viên kho", hand)

    def event(self, event_id, status, **extra):
        tracking = self.client.get(f"/api/orders/{self.order_id}", headers={"X-Role": "cs"}).json()["shipment"]["tracking"]
        payload = {"event_id": event_id, "tracking": tracking, "status": status,
                   "occurred_at": "2026-11-26T10:00:00+07:00", **extra}
        return self.call("POST", "/api/webhooks/carrier", json=payload, hook="carrier")

def e2e(r: Runner):
    r.step("Khách đặt 2 sản phẩm, chọn QR, hệ thống giữ hàng", "Khách hàng", r.create("QR"))
    ref = {}
    def intent(check):
        code, q = r.call("POST", f"/api/orders/{r.order_id}/payments/qr-intents", "customer",
                         headers={"Idempotency-Key": "demo-qr-1"})
        ref["v"] = q["qr_ref"]
        check("HTTP", code, 201); check("Số tiền QR", q["amount"], 300000); check("Phí QR", q["fee"], 0)
    r.step("Tạo QR đúng tổng đơn", "Khách hàng + Đơn vị QR", intent)
    def paid(check):
        p = {"event_id": "qr-evt-1", "ref": ref["v"], "amount": 300000, "status": "PAID"}
        a = r.call("POST", "/api/webhooks/qr-provider", json=p, hook="qr")[1]
        b = r.call("POST", "/api/webhooks/qr-provider", json=p, hook="qr")[1]
        o = r.get_order()
        check("Callback lần 1", a["result"], "accepted"); check("Callback lần 2", b["result"], "duplicate")
        check("Payment", o["payment"]["status"], "PAID"); check("Order", o["status"], "CONFIRMED")
        check("Số bút toán paid", sum(x["type"] == "paid" for x in o["payment_entries"]), 1)
    r.step("Đơn vị QR gửi callback hai lần, chỉ ghi tiền một lần", "Đơn vị QR", paid)
    r.ship(cod=0)
    def deliver(check):
        r.event("ship-1", "in_transit")
        r.event("ship-2", "delivered")
        late = r.event("ship-0", "in_transit")[1]
        o = r.get_order()
        check("Shipment giữ DELIVERED", o["shipment"]["status"], "DELIVERED")
        check("Sự kiện cũ đến muộn", late["result"], "stored_not_applied")
        check("Order", o["status"], "COMPLETED")
    r.step("Giao thành công, sự kiện cũ không làm lùi trạng thái", "ĐVVC", deliver)
    def recon(check):
        line = [{"ref": ref["v"], "amount": 300000}]
        code, b = r.call("POST", "/api/reconciliation/batches", "accountant",
                         {"provider": "qr", "batch_id": "QR-2026-11-26", "statement_lines": line, "bank_lines": line})
        check("HTTP", code, 202); check("Batch", b["status"], "MATCHED")
        check("Số case", len(r.call("GET", "/api/reconciliation/cases", "accountant")[1]["items"]), 0)
    r.step("Đối soát sổ thanh toán, bảng kê QR và tiền ngân hàng", "Kế toán", recon)

def exception(r: Runner):
    r.step("Khách đặt 2 sản phẩm, chọn COD, hệ thống giữ hàng", "Khách hàng", r.create("COD"))
    r.ship(cod=300000, fail_first=True)
    def refused(check):
        r.event("ship-1", "in_transit")
        a = r.event("ship-2", "delivery_refused")[1]
        b = r.event("ship-2", "delivery_refused")[1]
        o = r.get_order()
        check("Chuyển hoàn ngay", a["shipment_status"], "RETURNING"); check("Event gửi lặp", b["result"], "duplicate")
        check("Số lần giao thất bại", o["shipment"]["failed_attempts"], 1)
        check("Order chưa hoàn thành", o["status"], "FULFILLING")
        check("Hàng đang hoàn chưa được bán", r.stock()["available"], 8)
    r.step("NGOẠI LỆ: khách từ chối nhận hàng", "ĐVVC", refused)
    rma = {}
    def open_return(check):
        code, o = r.call("POST", "/api/returns", "cs", {"order_id": r.order_id, "type": "RTO", "reason": "Khách từ chối nhận"})
        rma.update(id=o["return"]["id"], tracking=o["shipment"]["tracking"])
        r.event("ship-3", "returned")
        check("HTTP", code, 201)
        check("ĐVVC báo đã hoàn, tồn bán được chưa tăng", r.stock()["available"], 8)
    r.step("CSKH mở hồ sơ chuyển hoàn", "CSKH + ĐVVC", open_return)
    def recv(check):
        body = {"tracking": rma["tracking"], "received_lines": [{"sku": SKU, "quantity": 2}]}
        a = r.call("POST", f"/api/returns/{rma['id']}/receive", "warehouse", body)[0]
        b, err = r.call("POST", f"/api/returns/{rma['id']}/receive", "warehouse", body)
        o, s = r.get_order(), r.stock()
        check("Quét lần 1", a, 200); check("Quét lần 2 bị chặn", b, 409)
        check("Mã lỗi", err["error"]["code"], "DUPLICATE_RECEIVE")
        check("Số dòng RETURN_TO_QC", sum(x["type"] == "RETURN_TO_QC" for x in o["stock_entries"]), 1)
        check("Chờ QC", s["qc"], 2); check("Tồn bán được chưa tăng", s["available"], 8)
    r.step("Kho nhận kiện hoàn, quét hai lần", "Nhân viên kho", recv)
    def do_qc(check):
        code, o = r.call("POST", f"/api/returns/{rma['id']}/qc", "warehouse", {"result": "PASS"})
        s = r.stock()
        check("Số dòng RESTOCK", sum(x["type"] == "RESTOCK" for x in o["stock_entries"]), 1)
        check("Tồn bán được", s["available"], 10); check("Chờ QC", s["qc"], 0)
        check("Payment", o["payment"]["status"], "UNCOLLECTED"); check("Order", o["status"], "CANCELLED")
        check("Hồ sơ hoàn", o["return"]["status"], "CLOSED")
        check("Không có tiền collected", any(x["type"] == "collected" for x in o["payment_entries"]), False)
    r.step("QC đạt, nhập lại kho, đóng COD là chưa thu", "Nhân viên kho", do_qc)

SCENARIOS = {"e2e": e2e, "exception": exception}

def run(name):
    with _lock:
        db.reset(); mocks.carrier.reset()
        r = Runner()
        try:
            SCENARIOS[name](r)
        except StopIteration:
            pass
        return {"scenario": name, "passed": all(s["ok"] for s in r.steps), "steps": r.steps}
