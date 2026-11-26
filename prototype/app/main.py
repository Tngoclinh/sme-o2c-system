"""Prototype Order-to-Cash: modular monolith thu nhỏ.
Vai trò lấy từ header X-Role: CHỈ để minh hoạ phân quyền, không phải xác thực thật."""
import hashlib, hmac, json, time, uuid
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, ValidationError

from . import db, mocks

app = FastAPI(title="O2C Prototype", version="0.1")
PRICES = {db.SKU: 140000}

class ApiError(Exception):
    def __init__(self, status, code, message, details=None):
        self.status, self.code, self.message, self.details = status, code, message, details or {}

def error_body(code, message, details):
    return {"error": {"code": code, "message": message, "details": details,
                      "correlation_id": new_id("cor")}}

@app.exception_handler(ApiError)
def on_api_error(_, e):
    return JSONResponse(error_body(e.code, e.message, e.details), e.status)

@app.exception_handler(RequestValidationError)
def on_invalid(_, e):
    fields = [".".join(map(str, x["loc"])) for x in e.errors()]
    return JSONResponse(error_body("VALIDATION_ERROR", "Dữ liệu đầu vào không hợp lệ", {"fields": fields}), 400)

def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def audit(c, actor, action, ref):
    c.execute("INSERT INTO audit_log(actor,action,ref) VALUES(?,?,?)", (actor, action, ref))

def role(*allowed):
    def check(request: Request, x_role: str = Header("")):
        if x_role not in allowed:
            with db.tx() as c:
                audit(c, x_role or "anonymous", "DENIED", request.url.path)
            raise ApiError(403, "FORBIDDEN", "Vai trò không được phép thực hiện thao tác này")
        return x_role
    return check

def one(c, sql, *args, missing="Không tìm thấy"):
    row = c.execute(sql, args).fetchone()
    if not row:
        raise ApiError(404, "NOT_FOUND", missing)
    return row

def require(ok, message, **details):
    if not ok:
        raise ApiError(409, "INVALID_STATE", message, details)

# ---------- Inventory: nơi duy nhất sửa tồn ----------
BUCKETS = {"available", "reserved", "picked", "qc", "quarantine"}

def move_stock(c, order_id, sku, qty, kind, src, dst, op_key):
    """Chuyển tồn giữa hai nhóm (None = ra/vào kho) và ghi StockEntry trong cùng giao dịch."""
    assert {src, dst} <= BUCKETS | {None}
    if src:
        n = c.execute(f"UPDATE stock_balances SET {src}={src}-? WHERE sku=? AND {src}>=?",
                      (qty, sku, qty)).rowcount
        if n != 1:
            raise ApiError(409, "INVENTORY_INSUFFICIENT", f"Không đủ tồn cho SKU {sku}",
                           {"sku": sku, "requested": qty})
    if dst:
        c.execute(f"UPDATE stock_balances SET {dst}={dst}+? WHERE sku=?", (qty, sku))
    c.execute("INSERT INTO stock_entries(op_key,order_id,sku,type,qty) VALUES(?,?,?,?,?)",
              (op_key, order_id, sku, kind, qty))

def lines_of(c, order_id):
    return c.execute("SELECT sku,qty FROM reservations WHERE order_id=? ORDER BY sku", (order_id,)).fetchall()

# ---------- Order ----------
class Line(BaseModel):
    sku: str
    quantity: int = Field(gt=0)

class OrderIn(BaseModel):
    customer: dict
    shipping_address: dict
    payment_method: Literal["QR", "COD"]
    customer_shipping_charge: int = Field(ge=0)
    lines: list[Line] = Field(min_length=1)

@app.post("/api/orders", status_code=201)
def create_order(body: OrderIn, actor=Depends(role("customer", "cs"))):
    qty = {}
    for ln in body.lines:
        if ln.sku not in PRICES:
            raise ApiError(400, "UNKNOWN_SKU", "SKU không tồn tại", {"sku": ln.sku})
        qty[ln.sku] = qty.get(ln.sku, 0) + ln.quantity
    subtotal = sum(PRICES[s] * q for s, q in qty.items())   # giá lấy từ server
    total = subtotal + body.customer_shipping_charge
    oid, pid, cor = new_id("ord"), new_id("pay"), new_id("cor")
    cod = body.payment_method == "COD"
    with db.tx() as c:
        c.execute("INSERT INTO orders VALUES(?,?,?,?,?,?,?,?,?)",
                  (oid, "CONFIRMED" if cod else "PENDING_PAYMENT", body.payment_method, subtotal,
                   body.customer_shipping_charge, total, cor,
                   json.dumps(body.customer), json.dumps(body.shipping_address)))
        for sku, q in sorted(qty.items()):
            move_stock(c, oid, sku, q, "RESERVE", "available", "reserved", f"{oid}:{sku}:RESERVE")
            c.execute("INSERT INTO reservations VALUES(?,?,?,'ACTIVE')", (oid, sku, q))
        c.execute("INSERT INTO payments(id,order_id,method,status,amount) VALUES(?,?,?,'PENDING',?)",
                  (pid, oid, body.payment_method, total))
        if cod:
            c.execute("INSERT INTO payment_entries(order_id,type,amount,provider,external_ref) "
                      "VALUES(?,'expected',?,'internal',?)", (oid, total, oid))
        audit(c, actor, "ORDER_CREATED", oid)
    return view(oid)

def view(oid):
    c = db.connect()
    try:
        o = dict(one(c, "SELECT * FROM orders WHERE id=?", oid, missing="Không tìm thấy đơn"))
        o.pop("customer"); o.pop("address")                  # không trả PII
        q = lambda sql: [dict(r) for r in c.execute(sql, (oid,))]
        first = lambda rows: rows[0] if rows else None
        o["payment"] = first(q("SELECT id,status,amount,qr_ref FROM payments WHERE order_id=?"))
        o["shipment"] = first(q("SELECT * FROM shipments WHERE order_id=?"))
        o["return"] = first(q("SELECT id,type,status,reason FROM returns WHERE order_id=?"))
        o["reservations"] = q("SELECT sku,qty,status FROM reservations WHERE order_id=?")
        o["stock_entries"] = q("SELECT type,sku,qty FROM stock_entries WHERE order_id=? ORDER BY id")
        o["payment_entries"] = q("SELECT type,amount,provider,external_ref FROM payment_entries WHERE order_id=? ORDER BY id")
        o["shipment_events"] = q("SELECT e.event_id,e.raw_status,e.applied FROM shipment_events e "
                                 "JOIN shipments s ON s.id=e.shipment_id WHERE s.order_id=? ORDER BY e.id")
        return o
    finally:
        c.close()

READERS = ("customer", "cs", "warehouse", "accountant", "owner")  # demo chưa kiểm quyền theo chủ đơn

@app.get("/api/orders/{oid}")
def get_order(oid: str, actor=Depends(role(*READERS))):
    return view(oid)

@app.get("/api/inventory/{sku}")
def inventory(sku: str, actor=Depends(role("warehouse", "owner"))):
    c = db.connect()
    try:
        b = dict(one(c, "SELECT * FROM stock_balances WHERE sku=?", sku))
        b["on_hand"] = sum(b[k] for k in BUCKETS)
        return b
    finally:
        c.close()

# ---------- Payment ----------
@app.post("/api/orders/{oid}/payments/qr-intents", status_code=201)
def qr_intent(oid: str, idempotency_key: str = Header(...), actor=Depends(role("customer"))):
    # Mock QR trả mã ngay trong tiến trình (ADR-03: bước lấy mã QR là đồng bộ).
    with db.tx() as c:
        o = one(c, "SELECT * FROM orders WHERE id=?", oid)
        p = one(c, "SELECT * FROM payments WHERE order_id=?", oid)
        require(o["payment_method"] == "QR" and o["status"] == "PENDING_PAYMENT", "Đơn không chờ thanh toán QR")
        if p["qr_ref"]:
            require(p["idem_key"] == idempotency_key, "Đơn đã có QR intent với khoá khác")
        else:
            c.execute("UPDATE payments SET qr_ref=?, idem_key=? WHERE id=?", (f"QR-{oid}", idempotency_key, p["id"]))
        return {"payment_id": p["id"], "qr_ref": f"QR-{oid}", "amount": p["amount"], "currency": "VND", "fee": 0}

async def verified_body(provider, request: Request):
    body = await request.body()
    ts, sig = request.headers.get("x-timestamp", ""), request.headers.get("x-signature", "")
    fresh = ts.isdigit() and abs(time.time() - int(ts)) <= 300
    if not fresh or not hmac.compare_digest(sig.encode(), mocks.sign(provider, body, ts).encode()):
        raise ApiError(401, "BAD_SIGNATURE", "Chữ ký hoặc thời điểm không hợp lệ")
    return body

def parse(model, body):
    try:
        return model.model_validate_json(body)
    except ValidationError:
        raise ApiError(422, "BAD_PAYLOAD", "Payload không đúng hợp đồng")

def seen_before(c, provider, event_id, body):
    """Inbox: ghi nhận và xử lý nằm trong cùng một giao dịch."""
    digest = hashlib.sha256(body).hexdigest()
    row = c.execute("SELECT payload_hash FROM inbox_events WHERE provider=? AND event_id=?",
                    (provider, event_id)).fetchone()
    if not row:
        c.execute("INSERT INTO inbox_events(provider,event_id,payload_hash) VALUES(?,?,?)",
                  (provider, event_id, digest))
        return False
    if row["payload_hash"] != digest:
        raise ApiError(409, "IDEMPOTENCY_CONFLICT", "Cùng event_id nhưng nội dung khác")
    c.execute("UPDATE inbox_events SET duplicates=duplicates+1 WHERE provider=? AND event_id=?",
              (provider, event_id))
    audit(c, provider, "DUPLICATE_EVENT", event_id)
    return True

class QrEvent(BaseModel):
    event_id: str
    ref: str
    amount: int
    status: Literal["PAID"]

@app.post("/api/webhooks/qr-provider")
async def qr_webhook(request: Request):
    body = await verified_body("qr", request)
    e = parse(QrEvent, body)
    with db.tx() as c:
        if seen_before(c, "qr", e.event_id, body):
            return {"result": "duplicate"}
        p = c.execute("SELECT * FROM payments WHERE qr_ref=?", (e.ref,)).fetchone()
        if not p or p["amount"] != e.amount:
            raise ApiError(422, "MAPPING_ERROR", "Sai mã tham chiếu hoặc số tiền")
        if p["status"] != "PENDING":
            return {"result": "ignored", "payment_status": p["status"]}
        c.execute("UPDATE payments SET status='PAID' WHERE id=?", (p["id"],))
        c.execute("UPDATE orders SET status='CONFIRMED' WHERE id=? AND status='PENDING_PAYMENT'", (p["order_id"],))
        c.execute("INSERT INTO payment_entries(order_id,type,amount,provider,external_ref) "
                  "VALUES(?,'paid',?,'qr',?)", (p["order_id"], e.amount, e.ref))
        audit(c, "qr", "PAYMENT_PAID", p["order_id"])
    return {"result": "accepted"}

# ---------- Fulfillment / Shipping ----------
class FulfillIn(BaseModel):
    picked_lines: list[Line]

@app.post("/api/orders/{oid}/fulfill", status_code=202)
def fulfill(oid: str, body: FulfillIn, actor=Depends(role("warehouse"))):
    with db.tx() as c:
        o = one(c, "SELECT * FROM orders WHERE id=?", oid)
        require(o["status"] == "CONFIRMED", "Chỉ đóng gói đơn đã xác nhận", status=o["status"])
        want = {r["sku"]: r["qty"] for r in lines_of(c, oid)}
        got = {ln.sku: ln.quantity for ln in body.picked_lines}
        require(want == got and len(got) == len(body.picked_lines), "Hàng lấy không khớp đơn")
        for sku, q in want.items():
            move_stock(c, oid, sku, q, "PICK", "reserved", "picked", f"{oid}:{sku}:PICK")
        c.execute("UPDATE orders SET status='FULFILLING' WHERE id=?", (oid,))
        cod = o["grand_total"] if o["payment_method"] == "COD" else 0
        c.execute("INSERT INTO shipments(id,order_id,status,cod_amount) VALUES(?,?,'PENDING',?)",
                  (new_id("shp"), oid, cod))
        c.execute("INSERT INTO outbox_events(idem_key,order_id,status) VALUES(?,?,'PENDING')",
                  (f"create-shipment:{oid}", oid))
        audit(c, actor, "FULFILL", oid)
    return view(oid)

MAX_ATTEMPTS = 5

@app.post("/api/worker/run")
def run_worker(actor=Depends(role("it_admin"))):
    """Một lượt của worker duy nhất (demo gọi tay để thấy retry; chưa có backoff)."""
    c = db.connect()
    jobs = c.execute("SELECT o.*, s.cod_amount FROM outbox_events o JOIN shipments s USING(order_id) "
                     "WHERE o.status='PENDING'").fetchall()
    c.close()
    out = []
    for j in jobs:
        n = j["attempts"] + 1
        try:                                     # gọi đối tác NGOÀI giao dịch DB
            r = mocks.carrier.create_shipment(j["idem_key"], j["cod_amount"])
        except ConnectionError as err:
            state = "FAILED" if n >= MAX_ATTEMPTS else "PENDING"
            with db.tx() as c:
                c.execute("UPDATE outbox_events SET attempts=?, last_error=?, status=? WHERE id=?",
                          (n, str(err), state, j["id"]))
            out.append({"order_id": j["order_id"], "status": state, "attempts": n, "error": str(err)})
            continue
        with db.tx() as c:
            c.execute("UPDATE shipments SET tracking=?, status='CREATED' WHERE order_id=?", (r["tracking"], j["order_id"]))
            c.execute("UPDATE outbox_events SET status='SENT', attempts=?, last_error=NULL WHERE id=?", (n, j["id"]))
        out.append({"order_id": j["order_id"], "status": "SENT", "attempts": n, "tracking": r["tracking"]})
    return {"processed": out}

@app.post("/api/orders/{oid}/handover")
def handover(oid: str, actor=Depends(role("warehouse"))):
    """Bổ sung so với API catalog: BPMN-01 bước 5 ghi xuất kho lúc bàn giao thực tế."""
    with db.tx() as c:
        s = one(c, "SELECT * FROM shipments WHERE order_id=?", oid)
        require(s["status"] == "CREATED", "Vận đơn chưa sẵn sàng bàn giao", status=s["status"])
        for r in lines_of(c, oid):
            move_stock(c, oid, r["sku"], r["qty"], "SHIP", "picked", None, f"{oid}:{r['sku']}:SHIP")
        c.execute("UPDATE reservations SET status='COMMITTED' WHERE order_id=?", (oid,))
        c.execute("UPDATE shipments SET status='HANDED_OVER' WHERE id=?", (s["id"],))
        audit(c, actor, "HANDOVER", oid)
    return view(oid)

class CarrierEvent(BaseModel):
    event_id: str
    tracking: str
    status: Literal["in_transit", "delivered", "delivery_failed", "delivery_refused", "returned"]
    occurred_at: str
    collected_amount: int | None = None

ALLOWED = {  # sự kiện -> trạng thái được phép chuyển từ đó
    "in_transit": {"HANDED_OVER", "FAILED"},
    "delivered": {"HANDED_OVER", "IN_TRANSIT", "FAILED"},
    "delivery_failed": {"HANDED_OVER", "IN_TRANSIT", "FAILED"},
    "delivery_refused": {"HANDED_OVER", "IN_TRANSIT", "FAILED"},
    "returned": {"RETURNING"},
}
MAX_DELIVERY = 2

@app.post("/api/webhooks/carrier")
async def carrier_webhook(request: Request):
    body = await verified_body("carrier", request)
    e = parse(CarrierEvent, body)
    with db.tx() as c:
        if seen_before(c, "carrier", e.event_id, body):
            return {"result": "duplicate"}
        s = c.execute("SELECT * FROM shipments WHERE tracking=?", (e.tracking,)).fetchone()
        if not s:
            raise ApiError(422, "MAPPING_ERROR", "Không tìm thấy mã vận đơn")
        ok = s["status"] in ALLOWED[e.status]
        c.execute("INSERT INTO shipment_events(shipment_id,event_id,raw_status,occurred_at,applied) "
                  "VALUES(?,?,?,?,?)", (s["id"], e.event_id, e.status, e.occurred_at, int(ok)))
        if not ok:                               # event cũ/sai thứ tự: lưu, không lùi trạng thái
            return {"result": "stored_not_applied", "shipment_status": s["status"]}
        attempts, new = s["failed_attempts"], None
        if e.status in ("delivery_failed", "delivery_refused"):
            attempts += 1
            # Khách từ chối = không đồng ý giao lại -> chuyển hoàn ngay (BPMN-02)
            new = "RETURNING" if e.status == "delivery_refused" or attempts >= MAX_DELIVERY else "FAILED"
        else:
            new = {"in_transit": "IN_TRANSIT", "delivered": "DELIVERED", "returned": "RETURNED"}[e.status]
        if e.status == "delivered":
            if s["cod_amount"]:
                if e.collected_amount != s["cod_amount"]:
                    raise ApiError(422, "COD_MISMATCH", "Số thu hộ khác COD; demo từ chối để xác minh")
                c.execute("INSERT INTO payment_entries(order_id,type,amount,provider,external_ref) "
                          "VALUES(?,'collected',?,'carrier',?)", (s["order_id"], e.collected_amount, e.tracking))
            c.execute("UPDATE orders SET status='COMPLETED' WHERE id=?", (s["order_id"],))
        c.execute("UPDATE shipments SET status=?, failed_attempts=? WHERE id=?", (new, attempts, s["id"]))
        audit(c, "carrier", f"SHIPMENT_{new}", s["order_id"])
    return {"result": "accepted", "shipment_status": new}

# ---------- Return & QC ----------
class ReturnIn(BaseModel):
    order_id: str
    type: Literal["RTO"]
    reason: str = Field(min_length=3)

@app.post("/api/returns", status_code=201)
def create_return(body: ReturnIn, actor=Depends(role("cs"))):
    rid = new_id("rma")
    with db.tx() as c:
        s = one(c, "SELECT * FROM shipments WHERE order_id=?", body.order_id)
        require(s["status"] in ("RETURNING", "RETURNED"), "Vận đơn không ở luồng chuyển hoàn", status=s["status"])
        require(not c.execute("SELECT 1 FROM returns WHERE order_id=? AND type='RTO'", (body.order_id,)).fetchone(),
                "Đã có hồ sơ chuyển hoàn")
        c.execute("INSERT INTO returns VALUES(?,?,'RTO','IN_TRANSIT',?)", (rid, body.order_id, body.reason))
        audit(c, actor, "RETURN_OPENED", body.order_id)
    return view(body.order_id)

class ReceiveIn(BaseModel):
    tracking: str
    received_lines: list[Line]

@app.post("/api/returns/{rid}/receive")
def receive(rid: str, body: ReceiveIn, actor=Depends(role("warehouse"))):
    with db.tx() as c:
        r = one(c, "SELECT * FROM returns WHERE id=?", rid)
        if r["status"] != "IN_TRANSIT":
            raise ApiError(409, "DUPLICATE_RECEIVE", "Kiện này đã được nhận", {"status": r["status"]})
        s = one(c, "SELECT * FROM shipments WHERE order_id=?", r["order_id"])
        want = {x["sku"]: x["qty"] for x in lines_of(c, r["order_id"])}
        got = {x.sku: x.quantity for x in body.received_lines}
        require(body.tracking == s["tracking"] and want == got and len(got) == len(body.received_lines),
                "Mã kiện hoặc hàng nhận không khớp")
        for sku, q in want.items():
            move_stock(c, r["order_id"], sku, q, "RETURN_TO_QC", None, "qc", f"{rid}:{sku}:RECEIVE")
        c.execute("UPDATE returns SET status='RECEIVED' WHERE id=?", (rid,))
        c.execute("UPDATE shipments SET status='RETURNED' WHERE id=?", (s["id"],))
        audit(c, actor, "RETURN_RECEIVED", r["order_id"])
    return view(r["order_id"])

class QcIn(BaseModel):
    result: Literal["PASS", "FAIL"]     # demo: một kết quả cho cả kiện
    note: str = ""

@app.post("/api/returns/{rid}/qc")
def qc(rid: str, body: QcIn, actor=Depends(role("warehouse"))):
    with db.tx() as c:
        r = one(c, "SELECT * FROM returns WHERE id=?", rid)
        require(r["status"] == "RECEIVED", "Phải thực nhận trước khi QC và chỉ QC một lần", status=r["status"])
        oid = r["order_id"]
        kind, dst = ("RESTOCK", "available") if body.result == "PASS" else ("QUARANTINE", "quarantine")
        for x in lines_of(c, oid):
            move_stock(c, oid, x["sku"], x["qty"], kind, "qc", dst, f"{rid}:{x['sku']}:QC")
        audit(c, actor, f"QC_{body.result}", oid)
        p = one(c, "SELECT * FROM payments WHERE order_id=?", oid)
        collected = c.execute("SELECT 1 FROM payment_entries WHERE order_id=? AND type='collected'", (oid,)).fetchone()
        if p["method"] == "COD" and not collected:
            c.execute("UPDATE payments SET status='UNCOLLECTED' WHERE id=?", (p["id"],))
            c.execute("UPDATE orders SET status='CANCELLED' WHERE id=?", (oid,))
            c.execute("UPDATE returns SET status='CLOSED' WHERE id=?", (rid,))
        else:   # đã có tiền: không tự đóng, chuyển kế toán xác minh
            c.execute("UPDATE returns SET status=? WHERE id=?", (f"QC_{body.result}ED", rid))
            c.execute("INSERT INTO cases(order_id,code,amount,status,owner,source_ref) "
                      "VALUES(?,'RETURN_NEEDS_VERIFY',?,'OPEN','accountant',?)", (oid, p["amount"], rid))
    return view(oid)

# ---------- Reconciliation (chỉ QR cho kịch bản E2E) ----------
class StatementLine(BaseModel):
    ref: str
    amount: int

class BatchIn(BaseModel):
    provider: Literal["qr"]
    batch_id: str
    statement_lines: list[StatementLine] = Field(min_length=1)
    bank_lines: list[StatementLine]

@app.post("/api/reconciliation/batches", status_code=202)
def reconcile(body: BatchIn, actor=Depends(role("accountant"))):
    """So PaymentEntry (paid) <-> bảng kê QR <-> ngân hàng, ghép theo mã, dung sai 0."""
    def totals(lines):
        out = {}
        for ln in lines:
            if ln.ref in out:
                raise ApiError(422, "DUPLICATE_LINE", "Trùng mã tham chiếu trong file", {"ref": ln.ref})
            out[ln.ref] = ln.amount
        return out
    st, bank = totals(body.statement_lines), totals(body.bank_lines)
    with db.tx() as c:
        if c.execute("SELECT 1 FROM batches WHERE provider=? AND batch_id=?", (body.provider, body.batch_id)).fetchone():
            raise ApiError(409, "DUPLICATE_BATCH", "Batch đã được nhập")
        results = []
        for ref in sorted(set(st) | set(bank)):   # demo chỉ xét mã xuất hiện trong file
            row = c.execute("SELECT order_id,amount FROM payment_entries WHERE type='paid' AND provider='qr' "
                            "AND external_ref=?", (ref,)).fetchone()
            ledger = row["amount"] if row else None
            ok = ledger is not None and ledger == st.get(ref) == bank.get(ref)
            results.append({"ref": ref, "ledger": ledger, "statement": st.get(ref), "bank": bank.get(ref), "matched": ok})
            if not ok:
                diff = abs((ledger or st.get(ref, 0)) - bank.get(ref, 0))
                c.execute("INSERT INTO cases(order_id,code,amount,status,owner,source_ref) "
                          "VALUES(?,'QR_MISMATCH',?,'OPEN','accountant',?)",
                          (row["order_id"] if row else None, diff, f"{body.batch_id}:{ref}"))
        status = "MATCHED" if all(r["matched"] for r in results) else "DISCREPANT"
        c.execute("INSERT INTO batches VALUES(?,?,?)", (body.provider, body.batch_id, status))
        audit(c, actor, f"BATCH_{status}", body.batch_id)
    return {"batch_id": body.batch_id, "status": status, "lines": results}

@app.get("/api/reconciliation/cases")
def list_cases(actor=Depends(role("accountant", "owner"))):
    c = db.connect()
    try:
        return {"items": [dict(r) for r in c.execute("SELECT * FROM cases ORDER BY id")]}
    finally:
        c.close()

@app.get("/health")
def health():
    try:
        c = db.connect(); c.execute("SELECT 1 FROM orders LIMIT 1"); c.close()
    except Exception:
        raise ApiError(503, "DB_UNAVAILABLE", "Chưa sẵn sàng")
    return {"status": "ok"}

# ---------- Trang demo ----------
@app.post("/demo/run/{name}")
def demo_run(name: Literal["e2e", "exception"]):
    """CHỈ cho demo: XOÁ dữ liệu rồi chạy kịch bản qua chính các API ở trên."""
    from .scenarios import run
    return run(name)

@app.get("/")
def index():
    return FileResponse(Path(__file__).parent.parent / "static" / "index.html")

if not Path(db.DB_PATH).exists():
    db.reset()
