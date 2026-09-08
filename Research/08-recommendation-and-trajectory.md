# 08 — Recommendation and project trajectory

Date: 2026-09-02. Evidence: `07-research-log.md` and `research-log/` (ten
tracks, ~670 sources). Citation form **[C-S61]** = track C, source 61.
Supersedes the direction set in `01-`…`06-` where the two disagree; a table of
every reversal is in §2.

## 1. Executive summary

AdVTT should ship as a **time-resolved advertising disclosure tool**: it reads a
media file, produces a canonical JSON record of advertising and sponsorship
spans, and exports that record into the formats real players already act on.
It never cuts audio. Ten findings drive everything below.

1. **The interchange problem is open; the detection problem is not.** Every
   open-source podcast ad tool of 2024–26 is Whisper → windowed LLM → ffmpeg cut
   → private RSS, and none emits a portable, typed, confidence-bearing segment
   file [A-S2, A-S4, A-S7, A-S62]. Commercial ad-intelligence vendors publish no
   accuracy figures [A-S40, A-S53]. AdVTT's differentiator is the *record*, its
   provenance, and a published benchmark, not a better cutter.
2. **Chapters are what players skip on.** mpv (`--chapters-file`, chapterskip),
   Kodi (EDL action 3), yt-dlp, Jellyfin Media Segments (`Commercial`), Apple
   Podcasts, Pocket Casts, Overcast and AntennaPod all consume chapters or EDL;
   **no surveyed player consumes a WebVTT `kind=metadata` track** [A-S56, H-S1,
   H-S4, H-S25, H-S65, H-S29]. The WebVTT track stays as the lossless
   interchange file and the HTML player's input, but it is one exporter among
   six, not the product.
3. **The two-line WebVTT payload is safe; the NOTE header is not.** Every
   fetched parser preserves multi-line payload text; NOTE blocks are dropped by
   ffmpeg, VLC, Chromium, Firefox, ExoPlayer and several libraries, and one
   podcast-app parser rejects a whole file whose first block is a NOTE
   [J-S13, J-S44, J-S61, C-S61]. Machine-relevant fields move into cues and
   the JSON record; NOTE becomes human documentation.
4. **Adopt the deployed vocabulary.** SponsorBlock's `sponsor / selfpromo /
   interaction / intro / outro / preview` and Jellyfin's `Commercial` are what
   consumers already branch on [A-S12, A-S42, H-S52]. AdVTT keeps its
   advertisement-vs-sponsorship distinction as a sub-field and separates *what
   it is* from *what to do* (`action`), as Matroska, SponsorBlock and Apple
   Interstitials all do [C-S63, C-S64, C-S33].
5. **Quote-anchored spans, not index-anchored.** Positional accuracy degrades
   with length even for trivial lookups; code-editing tools doubled accuracy by
   removing line numbers; span-grounding research and Anthropic's Citations
   feature converge on verbatim quotes resolved in code [E-S31, E-S63, E-S36,
   E-S37, B-S31, B-S32]. The project's own 800-segment misplacement is the same
   finding. Chunking stays, independently justified [E-S29, E-S30, E-S32].
6. **Replace the thinking-budget knob with an intersection ensemble.** The
   literature finds reasoning lowers recall at fixed low false-positive rates
   and recommends reasoning-on/off ensembles and token-level scores over
   verbalised confidence [E-S33, B-S38]; the project measured the opposite on a
   small model. Both are true; agreement between two passes is the robust
   signal, and it costs under $0.01 per episode on cheap tiers [E cost table].
7. **Acoustic signals are a second evidence channel, not a rival.** DAI now
   carries ~92% of US podcast ad revenue [F-S17]; loudness steps and silence
   gaps mark splices, fingerprints catch repeated produced spots (~26% of
   spend, growing fastest) [F-S49, F-S35], and host-read copy remains
   transcript-only [F-S11, F-S10]. MinusPod's fusion stance and its
   differential-download trick are the model, with a patent caveat [F-S32,
   F-S58].
8. **The evaluation is not yet credible for public claims.** Four fixtures from
   two shows, also used to tune the prompt, bound the per-episode violation
   rate at ≤75% [I-S30]; a public number needs ≥60 held-out episodes from ≥10
   shows, no-ad controls, per-show clustered confidence intervals, and a
   recorded-response replay store [I-S31, I-S42, A-S45]. No public
   time-aligned podcast-ad benchmark exists; AdVTT can publish the first
   [I, B-S50].
9. **Annotation-only, local-only is the defensible posture.** *Fox v. Dish*
   held that commercial-skipping "does not implicate Fox's copyright interest",
   describing a feature shipped off by default with markers in a separate file
   and the programme "not altered in any way" [G-S1]; the Podcast Index refused
   an ad-range tag because it "can be abused by ad blockers" [G-S40]; Pocket
   Casts and AntennaPod declined auto-skip on ecosystem grounds [G-S54, G-S64].
   Apache-2.0 code, transcripts never redistributed, TDM opt-outs honoured.
10. **Packaging follows yt-dlp and llm**: Hatchling, PEP 621, zero hard
    dependencies, extras for MLX/Parakeet/keyring, entry-point plugins for
    providers, Trusted Publishing, `uv tool install`; Homebrew core only
    [H-S6, H-S18, H-S27, H-S10, H-S75].

## 2. What changes from the preliminary design

| Preliminary (`01-`…`06-`) | New direction | Why |
|---|---|---|
| WebVTT `media-events.vtt` is the primary artefact; SRT is the hard case | Canonical **JSON record**; WebVTT is the interchange exporter; **chapters** (ID3 CHAP, MP4, JSON Chapters, ffmetadata), **EDL** and **SponsorBlock-JSON** are the delivery exporters; SRT twin retained as a minor exporter | Players skip on chapters/EDL, none on VTT metadata [A, H] |
| Vocabulary `ADVERTISEMENT / SPONSORSHIP / PROMOTION / PROGRAM` | `category` compatible with SponsorBlock/Jellyfin ids + `form` sub-field + `action` policy + `delivery` + `position` | Two vocabularies already deployed in consumers; ours would be a third [A-S42, H-S52] |
| Profile header in a `NOTE ADVTT/0.1` block | Header text on the `WEBVTT` line, `"v"` and file fingerprint in every cue, NOTE optional and preceded by a blank line | NOTE dropped by remuxers/browsers; one parser rejects files that open with NOTE [J-S61, C-S61] |
| Index-based `start_index/end_index` with an evidence quote as a check | Verbatim `start_quote/end_quote` as the anchor, resolved in code, index as a hint; unresolvable spans dropped | Index hallucination literature and the project's own measurement [E-S31, E-S63, B-S31] |
| Thinking budget left at default because budget 0 mislabels | Reasoning-on ∩ reasoning-off (or two-provider) intersection; per-model capability map | Reasoning's Razor; verbalised confidence is ordinal [E-S33, E-S39] |
| Default cloud model gpt-5.5 | Provisional: Claude Sonnet 5 or gpt-5.6-terra (quality), Gemini 3.1 Flash-Lite or gpt-5.6-luna (cheap); gpt-5.5 kept as a reference until re-evaluated with no-ad controls | 3× the price; fails MinusPod's no-ad control [E-S14, E-S16, A-S45] |
| `boundary_err_sec ≤ 3 s`, word-stream edge refinement | Two-level: 3 s detection tolerance; aligner-refined edges targeting ≤100 ms with an `edge_err_ms` estimate carried in the record | Forced aligners reach ~28–50 ms; Whisper timing sits in a 100–400 ms tail [D-S19, D-S37, D-S36] |
| STT auto order whisper-mlx → parakeet-mlx → gladia → openai | macOS: parakeet-mlx (TDT 0.6B v2/v3) first; Linux: faster-whisper large-v3-turbo with VAD; cloud: Deepgram Nova-3 / Voxtral / AssemblyAI; drop `gpt-4o-transcribe` from the seam | Word-timestamp support and price [D-S4, D-S22, D-S24] |
| 240 s max span, 35% over-label gate, tuned on 4 fixtures | Re-derive from a ≥60-episode test set; industry priors: 5–6.5 min ads/hour, spots 15–90 s, pre-roll in the first two minutes | [I impl. 8, F-S3, F-S17] |
| 4 fixtures are the eval | 4 fixtures become the dev set; build a disjoint public test set; publish PodAd-Bench | Rule of three; contamination [I-S30, I-S63] |
| No acoustic channel ("host-read ads have nothing acoustic") | Loudness-step + VAD corroboration at LLM edges; per-show fingerprint index for repeated creatives; differential download opt-in | Host-read claim stands, but DAI splices and produced spots are acoustic [F] |
| Licence, opt-outs, release posture undecided (`06-` #13) | Apache-2.0; annotation-only; local-only; TDMRep and a feed-level opt-out honoured; transcripts and evidence quotes stay local | [G] |
| Packaging undecided | Hatchling/PEP 621, zero hard deps, extras, pluggy entry points, `advtt keys`, `--offline` | [H] |

Kept unchanged, because nothing in the evidence contradicts them: the tiled
chunk planner with context margins [E-S29–S32, B-S22]; the ordered validation
ladder, including the empty-is-valid rung [0-L1]; the false-positive asymmetry
as the organising principle [G-S1 makes it a legal asset too]; the
`content_loss_sec` metric (it is a pyannote DetectionCostFunction with
fa-weight 1, miss-weight 0 [I-S9]); no silent local→cloud fallback; the
`TaskExtension` hook so PodcastFetch keeps its single model call.

## 3. Positioning and release posture

**Name the thing correctly.** Market it as time-resolved *disclosure* and
*verification* of advertising in finished media, with skipping as one
downstream use. This is not spin: the Podcast Index namespace's only live
proposal in this space is an un-timed `podcast:disclosure` [A-S57, C-S13];
ad-intelligence vendors sell "time-stamped proof" [A-S53]; and the framing that
killed prior efforts was "ad blocker" [A-S50, A-S17, A-S30].

**What the core never does.** No audio cutting, no burn-in, no shared database
of third-party episode labels at launch, no fetching from Apple/Spotify/YouTube.
Output is metadata about a file the user lawfully holds. This is the shape the
Ninth Circuit described approvingly in *Fox v. Dish* [G-S1, G-S11]; ad-blocking
litigation in Germany turns on *modifying* a program, which a sidecar does not
do [G-S13, G-S14, G-S38]; facts are not copyrightable [G-S19, G-S66]. Analysis,
not legal advice; the log records the caveats (host-owned ad copy weakens the
"we don't own the ads" limb; UK s.29A covers only non-commercial research
[G-S56]).

**Two-tier output as a privacy boundary.** The shareable record holds times,
category, confidence, advertiser, provenance and a file fingerprint. Evidence
quotes (≤15 words), transcript text and chunk records stay in the local
`analysis.json`. Transcripts never enter the public repo; fixtures ship as
enclosure URL + SHA-256 + labels + a regeneration script [G impl. 5, I impl. 7].

**Opt-outs.** Check W3C TDMRep on the enclosure host [G-S4] and propose a
feed-level `<podcast:txt purpose="tdm-reservation">` as an *opt-out* signal,
which is the inverse of the ad-range tag the namespace rejected [G-S70, G-S40].
Surface `podcast:funding` / `podcast:value` alongside any skip affordance so
players can pair "skip" with "support" [G-S26, G-S71].

**Defaults that encode the asymmetry.** `action: none` unless confidence and
agreement clear the gate; `selfpromo`, funding asks and interaction cues never
in the default skip set; auto-skip off in the reference player; a "ad remaining
0:27" countdown as the flagship affordance rather than a hard skip [G impl. 3].

**Licences.** Apache-2.0 for code (patent grant, trademark carve-out, PyPI norm)
[G-S59, G-S72]; CC BY-SA or CC0 for any future label set, and do not derive
training data from SponsorBlock's CC BY-NC-SA dump [G-S2, I-S2]. Add an
intro-skipper-style disclaimer [G-S51].

## 4. The record and its exporters

### 4.1 Canonical record (`<stem>.advtt.json`)

One JSON document per rendition. Required: `profile` (`advtt/1.0`), `media`
(`duration_sec`, `bytes`, `sha256`, optional Chromaprint), `generated`, `stt`,
`classifier` (resolved model id, `prompt_version`, ensemble members), `status`,
`thresholds`, `spans[]`. Rendition binding is mandatory because DAI produces
per-listener files [F-S6, A-S9]; consumers refuse a record whose duration
differs from the file by more than yt-dlp's tolerance rule (1 s, or 5 s and 5%
of span) [A-S14].

Per span:

```jsonc
{
  "id": "ad-0001",
  "start": 751.24, "end": 779.80,
  "category": "sponsor",            // sponsor | selfpromo | interaction | crosspromo | intro | outro | preview | program
  "form": "host_read",              // host_read | produced | sponsorship_credit | unknown   (the old ADVERTISEMENT/SPONSORSHIP axis)
  "position": "midroll",            // preroll | midroll | postroll | unknown   (vernacular; IAB defines none [C-S31])
  "delivery": "unknown",            // baked_in | inserted | unknown   (IAB v2.3 words [C-S31])
  "action": "skip",                 // none | prompt | skip | mute   (policy, separate from category)
  "confidence": 0.94,               // calibrated agreement score, not the model's verbalised number
  "agreement": {"members": 2, "agreed": 2},
  "advertiser": {"name": "Acme", "confidence": 0.82},
  "edges": {"mode": "aligner", "start_err_ms": 40, "end_err_ms": 120},
  "provenance": "machine"           // machine | human | mixed
}
```

`category` is lossless into SponsorBlock (`sponsor`, `selfpromo`,
`interaction`, `intro`, `outro`, `preview`) [A-S42] and Jellyfin
(`sponsor`→`Commercial`, `intro`→`Intro`, `outro`→`Outro`, `preview`→`Preview`)
[H-S52]. `crosspromo` follows MinusPod [A-S44]. A whole-episode label
(`status: rejected_overlabel`) maps to SponsorBlock's `full` action [A-S13].
A SCTE-35 mapping table is *published*, not adopted (sponsor/produced → 0x30,
crosspromo → 0x3C, program → 0x10) [C-S24].

### 4.2 Exporters, ranked by "works today with no consumer changes"

| # | Exporter | Consumer today | Mechanism | Evidence |
|---|---|---|---|---|
| 1 | **Kodi EDL** `start end 3` | Kodi auto-skips commercial breaks with an OSD notice, re-enterable by seeking back | `.edl` beside the file | [H-S65, H-S66, H-S74, A-S41] |
| 2 | **ffmetadata chapters** + `.chp` | mpv `--chapters-file`; chapterskip.lua by title regex; chapter-make-read.lua auto-loads | text file | [H-S1, H-S4, H-S77, H-S24] |
| 3 | **Embedded chapters**: ID3 CHAP/CTOC via mutagen (MP3), QuickTime/Nero via ffmpeg `-map_chapters` (M4A/MP4), Matroska chapters with `ChapterSkipType=6` (MKA/MKV) | Apple Podcasts, Overcast, AntennaPod, Pocket Casts (manual deselect), Audiobookshelf, Jellyfin via Chapter Segments Provider | rewrite container metadata, no re-encode; ffmpeg's mp3 muxer writes no CHAP, hence mutagen | [C-S16, C-S62, H-S16, H-S61, H-S79, C-S63] |
| 4 | **Podcasting 2.0 JSON Chapters 1.2** | PC2.0 apps; Apple Podcasts (iOS 26.2); served from PodcastFetch's private RSS | `startTime`, `endTime`, `toc:true`, title `[Ad] Acme`, extension object `advtt` | [C-S8, C-S51, H-S9] |
| 5 | **SponsorBlock-shaped JSON** | mpv_sponsorblock local mode, Invidious/NewPipe-style clients | `{segment:[s,e], category, actionType, videoDuration}` | [C-S64, H-S76] |
| 6 | **WebVTT `kind=metadata`** (hardened, §4.3) | AdVTT's own single-file player; any web page; WebM embedding | sidecar `.vtt` | [C-S1, J] |
| 7 | **Visible SRT twin** `[Ad — Acme]` | any subtitle-capable player, on purpose visible | `.ads.srt`; never `Speaker:` colon-space, start at 1, never end a cue on a bare number | [J-S40, J-S61, J-S3] |
| 8 | **Evaluation formats**: Audacity labels, RTTM, Praat TextGrid | labelling and scoring workflow | 10-line writers | [C-S39, C-S38, C-S30] |

Chapter rules learned the hard way: synthesise a `00:00:00` first chapter and
≥3 chapters or Apple/YouTube ignore the file [C-S28, C-S51]; `toc:false` hides
the chapter, which is the opposite of skippable, so ad chapters are visible and
titled [H-S9]; MP3 priming shifts round-tripped chapters by ≈25 ms, document it
[C-S61, C-S62]. Offer `--title-style sponsorblock` emitting literally
`[SponsorBlock]: Sponsor` so existing yt-dlp/mpv/Jellyfin regexes match [H-S15,
H-S20]. Never publish the ad VTT as `podcast:transcript` [C-S9].

### 4.3 The WebVTT profile, hardened

Retain the two-line payload (token line, then one-line JSON). It is legal
metadata text and survives ffmpeg, WebM/MKV remux, browsers, VLC, ExoPlayer and
every library fetched [C-S1, C-S61, J-S1, J-S12, J-S30, J-S44]. Changes:

- Version on the header line: `WEBVTT - advtt/1.0 https://…/profile` (legal per
  spec) and `"v"` plus the media fingerprint in **every** cue, because NOTE is
  invisible to `TextTrack` and dropped by remuxers [C-S1, J-S13, J-S61].
- NOTE blocks optional, always preceded by a blank line (Firefox and LibSE
  recognise NOTE only after one), never containing `-->` [J-S44, J-S58].
- Cue identifiers kept but not load-bearing; the JSON `id` is normative
  (astisub renumbers, ExoPlayer discards, transcriptator dies on non-numeric)
  [J-S28, J-S31, J-S61].
- Keep `<`, `&`, `-->` escapes inside JSON; state that consumers MUST read
  `cue.text`, never `getCueAsHTML()` (ExoPlayer runs markup parsing
  unconditionally) [J-S31, J-S38].
- Consider a reverse-DNS token (`org.advtt.sponsor`) as HLS DATERANGE does
  [C-S22, C-S33]; keep it a single token so `split("\n",1)` works.
- Player rules: `<track kind="metadata" default>` becomes `hidden` in all three
  engines; cue events lag up to 250 ms, so seek to `cue.endTime`, never to "now";
  inline the VTT for `file://` [J-S42, J-S43, J-S59, C-S2].
- Containers: `-c copy -disposition:s metadata` into WebM/MKV preserves id,
  settings and payload but not NOTE, and players show it as a subtitle track;
  mkvmerge's Matroska flavour and ffmpeg's WebM flavour are mutually
  unintelligible. Offer `--embed` as transport only [J-S23, J-S47, C-S19].
- SRT inline marking (`--srt-inline`): drop it. Preamble/cue 0 is fatal in
  ffmpeg, mpv, the `srt` library, Jellyfin and Podverse; `{ad}` is hidden in
  libass pipelines and literal in VLC/ExoPlayer [J-S15, J-S11, J-S51, J-S21,
  J-S20]. The visible twin covers the real need.

## 5. Detection pipeline

### 5.1 Transcription

| Platform | Default | Alternates | Why |
|---|---|---|---|
| macOS (Apple Silicon) | `parakeet-mlx` with `parakeet-tdt-0.6b-v2` (English) / `v3` (multilingual) | `mlx-whisper large-v3-turbo` with VAD | TDT emits native word timestamps at 6.05–6.34% WER, CC-BY-4.0 [D-S4, D-S5] |
| Linux/Windows | `faster-whisper large-v3-turbo`, Silero VAD cut-and-merge, `condition_on_previous_text=False` | whisper.cpp | Whisper's DTW word times absorb pauses; VAD chunks and dropping <50 ms tokens are the documented mitigations [D-S36, D-S47, D-S49] |
| Cloud | Deepgram Nova-3 ($0.26/h, word times, keyterms) | Voxtral Mini Transcribe V2 ($0.18/h), AssemblyAI Universal-2 ($0.15/h) | only `whisper-1` among OpenAI models returns word timestamps; Gladia is 2–4× the price [D-S22, D-S24, D-S16, D-S26, D-S27] |

Pass an `--advertisers` keyterm list to every backend's biasing hook; brand
names and spelled URLs are exactly what Whisper mangles [D-S12, 0-L1].
Audio-native LLMs are not an alternative for edges: Gemini drifts by seconds to
minutes on long audio, Qwen3-Omni fails after a minute [D-S52, D-S55]. One
experiment is worth running: Gemini Flash-Lite on 5–10 min chunks as a coarse
candidate finder feeding the ladder, at ~$0.04–0.12 per hour [D-S50, D-S51].

### 5.2 Classification

Keep the tiled chunk planner and the ordered ladder. Change the anchor, the
gating signal and the reasoning control:

1. **Quote-anchored spans.** The schema asks for `start_quote` and `end_quote`
   (5–12 verbatim words each) plus an optional index hint; code resolves quotes
   against the chunk with the existing normaliser (spoken URLs, hyphens) and
   drops spans that do not resolve instead of halving confidence [E-S36,
   E-S63, B-S32]. Indices printed inline beside each segment remain in the
   prompt because copying an adjacent literal token works; counting does not
   [B-S22, B-S23]. On Claude, custom-content document blocks with Citations
   return API-validated block indices at no output cost [E-S37].
2. **Intersection ensemble.** Two passes, reasoning-on and reasoning-off (or two
   providers); a span is emitted only where both agree, with the intersection as
   its extent and `agreement` recorded. Cost on Flash-Lite/luna-class models is
   under $0.01 per hour of audio [E cost table, E-S33, E-S40]. A per-model
   capability map replaces the budget knob: `budget_tokens` (Claude 4.5),
   `effort` (Claude 4.6+ and OpenAI), `thinking_level` (Gemini) [E-S55, E-S57,
   E-S58, E-S59].
3. **Confidence from agreement, not from the model.** Verbalised confidence is
   overconfident and at best ordinal [E-S39, B-S35, B-S36]. Record it in
   `analysis.json`, calibrate it on the dev set, and where logprobs exist record
   the first-token probability of the `category` enum [E-S33]. The published
   `confidence` field is the calibrated agreement score.
4. **Schema hygiene.** One schema in the cross-provider subset (no numeric
   bounds, no recursion, `additionalProperties:false`), byte-stable per run for
   grammar and prompt caches [E-S1, E-S2, E-S3, E-S46]; keep the JSON shape in
   the prompt text for local engines that do not show the schema to the model
   [E-S6, E-S7]; detect free-text, refusal and empty-thinking outputs as
   distinct rejection reasons, not as "no ads" [E-S11, E-S12].
5. **Prompt.** 3–5 paired positive / hard-negative examples (guest self-promo,
   listener mail, editorial product mention) in `<example>` tags; no "abstain"
   label; repeat the instruction after the transcript in long chunks; test
   transcript-first against rubric-first layout, since caching floors are 1,024
   tokens on GPT-5.6+/Sonnet 5 but 4,096 on Haiku 4.5 and Gemini 3.x Flash
   [E-S38, E-S41, E-S15, E-S17, E-S20, B-S28].
6. **Borrow from MinusPod** [A-S44]: a verification pass over the *remaining*
   audio; merging nearby spans by speech seconds, not wall-clock; a per-show →
   network → global sponsor-pattern cache as a prior; ACCEPT/REVIEW/REJECT
   tiers mapped to `action`.

Model tiers (prices per 1M tokens, 2026-09; ≈$0.002–0.15 per 60-minute
episode across the spread [E-S14, E-S16, E-S19, E-S54]):

| Tier | Default | Alternate | Notes |
|---|---|---|---|
| Cloud quality | Claude Sonnet 5 ($2/$10) | gpt-5.6-terra ($2/$12) | ≈$0.04–0.05/episode; structured outputs GA on both |
| Cloud cheap | Gemini 3.1 Flash-Lite ($0.25/$1.50, free tier) | gpt-5.6-luna ($0.20/$1.20) | ≈$0.006/episode; ensemble members |
| Open weights hosted | gpt-oss-120b on Fireworks ($0.15/$0.60) | — | when open weights are a requirement |
| Local 32 GB | Gemma 4 26B-A4B via Ollama GGUF or LM Studio | gpt-oss-20b (16 GB) | schema enforcement works on GGUF/llama-server/LM Studio; **not** on `mlx_lm.server`, and Ollama's MLX runner ignored `format` until PR #17929 [E-S9, E-S11, E-S12, E-S62, E-S53] |
| Local 64 GB | Qwen 3.8-27B | Gemma 4 31B | IFBench 79.5 / 76; ~30–90 s prefill per episode [E-S56, E-S26, E-S50] |

Archive runs use each vendor's batch API at 50% with the one-hour cache TTL
[E-S14, E-S18, E-S19].

### 5.3 Edge refinement

Cut a ≤5-minute window around each candidate edge and run a forced aligner
(Qwen3-ForcedAligner-0.6B, Apache-2.0, ~28 ms mean shift; MFA/ctc aligners
~50 ms) or snap to the nearest Silero-VAD silence [D-S19, D-S37, D-S49]. Avoid
torchaudio's deprecated `forced_align`, the CC-BY-NC MMS aligner default, and
AGPL whisper-timestamped [D-S40, D-S44, D-S64]. Carry `edges.mode` and an
estimated `start_err_ms/end_err_ms` so players pad conservatively when an edge
came from a coarse source; the reference player crossfades 10–20 ms [D-S45].
Keep the inherited rule that the end edge is not trimmed to the evidence quote.

### 5.4 Acoustic corroboration (new, in priority order)

1. **Loudness step + silence gap** within ±3 s of each LLM boundary, from
   `ffmpeg ebur128=metadata=1` (400 ms / 3 s LUFS) and Silero VAD: snap edges
   and adjust confidence; never mark on acoustics alone [F-S27, F-S37, F-S32].
2. **Per-show repeated-segment index.** Landmark fingerprints (Olaf or
   audfprint; Chromaprint is a whole-track identifier) over every episode of a
   show; ≥15 s spans recurring across episodes are produced spots or promos.
   Exclude the show's theme. Check Olaf's licence and patent note [F-S35,
   F-S40, F-S62, A-S36].
3. **Differential download** (two fetches, correlation ≤0.60 regions become
   DAI candidates): opt-in, off by default, implemented in the fetcher not the
   library, after reviewing Amazon's US 12,190,871 B1 and accepting doubled
   publisher download counts [F-S32, F-S58]. Emits `delivery: inserted`, a
   provenance fact distinct from the ad judgment.
4. **Music-bed-under-speech** via YAMNet's "Background music" / "Jingle" classes
   as a `form: produced` feature, after an FPR experiment; inaSpeechSegmenter
   cannot do this (tags speech-over-music as speech) [F-S30, F-S36, F-S54].
   Scripted-vs-spontaneous prosody stays a research item [F-S12].

Expected coverage: acoustic boundary cues apply to the ~92% of ad dollars
delivered by DAI; fingerprints to the ~26–30% that is produced/programmatic;
host-read baked-in reads remain transcript-only [F-S17, F-S49].

### 5.5 A distilled proposer (v2)

The measured state of the art for spoken-ad detection is a fine-tuned encoder
over ASR text (RADIA F1 87.8 on radio; Spotify per-sentence BERT F1 0.77 with
precision 0.69 on podcasts) [B-S49, B-S1]. That precision cannot meet a ≤5 s
content-loss gate alone, but recall ~0.9 makes a ModernBERT token classifier a
viable *proposer*: it selects candidate regions and the LLM adjudicates only
those (5–15% of an episode), cutting cost and latency 5–10× [E-S48, E-S44,
B-S39]. Train on AdVTT's own validator-passed spans from ≥200 episodes, not on
SponsorBlock (NC licence); expect the recall-heavy bias distillation inherits
[B-S39, B-S40].

## 6. Evaluation and the public benchmark

**Metric suite** (two levels, definitions published) [I-S9, I-S28, I-S54, B-S47]:

- Level A, duration-based per episode on a 1 s grid with a 0.5 s collar:
  `content_loss_sec` (false-alarm seconds; pyannote DCF with fa=1, miss=0, the
  inverse of OpenSAT's 0.25/0.75 and said so), `ad_recall_sec`, per-second MCC.
- Level B, event-based: a predicted span matches if IoU ≥ 0.5 or both boundaries
  fall within tolerance (onset 3 s; offset max(3 s, 20% of span)); report
  precision/recall/F0.5 (MinusPod's choice, for comparability [A-S45]), and
  boundary error as median and p90, plus `edge_err_ms` for aligner-refined
  edges.
- Gates keep their values (≤5 s, ≥0.70) but every number carries a bootstrap
  95% CI clustered by show; per-show tables and a worst-episode table, because
  the ship gate is a per-episode maximum [I-S31, I-S42].

**Dataset plan.** The 4 fixtures are the *dev* set and are named as
contaminated. Build a disjoint *test* set of ≥60 episodes from ≥10 shows
(rule of three: zero violations in 60 bounds the rate at 5%) including ≥5 no-ad
controls [I-S30, A-S45]. Two annotators on a 20% overlap; report γ agreement
and the boundary-distance histogram, which also justifies the 3 s tolerance
empirically [I-S7, I-S36]. Truth JSON gains `annotator`, `tool`, `source`,
`boundary_confidence`. Labelling via Audacity labels or Label Studio audio
regions with <30-line converters [I-S16, I-S62].

**Silver labels from SponsorBlock** for shows with YouTube mirrors: yt-dlp
`--sponsorblock-mark` plus dump rows filtered by the server's consensus rule,
aligned to RSS audio with BBC audio-offset-finder on several windows and
rejected when offsets disagree (that disagreement itself flags DAI); hand-verify
20% and publish the label-error rate (prior: half of DeepSponsorBlock's gross
failures were label errors) [I-S66, I-S26, I-S13, I-S5]. Derived data stays
BY-NC-SA and is used to *evaluate*, never to train [I-S2].

**PodAd-Bench (minimum viable, public).** Labels-only repository (GUID, feed
and enclosure URL, SHA-256, duration, spans, annotator/source, audio licence);
audio mirrored only for CC BY / BY-SA shows (Hacker Public Radio as ad-free
negatives; resolve Jupiter Broadcasting's BY-SA vs BY-NC per feed; TWiT
referenced whole-file only, since its BY-NC-ND text bans ad removal) [I-S41,
I-S40, I-S68, I-S67]; dev/test/private splits with written inclusion filters and
a quarterly refresh; a harness that downloads from original enclosures and
verifies hashes; a contamination statement. It would be the first public
time-aligned podcast-ad benchmark [I, B-S50]. Benchmark against MinusPod's
harness and ZeroAds' "85% of cut seconds are ad" figure [A-S45, A-S59].

**Regression and drift.** A recorded-response store keyed by
`sha256(prompt_version | model_id | chunk_text)` committed for the dev set, so
CI runs offline with zero dependencies; a weekly live canary that fails when a
Level-A metric leaves its CI; resolved model snapshot ids in provenance, since
aliases move and behaviour changes silently under one name [I-S34, I-S44,
I-S59, H-S35]. Re-derive the 240 s span cap and 35% gate from the test set's
empirical distribution [I impl. 8].

## 7. Packaging, configuration, distribution

- `pyproject.toml` with Hatchling and PEP 621; `requires-python >= 3.11`; zero
  hard dependencies in core (stdlib `urllib`, `json`, `subprocess` for ffmpeg)
  [H-S6, H-S18, H-S58, H-S59].
- Extras: `[openai] [anthropic] [gemini] [mlx] [parakeet] [aligner] [keyring]
  [all]`; providers as pluggy plugins via `[project.entry-points."advtt"]`,
  following `llm` [H-S30]. Never pin torch the way whisperX does [H-S44].
- Install paths: `uv tool install advtt --with advtt-mlx`, `pipx inject`,
  Trusted Publishing to PyPI, a personal Homebrew tap for the core only (core
  formulae cannot carry MLX/torch) [H-S10, H-S27, H-S75, H-S68].
- Keys: `advtt keys set openai` writing `keys.json` under the platform config
  dir, env fallback, optional `keyring` with `gh`'s fallback ladder
  [H-S2, H-S37, H-S39]. No key ever lands in an artefact.
- `--offline`: refuses every network provider and prints the hosts that would
  have been contacted. No comparable tool documents such a mode [H §keys].
- Tests: pytest-recording with `record_mode=none` and `block_network` for HTTP
  backends; the replay store of §6 for the classifier seam [H-S35].
- Spec publication: versioned profile document and JSON Schema (`$id`) on the
  project domain, RFC 6906 "profile" language, a SchemaStore catalog entry;
  a W3C Community Group draft only if outside interest appears (WebVMT has been
  an experimental Note for seven years) [C-S54, H-S34, C-S29, C-S55]. The
  podcast route is "already used in the wild" via chapters plus one cooperating
  host, not a new tag [C-S36].

## 8. PodcastFetch integration

- PodcastFetch consumes `advtt.classify_segments()` through the `TaskExtension`
  hook so speaker attribution stays in the same model call; the extraction
  regression protocol in `01-` §6 stands (self-test, `--dump-prompt` diff, eval,
  byte-identical `_ads.json` on fixtures) with one amendment: the quote-anchored
  schema is a `prompt_version` bump, so the archive is reclassified once in
  batch mode at 50% [E-S18].
- PodcastFetch is the natural home for the two fetcher-side channels: the
  differential download (§5.4) and serving a private RSS with
  `<podcast:chapters>` and embedded ID3 chapters, so any Podcasting 2.0 app,
  Apple Podcasts or Overcast shows the ad chapters without sideloading
  [H impl. 2, C-S51].
- PodcastFetch's dashboard reads the canonical record, not the VTT.

## 9. Trajectory

Phases have exit criteria, not dates.

**Phase 0 — Decisions and decisive experiments (before code moves).**
Decide: name and framing (§3), licence, vocabulary (§4.1), chapters-primary.
Run the experiments that change design: (a) quote-anchored vs index-anchored
output on the 4 fixtures, resolution rate and boundary error; (b) reasoning-on ∩
reasoning-off on Sonnet 5, gpt-5.6, Flash-Lite, Haiku 4.5, measuring recall
lost vs content-loss gained; (c) gpt-5.5 on two no-ad control episodes; (d)
Apple Podcasts / AntennaPod / Pocket Casts rendering of a test feed with
`[Ad]` chapters and `endTime`; (e) Kodi EDL action 3 on audio-only files.
Exit: decisions recorded in `09-decisions.md`; experiments logged as track K.

**Phase 1 — Extraction and core.** Move providers, chunking, ladder, refinement,
STT seam into `advtt` with the `TaskExtension` hook; implement the canonical
record; quote anchoring; capability map; agreement scoring. Exit: `--self-test`
green, `--dump-prompt` byte-identical for the legacy schema, fixtures
reclassify identically under the legacy `prompt_version`.

**Phase 2 — Exporters and player.** EDL, ffmetadata/`.chp`, mutagen CHAP/CTOC,
MP4/Matroska chapters (`ChapterSkipType=6`), JSON Chapters with extension
object, SponsorBlock JSON, hardened WebVTT, SRT twin, Audacity/RTTM. Reference
player reads the record and the VTT, countdown affordance, auto-skip off.
Exit: round-trip tests for every exporter; the compatibility matrix in `03-`
replaced by the measured one from track J plus device tests.

**Phase 3 — Evaluation and PodAd-Bench.** Test set ≥60 episodes / ≥10 shows /
≥5 no-ad controls; two-annotator overlap; metric suite; replay store; canary;
re-derived gates; public labels-only release with harness. Exit: a published
results table with CIs and a contamination statement; MinusPod-comparable
F0.5.

**Phase 4 — Edge precision and acoustic channel.** Aligner-based edges with
`edge_err_ms`; loudness/VAD corroboration; per-show fingerprint index;
differential download behind a flag in PodcastFetch. Exit: median edge error
≤100 ms on aligner-mode spans; produced-spot recall measured separately.

**Phase 5 — PodcastFetch re-consumes AdVTT.** `adclass.py` shrinks to speaker
task, sidecars, archive policy; private RSS with chapters; batch reclassify.
Exit: archive reclassified once; dashboard on the canonical record.

**Phase 6 — Distilled proposer and publication.** ModernBERT proposer trained
on ≥200 self-labelled episodes; profile document, JSON Schema, SchemaStore
entry; approach one podcast host and one app about "already in the wild"
chapters. Exit: proposer recall ≥0.95 at ≤15% of audio forwarded; spec
published.

## 10. Resolving the open questions of `06-`

| # | Question | Decision |
|---|---|---|
| 1 | Is extraction worth the coupling cost? | Yes. The `TaskExtension` hook stays; no evidence favours the thin-front-end alternative, and batch mode makes a one-time reclassification cheap. |
| 2 | Two-line cue payload? | Keep it; hardened per §4.3. Verified safe across every fetched parser [J]. |
| 3 | Where does the header belong? | Header line text + per-cue `"v"` and fingerprint; canonical record carries the rest; NOTE is optional documentation. |
| 4 | Four terms or seven? | Neither: SponsorBlock/Jellyfin-compatible `category` plus `form`, `delivery`, `position`, `action`. What is emitted is what is measured; the vocabulary can name more than the classifier emits. |
| 5 | Events track always separate from captions? | Yes, and the events track itself is one exporter of the canonical record. |
| 6 | Ship SRT inline? | No. Evidence in J makes every inline variant fail somewhere that matters; the visible twin stays. |
| 7 | Three drift probes enough? | Replace with audio-offset-finder over several windows with a confidence score and consistency check (the same mechanism used for SponsorBlock alignment) [I-S13]. |
| 8 | Cache key and location? | `analysis.json` presence is the cache; key `sha256(prompt_version | model_id | segments)`; the replay store reuses the same key. |
| 9 | Boundary confidence source? | `edges.mode` + aligner residual → `start_err_ms/end_err_ms`; omit numbers the pipeline cannot earn. |
| 10 | Human review: file, overlay or field? | Overlay diffs against the machine record (every correction is a labelled error for the test set); `provenance: human|mixed` on merge. |
| 11 | Naming | Tool `advtt`; profile `advtt/1.0`; framing "advertising disclosure record". Drop "Media Events WebVTT" as the profile name: the profile is now one exporter. |
| 12 | Does anything use the video? | Not in v1; demux only. Visual cues are a later track. |
| 13 | Licence, packaging, distribution | Apache-2.0; §7. |

## 11. Risks

- **Evidence quotes fail more on some STT backends** (WhisperX cannot align
  digits/symbols; brand names mangle) [D-S12]: measure per-backend quote
  resolution rates before dropping unresolved spans becomes the rule; normalise
  numerals and URLs in the matcher.
- **Ensemble recall loss.** Intersection may cut `ad_recall_sec` below 0.70 on
  cheap members; the Phase 0 experiment decides member choice.
- **Apple's `endTime`/`toc` handling is untested by anyone** [C-S60]; chapter
  delivery to Apple Podcasts may show start markers only.
- **Community reception.** The namespace and two apps have said no to
  ad-skipping tooling; the disclosure framing, opt-outs and funding surfacing
  are the mitigation, and they are cheap.
- **Patent exposure** on differential download [F-S58]: keep it optional,
  fetcher-side, and reviewed.
- **Model churn.** Everything model-specific (defaults, effort parameters,
  cache floors) will be stale within months; the capability map and canary
  exist for this.

## 12. Appendix: reading order into the log

Positioning → G, A. Formats → C, J, H. Pipeline → E, B, D, F. Evaluation → I.
Each track file ends with its own Open questions; those not promoted into §9
remain valid backlog.
