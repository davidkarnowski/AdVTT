"""The pure classification core: `classify_segments(segments, provider, ...)`.

Extracted from PodcastFetch adclass.py `_run_pass` (lines 2694-2779) and
`classify_file` (2871-3027), commit 74692de, minus file I/O, caching and the
speaker task. Everything path-shaped stays with the caller: PodcastFetch files
results into its `_ads.json` sidecars, the advtt CLI writes the canonical record.

The speaker task rides in the same model call through a `TaskExtension`
(Research/01 §4). With `extension=None` the prompt and schema are byte-identical
to the historical speaker-blind classifier.
"""

import sys
import time
from datetime import datetime

from .chunking import plan_chunks
from .prompts import SYSTEM_PROMPT, build_user_prompt, response_schema
from .providers.base import ProviderError
from .refine import refine_span_edges
from .validate import (
    EVIDENCE_LOOKAHEAD, LADDER_VERSION, MAX_AD_FRACTION, MAX_SPAN_SECONDS, MIN_SEGMENTS, PROMPT_VERSION, RAW_TRUNCATE,
    SCHEMA_VERSION, STATUS_FAILED, STATUS_OK, STATUS_REJECTED_DEGENERATE,
    STATUS_REJECTED_OVERLABEL, compute_stats, episode_duration, episode_gates,
    flags_from_spans, merge_spans, state_for, validate_chunk,
)


class TaskExtension:
    """Hook for a second task that rides in the same model call.

    PodcastFetch passes a SpeakerExtension; the advtt CLI passes None. The
    fragments are merged into the system prompt, the response schema and each
    chunk's user prompt; `collect` receives every chunk's raw response and
    `finalize` returns the block the caller attaches to the result under
    `result_key`. The extension may append to the shared `rejections` list.

    Byte-stability rule: when no extension is given, nothing here runs and the
    assembled prompt equals the historical one. The extension is responsible
    for reproducing its own historical prompt exactly (tags as a separate tab
    column, header lines in the historical order).
    """

    prompt_version_suffix = ""   # folded into the effective prompt_version
    result_key = "extension"     # key under which finalize()'s block is attached

    def system_fragment(self):
        """Text appended to SYSTEM_PROMPT."""
        return ""

    def schema_fragment(self):
        """{property_name: json_schema} merged into the response schema; all required."""
        return {}

    def begin(self, segments):
        """Per-pass mutable state handed to every other hook."""
        return {}

    def header_lines(self, segments, a, b, state):
        """Extra header lines for the window [a, b), inserted after the episode hint."""
        return []

    def line_tag(self, i, state):
        """Tag column for segment i (a string) or None for no column."""
        return None

    def collect(self, chunk_id, raw_obj, segments, a, b, rejections, state):
        """Receive one chunk's parsed response."""
        return None

    def finalize(self, state, rejections):
        """Return the block to attach to the result, or None."""
        return None


def effective_prompt_version(extension=None):
    """PROMPT_VERSION, plus the ladder version when the ladder is not the legacy
    one, plus any extension suffix. Replay keys use PROMPT_VERSION alone because
    model responses depend only on the prompt text."""
    ladder = ("+" + LADDER_VERSION) if EVIDENCE_LOOKAHEAD > 0 else ""
    return PROMPT_VERSION + ladder + (getattr(extension, "prompt_version_suffix", "") or "")


def _base_result(provider, segments, sha, status, extension=None, **extra):
    out = {
        "schema_version": SCHEMA_VERSION,
        "prompt_version": effective_prompt_version(extension),
        "status": status,
        "provider": getattr(provider, "name", "none"),
        "model": getattr(provider, "model", None),
        "classified_at": datetime.now().isoformat(timespec="seconds"),
        "processing_time_sec": 0.0,
        "source_sha256": sha,
        "segment_count": len(segments),
        "duration_sec": episode_duration(segments),
        "flags": "",
        "spans": [],
        "stats": {"ad_spans": 0, "ad_segments": 0, "ad_seconds": 0.0,
                  "ad_fraction": 0.0, "uncertain_segments": 0},
        "chunks": [],
        "rejections": [],
    }
    out.update(extra)
    return out


def _run_pass(provider, segments, max_chunk_tokens, episode_hint, rejections, timeout=180,
              extension=None):
    """One full pass over the episode. Returns (spans, chunk_records, ext_state).

    `ext_state` is None without an extension, else the extension's per-pass
    state after every chunk has been collected (not yet finalized).
    """
    schema = response_schema(extension)
    system = SYSTEM_PROMPT + (extension.system_fragment() or "") if extension is not None else SYSTEM_PROMPT
    plan = plan_chunks(segments, max_chunk_tokens)
    all_spans = []
    records = []
    state = extension.begin(segments) if extension is not None else None
    for ci, ch in enumerate(plan):
        a, b = ch["start"], ch["end"]
        user = build_user_prompt(segments, a, b, episode_hint=episode_hint,
                                 extension=extension, state=state)
        rec = {"index": ci, "start_index": a, "end_index": b - 1, "est_tokens": ch["est_tokens"]}
        try:
            obj, meta = provider.complete_json(system, user, schema, timeout=timeout)
        except ProviderError as e:
            rec["error"] = str(e)[:400]
            rejections.append({"chunk": ci, "reason": "provider error: %s" % str(e)[:200], "raw": ""})
            records.append(rec)
            continue
        rec["prompt_tokens"] = meta.get("prompt_tokens")
        rec["completion_tokens"] = meta.get("completion_tokens")
        rec["wall_sec"] = meta.get("wall_sec")
        rec["stop_reason"] = meta.get("stop_reason")
        if meta.get("cost_usd") is not None:
            rec["cost_usd"] = meta.get("cost_usd")
        if meta.get("parse_error"):
            rec["error"] = meta["parse_error"]
            rejections.append({"chunk": ci, "reason": meta["parse_error"],
                               "raw": (meta.get("raw_text") or "")[:RAW_TRUNCATE]})
            records.append(rec)
            continue
        spans = validate_chunk(obj, segments, a, b, rejections, chunk_id=ci)
        rec["spans"] = len(spans)
        if extension is not None:
            extension.collect(ci, obj, segments, a, b, rejections, state)
        records.append(rec)
        all_spans.extend(spans)

    # Seam handling: spans were already clipped to their window; now merge across
    # adjacent chunks (gap <= 1 segment), taking the MIN confidence.
    merged = merge_spans(all_spans, gap=1)
    kept = []
    for sp in merged:
        sp["start"] = round(float(segments[sp["start_index"]].get("start") or 0.0), 2)
        sp["end"] = round(float(segments[sp["end_index"]].get("end") or sp["start"]), 2)
        sp["state"] = state_for(sp["confidence"])
        sp.pop("evidence_ok", None)
        # Re-apply the duration cap AFTER the seam merge. The per-chunk check in
        # validate_chunk cannot see a span that only becomes over-long once two
        # chunks' spans are joined across a window boundary.
        if sp["end"] - sp["start"] > MAX_SPAN_SECONDS:
            rejections.append({"chunk": -1,
                               "reason": "merged span [%d,%d] is %.1fs, over the %.0fs cap"
                                         % (sp["start_index"], sp["end_index"],
                                            sp["end"] - sp["start"], MAX_SPAN_SECONDS),
                               "raw": ""})
            continue
        kept.append(sp)
    return kept, records, state


def classify_segments(segments, provider, *, max_chunk_tokens=None, episode_hint="",
                      max_fraction=MAX_AD_FRACTION, timeout=180, extension=None,
                      source_sha256=None, verbose=False):
    """Classify a list of transcript segments. Returns the result dict.

    `segments` are [{start, end, text, words?}] as produced by the STT seam or
    the captions reader. `provider` is an AdProvider. `source_sha256` is the
    caller's content hash (see io.source_sha256); it is recorded, not computed,
    so a caller with a different hashing rule can keep its own.

    The result carries `status`, `flags`, `spans`, `stats`, `chunks`,
    `incomplete_chunks`, `rejections`, `retried_half_window` and
    `processing_time_sec`. `rejections`, `chunks` and `incomplete_chunks` are
    how partial failure stays visible; drop them and a transient 503 caches as
    an ad-free episode forever.
    """
    t0 = time.time()
    from .io import source_sha256 as _sha
    sha = source_sha256 if source_sha256 is not None else _sha(segments)
    segments = segments or []

    if not segments:
        res = _base_result(provider, segments, sha, "no_transcript", extension,
                           rejections=[{"chunk": -1, "reason": "no segments in transcript", "raw": ""}])
        res["processing_time_sec"] = round(time.time() - t0, 2)
        return res

    # Step 7 pre-check: don't spend a model call on something too short to classify.
    if len(segments) < MIN_SEGMENTS:
        res = _base_result(provider, segments, sha, STATUS_REJECTED_DEGENERATE, extension,
                           rejections=[{"chunk": -1,
                                        "reason": "only %d segments (< %d): nothing to classify"
                                                  % (len(segments), MIN_SEGMENTS),
                                        "raw": ""}])
        res["processing_time_sec"] = round(time.time() - t0, 2)
        return res

    ok, msg = provider.ensure_ready()
    if not ok:
        res = _base_result(provider, segments, sha, STATUS_FAILED, extension,
                           rejections=[{"chunk": -1, "reason": "provider unavailable: %s" % msg, "raw": ""}])
        res["processing_time_sec"] = round(time.time() - t0, 2)
        return res

    rejections = []
    try:
        provider.warm_up()
    except Exception:
        pass

    mct = max_chunk_tokens or provider.max_chunk_tokens
    spans, records, ext_state = _run_pass(provider, segments, mct, episode_hint,
                                          rejections, timeout=timeout, extension=extension)
    status, detail = episode_gates(spans, segments, max_fraction=max_fraction)

    retried = False
    if status == STATUS_REJECTED_OVERLABEL:
        # Retry once at half the window size before condemning the episode.
        retried = True
        rejections.append({"chunk": -1, "reason": "over-label gate tripped (%s); retrying at half window" % detail,
                           "raw": ""})
        if verbose:
            sys.stderr.write("  over-label gate tripped, retrying at half window\n")
        spans2, records2, ext2 = _run_pass(provider, segments, max(200, mct // 2),
                                           episode_hint, rejections, timeout=timeout, extension=extension)
        status2, detail2 = episode_gates(spans2, segments, max_fraction=max_fraction)
        records = records + records2
        ext_state = ext2
        spans, status, detail = spans2, status2, detail2

    # A run where every chunk errored is not "no ads found" -- it is a failure,
    # and must not be cached as a clean result. Without this, one rate-limited
    # or quota-exhausted run silently marks an episode ad-free forever.
    if records:
        failed_chunks = sum(1 for r in records if r.get("error"))
        if failed_chunks and failed_chunks == len(records) and not spans:
            status = STATUS_FAILED
            detail = "all %d chunk(s) failed: %s" % (
                failed_chunks, str((rejections[0] if rejections else {}).get("reason", ""))[:160])
    elif rejections and not spans and any("provider error" in str(r.get("reason", ""))
                                          for r in rejections):
        status = STATUS_FAILED
        detail = str(rejections[0].get("reason", ""))[:160]

    if status == STATUS_OK:
        refine_span_edges(segments, spans)
        flags = flags_from_spans(spans, len(segments))
        stats = compute_stats(spans, flags, segments)
    else:
        # Only `ok` produces flags/spans.
        flags = ""
        stats = {"ad_spans": 0, "ad_segments": 0, "ad_seconds": 0.0, "ad_fraction": 0.0, "uncertain_segments": 0}
        rejections.append({"chunk": -1, "reason": "%s: %s" % (status, detail), "raw": ""})
        spans = []

    res = _base_result(provider, segments, sha, status, extension)
    res["flags"] = flags
    res["spans"] = spans
    res["stats"] = stats
    res["chunks"] = records
    # Partial failure: some chunks answered, some never did. The spans that were
    # found are worth keeping (a missed ad is the tolerable failure here), but
    # the episode is under-labelled, and without this it would cache as a clean
    # `ok` and never be retried -- a transient 503 would cost those ads forever.
    res["incomplete_chunks"] = sum(1 for r in records if r.get("error"))
    if extension is not None and ext_state is not None:
        block = extension.finalize(ext_state, rejections)
        if block is not None:
            res[extension.result_key] = block
    res["rejections"] = rejections[:200]
    res["retried_half_window"] = retried
    res["processing_time_sec"] = round(time.time() - t0, 2)
    return res
