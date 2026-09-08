"""OpenAI adapter. Unavailable in this environment by decision; exercised through replay only."""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 480-700. Do not edit the moved bodies without bumping PROMPT_VERSION
# where the prompt or ladder behaviour changes; see Research/01 and 12.
import json
import os
import re
import shutil
import subprocess
import time
import urllib.parse

from .base import (AdProvider, ProviderError, GLOBAL_LOG, _http_json,
                   _http_json_h, _extract_json_object)


class OpenAIProvider(AdProvider):
    """OpenAI chat completions with structured outputs (strict mode)."""

    name = "openai"
    cloud = True
    default_model = "gpt-5.5"
    # 128k context vs a ~21k-token worst-case episode: one chunk per episode.
    # Deliberately far below the context window. Measured on a 3919-segment
    # episode: unchunked, gpt-5.5 found the right sponsor text but misplaced the
    # indices badly (Superpower reported at segment 1245, truly at 445), and the
    # evidence check demoted almost everything. Chunked at 6000 it matched
    # hand-labelled ground truth exactly at 0.98-0.99 confidence. Index tracking
    # degrades over long inputs regardless of how much context the model accepts.
    max_chunk_tokens = 6000
    DEFAULT_ENDPOINT = "https://api.openai.com/v1"

    def __init__(self, model=None, endpoint=None):
        AdProvider.__init__(self, model=model, endpoint=endpoint or self.DEFAULT_ENDPOINT)

    # A 429 means one of two unrelated things. These codes are the billing one.
    _BILLING_CODES = ("insufficient_quota", "credit_balance_exhausted",
                      "billing_hard_limit_reached", "account_deactivated")

    @classmethod
    def _is_billing_429(cls, raw):
        low = (raw or "").lower()
        return any(c in low for c in cls._BILLING_CODES)

    @staticmethod
    def _billing_message(raw):
        try:
            err = (json.loads(raw or "{}").get("error") or {})
            return (err.get("message") or err.get("code") or "no credits remaining")[:160]
        except (ValueError, AttributeError):
            return "no credits remaining"

    def ensure_ready(self, probe=True):
        """Key presence, then one cheap live call.

        A key that is present but out of credit used to pass this check and then
        fail on every episode of the run, three retries at a time, writing
        status "failed" with no visible cause. One 16-token probe up front turns
        an hour of silent failure into one honest line before any work starts.
        """
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            return False, "OPENAI_API_KEY not set (.env or environment)"
        if not probe:
            return True, "OPENAI_API_KEY present (model %s)" % self.model
        try:
            code, _parsed, raw, _hdrs = _http_json_h(
                self.endpoint + "/chat/completions",
                payload={"model": self.model,
                         "messages": [{"role": "user", "content": "ping"}],
                         "max_completion_tokens": 16},
                headers={"Authorization": "Bearer " + key},
                timeout=30)
        except Exception as exc:                      # network down, DNS, TLS
            return False, "cannot reach %s: %s" % (self.endpoint, str(exc)[:120])
        if code == 200:
            return True, "OPENAI_API_KEY valid (model %s)" % self.model
        if code == 429 and self._is_billing_429(raw):
            return False, "openai billing: %s" % self._billing_message(raw)
        if code == 429:
            # Rate-limited right now, but funded and reachable: the pacer handles it.
            return True, "OPENAI_API_KEY present, rate-limited at probe time (model %s)" % self.model
        if code in (401, 403):
            return False, "OPENAI_API_KEY rejected (HTTP %s)" % code
        if code == 404:
            return False, "model %s not available to this account" % self.model
        return False, "openai HTTP %s: %s" % (code, (raw or "")[:160])

    # Tokens-per-minute pacing. The account tier, not the model context, is the
    # binding constraint here: gpt-4o allows 30k TPM on this org while its context
    # window is 128k, so a 38k-token episode is refused outright and a burst of
    # smaller chunks drains the minute. Rather than switch to a weaker model that
    # happens to have a higher cap, spend the budget at the rate it is granted.
    _tpm_limit = None
    _tpm_spent = []          # [(timestamp, tokens)] within the trailing minute
    _temperature_ok = True   # cleared if the model refuses an explicit temperature

    @staticmethod
    def _model_rejects_temperature(model):
        """Fixed-temperature models: gpt-5.5+, and o-series reasoning models."""
        m = re.match(r"gpt-(\d+)(?:\.(\d+))?", model or "")
        if m:
            return (int(m.group(1)), int(m.group(2) or 0)) >= (5, 5)
        return (model or "").startswith(("o1", "o3", "o4"))

    def _tpm_wait(self, need):
        if not self._tpm_limit:
            return
        while True:
            now = time.time()
            type(self)._tpm_spent = [(t, n) for t, n in self._tpm_spent if now - t < 60.0]
            used = sum(n for _, n in self._tpm_spent)
            if used + need <= self._tpm_limit * 0.95:
                return
            oldest = min((t for t, _ in self._tpm_spent), default=now)
            sleep_for = max(1.0, 60.0 - (now - oldest) + 0.5)
            GLOBAL_LOG("  [rate] %d/%d TPM used; waiting %.0fs" % (used, self._tpm_limit, sleep_for))
            time.sleep(sleep_for)

    def _tpm_record(self, tokens):
        type(self)._tpm_spent.append((time.time(), tokens))

    def web_search_answer(self, task, timeout=120):
        """Web-grounded answer via the Responses API's built-in web_search tool.

        Free-text out by design: search grounding and strict JSON schema don't
        combine reliably, so the caller structures the findings with a normal
        complete_json() second step."""
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            return None
        est = len(task) // 4 + 700
        self._tpm_wait(est)
        code, parsed, raw, _h = _http_json_h(
            self.endpoint + "/responses",
            payload={"model": self.model, "input": task,
                     "tools": [{"type": "web_search"}]},
            headers={"Authorization": "Bearer " + key},
            timeout=timeout,
        )
        if code != 200 or not isinstance(parsed, dict):
            GLOBAL_LOG("  [openai] web_search unavailable (HTTP %s): %s" % (code, (raw or "")[:160]))
            return None
        self._tpm_record(((parsed.get("usage") or {}).get("total_tokens")) or est)
        texts = []
        for item in parsed.get("output") or []:
            if isinstance(item, dict) and item.get("type") == "message":
                for c in item.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "output_text" and c.get("text"):
                        texts.append(c["text"])
        return "\n".join(texts).strip() or None

    def complete_json(self, system, user, schema, timeout=180):
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not key:
            raise ProviderError("OPENAI_API_KEY not set")
        est_tokens = (len(system) + len(user)) // 4 + 800
        self._tpm_wait(est_tokens)
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "ad_spans", "strict": True, "schema": schema},
            },
        }
        # Newer models (gpt-5.5 and up, plus the o-series reasoning models)
        # accept only the default temperature and reject an explicit 0 outright.
        # Known rejectors are skipped up front — otherwise every subprocess
        # wastes one 400 round-trip relearning it — and the 400 fallback below
        # still covers models this version check doesn't know about.
        if type(self)._temperature_ok and not self._model_rejects_temperature(self.model):
            body["temperature"] = 0
        t0 = time.time()
        attempts = 0
        while True:
            attempts += 1
            code, parsed, raw, hdrs = _http_json_h(
                self.endpoint + "/chat/completions",
                payload=body,
                headers={"Authorization": "Bearer " + key},
                timeout=timeout,
            )
            # Learn the real ceiling from the response rather than assuming one.
            lim = hdrs.get("x-ratelimit-limit-tokens")
            if lim and str(lim).isdigit():
                type(self)._tpm_limit = int(lim)
            if code == 400 and "temperature" in (raw or "").lower() and type(self)._temperature_ok:
                type(self)._temperature_ok = False
                body.pop("temperature", None)
                GLOBAL_LOG("  [openai] %s rejects temperature=0; retrying without it" % self.model)
                continue
            if code == 429 and self._is_billing_429(raw):
                # OpenAI returns 429 for two unrelated conditions: "too fast"
                # and "no money". Backing off from an exhausted balance just
                # burns 90s per episode and still fails, so this one is fatal
                # and says why -- the sidecar's error is what the dashboard
                # shows, and "adscan failed" with no reason is useless.
                raise ProviderError(
                    "openai billing: %s — add credits or switch --ad-provider "
                    "(gemini / claude-cli / ollama)" % self._billing_message(raw))
            if code != 429 or attempts >= 4:
                break
            wait = hdrs.get("retry-after") or hdrs.get("x-ratelimit-reset-tokens") or "20"
            try:
                wait = float(str(wait).rstrip("s"))
            except ValueError:
                wait = 20.0
            GLOBAL_LOG("  [rate] 429 from openai; retrying in %.0fs (attempt %d)" % (wait + 1, attempts))
            time.sleep(min(90.0, wait + 1.0))

        if code != 200 or not isinstance(parsed, dict):
            raise ProviderError("openai HTTP %s: %s" % (code, raw[:400]))
        self._tpm_record(((parsed.get("usage") or {}).get("total_tokens")) or est_tokens)
        choice = (parsed.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        if msg.get("refusal"):
            raise ProviderError("openai refusal: %s" % str(msg.get("refusal"))[:200])
        text = msg.get("content") or ""
        usage = parsed.get("usage") or {}
        meta = {
            "raw_text": text,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "wall_sec": round(time.time() - t0, 2),
            "stop_reason": choice.get("finish_reason"),
        }
        obj = _extract_json_object(text)
        if obj is None:
            meta["parse_error"] = "could not extract a JSON object"
            return {}, meta
        return obj, meta
