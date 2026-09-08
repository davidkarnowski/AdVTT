"""Structured event log for agents and CI (JSON Lines).

`advtt --log-json PATH` (or `-` for stderr) emits one JSON object per event:
    {"ts": ISO, "event": "run.start", ...}
Events: run.start, input.loaded, provider.ready, chunk.done, gate, output.written,
run.done, error. Fields are stable and additive; consumers must ignore unknown
keys. This is the machine-readable counterpart of the human progress lines.
"""

import json
import sys
import time
from datetime import datetime, timezone


class EventLog:
    def __init__(self, path=None):
        self.path = path
        self._fh = None
        self.t0 = time.time()
        if path == "-":
            self._fh = sys.stderr
        elif path:
            self._fh = open(path, "a", encoding="utf-8")

    def emit(self, event, **fields):
        if not self._fh:
            return
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
               "elapsed_sec": round(time.time() - self.t0, 3), "event": event}
        rec.update(fields)
        self._fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        self._fh.flush()

    def close(self):
        if self._fh and self._fh is not sys.stderr:
            self._fh.close()


class LoggingProvider:
    """Wraps a provider so every chunk call emits a chunk.done event."""

    def __init__(self, inner, log):
        self.inner = inner
        self.log = log
        for attr in ("name", "cloud", "model", "endpoint", "max_chunk_tokens", "effort"):
            if hasattr(inner, attr):
                setattr(self, attr, getattr(inner, attr))

    def ensure_ready(self, probe=False):
        ok, msg = self.inner.ensure_ready(probe=probe)
        self.log.emit("provider.ready", provider=self.inner.name, model=self.inner.model, ok=ok, detail=msg)
        return ok, msg

    def warm_up(self):
        return self.inner.warm_up()

    def web_search_answer(self, task, timeout=120):
        return self.inner.web_search_answer(task, timeout=timeout)

    def describe(self):
        return self.inner.describe()

    def complete_json(self, system, user, schema, timeout=180):
        self.log.emit("chunk.start", provider=self.inner.name, model=self.inner.model, prompt_chars=len(user))
        try:
            obj, meta = self.inner.complete_json(system, user, schema, timeout=timeout)
        except Exception as e:
            self.log.emit("chunk.error", provider=self.inner.name, error=str(e)[:300])
            raise
        self.log.emit("chunk.done", provider=self.inner.name, model=self.inner.model,
                      wall_sec=meta.get("wall_sec"), prompt_tokens=meta.get("prompt_tokens"),
                      completion_tokens=meta.get("completion_tokens"), thinking_tokens=meta.get("thinking_tokens"),
                      cost_usd=meta.get("cost_usd"), parse_error=meta.get("parse_error"),
                      spans=len((obj or {}).get("ad_spans") or []) if isinstance(obj, dict) else None)
        return obj, meta
