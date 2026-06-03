from pydantic import BaseModel


class StartSessionRequest(BaseModel):
    mode: str | None = None
    provider: str | None = None
    translate_to: str | None = None
    client_public_key: str | None = None


class RekeyRequest(BaseModel):
    session_id: str
    client_public_key: str


class CaptureRequest(BaseModel):
    session_id: str
    image_base64: str
    media_type: str = "image/jpeg"
    provider: str | None = None
    speak: bool = False
    translate_to: str | None = None
    temperature_c: float | None = None
    battery: float | None = None


class HeartbeatRequest(BaseModel):
    session_id: str
    battery: float | None = None
    temperature_c: float | None = None


class SecureEnvelopeRequest(BaseModel):
    session_id: str
    envelope: dict


class CandidateAnswer(BaseModel):
    provider: str
    hud_text: str
    confidence: float


class SolveResponse(BaseModel):
    kind: str
    summary: str
    detail: str
    hud_text: str
    confidence: float
    provider: str
    cached: bool = False
    winner: str | None = None
    agreement: float | None = None
    debated: bool = False
    candidates: list[CandidateAnswer] | None = None
    audio_base64: str | None = None
    audio_mime: str | None = None
    uncertain: bool = False
