import os, tempfile
os.environ["O2C_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
import pytest
from fastapi.testclient import TestClient
from app import db, mocks, scenarios
from app.main import app

@pytest.fixture
def r():
    db.reset(); mocks.carrier.reset()
    x = scenarios.Runner(); x.calls = []
    return x

def order(r, method="COD", qty=2):
    code, body = r.call("POST", "/api/orders", "customer", {"customer": {}, "shipping_address": {},
        "payment_method": method, "customer_shipping_charge": 20000, "lines": [{"sku": db.SKU, "quantity": qty}]})
    r.order_id = body.get("id")
    return code, body

def shipped(r):
    order(r); r.ship(cod=300000)

@pytest.mark.parametrize("name", ["e2e", "exception"])
def test_scenario(name):
    res = scenarios.run(name)
    assert res["passed"], [s for s in res["steps"] if not s["ok"]]
    assert len(res["steps"]) == 8

def test_out_of_stock_rolls_back(r):
    code, body = order(r, qty=11)
    assert code == 409 and body["error"]["code"] == "INVENTORY_INSUFFICIENT"
    assert r.stock()["available"] == 10
    c = db.connect(); assert c.execute("SELECT count(*) FROM orders").fetchone()[0] == 0

def test_cs_cannot_fulfill_and_is_audited(r):
    order(r)
    code, _ = r.call("POST", f"/api/orders/{r.order_id}/fulfill", "cs", {"picked_lines": []})
    assert code == 403 and r.stock()["reserved"] == 2
    c = db.connect(); assert c.execute("SELECT count(*) FROM audit_log WHERE action='DENIED'").fetchone()[0] == 1

def test_bad_signature(r):
    res = r.client.post("/api/webhooks/qr-provider", content=b"{}", headers={"X-Timestamp": "0", "X-Signature": "x"})
    assert res.status_code == 401

def test_wrong_qr_amount_can_be_resent(r):
    order(r, "QR")
    ref = r.call("POST", f"/api/orders/{r.order_id}/payments/qr-intents", "customer", headers={"Idempotency-Key": "k"})[1]["qr_ref"]
    p = {"event_id": "e1", "ref": ref, "amount": 1, "status": "PAID"}
    assert r.call("POST", "/api/webhooks/qr-provider", json=p, hook="qr")[0] == 422
    assert r.get_order()["payment"]["status"] == "PENDING"

def test_unpaid_qr_cannot_fulfill(r):
    order(r, "QR")
    assert r.call("POST", f"/api/orders/{r.order_id}/fulfill", "warehouse",
                  {"picked_lines": [{"sku": db.SKU, "quantity": 2}]})[0] == 409

def test_two_failed_attempts_then_rto_and_qc_fail(r):
    shipped(r)
    assert r.event("a", "delivery_failed")[1]["shipment_status"] == "FAILED"
    assert r.event("b", "delivery_failed")[1]["shipment_status"] == "RETURNING"
    o = r.call("POST", "/api/returns", "cs", {"order_id": r.order_id, "type": "RTO", "reason": "het luot"})[1]
    rid = o["return"]["id"]
    assert r.call("POST", f"/api/returns/{rid}/qc", "warehouse", {"result": "PASS"})[0] == 409  # chưa nhận
    r.call("POST", f"/api/returns/{rid}/receive", "warehouse",
           {"tracking": o["shipment"]["tracking"], "received_lines": [{"sku": db.SKU, "quantity": 2}]})
    assert r.call("POST", f"/api/returns/{rid}/qc", "warehouse", {"result": "FAIL"})[0] == 200
    s = r.stock(); assert (s["available"], s["quarantine"]) == (8, 2)
    assert r.call("POST", f"/api/returns/{rid}/qc", "warehouse", {"result": "PASS"})[0] == 409

def test_ledger_is_append_only(r):
    order(r)
    for sql in ("UPDATE stock_entries SET qty=0", "DELETE FROM payment_entries"):
        with pytest.raises(Exception, match="append-only"):
            db.connect().execute(sql)
