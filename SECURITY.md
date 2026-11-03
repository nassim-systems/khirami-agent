# Security policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | Yes |

## Reporting a vulnerability

Please do not open a public issue for a security problem.

Report it privately through GitHub: open the **Security** tab of this
repository and choose **Report a vulnerability**. Include:

- what the problem is and which file or function it affects,
- the steps to reproduce it,
- the impact you expect, for example exposed data or a bypassed check.

The discussion stays private in the advisory thread until a fix is
available.

## API keys

- The Anthropic adapter reads the API key from the `ANTHROPIC_API_KEY`
  environment variable only. Never write a key in code, in a configuration
  file, in a test or in a commit message.
- `.env` and `.env.*` files are ignored by Git. Keep them that way.
- If a key is ever committed or shared, revoke it immediately in the
  Anthropic Console and create a new one. Removing it from the Git history
  is not enough: assume it has already been copied.

## What to keep in mind when using the agent

- Every request, and the business context you pass, is sent to the model
  provider when a model client is used. Do not send personal or
  confidential client data without the agreement that allows it.
- Model answers are untrusted input. The pipeline parses them as JSON and
  filters them against upstream identifiers, but it does not execute them.
- The consultant guard is a quality check on the deliverable (traceability,
  register, completeness). It is not a security control and does not detect
  prompt injection.
