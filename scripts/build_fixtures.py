#!/usr/bin/env python3
"""
build_fixtures.py -- select recent episodes from a podcast RSS feed, download
each enclosure twice (dynamic-ad-insertion check), transcribe copy .a with
whisper-mlx, and record everything in tests/fixtures/manifest.json.

Stdlib only for feed/download/hash work; ffprobe for durations; transcription
runs in a subprocess under the PodcastFetch virtualenv (mlx_whisper lives
there) through the AdVTT STT seam (src/advtt/stt.py).

Everything is written incrementally:
  data/logs/fixtures-<show>.log        one line per step (created before the
                                        first network request)
  data/logs/<show>-feed-items.json     every parsed <item>
  data/episodes/<show>/<stem>.{a,b}.mp3
  data/fixtures/<show>/<stem>_stt.json
  tests/fixtures/manifest.json         merged by guid after every episode
  Research/local/PROGRESS.md           "## Log" status lines (gitignored work log)

Example (PDB):
  python3 scripts/build_fixtures.py --show pdb \
      --feed https://feeds.megaphone.fm/THFD6217271651 --count 5 \
      --seed 20260906 --days 30 \
      --exclude-titles "August 3rd 2026 How Iran Secretly Planned the Next" \
                       "PDB Afternoon Bulletin August 3rd 2026" \
                       "PDB Afternoon Bulletin August 8th 2026"
"""

import argparse
import datetime as dt
import email.utils
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
USER_AGENT = "AdVTT/0.1"
FFPROBE = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"
# The transcribing python must have mlx-whisper; the PodcastFetch venv does, when
# PODCASTFETCH_ROOT points at that (private) checkout. Otherwise this interpreter.
DEFAULT_PYTHON = (os.path.join(os.environ["PODCASTFETCH_ROOT"], ".venv", "bin", "python")
                  if os.environ.get("PODCASTFETCH_ROOT") else sys.executable)
PROGRESS_PATH = os.path.join(ROOT, "Research", "local", "PROGRESS.md")
DEFAULT_MODEL = "mlx-community/whisper-small-mlx"
ITUNES = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"
HEAD_BYTES = 64 * 1024
RETRIES = 3

# Python source run inside the venv for one transcription. argv: mp3, out, model.
TRANSCRIBE_SRC = r'''
import json, sys, time, datetime
from advtt import stt
mp3, out, model = sys.argv[1:4]
p = stt.make_provider("whisper-mlx", model=model, word_timestamps=True)
if p is None:
    raise SystemExit("whisper-mlx provider unavailable")
t0 = time.time()
res = p.transcribe(wav_path=mp3)
dt_ = time.time() - t0
doc = {
    "engine": "whisper-mlx",
    "model": model,
    "transcribed_at": datetime.datetime.now().isoformat(),
    "processing_time_sec": round(dt_, 1),
    "word_count": len(res["text"].split()),
    "segment_count": len(res["segments"]),
    "has_words": bool(res.get("has_words")),
    "timing": res["timing"],
    "text": res["text"],
    "segments": res["segments"],
}
tmp = out + ".tmp"
with open(tmp, "w") as fh:
    json.dump(doc, fh, ensure_ascii=False)
import os
os.replace(tmp, out)
print("RESULT " + json.dumps({k: doc[k] for k in
      ("processing_time_sec", "word_count", "segment_count", "has_words", "timing")}))
'''


# --------------------------------------------------------------------------- log
class Log:
    def __init__(self, path, progress_path, tag):
        self.path = path
        self.progress_path = progress_path
        self.tag = tag
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a") as fh:
            fh.write("=== %s start %s ===\n" % (tag, now_iso()))

    def __call__(self, msg):
        line = "[%s] %s" % (now_iso(timespec="seconds"), msg)
        print(line, flush=True)
        with open(self.path, "a") as fh:
            fh.write(line + "\n")

    def progress(self, msg):
        """Append a status line to the work log's trailing '## Log' section."""
        stamp = dt.datetime.now().strftime("%H:%M")
        with open(self.progress_path, "a") as fh:
            fh.write("- [%s %s] %s\n" % (self.tag, stamp, msg))


def now_iso(timespec="seconds"):
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec=timespec)


# -------------------------------------------------------------------- network
def http_get(url, log, timeout=60):
    """Open url with retries/backoff. Returns the response object (caller reads)."""
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            return urllib.request.urlopen(req, timeout=timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            last = e
            wait = 2 ** attempt
            log("  retry %d/%d after error: %s (sleep %ds)" % (attempt, RETRIES, e, wait))
            time.sleep(wait)
    raise RuntimeError("GET failed after %d attempts: %s (%s)" % (RETRIES, url, last))


def fetch_feed(url, log):
    log("feed fetch %s" % url)
    with http_get(url, log) as r:
        raw = r.read()
        final = r.geturl()
    log("feed fetched %d bytes, final url %s" % (len(raw), final))
    return raw


def parse_items(raw):
    root = ET.fromstring(raw)
    items = []
    for it in root.iter("item"):
        enc = it.find("enclosure")
        pub = (it.findtext("pubDate") or "").strip()
        pub_iso = None
        try:
            d = email.utils.parsedate_to_datetime(pub)
            # RFC 5322 "-0000" means "no zone information"; parsedate_to_datetime
            # then returns a naive datetime and .astimezone() would read it as
            # local time (measured 2026-09-06 on the megaphone JRE feed: every
            # 17:00 -0000 pubDate came out as 00:00 UTC the next day, shifting
            # stems and the window edge by +7 h). Treat naive as UTC.
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.timezone.utc)
            pub_iso = d.astimezone(dt.timezone.utc).isoformat()
        except Exception:
            pass
        items.append({
            "guid": (it.findtext("guid") or "").strip(),
            "title": (it.findtext("title") or "").strip(),
            "pubDate": pub,
            "pubDate_iso": pub_iso,
            "enclosure_url": enc.get("url") if enc is not None else None,
            "enclosure_length": enc.get("length") if enc is not None else None,
            "enclosure_type": enc.get("type") if enc is not None else None,
            "itunes_duration": (it.findtext(ITUNES + "duration") or "").strip() or None,
            "itunes_episode_type": (it.findtext(ITUNES + "episodeType") or "").strip() or None,
        })
    return items


# ------------------------------------------------------------------ selection
def norm_title(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def slugify(title, maxlen=60):
    s = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    return s[:maxlen].rstrip("_")


def make_stem(item):
    d = dt.datetime.fromisoformat(item["pubDate_iso"])
    return "%s_%s_%s" % (d.strftime("%Y-%m-%d"), d.strftime("%H%M"), slugify(item["title"]))


def is_excluded(item, excludes):
    nt = norm_title(item["title"])
    for ex in excludes:
        ne = norm_title(ex.replace("...", ""))
        if ne and nt.startswith(ne):
            return True
    return False


def kind_of(title):
    t = title.lower()
    if "afternoon bulletin" in t:
        return "afternoon"
    if "situation report" in t:
        return "sitrep"
    return "morning"


# -------------------------------------------------------------------- download
def download(url, dest, log):
    """Stream url to dest, following redirects. Returns (final_url, bytes)."""
    tmp = dest + ".part"
    with http_get(url, log, timeout=120) as r:
        final = r.geturl()
        n = 0
        with open(tmp, "wb") as fh:
            while True:
                chunk = r.read(1 << 20)
                if not chunk:
                    break
                fh.write(chunk)
                n += len(chunk)
    os.replace(tmp, dest)
    return final, n


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe_duration(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
    try:
        return round(float(out.stdout.decode().strip()), 3)
    except ValueError:
        return None


def id3v2_size(path):
    """Total ID3v2 tag length (header + payload) or 0 when no tag."""
    with open(path, "rb") as fh:
        hdr = fh.read(10)
    if len(hdr) < 10 or hdr[:3] != b"ID3":
        return 0
    size = 0
    for b in hdr[6:10]:
        size = (size << 7) | (b & 0x7F)
    return 10 + size


def compare_copies(a, b):
    """Return DAI notes for two downloads of the same enclosure."""
    notes = {}
    with open(a, "rb") as fa, open(b, "rb") as fb:
        notes["head_64k_differs"] = fa.read(HEAD_BYTES) != fb.read(HEAD_BYTES)
    ia, ib = id3v2_size(a), id3v2_size(b)
    notes["id3v2_bytes"] = {"a": ia, "b": ib}
    # audio payload after the ID3v2 tag: hash both tails
    ha, hb = hashlib.sha256(), hashlib.sha256()
    for path, off, h in ((a, ia, ha), (b, ib, hb)):
        with open(path, "rb") as fh:
            fh.seek(off)
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
    notes["audio_after_id3_identical"] = ha.hexdigest() == hb.hexdigest()
    return notes


# ---------------------------------------------------------------- transcribe
def transcribe(mp3, out_json, model, python, log):
    env = dict(os.environ, PYTHONPATH=os.path.join(ROOT, "src"))
    t0 = time.time()
    proc = subprocess.run([python, "-c", TRANSCRIBE_SRC, mp3, out_json, model],
                          cwd=ROOT, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    wall = time.time() - t0
    out = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")
    if proc.returncode != 0:
        raise RuntimeError("transcription failed rc=%d: %s" % (proc.returncode, err[-800:]))
    for line in out.splitlines():
        if line.startswith("RESULT "):
            res = json.loads(line[7:])
            res["wall_sec"] = round(wall, 1)
            return res
    raise RuntimeError("transcription produced no RESULT line; stderr tail: %s" % err[-400:])


# ------------------------------------------------------------------ manifest
def load_manifest(path):
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    return {"generated": now_iso(), "episodes": []}


def save_manifest(path, manifest, entry):
    """Merge entry by guid into the manifest on disk.

    Re-reads the file first: two build_fixtures runs (pdb, jre) can be alive at
    once, and merging into a copy loaded at startup would drop the other run's
    entries. `manifest` is refreshed in place so the caller's view stays current.
    """
    on_disk = load_manifest(path)
    manifest.clear()
    manifest.update(on_disk)
    manifest["generated"] = now_iso()
    eps = [e for e in manifest["episodes"] if e.get("guid") != entry["guid"]]
    eps.append(entry)
    eps.sort(key=lambda e: (e.get("show", ""), e.get("pubDate", "")))
    manifest["episodes"] = eps
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def fmt_dur(sec):
    if sec is None:
        return "?"
    sec = int(round(sec))
    return "%d:%02d:%02d" % (sec // 3600, sec % 3600 // 60, sec % 60)


def summary_table(rows):
    hdr = "| # | episode | date | duration | DAI | segments | STT time |\n|---|---|---|---|---|---|---|\n"
    body = ""
    for i, r in enumerate(rows, 1):
        body += "| %d | %s | %s | %s | %s | %s | %s |\n" % (
            i, r["title"][:70], r["pubDate"][:10], fmt_dur(r["duration_sec"]),
            r["dai_verdict"], r.get("segments", "-"),
            ("%.0fs" % r["stt_sec"]) if r.get("stt_sec") is not None else "-")
    return hdr + body


# ----------------------------------------------------------------------- main
def process_episode(item, args, log, manifest, manifest_path):
    stem = make_stem(item)
    ep_dir = os.path.join(ROOT, "data", "episodes", args.show)
    fx_dir = os.path.join(ROOT, "data", "fixtures", args.show)
    os.makedirs(ep_dir, exist_ok=True)
    os.makedirs(fx_dir, exist_ok=True)
    paths = {c: os.path.join(ep_dir, "%s.%s.mp3" % (stem, c)) for c in ("a", "b")}
    stt_path = os.path.join(fx_dir, stem + "_stt.json")
    log("episode start guid=%s stem=%s" % (item["guid"], stem))

    entry = {
        "show": args.show, "guid": item["guid"], "title": item["title"],
        "pubDate": item["pubDate_iso"], "enclosure_url": item["enclosure_url"],
        "final_host": None, "itunes_duration": item["itunes_duration"],
        "stem": stem, "downloads": [], "dai_verdict": None, "dai_notes": {},
        "stt": None, "status": "downloading",
    }

    # -- downloads (two independent fetches of the same enclosure)
    for copy in ("a", "b"):
        dest = paths[copy]
        if os.path.exists(dest) and os.path.getsize(dest) > 0 and args.resume:
            log("  copy %s exists (%d bytes), resume: reusing" % (copy, os.path.getsize(dest)))
            final = None
        else:
            t0 = time.time()
            final, n = download(item["enclosure_url"], dest, log)
            log("  copy %s downloaded %d bytes in %.1fs -> %s" % (copy, n, time.time() - t0, dest))
        if final and entry["final_host"] is None:
            entry["final_host"] = urllib.parse.urlsplit(final).netloc
            log("  redirect chain ends at host %s" % entry["final_host"])
        digest = sha256_of(dest)
        size = os.path.getsize(dest)
        dur = ffprobe_duration(dest)
        log("  copy %s sha256=%s bytes=%d duration=%s" % (copy, digest, size, dur))
        entry["downloads"].append({"copy": copy, "sha256": digest, "bytes": size,
                                   "duration_sec": dur})

    # -- DAI verdict
    da, db = entry["downloads"]
    if da["sha256"] == db["sha256"]:
        entry["dai_verdict"] = "identical"
        entry["dai_notes"] = {"size_delta": 0, "duration_delta_sec": 0.0}
        os.remove(paths["b"])
        log("  DAI: identical (copy b removed)")
    else:
        notes = compare_copies(paths["a"], paths["b"])
        notes["size_delta"] = db["bytes"] - da["bytes"]
        notes["duration_delta_sec"] = (round(db["duration_sec"] - da["duration_sec"], 3)
                                       if None not in (da["duration_sec"], db["duration_sec"]) else None)
        notes["body_differs"] = not notes["audio_after_id3_identical"]
        entry["dai_verdict"] = "differs"
        entry["dai_notes"] = notes
        log("  DAI: differs size_delta=%+d duration_delta=%s head64k_differs=%s "
            "audio_after_id3_identical=%s id3v2=%s" % (
                notes["size_delta"], notes["duration_delta_sec"], notes["head_64k_differs"],
                notes["audio_after_id3_identical"], notes["id3v2_bytes"]))
    entry["status"] = "downloaded"
    save_manifest(manifest_path, manifest, entry)
    log.progress("%s: downloaded 2x, DAI %s" % (stem, entry["dai_verdict"]))

    # -- transcription of copy a
    if args.no_transcribe:
        return entry
    if os.path.exists(stt_path) and args.resume:
        with open(stt_path) as fh:
            doc = json.load(fh)
        res = {k: doc.get(k) for k in ("processing_time_sec", "segment_count", "has_words")}
        log("  transcript exists, resume: reusing %s" % stt_path)
    else:
        log("  transcribe start %s model=%s" % (paths["a"], args.model))
        t0 = time.time()
        res = transcribe(paths["a"], stt_path, args.model, args.python, log)
        log("  transcribe finish in %.1fs (wall %.1fs incl. model load) segments=%d words=%d has_words=%s -> %s"
            % (res["processing_time_sec"], time.time() - t0, res["segment_count"],
               res["word_count"], res["has_words"], stt_path))
    entry["stt"] = {"engine": "whisper-mlx", "model": args.model,
                    "segment_count": res["segment_count"], "has_words": res["has_words"],
                    "processing_time_sec": res["processing_time_sec"]}
    entry["status"] = "complete"
    save_manifest(manifest_path, manifest, entry)
    log.progress("%s: transcribed (%d segments, %.0fs)" % (
        stem, res["segment_count"], res["processing_time_sec"]))
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", required=True, help="short show id, e.g. pdb or jre")
    ap.add_argument("--feed", required=True, help="RSS feed URL")
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--seed", type=int, default=20260906)
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--today", default=None, help="ISO date for the window end (default: now, UTC)")
    ap.add_argument("--exclude-titles", nargs="*", default=[], help="title prefixes to skip")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--python", default=DEFAULT_PYTHON, help="interpreter with mlx_whisper")
    ap.add_argument("--no-transcribe", action="store_true")
    ap.add_argument("--resume", action="store_true", help="reuse existing downloads/transcripts")
    ap.add_argument("--dry-run", action="store_true", help="fetch feed and select only")
    args = ap.parse_args()

    tag = "fixtures-" + args.show
    log = Log(os.path.join(ROOT, "data", "logs", "%s.log" % tag),
              PROGRESS_PATH, tag)
    log("args: %s" % json.dumps(vars(args)))

    # 1. feed
    raw = fetch_feed(args.feed, log)
    items = parse_items(raw)
    feed_json = os.path.join(ROOT, "data", "logs", "%s-feed-items.json" % args.show)
    with open(feed_json, "w") as fh:
        json.dump(items, fh, indent=1, ensure_ascii=False)
    log("feed parsed: %d items -> %s" % (len(items), feed_json))

    # 2. window + exclusions + random order
    end = (dt.datetime.fromisoformat(args.today).replace(tzinfo=dt.timezone.utc)
           if args.today else dt.datetime.now(dt.timezone.utc))
    start = end - dt.timedelta(days=args.days)
    window = [i for i in items if i["pubDate_iso"] and i["enclosure_url"]
              and start <= dt.datetime.fromisoformat(i["pubDate_iso"]) <= end]
    log("window %s .. %s: %d items" % (start.date(), end.date(), len(window)))
    excluded = [i for i in window if is_excluded(i, args.exclude_titles)]
    for i in excluded:
        log("  excluded (existing fixture): %s | %s" % (i["pubDate_iso"], i["title"]))
    cands = [i for i in window if i not in excluded]
    cands.sort(key=lambda i: i["pubDate_iso"], reverse=True)   # deterministic pre-shuffle order
    rng = random.Random(args.seed)
    rng.shuffle(cands)
    log("seed=%d candidates=%d; random order (first %d are the draw, rest are fallbacks):"
        % (args.seed, len(cands), args.count))
    for n, i in enumerate(cands):
        log("  %2d %s %s | %s | %s" % (n + 1, "*" if n < args.count else " ",
                                     i["pubDate_iso"], kind_of(i["title"]), i["title"]))
    draw = cands[:args.count]
    kinds = {}
    for i in draw:
        kinds[kind_of(i["title"])] = kinds.get(kind_of(i["title"]), 0) + 1
    log("draw guids: %s" % json.dumps([i["guid"] for i in draw]))
    log("draw mix: %s" % json.dumps(kinds))
    log.progress("feed %d items, %d in window, %d excluded, seed %d, draw mix %s"
                 % (len(items), len(window), len(excluded), args.seed, kinds))
    if args.dry_run:
        return 0

    # 3-5. per-episode pipeline, walking the shuffled list until count complete
    manifest_path = os.path.join(ROOT, "tests", "fixtures", "manifest.json")
    manifest = load_manifest(manifest_path)
    done, failed = [], []
    for item in cands:
        if len(done) >= args.count:
            break
        try:
            entry = process_episode(item, args, log, manifest, manifest_path)
            done.append({"title": item["title"], "pubDate": item["pubDate_iso"],
                         "duration_sec": entry["downloads"][0]["duration_sec"],
                         "dai_verdict": entry["dai_verdict"],
                         "segments": (entry["stt"] or {}).get("segment_count", "-"),
                         "stt_sec": (entry["stt"] or {}).get("processing_time_sec")})
        except Exception as e:      # log, skip, fall through to the next candidate
            log("  FAILED guid=%s: %s -- skipping, taking next candidate" % (item["guid"], e))
            log.progress("FAILED %s: %s" % (item["title"][:60], str(e)[:120]))
            failed.append((item["title"], str(e)))

    # 7. summary
    table = summary_table(done)
    log("SUMMARY (%d complete, %d failed)\n%s" % (len(done), len(failed), table))
    for t, e in failed:
        log("  failed: %s: %s" % (t, e))
    with open(PROGRESS_PATH, "a") as fh:
        fh.write("- [%s %s] %s summary (%d complete, %d failed):\n\n%s\n"
                 % (tag, dt.datetime.now().strftime("%H:%M"), args.show.upper(),
                    len(done), len(failed), table))
    print(table)
    return 0 if len(done) >= args.count else 1


if __name__ == "__main__":
    sys.exit(main())
