"""oMLX local inference adapter."""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 701-811. Do not edit the moved bodies without bumping PROMPT_VERSION
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


class OMLXProvider(AdProvider):
    """oMLX — a local OpenAI-compatible MLX inference server on Apple Silicon.

    Same wire format as the OpenAI adapter, three differences that matter:

    * **Local.** Nothing leaves the machine, so this is the only cloud-free path
      to speaker attribution and name healing besides Ollama. `cloud = False`
      means make_provider will never silently substitute it for a cloud
      provider, or vice versa.
    * **No enforced structured output.** oMLX needs xgrammar for that and this
      install was built without it, so `response_format` is accepted and
      ignored. The schema is therefore also stated in-band and the reply goes
      through the same balanced-brace extractor the CLI adapter uses. The
      validation ladder does not care where the JSON came from.
    * **Slow, and one model resident at a time.** ~9-10 tok/s on an M-series
      16 GB box, so a chunk costs minutes rather than seconds, and switching
      models mid-run can trip the server's memory guard. Chunk size is left at
      the project default: making chunks bigger to save calls would trade the
      accuracy mechanism for wall-clock, which is the wrong direction.

    Config comes from OMLX_BASE_URL / OMLX_API_KEY (this project's .env, same as
    every other provider key).
    """

    name = "omlx"
    cloud = False
    default_model = "Qwen3-8B-4bit"
    max_chunk_tokens = 6000
    DEFAULT_ENDPOINT = "http://127.0.0.1:11435"
    # Generous: generation is ~9 tok/s, so a 700-token answer is over a minute
    # before prefill of a 6k-token chunk is counted.
    default_timeout = 900

    def __init__(self, model=None, endpoint=None):
        AdProvider.__init__(self, model=model,
                            endpoint=(endpoint or os.environ.get("OMLX_BASE_URL")
                                      or self.DEFAULT_ENDPOINT).rstrip("/"))

    @staticmethod
    def _key():
        return os.environ.get("OMLX_API_KEY", "").strip()

    def _headers(self):
        key = self._key()
        return {"Authorization": "Bearer " + key} if key else {}

    def list_models(self):
        code, parsed, raw, _h = _http_json_h(self.endpoint + "/v1/models",
                                             headers=self._headers(), timeout=10)
        if code != 200 or not isinstance(parsed, dict):
            raise ProviderError("unexpected /v1/models response (HTTP %s): %s"
                                % (code, (raw or "")[:120]))
        return [m.get("id", "") for m in parsed.get("data", []) or []]

    def ensure_ready(self, probe=False):
        try:
            names = self.list_models()
        except ProviderError as e:
            return False, "oMLX not reachable at %s (%s)" % (self.endpoint, e)
        except Exception as e:
            return False, "oMLX not reachable at %s (%s)" % (self.endpoint, str(e)[:120])
        if not names:
            return False, "oMLX is up but serving no models"
        if self.model not in names:
            return False, "oMLX has no model %r (serving: %s)" % (self.model, ", ".join(names[:6]))
        return True, "oMLX ready at %s (model %s)" % (self.endpoint, self.model)

    def complete_json(self, system, user, schema, timeout=180):
        timeout = max(timeout, getattr(self, "default_timeout", timeout))
        # Stated in-band because enforcement is not available; harmless when it is.
        instruction = (system
                       + "\n\nRespond with a single JSON object matching this schema, "
                         "and nothing else:\n" + json.dumps(schema))
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": instruction},
                         {"role": "user", "content": user}],
            "temperature": 0,
            "max_tokens": 8192,
            # Sent in case the server was built with xgrammar; ignored otherwise.
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": "ad_spans", "strict": True,
                                                "schema": schema}},
        }
        t0 = time.time()
        code, parsed, raw, _hdrs = _http_json_h(self.endpoint + "/v1/chat/completions",
                                                payload=body, headers=self._headers(),
                                                timeout=timeout)
        if code != 200 or not isinstance(parsed, dict):
            raise ProviderError("oMLX HTTP %s: %s" % (code, (raw or "")[:400]))
        # The server reports load/guard problems as an HTTP 200 with an error body.
        if parsed.get("error") or parsed.get("server_error"):
            raise ProviderError("oMLX error: %s"
                                % str(parsed.get("error") or parsed.get("server_error"))[:300])
        choice = (parsed.get("choices") or [{}])[0]
        text = ((choice.get("message") or {}).get("content")) or ""
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
