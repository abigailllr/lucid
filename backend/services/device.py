import time

from config import settings


def _state(session: dict) -> dict:
    return session.setdefault("device", {})


def directive(temperature_c: float | None, battery: float | None) -> dict:
    if temperature_c is not None and temperature_c >= settings.device_temp_critical_c:
        return {"throttle_ms": max(settings.min_capture_interval_ms, 5000), "mode": "critical"}
    if temperature_c is not None and temperature_c >= settings.device_temp_throttle_c:
        return {"throttle_ms": max(settings.min_capture_interval_ms, 2500), "mode": "throttle"}
    if battery is not None and battery <= settings.low_battery_pct:
        return {"throttle_ms": max(settings.min_capture_interval_ms, 2500), "mode": "power_save"}
    return {"throttle_ms": settings.min_capture_interval_ms, "mode": "normal"}


def directive_for(session: dict) -> dict:
    state = _state(session)
    return directive(state.get("temperature_c"), state.get("battery"))


def heartbeat(session: dict, battery: float | None, temperature_c: float | None) -> dict:
    state = _state(session)
    if battery is not None:
        state["battery"] = battery
    if temperature_c is not None:
        state["temperature_c"] = temperature_c
    return directive_for(session)


def mode(session: dict) -> str:
    return directive_for(session)["mode"]


def too_soon(session: dict) -> bool:
    state = _state(session)
    last = state.get("last_capture")
    if last is None:
        return False
    interval = directive_for(session)["throttle_ms"] / 1000.0
    return (time.monotonic() - last) < interval


def register_capture(session: dict) -> None:
    _state(session)["last_capture"] = time.monotonic()
