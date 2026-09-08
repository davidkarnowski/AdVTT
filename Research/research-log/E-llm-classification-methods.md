# E — LLM-based span classification over long transcripts: providers, local models, structured outputs, cost, methodology
Accessed: 2026-09-01

Note on method: WebSearch budget for this session was exhausted (200/200) in the first run, which also lost its
in-memory notes. This second run re-writes the log from the recorded tool outputs of run 1 and then continues
with WebFetch of primary URLs only. Entries marked "snippet-only" come from search-result summaries in run 1
and were NOT verified against the primary page; treat their numbers as approximate.

## Status
COMPLETE — 2026-09-01 (run 2). 64 source entries (≈45 fetched from primary pages, remainder snippet-only and marked). Synthesis, Implications, Open questions written.

## Sources

### Search log (run 1, WebSearch — 200 queries used; candidates listed, fetched ones become S-entries)
- "vLLM structured outputs guided decoding xgrammar ..." → docs.vllm.ai/en/latest/features/structured_outputs/ (S8), Red Hat article 2025-06-03
- "mlx_lm.server structured output json schema ..." → lmstudio.ai docs (S10), dottxt-ai outlines mlxlm page (S13), ollama issue #16776 (S11), cubist38/mlx-openai-server
- "LM Studio structured output ..." → lmstudio.ai/docs/developer/openai-compat/structured-output (S10)
- "llama.cpp server json_schema response_format GBNF ..." → grammars/README.md (S7), tools/server/README.md (S6)
- "OpenAI API pricing GPT-5.5 ..." → developers.openai.com/api/docs/pricing (S14); third-party trackers (morphllm, benchlm) not used
- "Mistral AI API pricing 2026" → cloudzero, benchlm, pricepertoken (S21, snippet-only)
- "DeepSeek API pricing 2026" → benchlm/deepseek, nxcode (S22, snippet-only)
- "Groq / Together / Fireworks pricing" → cloudzero, fireworks.ai/pricing, docs.fireworks.ai/serverless/pricing (S23, snippet-only)
- "Anthropic batch 50% caching" → platform.claude.com batch-processing (S18)
- "ModernBERT ... DeBERTa-v3" → arXiv 2412.13663, 2111.09543, 2312.17543 (S42)
- "few-shot system vs user; abstain" → arXiv 2606.07479, 2601.12471, 2505.18688, cleanlab blog (S41)
- "reasoning effort thinking budget classification" → arXiv 2510.21049, 2508.12140, 2512.19585, 2509.06861 (S33, S34)
- "chunk size vs accuracy" → arXiv 2504.00274, 2603.06976, firecrawl blog (S35)
- "mlx-lm structured output issue" → ollama #16563, otriscon/llm-structured-output, arXiv 2501.10868 JSONSchemaBench (S12, S13)
- "Qwen3 30B-A3B MLX tok/s" → HN 44635589, deepnewz, markaicode (S24)
- "gpt-oss-20b Apple Silicon" → yage.ai 2026-03-31, starmorph, john-rocky/apple-silicon-llm-bench, llama.cpp discussion 4167 (S25)
- "Gemma 4 open weights 2026" → arXiv 2607.02770, artificialanalysis.ai (S26)
- "Qwen3.5 / 3.6 / 3.8" → codersera, insiderllm, Wikipedia (S27)
- "LongBench v2 leaderboard" → benchlm.ai/benchmarks/longbench-v2, arXiv 2412.15204 (S28)
- "RULER results" → openreview RULER, arXiv 2503.01996 (S29)
- "NoLiMa" → arXiv 2502.05167 (S30)
- "Chroma context rot" → trychroma.com/research/context-rot, arXiv 2605.12366 (S31, S32)
- "hallucinated line numbers / quote anchoring" → arXiv 2606.07130, 2512.12117, 2408.04568 (S36)
- "Just Ask for Calibration follow-ups" → arXiv 2305.14975, 2306.13063, 2412.14737, 2604.01457, ICLR 2026 distractors paper (S39)
- "self-consistency / ensembles false positives" → arXiv 2605.13624, 2510.11409, 2601.22290 (S40)
- "SponsorBlock-ML" → github xenova/sponsorblock-ml, HF Xenova/sponsorblock-classifier-v2 (S43)
- "podcast ad detection papers" → arXiv 2103.02585, HF morenolq/..., github heidonomm/AdDetection, arXiv 2502.15102, US patent 12190871 (S44)

### S1. OpenAI — Structured Outputs guide — https://developers.openai.com/api/docs/guides/structured-outputs
- Type: spec
- Verified: fetched (platform.openai.com 301 → developers.openai.com)
- Key facts:
  - "Structured Outputs is available in our latest large language models, starting with GPT-4o. For new projects, start with `gpt-5.6`." Older models (gpt-4-turbo) must use JSON mode.
  - Uses `text.format` (Responses API) / `response_format` `{"type":"json_schema", ..., "strict": true}`; function calling has its own `strict: true`.
  - Safety refusals surface as a separate `refusal` field rather than being forced into the schema.
  - Page states "supports much of JSON Schema, some features are unavailable"; the fetched rendering did NOT expose the numeric limits (max properties / nesting / enum count / string budget) — those could not be verified this session (gap). Recursive schemas via `$ref` ARE shown in examples.
- Relevance to AdVTT:
  - The classifier's output (list of {start_idx,end_idx,confidence,kind,quote}) fits strict mode; every object must have `additionalProperties:false` and all keys `required` (well-known strict-mode rule; not re-verified here).
  - A refusal path must be handled in the parse rung (treat as "no spans", not as error).

### S2. Anthropic — Structured outputs (Claude API) — https://platform.claude.com/docs/en/docs/build-with-claude/structured-outputs
- Type: spec
- Verified: fetched (docs.anthropic.com 301 → platform.claude.com)
- Key facts:
  - GA, no beta header (legacy header `structured-outputs-2025-11-13` still accepted).
  - Two features: JSON outputs via `output_config.format = {"type":"json_schema","schema":{...}}` (old `output_format` deprecated) and **strict tool use** (`strict: true` on a tool's `input_schema`).
  - Supported models listed: claude-fable-5-1, claude-mythos-5-1, claude-fable-5, claude-mythos-5, claude-opus-5, claude-opus-4-8, -4-7, -4-6, claude-sonnet-5, claude-sonnet-4-6, claude-sonnet-4-5-20250929, claude-opus-4-5-20251101, claude-haiku-4-5-20251001.
  - Schema support: object/array/string/integer/number/boolean/null; enum (primitives), const, anyOf, allOf (not with $ref), $ref/$defs (internal only), required, `additionalProperties` MUST be false; string formats date-time/date/time/duration/email/uri/uuid/ipv4/ipv6/hostname; array `minItems` only 0 or 1.
  - NOT supported: recursive schemas, numeric constraints (minimum/maximum/multipleOf), minLength/maxLength, other array constraints, pattern (limited).
  - Grammar compiled on first request (extra latency), cached 24 h from last use; changing schema structure invalidates; changing `output_config.format` also invalidates the *prompt* cache for that thread. A system prompt is injected explaining the format (slightly more input tokens).
  - SDKs strip unsupported constraints and validate client-side against the original schema.
- Relevance to AdVTT:
  - `confidence` as `number` cannot carry `minimum:0,maximum:1` server-side → validate in the parse rung (already done by the ladder).
  - Keep the schema byte-stable across the run so the 24 h grammar cache and the prompt cache both hit.
  - Since `minItems` >1 unsupported, "return at most N spans" must be prompt-side.

### S3. Google — Gemini API structured output — https://ai.google.dev/gemini-api/docs/structured-output
- Type: spec
- Verified: fetched (twice, same rendering)
- Key facts:
  - Current doc examples use `gemini-3.7-flash` and `gemini-3.1-pro-preview` and describe the feature as available on "Gemini 3 series models".
  - The fetched page shows a `response_format: {type:"text", mime_type:"application/json", schema:{...}}` shape (the 2025-era `generationConfig.responseSchema` / `responseJsonSchema` fields were NOT visible in this rendering; the GenerationConfig reference page fetch was too vague to confirm — gap, see S3a).
  - Supported keywords: string/number/integer/boolean/object/array/null; properties, required, additionalProperties; enum; string `format` (date-time, date, time); numeric minimum/maximum; items, prefixItems, minItems, maxItems; title, description; anyOf; $ref (recursive allowed).
  - "Not all JSON Schema features are supported"; "Very large or deeply nested schemas may be rejected"; validation remains developer's job.
- Relevance to AdVTT:
  - Gemini is the one cloud provider that accepts numeric min/max and minItems/maxItems, so a single shared schema must be the intersection (no numeric bounds) or per-provider variants.
  - The urllib client must special-case Gemini's request shape; the shape appears to have changed between 2.5 and 3.x docs — pin to the API version actually tested.

### S3a. Google — GenerationConfig reference — https://ai.google.dev/api/generate-content#generationconfig
- Type: spec
- Verified: fetched (rendering did not expose full field text)
- Key facts: confirms fields `responseMimeType`, `responseSchema`, `responseJsonSchema`, `thinkingConfig.thinkingBudget`, `thinkingConfig.thinkingLevel` exist; keyword list for `responseJsonSchema` not extractable from the fetched rendering. The v1beta/GenerationConfig REST page returned 404.
- Relevance: the legacy `responseSchema` (OpenAPI subset) vs `responseJsonSchema` (JSON Schema) split is real but its exact subset is unverified here → experiment needed.

### S4. Ollama — Structured outputs (blog, 2024-12-06) — https://ollama.com/blog/structured-outputs
- Type: product/blog
- Verified: fetched
- Key facts: introduced 2024-12-06 (Ollama 0.5); `format` accepts a JSON schema object on `/api/chat` and `/api/generate`; recommends temperature 0 and telling the model to "return as JSON" in the prompt; roadmap lists "performance and accuracy improvements for structured outputs".
- Relevance: the classifier's Ollama path can pass the span schema directly via `format`; keep the "respond in JSON" instruction in the prompt as the blog recommends.

### S5. Ollama — API reference (docs/api.md) — https://github.com/ollama/ollama/blob/main/docs/api.md
- Type: spec
- Verified: fetched
- Key facts: `format` = `"json"` or a JSON-schema object on both endpoints ("It's important to instruct the model to use JSON in the prompt"); `think` accepts bool or `"low"|"medium"|"high"|"max"` on thinking models; `options.num_ctx` sets context window (default is small — must be raised for 6k-token chunks + context); OpenAI-compat `/v1` `response_format` not covered in the fetched section.
- Relevance: set `num_ctx` ≥ 16k explicitly per request or the 6000-token chunk plus system prompt will be silently truncated; `think` gives a per-request thinking budget knob comparable to Anthropic's.

### S6. llama.cpp — llama-server README — https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- Type: spec
- Verified: fetched
- Key facts: `/completion` accepts `grammar` (GBNF) and `json_schema`; `/v1/chat/completions` accepts `response_format` as `{"type":"json_object","schema":{...}}` or `{"type":"json_schema","schema":{...}}` (note: llama.cpp nests `schema` directly, unlike OpenAI's `json_schema.schema`); "For schemas w/ external $refs, use --grammar + example/json_schema_to_grammar.py"; supported features documented only by tests/test-json-schema-to-grammar.cpp.
- Relevance: the schema is a sampling constraint only and is NOT injected into the prompt (also stated in S7) — the prompt must still describe the output shape.

### S7. llama.cpp — grammars/README.md (GBNF) — https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md
- Type: spec
- Verified: snippet-only
- Key facts (snippet): GBNF = "GGML BNF"; JSON-schema→GBNF converter exists in C++ and Python; "The JSON schema is only used to constrain the model output and is not injected into the prompt".
- Relevance: same as S6; LM Studio's GGUF path uses this machinery (S10).

### S8. vLLM — Structured Outputs — https://docs.vllm.ai/en/latest/features/structured_outputs/
- Type: spec
- Verified: snippet-only (fetch returned HTTP 429 twice)
- Key facts (snippet): backends xgrammar (default) or guidance; OpenAI-compatible server accepts `response_format` json_schema and an extra-body `structured_outputs: {json|regex|choice|grammar|structural_tag|whitespace_pattern}`; the old `guided_json`/`guided_regex`/`guided_choice`/`guided_grammar` fields were removed in v0.12.0.
- Relevance: if a Linux/NVIDIA box is ever used, target `structured_outputs`, not `guided_json`.

### S9. mlx-lm — SERVER.md (mlx_lm.server) — https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md
- Type: spec
- Verified: fetched
- Key facts: documented `/v1/chat/completions` fields are messages, role_mapping, stop, max_tokens, stream, temperature, top_p, top_k, min_p, repetition_penalty(+context_size), presence/frequency penalties, logit_bias, logprobs, model, adapters, draft_model, num_draft_tokens. **No `response_format`, `json_schema` or grammar field is documented** — no constrained decoding in the stock server.
- Relevance: the project's "MLX" backend must rely on prompt-only JSON plus the parse rung; if constrained decoding is wanted on MLX, use Outlines' mlxlm integration (S13) or LM Studio's MLX engine (S10), or Ollama's GGUF runner rather than its MLX runner (S11/S12).

### S10. LM Studio — Structured Output (OpenAI-compat) — https://lmstudio.ai/docs/developer/openai-compat/structured-output
- Type: spec
- Verified: fetched
- Key facts: `response_format: {type:"json_schema", json_schema:{name, strict:"true", schema}}` on `/v1/chat/completions`; GGUF models "utilize llama.cpp's grammar-based sampling APIs"; MLX models use Outlines; "not all models are capable of structured output, particularly LLMs below 7B parameters"; result is a JSON string in `choices[0].message.content`.
- Relevance: LM Studio is the only Mac-local server that gives constrained JSON on MLX out of the box; the classifier's OpenAI-compatible urllib path would work against it unchanged.

### S11. Ollama issue #16776 — "gemma4 MLX runner ignores JSON Schema format" — https://github.com/ollama/ollama/issues/16776
- Type: forum (bug report)
- Verified: fetched
- Key facts: Ollama 0.30.8; MLX runner "silently ignores the `format` JSON Schema parameter in /api/chat" and returns free text; same gemma4:26b model enforces schema on the GGUF runner; opened 2026-06-17; closed as duplicate of #16563.
- Relevance: on Apple Silicon Ollama, structured output only works on the GGUF backend — a silent failure mode the classifier's parse rung must catch (it does: parse → fail).

### S12. Ollama issue #16563 — "Structured outputs appear to be ignored for MLX models" — https://github.com/ollama/ollama/issues/16563
- Type: forum
- Verified: snippet-only
- Key facts (snippet): MLX variants of Qwen 3.5 and Gemma 4 "ignore the schema entirely"; non-MLX variants conform; a related report of mlx-community Qwen 3.5 checkpoints losing the ability to emit structured tool_use after several turns.
- Relevance: same as S11.

### S13. Outlines — mlx-lm model integration — https://dottxt-ai.github.io/outlines/latest/features/models/mlxlm/
- Type: repo/docs
- Verified: snippet-only
- Key facts (snippet): Outlines converts a JSON schema to a regex and applies a logits processor (`OutlinesJSONLogitsProcessor`) to mlx-lm generation; not part of mlx-lm core. Community alternatives: otriscon/llm-structured-output (schema-steered, no grammar compile), Toolio.
- Relevance: a Python-side path to constrained JSON on MLX if AdVTT ships its own MLX runner instead of calling mlx_lm.server.

### S14. OpenAI — API pricing — https://developers.openai.com/api/docs/pricing
- Type: product (pricing)
- Verified: fetched (openai.com/api/pricing returned 403)
- Key facts (USD per 1M tokens, input / cached input / output; batch = 50%):
  - gpt-5.6-sol 4.00 / 0.40 / 20.00 (batch 2.00/0.20/10.00); gpt-5.6-terra 2.00 / 0.20 / 12.00 (batch 1.00/0.10/6.00); gpt-5.6-luna 0.20 / 0.02 / 1.20 (batch 0.10/0.01/0.60).
  - gpt-5.5 5.00 / 0.50 / 30.00 (<272k ctx; long-context 10.00/1.00/45.00); batch 2.50/0.25/15.00. gpt-5.5-pro 30/–/180.
  - gpt-5.4 2.50 / 0.25 / 15.00; gpt-5.4-mini 0.75 / 0.075 / 4.50; gpt-5.4-nano 0.20 / 0.02 / 1.25.
  - gpt-5.2 1.75/0.175/14; gpt-5.1 and gpt-5 1.25/0.125/10; gpt-5-mini 0.25/0.025/2.00; gpt-5-nano 0.05/0.005/0.40.
  - gpt-4.1 2/0.5/8; gpt-4.1-mini 0.40/0.10/1.60; gpt-4.1-nano 0.10/0.025/0.40.
  - No gpt-5.5-mini / gpt-5.5-nano / gpt-5.6-mini rows exist; the 5.6 tiers are named sol/terra/luna. Flex tier exists at batch-equivalent rates for gpt-5.6 models and gpt-5-mini/nano.
- Relevance: the project's current cloud model gpt-5.5 is the most expensive non-pro tier on the page ($5/$30); gpt-5.6-terra ($2/$12) or luna ($0.20/$1.20) are the obvious candidates to A/B.

### S15. OpenAI — Prompt caching guide — https://developers.openai.com/api/docs/guides/prompt-caching
- Type: spec
- Verified: fetched
- Key facts: caching is automatic on exact prefix match; GPT-5.6+ minimum "1,024 visible input tokens" (older models 2,048; usage rounded down to multiples of 128); cached input billed at 0.1× on GPT-5.6+; retention "around 5 to 10 minutes of inactivity, up to one hour" (older), extended 24 h option, GPT-5.6 "at least 30 minutes after the latest write or reuse"; `prompt_cache_key` steers routing but does not guarantee hits; any change to model, tools, instructions or settings discards the entry; explicit caching only on GPT-5.6+.
- Relevance: put the long static rubric + few-shot block first, then the chunk; every chunk of the same episode within minutes will hit the cache for the prefix.

### S16. Anthropic — Pricing (platform docs) — https://platform.claude.com/docs/en/about-claude/pricing
- Type: product (pricing)
- Verified: fetched (claude.com/pricing rendered only subscription plans)
- Key facts (USD per 1M tokens: base input / 5m cache write / 1h cache write / cache read / output):
  - Claude Fable 5.1 (and Mythos 5.1, limited availability): 10 / 12.50 / 20 / 0.25 (0.025×) / 50.
  - Claude Fable 5: 10 / 12.50 / 20 / 1 / 50.
  - Claude Opus 5, Opus 4.8, 4.7, 4.6, 4.5: 5 / 6.25 / 10 / 0.50 / 25.
  - Claude Sonnet 5: 2 / 2.50 / 4 / 0.20 / 10 (introductory price made permanent; the Sept-1-2026 rise to $3/$15 "will not occur").
  - Claude Sonnet 4.6, 4.5: 3 / 3.75 / 6 / 0.30 / 15.
  - Claude Haiku 4.5: 1 / 1.25 / 2 / 0.10 / 5. (Haiku 3.5 retired on first-party API.)
  - Batch API: 50% off input and output (Haiku 4.5 batch 0.50/2.50; Sonnet 5 batch 1/5; Opus 5 batch 2.50/12.50). Batch and cache discounts stack.
  - Claude 4.7+ tokenizer "produces approximately 30% more tokens for the same text" than Sonnet 4.6 and earlier.
  - 1M context at standard price on 4.6+; tool-use system prompt overhead 286–804 tokens depending on model.
- Relevance: Haiku 4.5 remains the cheap tier ($1/$5); Sonnet 5 at $2/$10 is now cheaper than Sonnet 4.6; the 30% tokenizer inflation on 4.7+ models must be included in cost math.

### S17. Anthropic — Prompt caching — https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Type: spec
- Verified: fetched
- Key facts: hierarchy tools → system → messages; `cache_control` breakpoint on the last static block; automatic top-level `cache_control` option; 20-block lookback; minimum cacheable length: 512 tokens (Fable 5.1/5, Mythos, Opus 5), 1,024 (Opus 4.8, Sonnet 5/4.6/4.5), 2,048 (Opus 4.7), **4,096 (Opus 4.6/4.5 and Haiku 4.5)**; TTL 5 min default (refresh free on hit) or `ttl:"1h"` at 2× write; TTL measured from request start; changing `output_config.format` invalidates message cache; thinking blocks can't be explicitly cached.
- Relevance: on Haiku 4.5 the static prefix must exceed 4,096 tokens to cache at all — the rubric + negative-example list + few-shots should be sized past that threshold (or accept no caching on Haiku); keep schema and thinking config fixed per run.

### S18. Anthropic — Batch processing — https://platform.claude.com/docs/en/build-with-claude/batch-processing
- Type: spec
- Verified: fetched (73 KB page saved locally; only headline read so far)
- Key facts: asynchronous Message Batches API; "most batches finishing in less than 1 hour" (24 h ceiling); 50% cost reduction on input and output; each request processed independently; ZDR eligible.
- Relevance: an offline "classify my whole archive" mode could run every chunk of every episode as one batch at half price; interactive single-episode runs cannot.

### S19. Google — Gemini API pricing — https://ai.google.dev/gemini-api/docs/pricing
- Type: product (pricing)
- Verified: fetched
- Key facts (paid tier, USD per 1M tokens input / output; context cache read; batch = 50%):
  - Gemini 3.7 Flash and 3.6 Flash: 0.75 / 3.75 through 2026-12-31 (then 1.50 / 7.50); cache 0.075.
  - Gemini 3.5 Flash: 1.50 / 9.00; cache 0.15. Gemini 3.5 Flash-Lite: 0.30 / 2.50; cache 0.03.
  - Gemini 3.1 Flash-Lite: 0.25 / 1.50 (audio in 0.50); cache 0.025.
  - Gemini 3.1 Pro Preview: 2.00 / 12.00 (≤200k) ; 4.00 / 18.00 (>200k); no free tier.
  - Gemini 2.5 Pro: 1.25 / 10.00 (≤200k); 2.5 Flash: 0.30 / 2.50; 2.5 Flash-Lite: 0.10 / 0.40.
  - Free tier available on all Flash/Flash-Lite and 2.5 Pro.
- Relevance: 2.5 Flash-Lite ($0.10/$0.40) and 3.1 Flash-Lite ($0.25/$1.50) are the cheapest hosted frontier-family options; free tier makes Gemini the natural default for a public CLI's "no-credit-card" path.

### S20. Google — Gemini context caching — https://ai.google.dev/gemini-api/docs/caching
- Type: spec
- Verified: fetched
- Key facts: implicit caching on by default for 2.5 and newer; minimum input for implicit cache: 4,096 tokens (3.7/3.6/3.5 Flash, 3.1 Pro Preview), 2,048 (2.5 Flash, 2.5 Pro); explicit caching not in the Interactions API; cached tokens reported in `usage.total_cached_tokens`; discount percentage not on this page (pricing page S19 lists cache-read prices ≈10% of input).
- Relevance: same prefix-first prompt layout as OpenAI; the 4,096-token floor on 3.x Flash again argues for a long static system block.

### S21. Mistral API pricing (third-party trackers) — https://www.cloudzero.com/blog/mistral-api-pricing/ ; https://benchlm.ai/mistral/api-pricing
- Type: product (pricing, secondary)
- Verified: snippet-only (mistral.ai/pricing not fetched — session limit)
- Key facts (snippet, approx.): Mistral Large 3 $0.50/$1.50; Mistral Small 4 $0.15/$0.60; Mistral Medium 3.5 $1.50/$7.50; Ministral 3 edge family $0.10–0.20 symmetric.
- Relevance: Mistral Small 4 is in the gpt-5.6-luna / Gemini Flash-Lite price band; unverified.

### S22. DeepSeek API pricing (third-party trackers) — https://benchlm.ai/deepseek/api-pricing ; https://www.nxcode.io/resources/news/deepseek-api-pricing-complete-guide-2026
- Type: product (pricing, secondary)
- Verified: snippet-only (api-docs.deepseek.com not fetched — session limit)
- Key facts (snippet, approx., contradictory between trackers): V4 Flash $0.14 in (miss) / $0.0028 cached / $0.28 out; V4 Pro $0.435 / $0.003625 / $0.87; `deepseek-chat`/`deepseek-reasoner` retired as aliases 2026-07-24; one tracker reports time-of-day pricing from 2026-08-16 (V4-Flash peak $0.44/$1.32, off-peak $0.22/$0.66) which conflicts with the flat numbers above.
- Relevance: cheapest hosted tier by far if the numbers hold, but pricing volatility + data-residency questions make it a poor default for a public tool.

### S23. Groq / Together / Fireworks pricing for open models (third-party + vendor pages) — https://fireworks.ai/pricing ; https://docs.fireworks.ai/serverless/pricing ; https://www.cloudzero.com/blog/groq-pricing/ ; https://www.cloudzero.com/blog/together-ai-pricing/
- Type: product (pricing)
- Verified: snippet-only (vendor pages not fetched — session limit)
- Key facts (snippet, approx.): gpt-oss-120b $0.15/$0.60 on Groq, Together and Fireworks (Fireworks cached input $0.015); gpt-oss-20b $0.075/$0.30 (Groq); Qwen 3.6 27B $0.60/$3.00 (Groq); Llama 3.3 70B $0.59/$0.79 (Groq) vs $1.04/$1.04 (Together); Qwen 3.6 Plus $0.50/$3.00 (Fireworks).
- Relevance: gpt-oss-120b hosted at $0.15/$0.60 is a credible "cloud-cheap" tier with an open-weights fallback that is also runnable locally (S25).

### S24. Qwen3-30B-A3B throughput on Apple Silicon (MLX) — https://news.ycombinator.com/item?id=44635589 ; https://deepnewz.com/ai-modeling/qwen3-30b-a3b-model-mlx-weights-shows-m4-max-m3-ultra-lead-tokens-per-second-32k-380e5584
- Type: forum / blog
- Verified: snippet-only
- Key facts (snippet, approx.): 4-bit MLX Qwen3-30B-A3B: M4 Max ≈87.6 tok/s at 8k context, "70–100 tok/s depending on context"; M3 Ultra ≈76.3; M2 Ultra ≈68.5; M3 Max ≈70 tok/s; thermal throttling reduces sustained speed; M4 Max leads up to 32k context.
- Relevance: an MoE 30B-A3B class model decodes fast enough that a 60-min episode (≈10 chunks × ~600 output tokens) is seconds of decode; prefill of ~7k tokens/chunk is the real local cost (prefill numbers not captured — gap).

### S25. gpt-oss-20b and MLX vs llama.cpp on Apple Silicon — https://yage.ai/share/mlx-apple-silicon-en-20260331.html ; https://github.com/john-rocky/apple-silicon-llm-bench ; https://github.com/ggml-org/llama.cpp/discussions/4167
- Type: blog / repo / forum
- Verified: snippet-only (fetches blocked by session limit)
- Key facts (snippet, approx.): gpt-oss-20b MXFP4 on M4 Max via MLX ≈100 tok/s decode, ≈1,528 tok/s prefill; a Q5_K_M GGUF build 15–25 tok/s on lesser chips; MLX reported 10–25% (up to 87% for <14B) faster than llama.cpp on Apple Silicon; memory bandwidth (M3 Max 300–400 GB/s vs M4 Pro 273 GB/s) is the dominant predictor of decode speed; llama.cpp discussion #4167 is the canonical M-series PP/TG table (not re-read).
- Relevance: at ≈1.5k tok/s prefill, a 7k-token chunk costs ~5 s prefill; 10 chunks ≈ 1 min per episode on an M4 Max for a 20B-class model — competitive with cloud latency.

### S26. Gemma 4 (Google DeepMind, released 2026-04-02) — https://arxiv.org/abs/2607.02770 ; https://artificialanalysis.ai/articles/gemma-4-everything-you-need-to-know
- Type: paper / blog
- Verified: snippet-only (arXiv fetch blocked by session limit)
- Key facts (snippet, approx.): four open-weight sizes: E2B (2.3B effective), E4B (4.5B), 26B-A4B MoE (25.2B total / 3.8B active), 31B dense (30.7B); 128k context on E2B/E4B, 256k on 26B/31B; Apache 2.0; RULER: 31B 96.8% at 32k and 96.4% at 128k; Gemma 3 scored 13.5% on RULER-128k vs Gemma 4 66.4% (which variant unclear).
- Relevance: Gemma 4 26B-A4B (fits 32 GB at 4-bit) and 31B (needs ~20 GB at 4-bit) are the strongest 2026 local candidates on long-context reliability; IFEval numbers not captured (gap).

### S27. Qwen 3.5 / 3.6 / 3.8 open weights (2026) — https://codersera.com/blog/qwen-3-5-complete-guide-2026/ ; https://insiderllm.com/guides/qwen-models-guide/ ; https://en.wikipedia.org/wiki/Qwen
- Type: blog / encyclopedia
- Verified: snippet-only
- Key facts (snippet, approx.): Qwen 3.5 9B and 27B remain open on Hugging Face; Qwen 3.6 lineup 27B dense and 35B-A3B MoE, 256k context; Qwen 3.8-27B released 2026-08-14 under Apache 2.0, 262k context, Artificial Analysis Intelligence Index 52 (vs 38 for 3.6-27B); flagship Qwen weights reportedly closed. No IFEval figures captured.
- Relevance: Qwen3.6-35B-A3B / Qwen3.8-27B are direct competitors to Gemma 4 for the local tier; the original Qwen3 (8B/14B/30B-A3B/32B, 2025) is now two generations old.

### S28. LongBench v2 leaderboard (as of 2026-08-15) — https://benchlm.ai/benchmarks/longbench-v2 ; paper https://arxiv.org/abs/2412.15204
- Type: dataset / paper (leaderboard via tracker)
- Verified: snippet-only
- Key facts (snippet, approx.): Qwen3.8 Max 66.3%, Claude Opus 4.5 64.4%, Qwen3.5-397B 63.2%, Nemotron 3 Ultra 61.9%, Kimi K2.5 61.0%, GLM-5 60.8%, **Qwen3.5-27B 60.6%**, DeepSeek V4 Pro Base 51.5%; Llama 3.1/3.3 ≈30% in the original paper. Human experts 53.7% in the paper (from memory of the paper; not re-verified).
- Relevance: a 27B open model within 4 points of the best frontier model on LongBench v2 supports a local-first default for 6k-token chunks.

### S29. RULER and effective context length — https://openreview.net/pdf?id=kIoBbc76Sy ; https://arxiv.org/html/2503.01996v2
- Type: paper
- Verified: snippet-only
- Key facts (snippet): RULER = synthetic retrieval / multi-hop / aggregation / QA tasks; "effective context length sits at roughly 50–65% of the marketed capacity for most models"; Llama 4 Scout's 10M window was trained at 256k and extrapolated.
- Relevance: chunking at 6k tokens sits comfortably inside every candidate's effective length; whole-episode (30–60k) calls do not on most open models.

### S30. NoLiMa: Long-Context Evaluation Beyond Literal Matching (ICML 2025) — https://arxiv.org/abs/2502.05167
- Type: paper
- Verified: snippet-only (arXiv fetch blocked by session limit)
- Key facts (snippet): 13 models; when question/needle share no lexical overlap, "11 out of 13 models drop below 50% of their baseline scores at 32K"; GPT-4o 99.3% at 1k → 69.7% at 32k; Llama 3.1 70B effective length ~2k, 42.7% at 32k vs 94.3% base.
- Relevance: host-read ads have weak lexical signal (no jingle, host's voice) — exactly the non-literal-matching regime where long-context accuracy collapses; strong argument to keep chunks ≤ 8k tokens even on frontier models.

### S31. Chroma — Context Rot (2025-07) — https://www.trychroma.com/research/context-rot
- Type: blog (technical report)
- Verified: snippet-only (redirect not followed before session limit)
- Key facts (snippet): Hong, Troynikov, Huber; 18 models incl. GPT-4.1, Claude 4, Gemini 2.5, Qwen3; performance degrades at every input-length increment even on simple retrieval and **text replication**; degradation observable well below the window (e.g. at 50k on 1M-window models); needle in the middle retrieved worse than at the ends.
- Relevance: the text-replication experiment is the closest published analogue to "copy the right segment index" — degradation with length is the mechanism behind the project's 800-segment misplacement on a 3919-segment single call.

### S32. Classifier Context Rot: Monitor Performance Degrades with Context Length — https://arxiv.org/abs/2605.12366
- Type: paper
- Verified: snippet-only
- Key facts (snippet): LLM classifiers used as monitors lose accuracy as context length grows; title-level claim only (details not read).
- Relevance: direct support for per-chunk classification over whole-episode; should be read in full (open item).

### S33. Reasoning's Razor: Reasoning Improves Accuracy but Can Hurt Recall at Low FPR — https://arxiv.org/html/2510.21049
- Type: paper
- Verified: snippet-only
- Key facts (snippet): "first systematic study of reasoning for classification tasks under strict low false positive rate regimes"; reasoning improves overall accuracy, but "direct classification without explicit reasoning achieves better recall at strict low-FPR thresholds".
- Relevance: partially contradicts the project's observation (thinking budget 0 → 77.5 s false positives vs 2 s at 4000 on claude-haiku). The paper's regime is fixed-FPR thresholding on a score; AdVTT's regime is un-thresholded generation. Needs an experiment across budgets (0 / 1k / 4k) on all four fixtures.

### S34. Thinking-budget scaling studies — https://arxiv.org/abs/2508.12140 ; https://arxiv.org/html/2512.19585v1 ; https://arxiv.org/html/2509.06861v1
- Type: paper
- Verified: snippet-only
- Key facts (snippet): "Exploring Efficiency Frontiers of Thinking Budget": +2–5 points for 4–5× tokens; "Increasing the Thinking Budget is Not All You Need": <2% gain on knowledge-intensive tasks, high effort can show confirmation bias / overconfident wrong answers; "Test-Time Scaling ... Is Not Effective for ..." (task family not captured).
- Relevance: a moderate fixed budget (project's 4000) is defensible; unbounded thinking is not a precision lever.

### S35. Chunk-size vs accuracy studies — https://arxiv.org/pdf/2504.00274 ; https://arxiv.org/html/2603.06976 ; https://www.firecrawl.dev/blog/best-chunking-strategies-rag
- Type: paper / blog
- Verified: snippet-only
- Key facts (snippet): "Text Chunking for Document Classification for Urban System Management" (2025): GPT-4o and o1-mini "more correctly identified relevant outcomes when they have a smaller volume of data"; chunking raised recall without a precision penalty. "A Systematic Investigation of Document Chunking Strategies" (2026): structure-preserving chunking mitigates precision/recall trade-off better than fine-grained semantic chunks. Practitioner default 400–512 tokens w/ 10–20% overlap is for RAG retrieval, not classification.
- Relevance: evidence favours smaller-than-6k chunks for recall, but boundary artefacts (an ad split across chunks) are the AdVTT-specific cost; the ±12-segment read-only context is the right mitigation — worth testing 3k vs 6k.

### S36. Span/citation grounding studies — https://arxiv.org/pdf/2606.07130 ; https://arxiv.org/pdf/2512.12117 ; https://arxiv.org/pdf/2408.04568
- Type: paper
- Verified: snippet-only
- Key facts (snippet): "Explicit Evidence Grounding via Structured Inline Citation Generation" (2026): models "struggle to localize the precise evidence span"; verbatim-span methods (FullCite) beat alternatives by ≥20% overlap. "Preventing LLM Hallucination Through Hybrid Retrieval" (2025): mechanical verification of cited file/line ranges "prevented hallucination in 100% of cases" where invalid ranges were emitted. Fine-grained grounded citations (2024) train models to quote supporting spans.
- Relevance: strong support for the project's rung 5 (verbatim quote must match) and for moving the *primary* anchor from index to quote: quotes are verifiable, indices are not.

### S37. Anthropic — Citations — https://platform.claude.com/docs/en/build-with-claude/citations
- Type: spec
- Verified: fetched (73 KB saved; detail extracted below in S37 addendum)
- Key facts: all active models support citations; documents passed as `document` content blocks with `citations:{enabled:true}`; plain-text documents are chunked into sentences and citations return `cited_text` with `start_char_index`/`end_char_index` (`char_location`) — server-side, so the quote is guaranteed verbatim from the source.
- Relevance: an alternative to asking the model for indices at all: pass the chunk as a citable document and read the char offsets back from the citation blocks; Claude-only, but it removes hallucinated positions on that provider.

### S38. Anthropic — Prompting best practices (current models) — https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Type: spec
- Verified: fetched (63 KB saved; detail to be extracted)
- Key facts: covers Fable 5.1 … Haiku 4.5; sections on examples, XML structuring, thinking, output formatting (addendum to follow after reading the saved file).
- Relevance: provider-official guidance on where to put examples and how to phrase negative instructions.

### S39. Verbalised confidence & calibration line — https://arxiv.org/abs/2305.14975 (Tian et al., EMNLP 2023) ; https://arxiv.org/abs/2306.13063 (Xiong et al., ICLR 2024) ; https://arxiv.org/html/2412.14737v2 (Yang et al. 2024) ; https://arxiv.org/pdf/2604.01457 ("Wired for Overconfidence", 2026)
- Type: paper
- Verified: snippet-only
- Key facts (snippet): Tian 2023: RLHF models' verbalised probabilities are better calibrated than their token probabilities; prompting + temperature scaling cut ECE by >50%. Xiong 2024: verbalised confidence "predominantly in the 80–100% range regardless of actual accuracy"; best results from combining sampling consistency with verbalised scores. Yang 2024 and 2025–26 follow-ups: verbalised confidence "generally outstrips average accuracy within a confidence bin"; ICLR 2026 paper calibrates via self-generated distractors.
- Relevance: the model's `confidence` field is a weak ordinal signal at best; keep the ladder's rule-based halving, and if a numeric threshold is used, calibrate it post-hoc on the fixtures (temperature/Platt scaling of the verbalised score, or replace it with agreement counts from multiple samples).

### S40. Self-consistency / ensembles against false positives — https://arxiv.org/pdf/2605.13624 ; https://arxiv.org/pdf/2510.11409 ; https://arxiv.org/pdf/2601.22290
- Type: paper
- Verified: snippet-only
- Key facts (snippet): "Edit-level Majority Voting Mitigates Over-Correction in LLM-based GEC" (2026): voting over sampled edits reduces spurious edits (precision up). SLR corpus filtration (2025): open models over-include; "in most cases only one model was responsible" for false inclusions; requiring agreement of multiple models cut manual review by 695 papers. A "Probabilistic Consensus Framework" claim of precision 73.1% → 93.9% with two models, 95.6% with three (78 cases; source paper not verified).
- Relevance: intersect-two-providers (or two samples) is the cheapest known precision lever and matches the false-positive asymmetry; cost doubles but on Flash-Lite/Haiku-class models that is cents.

### S41. Few-shot placement, negative examples, abstention — https://arxiv.org/pdf/2606.07479 ; https://arxiv.org/pdf/2601.12471 ; https://arxiv.org/pdf/2505.18688 ; https://cleanlab.ai/blog/learn/reliable-fewshot-prompts/
- Type: paper / blog
- Verified: snippet-only
- Key facts (snippet): few-shot beat zero-shot by ~10 pts accuracy / 7 pts F1, saturating after ~20 examples (2505.18688); paired positive+negative demonstrations "largely eliminate zero-shot always-negative failure modes" but some models over-predict positives on negative splits (2606.07479); explicit abstain options: "gains in abstention rate are negligible" from few-shot alone (2601.12471). **No study found that directly compares examples in the system prompt vs the user turn** — gap.
- Relevance: include hard negatives (guest self-promotion, host reading listener mail, product mentions in editorial) as labelled negatives; do not rely on an "abstain" enum to reduce FPs — use the ladder.

### S42. Small encoders — https://arxiv.org/abs/2412.13663 (ModernBERT, 2024-12) ; https://arxiv.org/abs/2111.09543 (DeBERTaV3) ; https://arxiv.org/pdf/2312.17543 (NLI universal classifiers)
- Type: paper
- Verified: snippet-only
- Key facts (snippet): ModernBERT: 2T training tokens, native 8,192 sequence length, SOTA among encoders on classification and retrieval, "major Pareto improvement" in speed/memory; DeBERTaV3 small/xsmall beat prior same-size SOTA by >1.2% MNLI acc; NLI-fine-tuned DeBERTa classifiers reach good performance "with just a few hundred examples per class" in minutes on a free GPU.
- Relevance: a ModernBERT-base (≈149M) sentence/window classifier trained on LLM-labelled spans is feasible on a Mac CPU/MPS; 8k context lets a whole chunk be one input for a token-classification (BIO) head.

### S43. SponsorBlock-ML (Xenova) — https://github.com/xenova/sponsorblock-ml ; https://huggingface.co/Xenova/sponsorblock-classifier-v2
- Type: repo / model
- Verified: snippet-only
- Key facts (snippet): detects SPONSOR, SELFPROMO, INTERACTION segments in YouTube transcripts; two-stage: a transformer extracts candidate segments from the transcript, a BERT-style classifier labels them; trained from the SponsorBlock database (CC BY-NC-SA 4.0); pipeline downloads YouTube transcripts and builds positive/negative text windows. No evaluation metrics captured.
- Relevance: an existing open two-stage "propose then classify" design on transcripts — the hybrid architecture in question 6(c) already exists for video; licence (NC-SA on the data) constrains commercial reuse of derived weights.

### S44. Podcast-specific ad detection prior work — https://arxiv.org/abs/2103.02585 (Reddy et al., Spotify 2021) ; https://huggingface.co/morenolq/spotify-podcast-advertising-classification ; https://github.com/heidonomm/AdDetection ; https://arxiv.org/abs/2502.15102 ; US patent 12190871
- Type: paper / model / repo / legal
- Verified: snippet-only
- Key facts (snippet): Reddy et al. split transcripts into sentences and classified "extraneous content" with BERT and TF-IDF n-gram baselines, also using episode descriptions; morenolq's model is a BERT binary sentence classifier with previous-sentence context (ACM SAC 2022 "Leveraging multimodal content for podcast summarization"); 2025 paper uses ChatGPT for sponsored-ad detection in YouTube; a 2025 US patent covers deep-learning detection of dynamically inserted ads in long-form audio; Comscore launched transcript-level ad classification for Spotify/SiriusXM/Acast/Libsyn on 2026-07-22 (ppc.land). Metrics not captured — gap.
- Relevance: sentence-level BERT with one-sentence context is the published baseline for podcast ads; AdVTT's LLM-per-chunk approach has no published head-to-head against it — an experiment on the 4 fixtures would be novel.


### Run-2 fetch round A (WebFetch only; WebSearch exhausted). Results:

### S37 addendum — Anthropic Citations (detail from the saved page)
- Verified: fetched
- Key facts: plain-text documents are "chunked into sentences"; custom-content documents (recommended "for bullet points or transcripts") keep your blocks as-is and return **block indices (0-indexed)**; plain text returns `char_location` with `start_char_index` (0-indexed) / `end_char_index` (exclusive) and `cited_text`; "citations are guaranteed to contain valid pointers to the provided documents"; `cited_text` "does not count toward output tokens"; works with prompt caching and batch.
- Relevance: passing each transcript segment as one custom-content block would make Claude return *validated* segment indices (block indices) instead of free-text indices — a provider-native fix for the hallucinated-index problem, at zero extra output cost.

### S38 addendum — Anthropic prompting best practices (detail from the saved page)
- Verified: fetched
- Key facts: "Include 3–5 examples for best results", wrap in `<example>`/`<examples>` tags; "Put longform data at the top ... above your query, instructions, and examples. This improves performance across all models"; for classification "use either tools with an enum field containing your valid labels or structured outputs"; prefer positive phrasing over "Do not ..."; Opus 4.5/4.6 "more responsive to the system prompt ... may now overtrigger" — dial back aggressive language; `budget_tokens` deprecated on 4.6, **returns 400 on Claude 4.7+**; use `effort` + adaptive thinking (`thinking:{type:"adaptive"}`); "adaptive thinking reliably drives better performance than extended thinking" (internal evals). No statement about system-vs-user placement of examples.
- Relevance: (a) the current prompt layout (instructions first, transcript last) is the opposite of Anthropic's guidance — test transcript-first; (b) the project's `budget_tokens: 4000` knob will break on Claude 4.7+ and must be re-expressed as `effort`; (c) the measured FP explosion at budget 0 should be re-tested with `effort: low` vs `medium`.

### S18 addendum — Batch limits (detail from the saved page)
- Verified: fetched
- Key facts: ≤100,000 requests or 256 MB per batch; results when all complete or after 24 h; results downloadable 29 days; `max_tokens:0` not allowed; recommends the 1-hour cache TTL for shared context inside batches since batches "can take longer than 5 minutes".

### S30 (upgraded) NoLiMa — https://arxiv.org/abs/2502.05167
- Verified: fetched (abstract)
- Key facts: 13 LLMs claiming ≥128k; "at 32K, 11 models drop below 50% of their strong short-length baselines"; GPT-4o 99.3% → 69.7%; reasoning/CoT variants also "struggle to maintain performance in long contexts"; ICML 2025, v1 2025-02-07, final 2025-07-09.

### S45. Lost in the Middle (Liu et al., TACL 2023) — https://arxiv.org/abs/2307.03172
- Type: paper
- Verified: fetched (abstract)
- Key facts: multi-document QA and key-value retrieval; "performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle"; holds even for explicitly long-context models; submitted 2023-07-06.
- Relevance: mid-roll ads sit in the middle of an episode by definition; per-chunk classification puts every ad near the "ends" of some window.

### S31 (upgraded) Chroma Context Rot (2025-07-14) — https://www.trychroma.com/research/context-rot
- Verified: fetched
- Key facts: 18 models (Claude Opus 4/Sonnet 4/3.7/3.5/Haiku 3.5; o3, GPT-4.1 family, GPT-4o, GPT-4 Turbo, 3.5 Turbo; Gemini 2.5 Pro/Flash, 2.0 Flash; Qwen3-235B-A22B/32B/8B). Repeated-words task: replicate a sequence of repeated words with one unique word inserted, 25–10,000 words, 1,090 position variants — "position accuracy declines as input grows; unique words placed early are identified more reliably"; models "under-generate at longer lengths"; single distractor hurts, four compound; lower needle–question similarity accelerates decline; shuffled haystacks beat coherent ones.
- Relevance: the repeated-words result is a direct measurement of *positional counting* failing with length — the same failure as gpt-5.5 misplacing indices by ~800 segments over 3,919; coherent (non-shuffled) text is the *harder* case, which is what a transcript is.

### S32 (upgraded) Classifier Context Rot (Martin & Roger, 2026-05-12) — https://arxiv.org/abs/2605.12366
- Verified: fetched (abstract)
- Key facts: LLM monitors (Opus 4.6, GPT-5.4, Gemini 3.1) detecting dangerous actions in agent transcripts "miss dangerous actions 2× to 30× more often when they occur after 800K tokens of benign activity than when they occur on their own"; partial mitigation from "periodic reminders throughout the transcript".
- Relevance: even 2026 frontier models are context-rot-prone as *classifiers*; the "periodic reminder" mitigation maps to AdVTT re-stating the rubric per chunk (which chunking already does).

### S33 (upgraded) Reasoning's Razor (Chegini et al., Apple, 2025-10-23) — https://arxiv.org/abs/2510.21049
- Verified: fetched (abstract)
- Key facts: safety and hallucination detection classification, LLMs vs LRMs, fine-tuned and zero-shot; "reasoning improves overall accuracy, but underperforms at the low-FPR thresholds essential for practical use"; "simple ensembles combining reasoning-on and reasoning-off modes recover each approach's strengths"; "token-based scoring substantially outperforms self-reported confidence for precision-sensitive deployments".
- Relevance: two concrete recommendations for AdVTT's low-FPR regime: (1) ensemble a thinking and a non-thinking pass; (2) prefer logprob-derived scores over the verbalised `confidence` field where the provider exposes logprobs (OpenAI, llama.cpp, mlx-lm `logprobs`; not Anthropic/Gemini).

### S39 (upgraded) Tian et al. 2023; Xiong et al. ICLR 2024 — https://arxiv.org/abs/2305.14975 ; https://arxiv.org/abs/2306.13063
- Verified: fetched (abstracts)
- Key facts: Tian: on ChatGPT/GPT-4/Claude, "verbalized confidences emitted as output tokens are typically better-calibrated than the model's conditional probabilities", ≈50% relative ECE reduction; RLHF degrades token-probability calibration. Xiong: "LLMs, when verbalizing their confidence, tend to be overconfident"; consistency across sampled responses + better aggregation mitigates; "none of these techniques consistently outperform others"; white-box vs black-box AUROC gap modest (0.522–0.605).
- Relevance: verbalised confidence is usable as an *ordinal* filter but needs post-hoc calibration on the fixtures; sample-consistency (run twice, keep agreement) is the most robust black-box signal.

### S46. JSONSchemaBench (Geng et al., 2025-01) — https://arxiv.org/abs/2501.10868
- Type: paper/dataset
- Verified: fetched (abstract)
- Key facts: 10,000 real-world JSON schemas; engines Guidance, Outlines, llama.cpp, XGrammar, OpenAI, Gemini; measures efficiency, coverage of constraint types, and output quality; released on GitHub; authors include Microsoft (Nori, Horvitz) and EPFL.
- Relevance: the engines behind every AdVTT backend (llama.cpp/Ollama/LM Studio-GGUF, Outlines/LM Studio-MLX, xgrammar/vLLM, OpenAI, Gemini) are all covered — use their schema-coverage tables to pick the schema subset that every backend accepts.

### S47. Let Me Speak Freely? (Tam et al., 2024-08) — https://arxiv.org/abs/2408.02442
- Type: paper
- Verified: fetched (abstract)
- Key facts: "a significant decline in LLMs reasoning abilities under format restrictions" with stricter constraints degrading more; JSON/XML vs free-form.
- Relevance: an argument for letting the model reason in free text (or thinking) *before* the constrained JSON, i.e. do not force JSON-only decoding on a non-thinking local model; Ollama `think`, Anthropic thinking, or a two-step "analyse then emit" prompt.

### S44 (upgraded) Reddy et al. 2021 — https://arxiv.org/abs/2103.02585
- Verified: fetched (abstract only; metrics not in abstract)
- Key facts: EACL 2021; "Podcast episodes often contain material extraneous to the main content, such as advertisements"; removing it improved summarisation ROUGE. Dataset size / F1 not visible — gap remains.

### S44b. morenolq/spotify-podcast-advertising-classification (HF) — https://huggingface.co/morenolq/spotify-podcast-advertising-classification
- Type: model
- Verified: fetched
- Key facts: `bert-base-cased` binary classifier; input = sentence + preceding sentence; manually annotated podcast sentences; test split 396 samples: accuracy 92%; ad class precision 0.88 / recall 0.91; non-ad precision 0.95 / recall 0.93; paper Vaiani, La Quatra, Cagliero, Garza, ACM SAC 2022.
- Relevance: the only published per-sentence podcast-ad number found: ≈0.88 precision means ~1 in 8 flagged sentences is content — far from AdVTT's ≤5 s content-loss gate without smoothing/adjudication; but as a *proposer* stage (recall 0.91) it is credible.

### S43 (partial) Xenova/sponsorblock-classifier-v2 — https://huggingface.co/Xenova/sponsorblock-classifier-v2
- Verified: fetched — README empty; only tags (BERT, text-classification, PyTorch, 418 downloads/month). No metrics available anywhere fetched.

### S48. ModernBERT (Warner et al., 2024-12-18) — https://arxiv.org/abs/2412.13663
- Type: paper
- Verified: fetched (abstract)
- Key facts: 2T tokens, native 8,192 sequence length, SOTA across "diverse classification tasks and both single and multi-vector retrieval", "most speed and memory efficient encoder"; CC BY 4.0 paper (model weights Apache 2.0 per HF — not re-verified). Parameter sizes not in abstract (base ≈149M / large ≈395M from memory — approx.).

### S49. SetFit (Tunstall et al., 2022-09) — https://arxiv.org/abs/2209.11055
- Type: paper
- Verified: fetched (abstract)
- Key facts: contrastive fine-tuning of a sentence-transformer + light classification head; competitive with PEFT/PET few-shot methods with "orders of magnitude less parameters" and "an order of magnitude faster to train"; no prompts/verbalisers.
- Relevance: the cheapest embedding-classifier baseline for question 6(b); a few hundred LLM-labelled sentences would suffice to train.

### S40 (upgraded) Edit-level majority voting for GEC (2026-05-13) — https://arxiv.org/abs/2605.13624
- Verified: fetched (abstract)
- Key facts: training-free; sample several candidates from one model, vote at edit level; beats greedy and MBR on most of nine benchmarks across 7 languages; "stable correction quality regardless of the instruction prompts used".
- Relevance: the span analogue — sample k classifications per chunk, keep only spans (or segments) present in ≥⌈k/2⌉ samples — is a prompt-robust way to trade recall for precision.

### S26 (partial upgrade) Gemma 4 technical report — https://arxiv.org/abs/2607.02770
- Verified: fetched (abstract)
- Key facts: "dense and Mixture-of-Experts architectures, ranging from 2.3B to 31B parameters"; native multimodality with audio encoder; "a thinking mode"; "a leap in performance across STEM, multimodal, and long-context benchmarks"; submitted 2026-07-02, revised 2026-07-24. Per-benchmark numbers not in abstract (the 96.8%/96.4% RULER figures in S26 remain snippet-only).

### S50. llama.cpp Apple Silicon performance table (discussion #4167) — https://github.com/ggml-org/llama.cpp/discussions/4167
- Type: forum (maintainer benchmark)
- Verified: fetched
- Key facts (LLaMA 7B, Metal, pp512 / tg128): M2 Max 400 GB/s — Q4_0 PP 671 t/s, TG 66.0 t/s; M3 Max 300 GB/s — Q4_0 PP 760, TG 66.3; M4 Max 546 GB/s — Q4_0 PP 886, TG 83.1; M2 Ultra 800 GB/s — PP 1238, TG 94.3; M3 Ultra — PP 1471, TG 92.1. F16 TG ≈25–41 t/s.
- Relevance: for a 7B-class Q4 model, a 7k-token chunk prefill ≈ 8–10 s on M3/M4 Max; 10 chunks ≈ 1.5 min per episode; dense 27–32B models scale ~4× slower (bandwidth-bound) → ~6 min/episode, still acceptable for a batch tool.

### S51. john-rocky/apple-silicon-llm-bench — https://github.com/john-rocky/apple-silicon-llm-bench
- Type: repo (benchmark, 2026)
- Verified: fetched
- Key facts: M4 Max decode, MLX-Swift Q4 vs llama.cpp Q4_K_M: Qwen 3.5 2B 291.9 vs 149.7 t/s; Gemma 4 E2B 185.4 vs 119.2; Gemma 4 E4B 113.5 vs 80.5 ("MLX-Swift now wins decode on every cell — 1.4×–1.8×"); prefill Qwen3-8B ≈ 90–94 t/s (Core AI vs MLX) on the tested config; GPU runtimes "lose ~50–60% throughput under continuous load due to thermal throttling".
- Relevance: prefill numbers in this repo are far below llama.cpp's pp512 figures (different batch settings), so the honest planning number for an 8B model is "tens to hundreds of t/s prefill depending on runtime" — measure on the target Mac; sustained-load throttling matters for whole-archive runs.

### S52. Pricing pages that could not be fetched (documented gap)
- https://openai.com/index/introducing-gpt-oss/ → 403; https://groq.com/pricing → marketing page without prices; https://fireworks.ai/pricing → defers to docs.fireworks.ai/serverless/pricing; https://mistral.ai/pricing → only "Mistral Large $0.5 in / $1.5 out", "Batch processing ... reduces the price by 50%", "cached input tokens reduce input cost by up to 90%"; https://api-docs.deepseek.com/quick_start/pricing → model names only (deepseek-v4-flash, deepseek-v4-pro, deepseek-v4-flash-vision-exp), table not rendered; https://docs.vllm.ai/... → 429 ×3.
- Verified: fetched (pages returned, content absent)
- Relevance: Mistral Large 3 at $0.50/$1.50 with 50% batch and 90% cache is verified from the vendor; all other open-model hosting prices remain snippet-only (S21–S23).

### Run-2 fetch round B. Results:

### S53. openai/gpt-oss-20b model card (HF) — https://huggingface.co/openai/gpt-oss-20b
- Type: model
- Verified: fetched
- Key facts: gpt-oss-120b 117B total / 5.1B active, fits one 80 GB GPU; gpt-oss-20b 21B total / 3.6B active, "runs within 16GB of memory"; MXFP4 on MoE weights; Apache 2.0; released August 2025; reasoning levels low/medium/high; must use the "harmony" response format; native "structured outputs" listed; gpt-oss-20b GPQA Diamond 58.59%, SWE-bench Verified 53.2% (medium). No IFEval on card.
- Relevance: the only OpenAI-lineage model runnable on a 32 GB Mac; harmony format means Ollama/LM Studio/llama.cpp chat templates must be current or JSON output breaks (see llama.cpp discussion #15341 "gpt-oss and grammar", snippet-only in run 1).

### S54. Fireworks serverless pricing (docs) — https://docs.fireworks.ai/serverless/pricing
- Type: product (pricing)
- Verified: fetched
- Key facts (USD per 1M, input / cached / output): gpt-oss-120b 0.15 / 0.015 / 0.60 (Priority 0.18/0.018/0.72); Qwen 3.7 Plus 0.40 / 0.08 / 1.60; Qwen 3.8 Max 2.00 / 0.25 / 6.00; DeepSeek V4 Pro 1.32 / 0.044 / 3.96; DeepSeek V4 Flash 0.22 / 0.007 / 0.66; Kimi K3 3.00 / 0.30 / 15.00; size tiers for unlisted models: <4B $0.10, 4–16B $0.20, >16B $0.90, MoE ≤56B $0.50, MoE 56.1–176B $1.20 (per 1M, in=out); batch 50% off; cached input ≈10% of input.
- Relevance: confirms the gpt-oss-120b $0.15/$0.60 figure from S23 with a vendor page; DeepSeek V4 Flash via Fireworks (US-hosted) at $0.22/$0.66 sidesteps the direct-API residency question.

### S12 (upgraded) Ollama #16563 — https://github.com/ollama/ollama/issues/16563
- Verified: fetched
- Key facts: Ollama 0.30.6; Qwen 3.5 MLX and Gemma 4 MLX "ignore the schema entirely"; non-MLX variants conform; reported 2026-06-06; assigned dhiltgen; **closed via PR #17929** (fix version not stated on the issue page).
- Relevance: verify the installed Ollama version includes #17929 before trusting `format` on MLX-backed models; keep the parse rung strict either way.

### S43 (upgraded) xenova/sponsorblock-ml README — https://github.com/xenova/sponsorblock-ml
- Verified: fetched
- Key facts: two stages — a T5 (t5-small/base/large, v1.1) segment extractor + a classifier that scores categories; positive segments = sponsors, unpaid/self-promos, interaction reminders; negatives = normal content; dataset from SponsorBlock DB under CC BY-NC-SA 4.0; "accuracy (and other metrics)" mentioned, none reported; 148 commits.
- Relevance: architecture precedent for 6(c); the NC licence on the data means any AdVTT model trained on SponsorBlock cannot be shipped for commercial use — LLM-labelled podcast data avoids that.

### S35 (upgraded) Text Chunking for Document Classification (2025-03-31) — https://arxiv.org/abs/2504.00274
- Verified: fetched (abstract)
- Key facts: GPT-4o, GPT-4o-mini, o1-mini; whole-text vs chunked coding of documents; chunked approach "showed significant agreement with human raters", whole-text "may introduce multiple meanings". Chunk sizes not in abstract.
- Relevance: supports chunking over whole-episode even on frontier models, independent of the index problem.

### S36 (upgraded) Explicit Evidence Grounding via Structured Inline Citation Generation (2026-06-05) — https://arxiv.org/abs/2606.07130
- Verified: fetched (abstract)
- Key facts: LLMs "are generally effective at identifying relevant documents, they struggle to identify the precise supporting spans within them"; three strategies: prompt-based, constrained decoding over a citation grammar, post-hoc span alignment; benchmarks ASQA, BioASQ, ExpertQA.
- Relevance: "post-hoc span alignment" is exactly AdVTT's rung 5 + word-level edge refinement; the paper confirms this is the standard remedy, and that constrained citation grammars are a second option.

### S55. Anthropic — Effort parameter — https://platform.claude.com/docs/en/build-with-claude/effort
- Type: spec
- Verified: fetched
- Key facts: `output_config.effort` ∈ {low, medium, high (default), xhigh, max}; supported on Fable 5.1/5, Mythos, Opus 5/4.8/4.7/4.6/4.5, Sonnet 5/4.6 — **not listed for Haiku 4.5**; "Effort is a behavioral signal, not a strict token budget"; affects all output tokens incl. thinking; on Opus 4.7 `max` "on some structured-output or less intelligence-sensitive tasks it can lead to overthinking"; changing top-level effort between requests invalidates the prompt cache (per-message effort beta `mid-conversation-output-config-2026-07-01` preserves it on Fable 5.1/Opus 5); Sonnet 5 `medium` ≈ Sonnet 4.6 `high`; Sonnet 4.6 recommended default `medium`.
- Relevance: Haiku 4.5 (the project's Claude budget experiments) still uses `budget_tokens`; any move to Sonnet 5 / Opus 5 must switch to `effort` and hold it constant per run to keep caching.

### S26 (upgraded) Artificial Analysis — Gemma 4 (2026-04-06) — https://artificialanalysis.ai/articles/gemma-4-everything-you-need-to-know
- Verified: fetched
- Key facts: Intelligence Index: Gemma 4 31B 39, 26B-A4B 31, E4B 19, E2B 15; Qwen3.5 27B (Reasoning) 42, GLM-4.7 42; **IFBench: Gemma 4 31B 76%, matching Qwen3.5 27B**; Gemma 4 31B used 39M output tokens vs 98M for Qwen3.5-27B-Reasoning on the index (≈2.5× fewer); +29 points over Gemma 3 27B; 256k context (31B, 26B-A4B), 128k (E2B/E4B); Apache 2.0; E2B fits under 3 GB at 4-bit.
- Relevance: Gemma 4 31B is the most token-frugal strong open model — important for local latency; Qwen3.5-27B is slightly stronger but reasons ~2.5× longer.

### S56. Qwen/Qwen3.8-27B model card (HF) — https://huggingface.co/Qwen/Qwen3.8-27B
- Type: model
- Verified: fetched
- Key facts: 27B dense; context "262,144 natively and extensible up to 1,000,000 tokens"; Apache 2.0; August 2026; thinking on by default, `reasoning_effort` xhigh/medium/low, `preserve_thinking`; IFBench 79.5; GPQA Diamond 89.2; LiveCodeBench v6 90.3; vision-language included. No RULER/LongBench rows on the card. No IFEval figure.
- Relevance: at 4-bit (~15–16 GB weights) it fits a 32 GB Mac with room for a 16k context; IFBench 79.5 is the highest instruction-following score among the local candidates found.

### Run-2 fetch round C. Results:

### S44 (upgraded) Reddy et al. 2021, full PDF (extracted locally with pdftotext) — https://arxiv.org/pdf/2103.02585
- Verified: fetched (PDF text)
- Key facts: episodes sampled from the Spotify Podcast Dataset (105,360 episodes); sentences split with SpaCy, labelled extraneous if >50% of the sentence is annotated; bert-base-cased fine-tuned, plus logistic regression / SVM on TF-IDF uni+bigrams; "BERT where the model sees the previous sentence" is best. Table 3 (F1, sentence-level): Descriptions BERT 0.920 single-sentence → 0.940 with context; **Transcripts (gold) BERT 0.710 → 0.769 with context**; on transcripts "precision tends to be lower (0.690) than recall (0.870)" — the model over-flags content. Post-hoc smoothing / BiLSTM-CRF / change-point rows exist (Transcripts: sentence-level BERT 43.1 / 88.7 → BERT + Smoothing 49.1 / 90.9; another split 60.8 / 96.6 → 66.7 / 97.0; column headers not captured in extraction). Listener "dip" (skip) boundaries vs manual annotation: absolute mean error 16.0 words at starts, 35.2 words at ends; 38.4% of dips were not extraneous content. Silver training set: 82,451 episodes from listener dips. Notes "identifying native advertising" as the hard case.
- Relevance: the strongest published baseline for exactly AdVTT's task: per-sentence BERT on podcast transcripts reaches F1 ≈0.77 with precision ≈0.69 — an order of magnitude too many false positives for a ≤5 s content-loss gate; smoothing helps only modestly. This is the number a local encoder must beat and the number the LLM-per-chunk approach should be compared against on the same fixtures.

### S57. OpenAI — Reasoning guide — https://developers.openai.com/api/docs/guides/reasoning
- Type: spec
- Verified: fetched
- Key facts: `reasoning.effort` ∈ {none, minimal, low, medium, high, xhigh, max}; "Some models support only a subset"; reasoning tokens "are billed as output tokens"; `none` is recommended for "latency-critical tasks that do not benefit from any reasoning" — examples given: "voice, fast information retrieval, and classification". No statement about reasoning vs structured outputs.
- Relevance: OpenAI's own guidance nominates classification for effort `none` — the opposite of the project's Haiku observation (budget 0 → 77.5 s FP). Provider guidance is not task-specific; the fixtures must decide.

### S58. Google — Gemini thinking — https://ai.google.dev/gemini-api/docs/thinking
- Type: spec
- Verified: fetched
- Key facts: `thinking_level`: Gemini 3.7 Flash low/medium/high (default medium); 3.6 Flash minimal/low/medium/high (default medium); 3.5 Flash-Lite minimal/low/medium/high (default minimal); 2.5 Pro/Flash low/medium/high; 2.5 Flash-Lite thinking off by default; "response pricing is the sum of output tokens and thinking tokens"; `total_thought_tokens` reported. Numeric `thinkingBudget` not described on the fetched rendering.
- Relevance: on 3.x Flash the cheapest setting is `minimal`, not off; 2.5 Flash-Lite is the only current Gemini with thinking off by default — useful for a "reasoning-off" ensemble member (S33).

### S59. Anthropic — Thinking troubleshooting / per-model table — https://platform.claude.com/docs/en/build-with-claude/thinking-troubleshooting
- Type: spec
- Verified: fetched
- Key facts: **Claude Haiku 4.5, Sonnet 4.5, Opus 4.5: extended thinking only (`budget_tokens`), default off, reject `adaptive`**; Opus 4.6 / Sonnet 4.6: adaptive + deprecated extended; Opus 4.7/4.8, Sonnet 5: adaptive only, reject `enabled`; Opus 5: adaptive, on by default, `disabled` allowed only at effort ≤ high; Fable 5/5.1 and Mythos: always on, reject `disabled`. Changing thinking config, effort or budget_tokens invalidates message-cache breakpoints. On Opus 5 with thinking disabled, "tool calls or XML tags appear in the text output" more often.
- Relevance: the project's Haiku `budget_tokens` experiments are valid only for the 4.5 generation; the classifier's Claude backend needs a per-model capability map (budget_tokens vs effort) and must hold the setting fixed across all chunks of a run.

### S26 (upgraded) google/gemma-4-31b-it model card — https://huggingface.co/google/gemma-4-31b-it
- Verified: fetched
- Key facts: 30.7B params; 256k context; Apache 2.0; MMLU Pro 85.2%; GPQA Diamond 84.3%; **MRCR v2 8-needle 128k 66.4%** (this is the "66.4%" figure the run-1 snippet mislabelled as RULER); BigBench Extra Hard 74.4%; Codeforces ELO 2150. No RULER / IFEval / LongBench rows on the card; quantised memory not listed.
- Correction to S26: the 66.4% is MRCR-v2 @128k, not RULER; the 96.8%/96.4% RULER figures remain snippet-only and unverified.

### S28 (upgraded) LongBench v2 paper — https://arxiv.org/abs/2412.15204
- Verified: fetched (abstract)
- Key facts: 503 multiple-choice questions; contexts 8k–2M words; human experts 53.7% (15-min limit); best model 50.1% direct, o1-preview 57.7% with reasoning; six task categories; 2024-12-19 / 2025-01-03.

### S29 (upgraded) RULER (Hsieh et al., COLM 2024) — https://arxiv.org/abs/2404.06654
- Verified: fetched (abstract)
- Key facts: 13 tasks (NIAH variants, multi-hop tracing, aggregation, QA); 17 models; "only half of them can maintain satisfactory performance at the length of 32K" despite all claiming ≥32k.

### S41 (upgraded) Supervision vs demonstration-based ICL (Turkish LVCs, ACL SRW 2026) — https://arxiv.org/abs/2606.07479
- Verified: fetched (abstract)
- Key facts: zero-shot LLMs "strong negative detection" but "very low recall"; one-shot "sharply improves detection but can induce strong, model-specific biases" (over/under-prediction); richer multi-example prompts improve calibration; supervised BERTurk encoder "remained competitive"; gpt-oss-20b and Qwen2.5-14B robust with enriched few-shot.
- Relevance: (a) a single positive example can tip a local model into over-flagging — pair every positive with a hard negative; (b) an encoder baseline stays competitive with prompted LLMs on binary span-ish classification.

### S44c. ChatGPT for sponsored-ad detection in YouTube (2025-02) — https://arxiv.org/abs/2502.15102
- Verified: fetched (abstract)
- Key facts: 421 transcripts; prompt-engineered GPT-4o + KeyBERT; work-in-progress, **no precision/recall reported**.
- Relevance: no usable numbers; confirms the literature gap — no published LLM-vs-encoder comparison on ad-span detection exists.

### S60. Documented gaps after run 2
- OpenAI "Supported schemas" numeric limits: the section is referenced (`#supported-schemas`) but never rendered in three fetches — unverified.
- Gemini `responseSchema` / `responseJsonSchema`: absent from the current Gemini-3-era docs, which show a `response_format {type, mime_type, schema}` shape; the 2.5-era field names are presumably still accepted on `generateContent` but this was not verified.
- Calibration via self-generated distractors (ICLR 2026): OpenReview blocked by a verification screen.
- 2505.18688 (few-shot saturation at ~20 examples): only abstract accessible; the "+10 acc / +7 F1" figures remain snippet-only.
- Qwen3 (2025) IFEval, Gemma 3, Llama 3.3/4, Mistral Small 3.x/4, Phi-4, DeepSeek-R1 distills, Granite: not researched in run 2 (WebSearch exhausted); in 2026 all are superseded for the local tier by Gemma 4 / Qwen 3.6–3.8 / gpt-oss (S26, S27, S53, S56).

## Cost arithmetic — one 60-minute episode (computed 2026-09-01 from S14/S16/S19/S52/S54)

Assumptions: transcript 13,500 tok × 1.30 duplication = 17,550 tok, in 3 chunks; static prefix 2,000 tok × 3 = 6,000 tok; output 600 tok. 'No cache' bills the prefix at input price every chunk; 'cached' bills 2 of 3 prefix copies at the cache-read price (first copy at input price; 5-min write premium ignored, ≤25%). Batch = 50% on everything (all three cloud vendors). Claude 4.7+/5 rows multiply all input by 1.30 for the new tokenizer (S16). Fixed-cost local runs are $0 marginal.

| Model | $/episode no cache | $/episode cached | $/episode cached+batch | $/1,000 episodes cached | src |
|---|---|---|---|---|---|
| OpenAI gpt-5.5 | $0.1357 | $0.1178 | $0.0589 | $117.75 | S14 |
| OpenAI gpt-5.6-terra | $0.0543 | $0.0471 | $0.0236 | $47.10 | S14 |
| OpenAI gpt-5.6-luna | $0.0054 | $0.0047 | $0.0024 | $4.71 | S14 |
| OpenAI gpt-5.4-mini | $0.0204 | $0.0177 | $0.0088 | $17.66 | S14 |
| OpenAI gpt-5-nano | $0.0014 | $0.0012 | $0.0006 | $1.24 | S14 |
| Claude Opus 5 (x1.3 tok) | $0.1681 | $0.1447 | $0.0723 | $144.68 | S16 |
| Claude Sonnet 5 (x1.3 tok) | $0.0672 | $0.0579 | $0.0289 | $57.87 | S16 |
| Claude Sonnet 4.6 | $0.0796 | $0.0688 | $0.0344 | $68.85 | S16 |
| Claude Haiku 4.5 (no cache: prefix<4096) | $0.0266 | $0.0266 | $0.0133 | $26.55 | S16,S17 |
| Gemini 3.1 Pro Preview | $0.0543 | $0.0471 | $0.0236 | $47.10 | S19 |
| Gemini 3.7 Flash (promo) | $0.0199 | $0.0172 | $0.0086 | $17.21 | S19 |
| Gemini 3.5 Flash-Lite | $0.0086 | $0.0075 | $0.0037 | $7.49 | S19 |
| Gemini 3.1 Flash-Lite | $0.0068 | $0.0059 | $0.0029 | $5.89 | S19 |
| Gemini 2.5 Flash-Lite | $0.0026 | $0.0022 | $0.0011 | $2.24 | S19 |
| Mistral Large 3 (vendor page) | $0.0127 | $0.0109 | $0.0054 | $10.88 | S52 |
| gpt-oss-120b @Fireworks | $0.0039 | $0.0034 | $0.0017 | $3.35 | S54 |
| DeepSeek V4 Flash @Fireworks | $0.0056 | $0.0047 | $0.0024 | $4.72 | S54 |
| Qwen 3.7 Plus @Fireworks | $0.0104 | $0.0091 | $0.0046 | $9.10 | S54 |

Reading: the whole cloud spread is ~$0.002 (gpt-5-nano, Gemini 2.5 Flash-Lite) to ~$0.15 (gpt-5.5, Opus 5) per hour of audio; a two-provider ensemble on Flash-Lite-class models costs under half a cent per episode. Output tokens are ≤15% of cost everywhere because the classifier emits only spans.

### Run-2 fetch round D. Results:

### S61. OpenAI — gpt-5.5 model page — https://developers.openai.com/api/docs/models/gpt-5.5
- Type: spec
- Verified: fetched
- Key facts: context 1,050,000 tokens; max output 128,000; reasoning effort "supports: none, low, medium (default), high and xhigh"; structured outputs, function calling, prompt caching, batch all supported; knowledge cutoff 2025-12-01; $5 / $0.50 cached / $30; >272k-token prompts billed at 2× input, 1.5× output.
- Relevance: the project's current cloud model defaults to `medium` reasoning — the FP measurements taken so far are at an unstated effort; `none` is available for the reasoning-off ensemble member (S33) and is what OpenAI recommends for classification (S57).

### S62. Ollama library — gemma4 — https://ollama.com/library/gemma4
- Type: product
- Verified: fetched
- Key facts: tags e2b (7.2 GB, 128k), e4b (9.6 GB, 128k), 12b (7.6 GB, 256k), 26b MoE (19 GB, 256k), 31b (20 GB, 256k); `-mlx` variants of each; cloud variants; 24M pulls; 26b updated one week ago.
- Relevance: on a 32 GB Mac the 26B-MoE (19 GB) leaves ~10 GB for KV cache and the OS — enough for one 16k-token request; the 31B dense (20 GB) is similar in footprint but ~5× slower to decode (bandwidth-bound, 30.7B vs 3.8B active). On 64 GB both are comfortable. Note the `-mlx` tags are exactly the backend with the structured-output bug (S11/S12) unless the fix from PR #17929 is present.

### S63. aider — edit formats & "unified diffs" post (2023-12-21) — https://aider.chat/docs/more/edit-formats.html ; https://aider.chat/2023/12/21/unified-diffs.html
- Type: blog / docs (practitioner report)
- Verified: fetched (both)
- Key facts: "GPT is terrible at working with source code line numbers" — aider strips `@@` line numbers from diff hunk headers and locates hunks by content; switching GPT-4 Turbo from SEARCH/REPLACE blocks to line-number-free unified diffs raised its refactor benchmark from 20% to 61% (June GPT-4: 26% → 59%); Gemini models "often fail to conform to the fencing approach" so a "diff-fenced" variant exists.
- Relevance: the most widely deployed practitioner evidence that content anchors beat numeric positions for LLM-emitted locations; directly analogous to index-based vs quote-anchored spans. Also a reminder that output-format robustness is model-family-specific (Gemini fencing), so the parse rung should stay lenient about wrappers while strict about content.

### S64. Vertex AI "control generated output" page — https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output
- Type: spec
- Verified: fetched (redirect followed; page rendered only as a navigation index)
- Key facts: the legacy `responseSchema` (OpenAPI-subset) documentation was not retrievable; the site now files structured output under a "Gemini Enterprise Agent Platform" tree. Gap stands (see S3, S60).

## Synthesis

**1. Structured output is now universal, but the *common* schema subset is small, and local MLX is the weak spot.**
OpenAI (`text.format`/`response_format` strict, S1), Anthropic (`output_config.format` + strict tools, GA, S2) and Gemini (`response_format {type,mime_type,schema}` on 3.x, S3) all constrain to a schema server-side. The intersection that every provider and every local engine accepts is: objects with `additionalProperties:false` and all keys required, primitive enums, arrays, `anyOf`, internal `$ref`, **no numeric bounds, no string length bounds, no recursion** (Anthropic forbids min/max and recursion, S2; Gemini and llama.cpp allow more, S3/S6). Locally, llama.cpp/llama-server (S6/S7), Ollama's GGUF runner (S4/S5) and LM Studio (both engines, S10) enforce schemas; `mlx_lm.server` has no such field at all (S9), and Ollama's MLX runner silently ignored `format` until PR #17929 (S11/S12). Every engine that constrains sampling does *not* show the schema to the model (S6/S7), so the prompt must still describe the output. Two literature caveats: constrained decoding can degrade reasoning quality (S47), and engines differ in schema coverage (JSONSchemaBench, S46) — so "reason in free text or thinking, then emit constrained JSON" is the safe pattern, and the parse rung must treat schema non-compliance as a first-class outcome, not an exception.

**2. Cost is a non-issue at the per-episode level; the levers are caching floors and batch.**
The full computed spread is ≈$0.002 (gpt-5-nano, Gemini 2.5 Flash-Lite) to ≈$0.15 (gpt-5.5, Opus 5) per hour of audio (cost table above; S14/S16/S19/S54). Output is ≤15% of cost because the classifier emits only spans. Prompt caching helps only if the static prefix clears the model's floor: 1,024 tokens on GPT-5.6+ (S15), 1,024 on Sonnet 5/4.6, **4,096 on Haiku 4.5** (S17), 4,096 on Gemini 3.x Flash (S20) — a 2k-token rubric caches on OpenAI/Sonnet but not on Haiku or Gemini 3.x Flash. All three vendors give 50% for batch (S14/S16/S19), and Anthropic's batch stacks with caching (S16/S18). Two 2026 pricing facts change the Claude picture: Sonnet 5 is $2/$10 (cheaper than Sonnet 4.6, S16) and 4.7+ models tokenize ≈30% more tokens (S16). Third-party open-model hosting (gpt-oss-120b $0.15/$0.60, S54) sits between Flash-Lite and Haiku.

**3. Local models have caught up for this task class.**
The 2025 list in the brief (Qwen3, Gemma 3, Llama 3.3/4, Mistral Small 3.x, Phi-4, R1 distills, Granite) is superseded: Gemma 4 (2026-04, Apache 2.0; 26B-A4B 19 GB, 31B 20 GB on Ollama, S26/S62), Qwen 3.8-27B (2026-08, Apache 2.0, IFBench 79.5, 262k ctx, S56) and gpt-oss-20b (2025-08, 16 GB, S53) are the candidates for 32–64 GB Macs. Independent numbers: Gemma 4 31B IFBench 76% = Qwen3.5-27B, Intelligence Index 39 vs 42, but 2.5× fewer output tokens (S26); Qwen3.5-27B scores 60.6% on LongBench v2, within 4 points of the best frontier model (S28); Gemma 4 31B MRCR-v2 8-needle @128k 66.4% (S26 card). Throughput: 30B-A3B-class MoE decodes 70–100 tok/s on M4 Max (S24, snippet), gpt-oss-20b ≈100 tok/s decode / ≈1.5k tok/s prefill on M4 Max via MLX (S25, snippet); llama.cpp 7B-Q4 prefill 670–1,470 tok/s across M2 Max→M3 Ultra (S50, fetched); sustained runs lose ~50–60% to thermal throttling (S51). A 60-min episode (3 chunks × ~7.5k tokens) is therefore ~30–90 s of prefill on a 20–30B model — comparable to cloud latency, at $0.

**4. Indices are the wrong primary anchor; quotes are the right one.** Convergent evidence from four independent directions: (a) Chroma's repeated-words experiment shows positional accuracy degrading with length even for the trivial task of naming where a unique word sits, and coherent text is *harder* than shuffled (S31); (b) aider found "GPT is terrible at working with source code line numbers" and doubled its benchmark by removing them (S63); (c) span-grounding research finds LLMs locate documents well but "struggle to identify the precise supporting spans", and remedies are verbatim quotes + post-hoc alignment or constrained citation grammars (S36); (d) Anthropic's Citations feature returns *validated* block or char indices from verbatim `cited_text`, at zero output-token cost (S37). The project's own 800-segment misplacement over 3,919 segments and its existing rung-5 quote check are the same finding.

**5. Chunking is justified by more than the index bug.** Lost-in-the-middle (S45), RULER (only half of 17 models held at 32k, S29), NoLiMa (11/13 below half their baseline at 32k when lexical overlap is removed, S30), Context Rot (degradation at every length step, S31), Classifier Context Rot (2026 frontier monitors miss events 2–30× more after long benign context, S32) and a chunked-vs-whole classification study (S35) all point the same way. Host-read ads with no jingle are the low-lexical-overlap case NoLiMa isolates.

**6. Reasoning: the literature and the project disagree, and the resolution is an ensemble, not a budget.** Reasoning's Razor finds reasoning raises accuracy but *lowers* recall at fixed low FPR for safety/hallucination classification, and recommends (i) reasoning-on/off ensembles and (ii) token-probability scores over self-reported confidence (S33); OpenAI recommends effort `none` for classification (S57). The project measured the opposite on Haiku 4.5 (budget 0 → 77.5 s FP vs 2 s at 4000). Both can be true: the Razor result is about thresholding a score; AdVTT's failure is un-thresholded over-generation on a small model without thinking. Budget-scaling studies show diminishing returns beyond moderate budgets and confirmation bias at high effort (S34). Mechanically, `budget_tokens` exists only on the 4.5 generation; 4.7+ rejects it and uses `effort` (S55/S59); Gemini 3.x Flash cannot go below `minimal` (S58); gpt-5.5 supports `none` (S61).

**7. Verbalised confidence is ordinal at best.** Tian 2023 (verbalised beats token probabilities on RLHF models, S39) is qualified by Xiong 2024 (systematic overconfidence, no method consistently best, S39) and 2024–26 follow-ups. Agreement across samples or providers is the robust black-box signal (S39/S40); edit-level majority voting is the closest published analogue to voting over spans (S40); multi-model over-inclusion was "in most cases only one model" (S40).

**8. Prompting evidence is thin but consistent.** 3–5 examples in `<example>` tags (S38); one-shot positives can bias small models toward over-prediction, richer paired demonstrations calibrate (S41); an "abstain" enum did not help abstention rates (S41); no study compares examples in system vs user turn (S41 gap); Anthropic says put long documents *above* instructions and examples (S38) — which conflicts with caching-friendly static-prefix-first layouts (S15/S17); with a ~2k prefix the cache saving is <10% of per-chunk cost, so accuracy layout should win unless the prefix grows past ~4k.

**9. Small-encoder baselines exist and are not good enough alone.** Reddy et al. (Spotify, EACL 2021): per-sentence BERT with previous-sentence context, F1 0.769 on transcripts, precision 0.690 vs recall 0.870, smoothing/CRF helps only a few points; description text is much easier (F1 0.94) (S44). A public BERT sentence classifier reports 0.88 ad-precision on 396 test sentences (S44b). SponsorBlock-ML is a two-stage T5 proposer + classifier on NC-licensed data (S43). ModernBERT (8k native context, S48) and SetFit (few-hundred-example training, S49) make a *proposer* cheap to train on AdVTT's own LLM-labelled outputs; NLI-style DeBERTa classifiers train on hundreds of examples (S42). No published LLM-vs-encoder comparison on ad spans exists (S44c gap).

**Contradictions to flag:** (i) reasoning helps vs hurts precision (S33/S57 vs project); (ii) "documents first" (S38) vs "static prefix first" (S15/S17); (iii) DeepSeek pricing differs across trackers by 2× (S22); (iv) the run-1 snippet's "Gemma 4 RULER 66.4%" was actually MRCR-v2 (S26 correction).

## Implications for AdVTT

1. **Default models per tier.** *Cloud-quality:* Claude Sonnet 5 ($2/$10, structured outputs GA, 1,024-token cache floor, S2/S16/S17) or OpenAI gpt-5.6-terra ($2/$12, S14) — both ≈$0.04–0.05/episode; keep gpt-5.5 only as an evaluation reference (3× the price, S14/S61). *Cloud-cheap:* Gemini 3.1 Flash-Lite ($0.25/$1.50, free tier, S19) or gpt-5.6-luna ($0.20/$1.20, S14), ≈$0.006/episode; gpt-oss-120b via Fireworks ($0.15/$0.60, S54) when an open model is required. *Local:* Gemma 4 26B-A4B through Ollama's GGUF runner or LM Studio (schema enforcement, 19 GB, S10/S12/S62) on 32 GB; Qwen 3.8-27B (S56) or Gemma 4 31B (S26) on 64 GB; gpt-oss-20b as the 16 GB fallback (S53). Avoid `mlx_lm.server` and Ollama `-mlx` tags for JSON until PR #17929 is confirmed (S9/S11/S12).
2. **Make the quote the primary anchor and derive the index.** Ask for `start_quote`/`end_quote` (5–12 words each, verbatim) plus an *optional* index hint; resolve quotes against the chunk text with the existing word-stream matcher; drop spans whose quotes do not resolve instead of halving confidence (S31, S36, S63). On Claude, pass segments as custom-content document blocks and read block indices from citations, which the API guarantees valid (S37).
3. **Replace "thinking budget" with a two-member ensemble where the FP asymmetry matters.** Run a reasoning-on pass and a reasoning-off/`none`/`minimal` pass (same or different provider) and keep only intersecting spans; on Flash-Lite/luna-class models this costs <$0.01/episode (cost table, S33, S40, S57/S58/S61). Encode a per-model capability map: `budget_tokens` for Claude 4.5, `output_config.effort` for 4.6+, `reasoning.effort` for OpenAI, `thinking_level` for Gemini (S55/S58/S59/S61); hold it constant per run to keep caches (S17/S59).
4. **Stop using the model's `confidence` for gating.** Use k-sample or two-provider agreement as the confidence; if a numeric score is still reported, calibrate it on the fixtures (temperature/Platt on the verbalised value) and label it as such in `analysis.json` (S39/S40). Where the backend exposes logprobs (OpenAI, llama.cpp, mlx-lm), record the first-token logprob of the `kind` enum as an additional score (S33).
5. **Schema and prompt hygiene.** Ship one schema in the cross-provider subset (no min/max, no recursion, `additionalProperties:false`, S2/S3/S46); never change it mid-run (24 h grammar cache + prompt cache, S2/S17); keep the "return JSON matching this shape" text in the prompt for local engines (S6/S7); set Ollama `num_ctx` ≥ 16k explicitly (S5); test transcript-first layout against rubric-first (S38 vs S15/S17); include 3–5 paired positive/hard-negative examples (guest self-promo, listener mail, editorial product mentions) in `<example>` tags (S38/S41); do not add an "abstain" label (S41).
6. **Chunk-size experiment.** Evidence favours smaller chunks for recall and no precision penalty (S35); test 3k vs 6k windows with the same ±12-segment context on the four fixtures, measuring `content_loss_sec`, `ad_recall_sec`, `boundary_err_sec` and the merge rate across chunk boundaries (S30/S31/S45).
7. **A distilled local encoder is a realistic v2 *proposer*, not a v2 classifier.** Published per-sentence precision on podcast transcripts is 0.69–0.88 (S44/S44b), far from a ≤5 s content-loss gate; but recall 0.87–0.91 makes a ModernBERT/SetFit proposer (S48/S49) trained on AdVTT's own LLM-labelled spans viable: it selects candidate regions, and the LLM adjudicates only those (typically 5–15% of an episode), cutting cloud cost and local latency 5–10×. Train on self-generated labels, not SponsorBlock (CC BY-NC-SA, S43). Needs far more than four fixtures — bootstrap labels with the two-provider ensemble (impl. 3).
8. **Add an archive/batch mode.** For whole-library runs submit all chunks as one Message Batch / OpenAI Batch / Gemini batch at 50% with the 1-hour cache TTL (S14/S16/S18/S19); PodcastFetch re-consumption fits this shape.
9. **Handle silent non-compliance.** Detect free-text-instead-of-JSON (S11/S12), refusals (S1), and empty thinking-only outputs as distinct rejection reasons in `analysis.json`; they are backend bugs, not "no ads".

## Open questions / things that need an experiment

1. Effort sweep on all four fixtures per provider: Claude Haiku 4.5 budget {0, 1024, 4000} vs Sonnet 5 effort {low, medium, high}; gpt-5.6-terra/luna effort {none, low, medium}; Gemini 3.1 Flash-Lite {minimal, low, medium}. Does the 77.5 s-vs-2 s FP effect reproduce off Haiku? (S33/S34/S57)
2. Intersection ensemble: measure `ad_recall_sec` loss vs `content_loss_sec` gain for (reasoning-on ∩ reasoning-off) and (provider A ∩ provider B). (S33/S40)
3. Quote-anchored vs index-anchored output on the same chunks: resolution rate, boundary error, and whether models with quote-only output stop producing spans in long chunks (under-generation, S31).
4. Chunk size 3k vs 6k vs 12k with fixed context margins (S35), and whole-episode single-call as the negative control, on both Sonnet 5 and Gemma 4 26B.
5. Local structured output matrix: Ollama GGUF vs Ollama MLX (post-#17929) vs LM Studio MLX vs llama-server, same schema, 100 chunks: compliance rate and latency (S6/S10/S11/S12/S46).
6. Does transcript-first prompt layout (S38) beat rubric-first, and what does it cost in cache hits (S15/S17)?
7. Prefill throughput on the target Mac for Gemma 4 26B-A4B and Qwen 3.8-27B at 8k and 16k prompts, sustained over 50 chunks (throttling, S51).
8. Encoder proposer: train ModernBERT-base BIO tagger on LLM-labelled spans from ≥200 episodes; report proposer recall at 95% and the fraction of audio forwarded to the LLM (S44/S48/S49).
9. Verify OpenAI's numeric schema limits and Gemini's `responseJsonSchema` subset directly against the APIs (S60).
10. Whether verbalised `confidence` correlates with fixture correctness at all (AUROC), before deciding to keep the field (S39).
