# 0005 — Multilingual lexicons isolated as data, canonical English categories

**Status:** accepted

## Context

Clients write in English, French, Spanish, Italian and Portuguese. Framing
must give the same result whatever the language, and the codebase must stay
readable in English.

## Decision

- Every keyword list lives in `khirami_agent/lexicons/<language>.py`. These
  data modules contain no logic and are the only place where non-English
  words appear in the source.
- Every module exposes the same table names with canonical English keys
  (`analyze`, `team`, `in_depth`, `brevity`…). `lexicons/__init__.py`
  assembles them per language and builds merged fallbacks for an undetermined
  language.
- Language detection never breaks a tie by declaration order. A tie or a weak
  signal returns `undetermined`.

## Consequences

- Adding a language means adding one data module and registering it.
- Multilingual test fixtures keep non-English sentences on purpose.
- The standalone constraint extractor (`constraints.py`) breaks ties by a
  fixed order and falls back to English when no signal is found. Its
  behaviour differs from the framer's on this point.
