from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    default_provider: str = "anthropic"

    cors_origins: str = "*"

    anthropic_model: str = "claude-opus-4-8"
    openai_model: str = "gpt-4o"
    gemini_model: str = "gemini-1.5-pro"

    ollama_enabled: bool = False
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2-vision"

    google_vision_credentials_path: str = "google-vision-credentials.json"
    enable_handwriting_ocr: bool = True

    tts_voice: str = "nova"

    cache_ttl_seconds: int = 300
    cache_hash_distance: int = 5

    session_ttl_seconds: int = 3600
    purge_interval_seconds: int = 300

    confidence_threshold: float = 0.55

    min_capture_interval_ms: int = 1200
    device_temp_throttle_c: float = 70.0
    device_temp_critical_c: float = 80.0
    low_battery_pct: float = 15.0

    class Config:
        env_file = ".env"


settings = Settings()
