"""Anthropic via the local `claude` CLI in print mode. The live Anthropic path
for this project: it uses the user's existing Claude Code login and needs no
API key, which matters because there is no budget for API access.

Adapted from PodcastFetch adclass.py ClaudeCLIProvider (lines 893-1049, commit
74692de). The measured history in that docstring is preserved below because it
is why the defaults are what they are.
"""

import json
import os
import shutil
import subprocess
import time

from .base import AdProvider, ProviderError, _extract_json_object
from .capabilities import EFFORT_LEVELS, capabilities, resolve_model


class ClaudeCLIProvider(AdProvider):
    """Anthropic via `claude -p` -- no API key needed.

    History (PodcastFetch, 2026-08-31, claude-haiku-4-5), which shaped the flags:

        as-shipped default        222 s   21,042 output tokens   $0.2182
        --tools ""                171 s   15,853               $0.1988
        + MAX_THINKING_TOKENS=0    17 s    1,574               $0.1139
        warm prompt cache          18 s    1,594               $0.0467

    The answer itself is ~500 tokens of JSON in every run; the rest was
    extended thinking, generated serially, which is the whole of the latency.
    Those thinking tokens are NOT waste. Scored against the fixtures with only
    the thinking budget changed:

        thinking off    content_loss 96.5s   recall 0.987   JRE episode  65 s
        thinking 4000   content_loss  8.6s   recall 0.993   JRE episode 260 s
        (ship gate is content_loss_sec <= 5.0)

    So the cheap-and-fast setting is the one that silently skips journalism,
    and the budget is left at the CLI default unless set explicitly.

    What changed since (verified 2026-09-06, CLI 2.1.263):

    * `--json-schema` gives real structured output. The envelope carries the
      parsed object in `structured_output`; `result` holds the same JSON as a
      string. The adapter prefers `structured_output` and falls back to
      extracting JSON from `result`, so older CLIs still work.
    * `--effort low|medium|high|xhigh|max` controls thinking depth on models
      that take effort (Sonnet 5, Opus 5, 4.6+). On Haiku 4.5 the budget path
      (`MAX_THINKING_TOKENS`) still applies. The capability map decides.
    * With `--tools ""` and `--exclude-dynamic-system-prompt-sections` the
      fixed per-call prefix measured 8,572 cache-creation tokens on a trivial
      call, not the ~26k seen with tools enabled.

    Every call still pays Claude Code's system-prompt prefix; for archive-scale
    work the Messages-API adapter with batch pricing is cheaper once a key
    exists. This adapter exists so a machine with a logged-in CLI is not stuck.
    """

    name = "claude-cli"
    cloud = True
    default_model = "claude-sonnet-5"
    # Chunk like the other adapters: index tracking, not context, is the limit.
    max_chunk_tokens = 6000
    # Generous: thinking runs serially and long chunks can take minutes.
    default_timeout = 420
    BINARY = "claude"

    def __init__(self, model=None, endpoint=None, effort=None, thinking_budget=None):
        AdProvider.__init__(self, model=resolve_model(model or self.default_model),
                            endpoint=endpoint or "local:claude-cli")
        self.effort = effort
        self.thinking_budget = thinking_budget
        self.use_json_schema = os.environ.get("ADVTT_CLI_JSON_SCHEMA", "1") != "0"

    def _binary(self):
        return shutil.which(self.BINARY)

    def ensure_ready(self, probe=False):
        path = self._binary()
        if not path:
            return False, "`claude` CLI not on PATH"
        cap = capabilities(self.model)
        return True, "claude CLI at %s (model %s, %s%s)" % (
            path, self.model, cap["reasoning"],
            (" effort=%s" % self.effort) if self.effort else "")

    def describe(self):
        d = AdProvider.describe(self)
        d["effort"] = self.effort
        d["json_schema"] = self.use_json_schema
        return d

    def _command(self, path, system, schema):
        cap = capabilities(self.model)
        cmd = [path, "-p", "--output-format", "json",
               "--model", self.model,
               # No tool is useful for labelling a transcript, and every tool
               # definition is system-prompt weight on every call.
               "--tools", "",
               # Move cwd/env/git sections out of the system prompt so the
               # cached prefix is identical across calls and across episodes.
               "--exclude-dynamic-system-prompt-sections"]
        if self.use_json_schema:
            cmd += ["--json-schema", json.dumps(schema, separators=(",", ":"))]
            instruction = system
        else:
            # The schema cannot be enforced, so state it in-band and demand bare JSON.
            instruction = (system
                           + "\n\nRespond with a single JSON object matching this schema, and nothing else:\n"
                           + json.dumps(schema))
        if self.effort and cap["reasoning"] == "effort":
            if self.effort not in EFFORT_LEVELS:
                raise ProviderError("effort must be one of %s" % ", ".join(EFFORT_LEVELS))
            cmd += ["--effort", self.effort]
        cmd += ["--append-system-prompt", instruction]
        return cmd

    def complete_json(self, system, user, schema, timeout=180):
        # Honour the adapter's own floor: the caller's default is tuned for API
        # providers that do not carry a fixed per-call tax.
        timeout = max(timeout, getattr(self, "default_timeout", timeout))
        path = self._binary()
        if not path:
            raise ProviderError("`claude` CLI not on PATH")
        cmd = self._command(path, system, schema)

        env = dict(os.environ)
        # Thinking budget (Haiku 4.5 path). Left at the CLI default unless set:
        # measured, budget 0 is the setting that silently skips journalism.
        budget = self.thinking_budget
        if budget is None and os.environ.get("ADVTT_CLI_THINKING") is not None:
            budget = os.environ.get("ADVTT_CLI_THINKING")
        if budget is not None:
            env["MAX_THINKING_TOKENS"] = str(budget)

        t0 = time.time()
        try:
            proc = subprocess.run(cmd, input=user, capture_output=True, text=True,
                                  timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            raise ProviderError("claude CLI timed out after %ss" % timeout)
        except OSError as e:
            raise ProviderError("claude CLI failed to start: %s" % e)

        # `wall_sec` is the key the chunk recorder reads.
        meta = {"wall_sec": round(time.time() - t0, 2), "raw": (proc.stdout or "")[:2000]}
        if proc.returncode != 0:
            # A failing CLI usually explains itself in the stdout JSON envelope
            # ("is_error": true, usage-limit text), not on stderr; measured
            # 2026-09-06 when 15 JRE runs logged an empty reason.
            reason = (proc.stderr or "").strip() or (proc.stdout or "").strip()
            raise ProviderError("claude CLI exited %s: %s"
                                % (proc.returncode, reason[:300]))

        try:
            envelope = json.loads(proc.stdout)
        except ValueError:
            # Older CLI builds may print bare text even with --output-format json.
            obj = _extract_json_object(proc.stdout or "")
            meta["raw_text"] = (proc.stdout or "")[:20000]
            if obj is None:
                meta["parse_error"] = "CLI output was neither an envelope nor JSON"
                return {}, meta
            return obj, meta

        if envelope.get("is_error"):
            raise ProviderError("claude CLI reported an error: %s"
                                % str(envelope.get("result"))[:300])

        usage = envelope.get("usage") or {}
        details = usage.get("output_tokens_details") or {}
        meta.update({
            "prompt_tokens": usage.get("input_tokens"),
            "completion_tokens": usage.get("output_tokens"),
            "thinking_tokens": details.get("thinking_tokens"),
            "cache_read_tokens": usage.get("cache_read_input_tokens"),
            "cache_write_tokens": usage.get("cache_creation_input_tokens"),
            "cost_usd": envelope.get("total_cost_usd"),
            "stop_reason": envelope.get("stop_reason"),
            "num_turns": envelope.get("num_turns"),
            "effort": self.effort,
        })
        result_text = envelope.get("result") or ""
        meta["raw_text"] = result_text if isinstance(result_text, str) else json.dumps(result_text)

        # A refusal or an empty answer is a distinct outcome, not "no ads".
        if envelope.get("subtype") not in (None, "success"):
            meta["parse_error"] = "CLI subtype %s" % envelope.get("subtype")
            return {}, meta

        so = envelope.get("structured_output")
        if isinstance(so, dict):
            return so, meta
        obj = _extract_json_object(result_text if isinstance(result_text, str) else "")
        if obj is None:
            meta["parse_error"] = "could not extract a JSON object from CLI result"
            return {}, meta
        return obj, meta
