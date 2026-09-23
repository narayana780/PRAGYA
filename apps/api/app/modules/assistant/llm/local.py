from app.core.config import settings
from app.modules.assistant.llm.openai_compatible import APICompatibleLLMProvider


class LocalLLMProvider(APICompatibleLLMProvider):
    """
    Local OpenAI-compatible LLM provider running on the host machine
    (e.g., Ollama, LM Studio, LocalAI, vLLM).
    Configured via settings.LLM_BASE_URL and settings.LLM_MODEL.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str | None = None,
        api_key: str | None = None,
        timeout: float = 60.0,
    ):
        super().__init__(
            base_url=base_url or settings.LLM_BASE_URL,
            model_name=model_name or settings.LLM_MODEL,
            api_key=api_key or settings.LLM_API_KEY,
            timeout=timeout,
        )
