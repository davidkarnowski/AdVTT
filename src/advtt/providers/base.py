"""Provider seam: the AdProvider base class, HTTP helpers and JSON extraction.

Invariants that travel with this module (Research/01 §2):
* every adapter is stdlib-only (urllib), no SDKs;
* `make_provider` (registry.py) never falls back from a local provider to a cloud one;
* a parse failure is reported in meta['parse_error'] and handled by the caller
  (validation ladder rung 1), never retried inside the adapter.
"""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 197-270, 271-346, 347-389. Do not edit the moved bodies without bumping PROMPT_VERSION
# where the prompt or ladder behaviour changes; see Research/01 and 12.
import json
import re
import urllib.error
import urllib.request


def GLOBAL_LOG(msg):
    """Progress line for long, paced cloud runs. Quiet unless something waits."""
    print(msg, flush=True)


def _http_json_h(url, payload=None, headers=None, timeout=60, method=None):
    """Like _http_json but also returns the response headers (lowercased)."""
    data = None
    hdrs = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs,
                                 method=method or ("POST" if data else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            rh = {k.lower(): v for k, v in dict(resp.headers).items()}
            try:
                return resp.status, json.loads(raw), raw, rh
            except ValueError:
                return resp.status, None, raw, rh
    except urllib.error.HTTPError as e:
        raw = ""
        try:
            raw = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        rh = {}
        try:
            rh = {k.lower(): v for k, v in dict(e.headers).items()}
        except Exception:
            pass
        try:
            return e.code, json.loads(raw), raw, rh
        except ValueError:
            return e.code, None, raw, rh
    except Exception as e:
        return 0, None, str(e), {}


def _http_json(url, payload=None, headers=None, timeout=60, method=None):
    """POST/GET JSON. Returns (status_code, parsed_or_None, raw_text)."""
    data = None
    hdrs = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        hdrs["Content-Type"] = "application/json"
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method or ("POST" if data else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw), raw
            except ValueError:
                return resp.status, None, raw
    except urllib.error.HTTPError as e:
        raw = ""
        try:
            raw = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        try:
            return e.code, json.loads(raw), raw
        except ValueError:
            return e.code, None, raw
    except Exception as e:
        raise ProviderError("%s: %s" % (type(e).__name__, e))


class ProviderError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Provider abstraction
# --------------------------------------------------------------------------

class AdProvider:
    """Base class. Subclasses talk to one LLM backend and return parsed JSON."""

    name = "base"
    cloud = False
    default_model = ""
    max_chunk_tokens = 1500

    def __init__(self, model=None, endpoint=None):
        self.model = model or self.default_model
        self.endpoint = (endpoint or "").rstrip("/") or None

    def available(self):
        """Cheap, non-throwing check: can we plausibly use this provider?

        Never touches the network — this feeds the settings UI, where one live
        call per adapter per panel open would be four wasted round-trips. Live
        verification is ensure_ready(probe=True), made once per run.
        """
        return self.ensure_ready(probe=False)[0]

    def ensure_ready(self, probe=False):
        """(ok, message). Message explains what is missing when ok is False.

        `probe=True` permits one cheap live call; adapters without a probe
        ignore it. Callers that run once per job should probe, so a key that is
        present but unusable is caught before the work starts rather than on
        every episode.
        """
        raise NotImplementedError

    def warm_up(self):
        """Optional: pay one-time model load cost up front."""
        return None

    def complete_json(self, system, user, schema, timeout=180):
        """Returns (parsed_dict, meta). meta always carries `raw_text`.

        On a parse failure `parsed_dict` is {} and meta['parse_error'] is set;
        the caller decides what to do (see validate ladder step 1).
        """
        raise NotImplementedError

    def web_search_answer(self, task, timeout=120):
        """Answer `task` using the provider's NATIVE web-search tool call, or
        None when this backend has no such tool (the caller then skips web
        verification). The healing passes use this instead of any local search
        stack — the selected LLM does its own searching (§ user decision
        2026-08-11: no SearXNG/self-hosted search; LLM tool calls only)."""
        return None

    def describe(self):
        ok, msg = (False, "")
        try:
            ok, msg = self.ensure_ready(probe=False)
        except Exception as e:
            ok, msg = False, "probe failed: %s" % e
        return {
            "name": self.name,
            "cloud": self.cloud,
            "model": self.model,
            "endpoint": self.endpoint,
            "max_chunk_tokens": self.max_chunk_tokens,
            "available": ok,
            "detail": msg,
        }


def _extract_json_object(text):
    """Pull the first balanced {...} out of `text`. Returns dict or None.

    Grammar-constrained decoding usually makes this unnecessary, but a model can
    still emit a <think> preamble or trailing prose.
    """
    if not text:
        return None
    try:
        return json.loads(text)
    except ValueError:
        pass
    # Strip common reasoning wrappers first.
    text = re.sub(r"<think>.*?</think>", " ", text, flags=re.S)
    depth = 0
    start = -1
    in_str = False
    esc = False
    for i, ch in enumerate(text):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    return json.loads(text[start:i + 1])
                except ValueError:
                    start = -1
    return None
