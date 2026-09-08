# Contributing

AdVTT is a small research-stage project by a single author, accelerated by
Claude Code. Issues and pull requests are welcome; please read this first.

## Running the tests

Everything runs offline, with no keys and no model calls:

```bash
PYTHONPATH=src python3 -m advtt.cli --self-test     # the validation ladder
PYTHONPATH=src pytest -q tests                      # the full suite
```

There is no hosted CI; run both before opening a pull request and say so in
the description.

## Rules that protect measured behaviour

- `src/advtt/prompts.py`, `chunking.py`, `validate.py` and `refine.py`
  encode measured accuracy mechanisms (see README, "How it works"). A change
  to any of them is a `PROMPT_VERSION` bump, or a `LADDER_VERSION` bump when
  only the validation ladder changes. Say which in the pull request and
  include the measurement.
- Do not remove chunking because the context window is large, and do not
  disable thinking to save cost. Both were measured to matter.
- The false-positive asymmetry is the first design pillar: a change that
  marks more content as advertising needs a stronger case than one that
  misses an ad.

## What never goes into the repository

- Transcripts, audio or video of copyrighted episodes, in any form. The
  hand-labelled fixtures live outside this repository for that reason;
  `data/` and `eval-out/` are gitignored on purpose.
- Keys, `.env` files, machine-specific paths, or session identifiers.
- SponsorBlock data (CC BY-NC-SA 4.0); see `NOTICE`.

## Recording model responses

`--record-replay` stores raw model responses under `tests/replay/` so a run
can be reproduced with `--provider replay` and no network. Recorded responses
may contain short verbatim evidence quotes from the transcript; keep them
short and never record a run on private material into the shared store.

## Style

Standard library only in `src/advtt/` (adapters use `urllib` and
`subprocess`). Docstrings carry the measured reason for every non-obvious
rule; keep them when moving code and add one when adding a rule.
