"""The canonical record (`<stem>.advtt.json`, profile advtt/1.0) and the local
analysis file (`<stem>.analysis.json`).

Research/08 §4.1 defines the record; Research/12 WP3 defines the mapping from
the legacy classifier result. Two tiers on purpose (track G): the record holds
times, category, confidence, advertiser and provenance and is shareable; the
evidence quotes, transcript-derived text and chunk records stay in the analysis
file, which never leaves the machine.
"""

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

PROFILE = "advtt/1.0"

# Legacy `kind` -> (category, form, position). Category ids are SponsorBlock /
# Jellyfin compatible; the old ADVERTISEMENT-vs-SPONSORSHIP axis lives in `form`.
KIND_MAP = {
    "preroll":  ("sponsor",   "host_read",          "preroll"),
    "midroll":  ("sponsor",   "host_read",          "midroll"),
    "postroll": ("sponsor",   "host_read",          "postroll"),
    "house":    ("selfpromo", "host_read",          "unknown"),
    "section":  ("sponsor",   "sponsorship_credit", "unknown"),
}

# Categories that are never in the default skip set (Research/08 §3).
NEVER_SKIP = {"selfpromo", "interaction", "intro", "outro", "preview", "program"}


def media_fingerprint(path):
    """duration_sec (ffprobe), bytes and sha256 of the exact rendition."""
    out = {"path": os.path.abspath(path), "bytes": os.path.getsize(path)}
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    out["sha256"] = h.hexdigest()
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        try:
            r = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration",
                                "-of", "default=nw=1:nk=1", path],
                               capture_output=True, text=True, timeout=60)
            out["duration_sec"] = round(float(r.stdout.strip()), 3)
        except Exception:
            pass
    return out


def _action_for(category, state):
    if state == "ad" and category not in NEVER_SKIP:
        return "skip"
    if state in ("ad", "uncertain"):
        return "prompt"
    return "none"


def build_record(result, media=None, stt=None, thresholds=None, source=None):
    """Legacy classifier result -> advtt/1.0 record dict (shareable tier)."""
    from .validate import AD_THRESHOLD, UNCERTAIN_THRESHOLD, MAX_AD_FRACTION, MAX_SPAN_SECONDS
    spans = []
    for n, sp in enumerate(result.get("spans") or [], 1):
        category, form, position = KIND_MAP.get(sp.get("kind"), ("sponsor", "unknown", "unknown"))
        start = sp.get("start_exact", sp.get("start"))
        end = sp.get("end_exact", sp.get("end"))
        edge_mode = "word" if sp.get("start_exact") is not None and sp.get("start_exact") != sp.get("start") else "segment"
        rec = {
            "id": "ad-%04d" % n,
            "start": round(float(start), 3),
            "end": round(float(end), 3),
            "category": category,
            "form": form,
            "position": position,
            "delivery": "unknown",
            "action": _action_for(category, sp.get("state")),
            "state": sp.get("state"),
            "confidence": sp.get("confidence"),
            "confidence_source": "verbalised",   # becomes "agreement" once the ensemble exists (WP4)
            "edges": {"mode": edge_mode},
            "provenance": "machine",
        }
        if sp.get("label"):
            rec["advertiser"] = {"name": sp["label"], "confidence": sp.get("label_confidence")}
        spans.append(rec)
    record = {
        "profile": PROFILE,
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "media": media or {},
        "source": source or {},
        "stt": stt or {},
        "classifier": {
            "provider": result.get("provider"),
            "model": result.get("model"),
            "prompt_version": result.get("prompt_version"),
            "schema_version": result.get("schema_version"),
            "chunks": len(result.get("chunks") or []),
            "incomplete_chunks": result.get("incomplete_chunks", 0),
            "retried_half_window": result.get("retried_half_window", False),
            "ensemble": {"members": 1, "mode": "single"},
        },
        "status": result.get("status"),
        "thresholds": thresholds or {
            "ad": AD_THRESHOLD, "uncertain": UNCERTAIN_THRESHOLD,
            "max_ad_fraction": MAX_AD_FRACTION, "max_span_sec": MAX_SPAN_SECONDS,
        },
        "transcript_sha256": result.get("source_sha256"),
        "duration_sec": result.get("duration_sec"),
        "stats": result.get("stats"),
        "spans": spans,
    }
    return record


def build_analysis(result, record):
    """The local, non-shareable tier: everything the classifier produced."""
    out = dict(result)
    out["profile"] = PROFILE
    out["record_span_ids"] = [s["id"] for s in record.get("spans") or []]
    return out


def write_json(path, obj):
    from .io import write_atomic
    write_atomic(path, obj)


def load_schema():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "schema", "advtt-1.0.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def validate_record(record):
    """Minimal structural validation without a jsonschema dependency.
    Returns a list of problems (empty when valid)."""
    problems = []
    for key in ("profile", "generated", "media", "stt", "classifier", "status", "thresholds", "spans"):
        if key not in record:
            problems.append("missing %s" % key)
    if record.get("profile") != PROFILE:
        problems.append("profile is %r, expected %r" % (record.get("profile"), PROFILE))
    cats = {"sponsor", "selfpromo", "interaction", "crosspromo", "intro", "outro", "preview", "program"}
    for sp in record.get("spans") or []:
        if not isinstance(sp.get("start"), (int, float)) or not isinstance(sp.get("end"), (int, float)):
            problems.append("%s: non-numeric start/end" % sp.get("id"))
        elif sp["end"] <= sp["start"]:
            problems.append("%s: end <= start" % sp.get("id"))
        if sp.get("category") not in cats:
            problems.append("%s: bad category %r" % (sp.get("id"), sp.get("category")))
        if sp.get("action") not in ("none", "prompt", "skip", "mute"):
            problems.append("%s: bad action %r" % (sp.get("id"), sp.get("action")))
    return problems
