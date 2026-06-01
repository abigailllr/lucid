from functools import lru_cache

from config import settings
from .base import LUCID_SYSTEM, LucidSolution, build_user_text

NAME = "openai"


def available() -> bool:
    return bool(settings.openai_api_key)


@lru_cache(maxsize=1)
def _client():
    from openai import OpenAI

    return OpenAI(api_key=settings.openai_api_key)


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
    completion = _client().beta.chat.completions.parse(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": LUCID_SYSTEM},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": build_user_text(ocr_text, mode, peer_answers, notes, translate_to)},
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_base64}"}},
                ],
            },
        ],
        response_format=LucidSolution,
    )
    return completion.choices[0].message.parsed
