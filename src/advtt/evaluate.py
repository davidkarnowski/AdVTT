"""Evaluation against hand-labelled truth, and the offline self-test.

`score_against_truth` is verbatim from PodcastFetch adclass.py lines 3028-3178
(commit 74692de); `_print_eval` is the same printer with one change: a truth
set with no ad seconds (no-ad controls) reports recall and boundary error as
undefined instead of FAIL. The metrics are time-weighted:

    content_loss_sec   content seconds falsely marked ad at the skip threshold  <= 5 s (ship gate)
    ad_recall_sec      ad seconds correctly caught                              >= 0.70
    boundary_err_sec   mean |predicted end - true end| over matched blocks      <= 3 s

Recall is additionally split by how the ad got into the file (K6, 2026-09-07):

    inserted   spliced in by the host's ad server (Megaphone stitch map); the
               stitch map already labels these exactly, so a model earns nothing
               by finding them
    host-read  baked into the master by the host; the only spans a transcript
               classifier is actually needed for

A model that catches every inserted creative and misses every host read
scores ~0.9 total recall on a JRE episode and is useless, so the recall
target is reported per delivery. Delivery comes from a `delivery` field on
each truth span, or from a sibling `<stem>_ads.truth.inserted.json`
(written by scripts/stitchmap_to_truth.py, or hand-made): truth segments
inside an inserted span are `inserted`, the rest `host-read`. An inserted
file with no spans means "no dynamic insertion on this copy" (PDB), so
every truth second is host-read. Without either source delivery is unknown
and only the total is reported.
"""

import glob as globmod
import os

from .validate import episode_duration, segment_seconds


def _truth_flags(truth, n):
    flags = ["c"] * n
    for sp in truth.get("spans") or []:
        try:
            si = max(0, int(sp["start_index"]))
            ei = min(n - 1, int(sp["end_index"]))
        except (KeyError, TypeError, ValueError):
            continue
        for i in range(si, ei + 1):
            flags[i] = "a"
    return "".join(flags)


DELIVERY_INSERTED = "inserted"
DELIVERY_HOSTREAD = "host-read"
INSERTED_SUFFIX = "_ads.truth.inserted.json"


def _truth_delivery(truth, n, inserted=None):
    """Per-segment delivery: 'c' content, 'i' inserted ad, 'h' host-read ad,
    '?' ad of unknown delivery. Precedence: explicit `delivery` on the truth
    span, then the inserted sibling (index overlap), then the truth file's
    top-level `delivery`, else unknown. Assignment is per segment, not per
    span, so a host read glued onto a stitched break is split at the stitch
    boundary rather than absorbed into it."""
    tflags = _truth_flags(truth, n)
    out = list(tflags)
    ins = [False] * n
    if inserted is not None:
        for sp in inserted.get("spans") or []:
            try:
                si, ei = max(0, int(sp["start_index"])), min(n - 1, int(sp["end_index"]))
            except (KeyError, TypeError, ValueError):
                continue
            for i in range(si, ei + 1):
                ins[i] = True
    default = truth.get("delivery")
    for sp in truth.get("spans") or []:
        try:
            si, ei = max(0, int(sp["start_index"])), min(n - 1, int(sp["end_index"]))
        except (KeyError, TypeError, ValueError):
            continue
        explicit = sp.get("delivery") or default
        for i in range(si, ei + 1):
            if explicit == DELIVERY_INSERTED:
                out[i] = "i"
            elif explicit == DELIVERY_HOSTREAD:
                out[i] = "h"
            elif inserted is not None:
                out[i] = "i" if ins[i] else "h"
            else:
                out[i] = "?"
    return "".join(out)


def score_against_truth(pred, truth, segments, inserted=None):
    """TIME-weighted metrics. A 30s segment matters more than a 3s one.

    * content_loss_sec — content seconds falsely marked ad at the auto-skip
      threshold (>= AD_THRESHOLD, i.e. flag 'a'). THIS IS THE SHIP GATE.
    * ad_recall_sec    — fraction of true ad seconds caught at 'a'.
    * boundary_err_sec — mean |predicted end - true end| over matched spans.
    * inserted_recall_sec / hostread_recall_sec — recall restricted to truth
      seconds of that delivery (see module docstring); None when the truth
      set has no seconds of that delivery. `inserted` is the optional sibling
      document from stitchmap_to_truth.py.
    """
    n = len(segments)
    tflags = _truth_flags(truth, n)
    dflags = _truth_delivery(truth, n, inserted)
    pflags = pred.get("flags") or ""
    if len(pflags) < n:
        pflags = pflags + "c" * (n - len(pflags))

    dur = [segment_seconds(s) for s in segments]
    true_ad_sec = sum(dur[i] for i in range(n) if tflags[i] == "a")
    content_sec = sum(dur[i] for i in range(n) if tflags[i] == "c")

    content_loss = sum(dur[i] for i in range(n) if pflags[i] == "a" and tflags[i] == "c")
    caught = sum(dur[i] for i in range(n) if pflags[i] == "a" and tflags[i] == "a")
    missed = true_ad_sec - caught
    uncertain_on_content = sum(dur[i] for i in range(n) if pflags[i] == "u" and tflags[i] == "c")

    def _by_delivery(ch):
        true_s = sum(dur[i] for i in range(n) if dflags[i] == ch)
        caught_s = sum(dur[i] for i in range(n) if dflags[i] == ch and pflags[i] == "a")
        return round(true_s, 1), round(caught_s, 1), (round(caught_s / true_s, 3) if true_s > 0 else None)
    ins_true, ins_caught, ins_recall = _by_delivery("i")
    host_true, host_caught, host_recall = _by_delivery("h")
    unk_true, _unk_caught, _unk_recall = _by_delivery("?")

    # Boundary error: compare contiguous ad BLOCKS, not raw spans. Two sponsors
    # read back to back may legitimately be returned as one span or two, so both
    # sides are collapsed into maximal contiguous runs before matching. Each truth
    # block is matched to the predicted block with the nearest end time, and only
    # if they actually overlap in index space (a non-overlapping block is a recall
    # failure, already counted above, not a boundary error).
    def _blocks(flags, ch):
        out, i = [], 0
        while i < n:
            if flags[i] == ch:
                j = i
                while j + 1 < n and flags[j + 1] == ch:
                    j += 1
                out.append((i, j))
                i = j + 1
            else:
                i += 1
        return out

    errs = []
    pred_blocks = _blocks(pflags, "a")
    for (ts, te) in _blocks(tflags, "a"):
        if not pred_blocks:
            continue
        t_end = float(segments[te].get("end") or 0.0)
        best = min(pred_blocks, key=lambda b: abs(float(segments[b[1]].get("end") or 0.0) - t_end))
        if best[1] >= ts and best[0] <= te:
            errs.append(abs(float(segments[best[1]].get("end") or 0.0) - t_end))

    return {
        "segment_count": n,
        "duration_sec": round(episode_duration(segments), 1),
        "true_ad_sec": round(true_ad_sec, 1),
        "true_content_sec": round(content_sec, 1),
        "pred_ad_sec": round(sum(dur[i] for i in range(n) if pflags[i] == "a"), 1),
        "content_loss_sec": round(content_loss, 1),
        "ad_caught_sec": round(caught, 1),
        "ad_missed_sec": round(missed, 1),
        "ad_recall_sec": round(caught / true_ad_sec, 3) if true_ad_sec > 0 else None,
        "uncertain_on_content_sec": round(uncertain_on_content, 1),
        "boundary_err_sec": round(sum(errs) / len(errs), 2) if errs else None,
        "inserted_true_sec": ins_true, "inserted_caught_sec": ins_caught, "inserted_recall_sec": ins_recall,
        "hostread_true_sec": host_true, "hostread_caught_sec": host_caught, "hostread_recall_sec": host_recall,
        "delivery_unknown_sec": unk_true,
        "matched_spans": len(errs),
        "truth_spans": len(truth.get("spans") or []),
        "status": pred.get("status"),
    }


def truth_path_for(stt_path):
    p = str(stt_path)
    if p.endswith("_stt.json"):
        return p[: -len("_stt.json")] + "_ads.truth.json"
    base, _ext = os.path.splitext(p)
    return base + "_ads.truth.json"


def inserted_truth_for(stt_path, inserted_dir=None):
    """Path of the inserted-ad sibling for a transcript, or None. Looked up
    beside the transcript first, then in `inserted_dir` (the repository keeps
    them in tests/fixtures/truth-drafts/ because the hand-labelled transcripts
    live in PodcastFetch, which this package never writes into)."""
    p = str(stt_path)
    stem = p[: -len("_stt.json")] if p.endswith("_stt.json") else os.path.splitext(p)[0]
    cands = [stem + INSERTED_SUFFIX]
    if inserted_dir:
        cands.append(os.path.join(inserted_dir, os.path.basename(stem) + INSERTED_SUFFIX))
    for c in cands:
        if os.path.exists(c):
            return c
    return None


def ads_path_for(stt_path, out_dir=None):
    p = str(stt_path)
    stem = p[: -len("_stt.json")] if p.endswith("_stt.json") else os.path.splitext(p)[0]
    if out_dir:
        stem = os.path.join(out_dir, os.path.basename(stem))
    return stem + "_ads.json"


def evaluate(pattern, verbose=True, provider=None, out_dir=None, force=False,
             timeout=180, max_chunk_tokens=None, inserted_dir=None):
    """Score every transcript that has a matching *_ads.truth.json.

    Follows PodcastFetch's fixture conventions (`<stem>_stt.json`,
    `<stem>_ads.truth.json`, `<stem>_ads.json`) so the dev set can be scored in
    place. With `provider`, transcripts are (re)classified first and the
    predictions are written to `out_dir` (never beside PodcastFetch's own
    committed predictions unless out_dir is None and force is True).
    """
    from .classify import classify_segments
    from .io import load_json, write_atomic
    paths = sorted(globmod.glob(pattern))
    rows = []
    for p in paths:
        if p.endswith("_ads.truth.json"):
            stt = p[: -len("_ads.truth.json")] + "_stt.json"
        elif p.endswith("_ads.json"):
            stt = p[: -len("_ads.json")] + "_stt.json"
        elif p.endswith("_stt.json"):
            stt = p
        else:
            continue
        tp = truth_path_for(stt)
        ap = ads_path_for(stt, out_dir)
        if not (os.path.exists(tp) and os.path.exists(stt)):
            continue
        segments = load_json(stt).get("segments") or []
        if provider is not None and (force or not os.path.exists(ap)):
            hint = os.path.basename(stt).replace("_stt.json", "")
            res = classify_segments(segments, provider, episode_hint=hint, timeout=timeout,
                                    max_chunk_tokens=max_chunk_tokens, verbose=verbose)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            write_atomic(ap, res)
        if not os.path.exists(ap):
            rows.append((os.path.basename(stt), None, "no prediction -- pass a provider to classify"))
            continue
        ip = inserted_truth_for(stt, inserted_dir)
        row = score_against_truth(load_json(ap), load_json(tp), segments,
                                  inserted=load_json(ip) if ip else None)
        rows.append((os.path.basename(stt), row, None))

    if verbose:
        _print_eval(rows)
    return rows


def _print_eval(rows):
    def _r(v):
        return ("%.3f" % v) if v is not None else "n/a"
    hdr = "%-46s %7s %8s %9s %7s %7s %7s %8s %6s" % (
        "episode", "status", "trueAd", "lossSec", "recall", "recHost", "recIns", "boundary", "predAd")
    print(hdr)
    print("-" * len(hdr))
    tot_loss = tot_true = tot_caught = 0.0
    host_true = host_caught = ins_true = ins_caught = unk_true = 0.0
    berrs = []
    for name, row, err in rows:
        if row is None:
            print("%-46s %s" % (name[:46], err))
            continue
        print("%-46s %7s %8.1f %9.1f %7s %7s %7s %8s %6.1f" % (
            name[:46], (row["status"] or "?")[:7], row["true_ad_sec"], row["content_loss_sec"],
            _r(row["ad_recall_sec"]), _r(row.get("hostread_recall_sec")), _r(row.get("inserted_recall_sec")),
            ("%.2f" % row["boundary_err_sec"]) if row["boundary_err_sec"] is not None else "n/a",
            row["pred_ad_sec"]))
        tot_loss += row["content_loss_sec"]
        tot_true += row["true_ad_sec"]
        tot_caught += row["ad_caught_sec"]
        host_true += row.get("hostread_true_sec") or 0.0
        host_caught += row.get("hostread_caught_sec") or 0.0
        ins_true += row.get("inserted_true_sec") or 0.0
        ins_caught += row.get("inserted_caught_sec") or 0.0
        unk_true += row.get("delivery_unknown_sec") or 0.0
        if row["boundary_err_sec"] is not None:
            berrs.append(row["boundary_err_sec"])
    print("-" * len(hdr))
    recall = (tot_caught / tot_true) if tot_true else None
    host_recall = (host_caught / host_true) if host_true else None
    ins_recall = (ins_caught / ins_true) if ins_true else None
    berr = (sum(berrs) / len(berrs)) if berrs else None
    print("%-46s %7s %8.1f %9.1f %7s %7s %7s %8s" % (
        "AGGREGATE", "", tot_true, tot_loss, _r(recall), _r(host_recall), _r(ins_recall),
        ("%.2f" % berr) if berr is not None else "n/a"))
    print()
    print("  ship gate  content_loss_sec <= 5.0  -> %.1f  %s" % (tot_loss, "PASS" if tot_loss <= 5.0 else "FAIL"))
    if recall is None:
        # No ad seconds in the truth set (no-ad controls): recall and boundary
        # error are undefined, and the only thing that can fail is the ship gate.
        print("  target     ad_recall_sec    >= 0.70 -> n/a   (no ads in truth)")
        print("  target     boundary_err_sec <= 3.0  -> n/a   (no ads in truth)")
        return
    print("  target     ad_recall_sec    >= 0.70 -> %.3f %s" % (recall, "PASS" if recall >= 0.70 else "FAIL"))
    # The per-delivery lines are the ones that matter: host reads are the
    # classifier's job, inserted creatives are already labelled by the stitch map.
    if host_recall is not None:
        print("  target     hostread_recall  >= 0.70 -> %.3f %s  (%.0f s host-read truth)" % (
            host_recall, "PASS" if host_recall >= 0.70 else "FAIL", host_true))
    if ins_recall is not None:
        print("  info       inserted_recall          -> %.3f       (%.0f s inserted truth)" % (ins_recall, ins_true))
    if unk_true:
        print("  info       delivery unknown for %.0f s of truth (no delivery field, no inserted sibling)" % unk_true)
    if berr is not None:
        print("  target     boundary_err_sec <= 3.0  -> %.2f  %s" % (berr, "PASS" if berr <= 3.0 else "FAIL"))
    else:
        print("  target     boundary_err_sec <= 3.0  -> n/a   FAIL (no spans matched)")


# --------------------------------------------------------------------------
# Self tests — validation ladder, offline, no network
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Self tests -- validation ladder, offline, no network
# --------------------------------------------------------------------------

def self_test(verbose=True):
    """The ad-classifier half of PodcastFetch's `adclass.py --self-test`
    (items 1-13 and 15, plus the seam-merge case 9b), ported symbol for symbol.
    The speaker items (16-22) belong to PodcastFetch's extension.
    Returns 0 on success, 1 on any failure."""
    import re
    import shutil
    import tempfile
    from .chunking import plan_chunks
    from .classify import _run_pass
    from .io import source_sha256, write_atomic, load_json
    from .prompts import build_user_prompt, response_schema
    from .providers.base import AdProvider, _extract_json_object
    from .validate import (CONTEXT_SEGMENTS, STATUS_OK, STATUS_REJECTED_DEGENERATE,
                           STATUS_REJECTED_OVERLABEL, compute_stats, episode_gates,
                           flags_from_spans, validate_chunk)
    fails = []

    def check(name, cond, detail=""):
        if cond:
            if verbose:
                print("  ok    %s" % name)
        else:
            print("  FAIL  %s %s" % (name, detail))
            fails.append(name)

    # 40 segments x 5s = 200s episode.
    segs = [{"start": i * 5.0, "end": i * 5.0 + 5.0, "text": "segment %d some spoken words here" % i}
            for i in range(40)]

    # 1. out-of-range indices (the observed qwen2.5:1.5b failure mode)
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 5, "end_index": 13, "kind": "midroll", "confidence": 1.0, "evidence": "segment 5"}]},
        segs, 0, 4, rej, 0)
    check("out-of-window span dropped", out == [] and len(rej) == 1, repr(out))

    # 2. partial overlap gets clipped, not dropped
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 2, "end_index": 30, "kind": "midroll", "confidence": 0.9, "evidence": "segment 2 some"}]},
        segs, 0, 10, rej, 0)
    check("overhanging span clipped to window",
          len(out) == 1 and out[0]["start_index"] == 2 and out[0]["end_index"] == 9, repr(out))

    # 3. duration cap (> 240s)
    long_segs = [{"start": i * 30.0, "end": i * 30.0 + 30.0, "text": "segment %d words" % i} for i in range(40)]
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 0, "end_index": 20, "kind": "midroll", "confidence": 0.9, "evidence": "segment 0 words"}]},
        long_segs, 0, 40, rej, 0)
    check("span over 240s dropped", out == [] and any("cap" in r["reason"] for r in rej), repr(out))

    # 4. overlapping spans merge, confidence takes the MIN
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 4, "end_index": 8, "kind": "midroll", "confidence": 0.9, "evidence": "segment 4 some"},
        {"start_index": 7, "end_index": 11, "kind": "midroll", "confidence": 0.5, "evidence": "segment 7 some"}]},
        segs, 0, 20, rej, 0)
    check("overlapping spans merged with min confidence",
          len(out) == 1 and out[0]["start_index"] == 4 and out[0]["end_index"] == 11
          and abs(out[0]["confidence"] - 0.5) < 1e-9, repr(out))

    # 5. bad evidence halves confidence rather than dropping the span
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 3, "end_index": 5, "kind": "midroll", "confidence": 0.9,
         "evidence": "this quote appears nowhere"}]},
        segs, 0, 20, rej, 0)
    check("bad evidence -> confidence halved to uncertain",
          len(out) == 1 and abs(out[0]["confidence"] - 0.45) < 1e-9 and out[0]["state"] == "uncertain", repr(out))

    # 5b. good evidence survives (punctuation/case-insensitive)
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 3, "end_index": 5, "kind": "midroll", "confidence": 0.9,
         "evidence": "Segment 3, SOME spoken words!"}]},
        segs, 0, 20, rej, 0)
    check("verbatim evidence preserved",
          len(out) == 1 and abs(out[0]["confidence"] - 0.9) < 1e-9 and out[0]["state"] == "ad", repr(out))

    # 5d. ladder 2026-09-a: a quote that straddles the start segment and the
    #     next one is accepted (measured cause of every model recall gap on
    #     the 2026-09-06 PDB episodes).
    rej = []
    words = ["alpha beta gamma delta", "epsilon zeta eta theta", "iota kappa lambda mu", "nu xi omicron pi"] * 5
    ssegs = [{"start": i * 5.0, "end": i * 5.0 + 5.0, "text": words[i]} for i in range(20)]
    out = validate_chunk({"ad_spans": [
        {"start_index": 4, "end_index": 6, "kind": "midroll", "confidence": 0.9,
         "evidence": "gamma delta epsilon zeta"}]},
        ssegs, 0, 20, rej, 0)
    check("straddling evidence accepted",
          len(out) == 1 and abs(out[0]["confidence"] - 0.9) < 1e-9 and out[0].get("evidence_straddles") is True, repr(out))
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 4, "end_index": 6, "kind": "midroll", "confidence": 0.9,
         "evidence": "iota kappa lambda mu"}]},
        ssegs, 0, 20, rej, 0)
    check("evidence two segments away still fails",
          len(out) == 1 and abs(out[0]["confidence"] - 0.45) < 1e-9, repr(out))

    # 5c. dialogue check demotes a question-dense span
    qsegs = [dict(s, text=s["text"] + "?") for s in segs]
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 3, "end_index": 8, "kind": "midroll", "confidence": 0.9,
         "evidence": "segment 3 some spoken words here"}]},
        qsegs, 0, 20, rej, 0)
    check("question-dense span demoted to uncertain",
          len(out) == 1 and out[0]["state"] == "uncertain" and out[0].get("dialogue_suspect"), repr(out))

    # 6. empty list is a correct answer, no rejections
    rej = []
    out = validate_chunk({"ad_spans": []}, segs, 0, 20, rej, 0)
    check("empty ad_spans accepted", out == [] and rej == [], repr(rej))

    # 7. episode over-label gate
    rej = []
    out = validate_chunk({"ad_spans": [
        {"start_index": 0, "end_index": 19, "kind": "midroll", "confidence": 0.9,
         "evidence": "segment 0 some spoken"}]},
        segs, 0, 40, rej, 0)
    st, det = episode_gates(out, segs)
    check("span covering half the episode -> rejected", st != STATUS_OK, "%s %s" % (st, det))

    # 7b. one span covering everything -> degenerate
    st, det = episode_gates(
        [{"start_index": 0, "end_index": 39, "start": 0.0, "end": 200.0, "confidence": 0.9, "state": "ad"}],
        segs)
    check("full-episode span -> rejected_degenerate", st == STATUS_REJECTED_DEGENERATE, det)

    # 7c. uncertain-only over-labelling still trips the gate
    st, det = episode_gates(
        [{"start_index": 0, "end_index": 17, "start": 0.0, "end": 90.0, "confidence": 0.5, "state": "uncertain"}],
        segs)
    check("uncertain-only over-labelling still gated", st == STATUS_REJECTED_OVERLABEL, det)

    # 7d. a realistic 20% ad load passes
    st, det = episode_gates(
        [{"start_index": 10, "end_index": 17, "start": 50.0, "end": 90.0, "confidence": 0.9, "state": "ad"}],
        segs)
    check("realistic 20% ad load accepted", st == STATUS_OK, det)

    # 7e. too-short episode
    st, det = episode_gates([], segs[:5])
    check("under 10 segments -> rejected_degenerate", st == STATUS_REJECTED_DEGENERATE, det)

    # 8. flags/stats
    sp = [{"start_index": 10, "end_index": 17, "start": 50.0, "end": 90.0, "confidence": 0.9, "state": "ad"},
          {"start_index": 30, "end_index": 31, "start": 150.0, "end": 160.0, "confidence": 0.5, "state": "uncertain"}]
    fl = flags_from_spans(sp, 40)
    check("flags length + content", len(fl) == 40 and fl[10] == "a" and fl[17] == "a"
          and fl[18] == "c" and fl[30] == "u", fl)
    stats = compute_stats(sp, fl, segs)
    check("stats time-weighted", stats["ad_segments"] == 8 and abs(stats["ad_seconds"] - 40.0) < 1e-6
          and stats["uncertain_segments"] == 2, repr(stats))

    # 9. malformed model output
    rej = []
    check("non-dict input tolerated", validate_chunk(None, segs, 0, 20, rej, 0) == [])
    rej = []
    check("ad_spans not a list tolerated", validate_chunk({"ad_spans": "nope"}, segs, 0, 20, rej, 0) == []
          and len(rej) == 1)
    rej = []
    out = validate_chunk({"ad_spans": [{"start_index": "x", "end_index": 3, "kind": "bogus",
                                        "confidence": "hi", "evidence": None}]}, segs, 0, 20, rej, 0)
    check("garbage field types tolerated", out == [] and len(rej) == 1, repr(out))
    rej = []
    out = validate_chunk({"ad_spans": [{"start_index": 8, "end_index": 4, "kind": "midroll",
                                        "confidence": 0.9, "evidence": "segment 4 some"}]}, segs, 0, 20, rej, 0)
    check("reversed indices normalised", len(out) == 1 and out[0]["start_index"] == 4, repr(out))

    # 9b. seam merge must re-apply the 240s cap: two adjacent chunks can each
    #     return a legal sub-240s span that becomes over-long once joined.
    class TwoChunk(AdProvider):
        name = "twochunk"
        max_chunk_tokens = 1
        def ensure_ready(self, probe=False):
            return True, "stub"
        def complete_json(self, system, user, schema, timeout=180):
            m = re.search(r"LABELABLE INDICES: (\d+) through (\d+)", user)
            a, b = int(m.group(1)), int(m.group(2))
            return ({"ad_spans": [{"start_index": a, "end_index": b, "kind": "midroll",
                                   "confidence": 0.9, "evidence": "segment %d words" % a}]}, {"raw_text": ""})
        def warm_up(self):
            return None
    seam_segs = [{"start": i * 4.0, "end": i * 4.0 + 4.0, "text": "segment %d words" % i} for i in range(80)]
    rej = []
    spans, _recs, _st = _run_pass(TwoChunk(), seam_segs, 1, "", rej)
    check("seam-merged over-long span dropped",
          spans == [] and any("merged span" in r["reason"] for r in rej), repr(spans))

    # 10. JSON extraction from a reasoning preamble
    obj = _extract_json_object('<think>hmm</think> here you go: {"ad_spans": []} thanks')
    check("json extracted from prose", obj == {"ad_spans": []}, repr(obj))
    check("unparseable text -> None", _extract_json_object("no json at all") is None)

    # 11. chunking invariants
    plan = plan_chunks(segs, 1500)
    check("chunks tile without overlap",
          plan[0]["start"] == 0 and plan[-1]["end"] == 40
          and all(plan[i]["end"] == plan[i + 1]["start"] for i in range(len(plan) - 1)), repr(plan))
    big = [{"start": i * 5.0, "end": i * 5.0 + 5, "text": "x" * 600} for i in range(300)]
    plan = plan_chunks(big, 1500)
    check("W >= 3C maintained under a tight budget",
          all(p["end"] - p["start"] >= 3 * CONTEXT_SEGMENTS or p is plan[-1] for p in plan), repr(plan[:3]))
    plan1 = plan_chunks(big, 100000)
    check("huge budget -> one chunk", len(plan1) == 1, repr(plan1))

    # 12. context lines are marked and windows are labelable-only
    u = build_user_prompt(segs, 12, 24)
    check("context lines marked", u.count("\n[CONTEXT] ") == 24 and "LABELABLE INDICES: 12 through 23" in u,
          str(u.count("\n[CONTEXT] ")))
    check("no context marker at window start", "\n12\t" in u)

    # 12b. schema is parametric on the extension only
    s0 = response_schema()
    check("schema has only ad_spans without an extension",
          list(s0["properties"]) == ["ad_spans"] and s0["required"] == ["ad_spans"], repr(s0["required"]))

    # 13. sha256 is content-based, not byte-based
    a = source_sha256(segs)
    b = source_sha256([dict(s) for s in segs])
    c = source_sha256(segs[:-1])
    check("sha stable across identical content", a == b)
    check("sha changes with different segmentation", a != c)

    # 14. atomic write round trip
    tmpd = tempfile.mkdtemp(prefix="advtt-selftest-")
    try:
        p = os.path.join(tmpd, "ep.json")
        write_atomic(p, {"flags": fl, "spans": sp})
        rt = load_json(p)
        check("round trip preserves flags/spans", rt["flags"] == fl and len(rt["spans"]) == 2)
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    # 15. scoring maths
    pred = {"flags": "c" * 10 + "a" * 8 + "c" * 22,
            "spans": [{"start_index": 10, "end_index": 17, "start": 50.0, "end": 90.0, "state": "ad"}],
            "status": STATUS_OK}
    truth = {"segment_count": 40, "spans": [{"start_index": 10, "end_index": 18}]}
    sc = score_against_truth(pred, truth, segs)
    check("no content loss when prediction is inside truth", sc["content_loss_sec"] == 0.0, repr(sc))
    check("recall is time weighted", abs(sc["ad_recall_sec"] - 40.0 / 45.0) < 1e-3, repr(sc))
    check("boundary error measured", abs(sc["boundary_err_sec"] - 5.0) < 1e-6, repr(sc))
    pred_over = {"flags": "a" * 20 + "c" * 20,
                 "spans": [{"start_index": 0, "end_index": 19, "start": 0.0, "end": 100.0, "state": "ad"}],
                 "status": STATUS_OK}
    sc = score_against_truth(pred_over, truth, segs)
    # truth ad is 10-18; predicting 0-19 falsely skips segments 0-9 and 19 = 11 x 5s.
    check("content loss counted", abs(sc["content_loss_sec"] - 55.0) < 1e-6, repr(sc))

    if verbose:
        print()
    if fails:
        print("%d self-tests FAILED: %s" % (len(fails), ", ".join(fails)))
        return 1
    if verbose:
        print("all self-tests passed")
    return 0
