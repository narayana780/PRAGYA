import threading
from app.core.config import settings
from app.core.logging import logger
from app.modules.assistant.llm.base import LLMProvider
from app.modules.assistant.llm.local import LocalLLMProvider
from app.modules.assistant.llm.mock import MockLLMProvider
from app.modules.assistant.llm.openai_compatible import APICompatibleLLMProvider

_cached_llm_provider: LLMProvider | None = None
_llm_lock = threading.Lock()


def get_llm_provider(force_reload: bool = False) -> LLMProvider:
    """
    Thread-safe factory returning the application-scoped LLM provider instance
    based on the configured LLM_PROVIDER setting.
    """
    global _cached_llm_provider
    if _cached_llm_provider is not None and not force_reload:
        return _cached_llm_provider

    with _llm_lock:
        if _cached_llm_provider is not None and not force_reload:
            return _cached_llm_provider

        provider_name = settings.LLM_PROVIDER.lower().strip()
        logger.info(f"Initializing LLM Provider: {provider_name} (model: {settings.LLM_MODEL})")

        if provider_name in ("mock", "test", "testing"):
            provider = MockLLMProvider(model_name=settings.LLM_MODEL)
        elif provider_name in ("local", "ollama", "lmstudio", "localai", "vllm"):
            provider = LocalLLMProvider(
                base_url=settings.LLM_BASE_URL,
                model_name=settings.LLM_MODEL,
                api_key=settings.LLM_API_KEY,
            )
        elif provider_name in ("api_compatible", "openai", "openrouter", "remote"):
            provider = APICompatibleLLMProvider(
                base_url=settings.LLM_BASE_URL,
                model_name=settings.LLM_MODEL,
                api_key=settings.LLM_API_KEY,
            )
        else:
            logger.warning(
                f"Unknown LLM_PROVIDER '{provider_name}'. Defaulting to LocalLLMProvider."
            )
            provider = LocalLLMProvider()

        _cached_llm_provider = provider
        return _cached_llm_provider
