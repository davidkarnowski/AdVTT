"""Ollama local adapter (never exercised on a real episode; kept for parity)."""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 390-479. Do not edit the moved bodies without bumping PROMPT_VERSION
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


class OllamaProvider(AdProvider):
    """Local Ollama. Default and first-class: the user runs this on-box."""

    name = "ollama"
    cloud = False
    default_model = "qwen3:8b"
    max_chunk_tokens = 1500
    DEFAULT_ENDPOINT = "http://127.0.0.1:11434"

    def __init__(self, model=None, endpoint=None):
        AdProvider.__init__(self, model=model, endpoint=endpoint or self.DEFAULT_ENDPOINT)
        self._warmed = False

    def list_models(self):
        code, parsed, _raw = _http_json(self.endpoint + "/api/tags", timeout=2)
        if code != 200 or not isinstance(parsed, dict):
            raise ProviderError("unexpected /api/tags response (HTTP %s)" % code)
        return [m.get("name", "") for m in parsed.get("models", []) or []]

    def ensure_ready(self, probe=False):
        try:
            names = self.list_models()
        except ProviderError as e:
            return False, "ollama not reachable at %s (%s)" % (self.endpoint, e)
        if not names:
            return False, "ollama is up but no models are installed"
        # Accept both `qwen3:8b` and a bare `qwen3` written by the user.
        want = self.model
        bare = {n.split(":")[0] for n in names}
        if want in names or want in bare or (":" not in want and want in bare):
            return True, "ollama ready at %s (model %s)" % (self.endpoint, self.model)
        return False, "model '%s' not pulled — run: ollama pull %s" % (want, want)

    def warm_up(self):
        if self._warmed:
            return
        try:
            _http_json(
                self.endpoint + "/api/chat",
                payload={
                    "model": self.model,
                    "stream": False,
                    "messages": [{"role": "user", "content": "hi"}],
                    "options": {"temperature": 0, "num_predict": 1, "seed": 7},
                },
                timeout=600,
            )
        except ProviderError:
            pass
        self._warmed = True

    def complete_json(self, system, user, schema, timeout=180):
        # First call may pay a cold model-load cost.
        eff_timeout = timeout if self._warmed else max(timeout, 600)
        body = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "format": schema,
            "options": {
                "temperature": 0,
                "num_ctx": 8192,
                "num_predict": 1536,   # roster+corrections+splits+fixes+spans can pass 1280
                "seed": 7,
            },
        }
        t0 = time.time()
        code, parsed, raw = _http_json(self.endpoint + "/api/chat", payload=body, timeout=eff_timeout)
        self._warmed = True
        if code != 200 or not isinstance(parsed, dict):
            raise ProviderError("ollama HTTP %s: %s" % (code, raw[:400]))
        text = (parsed.get("message") or {}).get("content", "") or ""
        meta = {
            "raw_text": text,
            "prompt_tokens": parsed.get("prompt_eval_count"),
            "completion_tokens": parsed.get("eval_count"),
            "wall_sec": round(time.time() - t0, 2),
            "provider_duration_sec": round((parsed.get("total_duration") or 0) / 1e9, 2),
            "stop_reason": parsed.get("done_reason"),
        }
        obj = _extract_json_object(text)
        if obj is None:
            meta["parse_error"] = "could not extract a JSON object"
            return {}, meta
        return obj, meta
