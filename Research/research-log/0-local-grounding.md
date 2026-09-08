# 0 — Local grounding (what already exists, read before any web research)
Accessed: 2026-09-01 (local files)

## Sources
### L1. `PodcastFetch (private sibling project)/adclass.py` (3701 lines, PROMPT_VERSION `2026-08-g`)
- Type: code
- Verified: read
- Key facts:
  - Constants: `AD_THRESHOLD=0.75`, `UNCERTAIN_THRESHOLD=0.40`, `CONTEXT_SEGMENTS=12`,
    `MAX_SPAN_SECONDS=240`, `MAX_AD_FRACTION=0.35`, `DEGENERATE_SPAN_FRACTION=0.60`,
    `DIALOGUE_Q_DENSITY=0.20`, `MIN_SEGMENTS=10`, `AD_KINDS=(preroll,midroll,postroll,house,section)`.
  - Model returns `ad_spans[{start_index,end_index,kind,confidence,evidence,end_evidence}]`
    under an OpenAI strict-mode-compatible JSON schema.
  - System prompt (~165 lines) is entirely about *host-read* ads; explicit
    negative list (company as news subject, guest self-promotion, handoffs,
    sign-offs, free cross-promo, off-hand sponsor mentions); the "flow test"
    (delete the passage: does the conversation still join up?); evidence must
    be a 5–15 word verbatim quote from the `start_index` line only.
  - Speaker attribution rides in the same call when `_diar.json` exists.
- Relevance to AdVTT: this is the asset being extracted; any recommendation must
  preserve or deliberately supersede it with measured evidence.

### L2. `PodcastFetch (private sibling project)/README.md` §"Adapter maturity", §"Chunking", §"Validation ladder"
- Type: project doc (measured results, 2026-08-31)
- Verified: read
- Key facts:
  - 99 archive episodes classified: openai/gpt-5.5 65, claude-cli 33, gemini 1, ollama 0.
  - Fixture eval, 4 episodes: gpt-5.5 passes gate; gemini-2.5-flash `content_loss_sec` 11.7 (FAIL), gemini-3.6-flash 0.0 (PASS, recall 0.786 with 2 chunks lost to 503s).
  - claude-haiku-4-5 via CLI: thinking off → `content_loss_sec` 96.5 (JRE alone 77.5 s false-positive); budget 4000 → 8.6; default budget → ships. Cost per classification call $0.11–0.22; ~500 tokens of JSON answer, the rest is thinking.
  - Whole-episode single call on a 3919-segment transcript: gpt-5.5 found the right sponsor text but reported it at segment 1245 instead of 445. 6000-token chunks matched ground truth exactly.
  - 503s on flash models previously dropped chunks silently and cached `ok`; now `incomplete_chunks` blocks caching.
- Relevance: the strongest empirical facts in the project; chunking and thinking are accuracy levers, not cost levers.

### L3. `PodcastFetch (private sibling project)/tests/fixtures/README.md`
- Type: dataset doc
- Verified: read
- Key facts: 4 fixtures, 3 from The President's Daily Brief (news, clearly marked breaks) + 1 Joe Rogan Experience (long-form interview). One `.mp3` retained (764.6 s). Covers: clean sponsor reads with URL/promo code; a "support for Israel" false-positive trap; handoff lines; free cross-promo vs paid `house`.
- Relevance: the evaluation set is tiny (4 episodes, 2 shows) and was used to tune the prompt → not a held-out set. Track I must address this.

### L4. `WebVTT.Ads (sibling project)/Research/media-events-webvtt-advertising-analysis.md` (1613 lines, 7 references)
- Type: design analysis (author's own)
- Verified: read (§1–9, 24–27, 32–36, references)
- Key facts: proposes a WebVTT `kind=metadata` profile "Media Events WebVTT"; 7-term primary vocabulary; two-tier (VTT + analysis.json); provenance first-class; detection separate from identification; phased path profile → spec → player → standards. References are W3C WebVTT, MDN, W3C Media Timed Events, IPTC Video Metadata Hub, w3c/webvtt repo only — no prior-art survey of ad detection tools, no Podcasting 2.0, no SCTE-35 detail, no ID3/MP4/Matroska chapters.
- Relevance: the north star is a *format* argument; it never asked whether a format other than WebVTT already reaches more players. Track C/H must answer that.

### L5. `the AdVTT repository root/Research/01–06` and `README.md`
- Type: design docs (2026-09-01)
- Verified: read
- Key facts: extraction plan with `TaskExtension` hook; `advtt/0.1` profile with two-line cue payload; SRT companion strategy with an untested compatibility matrix; CLI with drift check; player prototype; 13 open questions (blocking: coupling cost of extraction).
- Relevance: the baseline the new recommendation either confirms or replaces.

## Synthesis
The existing work is strong on classifier mechanics and format design and thin on
(1) prior art, (2) alternative delivery formats that existing players already
skip on (chapters), (3) non-transcript signals, (4) evaluation scale, and
(5) release policy. The research tracks A–J were scoped to those gaps.

## Implications for AdVTT
1. Preserve the measured invariants (chunking, ladder, thinking budget) unless a
   track produces contrary measurements.
2. Every format recommendation must be tested against "which player skips on it
   today", not just "which spec permits it".
