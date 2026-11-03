# 0006 — Anthropic adapter as an optional extra, key from the environment only

**Status:** accepted

## Context

The engagement pipeline only produces consulting content when a model is
plugged in (see [0002](0002-injected-model-client.md)). The adapter must not
add a dependency to the core, must keep credentials out of the code and the
repository, and must fail in a way the caller can understand.

## Decision

- `AnthropicClient` implements `client(system_prompt, task_prompt) -> str` on
  the Anthropic Messages API. The SDK is an optional extra
  (`pip install -e ".[anthropic]"`) and is imported only when the client is
  created.
- The API key comes from `ANTHROPIC_API_KEY` only. The client checks that it
  is set, then lets the SDK read it: the key is never an argument, an
  attribute or part of an error message.
- The model defaults to `claude-sonnet-5-5`, a balance of quality, speed and
  cost. It can be changed per instance or with `KHIRAMI_ANTHROPIC_MODEL`.
- Timeouts and a bounded number of retries are delegated to the SDK.
  Provider errors are translated into a small set of explicit exceptions.
- The answer must be one JSON object. A surrounding code fence is removed,
  and anything else raises `InvalidJSONResponseError`. The pipeline then
  applies its usual single retry.

## Consequences

- The core stays dependency-free, and CI runs without the SDK or a key.
- The adapter is tested against a simulated SDK. One live test runs only when
  a key is present.
- Inside `run_engagement()`, provider errors become entries in
  `meta.degraded` instead of exceptions, consistent with the other gaps.
