# AdVTT — guide for agents working in this repository

Read this first. It tells you what the tool is, what must not change, how to
run and evaluate it, and where results go. Humans: the same facts are in
`README.md` in prose; this file is the operational version.

## What this is

A Python package (`src/advtt/`) that finds advertising and sponsorship spans in
a transcript of finished audio and writes a canonical JSON record
(`<stem>.advtt.json`, profile `advtt/1.0`) plus exporters (EDL, ffmetadata
and JSON chapters, SponsorBlock JSON, WebVTT, SRT twin, Audacity labels, RTTM,
full-transcript captions in VTT and SRT with the ad cues marked). It classifies; it produces no derivative media. Extracted
from PodcastFetch (a private sibling project; its `adclass.py`), which will
re-consume it. Scripts that need it read the `PODCASTFETCH_ROOT` environment
variable. Plan and decisions: `Research/12-*.md`. Evidence:
`Research/08-*.md` and `Research/research-log/`.

## Design pillars (in priority order)

1. **False-positive asymmetry.** Silently skipping journalism is worse than
   missing an ad. Every default follows: `action: skip` only above the ad
   threshold, `selfpromo` never auto-skipped, rejected episodes produce no
   marks, evidence failures halve confidence instead of dropping spans, the
   ship gate is `content_loss_sec <= 5` per episode.
2. **Measured invariants over intuition.** Chunking and thinking are accuracy
   mechanisms (see `README.md`). Do not remove chunking because the context
   window is large; do not disable thinking to save money.
3. **Agentic controllability.** Everything an agent needs is machine-readable
   and deterministic: `advtt --describe` (capabilities as JSON), `--dry-run`
   (plan and cost, no calls), `--json` output, `--log-json` (JSON Lines
   events), stable exit codes (0/1/2/3/4/5/6, listed in `cli.py`), the replay
   store (`--record-replay`, `--provider replay`) for reruns with no network,
   `--offline` that refuses network providers, and a library API
   (`classify_segments`, `build_record`, `exporters.render`).
4. **Provenance and two tiers.** The record carries STT and classifier
   identity, `prompt_version`, thresholds and the media fingerprint; evidence
   quotes and chunk records go only to the local `analysis.json`.
5. **Thin, stdlib-only adapters.** One class per backend, `urllib` or
   `subprocess`, no SDKs; `make_provider` never falls back local -> cloud.

## Things that must not change without a `prompt_version` bump

`prompts.py` (system prompt, schema, user prompt layout), `chunking.py`,
`validate.py` (the ladder and constants), `refine.py`. The regression check is
byte equality of `advtt --dump-prompt <fixture> --provider claude-cli` against
`adclass.py --dump-prompt <fixture> --provider claude-cli` in PodcastFetch.
`PROMPT_VERSION` lives in `validate.py`; bumping it invalidates 99 cached
classifications in PodcastFetch, so it is a deliberate decision. Ladder-only
changes bump `LADDER_VERSION` instead (results record
`PROMPT_VERSION+LADDER_VERSION`; replay keys use the prompt version alone,
so recorded responses stay valid and a ladder change can be measured offline
by replaying them, as K3 did).

## Commands

```bash
PYTHONPATH=src python3 -m advtt.cli --self-test            # ladder, offline, free
PYTHONPATH=src uvx --python 3.14 pytest -q tests           # full offline suite
PYTHONPATH=src python3 -m advtt.cli --describe             # capabilities JSON
PYTHONPATH=src python3 -m advtt.cli --dry-run --stt X_stt.json --model claude-sonnet-5
PYTHONPATH=src python3 -m advtt.cli --stt X_stt.json --provider claude-cli --model claude-sonnet-5 \
    --record-replay --export all --log-json run.jsonl --out-dir eval-out/run
PYTHONPATH=src python3 -m advtt.cli --eval '<dir>/*_stt.json' --classify --provider claude-cli \
    --model claude-opus-5 --record-replay --out-dir eval-out/opus5
PYTHONPATH=src python3 -m advtt.cli --eval '<dir>/*_stt.json' --classify --provider replay \
    --model claude-sonnet-5 --out-dir eval-out/replay --offline
python3 scripts/compare_models.py --stt-dirs <dirs> --runs eval-out/*     # per-model table
python3 scripts/consensus.py --stt-dirs <dirs> --runs eval-out/* --out-dir data/truth-drafts
```

Live model calls go through the `claude` CLI on the user's subscription
(there is no API budget). Do not call OpenAI or Gemini. Gladia (STT) is paid;
use `--stt-provider whisper-mlx` with a python that has `mlx-whisper`
installed (the PodcastFetch venv, `$PODCASTFETCH_ROOT/.venv/bin/python`):
`PYTHONPATH=src "$PODCASTFETCH_ROOT/.venv/bin/python" -m advtt.cli EP.mp3 --stt-provider whisper-mlx`.

## Where things are

| What | Where |
|---|---|
| Hand-labelled dev fixtures (4, private, never in this repo) | `$PODCASTFETCH_ROOT/tests/fixtures/{pdb,jre}` |
| Ad-free control fixture | `tests/fixtures/notebooklm/` |
| Synthetic fixtures | `tests/fixtures/synthetic/` |
| New episodes (audio, transcripts; gitignored) | `data/episodes/`, `data/fixtures/` |
| Fixture manifest (committed, labels-only) | `tests/fixtures/manifest.json` |
| Replay store | `tests/replay/` |
| Eval predictions | `eval-out/<run>/` (gitignored) |
| Experiment results | `Research/research-log/K-experiments.md` |
| Work log (private, gitignored) | `Research/local/PROGRESS.md` |
| Pre-release checklist and backlog | `docs/release-checklist.md`, `docs/backlog.md` |

## Conventions

- Write incrementally: create the log or result file first, append per step.
- Never write into the PodcastFetch tree. Never put transcripts of copyrighted
  episodes into git. `data/` and `eval-out/` are gitignored on purpose.
- Commits end with exactly one `Co-Authored-By: Claude <model> <noreply@anthropic.com>`
  trailer and never a session link. The GitHub repo is public (since
  2026-09-07, single-commit snapshot); never commit transcripts, audio, keys,
  private paths or session identifiers.
- Docstrings carry the measured reason for every non-obvious rule. Keep them
  when moving code; add one when adding a rule.
