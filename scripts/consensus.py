#!/usr/bin/env python3
"""Cross-model agreement and draft truth for episodes without hand labels.

Given several eval-out run directories (one model each) and the transcripts,
computes, per episode, on a per-segment basis:

  * per-model ad flags (state 'ad' only, i.e. the auto-skip threshold);
  * pairwise agreement in seconds (Jaccard over ad seconds);
  * a consensus flag string: 'a' where >= --min-agree models say ad;
  * draft truth spans from the consensus runs, each carrying which models
    agreed and the union/intersection extents, so a reviewer sees exactly
    where models disagree.

Writes <out-dir>/<stem>_ads.truth.draft.json (never *.truth.json: that name is
reserved for human labels) and a markdown summary to stdout.
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from advtt.validate import segment_seconds  # noqa: E402


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def runs_of(flags, ch="a"):
    out, i, n = [], 0, len(flags)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stt-dirs", nargs="+", required=True)
    ap.add_argument("--runs", nargs="+", required=True, help="eval-out dirs, one per model")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--min-agree", type=int, default=2)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    stts = {}
    for d in args.stt_dirs:
        for p in glob.glob(os.path.join(d, "*_stt.json")):
            stts[os.path.basename(p)[: -len("_stt.json")]] = p

    summary = []
    for stem, sp in sorted(stts.items()):
        segs = load(sp).get("segments") or []
        n = len(segs)
        dur = [segment_seconds(s) for s in segs]
        models, flags, preds = [], {}, {}
        for run in args.runs:
            name = os.path.basename(run.rstrip("/"))
            ap_ = os.path.join(run, stem + "_ads.json")
            if not os.path.exists(ap_):
                ap_ = os.path.join(run, stem + ".analysis.json")   # written by `advtt --stt`
            if not os.path.exists(ap_):
                continue
            pred = load(ap_)
            if pred.get("status") != "ok":
                continue
            fl = (pred.get("flags") or "").ljust(n, "c")[:n]
            models.append(name)
            flags[name] = fl
            preds[name] = pred
        if not models:
            continue
        # pairwise Jaccard on ad seconds
        pair = {}
        for i, a in enumerate(models):
            for b in models[i + 1:]:
                inter = sum(dur[k] for k in range(n) if flags[a][k] == "a" and flags[b][k] == "a")
                union = sum(dur[k] for k in range(n) if flags[a][k] == "a" or flags[b][k] == "a")
                pair["%s~%s" % (a, b)] = round(inter / union, 3) if union else None
        votes = [sum(1 for m in models if flags[m][k] == "a") for k in range(n)]
        cons = "".join("a" if v >= args.min_agree else "c" for v in votes)
        union_fl = "".join("a" if v >= 1 else "c" for v in votes)
        spans = []
        for (i, j) in runs_of(cons):
            agreed = [m for m in models if any(flags[m][k] == "a" for k in range(i, j + 1))]
            # extents: intersection = consensus run; union = the enclosing union run
            uruns = [r for r in runs_of(union_fl) if r[0] <= i and r[1] >= j]
            u = uruns[0] if uruns else (i, j)
            kinds = {}
            for m in agreed:
                for sp_ in preds[m].get("spans") or []:
                    if sp_["start_index"] <= j and sp_["end_index"] >= i:
                        kinds[sp_.get("kind")] = kinds.get(sp_.get("kind"), 0) + 1
            spans.append({
                "start_index": i, "end_index": j,
                "start": segs[i]["start"], "end": segs[j]["end"],
                "kind": max(kinds, key=kinds.get) if kinds else "midroll",
                "agreed_models": agreed, "votes": min(votes[i:j + 1]),
                "union_extent": {"start_index": u[0], "end_index": u[1],
                                 "start": segs[u[0]]["start"], "end": segs[u[1]]["end"]},
                "disputed_seconds": round(sum(dur[k] for k in range(u[0], u[1] + 1)) - sum(dur[k] for k in range(i, j + 1)), 1),
            })
        only_one = [(r, [m for m in models if flags[m][r[0]] == "a"]) for r in runs_of(union_fl)
                    if max(votes[r[0]:r[1] + 1]) < args.min_agree]
        draft = {
            "schema_version": 1, "kind": "ground_truth", "episode": stem, "segment_count": n,
            "duration_sec": round(max((s.get("end") or 0) for s in segs), 1) if segs else 0,
            "labeled_by": "machine-draft: consensus of %s (>= %d agree)" % (", ".join(models), args.min_agree),
            "source": "machine-draft", "status": "needs_human_review",
            "spans": [{k: v for k, v in s.items() if k in ("start_index", "end_index", "kind")} for s in spans],
            "consensus_detail": spans,
            "single_model_only": [{"start_index": r[0], "end_index": r[1], "start": segs[r[0]]["start"],
                                   "end": segs[r[1]]["end"], "models": ms} for r, ms in only_one],
            "pairwise_jaccard_ad_seconds": pair,
            "notes": ["Draft produced by scripts/consensus.py; a human must confirm every span and resolve "
                      "single_model_only regions before this becomes <stem>_ads.truth.json."],
        }
        with open(os.path.join(args.out_dir, stem + "_ads.truth.draft.json"), "w", encoding="utf-8") as f:
            json.dump(draft, f, indent=1)
        cons_sec = sum(dur[k] for k in range(n) if cons[k] == "a")
        union_sec = sum(dur[k] for k in range(n) if union_fl[k] == "a")
        summary.append({"episode": stem, "models": models, "consensus_spans": len(spans),
                        "consensus_sec": round(cons_sec, 1), "union_sec": round(union_sec, 1),
                        "disputed_sec": round(union_sec - cons_sec, 1), "single_model_regions": len(only_one),
                        "pairwise": pair})

    print("| episode | models | consensus spans | consensus s | union s | disputed s | single-model regions | pairwise Jaccard |")
    print("|---|---|---|---|---|---|---|---|")
    for s in summary:
        print("| %s | %d | %d | %.1f | %.1f | %.1f | %d | %s |" % (
            s["episode"][:44], len(s["models"]), s["consensus_spans"], s["consensus_sec"], s["union_sec"],
            s["disputed_sec"], s["single_model_regions"],
            ", ".join("%s=%s" % (k.replace("-default", ""), v) for k, v in s["pairwise"].items())))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
