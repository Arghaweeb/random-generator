import pytest
from node.core.random_buffer import RandomBuffer
from node.core.hasher import Hasher


def test_random_buffer_append_take():
    buf = RandomBuffer(capacity=100)
    
    buf.append(b"hello")
    assert buf.stats()["bytes_available"] == 5
    
    chunk = buf.take_chunk(3)
    assert chunk == b"hel"
    assert buf.stats()["bytes_available"] == 2
    
    chunk = buf.take_chunk(10)
    assert chunk is None


def test_random_buffer_capacity():
    buf = RandomBuffer(capacity=10)
    
    buf.append(b"x" * 15)
    assert buf.stats()["bytes_available"] == 10


def test_hasher_condition():
    hasher = Hasher()
    
    entropy = b"x" * 64
    conditioned = hasher.condition(entropy)
    
    assert len(conditioned) == 64
    
    entropy = b"x" * 100
    conditioned = hasher.condition(entropy)
    expected_blocks = (100 + 31) // 32
    assert len(conditioned) == expected_blocks * 32
