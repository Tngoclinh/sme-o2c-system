"""SQLite cho demo (ADR-02). Mỗi giao dịch dùng BEGIN IMMEDIATE."""
import os, sqlite3, tempfile
from contextlib import contextmanager

DB_PATH = os.environ.get("O2C_DB", os.path.join(tempfile.gettempdir(), "o2c_demo.db"))
SKU = "HOME-SET-01"

SCHEMA = """
CREATE TABLE stock_balances(sku TEXT PRIMARY KEY,
  available INT NOT NULL CHECK(available>=0), reserved INT NOT NULL CHECK(reserved>=0),
  picked INT NOT NULL CHECK(picked>=0), qc INT NOT NULL CHECK(qc>=0),
  quarantine INT NOT NULL CHECK(quarantine>=0));
CREATE TABLE stock_entries(id INTEGER PRIMARY KEY, op_key TEXT UNIQUE NOT NULL, order_id TEXT,
  sku TEXT, type TEXT, qty INT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TRIGGER se_no_update BEFORE UPDATE ON stock_entries BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER se_no_delete BEFORE DELETE ON stock_entries BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TABLE orders(id TEXT PRIMARY KEY, status TEXT, payment_method TEXT, item_subtotal INT,
  shipping_charge INT, grand_total INT, correlation_id TEXT, customer TEXT, address TEXT);
CREATE TABLE reservations(order_id TEXT, sku TEXT, qty INT, status TEXT, UNIQUE(order_id,sku));
CREATE TABLE payments(id TEXT PRIMARY KEY, order_id TEXT UNIQUE, method TEXT, status TEXT,
  amount INT, qr_ref TEXT UNIQUE, idem_key TEXT);
CREATE TABLE payment_entries(id INTEGER PRIMARY KEY, order_id TEXT, type TEXT, amount INT,
  provider TEXT, external_ref TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(provider,external_ref,type));
CREATE TRIGGER pe_no_update BEFORE UPDATE ON payment_entries BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TRIGGER pe_no_delete BEFORE DELETE ON payment_entries BEGIN SELECT RAISE(ABORT,'append-only'); END;
CREATE TABLE shipments(id TEXT PRIMARY KEY, order_id TEXT UNIQUE, status TEXT, tracking TEXT UNIQUE,
  cod_amount INT, failed_attempts INT DEFAULT 0);
CREATE TABLE shipment_events(id INTEGER PRIMARY KEY, shipment_id TEXT, event_id TEXT UNIQUE,
  raw_status TEXT, occurred_at TEXT, applied INT);
CREATE TABLE returns(id TEXT PRIMARY KEY, order_id TEXT, type TEXT, status TEXT, reason TEXT,
  UNIQUE(order_id,type));
CREATE TABLE inbox_events(provider TEXT, event_id TEXT, payload_hash TEXT, duplicates INT DEFAULT 0,
  UNIQUE(provider,event_id));
CREATE TABLE outbox_events(id INTEGER PRIMARY KEY, idem_key TEXT UNIQUE, order_id TEXT, status TEXT,
  attempts INT DEFAULT 0, last_error TEXT);
CREATE TABLE batches(provider TEXT, batch_id TEXT, status TEXT, UNIQUE(provider,batch_id));
CREATE TABLE cases(id INTEGER PRIMARY KEY, order_id TEXT, code TEXT, amount INT, status TEXT,
  owner TEXT, source_ref TEXT);
CREATE TABLE audit_log(id INTEGER PRIMARY KEY, actor TEXT, action TEXT, ref TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""

def connect():
    c = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
    c.row_factory = sqlite3.Row
    return c

@contextmanager
def tx():
    c = connect()
    try:
        c.execute("BEGIN IMMEDIATE")
        yield c
        c.execute("COMMIT")
    except BaseException:
        if c.in_transaction:
            c.execute("ROLLBACK")
        raise
    finally:
        c.close()

def reset(available=10):
    for p in (DB_PATH, DB_PATH + "-journal"):
        if os.path.exists(p):
            os.remove(p)
    c = connect()
    c.executescript(SCHEMA)
    c.execute("INSERT INTO stock_balances VALUES(?,?,0,0,0,0)", (SKU, available))
    c.close()
