# 02 — The AdVTT WebVTT profile (advtt/0.1)

Builds directly on `media-events-webvtt-advertising-analysis.md`. Sections cited
as §n refer to that document. Where this profile narrows or contradicts it, the
divergence is flagged **[divergence]** with a reason.

## 0. Scope

This profile defines two distinct WebVTT artefacts:

1. **The media-events track** — `kind="metadata"`, one cue per event, no captions.
   This is the interchange layer of §23.
2. **The amended caption track** — an ordinary caption file whose cues are
   untouched and whose ad markings live in `NOTE` blocks.

They are separate files. A single file cannot be both a caption track and a
metadata track, because `kind` is a property of the `<track>` element, not of the
file, and a player told `kind="captions"` will render whatever the payload says.

## 1. Payload: resolving Option A vs Option B (§11)

**Decision: both, layered. Line 1 is the vocabulary token; line 2 is a
single-line JSON object.**

```vtt
ad-001
00:12:31.200 --> 00:12:59.800
ADVERTISEMENT
{"v":"advtt/0.1","type":"ADVERTISEMENT","id":"ad-001","confidence":0.98,"state":"ad","kind":"midroll","skippable":true,"label":"Acme Corporation"}
```

### Why not Option A alone

§11 lists "needs a formal grammar" and "nesting becomes awkward" as the costs, and
both bite immediately rather than eventually. The profile has to carry, on day
one: an entities array (§12 — detection and identification are separate
assertions with separate confidences), a nested `edges` object (§14 — separate
start/end boundary confidence), and provenance (§13). A key/value line format
that supports those is a new grammar with quoting, escaping and array rules, and
writing that grammar is strictly more work than `json.dumps` for strictly less
capability. Sponsor names contain commas, quotes and non-ASCII; escaping is not a
hypothetical.

### Why not Option B alone

JSON alone throws away the property §10 identifies as the whole point: graceful
degradation. A person opening the file, a `grep`, a chapter-track renderer, or a
consumer that only reads the first payload line all see `{"v":"advtt/0.1",...` —
technically parseable, practically opaque. §9's minimal form (a bare
`ADVERTISEMENT`) is the thing that makes the file self-evident, and it costs one
line to keep.

### Why the layering is free

WebVTT cue payloads are multi-line by definition; a cue ends at a blank line. Both
lines are `cue.text` in the browser, separated by `\n`. A parser reads:

```js
const [token, ...rest] = cue.text.split("\n");
const data = rest.length ? JSON.parse(rest.join("\n")) : {type: token};
```

The token is normative and MUST equal `data.type` when both are present; a
mismatch is a hard parse error, not a merge. Redundancy that can disagree is a
bug source, so the rule is: on disagreement, reject the cue and record it.

**[divergence]** §11 concludes "for an initial experimental implementation, JSON
is probably the most practical" and §36's example shows JSON only. This profile
keeps the JSON as normative and adds the token line back. The reason is that
§9/§10's degradation argument and §11's JSON argument are both right and are not
in conflict — the notes treated them as an either/or because they were considering
one payload line.

## 2. File shape

```vtt
WEBVTT
NOTE ADVTT/0.1
{ ...header JSON... }

<blank line>
<cue>
<blank line>
<cue>
```

The header is a `NOTE` block whose first line is the version sentinel
`ADVTT/0.1` and whose remaining lines are one JSON object (pretty-printed is fine;
NOTE blocks may span lines and end at a blank line). Putting the header in a NOTE
rather than in a cue means it has no timing, cannot be mistaken for an event, and
is discarded by every conforming parser.

Header fields:

| Field | Req | Meaning |
|---|---|---|
| `profile` | yes | `"advtt/0.1"` |
| `media_id` | no | opaque identifier for the asset |
| `media_duration_sec` | rec | lets a consumer sanity-check that the track belongs to the media |
| `generated` | yes | ISO-8601 UTC |
| `stt` | rec | `{provider, model, timing, has_words}` |
| `classifier` | yes | `{provider, model, prompt_version, chunk_tokens}` |
| `status` | yes | `ok` \| `rejected_overlabel` \| `rejected_degenerate` \| `failed` \| `no_transcript` |
| `source_sha256` | rec | hash over the segments the analysis was made from |
| `thresholds` | rec | `{ad, uncertain}` — a consumer must not assume 0.75/0.40 |
| `stats` | no | `{ad_spans, ad_seconds, ad_fraction}` |
| `analysis` | no | relative path to the full `analysis.json` |

**A non-`ok` status means the file contains no event cues.** This is the asymmetry
expressed in the format: a rejected episode produces *no* marking, never partial
marking. A consumer that finds `status != "ok"` and cues anyway should treat the
file as corrupt.

## 3. Cue syntax

```text
<identifier>            required; stable within the file; e.g. ad-001
<start> --> <end>       standard WebVTT timing, milliseconds
<TOKEN>                 vocabulary token, uppercase
<json>                  single line, optional but recommended
```

No cue settings (`align`, `line`, …) are used or permitted; they are meaningless
on a metadata track and would only invite a renderer to do something.

### Escaping rules that are not optional

WebVTT cue text is not JSON-transparent. Three characters must be escaped inside
the JSON payload using `\uXXXX`, so that the raw text and any markup-parsed
reading of the text agree:

| In the payload | Write it as | Why |
|---|---|---|
| `-->` | `--\u003E` | a cue-text line containing `-->` is read as a timing line |
| `<` | `\u003C` | begins a WebVTT cue span; `getCueAsHTML()` would eat it |
| `&` | `\u0026` | begins a WebVTT character escape (`&amp;`, `&lrm;`) |

JSON `\uXXXX` escapes are decoded by any JSON parser, so the payload survives
round-tripping while the byte stream stays inert to a WebVTT parser.

A blank line inside a payload is impossible by construction (JSON is emitted on
one line), and a payload line may not begin with the literal text of a timestamp.
`json.dumps(obj, ensure_ascii=False)` followed by those three substitutions is the
whole writer.

## 4. Vocabulary

**v0.1 is closed at four tokens:**

```text
ADVERTISEMENT     produced or read commercial message for a paying advertiser
SPONSORSHIP       acknowledgement of a sponsor; typically host-read, often
                  integrated into program speech
PROMOTION         promotion of the producer's own or affiliated content
PROGRAM           editorial content; the complement of the above
```

§8 proposes seven primary classes plus seven for later. This profile ships four.
**[divergence, deliberate]**: `STATION-ID`, `NETWORK-PROMOTION` and
`PUBLIC-SERVICE-ANNOUNCEMENT` are all distinctions the *classifier cannot
currently make reliably*, and a vocabulary term that is emitted at chance is worse
than absent — a consumer will build a filter on it. The existing classifier's
`kind` field (`preroll | midroll | postroll | house | section`) already carries the
placement distinction that most consumers actually want, and it is carried as an
attribute rather than as a type. `house` is where a station or network promo lands
today.

Extension is by a `x-` prefix (`x-POLITICAL-ADVERTISEMENT`) until a term is
promoted into a numbered profile version. A consumer MUST ignore cues whose token
it does not know rather than reinterpreting them.

## 5. The event object

```jsonc
{
  "v": "advtt/0.1",
  "type": "ADVERTISEMENT",       // required, matches the token line
  "id": "ad-001",                // required, matches the cue identifier
  "confidence": 0.98,            // required, 0..1, classification confidence
  "state": "ad",                 // required: "ad" | "uncertain" | "content"
  "skippable": true,             // required; see §6
  "kind": "midroll",             // optional: preroll|midroll|postroll|house|section
  "label": "Acme Corporation",   // optional, the advertiser/sponsor as spoken
  "label_confidence": 0.82,      // optional; separate from `confidence` per §12
  "edges": {                     // optional
    "mode": "word",              // "word" | "segment" — how the edges were derived
    "start_exact": 751.24,
    "end_exact": 779.80,
    "start_confidence": 0.93,
    "end_confidence": 0.88
  },
  "segments": [197, 246],        // optional; source segment index range, inclusive
  "entities": [                  // optional, §12/§15
    {"type": "advertiser", "name": "Acme Corporation", "confidence": 0.82}
  ],
  "note": "…"                    // optional, human-readable caveat
}
```

Everything else — evidence quotes, rejection reasons, chunk records, per-rung
check results — lives in `analysis.json`, per §22 and §23. The track stays
compact enough to read.

### Why `state` exists when `confidence` is right there

Because the consumer's branch is tri-state and the thresholds are a *producer*
decision that may change. §14 asks how uncertainty should be represented; the
operational answer from PodcastFetch is that a single number invites every
consumer to pick its own cut-off, and the one that matters (auto-skip) must not be
picked by a player author. So the producer states the verdict, publishes the
thresholds it used in the header, and keeps the number for anyone who wants to
re-derive it.

- `state: "ad"` — confidence ≥ the header's `ad` threshold (0.75 by default).
- `state: "uncertain"` — ≥ `uncertain` (0.40). Show it; never skip it.
- `state: "content"` — never emitted as a cue; the span was demoted and is gone.

### Why `edges` is separate and has a `mode`

Word-level timings are not always available. `timing: "proportional"` transcripts
have invented timestamps; someone else's caption file has no word stream at all.
`mode: "segment"` tells the consumer the edges are cue-aligned and probably ±1
utterance, which is exactly what a player needs to know before drawing a skip
button. `mode: "word"` means the edge came from locating the evidence quote in the
word stream and is good to ~100 ms.

**The end edge is deliberately not trimmed to the evidence quote.** At the start
edge, landing late costs real content, so precision helps. At the end edge, the
final segment is already inside the span — the model judged the whole utterance to
be advertisement — so trimming removes coverage that was granted, and the observed
failure is an audible ad tail. This is inherited behaviour and is intentional.

## 6. `skippable`, and why it is a field rather than a computation

A player should not have to know the policy. `skippable` is `true` only when
`state == "ad"` **and** `confidence >= thresholds.ad` **and** the episode passed
its gates. It is `false` on every `uncertain` cue, always.

The asymmetry restated as a format rule: **a consumer may skip only cues with
`skippable: true`, and even then only if the user has opted in.** The prototype
player ships with auto-skip off.

## 7. Provenance and versioning (§13, §31)

Provenance is per-file, in the header, not per-cue: every cue in a file came from
one analysis run. Per-cue provenance would be pure duplication until human review
exists, at which point a reviewed cue gains:

```json
"provenance": {"method": "human-review", "by": "dk", "at": "2026-09-02T10:00:00Z"}
```

and its `confidence` becomes 1.0. A file mixing methods keeps `"method":"mixed"`
in the header.

Competing analyses are files, not cues (§31):

```text
episode-112.media-events.vtt              current
episode-112.media-events.v1.vtt           superseded
episode-112.media-events.reviewed.vtt     human
```

Version numbering: `profile` is `advtt/MAJOR.MINOR`. A minor bump may add optional
fields and `x-` tokens. A major bump may change required fields or token meanings.
A consumer MUST refuse a major version it does not know, and MAY read a higher
minor version by ignoring unknown fields.

`prompt_version` in the header is the classifier's cache key, not the profile
version. The two are unrelated on purpose: reclassifying with a better prompt does
not change the format.

## 8. Overlapping and nested cues (§15)

Permitted, with one rule that makes them tractable: **cues of the same `type` MUST
NOT overlap.** Two `ADVERTISEMENT` cues that overlap are a merge failure, not a
nesting. Different types may overlap freely — an `ADVERTISEMENT` containing an
entity cue, or a `PROGRAM` cue overlapping a `SPONSORSHIP` where a host slid a
sponsor mention into an answer.

Consumers computing "is time *t* inside an ad" take the union of `ADVERTISEMENT`
and `SPONSORSHIP` cues with `skippable: true`. That operation is well-defined
under the no-same-type-overlap rule.

## 9. `PROGRAM` cues

Optional, off by default, `--emit program` turns them on. They are the complement
of the marked intervals and carry `"derived": true`. They exist because §8 lists
`PROGRAM` in the vocabulary and because a timeline renderer sometimes wants an
explicit partition, but a file of two ad cues is smaller and says the same thing.

## 10. The amended caption track

Full example: `examples/episode-112.captions.vtt`.

Rules:

1. Caption cue identifiers, timings and text are **byte-identical** to the source.
2. All AdVTT information lives in `NOTE ADVTT …` blocks. Conforming parsers
   discard NOTE blocks entirely, so rendering is unchanged in every player.
3. A header `NOTE ADVTT/0.1 amended` block records the source file, its hash, and
   the companion events track.
4. Each ad boundary emits a paired `NOTE ADVTT enter <id>` before the first cue of
   the span and `NOTE ADVTT exit <id>` after the last.
5. A boundary cue that straddles an edge carries a `split` object naming the cue
   identifier and the exact time — advisory, since the caption cue itself is not
   modified.
6. Removing every `NOTE ADVTT` block restores the source file exactly. That is the
   test.

Note what this costs: a player reading only the caption track and not the events
track sees nothing. NOTE blocks are invisible to the `TextTrack` API too — the
browser does not expose them. So the amended caption file is for tools and humans;
players get the events track. That is the honest trade, and it is the same trade
SRT forces, only with a better hiding place.

## 11. Loading it in a page

```html
<audio controls src="episode-112.mp3">
  <track kind="metadata" src="episode-112.media-events.vtt" label="Ad markings" default>
</audio>
```

`kind="metadata"` cues are never rendered. Exposure is uniform enough in current
Chromium, Firefox and WebKit to read `track.cues` after `loadedmetadata`, but §25's
caveat stands: support for *kinds* of text track is not identical everywhere, and
`mode` must be set to `"hidden"` (not `"disabled"`) or the cues list stays empty.
The prototype player therefore also accepts a fetched/dragged `.vtt` and parses it
itself — one parser, two delivery paths, no dependence on the element.

## 12. Validation rules for a conforming file

A validator must check, in this order:

1. First line is `WEBVTT`; a `NOTE ADVTT/<version>` header exists and parses.
2. `status == "ok"` iff event cues are present.
3. Every cue has an identifier, unique in the file.
4. Every payload's first line is a known token (or `x-`-prefixed).
5. `data.type == token`, `data.id == cue identifier` when JSON is present.
6. `state` is consistent with `confidence` and the header thresholds.
7. `skippable` is false wherever `state != "ad"`.
8. No two cues of the same type overlap.
9. Every cue lies within `[0, media_duration_sec]` when the header declares one.
10. Total marked seconds ≤ `MAX_AD_FRACTION` of the declared duration — the same
    over-label gate the classifier applies, re-applied at read time, because a
    hand-edited file is not validated by anything else.
