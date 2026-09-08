# Research brief (shared context for every research track)

Date: 2026-09-01. Project: **AdVTT** at `the AdVTT repository root`.

## What the project is

An LLM-based advertisement/sponsorship classifier for finished digital audio
(podcast episodes first; video later) whose output is **time-based metadata**:
start/end times of advertising and sponsorship blocks, with confidence, kind
(preroll/midroll/postroll/house/section), advertiser label, and provenance.
The tool is being split out of the author's private podcast downloader
**PodcastFetch** for **public release** as a standalone CLI + library, and
PodcastFetch will re-consume it.

## What exists today (proven, measured)

- STT seam: whisper-mlx / parakeet-mlx (Apple Silicon local), Gladia, OpenAI.
  Word timestamps when available.
- Transcript is chunked into ~6000-token tiled windows with 12 read-only context
  segments each side; an LLM (OpenAI gpt-5.5, Claude via CLI, Gemini, Ollama,
  MLX) returns index spans + a verbatim evidence quote from the first line.
- An eight-rung validation ladder: parse → index range → max duration (240 s) →
  merge (min confidence) → evidence quote must match verbatim (fails halve
  confidence) → dialogue/question-density demotion → episode over-label gate
  (>35% ad = reject whole episode) → empty-is-valid.
- Word-precise edge refinement using the evidence quote in the word stream.
- Metrics on 4 hand-labelled fixtures: `content_loss_sec` (content seconds
  falsely marked ad; ship gate ≤ 5 s), `ad_recall_sec` (≥ 0.70), `boundary_err_sec`
  (≤ 3 s). Whole-episode single-call classification was measured to misplace
  span indices badly (right text, wrong segment index), hence chunking.
- Design principle: **the false-positive asymmetry** — silently skipping
  journalism is far worse than failing to skip an ad. Auto-skip off by default.
- Ads targeted are largely **host-read**, in the host's voice, no jingle.

## Preliminary design (not committed; the user is "not married to any of it")

- Output as WebVTT `kind="metadata"` track ("media-events.vtt") with a two-line
  cue payload (vocabulary token line + JSON line), a `NOTE ADVTT/0.1` header,
  plus `analysis.json` with evidence; SRT treated as caption-only with a
  companion `.ads.vtt` and an optional visible `.ads.srt` twin.
- Vocabulary v0.1: ADVERTISEMENT, SPONSORSHIP, PROMOTION, PROGRAM.
- Single-file HTML player prototype that reads the track and offers skip.

## What this research spike must produce

A **new** recommendation and project trajectory. Every track should challenge
the preliminary design where evidence warrants, and surface alternatives the
author has not considered. Be concrete, cite everything.


## INCREMENTAL WRITING — MANDATORY

Session limits have already killed one full run of this spike with nothing on
disk. So:

- **Create your log file first**, before any web request, with the title,
  "Accessed" line, an empty `## Sources` heading and a `## Status` line reading
  `IN PROGRESS — started <time>`.
- **Append each source entry to the file the moment you have read it** (Bash
  `cat >> file <<'EOF'` or Edit). Never hold more than ONE source in memory
  unwritten. A search that yields candidate URLs should be logged immediately as a
  `### Search: "<query>"` line listing the candidates, before you fetch any.
- Every ~5 sources, update the `## Status` line with a count and the next
  planned queries, so a successor can pick up exactly where you stopped.
- Write `## Synthesis`, `## Implications for AdVTT` and `## Open questions` as
  soon as you have enough to say anything, then revise them; do not save them
  for the end.
- When finished, set `## Status` to `COMPLETE`.

## Rules for every research track

1. Use WebSearch and WebFetch extensively (aim for 15–30 distinct sources; fetch
   the primary source whenever possible rather than trusting a snippet).
2. **Never** launch a browser, headless Chrome, or any browser automation.
3. Write your log to the file path you were given. Format:

   ```
   # <Track letter> — <Title>
   Accessed: 2026-09-01

   ## Sources
   ### S1. <Title> — <URL>
   - Type: spec | paper | product | repo | blog | forum | dataset | legal
   - Verified: fetched | snippet-only
   - Key facts: (bullets, with exact numbers, quotes ≤ 25 words, version/dates)
   - Relevance to AdVTT: (1–3 bullets)
   ### S2. ...

   ## Synthesis
   (what the evidence says, contradictions between sources, gaps)

   ## Implications for AdVTT
   (numbered, concrete, each pointing back to S-numbers)

   ## Open questions / things that need an experiment
   ```
4. Mark each claim with its source number. Distinguish what you verified by
   fetching from what you only saw in a search snippet. If you could not
   find something, say so — a documented gap is a finding.
5. Do not fabricate URLs, version numbers, benchmark figures or quotes. If a
   figure is approximate, say "approx." and cite where it came from.
6. Prefer 2024–2026 sources for anything about model capability, pricing, or
   software features; older sources are fine for standards and case law.
7. Finish by returning (as your final message) a summary of ≤ 900 words: the
   top findings, each with its URL, and the top 3–5 implications for AdVTT.
