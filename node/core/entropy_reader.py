import os


class EntropyReader:
    def __init__(self, chunk_size: int = 4096):
        self.chunk_size = chunk_size

    def read_chunk(self) -> bytes:
        return os.urandom(self.chunk_size)
