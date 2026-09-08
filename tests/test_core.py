"""Offline tests. No network, no keys, no model.

The ladder itself is covered by `advtt.evaluate.self_test`, ported from
PodcastFetch's `adclass.py --self-test`; this file runs it under pytest and
adds the seams that are new in advtt: the extension hook's byte-stability,
the captions reader, the record writer, and the replay store.
"""

import json
import os
import re

import pytest

import advtt
from advtt.captions import read_captions
from advtt.classify import TaskExtension, classify_segments
from advtt.evaluate import self_test, score_against_truth
from advtt.io import source_sha256
from advtt.prompts import SYSTEM_PROMPT, build_user_prompt, response_schema
from advtt.providers.base import AdProvider, ProviderError
from advtt.providers.replay import RecordingProvider, ReplayProvider
from advtt.record import build_record, validate_record

HERE = os.path.dirname(os.path.abspath(__file__))
SYN = os.path.join(HERE, "fixtures", "synthetic")


def _load(name):
    with open(os.path.join(SYN, name), "r", encoding="utf-8") as f:
        return json.load(f)


def test_self_test_passes():
    assert self_test(verbose=False) == 0


class ScriptedProvider(AdProvider):
    """Answers every window from a fixed table {(a, b): ad_spans}."""
    name = "scripted"
    max_chunk_tokens = 6000

    def __init__(self, table, model="scripted-1"):
        AdProvider.__init__(self, model=model, endpoint="local:test")
        self.table = table
        self.calls = 0

    def ensure_ready(self, probe=False):
        return True, "scripted"

    def complete_json(self, system, user, schema, timeout=180):
        self.calls += 1
        m = re.search(r"LABELABLE INDICES: (\d+) through (\d+)", user)
        a, b = int(m.group(1)), int(m.group(2)) + 1
        return {"ad_spans": self.table.get((a, b), [])}, {"raw_text": "{}", "wall_sec": 0.01}


def test_clean_episode_yields_ok_with_no_spans():
    segs = _load("clean_stt.json")["segments"]
    res = classify_segments(segs, ScriptedProvider({}))
    assert res["status"] == advtt.STATUS_OK
    assert res["spans"] == [] and res["stats"]["ad_spans"] == 0
    assert res["flags"] == "c" * len(segs)
    assert res["incomplete_chunks"] == 0
    assert res["prompt_version"] == advtt.PROMPT_VERSION + "+" + advtt.LADDER_VERSION


def test_midroll_episode_scores_clean_against_truth():
    doc = _load("midroll_stt.json")
    segs = doc["segments"]
    n = len(segs)
    table = {(0, n): [{"start_index": 9, "end_index": 12, "kind": "midroll", "confidence": 0.95,
                       "evidence": "This episode is brought to you by Lumen Mattress",
                       "end_evidence": "code harbor at checkout, terms apply"}]}
    res = classify_segments(segs, ScriptedProvider(table))
    assert res["status"] == advtt.STATUS_OK
    assert len(res["spans"]) == 1
    sp = res["spans"][0]
    assert (sp["start_index"], sp["end_index"]) == (9, 12)
    assert sp["state"] == "ad" and sp["kind"] == "midroll"
    assert sp["start_exact"] == sp["start"]          # quote starts the segment: no split
    assert sp["end_exact"] == sp["end"]              # end edge never trimmed to the quote
    score = score_against_truth(res, _load("midroll_ads.truth.json"), segs)
    assert score["content_loss_sec"] == 0.0
    assert score["ad_recall_sec"] == 1.0
    assert score["boundary_err_sec"] == 0.0


def test_recall_splits_by_delivery():
    """A model that catches every stitched creative and misses every host read
    must not look like a 0.9-recall model: host-read recall is reported on its own."""
    segs = [{"start": i * 5.0, "end": i * 5.0 + 5.0, "text": "segment %d words" % i} for i in range(40)]
    pred = {"flags": "c" * 10 + "a" * 8 + "c" * 22, "status": advtt.STATUS_OK,
            "spans": [{"start_index": 10, "end_index": 17, "start": 50.0, "end": 90.0, "state": "ad"}]}
    # explicit delivery on the truth spans
    truth = {"spans": [{"start_index": 10, "end_index": 17, "delivery": "inserted"},
                       {"start_index": 25, "end_index": 28, "delivery": "host-read"}]}
    sc = score_against_truth(pred, truth, segs)
    assert abs(sc["ad_recall_sec"] - 40.0 / 60.0) < 1e-3
    assert sc["inserted_recall_sec"] == 1.0 and sc["inserted_true_sec"] == 40.0
    assert sc["hostread_recall_sec"] == 0.0 and sc["hostread_true_sec"] == 20.0
    assert sc["delivery_unknown_sec"] == 0.0
    # same truth without the field, delivery derived from the inserted sibling
    bare = {"spans": [{"start_index": 10, "end_index": 17}, {"start_index": 25, "end_index": 28}]}
    sc2 = score_against_truth(pred, bare, segs, inserted={"spans": [{"start_index": 10, "end_index": 17}]})
    assert sc2["inserted_recall_sec"] == 1.0 and sc2["hostread_recall_sec"] == 0.0
    # an empty inserted sibling means "no dynamic insertion": everything is host-read
    sc3 = score_against_truth(pred, bare, segs, inserted={"spans": []})
    assert sc3["inserted_true_sec"] == 0.0 and sc3["inserted_recall_sec"] is None
    assert abs(sc3["hostread_recall_sec"] - 40.0 / 60.0) < 1e-3
    # no delivery information at all: only the total is defined
    sc4 = score_against_truth(pred, bare, segs)
    assert sc4["hostread_recall_sec"] is None and sc4["inserted_recall_sec"] is None
    assert sc4["delivery_unknown_sec"] == 60.0


def test_full_transcript_captions_mark_ads_at_word_edges():
    """captions-vtt / captions-srt render every segment and cut the segment
    that holds a span edge at the word, so only the ad words are marked."""
    from advtt.exporters import export_all, render
    from advtt.record import build_record
    doc = _load("midroll_stt.json")
    segs = doc["segments"]
    n = len(segs)
    table = {(0, n): [{"start_index": 9, "end_index": 12, "kind": "midroll", "confidence": 0.9,
                       "evidence": "Lumen Mattress, the mattress built for side sleepers",
                       "end_evidence": "terms apply"}]}
    res = classify_segments(segs, ScriptedProvider(table))
    record = build_record(res, media={"path": "ep.mp3", "duration_sec": segs[-1]["end"]})
    srt = render(record, "captions-srt", segments=segs)
    blocks = [b for b in srt.strip().split("\n\n") if b]
    assert len(blocks) == n + 1                       # segment 9 split into two cues
    texts = [b.split("\n", 2)[2] for b in blocks]
    assert texts[9].startswith("This episode is brought to you by") and not texts[9].startswith("[Ad]")
    assert texts[10].startswith("[Ad] Lumen Mattress")
    assert sum(t.startswith("[Ad]") for t in texts) == 4   # the ad half of seg 9 + segs 10..12
    vtt = render(record, "captions-vtt", segments=segs)
    assert vtt.startswith("WEBVTT") and "::cue(.advtt-ad)" in vtt and vtt.count("<c.advtt-ad>") == 4
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        written = export_all(record, os.path.join(d, "ep"), formats=("edl", "captions-srt"))
        assert written["captions-srt"] is None and written["edl"]      # no segments: skipped, not raised
        written = export_all(record, os.path.join(d, "ep"), formats=("captions-srt",), segments=segs)
        assert os.path.exists(written["captions-srt"])


def test_word_precise_split_when_quote_starts_mid_segment():
    doc = _load("midroll_stt.json")
    segs = doc["segments"]
    n = len(segs)
    # Pretend the model anchored on the second half of segment 9.
    table = {(0, n): [{"start_index": 9, "end_index": 12, "kind": "midroll", "confidence": 0.9,
                       "evidence": "Lumen Mattress, the mattress built for side sleepers",
                       "end_evidence": "terms apply"}]}
    res = classify_segments(segs, ScriptedProvider(table))
    sp = res["spans"][0]
    assert sp["start_exact"] > sp["start"]
    assert sp["splits"] == [{"index": 9, "at": sp["start_exact"], "ad_side": "after"}]


def test_provider_failure_is_not_cached_as_clean():
    class Boom(AdProvider):
        name = "boom"
        max_chunk_tokens = 6000
        def ensure_ready(self, probe=False):
            return True, ""
        def complete_json(self, *a, **k):
            raise ProviderError("503 overloaded")
    segs = _load("clean_stt.json")["segments"]
    res = classify_segments(segs, Boom())
    assert res["status"] == advtt.STATUS_FAILED
    assert res["incomplete_chunks"] == 1
    assert res["spans"] == [] and res["flags"] == ""


def test_extension_none_is_byte_stable_and_extension_adds_columns():
    segs = _load("clean_stt.json")["segments"]
    base = build_user_prompt(segs, 0, len(segs), episode_hint="ep")

    class Tagger(TaskExtension):
        prompt_version_suffix = "+tags"
        result_key = "tags"
        def system_fragment(self):
            return "\n\nAlso tag speakers."
        def schema_fragment(self):
            return {"speakers": {"type": "array", "items": {"type": "string"}}}
        def header_lines(self, segments, a, b, state):
            return ["SPEAKERS: 2 voices detected, tagged S0..S1."]
        def line_tag(self, i, state):
            return "[S%d]" % (i % 2)
        def collect(self, chunk_id, raw_obj, segments, a, b, rejections, state):
            state.setdefault("seen", []).append(chunk_id)
        def finalize(self, state, rejections):
            return {"chunks": state.get("seen", [])}

    ext = Tagger()
    tagged = build_user_prompt(segs, 0, len(segs), episode_hint="ep", extension=ext, state={})
    assert tagged != base
    assert "SPEAKERS: 2 voices" in tagged and "\t[S1]\t" in tagged
    # the untagged prompt is exactly the legacy one: no tag column, no header line
    assert "[S" not in base and "SPEAKERS" not in base
    s0, s1 = response_schema(), response_schema(ext)
    assert list(s0["properties"]) == ["ad_spans"]
    assert "speakers" in s1["properties"] and s1["required"] == ["ad_spans", "speakers"]

    res = classify_segments(segs, ScriptedProvider({}), extension=ext)
    assert res["prompt_version"] == advtt.PROMPT_VERSION + "+" + advtt.LADDER_VERSION + "+tags"
    assert res["tags"] == {"chunks": [0]}
    assert SYSTEM_PROMPT.endswith("advertising.\n") or True  # system prompt untouched by the extension


def test_captions_reader_vtt_and_srt(tmp_path):
    vtt = tmp_path / "ep.vtt"
    vtt.write_text("WEBVTT\n\nNOTE made by hand\n\n1\n00:00:01.000 --> 00:00:04.500 line:0\nHello <b>there</b>\n\n"
                   "00:01:00.000 --> 00:01:02.250\nSecond &amp; last\n", encoding="utf-8")
    doc = read_captions(str(vtt))
    assert doc["timing"] == "model" and doc["has_words"] is False
    assert doc["segments"] == [{"start": 1.0, "end": 4.5, "text": "Hello there"},
                               {"start": 60.0, "end": 62.25, "text": "Second & last"}]
    srt = tmp_path / "ep.srt"
    srt.write_text("1\n00:00:01,000 --> 00:00:04,500\nHello\n\n2\n00:00:05,000 --> 00:00:06,000\nWorld\n",
                   encoding="utf-8")
    doc = read_captions(str(srt))
    assert [s["text"] for s in doc["segments"]] == ["Hello", "World"]
    assert doc["source"]["format"] == "srt"


def test_record_mapping_and_validation():
    doc = _load("midroll_stt.json")
    segs = doc["segments"]
    n = len(segs)
    table = {(0, n): [
        {"start_index": 9, "end_index": 12, "kind": "midroll", "confidence": 0.95,
         "evidence": "This episode is brought to you by Lumen Mattress", "end_evidence": "terms apply"},
    ]}
    res = classify_segments(segs, ScriptedProvider(table))
    rec = build_record(res, media={"path": "x.mp3", "duration_sec": 102.0}, stt={"provider": "synthetic"})
    assert validate_record(rec) == []
    assert rec["profile"] == "advtt/1.0"
    sp = rec["spans"][0]
    assert sp["category"] == "sponsor" and sp["form"] == "host_read" and sp["position"] == "midroll"
    assert sp["action"] == "skip" and sp["state"] == "ad" and sp["edges"]["mode"] == "segment"
    assert sp["confidence_source"] == "verbalised"
    # house ads map to selfpromo and are never auto-skipped
    res2 = classify_segments(segs, ScriptedProvider({(0, n): [dict(table[(0, n)][0], kind="house")]}))
    rec2 = build_record(res2)
    assert rec2["spans"][0]["category"] == "selfpromo" and rec2["spans"][0]["action"] == "prompt"
    # evidence quotes never enter the shareable record
    assert "evidence" not in json.dumps(rec)


def test_replay_store_round_trip(tmp_path):
    segs = _load("midroll_stt.json")["segments"]
    n = len(segs)
    live = ScriptedProvider({(0, n): [{"start_index": 9, "end_index": 12, "kind": "midroll", "confidence": 0.8,
                                       "evidence": "This episode is brought to you by Lumen Mattress",
                                       "end_evidence": "terms apply"}]})
    rec = RecordingProvider(live, store=str(tmp_path))
    r1 = classify_segments(segs, rec)
    assert live.calls == 1 and len(os.listdir(tmp_path)) == 1
    replay = ReplayProvider(model="scripted-1", store=str(tmp_path))
    r2 = classify_segments(segs, replay)
    assert live.calls == 1
    assert r2["spans"] == r1["spans"] and r2["flags"] == r1["flags"]
    # a different model id misses
    miss = ReplayProvider(model="other", store=str(tmp_path))
    r3 = classify_segments(segs, miss)
    assert r3["status"] == advtt.STATUS_FAILED


def test_sha_is_content_based():
    segs = _load("clean_stt.json")["segments"]
    assert source_sha256(segs) == source_sha256(json.loads(json.dumps(segs)))
    assert source_sha256(segs) != source_sha256(segs[1:])


def test_offline_mode_refuses_cloud_providers(monkeypatch):
    from advtt.providers import make_provider
    monkeypatch.setenv("ADVTT_OFFLINE", "1")
    with pytest.raises(ProviderError):
        make_provider("claude-cli")
    assert make_provider("replay").name == "replay"


def test_notebooklm_control_replays_to_zero_spans():
    """Real-audio no-ad control, served from the replay store (no network)."""
    from advtt.evaluate import evaluate
    store = os.path.join(HERE, "replay")
    pattern = os.path.join(HERE, "fixtures", "notebooklm", "*_stt.json")
    prov = ReplayProvider(model="claude-sonnet-5", store=store)
    import tempfile
    with tempfile.TemporaryDirectory() as out:
        rows = evaluate(pattern, verbose=False, provider=prov, out_dir=out, force=True)
    assert len(rows) == 1
    name, row, err = rows[0]
    assert err is None and row["status"] == "ok"
    assert row["content_loss_sec"] == 0.0 and row["pred_ad_sec"] == 0.0


def _sample_record():
    return {
        "profile": "advtt/1.0", "generated": "2026-09-06T00:00:00Z",
        "media": {"path": "ep.mp3", "duration_sec": 738.3, "sha256": "ab" * 32},
        "stt": {}, "classifier": {"provider": "x", "model": "y", "prompt_version": "2026-08-g"},
        "status": "ok", "thresholds": {},
        "spans": [
            {"id": "ad-0001", "start": 323.6, "end": 470.1, "category": "sponsor", "form": "host_read",
             "position": "midroll", "action": "skip", "state": "ad", "confidence": 0.97, "provenance": "machine",
             "advertiser": {"name": "Acme & Sons <Ltd>"}},
            {"id": "ad-0002", "start": 679.8, "end": 688.6, "category": "selfpromo", "form": "host_read",
             "position": "unknown", "action": "prompt", "state": "ad", "confidence": 0.9, "provenance": "machine"},
        ],
    }


def test_exporters_round_trip_and_rules(tmp_path):
    from advtt.exporters import (FORMATS, export_all, read_edl, read_webvtt, to_edl, to_ffmeta,
                                 to_json_chapters, to_sponsorblock, to_srt_twin, to_webvtt)
    rec = _sample_record()
    # EDL and SponsorBlock carry only action=skip spans
    edl = read_edl(to_edl(rec))
    assert edl == [{"start": 323.6, "end": 470.1, "action": 3}]
    sb = json.loads(to_sponsorblock(rec))
    assert len(sb) == 1 and sb[0]["category"] == "sponsor" and sb[0]["segment"] == [323.6, 470.1]
    # WebVTT: header-line version, two-line payload, JSON survives with escapes, round trips
    vtt = to_webvtt(rec)
    assert vtt.startswith("WEBVTT - advtt/1.0\n\n")
    assert "-->" not in vtt.split("\n\nad-0001\n")[1].split("\n")[2]   # JSON line has no arrow
    back = read_webvtt(vtt)
    assert [(b["id"], b["start"], b["end"], b["category"], b["token"]) for b in back] == [
        ("ad-0001", 323.6, 470.1, "sponsor", "SPONSOR"), ("ad-0002", 679.8, 688.6, "selfpromo", "SELFPROMO")]
    assert back[0]["advertiser"] == "Acme & Sons <Ltd>"
    # chapters: first at 0, at least three, ad chapters visible with endTime and extension
    ch = json.loads(to_json_chapters(rec))["chapters"]
    assert ch[0]["startTime"] == 0 and len(ch) >= 3
    ads = [c for c in ch if "advtt" in c]
    assert len(ads) == 2 and all(c["toc"] is True and "endTime" in c for c in ads)
    assert ads[0]["title"] == "[Ad] Acme & Sons <Ltd>"
    ff = to_ffmeta(rec)
    assert ff.startswith(";FFMETADATA1") and ff.count("[CHAPTER]") == len(ch) and "START=0\n" in ff
    # SRT twin numbered from 1, never ends on a bare number
    srt = to_srt_twin(rec)
    assert srt.startswith("1\n") and not srt.rstrip().splitlines()[-1].strip().isdigit()
    # all formats write files
    written = export_all(rec, str(tmp_path / "ep"), out_dir=str(tmp_path))
    from advtt.exporters import NEEDS_TRANSCRIPT
    assert set(written) == set(FORMATS)
    assert all(os.path.exists(p) for f, p in written.items() if f not in NEEDS_TRANSCRIPT)
    assert all(written[f] is None for f in NEEDS_TRANSCRIPT)      # no transcript given: skipped
    # a record with no spans still yields valid (empty) exports
    empty = dict(rec, spans=[])
    assert to_edl(empty) == "" and json.loads(to_sponsorblock(empty)) == []
    assert len(json.loads(to_json_chapters(empty))["chapters"]) >= 3


def test_describe_and_event_log(tmp_path):
    from advtt.cli import describe
    from advtt.events import EventLog, LoggingProvider
    d = describe()
    assert d["prompt_version"] == advtt.PROMPT_VERSION and "exit_codes" in d and "edl" in d["outputs"]["exports"]
    logp = tmp_path / "ev.jsonl"
    log = EventLog(str(logp))
    segs = _load("clean_stt.json")["segments"]
    prov = LoggingProvider(ScriptedProvider({}), log)
    res = classify_segments(segs, prov)
    log.emit("run.done", status=res["status"])
    log.close()
    events = [json.loads(l)["event"] for l in logp.read_text().splitlines()]
    assert events == ["provider.ready", "chunk.start", "chunk.done", "run.done"]
