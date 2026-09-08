"""Anthropic Messages API adapter, stdlib urllib only (decision C.1).

Dormant until ANTHROPIC_API_KEY exists: `ensure_ready` reports the missing
key and nothing here ever crashes without one. Exercised through the replay
store in tests. Adapted from PodcastFetch adclass.py ClaudeProvider (lines
812-892, commit 74692de) and brought to the current API on 2026-09-06:

* structured outputs via `output_config.format` (unchanged);
* thinking: omitted (adaptive) on effort-class models, with
  `output_config.effort` when the caller sets one; `budget_tokens` only on
  budget-class models (Haiku 4.5), never on the 5-family where it is a 400;
* `stop_reason: refusal` and `max_tokens` are reported as distinct outcomes;
* no `temperature` (removed on current models; never set here anyway).
"""

import os
import time

from .base import AdProvider, ProviderError, _extract_json_object, _http_json
from .capabilities import EFFORT_LEVELS, capabilities, resolve_model


class ClaudeProvider(AdProvider):
    name = "claude"
    cloud = True
    default_model = "claude-sonnet-5"
    max_chunk_tokens = 6000   # chunk like every other adapter: indexing, not context, is the limit
    DEFAULT_ENDPOINT = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"

    def __init__(self, model=None, endpoint=None, effort=None, thinking_budget=None):
        AdProvider.__init__(self, model=resolve_model(model or self.default_model),
                            endpoint=endpoint or self.DEFAULT_ENDPOINT)
        self.effort = effort
        self.thinking_budget = thinking_budget

    @staticmethod
    def _key():
        return os.environ.get("ANTHROPIC_API_KEY", "").strip()

    def ensure_ready(self, probe=False):
        if not self._key():
            return False, "ANTHROPIC_API_KEY not set (.env or environment)"
        return True, "ANTHROPIC_API_KEY present (model %s)" % self.model

    def _body(self, system, user, schema, max_tokens):
        cap = capabilities(self.model)
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_config": {"format": {"type": "json_schema", "schema": schema}},
        }
        if cap["reasoning"] == "effort":
            if self.effort:
                if self.effort not in EFFORT_LEVELS:
                    raise ProviderError("effort must be one of %s" % ", ".join(EFFORT_LEVELS))
                body["output_config"]["effort"] = self.effort
            # thinking omitted: adaptive by default on these models
        elif self.thinking_budget:
            budget = int(self.thinking_budget)
            if budget >= 1024:
                body["thinking"] = {"type": "enabled", "budget_tokens": min(budget, max_tokens - 1)}
        return body

    def _call(self, system, user, schema, timeout, max_tokens):
        key = self._key()
        if not key:
            raise ProviderError("ANTHROPIC_API_KEY not set")
        return _http_json(
            self.endpoint + "/messages",
            payload=self._body(system, user, schema, max_tokens),
            headers={"x-api-key": key, "anthropic-version": self.API_VERSION},
            timeout=timeout,
        )

    def complete_json(self, system, user, schema, timeout=180):
        t0 = time.time()
        max_tokens = 16000
        code, parsed, raw = self._call(system, user, schema, timeout, max_tokens)
        if code in (429, 529) or code >= 500:
            raise ProviderError("claude HTTP %s (transient): %s" % (code, raw[:300]))
        if code != 200 or not isinstance(parsed, dict):
            raise ProviderError("claude HTTP %s: %s" % (code, raw[:400]))
        stop = parsed.get("stop_reason")
        if stop == "max_tokens":
            max_tokens = 32000
            code, parsed, raw = self._call(system, user, schema, timeout, max_tokens)
            if code != 200 or not isinstance(parsed, dict):
                raise ProviderError("claude HTTP %s (retry): %s" % (code, raw[:400]))
            stop = parsed.get("stop_reason")
        text = ""
        for block in parsed.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "text":
                text += block.get("text") or ""
        usage = parsed.get("usage") or {}
        meta = {
            "raw_text": text,
            "prompt_tokens": usage.get("input_tokens"),
            "completion_tokens": usage.get("output_tokens"),
            "cache_read_tokens": usage.get("cache_read_input_tokens"),
            "wall_sec": round(time.time() - t0, 2),
            "stop_reason": stop,
            "model": parsed.get("model"),
            "effort": self.effort,
        }
        if stop == "refusal":
            details = parsed.get("stop_details") or {}
            meta["parse_error"] = "refusal (%s)" % (details.get("category") or "unspecified")
            return {}, meta
        if stop == "max_tokens":
            meta["parse_error"] = "response truncated even at max_tokens=%d" % max_tokens
            return {}, meta
        obj = _extract_json_object(text)
        if obj is None:
            meta["parse_error"] = "could not extract a JSON object"
            return {}, meta
        return obj, meta
