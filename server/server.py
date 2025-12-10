import base64
from datetime import datetime, timezone
from fastapi import FastAPI, Query
from server.models import (
    RandomChunk, Heartbeat, RandomResponse, 
    StatusResponse, NodeInfo
)
from server import state

app = FastAPI(title="RNGaaS Central Server")


@app.post("/v1/nodes/{node_id}/chunks")
async def upload_chunk(node_id: str, chunk: RandomChunk):
    data = base64.b64decode(chunk.data_b64)
    total_bytes = await state.append_chunk(node_id, data)

    return {
        "status": "ok",
        "stored_bytes": len(data),
        "buffer_total_bytes": total_bytes
    }


@app.post("/v1/nodes/{node_id}/heartbeat")
async def heartbeat(node_id: str, hb: Heartbeat):
    await state.update_node_status(node_id, hb.dict())

    return {
        "status": "ok",
        "control": {
            "surplus_allowed": True,
            "target_state": "GENERATING",
            "max_buffer_bytes": 1048576
        }
    }


@app.get("/v1/nodes/{node_id}/config")
async def get_node_config(node_id: str):
    return {
        "node_id": node_id,
        "mode": "always_on",
        "upload_chunk_bytes": 32768,
        "heartbeat_interval_s": 5,
        "generation_enabled": True
    }


@app.get("/v1/random", response_model=RandomResponse)
async def get_random(
    bytes: int = Query(32, ge=1, le=1048576),
    format: str = Query("hex", pattern="^(hex|b64)$")
):
    data = await state.take_random_bytes(bytes)

    if format == "hex":
        value = data.hex()
    else:
        value = base64.b64encode(data).decode("ascii")

    return RandomResponse(
        bytes=len(data),
        format=format,
        value=value,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@app.get("/v1/status", response_model=StatusResponse)
async def get_status():
    stats = await state.get_global_stats()

    nodes = [
        NodeInfo(
            node_id=n["node_id"],
            status=n["status"],
            state=n["state"],
            buffer_bytes=n["buffer_bytes"],
            buffer_capacity=n["buffer_capacity"],
            last_seen=n["last_seen"]
        )
        for n in stats["nodes"]
    ]

    return StatusResponse(
        global_buffer_bytes=stats["global_buffer_bytes"],
        total_nodes=len(nodes),
        nodes=nodes
    )


# Run with: uvicorn server.server:app --reload
