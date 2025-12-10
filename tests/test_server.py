import base64
import pytest
from fastapi.testclient import TestClient
from server.server import app
from server import state

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    state.global_buffer.clear()
    state.node_buffers.clear()
    state.node_status.clear()


def test_upload_chunk():
    chunk_data = b"random_bytes_here"
    payload = {
        "node_id": "test-node",
        "chunk_id": "chunk-1",
        "sequence": 1,
        "created_at": "2025-01-01T00:00:00Z",
        "length_bytes": len(chunk_data),
        "entropy_source": "os.urandom",
        "conditioner": "sha256",
        "data_b64": base64.b64encode(chunk_data).decode("ascii"),
        "health": {"ok": True}
    }
    
    response = client.post("/v1/nodes/test-node/chunks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["stored_bytes"] == len(chunk_data)


def test_get_random():
    state.global_buffer.extend(b"x" * 100)
    
    response = client.get("/v1/random?bytes=32&format=hex")
    assert response.status_code == 200
    data = response.json()
    assert data["bytes"] == 32
    assert data["format"] == "hex"
    assert len(data["value"]) == 64


def test_get_status():
    response = client.get("/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert "global_buffer_bytes" in data
    assert "total_nodes" in data
    assert "nodes" in data
