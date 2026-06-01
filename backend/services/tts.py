import base64
from functools import lru_cache

from config import settings


def available() -> bool:
    return bool(settings.openai_api_key)


@lru_cache(maxsize=1)
def _client():
    from openai import OpenAI

    return OpenAI(api_key=settings.openai_api_key)


def synthesize(text: str) -> str:
    response = _client().audio.speech.create(
        model="tts-1",
        voice=settings.tts_voice,
        input=text,
        response_format="mp3",
    )
    return base64.b64encode(response.content).decode()
