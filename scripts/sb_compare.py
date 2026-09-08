#!/usr/bin/env python3
"""Compare AdVTT predictions against SponsorBlock silver labels mapped to RSS time.

Input: data/sponsorblock/<stem>_silver.json files of the form
  {"stem": ..., "video_id": ..., "offset_sec": float | null, "offset_consistent": bool,
   "segments": [{"start": s, "end": e, "category": "sponsor"|..., "votes": n, "locked": bool}]}
where start/end are already in RSS-audio seconds (or, if offset_sec is given
and segments are in YouTube time, they are shifted here).

Output: per episode, duration-based overlap between AdVTT 'ad' seconds and
SponsorBlock sponsor/selfpromo seconds, plus the seconds each side has that
the other does not. Because the RSS copy carries dynamically inserted ads the
YouTube upload does not, AdVTT-only seconds are expected and are listed with
their spans for inspection rather than counted as errors.
"""

import argparse
import glob
import json
import os


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def intervals_from_pred(pred):
    return [(sp["start"], sp["end"]) for sp in pred.get("spans") or [] if sp.get("state") == "ad"]


def merge(iv):
    iv = sorted(iv)
    out = []
    for s, e in iv:
        if out and s <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], e))
        else:
            out.append((s, e))
    return out


def total(iv):
    return sum(e - s for s, e in iv)


def intersect(a, b):
    out = []
    for s1, e1 in a:
        for s2, e2 in b:
            s, e = max(s1, s2), min(e1, e2)
            if e > s:
                out.append((s, e))
    return merge(out)


def subtract(a, b):
    out = []
    for s, e in a:
        cur = [(s, e)]
        for s2, e2 in b:
            nxt = []
            for cs, ce in cur:
                if e2 <= cs or s2 >= ce:
                    nxt.append((cs, ce))
                else:
                    if s2 > cs:
                        nxt.append((cs, s2))
                    if e2 < ce:
                        nxt.append((e2, ce))
            cur = nxt
        out.extend(cur)
    return merge(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--silver-dir", default="data/sponsorblock")
    ap.add_argument("--run", required=True, help="eval-out dir with <stem>.advtt.json or <stem>_ads.json predictions")
    ap.add_argument("--categories", default="sponsor,selfpromo")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    cats = set(args.categories.split(","))
    rows = []
    for p in sorted(glob.glob(os.path.join(args.silver_dir, "*_silver.json"))):
        sv = load(p)
        stem = sv.get("stem") or os.path.basename(p)[: -len("_silver.json")]
        # `advtt --stt` writes <stem>.advtt.json (+ .analysis.json); `advtt --eval` writes <stem>_ads.json.
        # All three carry spans with start/end/state. (Before 2026-09-07 only the last name was tried,
        # so the overnight JRE comparison reported "no AdVTT prediction" for every episode.)
        ap_ = None
        for cand in (stem + ".advtt.json", stem + "_ads.json", stem + ".analysis.json"):
            if os.path.exists(os.path.join(args.run, cand)):
                ap_ = os.path.join(args.run, cand)
                break
        if ap_ is None:
            rows.append({"episode": stem, "note": "no AdVTT prediction in %s" % args.run})
            continue
        pred = load(ap_)
        off = sv.get("offset_sec") or 0.0
        in_rss = sv.get("segments_in_rss_time", True)
        sb = merge([((s["start"] if in_rss else s["start"] + off), (s["end"] if in_rss else s["end"] + off))
                    for s in sv.get("segments") or [] if s.get("category") in cats])
        ad = merge(intervals_from_pred(pred))
        both = intersect(ad, sb)
        row = {
            "episode": stem, "video_id": sv.get("video_id"), "offset_consistent": sv.get("offset_consistent"),
            "advtt_ad_sec": round(total(ad), 1), "sponsorblock_sec": round(total(sb), 1),
            "overlap_sec": round(total(both), 1),
            "sb_recall_by_advtt": round(total(both) / total(sb), 3) if total(sb) else None,
            "advtt_precision_vs_sb": round(total(both) / total(ad), 3) if total(ad) else None,
            "advtt_only": [(round(s, 1), round(e, 1)) for s, e in subtract(ad, sb)],
            "sponsorblock_only": [(round(s, 1), round(e, 1)) for s, e in subtract(sb, ad)],
        }
        rows.append(row)
    print("| episode | video | offset ok | AdVTT ad s | SB s | overlap s | SB recall | AdVTT prec. vs SB | AdVTT-only spans | SB-only spans |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if "note" in r:
            print("| %s | %s |" % (r["episode"][:40], r["note"]))
            continue
        print("| %s | %s | %s | %.1f | %.1f | %.1f | %s | %s | %d | %d |" % (
            r["episode"][:40], r["video_id"], r["offset_consistent"], r["advtt_ad_sec"], r["sponsorblock_sec"],
            r["overlap_sec"], r["sb_recall_by_advtt"], r["advtt_precision_vs_sb"],
            len(r["advtt_only"]), len(r["sponsorblock_only"])))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
