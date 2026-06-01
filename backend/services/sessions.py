import secrets
import time

_sessions: dict[str, dict] = {}


def create(mode: str | None = None, provider: str | None = None, translate_to: str | None = None) -> dict:
    session_id = secrets.token_urlsafe(12)
    _sessions[session_id] = {
        "id": session_id,
        "mode": mode,
        "provider": provider,
        "translate_to": translate_to,
        "created": time.time(),
        "last_solution": None,
        "channel": None,
        "notes": [],
    }
    return _sessions[session_id]


def get(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def set_last(session_id: str, solution: dict) -> None:
    session = _sessions.get(session_id)
    if session:
        session["last_solution"] = solution


def set_channel(session_id: str, channel) -> None:
    session = _sessions.get(session_id)
    if session:
        session["channel"] = channel


def purge_expired(ttl: float) -> int:
    cutoff = time.time() - ttl
    removed = 0
    for session_id, session in list(_sessions.items()):
        if session["created"] < cutoff:
            del _sessions[session_id]
            removed += 1
    return removed
