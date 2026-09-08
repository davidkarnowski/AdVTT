"""The validation ladder and its constants. Moves as ONE unit; the rungs are ordered
and two are order-dependent (the duration cap is re-applied after merging; merge
takes the MIN confidence). `_QUOTE_EQUIV` is tuned against real ASR output.
"""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 67-86, 99-105, 1636-1857, 2470-2552. Do not edit the moved bodies without bumping PROMPT_VERSION
# where the prompt or ladder behaviour changes; see Research/01 and 12.
import json
import re


SCHEMA_VERSION = 1
PROMPT_VERSION = "2026-08-g"

# Ladder version. The prompt text is unchanged since 2026-08-g, so replay
# keys and PodcastFetch's prompt still match; but the validation ladder's
# behaviour changed on 2026-09-06 and results must not be confused with the
# legacy ones, so the effective prompt_version recorded in every result is
# PROMPT_VERSION + "+" + LADDER_VERSION (see classify.effective_prompt_version).
#
# 2026-09-a: rung 5 (verbatim evidence) also accepts a quote that straddles
# the boundary between the start segment and the next EVIDENCE_LOOKAHEAD
# segments. Measured 2026-09-06 on five new PDB episodes: every recall
# difference between Sonnet 5, Opus 5 and Haiku 4.5 was a real ad whose quote
# began in the start segment and ended in the next one (token overlap 58%
# against the start segment alone, under the 70% floor), demoted to
# `uncertain`. Set EVIDENCE_LOOKAHEAD = 0 for the legacy behaviour.
LADDER_VERSION = "2026-09-a"
EVIDENCE_LOOKAHEAD = 1

# Questions per segment above which a span reads as interview dialogue rather
# than a sponsor read. Set from measured data: real ad blocks sit at 0.00-0.07,
# the one confirmed false positive at 0.29. Deliberately nearer the false
# positive than the ads, because demotion costs a manual skip while a missed
# demotion silently eats content.
DIALOGUE_Q_DENSITY = 0.20

# Confidence -> state
AD_THRESHOLD = 0.75          # >= this is auto-skippable
UNCERTAIN_THRESHOLD = 0.40   # >= this but < AD_THRESHOLD is "show but don't skip"

CONTEXT_SEGMENTS = 12        # C: read-only context on each side of a labelling window
MAX_SPAN_SECONDS = 240.0     # no single ad span may exceed this
MAX_AD_FRACTION = 0.35       # episode-level over-label gate
DEGENERATE_SPAN_FRACTION = 0.60
MIN_SEGMENTS = 10            # short USDA actualities have nothing to classify
RAW_TRUNCATE = 2000


STATUS_OK = "ok"
STATUS_REJECTED_OVERLABEL = "rejected_overlabel"
STATUS_REJECTED_DEGENERATE = "rejected_degenerate"
STATUS_FAILED = "failed"
STATUS_NO_TRANSCRIPT = "no_transcript"

AD_KINDS = ("preroll", "midroll", "postroll", "house", "section")


_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_WS_RE = re.compile(r"\s+")


# Spoken-form variants an ASR transcript and a model quoting it will disagree on.
_QUOTE_EQUIV = [
    (re.compile(r"\b(\w)[\s\-]+(?=\w\b)"), r"\1"),      # "b-e-t-t-e-r" -> "better"
    (re.compile(r"\bdot\s+com\b"), "com"),                # "betterhelp dot com"
    (re.compile(r"\bslash\b"), " "),                       # "site.com slash rogan"
    (re.compile(r"\band\b"), " "),
    (re.compile(r"\bthe\b"), " "),
]


def normalize_quote(text):
    """Lowercase, unhyphenate, strip punctuation, collapse whitespace.

    Hyphenation is the important part. Whisper emits "last-minute" as the two
    tokens ["last", "-minute"], so a model quoting the segment verbatim produces
    a string that a naive normalizer cannot align against the word stream -- and
    the evidence check then halves the confidence of a perfectly good span. The
    same applies to spelled-out URLs ("better h-e-l-p dot com"), which are
    everywhere in host-read sponsor copy.
    """
    t = (text or "").lower()
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u2014", " ").replace("\u2013", " ")
    # Join intra-word hyphens BEFORE punctuation stripping, so "last-minute" and
    # "last minute" and "lastminute" all reduce to the same token.
    t = re.sub(r"(?<=\w)-(?=\w)", "", t)
    t = _PUNCT_RE.sub(" ", t)
    t = _WS_RE.sub(" ", t).strip()
    return t


def quote_matches(needle, haystack):
    """Fuzzy containment for evidence quotes.

    Tries exact containment first, then a spoken-form-normalised comparison, then
    a token-overlap fallback so a quote that drops a filler word still counts.
    """
    n, h = normalize_quote(needle), normalize_quote(haystack)
    if not n:
        return False
    if n in h:
        return True

    # Whitespace-insensitive: hyphen-joining turns "last-minute" into
    # "lastminute" while the transcript may hold "last minute". Comparing with
    # all spaces removed makes the three spellings equivalent.
    if n.replace(" ", "") in h.replace(" ", ""):
        return True

    def spoken(x):
        for pat, rep in _QUOTE_EQUIV:
            x = pat.sub(rep, x)
        return _WS_RE.sub(" ", x).strip()

    if spoken(n) and spoken(n) in spoken(h):
        return True

    nt, ht = n.split(), set(h.split())
    if not nt:
        return False
    hit = sum(1 for w in nt if w in ht)
    return hit / len(nt) >= 0.7


def state_for(confidence):
    if confidence >= AD_THRESHOLD:
        return "ad"
    if confidence >= UNCERTAIN_THRESHOLD:
        return "uncertain"
    return "content"


def merge_spans(spans, gap=1):
    """Sort by start_index and merge overlapping/adjacent spans.

    Confidence of a merged span is the MIN of its parts, never the max: merging
    is a widening operation and widening must not increase certainty.
    """
    if not spans:
        return []
    out = []
    for sp in sorted(spans, key=lambda s: (s["start_index"], s["end_index"])):
        if out and sp["start_index"] - out[-1]["end_index"] <= gap:
            prev = out[-1]
            prev["end_index"] = max(prev["end_index"], sp["end_index"])
            prev["confidence"] = min(prev["confidence"], sp["confidence"])
            if not prev.get("evidence") and sp.get("evidence"):
                prev["evidence"] = sp["evidence"]
        else:
            out.append(dict(sp))
    return out


def validate_chunk(raw_obj, segments, a, b, rejections, chunk_id=0):
    """Steps 1-5 of the ladder, applied to one chunk's model output.

    Returns a list of span dicts with indices, seconds, confidence and evidence.
    Never raises on malformed model output — it degrades to fewer/weaker spans.
    """
    n = len(segments)
    spans_in = []
    if isinstance(raw_obj, dict):
        spans_in = raw_obj.get("ad_spans")
    if spans_in is None:
        spans_in = []
    if not isinstance(spans_in, list):
        rejections.append({"chunk": chunk_id, "reason": "ad_spans was not a list",
                           "raw": json.dumps(raw_obj)[:RAW_TRUNCATE]})
        return []

    kept = []
    for item in spans_in:
        if not isinstance(item, dict):
            rejections.append({"chunk": chunk_id, "reason": "span was not an object",
                               "raw": json.dumps(item)[:RAW_TRUNCATE]})
            continue
        try:
            si = int(item.get("start_index"))
            ei = int(item.get("end_index"))
        except (TypeError, ValueError):
            rejections.append({"chunk": chunk_id, "reason": "non-integer indices",
                               "raw": json.dumps(item)[:RAW_TRUNCATE]})
            continue
        try:
            conf = float(item.get("confidence", 0.0))
        except (TypeError, ValueError):
            conf = 0.0
        conf = max(0.0, min(1.0, conf))
        kind = item.get("kind") if item.get("kind") in AD_KINDS else "midroll"
        evidence = item.get("evidence") or ""
        end_evidence = item.get("end_evidence") or ""
        if si > ei:
            si, ei = ei, si

        # --- Step 2: range. Clip to the episode and to the labelable window.
        orig = (si, ei)
        si = max(si, 0, a)
        ei = min(ei, n - 1, b - 1)
        if si > ei:
            rejections.append({"chunk": chunk_id, "reason": "span %s outside labelable window [%d,%d)" % (list(orig), a, b),
                               "raw": json.dumps(item)[:RAW_TRUNCATE]})
            continue
        if orig != (si, ei):
            rejections.append({"chunk": chunk_id, "reason": "span %s clipped to [%d,%d]" % (list(orig), si, ei),
                               "raw": json.dumps(item)[:RAW_TRUNCATE]})

        start_t = float(segments[si].get("start") or 0.0)
        end_t = float(segments[ei].get("end") or start_t)

        # --- Step 3: duration. No single ad runs longer than MAX_SPAN_SECONDS.
        if end_t - start_t > MAX_SPAN_SECONDS:
            rejections.append({"chunk": chunk_id,
                               "reason": "span %.1fs exceeds %.0fs cap" % (end_t - start_t, MAX_SPAN_SECONDS),
                               "raw": json.dumps(item)[:RAW_TRUNCATE]})
            continue

        kept.append({
            "start_index": si, "end_index": ei,
            "start": round(start_t, 2), "end": round(end_t, 2),
            "kind": kind, "confidence": conf, "evidence": str(evidence)[:300],
            "end_evidence": str(end_evidence)[:300],
        })

    # --- Step 4: merge overlapping/adjacent.
    kept = merge_spans(kept)

    # --- Step 5: evidence must be a verbatim quote from the span's FIRST segment.
    # Ladder 2026-09-a: a quote may run past the end of the first segment into
    # the next EVIDENCE_LOOKAHEAD segment(s); the concatenation is tried only
    # when the first segment alone fails, so legacy passes are unchanged.
    for sp in kept:
        first_txt = segments[sp["start_index"]].get("text") or ""
        quote = sp.get("evidence") or ""
        sp["evidence_ok"] = quote_matches(quote, first_txt)
        if not sp["evidence_ok"] and EVIDENCE_LOOKAHEAD > 0:
            joined = " ".join((segments[k].get("text") or "")
                              for k in range(sp["start_index"],
                                             min(len(segments), sp["start_index"] + 1 + EVIDENCE_LOOKAHEAD)))
            if quote_matches(quote, joined):
                sp["evidence_ok"] = True
                sp["evidence_straddles"] = True
        if not sp["evidence_ok"]:
            # Halve rather than drop: a real ad with a paraphrased quote should
            # degrade to `uncertain`, not vanish.
            sp["confidence"] = round(sp["confidence"] * 0.5, 4)
            rejections.append({"chunk": chunk_id,
                               "reason": "evidence not verbatim in segment %d; confidence halved to %.2f"
                                         % (sp["start_index"], sp["confidence"]),
                               "raw": (sp.get("evidence") or "")[:RAW_TRUNCATE]})
    # --- Step 5b: an advertisement is a MONOLOGUE addressed to the listener.
    # A dense back-and-forth of questions is an interview, even when it carries
    # every surface feature of an ad -- a brand, a URL, a call to action, a
    # request for money. The measured separation on real data is wide: genuine
    # host-read sponsor blocks run 0.00-0.07 questions per segment, while a guest
    # being asked about their own foundation ran 0.29.
    #
    # Demote rather than drop, exactly as the evidence rule does: the span stays
    # visible and manually skippable, but drops below the auto-skip threshold so
    # it is never silently removed for the listener. Prompting alone did not fix
    # this case, so the structural check is what actually holds the ship gate.
    for sp in kept:
        body = segments[sp["start_index"]:sp["end_index"] + 1]
        if not body:
            continue
        q_density = sum(t.get("text", "").count("?") for t in body) / len(body)
        if q_density >= DIALOGUE_Q_DENSITY:
            sp["dialogue_suspect"] = round(q_density, 3)
            sp["confidence"] = round(sp["confidence"] * 0.5, 4)
            rejections.append({
                "chunk": chunk_id,
                "reason": "span %d-%d reads as dialogue (%.2f questions/segment); "
                          "confidence halved to %.2f"
                          % (sp["start_index"], sp["end_index"], q_density, sp["confidence"]),
                "raw": (body[0].get("text") or "")[:RAW_TRUNCATE],
            })

    # Recompute seconds after the merge widened anything.
    for sp in kept:
        sp["start"] = round(float(segments[sp["start_index"]].get("start") or 0.0), 2)
        sp["end"] = round(float(segments[sp["end_index"]].get("end") or sp["start"]), 2)
        sp["state"] = state_for(sp["confidence"])
    return kept


# --------------------------------------------------------------------------
# Speaker attribution validation
# --------------------------------------------------------------------------


def segment_seconds(seg):
    try:
        return max(0.0, float(seg.get("end") or 0.0) - float(seg.get("start") or 0.0))
    except (TypeError, ValueError):
        return 0.0


def episode_duration(segments):
    if not segments:
        return 0.0
    try:
        return round(max(float(s.get("end") or 0.0) for s in segments), 2)
    except (TypeError, ValueError):
        return 0.0


def flags_from_spans(spans, n):
    """One char per segment: 'a' ad, 'u' uncertain, 'c' content."""
    flags = ["c"] * n
    rank = {"c": 0, "u": 1, "a": 2}
    for sp in spans:
        ch = {"ad": "a", "uncertain": "u", "content": "c"}.get(sp.get("state"), "c")
        for i in range(max(0, sp["start_index"]), min(n - 1, sp["end_index"]) + 1):
            if rank[ch] > rank[flags[i]]:
                flags[i] = ch
    return "".join(flags)


def compute_stats(spans, flags, segments):
    n = len(segments)
    dur = episode_duration(segments)
    ad_seconds = sum(segment_seconds(segments[i]) for i in range(n) if flags[i] == "a")
    unc_segments = sum(1 for i in range(n) if flags[i] == "u")
    return {
        "ad_spans": sum(1 for sp in spans if sp.get("state") == "ad"),
        "ad_segments": sum(1 for i in range(n) if flags[i] == "a"),
        "ad_seconds": round(ad_seconds, 2),
        "ad_fraction": round(ad_seconds / dur, 4) if dur > 0 else 0.0,
        "uncertain_segments": unc_segments,
    }


def episode_gates(spans, segments, max_fraction=MAX_AD_FRACTION):
    """Ladder steps 6-7. Returns (status, detail).

    The over-label gate counts every retained span (ad + uncertain), not just the
    auto-skip ones: a degenerate model that emits confidence 0.5 across the whole
    episode must not slip past by staying under the ad threshold.
    """
    n = len(segments)
    dur = episode_duration(segments)
    if n < MIN_SEGMENTS:
        return STATUS_REJECTED_DEGENERATE, "only %d segments (< %d): nothing to classify" % (n, MIN_SEGMENTS)
    if dur <= 0:
        return STATUS_REJECTED_DEGENERATE, "episode duration is zero"

    live = [sp for sp in spans if sp.get("state") in ("ad", "uncertain")]

    # Step 7: one span swallowing the episode.
    for sp in live:
        cover = (sp["end"] - sp["start"]) / dur if dur else 0.0
        if cover > DEGENERATE_SPAN_FRACTION:
            return (STATUS_REJECTED_DEGENERATE,
                    "single span [%d,%d] covers %.0f%% of the episode contiguously"
                    % (sp["start_index"], sp["end_index"], cover * 100))

    # Step 6: total over-labelling.
    covered = set()
    for sp in live:
        covered.update(range(sp["start_index"], sp["end_index"] + 1))
    secs = sum(segment_seconds(segments[i]) for i in sorted(covered) if 0 <= i < n)
    frac = secs / dur if dur else 0.0
    if frac > max_fraction:
        return (STATUS_REJECTED_OVERLABEL,
                "labelled %.1fs of %.1fs (%.1f%%) as advertising, over the %.0f%% cap"
                % (secs, dur, frac * 100, max_fraction * 100))
    return STATUS_OK, ""


# --------------------------------------------------------------------------
# Sidecar IO
# --------------------------------------------------------------------------
