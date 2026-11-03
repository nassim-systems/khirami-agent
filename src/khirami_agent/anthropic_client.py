"""
Anthropic model client for the consulting engagement pipeline.

`AnthropicClient` implements the `client(system_prompt, task_prompt) -> str`
callable expected by `run_engagement()`. It is the only module that talks to
a model provider, and the only one that needs a third-party package:

    pip install -e ".[anthropic]"

The API key is read from the `ANTHROPIC_API_KEY` environment variable only.
It is never accepted as an argument, never stored on the instance and never
included in an error message.

Every answer is returned as the text of one JSON object. Markdown code fences
around it are removed. Anything that does not parse as a JSON object raises
`InvalidJSONResponseError`, which the engagement pipeline retries once and
then declares as a gap.
"""

from __future__ import annotations

import json
import os
from typing import Any

API_KEY_ENV: str = "ANTHROPIC_API_KEY"
MODEL_ENV: str = "KHIRAMI_ANTHROPIC_MODEL"

DEFAULT_MODEL: str = "claude-sonnet-5-5"
DEFAULT_MAX_TOKENS: int = 8192
DEFAULT_TIMEOUT_SECONDS: float = 120.0
DEFAULT_MAX_RETRIES: int = 2


class ModelClientError(RuntimeError):
    """Base class for every error raised by a model client."""


class MissingAPIKeyError(ModelClientError):
    """The API key environment variable is not set."""


class MissingDependencyError(ModelClientError):
    """The optional provider SDK is not installed."""


class AuthenticationFailedError(ModelClientError):
    """The provider rejected the API key."""


class RateLimitedError(ModelClientError):
    """The provider rate limit was still hit after the retries."""


class ModelTimeoutError(ModelClientError):
    """The request did not complete within the timeout, retries included."""


class ModelConnectionError(ModelClientError):
    """The provider could not be reached."""


class ModelAPIError(ModelClientError):
    """Any other error status returned by the provider."""


class InvalidJSONResponseError(ModelClientError):
    """The model answer is not a single JSON object."""


def _load_sdk() -> Any:
    try:
        import anthropic
    except ImportError as error:
        raise MissingDependencyError(
            'The Anthropic SDK is not installed. Run: pip install -e ".[anthropic]"'
        ) from error
    return anthropic


def _strip_code_fence(text: str) -> str:
    """Remove a surrounding Markdown code fence, if the model added one."""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    body = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
    return "\n".join(body).strip()


class AnthropicClient:
    """
    Callable model client backed by the Anthropic Messages API.

    Parameters
        model        Model ID. Defaults to the `KHIRAMI_ANTHROPIC_MODEL`
                     environment variable, then to `DEFAULT_MODEL`.
        max_tokens   Upper bound on the length of each answer.
        timeout      Seconds allowed for each request.
        max_retries  Retries on connection errors, timeouts, rate limits and
                     server errors, with the SDK's exponential backoff.
        sdk          The `anthropic` module, or a stand-in exposing the same
                     names. Only meant for tests; loaded lazily otherwise.

    Raises `MissingAPIKeyError` at construction when `ANTHROPIC_API_KEY` is not
    set, so a misconfiguration fails before any engagement starts.
    """

    def __init__(
        self,
        model: str | None = None,
        *,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        sdk: Any = None,
    ) -> None:
        if not os.environ.get(API_KEY_ENV):
            raise MissingAPIKeyError(
                f"{API_KEY_ENV} is not set. Export it in your shell before running "
                "the engagement; the key is never read from code or files."
            )
        self.model = model or os.environ.get(MODEL_ENV) or DEFAULT_MODEL
        self.max_tokens = max_tokens
        self._sdk = sdk if sdk is not None else _load_sdk()
        # The SDK reads ANTHROPIC_API_KEY itself; the key never passes through here.
        self._client = self._sdk.Anthropic(timeout=timeout, max_retries=max_retries)

    def __call__(self, system_prompt: str, task_prompt: str) -> str:
        """Send one task to the model and return its answer as a JSON object string."""
        sdk = self._sdk
        try:
            message = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": task_prompt}],
            )
        except sdk.AuthenticationError as error:
            raise AuthenticationFailedError(
                f"The API key in {API_KEY_ENV} was rejected (HTTP 401)."
            ) from error
        except sdk.RateLimitError as error:
            raise RateLimitedError(
                "Rate limit reached (HTTP 429) after the configured retries. "
                "Wait before retrying, or lower the request rate."
            ) from error
        except sdk.APITimeoutError as error:
            raise ModelTimeoutError(
                "The model did not answer within the timeout, retries included."
            ) from error
        except sdk.APIConnectionError as error:
            raise ModelConnectionError("Could not reach the Anthropic API.") from error
        except sdk.APIStatusError as error:
            raise ModelAPIError(
                f"The Anthropic API returned HTTP {getattr(error, 'status_code', '?')}."
            ) from error

        text = "".join(
            getattr(block, "text", "")
            for block in message.content
            if getattr(block, "type", None) == "text"
        )
        candidate = _strip_code_fence(text)
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError as error:
            reason = (
                "the answer was cut off at max_tokens"
                if getattr(message, "stop_reason", None) == "max_tokens"
                else f"invalid JSON ({error.msg} at position {error.pos})"
            )
            raise InvalidJSONResponseError(f"Model answer is not usable: {reason}.") from error
        if not isinstance(payload, dict):
            raise InvalidJSONResponseError(
                f"Model answer is a JSON {type(payload).__name__}, expected an object."
            )
        return candidate
