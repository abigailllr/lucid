from fastapi import APIRouter

import providers
from services import tts

router = APIRouter()


@router.get("/")
async def health():
    return {
        "status": "ok",
        "providers": providers.available_providers(),
        "audio_output": tts.available(),
    }
