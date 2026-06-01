import io
import time

from PIL import Image

from config import settings

_store: dict[int, tuple[float, dict]] = {}


def fingerprint(image_bytes: bytes, size: int = 16) -> int:
    img = Image.open(io.BytesIO(image_bytes)).convert("L").resize((size, size), Image.LANCZOS)
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for i, pixel in enumerate(pixels):
        if pixel > avg:
            bits |= 1 << i
    return bits


def _distance(a: int, b: int) -> int:
    return bin(a ^ b).count("1")


def get(fp: int) -> dict | None:
    now = time.monotonic()
    for stored_hash, (stored_at, solution) in list(_store.items()):
        if now - stored_at > settings.cache_ttl_seconds:
            del _store[stored_hash]
            continue
        if _distance(fp, stored_hash) <= settings.cache_hash_distance:
            return solution
    return None


def put(fp: int, solution: dict) -> None:
    _store[fp] = (time.monotonic(), solution)


def purge_expired() -> int:
    now = time.monotonic()
    removed = 0
    for stored_hash, (stored_at, _) in list(_store.items()):
        if now - stored_at > settings.cache_ttl_seconds:
            del _store[stored_hash]
            removed += 1
    return removed
