from . import anthropic_ai, openai_ai, gemini_ai, ollama_ai

_PROVIDERS = {p.NAME: p for p in (anthropic_ai, openai_ai, gemini_ai, ollama_ai)}


def available_providers() -> list[str]:
    return [name for name, provider in _PROVIDERS.items() if provider.available()]


def get_provider(name: str):
    provider = _PROVIDERS.get(name)
    if provider is None:
        raise KeyError(name)
    if not provider.available():
        raise RuntimeError(f"provider '{name}' is not enabled or has no API key configured")
    return provider
