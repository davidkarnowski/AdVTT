#!/usr/bin/env python3
"""Build a complete draft truth file for a DAI episode from two free sources.

    inserted creatives  <- the Megaphone stitch map of the transcribed copy
                           (`<stem>_ads.truth.inserted.json`, scripts/stitchmap_to_truth.py)
    host-read ads       <- SponsorBlock silver labels shifted into RSS time
                           (`data/sponsorblock/<stem>_silver.json`, track L)

Why (K6, 2026-09-07): on JRE the stitch map labels every inserted creative
to 0.1 s and SponsorBlock labels only the host reads (its segments are made
against the ad-free YouTube master, so it cannot see the creatives). The two
are disjoint by construction and together cover every ad second a listener
hears, so a JRE draft no longer depends on three-model consensus, which the
usage limit made unaffordable. The output keeps the consensus-draft schema
(`schema_version 1`, `kind ground_truth`, `status needs_human_review`) so the
evaluator and the review workflow are unchanged; every span carries
`delivery` and `source`.

What a human still has to check before promoting to `<stem>_ads.truth.json`:
  * SponsorBlock coverage is community-sourced; a host read nobody submitted
    is simply missing (K4 saw ~2 reads per JRE episode, both found).
  * Segment mapping uses the same half-duration rule as the stitch-map script,
    so edges are at STT segment resolution, not the sub-second silver times.
  * SponsorBlock data is CC BY-NC-SA 4.0: evaluation only, never training.

The output goes to gitignored `data/truth-drafts/`, never into the repository:
the host-read spans are SponsorBlock data (CC BY-NC-SA 4.0) about copyrighted
episodes, and the project publishes no such content (decided 2026-09-07).

Usage:
  scripts/merge_truth_sources.py --stt-dir data/fixtures/jre \
      --inserted-dir tests/fixtures/truth-drafts --silver-dir data/sponsorblock \
      --out-dir data/truth-drafts
"""

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from stitchmap_to_truth import map_to_segments  # noqa: E402

SB_LICENCE = "SponsorBlock data CC BY-NC-SA 4.0 (https://sponsor.ajay.app) - evaluation only, never training"


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def silver_intervals(sv, cats):
    """SponsorBlock segments in RSS time. The silver files already carry RSS
    times (`segments_in_rss_time: true`); older files carried YouTube times
    plus a single offset, handled the same way as scripts/sb_compare.py."""
    off = sv.get("offset_sec") or 0.0
    in_rss = sv.get("segments_in_rss_time", True)
    out = []
    for s in sv.get("segments") or []:
        if s.get("category") not in cats:
            continue
        st = s["start"] if in_rss else s["start"] + off
        en = s["end"] if in_rss else s["end"] + off
        out.append({"start": round(st, 3), "end": round(en, 3), "category": s.get("category"),
                    "uuid": s.get("UUID"), "votes": s.get("votes"), "locked": s.get("locked")})
    return sorted(out, key=lambda x: x["start"])


def overlap(a, b):
    return max(0.0, min(a["end"], b["end"]) - max(a["start"], b["start"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stt-dir", default="data/fixtures/jre")
    ap.add_argument("--inserted-dir", default="tests/fixtures/truth-drafts")
    ap.add_argument("--silver-dir", default="data/sponsorblock")
    ap.add_argument("--out-dir", default="data/truth-drafts",
                    help="gitignored on purpose; see the module docstring")
    ap.add_argument("--categories", default="sponsor,selfpromo",
                    help="SponsorBlock categories taken as host-read ads")
    ap.add_argument("--json", default=None, help="write the summary rows here")
    args = ap.parse_args()
    cats = set(args.categories.split(","))
    os.makedirs(args.out_dir, exist_ok=True)

    rows = []
    print("| episode | inserted breaks | inserted s | host reads (SB) | host-read s | total ad s | ad %% | overlaps | mapped |")
    print("|---|---|---|---|---|---|---|---|---|")
    for stt in sorted(glob.glob(os.path.join(args.stt_dir, "*_stt.json"))):
        stem = os.path.basename(stt)[: -len("_stt.json")]
        ins_p = os.path.join(args.inserted_dir, stem + "_ads.truth.inserted.json")
        sv_p = os.path.join(args.silver_dir, stem + "_silver.json")
        if not (os.path.exists(ins_p) and os.path.exists(sv_p)):
            print("| %s | missing %s |" % (stem[:44], "inserted file" if not os.path.exists(ins_p) else "silver file"))
            continue
        ins, sv = load(ins_p), load(sv_p)
        segs = load(stt).get("segments") or []
        n = len(segs)
        duration = float(segs[-1].get("end") or 0.0) if segs else 0.0

        breaks = ins.get("breaks") or []
        reads = silver_intervals(sv, cats)
        overlaps = [(r, b) for r in reads for b in breaks if overlap(r, b) > 0.0]

        spans, unmapped = [], []
        # One interval at a time: map_to_segments silently skips an interval that
        # covers no segment by half its duration, so zipping would misalign.
        for b in breaks:
            m = map_to_segments([b], segs)
            if not m:
                unmapped.append(("inserted", b["start"], b["end"]))
                continue
            m[0].update({"start": b["start"], "end": b["end"], "source": "megaphone-stitch-map",
                         "creatives": b.get("creatives"), "slots": b.get("slots")})
            spans.append(m[0])
        for r in reads:
            m = map_to_segments([{"start": r["start"], "end": r["end"], "slots": ["host"]}], segs)
            if not m:
                unmapped.append(("host-read", r["start"], r["end"]))
                continue
            m[0].update({"kind": "midroll", "delivery": "host-read", "start": r["start"], "end": r["end"],
                         "source": "sponsorblock", "category": r["category"], "sponsorblock_uuid": r["uuid"],
                         "sponsorblock_votes": r["votes"], "sponsorblock_locked": r["locked"]})
            spans.append(m[0])
        spans.sort(key=lambda s: s["start_index"])
        # postroll: an inserted break that runs to the end of the file
        for sp in spans:
            if sp["source"] == "megaphone-stitch-map" and duration and sp["end"] >= duration - 2.0:
                sp["kind"] = "postroll"

        ins_sec = round(sum(b["end"] - b["start"] for b in breaks), 1)
        host_sec = round(sum(r["end"] - r["start"] for r in reads), 1)
        out = {
            "schema_version": 1, "kind": "ground_truth", "episode": stem, "segment_count": n,
            "duration_sec": round(duration, 1),
            "labeled_by": "machine-draft: megaphone stitch map (inserted) + SponsorBlock silver (host-read)",
            "source": "machine-draft", "status": "needs_human_review",
            "sources": {
                "inserted": {"file": os.path.relpath(ins_p), "sha256": ins.get("sha256"), "breaks": len(breaks),
                             "creatives": sum(b.get("creatives") or 0 for b in breaks), "seconds": ins_sec},
                "host_read": {"file": os.path.relpath(sv_p), "video_id": sv.get("video_id"),
                              "method": sv.get("method"), "offset_consistent": sv.get("offset_consistent"),
                              "reads": len(reads), "seconds": host_sec, "licence": SB_LICENCE},
            },
            "spans": spans,
            "overlaps": [{"sponsorblock": r, "break": b, "seconds": round(overlap(r, b), 2)} for r, b in overlaps],
            "unmapped": [{"delivery": d, "start": a, "end": b} for d, a, b in unmapped],
            "notes": [
                "Draft produced by scripts/merge_truth_sources.py from two model-free sources; a human must "
                "confirm every span before this becomes <stem>_ads.truth.json.",
                "Inserted spans are exact for this copy (sha256 in sources.inserted); host-read spans are "
                "SponsorBlock community labels shifted into RSS time by the stitch map (track L) and may miss a read "
                "nobody submitted.",
                "Segment indices use the half-duration rule of stitchmap_to_truth.map_to_segments; `start`/`end` "
                "keep the sub-second source times.",
                SB_LICENCE,
            ],
        }
        with open(os.path.join(args.out_dir, stem + "_ads.truth.draft.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        total = ins_sec + host_sec
        row = {"episode": stem, "inserted_breaks": len(breaks), "inserted_sec": ins_sec, "host_reads": len(reads),
               "hostread_sec": host_sec, "total_ad_sec": round(total, 1),
               "ad_fraction": round(total / duration, 4) if duration else None, "overlaps": len(overlaps),
               "spans_mapped": len(spans)}
        rows.append(row)
        print("| %s | %d | %.1f | %d | %.1f | %.1f | %.1f | %d | %d/%d |" % (
            stem[:44], len(breaks), ins_sec, len(reads), host_sec, total, 100.0 * (row["ad_fraction"] or 0),
            len(overlaps), len(spans), len(breaks) + len(reads)))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
