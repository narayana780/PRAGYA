import json
import re
from typing import Any, AsyncIterator

import httpx

from app.core.logging import logger
from app.modules.assistant.llm.base import LLMProvider, LLMResponse


class APICompatibleLLMProvider(LLMProvider):
    """
    Production-grade OpenAI-compatible LLM provider.
    Connects to local endpoints (Ollama, LM Studio, vLLM, LocalAI) or standard remote APIs.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434/v1",
        model_name: str = "llama-3-8b-instruct",
        api_key: str | None = None,
        timeout: float = 45.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._model_name = model_name
        self._api_key = api_key or "not-needed"
        self._timeout = timeout

    @property
    def model_name(self) -> str:
        return self._model_name

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self._api_key and self._api_key != "not-needed":
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"{self._base_url}/models",
                    headers=self._get_headers(),
                )
                return res.status_code in (200, 401)
        except Exception:
            return False

    def _build_payload_messages(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None,
        context: str | None,
    ) -> list[dict[str, str]]:
        formatted = []
        full_system = system_prompt or "You are PRAGYA AI, a source-grounded learning assistant."
        if context:
            full_system += f"\n\n--- UNTRUSTED REFERENCE EVIDENCE ---\n{context}\n--- END REFERENCE EVIDENCE ---"

        formatted.append({"role": "system", "content": full_system})
        for m in messages:
            formatted.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        return formatted

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        context: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        endpoint = f"{self._base_url}/chat/completions"
        payload_messages = self._build_payload_messages(messages, system_prompt, context)
        payload = {
            "model": self._model_name,
            "messages": payload_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    endpoint,
                    json=payload,
                    headers=self._get_headers(),
                )
                if resp.status_code != 200:
                    # Fallback without response_format if model doesn't support json_object
                    payload.pop("response_format", None)
                    resp = await client.post(
                        endpoint,
                        json=payload,
                        headers=self._get_headers(),
                    )
                    resp.raise_for_status()

                data = resp.json()
                choice = data.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                usage = data.get("usage", {})

                # Try parsing structured JSON
                answer = content
                explanation = None
                example = None
                citations = []

                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        answer = parsed.get("answer", content)
                        explanation = parsed.get("explanation")
                        example = parsed.get("example")
                        raw_cites = parsed.get("citations", [])
                        for c in raw_cites:
                            if isinstance(c, int):
                                citations.append(c)
                            elif isinstance(c, dict) and "source_id" in c:
                                try:
                                    citations.append(int(c["source_id"]))
                                except ValueError:
                                    pass
                except Exception:
                    # Fallback to regex citation extraction if not valid JSON
                    matches = re.findall(r"\[(?:Source\s+)?(\d+)\]", content)
                    citations = [int(m) for m in matches if int(m) > 0]

                return LLMResponse(
                    answer=answer,
                    explanation=explanation,
                    example=example,
                    citations=citations,
                    model=self._model_name,
                    usage=usage,
                    raw_output=content,
                )

        except Exception as e:
            logger.error(f"Error calling OpenAI-compatible LLM endpoint ({endpoint}): {e}")
            raise ConnectionError(f"Failed to communicate with LLM provider: {e}") from e

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        context: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        endpoint = f"{self._base_url}/chat/completions"
        payload_messages = self._build_payload_messages(messages, system_prompt, context)
        payload = {
            "model": self._model_name,
            "messages": payload_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream(
                    "POST", endpoint, json=payload, headers=self._get_headers()
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        chunk_str = line[6:].strip()
                        if chunk_str == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(chunk_str)
                            delta = chunk_data.get("choices", [{}])[0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Error streaming from LLM endpoint: {e}")
            raise ConnectionError(f"Failed to stream from LLM: {e}") from e
