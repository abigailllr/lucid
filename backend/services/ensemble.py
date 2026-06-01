import asyncio
import logging

import providers
from providers.base import LucidSolution
from services import agreement

logger = logging.getLogger(__name__)

AGREEMENT_THRESHOLD = 0.82


async def _run(name, image_base64, media_type, ocr_text, mode, notes, translate_to, peer_answers=None):
    provider = providers.get_provider(name)
    solution = await asyncio.to_thread(
        provider.solve,
        image_base64,
        media_type=media_type,
        ocr_text=ocr_text,
        mode=mode,
        peer_answers=peer_answers,
        notes=notes,
        translate_to=translate_to,
    )
    return name, solution


def _collect(results) -> list[tuple[str, LucidSolution]]:
    collected = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning("provider failed in ensemble: %s", result)
            continue
        collected.append(result)
    return collected


def _texts(candidates: list[tuple[str, LucidSolution]]) -> list[str]:
    return [f"{name}: {sol.hud_text}. {sol.solution}" for name, sol in candidates]


def _build(winner: tuple[str, LucidSolution], candidates, agreement_score: float, debated: bool) -> dict:
    name, solution = winner
    return {
        **solution.model_dump(),
        "provider": "ensemble",
        "winner": name,
        "agreement": round(agreement_score, 3),
        "debated": debated,
        "candidates": [
            {"provider": n, "hud_text": s.hud_text, "confidence": s.confidence} for n, s in candidates
        ],
        "cached": False,
    }


async def solve_ensemble(
    image_base64: str,
    *,
    media_type: str,
    ocr_text,
    mode,
    provider_names: list[str],
    notes=None,
    translate_to=None,
) -> dict:
    first = _collect(
        await asyncio.gather(
            *[_run(name, image_base64, media_type, ocr_text, mode, notes, translate_to) for name in provider_names],
            return_exceptions=True,
        )
    )
    if not first:
        raise RuntimeError("all providers failed")
    if len(first) == 1:
        return _build(first[0], first, 1.0, debated=False)

    _, agreement_score = agreement.consensus(_texts(first))
    if agreement_score >= AGREEMENT_THRESHOLD:
        winner = max(first, key=lambda c: c[1].confidence)
        return _build(winner, first, agreement_score, debated=False)

    payload = [{"provider": n, "hud_text": s.hud_text, "solution": s.solution} for n, s in first]
    second = _collect(
        await asyncio.gather(
            *[
                _run(
                    name,
                    image_base64,
                    media_type,
                    ocr_text,
                    mode,
                    notes,
                    translate_to,
                    peer_answers=[p for p in payload if p["provider"] != name],
                )
                for name, _ in first
            ],
            return_exceptions=True,
        )
    )
    final = second or first
    medoid, final_score = agreement.consensus(_texts(final))
    return _build(final[medoid], final, final_score, debated=True)
