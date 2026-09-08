#!/usr/bin/env python3
"""Summarise eval-out/<run>/ predictions across models.

For every run directory given, prints per-episode status, chunk count, wall
time, CLI cost, ad seconds found, and, where a truth file exists beside the
transcript, the three gate metrics plus recall split by delivery (host-read
vs inserted, see advtt.evaluate). An episode with only an inserted-ad file
(`<stem>_ads.truth.inserted.json`, from the Megaphone stitch map) and no full
truth is scored on inserted recall alone: content loss is undefined there
because unlabelled host reads would count as loss. Writes a markdown table to
stdout and a JSON summary to --json.

Usage:
  scripts/compare_models.py --stt-dirs DIR [DIR ...] --runs eval-out/sonnet5-default eval-out/opus5-default ...
"""

import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from advtt.evaluate import inserted_truth_for, score_against_truth, truth_path_for  # noqa: E402


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stt-dirs", nargs="+", required=True, help="directories holding <stem>_stt.json (+ optional truth)")
    ap.add_argument("--runs", nargs="+", required=True, help="eval-out run directories, one per model/setting")
    ap.add_argument("--json", default=None)
    ap.add_argument("--inserted-dir", default="tests/fixtures/truth-drafts",
                    help="where <stem>_ads.truth.inserted.json siblings live when not beside the transcript")
    args = ap.parse_args()

    stts = {}
    for d in args.stt_dirs:
        for p in glob.glob(os.path.join(d, "*_stt.json")):
            stts[os.path.basename(p)[: -len("_stt.json")]] = p

    rows = []
    for run in args.runs:
        name = os.path.basename(run.rstrip("/"))
        for stem, sp in sorted(stts.items()):
            ap_ = os.path.join(run, stem + "_ads.json")
            if not os.path.exists(ap_):
                ap_ = os.path.join(run, stem + ".analysis.json")   # written by `advtt --stt`
            if not os.path.exists(ap_):
                continue
            pred = load(ap_)
            segs = load(sp).get("segments") or []
            chunks = pred.get("chunks") or []
            row = {
                "run": name, "episode": stem, "model": pred.get("model"), "status": pred.get("status"),
                "chunks": len(chunks), "incomplete": pred.get("incomplete_chunks", 0),
                "wall_sec": round(sum(float(c.get("wall_sec") or 0) for c in chunks), 1),
                "cost_usd": round(sum(float(c.get("cost_usd") or 0) for c in chunks), 4),
                "thinking_tokens": sum(int(c.get("thinking_tokens") or 0) for c in chunks) if any("thinking_tokens" in c for c in chunks) else None,
                "ad_spans": (pred.get("stats") or {}).get("ad_spans"),
                "ad_seconds": (pred.get("stats") or {}).get("ad_seconds"),
                "uncertain_segments": (pred.get("stats") or {}).get("uncertain_segments"),
                "rejections": len(pred.get("rejections") or []),
            }
            tp = truth_path_for(sp)
            ip = inserted_truth_for(sp, args.inserted_dir)
            ins = load(ip) if ip else None
            if os.path.exists(tp):
                sc = score_against_truth(pred, load(tp), segs, inserted=ins)
                row.update({"truth": "full", "content_loss_sec": sc["content_loss_sec"],
                            "ad_recall_sec": sc["ad_recall_sec"], "boundary_err_sec": sc["boundary_err_sec"],
                            "true_ad_sec": sc["true_ad_sec"],
                            "hostread_recall_sec": sc["hostread_recall_sec"], "hostread_true_sec": sc["hostread_true_sec"],
                            "inserted_recall_sec": sc["inserted_recall_sec"], "inserted_true_sec": sc["inserted_true_sec"]})
            elif ins is not None and ins.get("spans"):
                # Inserted-only truth: every inserted span is known, host reads are not.
                sc = score_against_truth(pred, {"spans": ins["spans"], "delivery": "inserted"}, segs)
                row.update({"truth": "inserted-only", "inserted_recall_sec": sc["inserted_recall_sec"],
                            "inserted_true_sec": sc["inserted_true_sec"], "boundary_err_sec": sc["boundary_err_sec"]})
            rows.append(row)

    hdr = ["run", "episode", "status", "chunks", "wall_sec", "cost_usd", "ad_spans", "ad_seconds", "truth",
           "content_loss_sec", "ad_recall_sec", "hostread_recall_sec", "inserted_recall_sec", "boundary_err_sec"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "---|" * len(hdr))
    for r in rows:
        print("| " + " | ".join("" if r.get(h) is None else (str(r[h])[:44] if h == "episode" else str(r[h])) for h in hdr) + " |")

    # per-run aggregate over episodes that have truth
    print()
    print("| run | episodes | with truth | total cost | total wall (s) | sum content_loss | min recall | min host-read recall | min inserted recall | max boundary_err | any gate fail |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for run in args.runs:
        name = os.path.basename(run.rstrip("/"))
        rs = [r for r in rows if r["run"] == name]
        wt = [r for r in rs if "content_loss_sec" in r]
        wi = [r for r in rs if r.get("inserted_recall_sec") is not None]
        if not rs:
            continue
        # The host-read recall target replaces the total-recall one where delivery is known:
        # total recall on a DAI episode is dominated by creatives the stitch map already labels.
        fail = any((r["content_loss_sec"] or 0) > 5
                   or (r.get("hostread_recall_sec") is not None and r["hostread_recall_sec"] < 0.7)
                   or (r.get("hostread_recall_sec") is None and r["ad_recall_sec"] is not None and r["ad_recall_sec"] < 0.7)
                   or (r["boundary_err_sec"] is not None and r["boundary_err_sec"] > 3) for r in wt)
        print("| %s | %d | %d | $%.3f | %.0f | %.1f | %s | %s | %s | %s | %s |" % (
            name, len(rs), len(wt), sum(r["cost_usd"] for r in rs), sum(r["wall_sec"] for r in rs),
            sum(r["content_loss_sec"] for r in wt),
            min((r["ad_recall_sec"] for r in wt if r["ad_recall_sec"] is not None), default="n/a"),
            min((r["hostread_recall_sec"] for r in wt if r.get("hostread_recall_sec") is not None), default="n/a"),
            min((r["inserted_recall_sec"] for r in wi), default="n/a"),
            max((r["boundary_err_sec"] for r in wt if r["boundary_err_sec"] is not None), default="n/a"),
            "YES" if fail else "no"))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
