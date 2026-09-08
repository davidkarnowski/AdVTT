"""Read existing caption files (.vtt / .srt) into classifier segments.

Cues become segments [{start, end, text}]. There are no word timings, so the
classifier can place edges only at cue boundaries (`edges.mode: segment`), and
following the false-positive asymmetry a boundary cue that is half content is
left out of the ad span rather than split. The source file is never modified.
"""

import os
import re

_TS_RE = re.compile(r"(\d+):(\d\d):(\d\d)[.,](\d{1,3})|(\d\d):(\d\d)[.,](\d{1,3})")
_TAG_RE = re.compile(r"<[^>]+>")
_ARROW = "-->"


def _parse_ts(s):
    s = s.strip()
    m = _TS_RE.match(s)
    if not m:
        raise ValueError("bad timestamp %r" % s)
    if m.group(1) is not None:
        h, mi, se, ms = m.group(1), m.group(2), m.group(3), m.group(4)
    else:
        h, mi, se, ms = "0", m.group(5), m.group(6), m.group(7)
    return int(h) * 3600 + int(mi) * 60 + int(se) + int(ms.ljust(3, "0")) / 1000.0


def _clean(text):
    text = _TAG_RE.sub("", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def read_captions(path):
    """Return {"segments": [...], "timing": "model", "has_words": False, "source": {...}}."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        raw = f.read()
    kind = "vtt" if raw.lstrip().startswith("WEBVTT") or path.lower().endswith(".vtt") else "srt"
    blocks = re.split(r"\r?\n\r?\n+", raw.strip())
    segments = []
    for blk in blocks:
        lines = [ln for ln in blk.split("\n")]
        if kind == "vtt" and lines and (lines[0].startswith("WEBVTT") or lines[0].startswith("NOTE")
                                        or lines[0].startswith("STYLE") or lines[0].startswith("REGION")):
            continue
        ti = next((i for i, ln in enumerate(lines) if _ARROW in ln), None)
        if ti is None:
            continue
        left, right = lines[ti].split(_ARROW, 1)
        right = right.strip().split(" ")[0]   # drop cue settings
        try:
            start, end = _parse_ts(left), _parse_ts(right)
        except ValueError:
            continue
        text = _clean(" ".join(lines[ti + 1:]))
        if not text:
            continue
        segments.append({"start": round(start, 3), "end": round(end, 3), "text": text})
    segments.sort(key=lambda s: (s["start"], s["end"]))
    return {
        "segments": segments,
        "timing": "model",
        "has_words": False,
        "source": {"path": os.path.abspath(path), "format": kind, "cues": len(segments)},
    }
