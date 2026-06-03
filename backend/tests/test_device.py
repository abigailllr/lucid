from services import device


def test_normal_mode():
    assert device.directive(temperature_c=25.0, battery=80.0)["mode"] == "normal"


def test_throttle_on_heat():
    assert device.directive(temperature_c=72.0, battery=80.0)["mode"] == "throttle"


def test_critical_on_high_heat():
    result = device.directive(temperature_c=85.0, battery=80.0)
    assert result["mode"] == "critical"
    assert result["throttle_ms"] >= 5000


def test_power_save_on_low_battery():
    assert device.directive(temperature_c=25.0, battery=10.0)["mode"] == "power_save"


def test_too_soon_tracks_capture():
    session = {}
    assert device.too_soon(session) is False
    device.register_capture(session)
    assert device.too_soon(session) is True
