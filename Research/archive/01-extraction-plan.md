# 01 — Extraction plan: what moves out of PodcastFetch

Source of truth for this document: `adclass.py` (3701 lines) and `stt.py` (667
lines) in `PodcastFetch (private sibling project)`, read 2026-09-01. Line
numbers are given as anchors and will drift; the symbol names will not.

The governing rule: **PodcastFetch must be able to re-consume AdVTT without a
single changed byte in `_ads.json`.** 99 classified episodes are cached against
`prompt_version` and a segment hash. If extraction perturbs the prompt, the
schema, or any rung of the ladder, the cache is either silently wrong or
wholesale invalidated at real money. So the extraction is a *move*, not a
rewrite, and the regression bar is byte equality.

## 1. The three things `adclass.py` currently does

| Concern | Lines (approx) | Podcast-specific? |
|---|---|---|
| LLM backend adapters | 271–1204 | No |
| Ad classification: prompt, chunking, ladder, refinement | 1206–1731, 2470–2560, 2694–2870 | No |
| Speaker attribution | 1375–1500, 1861–2469 | **Yes** (needs `_diar.json`, `sources.json` hosts) |
| Archive filing: sidecar paths, cache, atomic writes | 2567–2693 | **Yes** (`_stt.json` → `_ads.json` naming) |
| Eval + self-test | 3028–3583 | No (fixtures are, the harness is not) |
| CLI | 3584–3701 | Mixed |

That table is the extraction. Rows marked "No" move.

## 2. What moves

### `advtt/providers.py`
`AdProvider` (adclass:279), `ProviderError`, `_extract_json_object`, `_http_json`,
`_http_json_h`, and the six adapters: `OllamaProvider`, `OMLXProvider`,
`OpenAIProvider`, `ClaudeProvider`, `ClaudeCLIProvider`, `GeminiProvider`, plus
`PROVIDERS`, `make_provider`, `available_providers`.

Moves **verbatim**. The interface is already the right shape and is already
documented in the base class:

- `available()` — configured-ness, never touches the network, feeds a settings UI.
- `ensure_ready(probe=False)` — liveness; `probe=True` permits one cheap live call,
  made once per job. This distinction exists because OpenAI returns 429 for both
  "too fast" (retry) and "no money" (fatal), and finding out per-episode costs 90 s
  each.
- `complete_json(system, user, schema, timeout)` → `(dict, meta)`; `meta['raw_text']`
  always present, `meta['parse_error']` on failure, and the *caller* decides what
  to do with a parse failure — that is ladder rung 1 and must not migrate into the
  adapter.
- `web_search_answer(task)` → `None` on adapters with no native search tool. Only
  `OpenAIProvider` implements it.
- `max_chunk_tokens` is a per-adapter class attribute, not a global.

Two invariants travel with this file and must be restated in its module docstring
or they will be lost: `make_provider` **never** falls back local → cloud, and every
adapter is stdlib-`urllib` only. The second is what makes adding an adapter a
one-class job with no dependency negotiation.

`ClaudeCLIProvider` carries hard-won flags (`--tools ""`,
`--exclude-dynamic-system-prompt-sections`, thinking budget left at the CLI
default). The comments explaining *why the cheap setting is the dangerous one*
must move with the code: at thinking budget 0 the JRE fixture falsely marks 77.5 s
of journalism as advertisement.

### `advtt/chunking.py`
`estimate_tokens`, `plan_chunks`, `CONTEXT_SEGMENTS`. Moves verbatim, including
the docstring that says windows **tile rather than overlap** so every segment gets
exactly one authoritative vote, and the `W >= 3*context` invariant.

The comment that must survive translation into the new README: chunking is an
accuracy mechanism. On a 3919-segment episode, `gpt-5.5` given the whole
transcript found the right sponsor text and put it at segment 1245 instead of 445.
Anyone who sees "Gemini has a million-token context, why are we chunking" and
deletes this will regress the tool in a way the schema cannot catch.

### `advtt/validate.py`
`normalize_quote`, `_QUOTE_EQUIV`, `quote_matches`, `state_for`, `merge_spans`,
`validate_chunk`, `episode_gates`, `flags_from_spans`, `compute_stats`,
`segment_seconds`, `episode_duration`, and the constants block (adclass:67–105):
`AD_THRESHOLD`, `UNCERTAIN_THRESHOLD`, `MAX_SPAN_SECONDS`, `MAX_AD_FRACTION`,
`DEGENERATE_SPAN_FRACTION`, `DIALOGUE_Q_DENSITY`, `MIN_SEGMENTS`, `AD_KINDS`,
the `STATUS_*` strings, `SCHEMA_VERSION`, `PROMPT_VERSION`.

The whole eight-rung ladder moves as one unit. Splitting it is the obvious
refactor and is wrong: the rungs are ordered, and two of them are order-dependent
in a way the code comments record — the duration cap is re-applied *after* merging
because a span can first become over-long there, and merge takes the **min**
confidence because widening must never increase certainty.

`_QUOTE_EQUIV` is not incidental cleverness. It encodes the specific ways an ASR
word stream and a model quoting it disagree: intra-word hyphens (`last-minute` as
two tokens), spoken URLs (`better h-e-l-p dot com`), `slash`, dropped articles.
It is tuned against real Whisper output and must move unedited.

### `advtt/refine.py`
`_word_index_of`, `refine_span_edges`. Moves verbatim **including the long comment
about why the end edge is deliberately not trimmed** to `end_evidence`. That
asymmetry — precision helps at the start edge because landing late costs content;
trimming at the end edge removes coverage the model already granted — is the kind
of thing a reader will "fix" without the comment.

### `advtt/prompts.py`
`SYSTEM_PROMPT`, `build_user_prompt`, `_fmt_line`, `response_schema`,
`_gemini_schema`. Moves. `SPEAKER_TASK`, `GUEST_SEARCH_PROMPT`,
`ENTITY_SPELL_PROMPT` and their schemas do **not** — see §3.

### `advtt/classify.py`
The pure core, extracted from `classify_file` (adclass:2871) and `_run_pass`
(adclass:2694):

```python
def classify_segments(segments, provider, *, max_chunk_tokens=None,
                      episode_hint="", max_fraction=MAX_AD_FRACTION,
                      timeout=180, extension=None) -> dict
```

Returns the same result dict `classify_file` builds today, minus file I/O:
`status`, `provider`, `model`, `source_sha256`, `segment_count`, `duration_sec`,
`flags`, `spans`, `stats`, `chunks`, `incomplete_chunks`, `rejections`,
`retried_half_window`, `processing_time_sec`. Everything path-shaped stays out.

Also moving: `source_sha256` (hash over segments, not file bytes) and
`write_atomic`, both generic.

### `advtt/stt.py`
`stt.py` moves nearly whole: the `SttProvider` base, the MLX/Parakeet/OpenAI/
Gladia adapters, `read_audio_mono16k`, `get_audio_duration_seconds`,
`build_proportional_segments`, `is_junk`, `_PROVIDERS`, `_AUTO_ORDER`.

The documented return contract is the seam and does not change:
`text`, `segments[{start,end,text,words?}]`, `timing` (`model` | `proportional`),
`has_words`, optional `diarization{turns,provider,model}`.

Two consequences move with it and become AdVTT rules:
`timing: "proportional"` is character-count fiction, so it is never word-split and
never used for word-precise edges; and an adapter with `provides_diarization=True`
hands back turns the caller may adopt. AdVTT does not use diarization itself, but
must not drop the field — PodcastFetch does.

Video input is new work, not a move: AdVTT accepts `.mp4/.mkv/.webm` and shells
out to `ffmpeg` for a 16 kHz mono WAV, which the Gladia adapter already does
(`_prep_chunks`, stt:499). Reuse that helper rather than writing a second one.

### `advtt/eval.py`
`score_against_truth`, `evaluate`, `_print_eval`, `_truth_flags`, and `self_test`.
The metrics are format-generic and are the only objective statement of the ship
gate:

| Metric | Gate |
|---|---|
| `content_loss_sec` — content seconds falsely marked ad at the skip threshold | **≤ 5 s** |
| `ad_recall_sec` | ≥ 0.70 |
| `boundary_err_sec` | ≤ 3 s |

Time-weighted, because a 30 s segment matters more than a 3 s one. The
*fixtures* stay in PodcastFetch (they are hand-labelled ground truth about
specific episodes, listed as durable data). AdVTT ships a copy of one small
fixture for its own CI and points at the PodcastFetch set for the real gate.

## 3. What stays in PodcastFetch

- **The entire speaker layer.** `SPEAKER_TASK`, `validate_speakers`,
  `merge_speaker_rosters`, `load_speaker_ctx`, `assemble_speakers`,
  `_guest_search_fill`, `_entity_spell_search`, `_first_names_match`,
  `_needs_guest_search`, `_spk_tag_int`. It depends on `_diar.json`, on `hosts`
  from `sources.json`, and on the naming-escalation policy — all archive concerns.
- **Sidecar path resolution and caching**: `ads_path_for`, `truth_path_for`,
  `diar_path_for`, `metadata_path_for`, `_sibling_path`, `cache_hit`,
  `_speakers_cache_ok`, `save_result`, `load_json`. These encode
  `<name>_stt.json` → `<name>_ads.json` conventions.
- **Per-source policy** (`ad_detection` resolving feed → provider → default-on).
- **The dashboard, the fetcher, the server, retention.**
- `classify_file` itself, reduced to a thin wrapper: read `_stt.json`, hash,
  check cache, build speaker context, call `advtt.classify_segments(...)`, attach
  the `speakers` block, write `_ads.json`.

## 4. The hard part: the speaker task rides in the same model call

This is the one place where a clean extraction breaks something real. Today
`_run_pass` sends *one* request per chunk that asks for ad spans **and** speaker
attribution, and `response_schema(speakers=True)` merges both schemas. Extract the
ad half naively and PodcastFetch either doubles its API spend or loses the shared
context that makes attribution work.

The seam that solves it — the single most important API decision in this document
— is an **extension hook** on `classify_segments`:

```python
class TaskExtension:
    prompt_version_suffix: str     # folded into the effective prompt_version
    def system_fragment(self) -> str:            # appended to SYSTEM_PROMPT
    def schema_fragment(self) -> dict:           # merged into response_schema
    def user_fragment(self, segments, a, b) -> str   # per-chunk, e.g. speaker tags
    def collect(self, chunk_id, raw_obj, a, b):  # receives the raw response
    def finalize(self) -> dict                   # returns the block to attach
```

PodcastFetch passes a `SpeakerExtension`; AdVTT's own CLI passes `None`. When it
is `None` the assembled prompt must be **byte-identical** to today's speaker-blind
prompt — which is exactly what `--dump-prompt` on a fixture with no sibling
`_diar.json` already proves, and why that behaviour is called out in the existing
code as "that IS the regression check".

The extension must also be able to *veto* nothing and *reject* into the shared
`rejections` list, because the speaker layer already writes there.

Rejected alternatives:

- *Two calls.* Doubles cost, and the speaker adjudication loses the ad context that
  currently helps it (a sponsor read is a different speaker-role signal).
- *Keep the speaker task in AdVTT.* Drags `_diar.json`, `sources.json`, host
  rosters and web-search naming policy into a tool that has no archive.
- *Callback-on-raw only, no prompt fragments.* Insufficient: the schema and system
  prompt genuinely need to change for the extra task.

## 5. Package API

```python
from advtt import stt, classify_segments, providers
from advtt.captions import read_captions, write_webvtt, write_srt, write_media_events

result = classify_segments(segments, providers.make_provider("openai"))
write_media_events("ep.media-events.vtt", result, meta)
```

Public surface, deliberately small:

| Symbol | Purpose |
|---|---|
| `classify_segments(segments, provider, ...)` | the whole pipeline over segments |
| `providers.make_provider / PROVIDERS / available_providers` | backend selection |
| `stt.make_provider / transcribe` | the STT seam |
| `captions.read_captions(path)` | `.vtt`/`.srt` → segments + a source record |
| `captions.write_*` | the writers of `02-` and `03-` |
| `eval.evaluate / self_test` | the gate |
| constants: thresholds, `STATUS_*`, `SCHEMA_VERSION`, `PROMPT_VERSION` | shared vocabulary |

`classify_file`-style path logic is **not** in the public surface. Every consumer
files its own results.

## 6. How PodcastFetch re-consumes it without regressing

1. Vendor or pip-install `advtt`; keep `adclass.py` as the archive-facing module.
2. `adclass.PROMPT_VERSION` becomes `advtt.PROMPT_VERSION + speaker_suffix`. If the
   extraction changes neither, every cache entry still hits.
3. Replace the bodies of the moved functions with re-exports for one release, so
   any stale import in the fetcher, the server or the dashboard keeps working.
4. Regression protocol, in order, all offline or cheap:
   - `adclass.py --self-test` — ~40 assertions, no network, no cost. Must be green
     before anything else is run.
   - `adclass.py --dump-prompt <fixture>_stt.json` before and after; `diff` must be
     empty for both the speaker-blind and speaker-bearing cases.
   - `adclass.py --eval 'tests/fixtures/*/*_stt.json'` — `content_loss_sec ≤ 5`.
   - Reclassify the four fixtures with `--force` on `openai` and diff the resulting
     `_ads.json` against the committed ones, ignoring `processing_time_sec`.
5. Only then delete the moved bodies.

The failure that this protocol is designed to catch is not a crash. It is a
one-character prompt change that shifts a label on 3 % of episodes, which no
schema check and no unit test will see.

## 7. Things that will be tempting and are mistakes

- **"Make the ladder configurable."** Thresholds are already constants and that is
  the right amount of configurability. Turning rungs on and off gives every
  consumer a different definition of a validated span.
- **"Return spans, not the whole result dict."** `rejections`, `chunks` and
  `incomplete_chunks` are how a partial failure stays visible; drop them and a
  transient 503 caches as an ad-free episode forever. That bug has already
  happened once.
- **"Have the adapter retry the parse."** Rung 1 belongs to the caller.
- **"Normalise `_ads.json` into the new profile schema."** The sidecar and the
  interchange track are different layers (§23). Convert at the writer.
