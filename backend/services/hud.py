HUD_MAX_CHARS = 120


def to_hud(solution: dict) -> dict:
    return {
        "type": "result",
        "hud_text": solution["hud_text"][:HUD_MAX_CHARS],
        "kind": solution["kind"],
        "confidence": solution["confidence"],
        "uncertain": solution.get("uncertain", False),
        "provider": solution.get("provider"),
    }
