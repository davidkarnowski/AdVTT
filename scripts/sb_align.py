#!/usr/bin/env python3
"""Align a YouTube audio copy of an episode with the RSS audio copy and map
SponsorBlock segments (YouTube time) into RSS time.

Method: both files -> 8 kHz mono PCM (ffmpeg) -> log-RMS energy envelope at
100 ms hops -> normalised cross-correlation of YouTube windows against the RSS
envelope over a bounded lag range. Windows: first 5 min, +/-2.5 min around each
SponsorBlock sponsor segment, last 5 min, plus a coarse profile every 10 min.
Offset convention: rss_time = yt_time + offset.

Usage: sb_align.py <yt_audio> <rss_audio> <sponsorblock_json> <out_json> [--lag-min S] [--lag-max S]
Needs numpy and ffmpeg on PATH (or in the usual Homebrew location).
SponsorBlock data is CC BY-NC-SA 4.0: evaluation only, never training.
"""
import json, subprocess, sys, argparse, os
import numpy as np

import shutil
FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
SR = 8000
HOP = 800  # 100 ms

def decode(path):
    p = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0

def envelope(x, hop=HOP):
    n = len(x) // hop
    fr = x[: n * hop].reshape(n, hop)
    e = np.sqrt((fr ** 2).mean(axis=1) + 1e-10)
    return np.log(e)

def ncc(a, b_full, start_hop, lag_lo, lag_hi):
    """Normalised cross-correlation of window a (from YT envelope, starting at
    start_hop) against b_full over lags lag_lo..lag_hi (hops). Returns (lags, scores)."""
    n = len(a)
    a = a - a.mean(); an = np.linalg.norm(a) + 1e-9
    lo = start_hop + lag_lo; hi = start_hop + lag_hi + n
    pad_lo = max(0, -lo); lo = max(lo, 0); hi = min(hi, len(b_full))
    seg = b_full[lo:hi]
    if len(seg) < n: return None, None
    # sliding dot via correlate, sliding norm via cumsums
    dots = np.correlate(seg, a, mode="valid")
    cs = np.cumsum(np.insert(seg, 0, 0.0)); cs2 = np.cumsum(np.insert(seg ** 2, 0, 0.0))
    sums = cs[n:] - cs[:-n]; sq = cs2[n:] - cs2[:-n]
    var = sq - sums ** 2 / n
    norms = np.sqrt(np.maximum(var, 1e-9))
    scores = dots / (an * norms)
    lags = np.arange(len(scores)) + (lo - start_hop)
    return lags, scores

def best(lags, scores):
    i = int(np.argmax(scores)); pk = float(scores[i])
    # second peak at least 2 s away
    mask = np.abs(lags - lags[i]) > 20
    second = float(scores[mask].max()) if mask.any() else 0.0
    return int(lags[i]), pk, second

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("yt"); ap.add_argument("rss"); ap.add_argument("sb"); ap.add_argument("out")
    ap.add_argument("--lag-min", type=float, default=-120.0)
    ap.add_argument("--lag-max", type=float, default=720.0)
    ap.add_argument("--stem", default=None)
    a = ap.parse_args()
    sb = json.load(open(a.sb)); segs = sb["segments"]
    yt = envelope(decode(a.yt)); rss = envelope(decode(a.rss))
    yt_dur = len(yt) / 10.0; rss_dur = len(rss) / 10.0
    W = 3000  # 5 min in hops
    windows = [("first5", 0, W)]
    for s in segs:
        if s["category"] != "sponsor" or s["segment"][1] - s["segment"][0] < 10: continue
        c = int((s["segment"][0] + s["segment"][1]) / 2 * 10)
        windows.append((f"sponsor@{s['segment'][0]:.0f}", max(0, c - W // 2), min(len(yt), c + W // 2)))
    windows.append(("last5", max(0, len(yt) - W), len(yt)))
    for t in range(6000, len(yt) - W, 6000):  # every 10 min profile
        windows.append((f"profile@{t//10}", t, t + W))
    lag_lo, lag_hi = int(a.lag_min * 10), int(a.lag_max * 10)
    res = []
    for name, s0, s1 in windows:
        lags, sc = ncc(yt[s0:s1], rss, s0, lag_lo, lag_hi)
        if lags is None:
            res.append({"window": name, "yt_start": s0 / 10, "yt_end": s1 / 10, "status": "no-overlap"}); continue
        lag, pk, second = best(lags, sc)
        res.append({"window": name, "yt_start": s0 / 10, "yt_end": s1 / 10, "offset_sec": lag / 10.0,
                    "ncc_peak": round(pk, 3), "ncc_second": round(second, 3),
                    "confident": bool(pk > 0.5 and pk - second > 0.1)})
    # decide
    key = [r for r in res if r["window"] in ("first5", "last5") or r["window"].startswith("sponsor")]
    offs = [r["offset_sec"] for r in key if r.get("confident")]
    agree = bool(offs) and (max(offs) - min(offs) <= 1.0)
    mapped = []
    for s in segs:
        c = (s["segment"][0] + s["segment"][1]) / 2
        cands = [r for r in res if r.get("confident") and r["yt_start"] <= c <= r["yt_end"]]
        if not cands:
            cands = sorted([r for r in res if r.get("confident")], key=lambda r: abs((r["yt_start"] + r["yt_end"]) / 2 - c))[:1]
        if not cands:
            mapped.append({**s, "rss_segment": None, "offset_sec": None, "confidence": "none"}); continue
        r = cands[0]; off = r["offset_sec"]
        inside = r["yt_start"] <= c <= r["yt_end"]
        mapped.append({"category": s["category"], "yt_segment": s["segment"], "votes": s["votes"], "locked": s["locked"], "UUID": s["UUID"],
                       "rss_segment": [round(s["segment"][0] + off, 1), round(s["segment"][1] + off, 1)],
                       "offset_sec": off, "offset_window": r["window"], "ncc_peak": r["ncc_peak"],
                       "confidence": "high" if inside and r["ncc_peak"] > 0.7 else ("medium" if inside else "low"),
                       "tier": "gold" if s["locked"] else ("silver" if s["votes"] >= 2 else "bronze")})
    out = {"stem": a.stem or os.path.basename(a.rss), "yt_file": a.yt, "rss_file": a.rss, "videoID": sb["videoID"],
           "yt_duration_sec": round(yt_dur, 1), "rss_duration_sec": round(rss_dur, 1),
           "method": "8kHz mono, log-RMS 100ms envelope, NCC per window; rss_time = yt_time + offset",
           "lag_range_sec": [a.lag_min, a.lag_max], "windows": res,
           "key_offsets_sec": offs, "key_windows_agree_within_1s": agree,
           "verdict": ("same cut (single global offset)" if agree and offs else ("different cut: offset varies by window (inserted/removed material)" if offs else "alignment failed")),
           "licence": "SponsorBlock data CC BY-NC-SA 4.0 - evaluation only", "segments": mapped}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("yt_duration_sec", "rss_duration_sec", "key_offsets_sec", "key_windows_agree_within_1s", "verdict")}))
    for r in res: print(r)

if __name__ == "__main__":
    main()
