from functools import lru_cache

from config import settings
from .base import LUCID_SYSTEM, LucidSolution, build_user_text

NAME = "anthropic"


def available() -> bool:
    return bool(settings.anthropic_api_key)


@lru_cache(maxsize=1)
def _client():
    import anthropic

    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


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
    response = _client().messages.parse(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=[{"type": "text", "text": LUCID_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        output_format=LucidSolution,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_base64}},
                {"type": "text", "text": build_user_text(ocr_text, mode, peer_answers, notes, translate_to)},
            ],
        }],
    )
    return response.parsed_output
