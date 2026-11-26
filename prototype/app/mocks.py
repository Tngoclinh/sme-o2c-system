"""Đối tác GIẢ LẬP: Đơn vị QR và ĐVVC. Khoá HMAC chỉ dành cho demo."""
import hashlib, hmac, json, os, time

SECRETS = {"qr": os.environ.get("QR_SECRET", "demo-qr-secret"),
           "carrier": os.environ.get("CARRIER_SECRET", "demo-carrier-secret")}

def sign(provider, body: bytes, ts: str):
    return hmac.new(SECRETS[provider].encode(), ts.encode() + b"." + body, hashlib.sha256).hexdigest()

def signed(provider, payload):
    body = json.dumps(payload).encode()
    ts = str(int(time.time()))
    return body, {"X-Timestamp": ts, "X-Signature": sign(provider, body, ts),
                  "Content-Type": "application/json"}

class Carrier:
    def __init__(self):
        self.reset()
    def reset(self):
        self.shipments, self.fail_next = {}, 0
    def create_shipment(self, idem_key, cod_amount):
        if self.fail_next > 0:
            self.fail_next -= 1
            raise ConnectionError("carrier 503")
        if idem_key not in self.shipments:
            self.shipments[idem_key] = {"tracking": f"VD-{len(self.shipments)+1:04d}",
                                        "cod_amount": cod_amount}
        return self.shipments[idem_key]

carrier = Carrier()
