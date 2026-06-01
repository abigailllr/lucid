from functools import lru_cache

from config import settings
from .base import LUCID_SYSTEM, LucidSolution, build_user_text

NAME = "ollama"


def available() -> bool:
    return settings.ollama_enabled


@lru_cache(maxsize=1)
def _client():
    from ollama import Client

    return Client(host=settings.ollama_host)


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
    response = _client().chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": LUCID_SYSTEM},
            {
                "role": "user",
                "content": build_user_text(ocr_text, mode, peer_answers, notes, translate_to),
                "images": [image_base64],
            },
        ],
        format=LucidSolution.model_json_schema(),
    )
    return LucidSolution.model_validate_json(response["message"]["content"])
