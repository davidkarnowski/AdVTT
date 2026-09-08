# 07 — Research log (index)

Spike run 2026-09-01 → 2026-09-02. Purpose: replace the preliminary design in
`01-`…`06-` with an evidence-based recommendation for a publicly released,
time-based advertising annotation tool. Outcome: `08-recommendation-and-trajectory.md`.

This file is the index. The evidence lives in `research-log/`, one file per
track, each with numbered sources (`S1…`), a per-source *Verified: fetched |
snippet-only* flag, a Synthesis, Implications for AdVTT, and Open questions.
Citations in `08-` use the form **[C-S61]** = track C, source 61.

## Method

- Ten parallel research tracks, each briefed by `research-log/00-BRIEF.md`
  (shared project context, rules, log format). Local grounding first
  (`research-log/0-local-grounding.md`): PodcastFetch's `adclass.py`, its
  measured eval results, the fixtures, and the author's WebVTT analysis.
- Primary sources preferred over snippets: specs, source code (raw GitHub),
  court opinions, vendor docs, arXiv PDFs. Two tracks ran local `ffmpeg`
  experiments (C-S61, C-S62). Where a page could not be fetched it is logged as
  a gap, not guessed.
- No browser automation was used (WebFetch/curl/pdftotext only).

## Chronology

| When (PT) | Event |
|---|---|
| 09-01 ~16:00 | Local grounding read; brief written; ten tracks launched. |
| 09-01 ~16:10 | All ten tracks killed by a session rate limit with nothing on disk. |
| 09-01 16:43 | Brief amended with a mandatory **incremental-writing** rule (create file first, append per source, status line every ~5 sources). |
| 09-01 16:45 | Wave 1 resumed: A, C, E, I, J. All completed 16:55–17:35. |
| 09-01 ~17:00 | Wave 2 launched: B, D, F, G, H. Cut off again by a session limit; B/D/F/H had partial logs on disk (3–25 KB), G none. |
| 09-02 | Wave 2 resumed from partial logs; all completed. Session-wide WebSearch quota (200 calls) was exhausted early in wave 1, so most of the spike ran on direct fetches of primary URLs. |

## Tracks

| Track | File | Sources | Fetched | Scope |
|---|---|---|---|---|
| 0 | `0-local-grounding.md` | 5 | local | What exists: classifier, measurements, fixtures, north-star doc |
| A | `A-prior-art-products-and-oss.md` | 63 | 56 | Products, apps, OSS that detect/skip ads; SponsorBlock; ad-intelligence vendors; TV comskip lineage; time-range formats in the wild |
| B | `B-academic-literature.md` | 54 | ~34 | Podcast/radio/TV ad detection papers; segmentation; long-context; calibration; distillation; metrics |
| C | `C-time-based-metadata-standards.md` | 72 | ~45 (+2 experiments) | WebVTT/DataCue; Podcasting 2.0; ID3/MP4/Matroska chapters; SCTE-35/HLS/DASH; IAB; publication paths |
| D | `D-stt-and-alignment.md` | 73 | most | STT engines and pricing; word-timestamp accuracy; forced aligners; Whisper failure modes; audio-native LLMs; diarization |
| E | `E-llm-classification-methods.md` | 64 | ~45 | Structured outputs per provider; 2026 pricing; local models; index-vs-quote anchoring; chunking; reasoning; calibration; encoders |
| F | `F-acoustic-signals-and-dynamic-insertion.md` | 62 | most | Industry structure (DAI vs baked-in, host-read vs produced); DAI mechanics; differential download; fingerprinting; loudness/VAD/music detection |
| G | `G-legal-ethics-and-release-policy.md` | 75 | 50 | Ad-skipping and ad-blocking case law; TDM exceptions; ToS; community norms; opt-outs; licences |
| H | `H-packaging-distribution-integration.md` | 80 | most | Python packaging; key handling; mpv/Kodi/yt-dlp/Jellyfin/podcast-app mechanics; chapter carriers; spec publication; CI patterns |
| I | `I-evaluation-and-datasets.md` | 68 | ~55 | Datasets; SponsorBlock as silver truth; metric families; labelling tools; statistics; regression/drift testing; public benchmark design |
| J | `J-webvtt-srt-parser-and-player-compatibility.md` | 61 | most (source-level) | How real parsers/players/browsers treat NOTE, identifiers, two-line payloads, SRT quirks, Matroska/WebM embedding |

Total: ~670 logged sources, ~100k words of notes.

## Headline findings (one line each; details and citations in `08-`)

1. Nobody ships portable, typed, confidence-bearing ad time-range metadata for arbitrary podcast files; the detection problem is crowded (Podly, MinusPod, ZeroAds, Herd, Skipper), the interchange problem is open. [A]
2. MinusPod is the strongest open rival and publishes the only per-model podcast-ad benchmark; it ranks gpt-5.5 below Haiku 4.5 and Gemini Flash-Lite and flags it for failing a no-ad control. [A-S45]
3. Real players skip on **chapters** and **EDL**, not on WebVTT metadata; no surveyed tool consumes a `kind=metadata` track. [A, H]
4. The two-line token+JSON WebVTT payload is spec-legal and survives every fetched parser; **NOTE blocks and cue identifiers are the fragile parts**. [C, J]
5. Matroska is the only container standard that names ads as skippable (`ChapterSkipType=6`), but no player checked honours it. [C-S63, C-S71]
6. The Podcast Index namespace **rejected** a publisher-side ad-range tag over ad-blocker fears; Apple Podcasts now reads JSON, ID3 and MP4 chapters. [A-S50, C-S51]
7. Indices are the wrong anchor for LLM span output; verbatim quotes resolved in code are right. Chunking is independently justified by long-context degradation research. [E, B]
8. Reasoning-on vs reasoning-off is contested; the literature's fix is an ensemble, not a budget knob. Verbalised confidence is ordinal at best. [E-S33, B-S38]
9. State of the art for spoken-ad detection is a fine-tuned encoder over ASR text; LLMs are state of practice. A distilled encoder is viable as a *proposer*, not the final judge. [B, E]
10. Parakeet TDT / Whisper are the local STT choices; only `whisper-1` among OpenAI models returns word timestamps; audio-native LLMs drift by seconds to minutes and cannot place edges. [D]
11. Forced aligners put ~90% of word boundaries within 50 ms; Qwen3-ForcedAligner reports ~28 ms mean shift. [D-S19, D-S37]
12. DAI carries ~92% of US podcast ad revenue but host-read is still ~46% of spend; loudness steps and differential downloads find splices, fingerprints find repeats, transcripts find host reads. [F]
13. Fox v. Dish described an ad-skip architecture (markers in a separate file, off by default, media untouched) and held it non-infringing; annotation-only, local-only output is the defensible posture. [G-S1]
14. No public podcast benchmark with time-aligned host-read ad labels exists; 4 fixtures cannot support the ship-gate claim (rule of three → ≥60 episodes). [I]
15. Hatchling + PEP 621, zero hard deps, extras and entry-point plugins is the packaging norm (yt-dlp, llm); Homebrew cannot carry MLX/torch. [H]

## Cross-track contradictions and how `08-` resolves them

| Topic | Positions | Resolution |
|---|---|---|
| Primary output format | C: keep WebVTT metadata primary. A/H: chapters primary, WebVTT one exporter. | One canonical JSON record; WebVTT metadata is the lossless *interchange*; chapters/EDL/SponsorBlock-JSON are the *delivery* carriers. |
| `toc:false` for ad chapters | C/F: consider it. H: it hides the chapter from the UI, the opposite of skippable. | Emit visible (`toc:true`) titled ad chapters; carry machine fields in an extension object. |
| Reasoning budget | Project: thinking off → 77.5 s false positives. E/B literature: reasoning lowers recall at low FPR. | Reasoning-on ∩ reasoning-off (or two-provider) intersection ensemble; drop the budget knob. |
| Default cloud model | Project: gpt-5.5 passes its gate. A-S45: gpt-5.5 fails MinusPod's no-ad control. | Add no-ad controls to the eval; re-evaluate; provisional cloud-quality default Sonnet 5 or gpt-5.6-terra. |
| Boundary tolerance | I: 3 s onset tolerance for event matching. D: ≤100 ms edge target. | Two levels: 3 s for detection matching; ≤100 ms for aligner-refined edges, reported separately. |
| Pre/mid/post-roll authority | Snippets attribute definitions to IAB. C-S31 correction: IAB v2.3 defines none; F-S17 finds "first two minutes" in the 2023 IAB study. | Use position words as vernacular with the 2023 IAB study cited, not as a Tech Lab definition. |
| Amazon vs Spotify patent assignee | F-S51 initially Spotify. F-S58 correction: Amazon Technologies. | Amazon. |

## Documented gaps (could not be fetched or verified)

SponsorBlock's own wiki pages (anti-bot wall; read via mirrors/Wayback); Kodi wiki HTML (API used instead); Plex docs; VMAP 1.0.1 primary PDF; IAB 2016 Podcast Ad Metrics Guidelines; Art19 terms (404); NPR terms; Speechmatics and Google Chirp pricing; Apple-Silicon speed figures for STT models from primary sources; TiVo SkipMode mechanics; Herd's on-device claim; Singapore statute text (403); Audacity manual (521). Each is marked in the relevant track file.

## How to keep this log alive

Add new evidence as a new `S<n>` entry in the relevant track file (or a new
track file `K-…`), keep the *Verified* flag honest, and update the track's
Status line. Do not edit an existing S-entry's facts; add a dated correction
entry (see C-S31, F-S51, J-S21 for the pattern).
