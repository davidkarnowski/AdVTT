# 12 — Research evaluation and a plan for the standalone classifier

Date: 2026-09-06. Status: **approved 2026-09-06** (all nine recommendations in Part C accepted as written; see the approval note at the end). Written after reading `README.md`,
`01`–`10`, `07`/`08`/`09`, the track logs (0, E, I in full; the rest by
synthesis), `adclass.py` and `stt.py` in PodcastFetch, and the Gladia transcript
of the NotebookLM episode (`11-notebooklm-podcast-transcript.md`, made today).

Part A evaluates the research as it stands. Part B is the plan for building
the classifier routine as a standalone package. Part C lists the decisions
that need a yes or no before code is written.

---

## Part A — Evaluation of the research

### A.1 What is strong

1. **The measured invariants are real and well documented.** Three facts carry
   the design and all three come from experiments, not opinion: a whole-episode
   call placed the right sponsor text 800 segments away from where it was;
   Haiku 4.5 with thinking off falsely marked 77.5 s of JRE journalism; and the
   dialogue rung exists because a guest's own-foundation pitch fooled the
   prompt. `0-local-grounding.md` and the PodcastFetch README preserve these
   with numbers and dates.
2. **`08-` is a genuine synthesis, not a survey.** It states every reversal
   from `01`–`06` in one table with the evidence that forced it, resolves the
   thirteen open questions of `06-` explicitly, and gives each phase an exit
   criterion. The reasoning chain from "players skip on chapters" to "the
   record is the product" is sound and the podcast (A.4) shows it can be
   retold coherently by a third party.
3. **The false-positive asymmetry is applied consistently.** It shows up in
   the ladder (halve, do not drop), the merge rule (min confidence), the
   boundary rule (exclude a half-and-half cue), the player default (auto-skip
   off), the metric (`content_loss_sec`), and now the legal posture (Fox v.
   Dish). That consistency is the project's best asset.
4. **The evaluation section is honest about its own weakness.** Four fixtures
   from two shows, used to tune the prompt, are named as a contaminated dev
   set with a ≤75% bound on the violation rate. Few projects say this out loud.
5. **The extraction plan (`01-`) is code-level.** It names symbols, explains
   which comments must travel with which functions, and states the regression
   protocol. It is still correct against today's `adclass.py` (symbols
   verified 2026-09-06; line numbers have drifted by under 20 lines).

### A.2 What is weak or missing

1. **`08-` is a programme, and the classifier core is a small part of it.**
   Eight exporters, an acoustic channel, a public benchmark, a distilled
   proposer, packaging and a spec are all in one document with one trajectory.
   The part the user asked for now, a standalone classifier routine, is
   roughly §5.2 plus the extraction in `01-`. Part B carves that out.
2. **Two of the headline pipeline changes are unmeasured on this project's
   data** and both change the prompt or schema: quote-anchored spans and the
   reasoning-on ∩ reasoning-off ensemble. `08-` sequences the experiments
   *before* extraction (Phase 0). That puts experimental churn into
   `adclass.py`, the file whose byte stability the whole regression bar
   depends on. Part B reverses the order: extract the legacy behaviour first,
   run the experiments on the extracted package behind a `prompt_version`
   bump.
3. **Model-specific detail has already drifted.** Verified against the current
   Claude API reference today:
   - `budget_tokens` is rejected with a 400 on Sonnet 5 and Opus 5; thinking is
     adaptive by default and depth is `output_config.effort`
     (`low`…`max`). Haiku 4.5 still uses `budget_tokens`. `08-` §5.2 has this
     roughly right but the capability map must be per-model, not per-vendor.
   - The Citations feature `08-` proposes for validated block indices
     (E-S37) is **incompatible with structured outputs** (`output_config.format`
     returns 400 when both are set). Quote anchoring on Claude must therefore
     be schema-based with quotes resolved in code, which is what the ladder
     already does. The citations idea is dropped from the plan.
   - `stop_reason: "refusal"` is a first-class outcome on the 5-family and
     must be a distinct rejection reason, as E impl. 9 already asks.
   - The `claude` CLI (2.1.263 installed) now has `--json-schema` and
     `--effort`. The `ClaudeCLIProvider` docstring's two stated weaknesses (no
     schema enforcement, thinking only via an env var) no longer hold. This
     is the single most useful change for this project's present situation
     (A.3).
4. **The STT recommendation ignores what is available.** `08-` §5.1 ranks
   Deepgram, Voxtral and AssemblyAI above Gladia on price. Gladia is the only
   cloud STT with a working key today, and it transcribed the 39-minute
   podcast in 43 s with word timings and diarization through the existing
   provider without modification. Price ranking is right for the public tool;
   for building and testing the classifier now, Gladia is the default.
5. **Fixture privacy is not resolved for the standalone repo.** Track G says
   transcripts never enter the public repo; the four fixtures *are*
   transcripts of copyrighted episodes. `01-` §2 says "AdVTT ships a copy of
   one small fixture", which conflicts. Part B resolves it: fixtures are
   referenced from PodcastFetch by path, the standalone repo ships a synthetic
   fixture and a recorded-response replay store.
6. **Naming collision.** `08-` §9 says Phase 0 exits with decisions recorded
   in `09-decisions.md`; `09-` is the project brief. Part C of this document
   is the decisions record.
7. **The pre-spike documents are still live text.** `README.md` describes the
   `01`–`06` design at length with a status banner on top. Once Part B is
   approved the README should be rewritten around the record and the package,
   and `01`–`06` moved to an `archive/` folder with a one-line pointer each.
8. **Small factual gap in the research on the CLI adapter's economics.** The
   ~26k-token Claude Code system prompt tax and the `--exclude-dynamic-system-prompt-sections`
   trick are measured and documented, but nobody has measured what
   `--json-schema` does to output length or accuracy. That is a Part B
   experiment.

### A.3 Environment facts that shape the plan (checked today)

| Fact | Consequence |
|---|---|
| No `ANTHROPIC_API_KEY` in the environment or either `.env`; no `ant` CLI installed | The Messages-API adapter stays unavailable; the CLI adapter is the live Anthropic path |
| `claude` CLI 2.1.263 logged in; supports `--json-schema`, `--effort`, `--model`, `--tools ""`, `--exclude-dynamic-system-prompt-sections`, `--output-format json` | Structured output and effort control without an API key |
| Gladia was the only paid STT key available for this work; no OpenAI or Gemini budget | Gladia is the STT default; OpenAI and Gemini adapters move verbatim but are exercised only through the replay store |
| `ffmpeg`/`ffprobe` on PATH; PodcastFetch venv has `mlx-whisper`, `torch`, `openai` SDK; Python 3.14 | Local STT is possible; the new package must not depend on any of it in core |
| AdVTT is not a git repository | Decision C.7 |
| PodcastFetch is clean at `74692de` apart from generated files | Safe to read from; nothing in it needs to change for Part B |

### A.4 The NotebookLM episode as a research artefact

`11-notebooklm-podcast-transcript.md` (39.3 min, two speakers, 7,900 words,
Gladia `solaria-1` with diarization) is a faithful retelling of `08-` and
`09-`. Every number it cites checks against the documents: the 5 s gate, the
77.5 s Haiku failure, the whole-episode gpt-5.5 misplacement, MinusPod's
benchmark and differential download, Fox v. Dish, the rule of three and
sixty episodes, chapters and EDL over WebVTT. It invents nothing material.
Two small liberties: it describes the 5 s gate as something that "fails the
build", which presupposes CI that does not exist yet, and it attributes the
rule of three to "Poisson statistics", which is a fair approximation. Its
value is as an onboarding and communication artefact, not as evidence; it is
filed in `Research/` for that reason and is not cited by `08-`.

The transcription itself was a useful test of the STT seam: a 75 MB stereo AAC
file went to Gladia unchanged (under the 80 MB transcode threshold), returned
906 utterances with word timings and 426 speaker turns, and mapped onto the
provider's documented return shape without any edits.

---

## Part B — Plan: the standalone classifier routine

### B.1 Scope

**In:** a Python package `advtt` whose core is
`classify_segments(segments, provider, ...) -> result`, with the provider
seam, the STT seam, a caption-file reader, the canonical record writer, a
CLI, the self-test, the eval harness, and a recorded-response replay store.
Anthropic models through the `claude` CLI now, through the Messages API when a
key exists, with the abstraction kept so OpenAI, Gemini, Ollama and oMLX
adapters continue to compile and can be tested later.

**Out (later phases of `08-`):** the seven delivery exporters beyond the JSON
record, the acoustic channel, the ≥60-episode test set and PodAd-Bench, the
distilled proposer, the reference player, PodcastFetch's re-consumption
(although the hook for it is built in B.4 so nothing has to be redone).

### B.2 Principles carried over (not up for re-decision)

From `README.md` "Design constraints" and PodcastFetch's invariants: the
asymmetry; the ladder is the accuracy mechanism and moves as one unit; chunking
is an accuracy mechanism; no silent local→cloud fallback; adapters are thin
and stdlib-only; never modify the transcript of record; caches key on a
segment hash plus `prompt_version`; the end edge is not trimmed to the quote;
`rejections`, `chunks` and `incomplete_chunks` stay in the result so partial
failure is never cached as clean.

### B.3 Package layout

```text
AdVTT/
├── pyproject.toml            Hatchling, PEP 621, requires-python >= 3.11, no hard deps
├── src/advtt/
│   ├── __init__.py           classify_segments, PROMPT_VERSION, STATUS_*, thresholds
│   ├── providers/
│   │   ├── base.py           AdProvider, ProviderError, capability map, _http_json
│   │   ├── claude_cli.py     print-mode adapter (--json-schema, --effort)
│   │   ├── claude_api.py     Messages API adapter (stdlib urllib)
│   │   ├── openai.py, gemini.py, ollama.py, omlx.py   moved verbatim
│   │   ├── replay.py         ReplayProvider: recorded responses, no network
│   │   └── registry.py       PROVIDERS, make_provider, available_providers
│   ├── prompts.py            SYSTEM_PROMPT, build_user_prompt, response_schema
│   ├── chunking.py           estimate_tokens, plan_chunks, CONTEXT_SEGMENTS
│   ├── validate.py           the ladder: normalize_quote … episode_gates, constants
│   ├── refine.py             _word_index_of, refine_span_edges
│   ├── classify.py           classify_segments, _run_pass, TaskExtension, source_sha256
│   ├── stt/                  SttProvider seam: gladia, whisper-mlx, parakeet-mlx, openai
│   ├── captions.py           read_captions(.vtt/.srt) -> segments (new, small)
│   ├── record.py             legacy result -> advtt/1.0 canonical record (new)
│   ├── evaluate.py           score_against_truth, evaluate, self_test
│   └── cli.py                advtt <media|--stt|--captions> …
└── tests/
    ├── test_ladder.py        the ~40 self-test assertions as pytest
    ├── test_prompt_bytes.py  --dump-prompt golden files for the legacy prompt
    ├── fixtures/synthetic/   one hand-written ad-free + one with-ads transcript
    └── replay/               sha256(prompt_version|model_id|chunk_text).json
```

Source anchors in `adclass.py` (2026-09-06): providers 271–1204, schema
112–197, prompt 1206–1374 and 1501–1586, chunking 1587–1634, ladder
1636–1857, `_run_pass` 2694–2779, refinement 2780–2870, `classify_file`
2871–3027, eval and self-test 3028–3583. `stt.py` moves nearly whole.

### B.4 Work packages, in order

Each package has an exit criterion. Estimates are working days for one
person and assume nothing else changes in PodcastFetch.

**WP0 — Scaffold (0.5 d).** `pyproject.toml`, `src/advtt`, `advtt --version`,
`advtt --self-test` wired to an empty suite, `.env` loading for `ADVTT_*` and
provider keys with the same precedence PodcastFetch uses, `LICENSE`
(Apache-2.0, decision C.4), git init (C.7).
*Exit:* `uv run advtt --version` works from a clean checkout.

**WP1 — Verbatim extraction (2–3 d).** Move the modules in B.3 with the
comments `01-` says must travel. Build `TaskExtension` exactly as `01-` §4
specifies (system fragment, schema fragment, per-chunk user fragment,
collect, finalize, `prompt_version_suffix`); `extension=None` must produce a
prompt byte-identical to today's speaker-blind prompt. Add `captions.py`.
Keep `PROMPT_VERSION = "2026-08-g"`.
*Exit, all offline:* (a) `advtt --dump-prompt` on each of the four fixtures
diffs empty against `adclass.py --dump-prompt`; (b) the ladder suite is green;
(c) `classify_segments` fed the same raw model responses produces the same
`spans`, `flags`, `stats`, `rejections` as `classify_file` (tested through the
replay provider on the synthetic fixtures and on responses captured in WP2).

**WP2 — Anthropic adapters brought to the current API (1–2 d).**
- `claude_cli.py`: pass `--json-schema <schema>` (schema enforcement at last),
  `--effort <level>` from a per-model capability map, `--model`, keep
  `--tools ""` and `--exclude-dynamic-system-prompt-sections`; record
  `total_cost_usd`, tokens and wall time in the chunk record as today; detect
  a refusal or free-text envelope as its own rejection reason.
- `claude_api.py`: `output_config.format` for the schema; thinking omitted or
  `{type: adaptive}` plus `output_config.effort` on the 5-family; `budget_tokens`
  only when the capability map says the model needs it (Haiku 4.5); handle
  `stop_reason` `refusal` and `max_tokens`; stdlib `urllib` only (decision
  C.1); unavailable without a key, never crashes.
- Capability map: `{model: {reasoning: "effort"|"budget"|"none", schema: bool,
  cache_floor_tokens, price_in, price_out}}`, one table, used by both adapters
  and by the eval report.
- Replay capture: every live call's `raw_text` is written to `tests/replay/`
  keyed by `sha256(prompt_version|model_id|chunk_text)` so the same run can be
  replayed offline forever.
*Exit:* `advtt --eval` on the four PodcastFetch fixtures through `claude-cli`
passes the gate (`content_loss_sec ≤ 5`, `ad_recall_sec ≥ 0.70`) at the
default effort; cost and latency per chunk recorded in a table in track K;
the run's responses are in the replay store and `advtt --eval --provider
replay` reproduces the numbers with no network.

**WP3 — Canonical record and CLI (2 d).**
- `record.py`: build the `advtt/1.0` record of `08-` §4.1 from the legacy
  result. Media binding via `ffprobe` duration and a SHA-256 of the file;
  `stt` and `classifier` provenance including the resolved model id and
  `prompt_version`; per-span mapping from legacy fields:
  `preroll|midroll|postroll` → `category: sponsor` with `position`;
  `house` → `category: selfpromo`; `section` → `category: sponsor`,
  `form: sponsorship_credit`; `state: ad` → `action: skip`, otherwise
  `action: none`; `selfpromo` never `skip` by default; `confidence` carried
  as the model's number and **labelled** `verbalised` until WP4 gives an
  agreement score; `edges.mode` = `word` when `start_exact` differs from
  `start`, else `segment`; evidence quotes and chunk records go to
  `<stem>.analysis.json`, never to the shareable record (track G).
- `cli.py`: `advtt EP.mp3` (STT → classify → record), `advtt --stt X_stt.json`,
  `advtt --captions X.vtt [--media EP.mp3]`; `--provider`, `--model`,
  `--effort`, `--offline` (refuses every cloud provider and prints the hosts
  it would have contacted), `--dump-prompt`, `--self-test`, `--eval`,
  `--list-providers`, `--force`, `--json` to stdout.
- STT default: `gladia` when its key is present, else `whisper-mlx` if
  importable, else a clear error. No auto-fallback across the local/cloud
  line.
*Exit:* `advtt Research/AI_hunts_for_host-read_ads.m4a` writes a record and
an analysis file end to end (this episode has no ads; the record must say so
with `status: ok` and zero spans, the empty-is-valid rung); a JSON Schema for
the record lives in `src/advtt/schema/advtt-1.0.json` and the writer's output
validates against it in the test suite.

**WP4 — Experiments on the extracted core (3–5 d, mostly wall-clock).**
These are `08-`'s Phase 0 experiments (a) to (c) plus two from track E, run on
the package rather than on `adclass.py`. Each is a candidate `prompt_version`
or a provider option, scored with `advtt --eval` on the four-fixture dev set
plus two new **no-ad control** episodes transcribed with Gladia (candidates:
Hacker Public Radio, which is ad-free and CC BY-SA). Results go in
`research-log/K-experiments.md` with the incremental-writing rule.

| # | Experiment | Change under test | Adopt if |
|---|---|---|---|
| K1 | Effort sweep | `claude-opus-5` and `claude-sonnet-5` at effort low/medium/high; `claude-haiku-4-5` at budget 0/1024/4000 | Reproduces or refutes the 77.5 s effect off Haiku; picks the working default (C.2) |
| K2 | `--json-schema` on the CLI | schema flag on vs the in-band schema text | No accuracy loss; fewer parse rejections; output tokens not higher |
| K3 | Quote-anchored spans | schema asks `start_quote`/`end_quote` + index hint; code resolves quotes with the existing matcher; unresolved spans dropped | Resolution rate ≥ 95% on dev set; `boundary_err_sec` not worse; `content_loss_sec` ≤ 5 on every episode including controls |
| K4 | Intersection ensemble | reasoning-on ∩ reasoning-off (same model, two efforts), agreement recorded | `content_loss_sec` falls or holds and `ad_recall_sec` stays ≥ 0.70; cost within 2× single pass |
| K5 | Chunk size | 3k vs 6k token windows, same ±12 context | Recall up with no precision loss, or keep 6k |

*Exit:* Part C decisions C.2, C.5 and C.6 answered with numbers; if any of
K3–K5 is adopted, `PROMPT_VERSION` bumps and the legacy prompt stays selectable
as `--prompt-version 2026-08-g` so PodcastFetch's cache is untouched until it
chooses to reclassify.

**WP5 — Hand-off to PodcastFetch (not in this plan).** `08-` Phase 5. The
`TaskExtension` hook from WP1 and the replay store from WP2 are the only
prerequisites, and both are built here.

### B.5 Cost and risk

- **Money.** Live calls happen only in WP2's exit run and WP4. Through the CLI
  the measured cost is $0.05–0.22 per chunk on Haiku 4.5 with thinking; the
  four fixtures are about ten chunks. K1 is the expensive item: roughly 90
  chunk calls across models and settings. Budget the whole of WP4 at under
  $40 of API-equivalent usage; the CLI bills to whatever the logged-in account
  uses, so confirm that is acceptable (C.3). Everything else replays offline.
- **Non-determinism.** Byte-identical `_ads.json` across *live* runs was never
  achievable (the model is not deterministic); `01-` §6 step 4 is honest only
  for identical raw responses. The replay store makes that the tested
  property, which is the right one.
- **Quote resolution on other STT backends** (`08-` §11): Gladia's word stream
  differs from Whisper's; K3 must report resolution rate per backend before
  "drop unresolved" becomes the rule. Until then the legacy "halve" rule
  stands.
- **The CLI tax.** ~26k cached system-prompt tokens per call remain. For
  archive-scale work the Messages API adapter with batch pricing is the
  cheaper path; it is built in WP2 and waits for a key.
- **Model churn.** The capability map and the replay store exist for this;
  the canary of `08-` §6 is a later phase.

### B.6 Timeline

WP0–WP3 are about six working days of implementation and can be done
sequentially with no external dependency. WP4 is three to five days
dominated by model latency and can start as soon as WP2's replay store
exists. Nothing in Part B blocks on the decisions in Part C except C.1, C.4
and C.7, which affect WP0.

---

## Part C — Decisions requested

Recommendations first; each needs a yes, a no, or an alternative.

| # | Decision | Recommendation | Why |
|---|---|---|---|
| C.1 | Anthropic adapter: stdlib `urllib` or the `anthropic` SDK? | **stdlib**, SDK as an optional extra later | Invariant 5 (thin, stdlib-only adapters) is what made OMLX and Gemini one-class additions; zero hard deps is `08-` §7's packaging rule. The API reference's default of using the SDK is noted and overridden by the project rule. |
| C.2 | Default Anthropic model and effort | Reference: `claude-opus-5`, effort high. Working default: chosen by K1 between `claude-sonnet-5` and Opus at lower effort. Cheap ensemble member: `claude-haiku-4-5` or Sonnet at effort low | Opus 5 is the current general default; Sonnet 5 is `08-`'s provisional quality tier at $2/$10; the dev set decides, not the doc |
| C.3 | Live-call budget for WP2 and WP4 | ≤ $40 equivalent through the logged-in CLI account; no OpenAI or Gemini calls | The user declared those providers unavailable; their adapters are exercised only through replay |
| C.4 | Licence | Apache-2.0 | `08-` §3, track G |
| C.5 | Prompt-changing features (quote anchoring, ensemble) | Build behind a `prompt_version` bump only after WP4 measures them; legacy prompt stays selectable | Protects PodcastFetch's 99 cached classifications |
| C.6 | Experiment order | Extract first, then experiment on the package | Reverses `08-` §9 Phase 0; avoids churn in `adclass.py` |
| C.7 | Repository | `git init` in `AdVTT`, `src/` layout, fixtures **not** copied; `ADVTT_FIXTURES` points at `PodcastFetch/tests/fixtures`; a synthetic fixture and the replay store ship | Track G: transcripts never enter a public repo |
| C.8 | STT default for development | `gladia` (key present), `whisper-mlx` as the local alternative; Parakeet, Deepgram and others as later adapters | A.2 item 4 |
| C.9 | Documentation | On approval, rewrite `README.md` around the package and record; move `01`–`06` to `Research/archive/` with pointers; this file becomes the decisions record `08-` asks for | A.2 items 6 and 7 |

### Progress (2026-09-06)

| Package | Status |
|---|---|
| WP0 scaffold | done: `pyproject.toml`, `src/advtt`, Apache-2.0, git initialised (no commits made; the user commits) |
| WP1 extraction | done: `--dump-prompt` byte-identical on all four fixtures; self-test and 11 pytest tests green; `TaskExtension` built with `line_tag`/`header_lines` hooks (richer than `01-` §4 because the speaker task tags every line) |
| WP2 adapters | done: `claude-cli` uses `--json-schema`/`--effort`; `claude` API adapter on the current Messages API, dormant; capability map; replay store. Exit run: four fixtures via Sonnet 5, all gates pass with zero content loss (track K, K0d); offline replay reproduces it (K0e) |
| WP3 record + CLI | first cut done: `advtt/1.0` record and JSON Schema, `analysis.json`, CLI with `--stt`/`--captions`/media, `--offline`, `--record-replay`. Exit run done: the NotebookLM episode (Gladia transcript, media-bound record) classifies `ok` with zero spans (K0f) and is now the first no-ad control fixture. Remaining: schema validation with a real JSON-Schema validator once a dev dependency is acceptable |
| WP4 experiments | K0 baselines logged; K1–K5 not started |

### Addendum 2026-09-06 (overnight run): two more pillars

The user asked, mid-run, that (a) **agentic controllability** be a pillar of
the design and (b) the code be documented so that agents as well as humans
can evaluate it. Recorded as decisions:

| # | Decision | Implementation |
|---|---|---|
| C.10 | Agentic controllability is a design pillar | `advtt --describe`, `--dry-run`, `--json`, `--log-json`, stable exit codes, `--offline`, the replay store, pure library functions; see `docs/architecture.md` §6 and `CLAUDE.md` |
| C.11 | Documentation serves agents and humans equally | `CLAUDE.md` (operational guide), `docs/architecture.md` (module map, contracts, how to evaluate), module docstrings carrying the measured reason for every rule |

Exporters (08 §4.2, previously Phase 2) were also built during the overnight
run because they are pure functions of the record and were idle time away.

### Approval record

2026-09-06: the user accepted every recommendation in the table above and
asked that work proceed "with your recommendations for these issues at this
time and the direction of our notes and research".

One clarification changes the reading of C.3. The reason inference goes
through the `claude` CLI is funding: there is no budget for API access from
any provider right now. Consequences:

- **No paid API calls in WP2 or WP4.** Every live model call goes through the
  logged-in `claude` CLI on the user's subscription. The "$40 equivalent" in
  B.5 is a size guide for how many CLI calls K1–K5 may make, not a spending
  authorisation.
- The Messages-API adapter (`claude_api.py`) is built and tested against the
  replay store only; it stays dormant until a key exists.
- OpenAI, Gemini, Ollama and oMLX adapters move verbatim and are exercised
  only through the replay provider; oMLX and Ollama can be tried live later
  because they are local and free.
- Gladia is the one paid external call in the pipeline (STT). It is used for
  the two no-ad control episodes in WP4 and otherwise avoided; local
  `whisper-mlx` from the PodcastFetch venv is the fallback for development.
