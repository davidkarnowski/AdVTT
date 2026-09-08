"""Exporters: the canonical advtt/1.0 record rendered into the formats that
players and tools act on today (Research/08 §4.2, ranked by evidence):

    edl          Kodi EDL, `start end 3` (action 3 = commercial break, auto-skipped)
    ffmeta       ffmetadata chapters for mpv `--chapters-file` and ffmpeg embedding
    chapters     Podcasting 2.0 JSON Chapters 1.2 with an `advtt` extension object
    sponsorblock SponsorBlock-shaped JSON for mpv_sponsorblock local mode and clients
    vtt          hardened WebVTT `kind=metadata` track (two-line payload, header-line version)
    srt          the visible SRT twin (`[Ad] Acme`), a second subtitle track on purpose
    audacity     Audacity label track `start\\tend\\tlabel` for labelling and review
    rttm         NIST RTTM for pyannote-style scoring

Every exporter is a pure function record -> text; nothing here touches audio.
`export_all` writes `<stem>.<ext>` files and returns their paths. Rules learned
the hard way and applied here: chapters get a synthesised 00:00 first chapter
and at least three entries or Apple/YouTube ignore them; ad chapters are
visible (`toc: true`), because hiding them is the opposite of skippable; SRT
cues start at 1 and never end on a bare number; WebVTT NOTE blocks are
optional, preceded by a blank line, and carry nothing a machine needs.
"""

import json
import os

FORMATS = ("edl", "ffmeta", "chapters", "sponsorblock", "vtt", "srt", "audacity", "rttm",
           "captions-vtt", "captions-srt")
EXT = {"edl": ".edl", "ffmeta": ".ffmeta", "chapters": ".chapters.json", "sponsorblock": ".sponsorblock.json",
       "vtt": ".ads.vtt", "srt": ".ads.srt", "audacity": ".labels.txt", "rttm": ".rttm",
       "captions-vtt": ".captions.vtt", "captions-srt": ".captions.srt"}

# Formats that render the whole transcript need the segments, which the
# shareable record deliberately does not carry (transcript text stays local).
NEEDS_TRANSCRIPT = {"captions-vtt", "captions-srt"}

# Which record spans an exporter emits. Skip-oriented formats carry only spans
# whose action is `skip`; descriptive formats carry every span.
SKIP_ONLY = {"edl", "sponsorblock"}


def _spans(record, skip_only=False):
    out = []
    for sp in record.get("spans") or []:
        if skip_only and sp.get("action") != "skip":
            continue
        out.append(sp)
    return sorted(out, key=lambda s: (s["start"], s["end"]))


def _title(sp, style="advtt"):
    name = ((sp.get("advertiser") or {}).get("name") or "").strip()
    cat = sp.get("category", "sponsor")
    if style == "sponsorblock":
        return "[SponsorBlock]: %s" % {"sponsor": "Sponsor", "selfpromo": "Unpaid/Self Promotion",
                                       "interaction": "Interaction Reminder", "intro": "Intermission/Intro Animation",
                                       "outro": "Endcards/Credits", "preview": "Preview/Recap"}.get(cat, cat.title())
    label = {"sponsor": "Ad", "selfpromo": "Promo", "crosspromo": "Cross-promo", "intro": "Intro",
             "outro": "Outro", "preview": "Preview", "interaction": "Reminder", "program": "Program"}.get(cat, cat)
    return "[%s] %s" % (label, name) if name else "[%s]" % label


def _duration(record):
    return float((record.get("media") or {}).get("duration_sec") or record.get("duration_sec") or 0.0)


def _fmt_ts(sec, sep="."):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d%s%03d" % (h, m, s, sep, ms)


# --------------------------------------------------------------------------

def to_edl(record):
    """Kodi EDL: one line per skippable span, action 3 (commercial break)."""
    lines = ["%.3f\t%.3f\t3" % (sp["start"], sp["end"]) for sp in _spans(record, skip_only=True)]
    return "\n".join(lines) + ("\n" if lines else "")


def _chapter_list(record, title_style="advtt"):
    """Alternating program/ad chapters covering the whole file, first at 0."""
    dur = _duration(record)
    spans = _spans(record)
    chapters = []
    t = 0.0
    n_prog = 1
    for sp in spans:
        if sp["start"] > t + 0.5:
            chapters.append({"start": t, "end": sp["start"], "title": "Part %d" % n_prog, "ad": None})
            n_prog += 1
        chapters.append({"start": sp["start"], "end": sp["end"], "title": _title(sp, title_style), "ad": sp})
        t = sp["end"]
    if dur and dur > t + 0.5:
        chapters.append({"start": t, "end": dur, "title": "Part %d" % n_prog, "ad": None})
    if not chapters or chapters[0]["start"] > 0:
        chapters.insert(0, {"start": 0.0, "end": chapters[0]["start"] if chapters else dur, "title": "Start", "ad": None})
    # Apple and YouTube ignore chapter sets with fewer than three entries.
    while len(chapters) < 3 and dur:
        last = chapters[-1]
        mid = (last["start"] + last["end"]) / 2
        chapters[-1] = dict(last, end=mid)
        chapters.append({"start": mid, "end": last["end"], "title": "Part %d" % (n_prog + len(chapters) - 1), "ad": None})
    return chapters


def to_ffmeta(record, title_style="advtt"):
    """ffmetadata chapters (mpv --chapters-file; ffmpeg -i x -i y.ffmeta -map_metadata 1 -codec copy)."""
    out = [";FFMETADATA1"]
    for ch in _chapter_list(record, title_style):
        out += ["", "[CHAPTER]", "TIMEBASE=1/1000",
                "START=%d" % int(round(ch["start"] * 1000)),
                "END=%d" % int(round(ch["end"] * 1000)),
                "title=%s" % ch["title"].replace("\\", "\\\\").replace("=", "\\=").replace(";", "\\;").replace("#", "\\#")]
    return "\n".join(out) + "\n"


def to_json_chapters(record, title_style="advtt"):
    """Podcasting 2.0 JSON Chapters 1.2; ad chapters visible and titled, with an `advtt` extension."""
    chapters = []
    for ch in _chapter_list(record, title_style):
        c = {"startTime": round(ch["start"], 3), "title": ch["title"], "toc": True}
        if ch["ad"] is not None:
            sp = ch["ad"]
            c["endTime"] = round(ch["end"], 3)
            c["advtt"] = {"id": sp["id"], "category": sp["category"], "form": sp.get("form"),
                          "action": sp.get("action"), "confidence": sp.get("confidence"),
                          "profile": record.get("profile")}
        chapters.append(c)
    return json.dumps({"version": "1.2.0", "chapters": chapters}, indent=1) + "\n"


def to_sponsorblock(record):
    """SponsorBlock-shaped segments (mpv_sponsorblock local mode, Invidious/NewPipe-style clients)."""
    dur = _duration(record)
    fp = ((record.get("media") or {}).get("sha256") or "")[:12]
    out = []
    for sp in _spans(record, skip_only=True):
        out.append({"segment": [round(sp["start"], 3), round(sp["end"], 3)],
                    "category": sp["category"], "actionType": "skip",
                    "videoDuration": round(dur, 3) if dur else None,
                    "UUID": "advtt-%s-%s" % (fp, sp["id"]),
                    "locked": 0, "votes": 0, "description": (sp.get("advertiser") or {}).get("name") or ""})
    return json.dumps(out, indent=1) + "\n"


def to_webvtt(record, note=True):
    """Hardened WebVTT metadata track: version on the header line, per-cue `v`
    and media fingerprint, two-line payload (token, then one-line JSON),
    optional NOTE after a blank line, never containing `-->`."""
    fp = ((record.get("media") or {}).get("sha256") or "")[:16]
    lines = ["WEBVTT - advtt/1.0", ""]
    if note:
        lines += ["NOTE", "AdVTT advertising disclosure track. Consumers read cue.text, not HTML.",
                  "Line 1 of each cue is the category token; line 2 is a JSON object.", ""]
    for i, sp in enumerate(_spans(record), 1):
        payload = {"v": "advtt/1.0", "id": sp["id"], "media": fp, "category": sp["category"],
                   "form": sp.get("form"), "position": sp.get("position"), "action": sp.get("action"),
                   "state": sp.get("state"), "confidence": sp.get("confidence")}
        adv = (sp.get("advertiser") or {}).get("name")
        if adv:
            payload["advertiser"] = adv
        js = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        js = js.replace("-->", "--\\u003e").replace("<", "\\u003c").replace("&", "\\u0026")
        lines += ["%s" % sp["id"], "%s --> %s" % (_fmt_ts(sp["start"]), _fmt_ts(sp["end"])),
                  sp["category"].upper(), js, ""]
    return "\n".join(lines)


def to_srt_twin(record):
    """Visible SRT twin: a second subtitle track showing `[Ad] Acme` during ads."""
    lines = []
    for i, sp in enumerate(_spans(record), 1):
        text = _title(sp)
        if text.strip().isdigit():
            text = text + " ."
        lines += [str(i), "%s --> %s" % (_fmt_ts(sp["start"], ","), _fmt_ts(sp["end"], ",")), text, ""]
    return "\n".join(lines) + ("\n" if lines else "")


def to_audacity(record):
    return "".join("%.3f\t%.3f\t%s\n" % (sp["start"], sp["end"], _title(sp)) for sp in _spans(record))


def to_rttm(record, file_id=None):
    """NIST RTTM: SPEAKER <file> 1 <start> <dur> <NA> <NA> <label> <NA> <NA>."""
    fid = file_id or os.path.splitext(os.path.basename((record.get("media") or {}).get("path") or "media"))[0]
    return "".join("SPEAKER %s 1 %.3f %.3f <NA> <NA> %s <NA> <NA>\n"
                   % (fid, sp["start"], sp["end"] - sp["start"], sp["category"]) for sp in _spans(record))


def _caption_cues(record, segments):
    """Full-transcript cues with ad pieces marked.

    Every transcript segment becomes a cue. Where a span edge falls inside a
    segment and the segment has word timings, the segment is cut at that edge
    (a word belongs to the side its start time is on), so the caption marks
    exactly the words the record marks. Without word timings a segment is
    marked when at least half of it lies inside a span. Spans in state `ad`
    are marked with the span title (`[Ad] Acme`), spans in state `uncertain`
    with `[Ad?]`, so a viewer sees the classifier's doubt rather than a
    silent skip (design pillar 1). Returns [(start, end, text, span_or_None)].
    """
    spans = [sp for sp in _spans(record) if sp.get("state") in ("ad", "uncertain")]

    def span_at(t):
        for sp in spans:
            if sp["start"] <= t < sp["end"]:
                return sp
        return None

    cues = []
    for seg in segments or []:
        st, en = float(seg.get("start") or 0.0), float(seg.get("end") or 0.0)
        text = (seg.get("text") or "").strip()
        if en <= st or not text:
            continue
        words = seg.get("words") or []
        cuts = sorted({e for sp in spans for e in (sp["start"], sp["end"]) if st < e < en})
        if cuts and words:
            edges = [st] + cuts + [en]
            for a, b in zip(edges, edges[1:]):
                ws = [w for w in words if a <= float(w.get("s") or a) < b]
                if not ws:
                    continue
                cs = max(a, float(ws[0].get("s") or a))
                ce = min(b, max(float(w.get("e") or cs) for w in ws))
                cues.append((cs, max(ce, cs + 0.001), " ".join(w.get("w", "") for w in ws).strip(), span_at((cs + ce) / 2)))
        else:
            inside = sum(max(0.0, min(en, sp["end"]) - max(st, sp["start"])) for sp in spans)
            sp = span_at((st + en) / 2) if inside >= 0.5 * (en - st) else None
            if sp is None and inside >= 0.5 * (en - st):
                sp = max(spans, key=lambda x: max(0.0, min(en, x["end"]) - max(st, x["start"])))
            cues.append((st, en, text, sp))
    return cues


def _caption_text(text, sp):
    if sp is None:
        return text
    if sp.get("state") == "uncertain":
        return "[Ad?] " + text
    return "%s %s" % (_title(sp), text)


def to_captions_vtt(record, segments=None):
    """Full-transcript WebVTT subtitle track with ad pieces marked inline
    (`[Ad] Acme ...`) and wrapped in `<c.advtt-ad>` so browsers can style them
    via `::cue(.advtt-ad)`; ffmpeg-based players drop the tag and keep the
    text. Needs the transcript segments."""
    if segments is None:
        raise ValueError("captions-vtt needs the transcript segments (pass --stt or run from media)")
    lines = ["WEBVTT - advtt/1.0 captions", "",
             "NOTE", "Full transcript. Cues inside an advertising span are prefixed [Ad] (or [Ad?] when uncertain)",
             "and carry the class advtt-ad. The machine-readable disclosure track is the .ads.vtt twin.", "",
             "STYLE", "::cue(.advtt-ad) { color: #ffd166; font-style: italic; }", ""]
    n = 0
    for cs, ce, text, sp in _caption_cues(record, segments):
        n += 1
        body = _caption_text(text, sp).replace("-->", "-- >").replace("<", "\u003c") if sp is None else \
            "<c.advtt-ad>%s</c>" % _caption_text(text, sp).replace("-->", "-- >").replace("<", "\u003c")
        ident = "%s.%d" % (sp["id"], n) if sp else "seg.%d" % n
        lines += [ident, "%s --> %s" % (_fmt_ts(cs), _fmt_ts(ce)), body, ""]
    return "\n".join(lines)


def to_captions_srt(record, segments=None):
    """Full-transcript SRT with ad pieces prefixed `[Ad] Acme` / `[Ad?]`.
    Needs the transcript segments."""
    if segments is None:
        raise ValueError("captions-srt needs the transcript segments (pass --stt or run from media)")
    lines = []
    for i, (cs, ce, text, sp) in enumerate(_caption_cues(record, segments), 1):
        lines += [str(i), "%s --> %s" % (_fmt_ts(cs, ","), _fmt_ts(ce, ",")), _caption_text(text, sp), ""]
    return "\n".join(lines) + ("\n" if lines else "")


RENDER = {
    "edl": to_edl, "ffmeta": to_ffmeta, "chapters": to_json_chapters, "sponsorblock": to_sponsorblock,
    "vtt": to_webvtt, "srt": to_srt_twin, "audacity": to_audacity, "rttm": to_rttm,
    "captions-vtt": to_captions_vtt, "captions-srt": to_captions_srt,
}


def render(record, fmt, **kw):
    if fmt not in RENDER:
        raise ValueError("unknown export format %r (choose from %s)" % (fmt, ", ".join(FORMATS)))
    return RENDER[fmt](record, **kw)


def export_all(record, stem, formats=FORMATS, out_dir=None, title_style="advtt", segments=None):
    """Write one file per format beside `stem` (or in out_dir). Returns
    {fmt: path}; a transcript format requested without `segments` maps to
    None (skipped) rather than raising, so `--export all` on a bare record
    still writes everything else."""
    base = os.path.basename(stem)
    d = out_dir or os.path.dirname(os.path.abspath(stem))
    os.makedirs(d, exist_ok=True)
    written = {}
    for fmt in formats:
        if fmt in NEEDS_TRANSCRIPT and segments is None:
            written[fmt] = None
            continue
        kw = {"title_style": title_style} if fmt in ("ffmeta", "chapters") else {}
        if fmt in NEEDS_TRANSCRIPT:
            kw["segments"] = segments
        text = render(record, fmt, **kw)
        path = os.path.join(d, base + EXT[fmt])
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        written[fmt] = path
    return written


# --------------------------------------------------------------------------
# Readers for round-trip tests (WebVTT and EDL are the lossless-ish ones)

def read_webvtt(text):
    """Parse the hardened WebVTT track back into span dicts (from the JSON line)."""
    spans = []
    blocks = [b for b in text.replace("\r\n", "\n").split("\n\n") if b.strip()]
    for b in blocks:
        lines = b.split("\n")
        ti = next((i for i, ln in enumerate(lines) if "-->" in ln), None)
        if ti is None or lines[0].startswith("WEBVTT") or lines[0].startswith("NOTE"):
            continue
        payload = lines[ti + 1:]
        if len(payload) >= 2:
            try:
                d = json.loads(payload[1])
            except ValueError:
                continue
            left, right = lines[ti].split("-->")
            d["start"] = _parse_ts(left)
            d["end"] = _parse_ts(right.strip().split(" ")[0])
            d["token"] = payload[0]
            spans.append(d)
    return spans


def _parse_ts(s):
    s = s.strip().replace(",", ".")
    parts = s.split(":")
    parts = [float(p) for p in parts]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return round(parts[0] * 3600 + parts[1] * 60 + parts[2], 3)


def read_edl(text):
    out = []
    for ln in text.splitlines():
        p = ln.split()
        if len(p) >= 3:
            out.append({"start": float(p[0]), "end": float(p[1]), "action": int(p[2])})
    return out
