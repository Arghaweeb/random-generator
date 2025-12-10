import asyncio
from datetime import datetime, timezone

global_buffer = bytearray()
node_buffers: dict[str, bytearray] = {}
node_status: dict[str, dict] = {}

_lock = asyncio.Lock()


async def append_chunk(node_id: str, data: bytes) -> int:
    async with _lock:
        global global_buffer
        global_buffer.extend(data)

        if node_id not in node_buffers:
            node_buffers[node_id] = bytearray()
        node_buffers[node_id].extend(data)

        return len(global_buffer)


async def take_random_bytes(size: int) -> bytes:
    async with _lock:
        global global_buffer
        if len(global_buffer) < size:
            size = len(global_buffer)
        if size == 0:
            return b""
        result = bytes(global_buffer[:size])
        global_buffer = global_buffer[size:]
        return result


async def update_node_status(node_id: str, heartbeat_data: dict) -> None:
    async with _lock:
        node_status[node_id] = {
            **heartbeat_data,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }


async def get_global_stats() -> dict:
    async with _lock:
        return {
            "global_buffer_bytes": len(global_buffer),
            "node_buffers": {nid: len(buf) for nid, buf in node_buffers.items()},
            "nodes": list(node_status.values())
        }
