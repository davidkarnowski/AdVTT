"""Google Gemini adapter. Unavailable in this environment by decision; exercised through replay only."""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 1050-1168. Do not edit the moved bodies without bumping PROMPT_VERSION
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


def _gemini_schema(node):
    """Translate our JSON Schema into Gemini's OpenAPI-flavoured subset.

    Gemini wants uppercase type names, rejects `additionalProperties`, and takes
    enums only on strings. Converting here keeps one schema definition shared by
    every provider rather than maintaining a second copy that can drift.
    """
    if not isinstance(node, dict):
        return node
    t = node.get("type")
    out = {}
    if t:
        out["type"] = {"object": "OBJECT", "array": "ARRAY", "string": "STRING",
                       "number": "NUMBER", "integer": "INTEGER",
                       "boolean": "BOOLEAN"}.get(t, str(t).upper())
    if "properties" in node:
        out["properties"] = {k: _gemini_schema(v) for k, v in node["properties"].items()}
    if "items" in node:
        out["items"] = _gemini_schema(node["items"])
    if "required" in node:
        out["required"] = list(node["required"])
    if "enum" in node and out.get("type") == "STRING":
        out["enum"] = list(node["enum"])
    return out


class GeminiProvider(AdProvider):
    """Google AI Studio (Gemini) via the generativelanguage REST API.

    Structured output is native: responseMimeType application/json plus a
    responseSchema, so the reply parses without coaxing. Uses the same chunking
    as every other provider -- the million-token context is not a reason to send
    a whole episode, because index tracking, not context, is the binding
    constraint (see OpenAIProvider.max_chunk_tokens).
    """

    name = "gemini"
    cloud = True
    default_model = "gemini-2.5-flash"
    max_chunk_tokens = 6000
    DEFAULT_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"
    KEY_NAMES = ("GOOGLE_STUDIO_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY")

    def __init__(self, model=None, endpoint=None):
        AdProvider.__init__(self, model=model, endpoint=endpoint or self.DEFAULT_ENDPOINT)

    def _key(self):
        for name in self.KEY_NAMES:
            val = os.environ.get(name, "").strip()
            if val:
                return val
        return ""

    def ensure_ready(self, probe=False):
        if not self._key():
            return False, "no Google key set (%s)" % " / ".join(self.KEY_NAMES)
        return True, "Google key present (model %s)" % self.model

    def complete_json(self, system, user, schema, timeout=180):
        key = self._key()
        if not key:
            raise ProviderError("no Google API key set")

        body = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
                "responseSchema": _gemini_schema(schema),
            },
        }
        url = "%s/models/%s:generateContent?key=%s" % (self.endpoint, self.model, key)

        t0 = time.time()
        attempts = 0
        while True:
            attempts += 1
            code, parsed, raw, hdrs = _http_json_h(url, payload=body, timeout=timeout)
            # 503 "model is overloaded" is routine on the flash models and is
            # exactly as transient as a 429. Retrying only the 429 meant an
            # overloaded minute silently cost the episode a chunk -- observed
            # 2026-08-31: 2 of 13 chunks on the JRE fixture, still written as ok.
            if code not in (429, 500, 502, 503, 504) or attempts >= 4:
                break
            wait = float(hdrs.get("retry-after") or (20 if code == 429 else 5 * attempts))
            GLOBAL_LOG("  [rate] %d from gemini; retrying in %.0fs (attempt %d)"
                       % (code, wait + 1, attempts))
            time.sleep(min(90.0, wait + 1.0))

        if code != 200 or not isinstance(parsed, dict):
            raise ProviderError("gemini HTTP %s: %s" % (code, raw[:400]))

        cands = parsed.get("candidates") or []
        if not cands:
            fb = (parsed.get("promptFeedback") or {}).get("blockReason")
            raise ProviderError("gemini returned no candidates%s" % (" (%s)" % fb if fb else ""))
        cand = cands[0]
        finish = cand.get("finishReason")
        parts = ((cand.get("content") or {}).get("parts") or [])
        text = "".join(p.get("text") or "" for p in parts)

        usage = parsed.get("usageMetadata") or {}
        meta = {
            "raw_text": text,
            "prompt_tokens": usage.get("promptTokenCount"),
            "completion_tokens": usage.get("candidatesTokenCount"),
            "wall_sec": round(time.time() - t0, 2),
            "stop_reason": finish,
        }
        if finish == "MAX_TOKENS":
            meta["parse_error"] = "truncated at max tokens"
        obj = _extract_json_object(text)
        if obj is None:
            meta["parse_error"] = meta.get("parse_error") or "could not extract a JSON object"
            return {}, meta
        return obj, meta
