import threading


class RandomBuffer:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = bytearray()
        self.lock = threading.Lock()

    def append(self, data: bytes) -> None:
        with self.lock:
            self.buffer.extend(data)
            if len(self.buffer) > self.capacity:
                self.buffer = self.buffer[-self.capacity:]

    def take_chunk(self, size: int) -> bytes | None:
        with self.lock:
            if len(self.buffer) < size:
                return None
            chunk = bytes(self.buffer[:size])
            self.buffer = self.buffer[size:]
            return chunk

    def stats(self) -> dict:
        with self.lock:
            return {
                "bytes_available": len(self.buffer),
                "capacity": self.capacity
            }
