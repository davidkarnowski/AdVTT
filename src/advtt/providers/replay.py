"""Recorded-response replay (Research/08 §6, 12 WP2).

Every live call can be recorded under
    <store>/<sha256(prompt_version | model_id | system + user)>.json
and replayed later with no network and no key. The classifier seam is the
only place recording happens, so CI runs offline in seconds and a weekly live
canary can compare against the same store.
"""

import hashlib
import json
import os

from .base import AdProvider, ProviderError

DEFAULT_STORE = os.environ.get("ADVTT_REPLAY_STORE") or os.path.join(os.getcwd(), "tests", "replay")


def replay_key(prompt_version, model_id, system, user):
    h = hashlib.sha256()
    h.update((prompt_version or "").encode("utf-8"))
    h.update(b"|")
    h.update((model_id or "").encode("utf-8"))
    h.update(b"|")
    h.update(system.encode("utf-8"))
    h.update(b"\n\x00\n")
    h.update(user.encode("utf-8"))
    return h.hexdigest()


class ReplayProvider(AdProvider):
    """Serves recorded responses; raises ProviderError when none is recorded."""

    name = "replay"
    cloud = False
    default_model = "recorded"
    max_chunk_tokens = 6000

    def __init__(self, model=None, endpoint=None, store=None, prompt_version=None):
        AdProvider.__init__(self, model=model, endpoint=endpoint or "local:replay")
        self.store = store or (endpoint if endpoint and os.path.isdir(endpoint) else None) or DEFAULT_STORE
        self.prompt_version = prompt_version

    def ensure_ready(self, probe=False):
        if not os.path.isdir(self.store):
            return False, "replay store %s does not exist" % self.store
        return True, "replay store %s (%d responses)" % (
            self.store, len([f for f in os.listdir(self.store) if f.endswith(".json")]))

    def complete_json(self, system, user, schema, timeout=180):
        from ..validate import PROMPT_VERSION
        key = replay_key(self.prompt_version or PROMPT_VERSION, self.model, system, user)
        path = os.path.join(self.store, key + ".json")
        if not os.path.exists(path):
            raise ProviderError("no recorded response for %s (model %s)" % (key[:12], self.model))
        with open(path, "r", encoding="utf-8") as f:
            rec = json.load(f)
        meta = dict(rec.get("meta") or {})
        meta.setdefault("raw_text", rec.get("raw_text") or "")
        meta["replayed_from"] = key
        return rec.get("obj") or {}, meta


class RecordingProvider(AdProvider):
    """Wraps a live provider and writes every response into the replay store."""

    def __init__(self, inner, store=None, prompt_version=None):
        self.inner = inner
        self.name = inner.name
        self.cloud = inner.cloud
        self.model = inner.model
        self.endpoint = inner.endpoint
        self.max_chunk_tokens = inner.max_chunk_tokens
        self.store = store or DEFAULT_STORE
        self.prompt_version = prompt_version

    def ensure_ready(self, probe=False):
        return self.inner.ensure_ready(probe=probe)

    def warm_up(self):
        return self.inner.warm_up()

    def web_search_answer(self, task, timeout=120):
        return self.inner.web_search_answer(task, timeout=timeout)

    def complete_json(self, system, user, schema, timeout=180):
        from ..validate import PROMPT_VERSION
        obj, meta = self.inner.complete_json(system, user, schema, timeout=timeout)
        key = replay_key(self.prompt_version or PROMPT_VERSION, self.model, system, user)
        os.makedirs(self.store, exist_ok=True)
        rec = {"provider": self.inner.name, "model": self.model,
               "prompt_version": self.prompt_version or PROMPT_VERSION,
               "obj": obj, "raw_text": meta.get("raw_text") or "",
               "meta": {k: v for k, v in meta.items() if k not in ("raw_text", "raw")}}
        tmp = os.path.join(self.store, key + ".json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        os.replace(tmp, os.path.join(self.store, key + ".json"))
        meta["recorded_as"] = key
        return obj, meta
