from pydantic import BaseModel
from typing import Optional


class RandomChunk(BaseModel):
    node_id: str
    chunk_id: str
    sequence: int
    created_at: str
    length_bytes: int
    entropy_source: str
    conditioner: str
    data_b64: str
    health: dict


class Heartbeat(BaseModel):
    node_id: str
    timestamp: str
    status: str
    state: str
    mode: str
    buffer_bytes: int
    buffer_capacity: int
    last_error: Optional[str] = None


class RandomResponse(BaseModel):
    bytes: int
    format: str
    value: str
    timestamp: str


class NodeInfo(BaseModel):
    node_id: str
    status: str
    state: str
    buffer_bytes: int
    buffer_capacity: int
    last_seen: str


class StatusResponse(BaseModel):
    global_buffer_bytes: int
    total_nodes: int
    nodes: list[NodeInfo]
