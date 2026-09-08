# AdVTT — project brief

Date: 2026-09-02. One page covering the whole project. Detail lives in
`08-recommendation-and-trajectory.md`; evidence in `07-research-log.md` and
`research-log/`.

## What AdVTT is

AdVTT is a command-line tool and Python library that takes a finished audio file
(podcast episodes first, video later), transcribes it, decides which passages
are advertising or sponsorship, and writes that judgement out as **time-based
metadata**: start and end times, category, confidence, advertiser, and full
provenance. It never cuts the audio. Players, downloaders and archives decide
what to do with the marks.

It is being split out of PodcastFetch, a private offline podcast downloader,
where the classifier already exists and has been tuned against hand-labelled
episodes. PodcastFetch will re-consume AdVTT as a dependency. The public
release stands on its own for anyone holding a media file.

## Why it exists

Podcast advertising is mostly host-read: the same voice, no jingle, a slide
from journalism into a sales pitch mid-breath. Nothing acoustic marks it, so
detection has to be semantic, over a transcript. The tool exists because
listeners want to know where the ads are, archives want a record of them, and
nobody publishes a portable, typed, confidence-bearing description of ad timing
for arbitrary files. Every open-source predecessor detects and then cuts audio
into a private feed. AdVTT's product is the record itself.

## The governing principle

Silently skipping journalism is far worse than failing to skip an ad. Every
default follows from this asymmetry: auto-skip off, conservative thresholds, a
rejected episode produces no marks rather than partial marks, a boundary
segment that is half content is excluded, and the ship gate is measured in
content seconds falsely marked as ad (at most five per episode).

## What already works

A proven classifier in PodcastFetch: transcripts are cut into tiled windows of
about 6,000 tokens with read-only context either side; an LLM returns spans
with a verbatim evidence quote; an eight-rung validation ladder checks parsing,
index range, span duration, merging, quote verbatimness, question density (ads
are monologues), an episode-level over-label gate, and treats an empty answer
as valid. Word-level timestamps refine the edges. Ninety-nine archive episodes
are classified; four hand-labelled fixtures pass the gate.

## What the research spike found

Ten research tracks, about 670 cited sources, run on 1–2 September 2026.

- Real players skip on **chapters** (ID3, MP4, Podcasting 2.0 JSON) and **EDL**
  files (Kodi, mpv, Jellyfin). No surveyed player reads a WebVTT metadata
  track. WebVTT remains a valid, parser-safe interchange file, but its NOTE
  header is dropped by most tools.
- Two segment vocabularies are already deployed in consumers (SponsorBlock and
  Jellyfin). Inventing a third would isolate the output.
- Asking a model for line indices fails on long inputs; verbatim quotes
  resolved in code succeed. Chunking is independently justified by long-context
  research.
- Reasoning on versus off is contested in the literature; agreement between two
  passes is the robust signal, and it costs under a cent per episode on cheap
  models.
- Dynamic ad insertion carries about 92% of US podcast ad revenue, yet host
  reads are still about 46% of spend. Loudness steps and silence gaps find
  splices; audio fingerprints find repeated produced spots; transcripts find
  host reads. All three channels are needed.
- No public benchmark with time-aligned podcast ad labels exists. Four fixtures
  cannot support a public accuracy claim; sixty held-out episodes can.
- US case law (Fox v. Dish) approved an ad-skip design with markers in a
  separate file, off by default, media untouched. The podcast community has
  rejected ad-range tags and ad-blocker framing. Annotation-only, local-only,
  disclosure framing is the defensible posture.

## The recommendation

1. **One canonical JSON record per file**, bound to the exact rendition by
   duration and hash, with category (SponsorBlock-compatible), form (host-read,
   produced, sponsorship credit), position, delivery, a separate playback
   `action`, calibrated confidence, advertiser and edge-error estimates.
2. **Exporters ranked by what works today**: Kodi EDL, ffmetadata chapters for
   mpv, embedded ID3/MP4/Matroska chapters, Podcasting 2.0 JSON chapters,
   SponsorBlock-shaped JSON, a hardened WebVTT metadata track for the web
   player, and a visible SRT twin. Inline SRT marking is dropped.
3. **Pipeline changes**: quote-anchored spans; a reasoning-on and reasoning-off
   intersection ensemble; confidence from agreement; Parakeet or Whisper
   locally with word timestamps; a forced-aligner edge pass targeting 100 ms;
   loudness and silence corroboration; a per-show fingerprint index for
   repeated creatives; differential download as an opt-in in the fetcher.
4. **Evaluation**: the four fixtures become the dev set; a held-out test set of
   at least sixty episodes from ten shows with no-ad controls; two-level
   metrics with confidence intervals clustered by show; a recorded-response
   replay store for offline CI and a weekly drift canary; a public labels-only
   benchmark, PodAd-Bench.
5. **Release**: Apache-2.0; transcripts and evidence quotes never leave the
   machine; text-and-data-mining opt-outs honoured; funding and value tags
   surfaced beside any skip affordance; framed as time-resolved advertising
   disclosure.
6. **Packaging**: Hatchling, zero hard dependencies, extras for MLX and
   Parakeet, plugin providers, a key store, and an `--offline` mode that
   refuses network providers.

## Trajectory

Phase 0 settles naming, licence and vocabulary and runs five cheap experiments
(quote anchoring, ensemble, no-ad controls, Apple chapter rendering, Kodi EDL on
audio). Phase 1 extracts the core into `advtt` with byte-identical regression
against PodcastFetch. Phase 2 builds the exporters and reference player. Phase
3 builds the test set and publishes the benchmark. Phase 4 adds edge precision
and the acoustic channel. Phase 5 has PodcastFetch re-consume AdVTT and serve
chapters over its private RSS. Phase 6 distils a small local proposer model and
publishes the profile specification. Each phase has an exit criterion, not a
date.
