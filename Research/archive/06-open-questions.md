# 06 — Open questions

Decisions the user has to make, or unknowns that need an experiment. Ordered by
how much rework the wrong answer causes. Nothing here was resolved by fiat in the
other documents without saying so.

## 1. Is the standalone tool worth the coupling cost? *(blocking)*

Extraction is not free. The speaker-attribution task currently rides in the *same
model call* as ad classification, and keeping it there across a package boundary
needs the `TaskExtension` hook described in `01-` §4. That hook is the single
most invasive piece of the plan, and it exists only because PodcastFetch must not
double its API spend.

Alternatives, if the coupling is judged too expensive: keep `adclass.py` as the
implementation and make AdVTT a *thin front-end* that imports it (no extraction,
no hook, but AdVTT then depends on a podcast archive); or accept two model calls
in PodcastFetch and measure what attribution quality actually costs without the
shared context. **This needs a decision before Phase 0 starts.**

## 2. Payload: is the two-line cue acceptable? *(design, easy to change now)*

`02-` resolves §11 as token line + JSON line. The alternatives are JSON only (as
§11 and §36 lean toward) or token only (as §9 shows). The two-line form is a
small, deliberate departure and costs one line per cue. If it is unwelcome, the
fallback is JSON-only with a `"type"` field, and every tool in this repo changes
in one function.

## 3. Where does the header really belong?

Putting the profile header in a `NOTE` block makes it invisible to conforming
parsers — including the browser's `TextTrack` API, which cannot see NOTE blocks at
all (`05-` §2). A consumer using only `track.cues` therefore cannot read `status`
or `thresholds`. Options: (a) accept it, as `02-` currently does, and require a
text parse; (b) also emit a zero-length header *cue* at `00:00:00.000 -->
00:00:00.001` carrying the same JSON, duplicating it; (c) move the header into
`analysis.json` and make the VTT dumb. (b) is pragmatic and slightly ugly; it is
the most likely change to this profile.

## 4. Vocabulary: four terms or seven? *(divergence flagged in 02- §4)*

§8 proposes seven primary classes. `02-` ships four, on the grounds that the
classifier cannot reliably distinguish `STATION-ID` from `NETWORK-PROMOTION` from
`PUBLIC-SERVICE-ANNOUNCEMENT`, and an unreliable term is worse than a missing one.
If the intent is a general annotation vocabulary rather than what one classifier
can currently produce, the full §8 list should ship and the classifier should
simply never emit some of it. **Which is the file: what was measured, or what
could be measured?** That question also decides whether `TOPIC`, `PERSON` and
`LOCATION` (§16) belong in AdVTT at all or in a sibling profile.

## 5. Is the media-events track separate from the captions, always?

`02-` says yes: two files, because `kind` belongs to the `<track>` element. But a
single amended `captions.vtt` with NOTE-carried markings is *nearly* self
sufficient, and one file is easier to move around. Should AdVTT support a
"single-file mode" where the amended caption file is the only artefact and the
events track is generated on demand? It would need a NOTE-block reader in every
consumer, which is the thing the events track exists to avoid.

## 6. SRT inline: ship it at all?

`03-` recommends never defaulting to inline SRT marking but shipping it behind
`--srt-inline`. The argument against shipping it at all: every use produces a
caption file that shows text its author did not write, and someone will
redistribute one. The argument for: a personal archive with a player that can only
load one subtitle track is a real situation. **The compatibility matrix in `03-`
§3 is a hypothesis and has not been tested against real players** — it should be
before the flag ships, and the results may settle this question by themselves.

## 7. Drift detection: is three probes enough?

`04-` §8 proposes transcribing three 30-second probes and fitting offset + rate by
least squares. Untested. Failure modes to check: a caption file with a different
*edit* (ads removed from the captions but present in the audio) fits no linear
model at all and must be detected as such rather than fitted badly; and a probe
landing in music or silence gives no anchor. Should the fit be robust (median of
pairwise estimates) rather than least squares?

## 8. What is the AdVTT cache key, and where does the cache live?

PodcastFetch caches on a hash of the *segments* plus `prompt_version`, in the
sidecar itself. A standalone tool writing to `--output-dir` has no obvious home
for a cache. Options: cache inside `analysis.json` and treat its presence as the
cache (simple, matches the sidecar model); a `~/.cache/advtt` keyed by hash (works
across output directories, invisible); or no cache and rely on `--force` semantics
being inverted (always recompute unless the artefact exists). Leaning to the
first.

## 9. Confidence for boundaries: where does the number come from?

The profile carries `start_confidence` / `end_confidence` (§14), and the current
classifier does not produce them. Candidates: derive from `edges.mode` (word vs
segment) plus whether the evidence quote matched verbatim; ask the model for them
(and then validate them, since a model that returns 1.0 for a hallucinated span
will return 1.0 here too); or omit the fields until there is a way to earn them.
**Omitting is the honest default and is what the examples should show if no
derivation is agreed.**

## 10. Human review: file, overlay, or field?

§30 and §31 both want human correction to be cheap. Three shapes: edit the events
file in place and flip `provenance.method` to `human-review`; keep a separate
`.reviewed.vtt` that supersedes; or an overlay file of *diffs* against a machine
file. The third preserves what the machine said (useful for evaluation — every
correction is a labelled error, which is how `tests/fixtures/` grew) but needs a
merge step. Recommendation is the third, unresolved.

## 11. Naming

The notes (§26) recommend **Media Events WebVTT** for the profile and are explicit
that advertising should be the first application, not the whole purpose. This
project is called AdVTT, which names the application rather than the mechanism. If
the profile is ever published, the profile's name and the tool's name should
probably differ: tool `advtt`, profile `media-events/1.0`. The `advtt/0.1`
identifier in `02-` is a placeholder chosen so the two can be separated later
without a silent meaning change.

## 12. Video: does anything actually use the video?

The pipeline transcribes audio and reasons over text, for the reason PodcastFetch
gives: host-read ads have nothing acoustic (or visual) to detect. But §7 lists
visual transitions, lower-thirds and logos as boundary signals, and for broadcast
television they are the *strongest* signals. Is video input in v1 just "demux and
ignore the pictures" (currently assumed), or is there an intent to use frames? If
the latter, the provider interface needs an image channel and the whole cost model
changes.

## 13. Licence, packaging, distribution

Not addressed anywhere. Is `advtt` a pip package, a vendored directory in
PodcastFetch, or a git submodule? Does it get a licence that permits the archive
and media-monitoring uses §32 describes? Cheap to decide, annoying to change once
PodcastFetch imports it.
