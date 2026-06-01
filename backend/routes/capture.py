import asyncio
import base64
import json
import logging

from fastapi import APIRouter, HTTPException

import providers
from config import settings
from models.solve import CaptureRequest, SecureEnvelopeRequest, SolveResponse
from services import cache, device, ensemble, hud, imaging, notes, sessions, tts, vision_ocr
from services.connection_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter()


def _resolve_provider(req_provider: str | None, session: dict) -> str:
    return req_provider or session.get("provider") or settings.default_provider


async def _push_hud(session: dict, result: dict) -> None:
    payload = hud.to_hud(result)
    if result.get("audio_base64"):
        payload["audio_base64"] = result["audio_base64"]
        payload["audio_mime"] = result["audio_mime"]
    channel = session.get("channel")
    if channel is not None:
        envelope = channel.encrypt(json.dumps(payload).encode(), "s2c")
        await manager.push(session["id"], {"type": "secure", "envelope": envelope})
    else:
        await manager.push(session["id"], payload)


async def _maybe_speak(result: dict, speak: bool) -> dict:
    if not speak or not tts.available():
        return result
    try:
        audio = await asyncio.to_thread(tts.synthesize, result["hud_text"])
        return {**result, "audio_base64": audio, "audio_mime": "audio/mp3"}
    except Exception as e:
        logger.warning("TTS skipped: %s", e)
        return result


async def run_solve(
    session: dict,
    image_base64: str,
    media_type: str,
    provider_override: str | None,
    speak: bool = False,
    translate_to: str | None = None,
    temperature_c: float | None = None,
    battery: float | None = None,
) -> dict:
    try:
        raw = base64.b64decode(image_base64)
    except Exception:
        raise HTTPException(status_code=422, detail="image_base64 is not valid base64")

    jpeg_bytes, image_b64 = await asyncio.to_thread(imaging.prepare, raw)

    fp = cache.fingerprint(jpeg_bytes)
    cached = cache.get(fp)
    if cached is not None:
        result = await _maybe_speak({**cached, "cached": True}, speak)
        sessions.set_last(session["id"], result)
        await _push_hud(session, result)
        return result

    device.heartbeat(session, battery, temperature_c)
    power_mode = device.mode(session)
    if power_mode == "critical" and device.too_soon(session):
        raise HTTPException(status_code=429, detail=device.directive_for(session))

    ocr_text = None
    if settings.enable_handwriting_ocr:
        try:
            ocr_text = await asyncio.to_thread(vision_ocr.extract_handwriting, jpeg_bytes)
        except Exception as e:
            logger.warning("handwriting OCR skipped: %s", e)

    mode = session.get("mode")
    translate_to = translate_to or session.get("translate_to")
    note_chunks = await asyncio.to_thread(notes.retrieve, session, ocr_text)
    provider_name = _resolve_provider(provider_override, session)

    if power_mode != "normal" and provider_name == "ensemble":
        provider_name = settings.default_provider
    if power_mode == "critical":
        speak = False

    device.register_capture(session)

    try:
        if provider_name == "ensemble":
            names = providers.available_providers()
            if not names:
                raise HTTPException(status_code=503, detail="no AI providers configured")
            result = await ensemble.solve_ensemble(
                image_b64,
                media_type="image/jpeg",
                ocr_text=ocr_text,
                mode=mode,
                provider_names=names,
                notes=note_chunks,
                translate_to=translate_to,
            )
        else:
            provider = providers.get_provider(provider_name)
            solution = await asyncio.to_thread(
                provider.solve,
                image_b64,
                media_type="image/jpeg",
                ocr_text=ocr_text,
                mode=mode,
                notes=note_chunks,
                translate_to=translate_to,
            )
            result = {**solution.model_dump(), "provider": provider_name, "cached": False}
    except HTTPException:
        raise
    except KeyError:
        raise HTTPException(status_code=422, detail=f"unknown provider: {provider_name}")
    except Exception as e:
        logger.error("solve failed (%s): %s", provider_name, e)
        raise HTTPException(status_code=502, detail="AI solve failed")

    result["uncertain"] = result["confidence"] < settings.confidence_threshold
    cache.put(fp, result)
    result = await _maybe_speak(result, speak)
    sessions.set_last(session["id"], result)
    await _push_hud(session, result)
    return result


@router.post("/solve", response_model=SolveResponse)
async def solve(req: CaptureRequest):
    session = sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown session_id; call /session/start first")
    return await run_solve(
        session,
        req.image_base64,
        req.media_type,
        req.provider,
        req.speak,
        req.translate_to,
        req.temperature_c,
        req.battery,
    )


@router.post("/secure")
async def solve_secure(req: SecureEnvelopeRequest):
    session = sessions.get(req.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown session_id; call /session/start first")

    channel = session.get("channel")
    if channel is None:
        raise HTTPException(status_code=409, detail="no secure channel; start session with client_public_key")

    try:
        plaintext = channel.decrypt(req.envelope, "c2s")
        inner = json.loads(plaintext)
    except Exception:
        raise HTTPException(status_code=400, detail="could not decrypt envelope")

    result = await run_solve(
        session,
        inner["image_base64"],
        inner.get("media_type", "image/jpeg"),
        inner.get("provider"),
        inner.get("speak", False),
        inner.get("translate_to"),
        inner.get("temperature_c"),
        inner.get("battery"),
    )

    response_envelope = channel.encrypt(json.dumps(result).encode(), "s2c")
    return {"envelope": response_envelope}
