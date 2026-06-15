# P1B · AUTO_LLM_PROVIDER_PLAN

> Provider abstraction for the auto-LLM content factory. Implemented in
> `scripts/mvp2_autogen_prediction_draft.py`. Operator stays the approval gate; no auto-publish.

## Providers (abstraction; one is enough to ship)

| Provider | env var | model | endpoint |
|----------|---------|-------|----------|
| DeepSeek (default) | `DEEPSEEK_API_KEY` | `deepseek-chat` | `api.deepseek.com/chat/completions` |
| Gemini | `GEMINI_API_KEY` | `gemini-2.0-flash` | `generativelanguage.googleapis.com/.../generateContent` |
| Kimi | `KIMI_API_KEY` | `moonshot-v1-8k` | `api.moonshot.cn/v1/chat/completions` |

- Keys read from `os.environ` (optionally hydrated from `backend/.env` for local dev). **Never printed,
  never committed** — `check_auto_llm_factory.py` fails if an API-key literal appears in the generator.
- Timeout: 60s. Retries: 2. JSON response mode requested (`response_format`/`responseMimeType`).
- Cost/log policy: one call per fixture per generation; the draft file records `provider` + `mode`
  only (no token usage secrets). No background loops.

## Modes
- **dry-run (default, offline):** deterministic, model-grounded draft synthesized from `model_fields`
  + `source_refs`. No network, no key, always reproducible — drives `--selftest` and the guards.
- **--live:** real provider call. Demonstrated this sprint with DeepSeek for the primary
  (Belgium-Egypt) and a secondary (Saudi-Uruguay) → both `status=GUARD_PASSED`, grounded
  (primary_score == computed model), recap_seed present, compliant.

## Offline fixture selftest
`mvp2_autogen_prediction_draft.py --selftest` (7/7) verifies the dry-run draft has all required
fields, guard-passes, is grounded in `model_fields`, carries recap_seed, and carries no probability.

## What ships now
DeepSeek is the implemented provider (live verified). Gemini/Kimi share the same abstraction and env
contract but are not exercised this sprint. Provider keys are LOCAL DEV only; production auto-LLM in
the daily build remains gated (operator review before publish).
