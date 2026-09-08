#!/usr/bin/env python3
"""Transcribe downloaded fixture audio with Gladia (paid) into PodcastFetch-shaped
<stem>_stt.json files, one episode at a time, logging incrementally.

Usage: python3 scripts/transcribe_gladia.py --show jre [--only STEM ...]
Reads data/episodes/<show>/<stem>.a.mp3, writes data/fixtures/<show>/<stem>_stt.json
and updates tests/fixtures/manifest.json (stt block, status "complete").
"""
import argparse, datetime, glob, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from advtt import stt  # loads .env (GLADIA_API_KEY)

ap = argparse.ArgumentParser(); ap.add_argument("--show", required=True); ap.add_argument("--only", nargs="*")
args = ap.parse_args()
log_path = "data/logs/transcribe-gladia-%s.log" % args.show
def log(msg):
    line = "[%s] %s" % (datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), msg)
    print(line, flush=True)
    with open(log_path, "a") as f: f.write(line + "\n")

prov = stt.GladiaProvider()
ok, msg = prov.ensure_ready(); log("gladia ready=%s %s" % (ok, msg))
if not ok: sys.exit(2)
for mp3 in sorted(glob.glob("data/episodes/%s/*.a.mp3" % args.show)):
    stem = os.path.basename(mp3)[:-len(".a.mp3")]
    if args.only and stem not in args.only: continue
    out = "data/fixtures/%s/%s_stt.json" % (args.show, stem)
    if os.path.exists(out): log("skip (exists) %s" % stem); continue
    log("start %s (%d MB)" % (stem, os.path.getsize(mp3) >> 20))
    t0 = time.time()
    res = None
    for attempt in range(1, 4):
        try:
            res = prov.transcribe(wav_path=mp3)
            break
        except Exception as e:
            log("attempt %d failed for %s: %s" % (attempt, stem, str(e)[:300]))
            time.sleep(30 * attempt)
    if res is None:
        log("FAILED %s after 3 attempts" % stem); continue
    dt = time.time() - t0
    segs = res.get("segments") or []
    # PodcastFetch word shape is {w,s,e}; Gladia's is {word,start,end}
    for s in segs:
        if s.get("words"):
            s["words"] = [{"w": w.get("word") or w.get("w"), "s": w.get("start", w.get("s")), "e": w.get("end", w.get("e"))} for w in s["words"]]
    doc = {"engine": "gladia", "model": prov.model, "transcribed_at": datetime.datetime.now().isoformat(timespec="seconds"),
           "processing_time_sec": round(dt, 1), "word_count": sum(len(s.get("words") or []) for s in segs),
           "segment_count": len(segs), "has_words": bool(res.get("has_words")), "timing": res.get("timing"),
           "diarization": res.get("diarization"), "text": res.get("text"), "segments": segs}
    tmp = out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(doc, f, ensure_ascii=False, indent=0)
    os.replace(tmp, out)
    log("done %s: %d segments, words=%s, %.0f s" % (stem, len(segs), doc["has_words"], dt))
    try:
        mp = "tests/fixtures/manifest.json"; m = json.load(open(mp))
        for e in m.get("episodes", []):
            if e.get("stem") == stem:
                e["stt"] = {"engine": "gladia", "model": prov.model, "segment_count": len(segs), "has_words": doc["has_words"], "processing_time_sec": round(dt, 1)}
                e["status"] = "complete"
        json.dump(m, open(mp, "w"), indent=1)
    except Exception as e:
        log("manifest update failed: %s" % e)
    with open(os.path.join("Research", "local", "PROGRESS.md"), "a") as f:
        f.write("- [gladia-%s %s] transcribed %s: %d segments in %.0f s\n" % (args.show, datetime.datetime.now().strftime("%H:%M"), stem, len(segs), dt))
log("all done")
