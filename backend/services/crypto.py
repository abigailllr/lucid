import base64
import os
import struct

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_PAD_BLOCK = 256


def generate_keypair() -> tuple[X25519PrivateKey, str]:
    private_key = X25519PrivateKey.generate()
    public_raw = private_key.public_key().public_bytes_raw()
    return private_key, base64.b64encode(public_raw).decode()


def derive_root(server_private: X25519PrivateKey, client_public_b64: str) -> bytes:
    client_public = X25519PublicKey.from_public_bytes(base64.b64decode(client_public_b64))
    shared = server_private.exchange(client_public)
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"lucid-channel-root").derive(shared)


def _message_key(root: bytes, direction: str, counter: int) -> bytes:
    info = f"lucid-msg:{direction}:{counter}".encode()
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=info).derive(root)


def _pad(data: bytes) -> bytes:
    pad_len = (-(len(data) + 4)) % _PAD_BLOCK
    return struct.pack(">I", len(data)) + data + b"\x00" * pad_len


def _unpad(data: bytes) -> bytes:
    (length,) = struct.unpack(">I", data[:4])
    return data[4:4 + length]


_REPLAY_WINDOW = 256


class SecureChannel:
    def __init__(self, root: bytes) -> None:
        self._root = root
        self._send_counter = 0
        self._recv_high: dict[str, int] = {}
        self._recv_seen: dict[str, set[int]] = {}

    def _accept_counter(self, direction: str, n: int) -> None:
        high = self._recv_high.get(direction, -1)
        if n <= high - _REPLAY_WINDOW:
            raise ValueError("message counter too old (possible replay)")
        seen = self._recv_seen.setdefault(direction, set())
        if n in seen:
            raise ValueError("message counter already used (replay)")
        seen.add(n)
        if n > high:
            high = n
            self._recv_high[direction] = high
        seen.difference_update({c for c in seen if c <= high - _REPLAY_WINDOW})

    def encrypt(self, plaintext: bytes, direction: str) -> dict:
        counter = self._send_counter
        self._send_counter += 1
        key = _message_key(self._root, direction, counter)
        iv = os.urandom(12)
        ciphertext = AESGCM(key).encrypt(iv, _pad(plaintext), None)
        return {
            "n": counter,
            "iv": base64.b64encode(iv).decode(),
            "ct": base64.b64encode(ciphertext).decode(),
            "dir": direction,
        }

    def decrypt(self, envelope: dict, direction: str) -> bytes:
        n = int(envelope["n"])
        key = _message_key(self._root, direction, n)
        iv = base64.b64decode(envelope["iv"])
        ciphertext = base64.b64decode(envelope["ct"])
        plaintext = AESGCM(key).decrypt(iv, ciphertext, None)
        self._accept_counter(direction, n)
        return _unpad(plaintext)
