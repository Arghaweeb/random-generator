from datetime import datetime, timezone


class HealthTester:
    def __init__(self):
        self.bit_balance = 0.5
        self.last_updated = datetime.now(timezone.utc).isoformat()

    def update(self, data: bytes) -> None:
        if not data:
            return

        total_bits = len(data) * 8
        ones = sum(bin(byte).count('1') for byte in data)
        self.bit_balance = ones / total_bits if total_bits > 0 else 0.5
        self.last_updated = datetime.now(timezone.utc).isoformat()

    def current_status(self) -> dict:
        ok = 0.45 <= self.bit_balance <= 0.55
        return {
            "ok": ok,
            "bit_balance": self.bit_balance,
            "min_entropy_per_bit": 0.95 if ok else 0.8,
            "last_updated": self.last_updated
        }
