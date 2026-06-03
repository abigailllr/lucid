import base64
import io

from PIL import Image

_MAX_SIDE = 1568


def prepare(image_bytes: bytes) -> tuple[bytes, str]:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((_MAX_SIDE, _MAX_SIDE), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85, optimize=True)
    data = buf.getvalue()
    return data, base64.b64encode(data).decode()
