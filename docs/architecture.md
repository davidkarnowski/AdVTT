# AdVTT architecture

For humans and agents who need to evaluate this code. Every claim here is
checkable with a command listed in `CLAUDE.md`.

## 1. Data flow

```text
input ──► segments ──► chunk plan ──► provider.complete_json (per chunk) ──► validate_chunk
                                                                              │
              refine_span_edges ◄── episode_gates ◄── merge across seams ◄────┘
                     │
        legacy result dict {status, flags, spans, stats, chunks, rejections, incomplete_chunks}
                     │
        build_record ──► <stem>.advtt.json (shareable)      build_analysis ──► <stem>.analysis.json (local)
                     │
        exporters.render ──► .edl .ffmeta .chapters.json .sponsorblock.json .ads.vtt .ads.srt .labels.txt .rttm
                     (+ segments) ──► .captions.vtt .captions.srt   full transcript, ad cues marked
```

Inputs: a media file (STT seam), a PodcastFetch `_stt.json`, or a caption
file. All become `segments = [{start, end, text, words?}]`. `words` is
`[{w, s, e}]` and is what makes word-precise start edges possible; captions
have none, so their edges are cue boundaries.

## 2. Module map

| Module | Responsibility | Origin | Change policy |
|---|---|---|---|
| `prompts.py` | system prompt, response schema, user prompt layout | verbatim from `adclass.py` | only with a `PROMPT_VERSION` bump |
| `chunking.py` | tiled windows with read-only context | verbatim | same |
| `validate.py` | constants and the eight-rung ladder | verbatim | same; rungs are ordered and move together |
| `refine.py` | word-precise start edge; end edge never trimmed | verbatim | same |
| `classify.py` | `classify_segments`, `_run_pass`, `TaskExtension` | adapted | free, but the no-extension prompt must stay byte-identical |
| `providers/base.py` | `AdProvider` contract, HTTP helpers, JSON extraction | verbatim | free |
| `providers/claude_cli.py` | live Anthropic path via `claude -p` | adapted | free |
| `providers/claude_api.py` | Messages API, dormant without key | adapted | free |
| `providers/openai.py`, `gemini.py`, `ollama.py`, `omlx.py` | other backends | verbatim | untested here; keep compiling |
| `providers/replay.py` | recorded responses; deterministic reruns | new | free |
| `providers/capabilities.py` | per-model reasoning control, cache floor, prices | new | update as models change |
| `stt.py` | STT seam: gladia, whisper-mlx, parakeet-mlx, openai | verbatim | free |
| `captions.py` | .vtt/.srt to segments | new | free |
| `record.py` | legacy result to `advtt/1.0` record; media fingerprint | new | schema changes bump the profile |
| `exporters.py` | record to player formats | new | free; keep the hard-won rules in its docstring |
| `evaluate.py` | metrics, `evaluate`, `self_test` | verbatim metrics | metric definitions are published; changes are versioned |
| `events.py` | JSON Lines event log | new | additive fields only |
| `cli.py` | the `advtt` command | new | exit codes and `--describe` keys are a contract |
| `config.py`, `io.py` | env loading, hashing, atomic writes | new / verbatim | free |

## 3. The provider contract

`complete_json(system, user, schema, timeout) -> (dict, meta)`. `meta` always
has `raw_text`; on failure `dict` is `{}` and `meta["parse_error"]` says why.
The adapter never retries a parse and never decides what a bad answer means:
that is ladder rung 1, in `validate_chunk`. `ensure_ready(probe=False)` never
touches the network. `make_provider` raises rather than substituting a cloud
provider for a local one.

## 4. The record

`advtt/1.0` (schema in `src/advtt/schema/advtt-1.0.json`). Per span:
`category` (SponsorBlock/Jellyfin ids), `form` (host_read | produced |
sponsorship_credit), `position`, `delivery`, `action` (none | prompt | skip |
mute), `state`, `confidence` with `confidence_source`, `edges.mode`,
`provenance`. `action` is policy, computed in `record._action_for`, and is the
only field a player should branch on for skipping. The record is bound to the
rendition by duration, byte count and SHA-256 because dynamic ad insertion
produces per-download files.

## 5. How to evaluate this code

1. `advtt --self-test` and `pytest`: the ladder and the seams, offline.
2. `--dump-prompt` diff against PodcastFetch: proves the prompt did not move.
3. `--eval` on the dev fixtures with `--provider replay`: proves the pipeline
   reproduces recorded model behaviour with no network.
4. `--eval --classify` live, with `--record-replay`: measures the model; the
   numbers go in `Research/research-log/K-experiments.md` with cost and wall
   time from the chunk records.
5. Read `analysis.json` for any surprising span: `rejections` lists every
   rung that fired and why; `chunks` shows tokens, thinking, cost and wall
   time per call.

The dev set is four episodes from two shows that were also used to tune the
prompt; treat every number from it as necessary, not sufficient. The
no-ad control (`tests/fixtures/notebooklm/`) checks the empty-is-valid rung
against a transcript that talks about ads constantly.

## 6. Agentic controllability, concretely

| Need | Mechanism |
|---|---|
| Discover what the tool can do | `advtt --describe` (JSON: providers with availability, models, effort levels, exporters, schema path, exit codes, events) |
| Predict cost and side effects before acting | `--dry-run` (chunk windows, token and cost estimate, output paths, whether the network would be used) |
| Act without ambiguity | `--json` output, stable exit codes, `--force` required to overwrite, `--out-dir` |
| Observe while running | `--log-json` JSON Lines: `chunk.done` carries wall, tokens, thinking tokens, cost, parse errors |
| Reproduce | `--record-replay` then `--provider replay`; keys are `sha256(prompt_version | model | prompt)` |
| Stay inside a boundary | `--offline` refuses cloud providers and STT uploads; `data/` and `eval-out/` are gitignored |
| Compose | `classify_segments`, `build_record`, `exporters.render` are pure functions of their inputs |
