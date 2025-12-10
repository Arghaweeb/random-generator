import base64
import requests
from datetime import datetime, timezone


class UplinkClient:
    def __init__(self, server_url: str, api_key: str, node_id: str):
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.node_id = node_id
        self.headers = {"X-API-Key": api_key}

    def send_chunk(self, chunk: bytes, health: dict, seq: int) -> None:
        payload = {
            "node_id": self.node_id,
            "chunk_id": f"{self.node_id}-{seq}",
            "sequence": seq,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "length_bytes": len(chunk),
            "entropy_source": "os.urandom",
            "conditioner": "sha256",
            "data_b64": base64.b64encode(chunk).decode("ascii"),
            "health": health
        }
        url = f"{self.server_url}/v1/nodes/{self.node_id}/chunks"
        requests.post(url, json=payload, headers=self.headers, timeout=10)

    def send_heartbeat(self, buffer_stats: dict, health: dict, control_state: str) -> dict | None:
        payload = {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "ok" if health.get("ok") else "degraded",
            "state": control_state,
            "mode": "always_on",
            "buffer_bytes": buffer_stats.get("bytes_available", 0),
            "buffer_capacity": buffer_stats.get("capacity", 0),
            "last_error": None
        }
        url = f"{self.server_url}/v1/nodes/{self.node_id}/heartbeat"
        try:
            resp = requests.post(url, json=payload, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("control")
        except Exception:
            return None
