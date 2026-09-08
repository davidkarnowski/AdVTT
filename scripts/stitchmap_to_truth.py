#!/usr/bin/env python3
"""Turn a Megaphone stitch map into time-based draft truth for inserted ads.

Megaphone's dynamic content service returns the ad stitch map of the exact
copy it served in the `x-megaphone-payload-2` response header (byte offsets
per creative, slot pre/mid/post, campaign id). `scripts/build_fixtures.py`
saves the decoded map as `data/fixtures/<show>/<stem>.megaphone-ads.json`
(`ad_map.ads[]` with `start_sec`/`end_sec` derived from the CBR bitrate and
the ID3v2 size). Research/research-log/M-dai-check.md documents the format
and the verification against the hand-labelled #2537 truth (first break at
544.7 s in both).

This script writes `<out-dir>/<stem>_ads.truth.inserted.json`:

  {"episode": stem, "source": "megaphone-stitch-map", "sha256": ..., "delivery": "inserted",
   "spans_time": [{"start": s, "end": e, "slot": "pre|mid|post", "campaign": ..., "break": n}],
   "breaks": [{"start": s, "end": e, "creatives": k}],
   "spans": [{"start_index", "end_index", "kind"}]   # only when a transcript exists
  }

Adjacent creatives are merged into breaks (gap <= 0.5 s). With a transcript
(`<stem>_stt.json`), each break is also mapped onto segment indices: a
segment belongs to the break when at least half of its duration lies inside
it, so the index-based evaluator can use the file as truth for the inserted
channel. Host-read ads are NOT in the stitch map; a full truth file is the
union of this file and reviewed host-read spans.
"""

import argparse
import glob
import json
import os


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def breaks_from_ads(ads, gap=0.5):
    ads = sorted(ads, key=lambda a: a["start_sec"])
    out = []
    for a in ads:
        if out and a["start_sec"] - out[-1]["end"] <= gap:
            out[-1]["end"] = max(out[-1]["end"], a["end_sec"])
            out[-1]["creatives"] += 1
            out[-1]["slots"].add(a["slot"])
        else:
            out.append({"start": a["start_sec"], "end": a["end_sec"], "creatives": 1, "slots": {a["slot"]}})
    for b in out:
        b["slots"] = sorted(b["slots"])
        b["start"] = round(b["start"], 3)
        b["end"] = round(b["end"], 3)
    return out


def map_to_segments(breaks, segments):
    spans = []
    for b in breaks:
        idx = []
        for i, s in enumerate(segments):
            st, en = float(s.get("start") or 0), float(s.get("end") or 0)
            if en <= st:
                continue
            inside = max(0.0, min(en, b["end"]) - max(st, b["start"]))
            if inside >= 0.5 * (en - st):
                idx.append(i)
        if idx:
            kind = "preroll" if b["slots"] == ["pre"] else "postroll" if b["slots"] == ["post"] else "midroll"
            spans.append({"start_index": idx[0], "end_index": idx[-1], "kind": kind, "delivery": "inserted"})
    return spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", default="data/fixtures/jre/*.megaphone-ads.json")
    ap.add_argument("--stt-dir", default="data/fixtures/jre")
    ap.add_argument("--out-dir", default="data/truth-drafts")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    print("| episode | creatives | breaks | inserted s | slots | transcript mapped |")
    print("|---|---|---|---|---|---|")
    for p in sorted(glob.glob(args.maps)):
        d = load(p)
        stem = d["stem"]
        ads = (d.get("ad_map") or {}).get("ads") or []
        breaks = breaks_from_ads(ads)
        out = {
            "episode": stem, "guid": d.get("guid"), "source": "megaphone-stitch-map",
            "sha256": d.get("sha256"), "bytes": d.get("bytes"), "delivery": "inserted",
            "bitrate_bps": (d.get("ad_map") or {}).get("bitrate_bps"),
            "spans_time": [{"start": a["start_sec"], "end": a["end_sec"], "slot": a["slot"],
                            "campaign": a.get("campaign"), "ad_id": a.get("ad_id")} for a in ads],
            "breaks": breaks,
            "inserted_seconds": round(sum(b["end"] - b["start"] for b in breaks), 1),
            "notes": ["Inserted creatives only, from the Megaphone stitch map of this exact copy (sha256 above). "
                      "Host-read ads are not included; a complete truth file needs human review of the transcript."],
        }
        stt = os.path.join(args.stt_dir, stem + "_stt.json")
        mapped = False
        if os.path.exists(stt):
            segs = load(stt).get("segments") or []
            out["segment_count"] = len(segs)
            out["spans"] = map_to_segments(breaks, segs)
            mapped = True
        with open(os.path.join(args.out_dir, stem + "_ads.truth.inserted.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        slots = sorted({a["slot"] for a in ads})
        print("| %s | %d | %d | %.1f | %s | %s |" % (stem[:44], len(ads), len(breaks), out["inserted_seconds"],
                                                    "/".join(slots), "yes" if mapped else "no"))


if __name__ == "__main__":
    main()
