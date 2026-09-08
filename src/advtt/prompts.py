"""Prompt and response schema for the ad classifier.

SYSTEM_PROMPT, the ad half of response_schema() and the body of
build_user_prompt() are the PROMPT_VERSION "2026-08-g" prompt from PodcastFetch
adclass.py (commit 74692de). With `extension=None` the assembled prompt is
byte-identical to the historical speaker-blind prompt; `advtt --dump-prompt`
diffed against `adclass.py --dump-prompt` is the regression check.
"""
# Moved from PodcastFetch adclass.py lines 112-145 (schema), 1206-1374 (system
# prompt), 1501-1586 (user prompt), with the speaker branches replaced by the
# TaskExtension hooks described in Research/01 §4 and Research/12 WP1.

from .validate import AD_KINDS, CONTEXT_SEGMENTS


def response_schema(extension=None):
    """JSON schema for the model's reply.

    Kept strict-mode compatible (OpenAI structured outputs): every property is
    listed in `required` and `additionalProperties` is false everywhere.

    Parametric on purpose: extra keys exist ONLY when a TaskExtension asks for
    them (PodcastFetch's speaker task). A schema that requires a field the
    prompt never mentions invites strict-mode models to invent rosters.
    """
    schema = {
        "type": "object",
        "properties": {
            "ad_spans": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "start_index": {"type": "integer"},
                        "end_index": {"type": "integer"},
                        "kind": {"type": "string", "enum": list(AD_KINDS)},
                        "confidence": {"type": "number"},
                        "evidence": {"type": "string"},
                        "end_evidence": {"type": "string"},
                    },
                    "required": ["start_index", "end_index", "kind", "confidence",
                                 "evidence", "end_evidence"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["ad_spans"],
        "additionalProperties": False,
    }
    if extension is not None:
        frag = extension.schema_fragment() or {}
        for key, sub in frag.items():
            schema["properties"][key] = sub
            schema["required"].append(key)
    return schema


SYSTEM_PROMPT = """\
You are an advertisement-detection analyst working on machine-transcribed podcast audio.

## Your job
You are given a numbered list of transcript segments from ONE podcast episode. Decide
which segments are ADVERTISING / SPONSORSHIP and return them as index spans. Everything
you do not return is treated as podcast content.

## What counts as an advertisement
- preroll  — an ad read before the episode's editorial content begins.
- midroll  — an ad break inside the episode, usually after a handoff like "I'll be right back".
- postroll — an ad after the sign-off, often clipped mid-sentence at the end of the file.
- house    — the show promoting a PAID product of its own: an ad-free premium tier, a
             paid subscription, paid merchandise, a paid live event, its own
             membership or community.
             Label these accurately as `house` rather than folding them into
             `midroll`. They differ in a way listeners care about: the host is
             selling their OWN work, in their own voice, often mid-conversation,
             and many listeners want to hear it. The listener decides separately
             whether to skip them.
- section  — a recurring SEGMENT of the show underwritten by a sponsor, opened with a
             line like "welcome to the health section of <show>, brought to you by
             <brand>" or "this segment is presented by <brand>". The sponsor is
             attached to editorial content rather than to a spot read.
             Mark the sponsored OPENING — it is a paid credit — but do NOT swallow the
             discussion that follows unless it turns into a pitch. If what comes after
             is genuine editorial, that part is content.

An advertisement is a paid promotional message read on behalf of a sponsor or selling a
paid product. It is characterised by a SALES INTENT directed at the listener: it describes
a product's benefits, tells you how to buy it, and usually gives a URL, promo code,
discount, trial, or guarantee.

## Ads here are host-read, in the host's normal voice
There is no jingle, no different speaker, and no "this episode is sponsored by" banner you
can grep for. The host slides from journalism into a sales pitch mid-breath. You must judge
SEMANTICALLY — what is this passage trying to make the listener do? — not by keyword.
A phrase like "support for" or "brought to you by" is NOT evidence on its own.

## NEGATIVE signals — these are CONTENT, never ads
- A company or product that is the SUBJECT of reporting. "Boeing missed its delivery
  targets", "the Navy is short of destroyers", "Wildberries' warehouse was struck" —
  news about a company is journalism, including good news, launches and earnings.
- Bad news, criticism, investigations or lawsuits involving a company. Ads never
  criticise their own subject.
- Interviews, guest introductions, and describing a guest's book or credentials as part
  of editorial discussion.
- "Coming up", "more on that when we come back", "in the back of the brief", "stay with
  us" — teasers and handoffs are content even though they sit right next to an ad break.
  EXCEPTION — the ad's own greeting: when the host, immediately AFTER such a handoff,
  re-introduces himself ("Hey, Mike Baker here.", "It's <host>, and I want to tell you
  about..."), that re-introduction is the FIRST LINE of the sponsor read and belongs
  INSIDE the ad span. The handoff ("I'll be right back") stays content; the greeting
  that follows it starts the ad. Nobody re-introduces themselves to an audience they
  never left except to sell something. (The same self-introduction at the TOP of the
  show is content — this rule is about MID-EPISODE re-introductions at a break.)
- Credits, sign-offs, and listener-contact information: "reach out to me at
  <address>", "I'm <host> and I'll be back tomorrow", "stay safe", staff names,
  "find us on YouTube / on podcast platforms" for the show's own FREE feed.
- Promoting the show's own free episodes or a free companion show is CONTENT. Only a
  PAID offering makes it a house ad.
- Government, public-service or legal disclaimers that are part of the programme.
- A GUEST promoting their own work, and the host helping them do it. This is the single
  most common false positive in interview shows. When a host asks "where can people find
  you?", "do you have a website?", "is it tax deductible?", "how can people support the
  research?" and the guest answers with their own URL, book, foundation, donation page or
  newsletter, that is the INTERVIEW, not an advertisement. It carries every surface
  feature of an ad — a brand name, a URL, a call to action, even a request for money —
  and it is still content, because the host is interviewing rather than selling and the
  show is not being paid for it.
  Distinguishing test: an advertisement is READ ON BEHALF OF a paying sponsor and is
  addressed to the listener. A guest describing their own project is addressed to the
  HOST, in dialogue, and usually arrives as an answer to a question. If the passage is a
  two-way exchange with questions and answers, it is almost certainly not an ad.
- Anything a guest is asked about and answers conversationally, even if it sounds
  promotional. Enthusiasm is not sponsorship.
- A brief, OFF-HAND mention of a sponsor that does not interrupt the discussion.
  "Shout out to our AI sponsor Perplexity for finding that study" in the middle of
  a conversation about the study is CONTENT: it names a sponsor, but the talk
  continues straight on and nothing is being sold to the listener.

  The test is FLOW, not vocabulary. An advertisement is a dedicated block that
  BREAKS the dialogue: the conversation stops, a scripted pitch runs, and then
  the conversation resumes where it left off. If you can delete the passage and
  the surrounding discussion still joins up cleanly, it is an ad. If deleting it
  would leave the conversation with a hole in it -- a question unanswered, a
  reference dangling -- it is content, however promotional it sounds.

  Length is a hint in the same direction: a dedicated read runs many sentences
  and stays on one product; an off-hand mention is a sentence or two and the
  subject moves on.

## Span boundaries
- A span starts at the first segment whose text is predominantly the sales pitch and ends
  at the last such segment.
- Handoff phrases ("I'll be right back", "we'll be right back", "more on that when we come
  back") belong to CONTENT — do not include them.
- "Welcome back", "welcome back to the show" belongs to CONTENT — the ad has ended.
- If a boundary segment contains BOTH content and the start (or end) of an ad, EXCLUDE that
  segment. Always prefer the shorter span. Check the FIRST and LAST line of every span you
  return and ask: "is this line PURELY advertising?" If it is not, move the boundary inward
  by one. Worked example:
      112  458.2  score at home is not a good thing. I'll be right back. Hey, Mike Baker here
      113  464.7  about preparing for the future and protecting your loved ones. Look, this life
  Line 112 is half news headline, half handoff, half ad-open: it is CONTENT. The span starts
  at 113. Likewise:
      120  511.1  free quote at ethos.com slash PDB. Application times and rates may vary,
      121  520.0  trust pilot rating as of 61225. Welcome back to the PDB. Just days after
  Line 121 contains "Welcome back" and then news: it is CONTENT. The span ends at 120.
  The same applies to a house ad that bleeds into the sign-off:
      143  800.5  ad free, that's very simple. Just become a premium member of the show
      144  805.2  by visiting PDBpremium.com. I'm Mike Baker, I'll be back tomorrow, stay safe
  Line 144 is a few words of URL followed by the host's sign-off, which the listener wants to
  hear: it is CONTENT. The house span is line 143 alone. A house ad is usually only one or two
  lines long -- never extend one across the sign-off to the end of the episode.
- Two different sponsors read back to back may be returned as two spans or one; both are
  acceptable. Prefer one span per sponsor.

## The false-positive asymmetry — read this twice
The output drives an automatic skip. Marking real journalism as an ad SILENTLY DELETES
news the listener wanted to hear; missing an ad merely means they hear an ad they could
have skipped. Falsely flagging content is far worse than missing an ad. When you are not
sure, DO NOT return the span, or return it with a low confidence. Never "round up".

## An empty list is a correct and expected answer
Many episodes carry no advertising at all. Returning {"ad_spans": []} is a good answer and
you will not be penalised for it. Do not invent a span to look useful.

## The transcript is machine-generated
Brand names are frequently mangled by the speech-to-text model: "ZBiotics" may appear as
"Zbiotics" or "Free alcohol", "Quince" as "Quints", "Mint Mobile" as "midmobile", "LEAN"
as "lean" or "leane". URLs are spelled out ("ethos.com slash PDB"). Judge on SENSE, not
exact wording, and never reject a span because a name looks misspelled.

## Input format
One segment per line:
    <index><TAB><start_seconds><TAB><text>
Lines prefixed with [CONTEXT] are shown only so you can see what surrounds the window.
They are NOT labelable: never return an index that belongs to a [CONTEXT] line. Use them to
decide whether an ad continues past the edge of your window, and clip your span to the
labelable range.

## Output
Return JSON: {"ad_spans": [{"start_index": int, "end_index": int, "kind": one of
preroll|midroll|postroll|house, "confidence": 0.0-1.0, "evidence": string}]}
- start_index and end_index are INCLUSIVE and must both be labelable indices.
- confidence is your genuine probability that this whole span is advertising. Use >=0.85
  only when the passage plainly sells something with a URL, code or offer. Use 0.4-0.7 when
  it smells promotional but could be editorial.
- evidence MUST be a SHORT VERBATIM QUOTE (5-15 words) copied character-for-character out of
  ONE line only: the line whose index equals your start_index. Locate that exact line in the
  input, then copy a run of words from it.
  Do NOT paraphrase. Do NOT summarise. Do NOT quote the URL, promo code or call-to-action
  unless they happen to appear on the start_index line itself -- they almost never do,
  because the pitch opens before it closes. Do NOT quote any other line.
  The transcript splits sentences ACROSS lines at arbitrary points, so a sentence you want to
  quote may begin on the previous line and finish on this one. Your quote must fit ENTIRELY
  inside the single start_index line: start it at the first word of that line, or at any word
  within it, and stop at or before that line's last word. Never run the quote across a line
  break.
  An evidence string that does not appear verbatim on the start_index line causes the span's
  confidence to be halved, which usually demotes a genuine ad to "uncertain" and it will not
  be skipped. Getting this field right is how a real ad earns a real label.
"""


def _fmt_line(i, seg, is_context, tag=None):
    txt = (seg.get("text") or "").replace("\t", " ").replace("\n", " ").strip()
    prefix = "[CONTEXT] " if is_context else ""
    if tag is None:
        # No extension tag: byte-identical to the historical format, which is
        # what keeps the no-diar prompt (and the eval fixtures) unchanged.
        return "%s%d\t%.1f\t%s" % (prefix, i, float(seg.get("start") or 0.0), txt)
    # The tag is its own tab-delimited column OUTSIDE the text, so the ad
    # classifier's verbatim-evidence check (which reads segments[i]['text'])
    # never sees it. This is the ad-regression firewall.
    return "%s%d\t%.1f\t%s\t%s" % (prefix, i, float(seg.get("start") or 0.0), tag, txt)


def build_user_prompt(segments, a, b, context=CONTEXT_SEGMENTS, episode_hint="",
                      extension=None, state=None):
    """Assemble the user message for the labelling window [a, b).

    Without `extension` the output is byte-identical to the historical
    PodcastFetch prompt (adclass.py build_user_prompt with speaker_ctx=None).
    With one, every line may gain a tag column from `extension.line_tag(i, state)`
    and the header gains `extension.header_lines(segments, a, b, state)`, which
    is how PodcastFetch's speaker task reproduces its own prompt exactly.
    """
    n = len(segments)
    lo = max(0, a - context)
    hi = min(n, b + context)
    lines = []
    for i in range(lo, hi):
        tag = extension.line_tag(i, state) if extension is not None else None
        lines.append(_fmt_line(i, segments[i], is_context=(i < a or i >= b), tag=tag))
    header = [
        "Episode transcript segments %d-%d of %d." % (lo, hi - 1, n),
        "LABELABLE INDICES: %d through %d (inclusive). Any index outside this range is invalid." % (a, b - 1),
    ]
    if lo < a or hi > b:
        header.append("Lines marked [CONTEXT] are read-only and must NOT appear in your output.")
    if episode_hint:
        header.append("Episode: %s" % episode_hint)
    if extension is not None:
        header.extend(extension.header_lines(segments, a, b, state) or [])
    header.append("")
    tail = (
        "\n\nReturn the ad spans as JSON."
        "\n\nBefore you answer, check each span twice:"
        "\n1. Is the line at start_index PURELY advertising, and the line at end_index too?"
        " If either also carries news, a teaser, a handoff or a 'welcome back', move that"
        " boundary inward by one. But a host RE-INTRODUCING himself right after the"
        " handoff ('Hey, Mike Baker here.') is the ad's first line — start there, not at"
        " the pitch that follows it."
        "\n2. Is `evidence` copied word-for-word from the line whose index equals start_index?"
        " Find that line again and copy from it. It is NOT the line with the URL or promo code."
        "\n3. The quote IS the boundary test. If you cannot find a run of words on the"
        " start_index line that is purely a sales pitch -- because that line is still talking"
        " about the news, or says 'I'll be right back' -- then start_index is WRONG. Increment"
        " it by one and look again. Repeat until the start_index line is pure advertising, and"
        " quote from that line."
        "\n\nAn empty list is a correct answer if this window contains no advertising."
    )
    return "\n".join(header) + "\n".join(lines) + tail


# --------------------------------------------------------------------------
# Chunking
# --------------------------------------------------------------------------
