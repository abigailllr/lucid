import base64
from functools import lru_cache

from config import settings
from .base import LUCID_SYSTEM, LucidSolution, build_user_text

NAME = "gemini"


def available() -> bool:
    return bool(settings.gemini_api_key)


@lru_cache(maxsize=1)
def _model():
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    return genai.GenerativeModel(settings.gemini_model, system_instruction=LUCID_SYSTEM)


def solve(
    image_base64: str,
    *,
    media_type: str,
    ocr_text: str | None,
    mode: str | None,
    peer_answers: list[dict] | None = None,
    notes: list[str] | None = None,
    translate_to: str | None = None,
) -> LucidSolution:
    image_part = {"mime_type": media_type, "data": base64.b64decode(image_base64)}
    response = _model().generate_content(
        [build_user_text(ocr_text, mode, peer_answers, notes, translate_to), image_part],
        generation_config={"response_mime_type": "application/json", "response_schema": LucidSolution},
    )
    return LucidSolution.model_validate_json(response.text)
