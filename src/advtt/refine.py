"""Word-precise edge refinement. The END edge is deliberately not trimmed to the
evidence quote; read the comment inside refine_span_edges before changing it.
"""
# Moved verbatim from PodcastFetch adclass.py (commit 74692de, 2026-09-06),
# lines 2780-2870. Do not edit the moved bodies without bumping PROMPT_VERSION
# where the prompt or ladder behaviour changes; see Research/01 and 12.
from .validate import normalize_quote


def _word_index_of(words, phrase, from_end=False):
    """Index of the word where `phrase` begins within `words`, or None.

    Compares progressively looser forms, because an ASR word stream and a model
    quoting it disagree in predictable ways: Whisper emits "last-minute" as two
    tokens, spells URLs as "h-e-l-p dot com", and punctuates unevenly.
    """
    toks = [normalize_quote(w.get("w") or "") for w in words]
    toks = [t for t in toks]
    target = normalize_quote(phrase).split()
    if not target or not toks:
        return None

    n = len(target)
    rng = range(len(toks) - n, -1, -1) if from_end else range(len(toks) - n + 1)
    for i in rng:
        if toks[i:i + n] == target:
            return i

    # Whitespace-blind: "lastminute" vs "last minute".
    joined = "".join(toks)
    flat = "".join(target)
    if flat and flat in joined:
        run = 0
        for i, t in enumerate(toks):
            if joined[run:run + len(flat)] == flat:
                return i
            run += len(t)

    # Loosest: anchor on the first distinctive token.
    for i, t in enumerate(toks):
        if t and t == target[0]:
            return i
    return None


def refine_span_edges(segments, spans):
    """Place ad edges at word precision and mark segments that straddle one.

    Segment-level labelling has to take or leave a whole utterance. When a
    boundary utterance is half conversation and half sponsor read, that forces a
    choice between hearing the ad's opening words or losing real speech. Word
    timings remove the choice: the edge lands mid-utterance and the segment is
    split into a content half and an ad half.

    Adds to each span:
        start_exact / end_exact   seconds, word-precise where derivable
        splits                    [{index, at, ad_side}] for segments to divide

    A split is only emitted when the evidence quote is actually located inside
    the segment and does not start at its first word (or end at its last), i.e.
    only when the segment genuinely straddles the boundary.
    """
    for sp in spans:
        si, ei = sp["start_index"], sp["end_index"]
        sp["start_exact"] = sp["start"]
        sp["end_exact"] = sp["end"]
        splits = []

        first = segments[si] if 0 <= si < len(segments) else None
        words = (first or {}).get("words") or []
        if words and sp.get("evidence"):
            k = _word_index_of(words, sp["evidence"])
            if k is not None and k > 0:
                at = float(words[k].get("s") or sp["start"])
                if sp["start"] < at < float(first.get("end") or at):
                    sp["start_exact"] = round(at, 2)
                    splits.append({"index": si, "at": round(at, 2), "ad_side": "after"})

        # The END edge is deliberately NOT trimmed to the evidence quote.
        #
        # end_evidence is a representative phrase, not necessarily the ad's final
        # words, so trimming to it cuts the advertisement short and the listener
        # hears its tail. Measured: Blitzy's span quoted "...schedule a demo and
        # start building" while the segment continued "with Blitzy today", and
        # Vox's quote stopped before "That's Vox.com slash members" -- both left
        # audible ad on the content side of the boundary.
        #
        # The asymmetry also inverts at this edge. At the START, landing late
        # costs content, so precision helps. At the END, the final segment is
        # already INSIDE the span -- the model judged the whole utterance to be
        # advertisement -- so trimming it removes coverage we were given, while
        # keeping it costs at most a fraction of a second of speech the model
        # already called an ad.
        sp["end_exact"] = sp["end"]

        if splits:
            sp["splits"] = splits
    return spans
