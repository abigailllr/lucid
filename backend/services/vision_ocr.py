import logging
from functools import lru_cache

from config import settings

logger = logging.getLogger(__name__)

# Handwriting from a camera frame -> Cloud Vision DOCUMENT_TEXT_DETECTION.
# (ML Kit Digital Ink only takes pen strokes, not photos, so it does not fit here.)
_HANDWRITING_HINT = "en-t-i0-handwrit"


@lru_cache(maxsize=1)
def _client():
    from google.cloud import vision

    return vision.ImageAnnotatorClient.from_service_account_file(
        settings.google_vision_credentials_path
    )


def extract_handwriting(image_bytes: bytes) -> str:
    from google.cloud import vision

    image = vision.Image(content=image_bytes)
    context = vision.ImageContext(language_hints=[_HANDWRITING_HINT])
    response = _client().document_text_detection(image=image, image_context=context)
    if response.error.message:
        raise RuntimeError(response.error.message)
    return response.full_text_annotation.text.strip()
