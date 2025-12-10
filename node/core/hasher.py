import hashlib


class Hasher:
    def __init__(self, hash_alg: str = "sha256"):
        self.hash_alg = hash_alg
        self.block_size = 32

    def condition(self, entropy: bytes) -> bytes:
        digests = []
        for i in range(0, len(entropy), self.block_size):
            block = entropy[i:i + self.block_size]
            h = hashlib.new(self.hash_alg)
            h.update(block)
            digests.append(h.digest())
        return b"".join(digests)
