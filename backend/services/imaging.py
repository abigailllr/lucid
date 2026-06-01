import base64
import io

from PIL import Image

# Claude vision is sharpest when the long edge is <= 1568 px; larger just burns tokens.
_MAX_SIDE = 1568


def prepare(image_bytes: bytes) -> tuple[bytes, str]:
    """Downscale to Claude's optimal size and re-encode as clean JPEG.

    Returns (jpeg_bytes, base64_string) — bytes for hashing/OCR, base64 for the model.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((_MAX_SIDE, _MAX_SIDE), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88)
    data = buf.getvalue()
    return data, base64.b64encode(data).decode()
