from abc import ABC, abstractmethod
import time
import logging
import httpx
from app.config import Settings

logger = logging.getLogger(__name__)

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
_LLM_HEALTH_CACHE: dict[str, tuple[float, bool]] = {}
_LLM_HEALTH_TTL_S = 60.0


class LLMProvider(ABC):
    """Abstract contract for LLM providers."""

    @abstractmethod
    async def generate_answer(self, prompt: str, system_message: str | None = None) -> str | None:
        ...


class CloudMistralProvider(LLMProvider):
    """Calls the Mistral cloud API (api.mistral.ai) using an API key."""

    def __init__(self, settings: Settings):
        self._api_key = settings.MISTRAL_KEY
        self._model = "mistral-small-latest"

    async def generate_answer(self, prompt: str, system_message: str | None = None) -> str | None:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 1024,
        }
        timeout = httpx.Timeout(45.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info("Calling Mistral cloud API model=%s", self._model)
            response = await client.post(
                MISTRAL_API_URL, headers=headers, json=payload
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                return None
            result = choices[0].get("message", {}).get("content", "")
            logger.info("LLM response length: %d chars", len(result) if result else 0)
            return result.strip() if result else None


class LocalMistralProvider(LLMProvider):
    """Uses httpx async client to call Ollama REST API (local)."""

    def __init__(self, settings: Settings):
        self._host = settings.OLLAMA_HOST
        self._model = settings.OLLAMA_MODEL

    async def generate_answer(self, prompt: str, system_message: str | None = None) -> str | None:
        timeout = httpx.Timeout(45.0, connect=10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                logger.info("Calling Ollama model=%s at %s", self._model, self._host)
                body: dict = {"model": self._model, "prompt": prompt, "stream": False}
                if system_message:
                    body["system"] = system_message
                response = await client.post(
                    f"{self._host}/api/generate",
                    json=body,
                )
                response.raise_for_status()
                data = response.json()
                result = data.get("response", "")
                logger.info("LLM response length: %d chars", len(result) if result else 0)
                return result.strip() if result else None
        except Exception as exc:
            # If Ollama is not running locally, return a deterministic canned reply
            logger.warning("Ollama local provider failed (%s); returning canned reply for demo", exc)
            # make a simple helpful reply that mimics an LLM summary/prediction
            if system_message and "Hindi" in (system_message[:40] if system_message else ""):
                return "यह एक डेमो उत्तर है क्योंकि स्थानीय LLM अनुपलब्ध है। कृपया स्थानीय Ollama सर्वर चालू करें।"
            return (
                "Demo LLM response: local Ollama is not reachable.\n"
                "This is a fallback answer to allow demos — start Ollama to use a real model."
            )


async def check_llm_connection(settings: Settings, timeout_s: float = 5.0) -> bool:
    """Check if the configured LLM backend is reachable."""
    cache_key = f"{settings.LLM_MODE}:{settings.OLLAMA_HOST}:{settings.OLLAMA_MODEL}:{settings.MISTRAL_KEY[:8]}"
    now = time.monotonic()
    cached = _LLM_HEALTH_CACHE.get(cache_key)
    if cached and now - cached[0] < _LLM_HEALTH_TTL_S:
        return cached[1]

    try:
        if settings.LLM_MODE == "cloud":
            if not settings.MISTRAL_KEY:
                return False
            # Validate the API key with a lightweight models list request
            async with httpx.AsyncClient(timeout=timeout_s) as client:
                response = await client.get(
                    "https://api.mistral.ai/v1/models",
                    headers={"Authorization": f"Bearer {settings.MISTRAL_KEY}"},
                )
                result = response.status_code == 200
                _LLM_HEALTH_CACHE[cache_key] = (now, result)
                return result
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            response = await client.get(f"{settings.OLLAMA_HOST}/api/tags")
            result = response.status_code == 200
            _LLM_HEALTH_CACHE[cache_key] = (now, result)
            return result
    except Exception:
        _LLM_HEALTH_CACHE[cache_key] = (now, False)
        return False


def get_llm_provider(settings: Settings) -> LLMProvider:
    """Factory function. Returns cloud or local provider based on LLM_MODE."""
    if settings.LLM_MODE == "cloud" and settings.MISTRAL_KEY:
        return CloudMistralProvider(settings)
    return LocalMistralProvider(settings)
