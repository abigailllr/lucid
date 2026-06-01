def to_hud(solution: dict) -> dict:
    return {
        "type": "solution",
        "hud_text": solution["hud_text"][:120],
        "problem_type": solution["problem_type"],
        "confidence": solution["confidence"],
        "uncertain": solution.get("uncertain", False),
        "provider": solution.get("provider"),
    }
