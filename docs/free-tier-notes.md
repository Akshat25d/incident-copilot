# Free-tier notes

Checked on: 2026-11-06 (read from the provider consoles)

## Gemini (Google AI Studio), RPM / TPM / RPD
- gemini-3.5-flash-lite: 15 / 250K / 500  (main API model)
- gemini-3.8-flash: 5 / 250K / 20  (spot checks only)
- gemini-2.5-flash: 5 / 250K / 20
- gemini-2.5-flash-lite: 10 / 250K / 20
- gemma-4-26b and gemma-4-31b: 30 / 16K / 14.4K  (short prompts only; tool calling unverified)
- gemini-embedding-1 and -2: 100 / 30K / 1K  (not used; local embeddings instead)

## Groq free plan, RPM / RPD / TPM / TPD
- openai/gpt-oss-120b: 30 / 1K / 8K / 200K
- openai/gpt-oss-20b: 30 / 1K / 8K / 200K
- qwen/qwen3.8-27b: 30 / 1K / 8K / 200K
- meta-llama/llama-prompt-guard-2-22m and -86m: 30 / 14.4K / 15K / 500K
- Constraint: 8K tokens per minute and 200K per day, so only short prompts and a few runs a day

## Local (Ollama)
- qwen2.5:7b: no limits, speed depends on the GPU

## Decision
- Development and repeated runs: local qwen2.5:7b
- Quality eval runs: gemini-3.5-flash-lite, paced under 15 RPM, one full eval per day
- Fallback provider and model comparison: Groq gpt-oss
- Injection screening experiment: Groq llama-prompt-guard-2
- Embeddings and reranker: local
- Cache all model responses so repeated runs cost no quota
- Re-check limits before relying on any of this
