"""The `advtt` command.

    advtt EPISODE.mp3                      transcribe (STT seam), classify, write EPISODE_stt.json + EPISODE.advtt.json + EPISODE.analysis.json
    advtt --stt EPISODE_stt.json           classify an existing PodcastFetch-style transcript
    advtt --captions EPISODE.vtt [--media EPISODE.mp3]
    advtt --dump-prompt EPISODE_stt.json   print exactly what the model is asked (regression check vs adclass.py)
    advtt --self-test                      the validation ladder, offline, free
    advtt --eval 'fixtures/*/*_stt.json' [--classify] [--out-dir DIR]
    advtt --list-providers
    advtt --describe                       machine-readable capabilities (providers, models, exporters, schema)
    advtt --dry-run --stt X_stt.json       plan chunks and estimate cost; no model call
    advtt --export all --record X.advtt.json   render an existing record into every exporter format
    advtt ... --log-json events.jsonl      JSON Lines event stream for agents and CI

Exit codes (stable): 0 ok; 1 usage; 2 classification not ok (rejected/failed);
3 output exists (pass --force); 4 provider unavailable or refused by --offline;
5 input unreadable; 6 self-test or eval failed a gate.
"""

import argparse
import json
import os
import sys
import time

from . import __version__
from .captions import read_captions
from .chunking import plan_chunks
from .classify import classify_segments
from .config import loaded_env_files, offline_mode
from .evaluate import evaluate, self_test
from .events import EventLog, LoggingProvider
from .exporters import EXT, FORMATS, export_all
from .io import load_json, source_sha256
from .prompts import SYSTEM_PROMPT, build_user_prompt, response_schema
from .providers import DEFAULT_PROVIDER, PROVIDERS, ProviderError, RecordingProvider, available_providers, make_provider
from .providers.capabilities import CLAUDE_MODELS, EFFORT_LEVELS, capabilities, estimate_cost_usd
from .record import PROFILE, build_analysis, build_record, media_fingerprint, validate_record, write_json
from .validate import (AD_THRESHOLD, CONTEXT_SEGMENTS, MAX_AD_FRACTION, MAX_SPAN_SECONDS, PROMPT_VERSION,
                       SCHEMA_VERSION, STATUS_OK, UNCERTAIN_THRESHOLD)
from .prompts import SYSTEM_PROMPT as _SP
import datetime
import hashlib


def _out_paths(stem, out_dir=None):
    base = os.path.basename(stem)
    d = out_dir or os.path.dirname(os.path.abspath(stem))
    return os.path.join(d, base + ".advtt.json"), os.path.join(d, base + ".analysis.json")


def _stem_for(path):
    p = str(path)
    if p.endswith("_stt.json"):
        return p[: -len("_stt.json")]
    return os.path.splitext(p)[0]


def _provider_from_args(args):
    prov = make_provider(args.provider, model=args.model, endpoint=args.endpoint)
    if args.chunk:
        prov.max_chunk_tokens = args.chunk
    if args.effort and hasattr(prov, "effort"):
        prov.effort = args.effort
    if args.record_replay:
        prov = RecordingProvider(prov, store=args.replay_store)
    return prov


def _transcribe(media_path, args):
    from . import stt as sttmod
    prov = sttmod.make_provider(args.stt_provider or "auto", model=args.stt_model, word_timestamps=True)
    if prov is None:
        raise SystemExit("no STT provider available (tried %s); pass --stt-provider" % (args.stt_provider or "auto"))
    if offline_mode() and getattr(prov, "cloud", False):
        raise SystemExit("--offline: STT provider %s would upload the audio" % prov.name)
    ok, msg = prov.ensure_ready()
    sys.stderr.write("stt %s: %s\n" % (prov.name, msg))
    if not ok:
        raise SystemExit(2)
    t0 = time.time()
    res = prov.transcribe(wav_path=media_path)
    meta = {"provider": prov.name, "model": getattr(prov, "model_id", None) or getattr(prov, "model", None),
            "timing": res.get("timing"), "has_words": bool(res.get("has_words")),
            "segment_count": len(res.get("segments") or []), "processing_time_sec": round(time.time() - t0, 1)}
    return res.get("segments") or [], meta


def _write_transcript(stem, out_dir, segments, stt_meta, media_path, force):
    """Persist the transcript as `<stem>_stt.json` (the PodcastFetch layout that
    `--stt`, `--eval` and `--dump-prompt` read back). Written before the model
    is called so a transcription is never lost to a failed or rate-limited
    classification, and a rerun can use `--stt` (or `--provider replay`)
    instead of paying for STT again. Not overwritten without --force."""
    base = os.path.join(out_dir, os.path.basename(stem)) if out_dir else stem
    path = base + "_stt.json"
    if os.path.exists(path) and not force:
        return path, False
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    doc = dict(stt_meta)
    doc.update({"source_media": os.path.abspath(media_path), "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "segments": segments})
    write_json(path, doc)
    return path, True


def describe():
    """Everything an agent needs to drive this tool, as one JSON object."""
    return {
        "tool": "advtt", "version": __version__, "profile": PROFILE,
        "prompt_version": PROMPT_VERSION, "schema_version": SCHEMA_VERSION,
        "system_prompt_sha256": hashlib.sha256(_SP.encode("utf-8")).hexdigest(),
        "thresholds": {"ad": AD_THRESHOLD, "uncertain": UNCERTAIN_THRESHOLD, "max_ad_fraction": MAX_AD_FRACTION,
                       "max_span_sec": MAX_SPAN_SECONDS, "context_segments": CONTEXT_SEGMENTS},
        "providers": available_providers(),
        "default_provider": DEFAULT_PROVIDER,
        "claude_models": CLAUDE_MODELS, "effort_levels": list(EFFORT_LEVELS),
        "stt_providers": ["gladia", "whisper-mlx", "parakeet-mlx", "openai"],
        "inputs": ["media file (ffmpeg-decodable)", "--stt <PodcastFetch _stt.json>", "--captions <.vtt|.srt>"],
        "outputs": {"transcript": "<stem>_stt.json (media input only)", "record": "<stem>.advtt.json", "analysis": "<stem>.analysis.json",
                    "exports": {f: "<stem>" + EXT[f] for f in FORMATS}},
        "record_schema": os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema", "advtt-1.0.json"),
        "exit_codes": {"0": "ok", "1": "usage", "2": "classification not ok", "3": "output exists",
                       "4": "provider unavailable or refused by --offline", "5": "input unreadable",
                       "6": "self-test or eval gate failed"},
        "events": ["run.start", "input.loaded", "provider.ready", "chunk.start", "chunk.done", "chunk.error",
                   "gate", "output.written", "output.exported", "run.done", "error"],
        "offline": offline_mode(), "env_files": loaded_env_files(),
        "gates": {"content_loss_sec": "<= 5 per episode (ship gate)", "ad_recall_sec": ">= 0.70",
                  "hostread_recall_sec": ">= 0.70 (recall on host-read truth only; inserted creatives are "
                                         "labelled by the stitch map and reported separately)",
                  "boundary_err_sec": "<= 3"},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(prog="advtt", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("media", nargs="?", help="audio/video file to transcribe and classify")
    ap.add_argument("--stt", metavar="STT_JSON", help="classify an existing transcript ({segments:[...]})")
    ap.add_argument("--captions", metavar="VTT_OR_SRT", help="classify an existing caption file")
    ap.add_argument("--media", dest="media_for_captions", metavar="FILE", help="media file to bind the record to (with --captions/--stt)")
    ap.add_argument("--dump-prompt", metavar="STT_JSON", help="print the assembled prompt and exit")
    ap.add_argument("--self-test", action="store_true", help="run the offline validation-ladder tests")
    ap.add_argument("--eval", metavar="GLOB", help="score predictions against *_ads.truth.json")
    ap.add_argument("--classify", action="store_true", help="with --eval: (re)classify before scoring")
    ap.add_argument("--inserted-dir", default=None, metavar="DIR",
                    help="with --eval: where <stem>_ads.truth.inserted.json siblings live when not beside the "
                         "transcript (default: tests/fixtures/truth-drafts if it exists)")
    ap.add_argument("--out-dir", default=None, help="where outputs go (default: beside the input)")
    ap.add_argument("--list-providers", action="store_true")
    ap.add_argument("--describe", action="store_true", help="print capabilities as JSON and exit")
    ap.add_argument("--dry-run", action="store_true", help="plan chunks and estimate cost without calling a model")
    ap.add_argument("--export", default=None, metavar="FORMATS", help="comma list or 'all': " + ",".join(FORMATS))
    ap.add_argument("--record", default=None, metavar="ADVTT_JSON", help="with --export: an existing record to render")
    ap.add_argument("--title-style", default="advtt", choices=["advtt", "sponsorblock"], help="chapter title style")
    ap.add_argument("--log-json", default=None, metavar="PATH", help="append JSON Lines events to PATH ('-' = stderr)")
    ap.add_argument("--provider", default=DEFAULT_PROVIDER, choices=sorted(PROVIDERS))
    ap.add_argument("--model", default=None)
    ap.add_argument("--endpoint", default=None)
    ap.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--chunk", type=int, default=None, help="override max_chunk_tokens")
    ap.add_argument("--max-fraction", type=float, default=MAX_AD_FRACTION)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--stt-provider", default=None, help="whisper-mlx | parakeet-mlx | gladia | openai | auto")
    ap.add_argument("--stt-model", default=None)
    ap.add_argument("--offline", action="store_true", help="refuse every network provider")
    ap.add_argument("--record-replay", action="store_true", help="record live responses into the replay store")
    ap.add_argument("--replay-store", default=None)
    ap.add_argument("--force", action="store_true", help="overwrite existing outputs")
    ap.add_argument("--json", action="store_true", help="print the record as JSON to stdout")
    ap.add_argument("--version", action="version", version="advtt %s (prompt_version %s)" % (__version__, PROMPT_VERSION))
    args = ap.parse_args(argv)

    if args.offline:
        os.environ["ADVTT_OFFLINE"] = "1"

    if args.self_test:
        return 6 if self_test() else 0

    if args.describe:
        print(json.dumps(describe(), indent=1))
        return 0

    if args.export and args.record:
        rec = load_json(args.record)
        stem = args.record[: -len(".advtt.json")] if args.record.endswith(".advtt.json") else os.path.splitext(args.record)[0]
        fmts = FORMATS if args.export == "all" else tuple(f.strip() for f in args.export.split(",") if f.strip())
        # Transcript formats need the segments: --stt if given, else the
        # <stem>_stt.json a media run leaves beside the record.
        segs = None
        stt_src = args.stt or (stem + "_stt.json" if os.path.exists(stem + "_stt.json") else None)
        if stt_src:
            segs = load_json(stt_src).get("segments") or []
        written = export_all(rec, stem, formats=fmts, out_dir=args.out_dir, title_style=args.title_style, segments=segs)
        for k, v in written.items():
            if v is None:
                sys.stderr.write("%s skipped: needs the transcript (pass --stt <stem>_stt.json)\n" % k)
        print(json.dumps(written, indent=1) if args.json else "\n".join("%-12s %s" % (k, v) for k, v in written.items() if v))
        return 0

    if args.list_providers:
        for d in available_providers():
            mark = "OK " if d.get("available") else "-- "
            print("%s%-10s %-22s %-28s %s" % (
                mark, d.get("name"), d.get("model") or "", (d.get("endpoint") or "")[:28], d.get("detail")))
        env = loaded_env_files()
        print("\nenv: %s" % (", ".join(env) if env else "no .env loaded"))
        return 0

    if args.dump_prompt:
        # Byte-identical to `adclass.py --dump-prompt` for a transcript with no
        # sibling _diar.json, given the same provider/chunk size. That IS the
        # extraction regression check.
        stt = load_json(args.dump_prompt)
        segments = stt.get("segments") or []
        prov = make_provider(args.provider, model=args.model, endpoint=args.endpoint)
        mct = args.chunk or prov.max_chunk_tokens
        plan = plan_chunks(segments, mct)
        hint = os.path.basename(args.dump_prompt).replace("_stt.json", "")
        print("=" * 78)
        print("SYSTEM PROMPT (prompt_version=%s)" % PROMPT_VERSION)
        print("=" * 78)
        print(SYSTEM_PROMPT)
        print("=" * 78)
        print("PLAN: %d segments -> %d chunk(s) at max_chunk_tokens=%d" % (len(segments), len(plan), mct))
        print("=" * 78)
        for i, ch in enumerate(plan):
            print("--- chunk %d: window [%d,%d) est_tokens=%d ---" % (i, ch["start"], ch["end"], ch["est_tokens"]))
            print(build_user_prompt(segments, ch["start"], ch["end"], episode_hint=hint))
            print()
        print("=" * 78)
        print("RESPONSE SCHEMA")
        print(json.dumps(response_schema(), indent=2))
        return 0

    if args.eval:
        prov = _provider_from_args(args) if args.classify else None
        ins_dir = args.inserted_dir
        if ins_dir is None and os.path.isdir(os.path.join("tests", "fixtures", "truth-drafts")):
            ins_dir = os.path.join("tests", "fixtures", "truth-drafts")
        rows = evaluate(args.eval, provider=prov, out_dir=args.out_dir, force=args.force,
                        timeout=args.timeout, max_chunk_tokens=args.chunk, inserted_dir=ins_dir)
        return 0 if rows else 1

    # ---- classification of one input -------------------------------------
    segments, stt_meta, source, media_path = None, {}, {}, None
    if args.stt:
        doc = load_json(args.stt)
        segments = doc.get("segments") or []
        stt_meta = {k: doc.get(k) for k in ("provider", "model", "timing", "has_words") if k in doc}
        stt_meta["segment_count"] = len(segments)
        source = {"path": os.path.abspath(args.stt), "format": "stt-json"}
        stem = _stem_for(args.stt)
        media_path = args.media_for_captions
    elif args.captions:
        doc = read_captions(args.captions)
        segments = doc["segments"]
        stt_meta = {"provider": "captions", "timing": doc["timing"], "has_words": False,
                    "segment_count": len(segments)}
        source = doc["source"]
        stem = _stem_for(args.captions)
        media_path = args.media_for_captions
    elif args.media:
        media_path = args.media
        stem = _stem_for(args.media)
        segments, stt_meta = _transcribe(args.media, args)
        source = {"path": os.path.abspath(args.media), "format": "media"}
        stt_path, written = _write_transcript(stem, args.out_dir, segments, stt_meta, args.media, args.force)
        source["transcript"] = os.path.abspath(stt_path)
        sys.stderr.write("transcript %s -> %s\n" % ("written" if written else "kept (exists; --force to overwrite)", stt_path))
    else:
        ap.print_help()
        return 1

    rec_path, ana_path = _out_paths(stem, args.out_dir)
    if args.dry_run:
        prov = make_provider(args.provider, model=args.model, endpoint=args.endpoint)
        mct = args.chunk or prov.max_chunk_tokens
        plan = plan_chunks(segments, mct)
        est_in = sum(len(build_user_prompt(segments, c["start"], c["end"], episode_hint=os.path.basename(stem))) // 4 + len(_SP) // 4 for c in plan)
        est_out = 400 * len(plan)
        out = {"input": source, "segments": len(segments), "duration_sec": max((s.get("end") or 0) for s in segments) if segments else 0,
               "provider": prov.name, "model": prov.model, "max_chunk_tokens": mct, "chunks": len(plan),
               "windows": [[c["start"], c["end"]] for c in plan],
               "estimated_prompt_tokens": est_in, "estimated_output_tokens": est_out,
               "estimated_cost_usd_api_rates": estimate_cost_usd(prov.model, est_in, est_out),
               "prompt_version": PROMPT_VERSION, "outputs": [rec_path, ana_path], "would_call_network": bool(getattr(prov, "cloud", False))}
        print(json.dumps(out, indent=1))
        return 0
    if os.path.exists(rec_path) and not args.force:
        sys.stderr.write("%s exists; pass --force to overwrite\n" % rec_path)
        return 3

    log = EventLog(args.log_json)
    log.emit("run.start", argv=sys.argv[1:], prompt_version=PROMPT_VERSION, version=__version__)
    log.emit("input.loaded", source=source, segments=len(segments), stt=stt_meta)
    try:
        prov = _provider_from_args(args)
    except ProviderError as e:
        sys.stderr.write("%s\n" % e)
        log.emit("error", stage="provider", error=str(e))
        return 4
    if args.log_json:
        prov = LoggingProvider(prov, log)
    ok, msg = prov.ensure_ready()
    sys.stderr.write("provider %s: %s\n" % (prov.name, msg))
    if not ok:
        log.emit("error", stage="provider", error=msg)
        return 4
    hint = os.path.basename(stem)
    res = classify_segments(segments, prov, episode_hint=hint, max_fraction=args.max_fraction,
                            timeout=args.timeout, max_chunk_tokens=args.chunk, verbose=True,
                            source_sha256=source_sha256(segments))

    media = media_fingerprint(media_path) if media_path and os.path.exists(media_path) else {}
    record = build_record(res, media=media, stt=stt_meta, source=source)
    problems = validate_record(record)
    if problems:
        sys.stderr.write("record validation: %s\n" % "; ".join(problems))
    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
    write_json(rec_path, record)
    write_json(ana_path, build_analysis(res, record))
    log.emit("gate", status=res.get("status"), spans=len(record["spans"]), stats=res.get("stats"),
             incomplete_chunks=res.get("incomplete_chunks"), rejections=len(res.get("rejections") or []))
    log.emit("output.written", record=rec_path, analysis=ana_path, validation_problems=problems)
    exported = {}
    if args.export:
        fmts = FORMATS if args.export == "all" else tuple(f.strip() for f in args.export.split(",") if f.strip())
        exported = export_all(record, stem, formats=fmts, out_dir=args.out_dir, title_style=args.title_style,
                              segments=segments)
        log.emit("output.exported", files=exported)
    log.emit("run.done", status=res.get("status"), processing_time_sec=res.get("processing_time_sec"),
             cost_usd=sum(float(c.get("cost_usd") or 0.0) for c in res.get("chunks") or []))
    log.close()

    if args.json:
        print(json.dumps(record, ensure_ascii=False, indent=1))
    else:
        print("%s -> %s" % (os.path.basename(stem), rec_path))
        print("  status           %s" % res.get("status"))
        print("  provider/model   %s / %s" % (res.get("provider"), res.get("model")))
        print("  segments         %d over %.1fs" % (res.get("segment_count", 0), res.get("duration_sec", 0.0)))
        print("  processing       %.1fs" % res.get("processing_time_sec", 0.0))
        st = res.get("stats") or {}
        print("  ad spans         %d  (%d segments, %.1fs, %.1f%% of episode)" % (
            st.get("ad_spans", 0), st.get("ad_segments", 0), st.get("ad_seconds", 0.0),
            100 * st.get("ad_fraction", 0.0)))
        print("  uncertain segs   %d" % st.get("uncertain_segments", 0))
        for sp in record.get("spans") or []:
            print("    %-8s %8.1f-%8.1fs %-9s %-6s conf=%.2f %-9s" % (
                sp["id"], sp["start"], sp["end"], sp["category"], sp["action"],
                float(sp.get("confidence") or 0.0), sp.get("state")))
        rj = res.get("rejections") or []
        if rj:
            print("  rejections (%d):" % len(rj))
            for r in rj[:12]:
                print("    chunk %-3s %s" % (r.get("chunk"), (r.get("reason") or "")[:110]))
        cost = sum(float(c.get("cost_usd") or 0.0) for c in res.get("chunks") or [])
        if cost:
            print("  cost             $%.4f" % cost)
        for k, v in exported.items():
            print("  exported %-8s %s" % (k, v))
    return 0 if res.get("status") == STATUS_OK else 2


if __name__ == "__main__":
    sys.exit(main())
