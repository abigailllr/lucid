from services import hud


def test_truncates_hud_text():
    solution = {"hud_text": "x" * 300, "kind": "text", "confidence": 0.9}
    payload = hud.to_hud(solution)
    assert len(payload["hud_text"]) == hud.HUD_MAX_CHARS
    assert payload["type"] == "result"
    assert payload["kind"] == "text"


def test_defaults_uncertain():
    payload = hud.to_hud({"hud_text": "ok", "kind": "sign", "confidence": 0.8})
    assert payload["uncertain"] is False
