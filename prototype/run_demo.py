"""Chạy cả hai kịch bản trên terminal:  python run_demo.py"""
import os, sys, tempfile
os.environ.setdefault("O2C_DB", os.path.join(tempfile.gettempdir(), "o2c_cli.db"))
from app.scenarios import run

ok = True
for name, title in [("e2e", "E2E: QR, giao thành công, đối soát"), ("exception", "NGOẠI LỆ: COD bị từ chối, chuyển hoàn")]:
    res = run(name); ok &= res["passed"]
    print(f"\n=== {title} ===")
    for i, s in enumerate(res["steps"], 1):
        print(f"[{'PASS' if s['ok'] else 'FAIL'}] {i}. {s['title']}")
        for c in s["checks"]:
            print(f"       {'✓' if c['ok'] else '✗'} {c['label']}: {c['actual']}" + ("" if c["ok"] else f" (mong đợi {c['expected']})"))
        if s["error"]: print("       ", s["error"])
        if s["order"]: o = s["order"]
    print(f"Truy vết: order_id={o['id']}  correlation_id={o['correlation_id']}")
sys.exit(0 if ok else 1)
