# Release checklist: making AdVTT public

Audit date: 2026-09-07. Scope: every tracked file in `davidkarnowski/AdVTT`
(286 files, 22 commits) plus the full git history, checked for secrets,
personal and machine-specific data, copyrighted transcript text, third-party
data licences, repository hygiene, documentation consistency and GitHub-side
settings. Read-only audit; nothing below has been applied yet.

## Must do before public

- [x] **Strip `meta.session_id` from the replay store.** All 177
  `tests/replay/*.json` files carry the claude CLI session UUID recorded by
  `src/advtt/providers/claude_cli.py:180`. They are conversation identifiers
  tied to the owner's account. Fix: one-off rewrite that deletes
  `meta.session_id` from every file (replay keys are
  `sha256(prompt_version | model | prompt)`, `providers/replay.py:4`, so the
  store stays valid), and drop the field at `claude_cli.py:180` so future
  `--record-replay` runs never write it.
- [x] **State the SponsorBlock licence at repository level.** Five JRE draft
  truth files (`tests/fixtures/truth-drafts/2026-08-11_*`, `2026-08-14_*`,
  `2026-08-19_1700_*`, `2026-08-27_*`, `2026-09-01_*` `*_ads.truth.draft.json`)
  contain host-read spans derived from SponsorBlock, and
  `Research/research-log/L-sponsorblock-silver.md` tabulates sponsor spans for
  15 episodes. Both carry a per-file CC BY-NC-SA 4.0 note, but `pyproject.toml`
  and `LICENSE` declare the whole repository Apache-2.0. Fix: add a
  "Third-party data" section to `README.md` (and a `NOTICE` file) saying those
  spans and tables are SponsorBlock data, CC BY-NC-SA 4.0, attributed to
  https://sponsor.ajay.app, used for evaluation only, and excluded from the
  Apache-2.0 grant.
- [x] **Remove home-directory paths from tracked files.** Occurrences:
  `CLAUDE.md:13,74,80`, `scripts/build_fixtures.py:48` (`DEFAULT_PYTHON`),
  `scripts/overnight_jre.sh:6`, `Research/research-log/0-local-grounding.md:5,23,34,40,46`,
  `Research/research-log/00-BRIEF.md:3`, `Research/archive/01-extraction-plan.md`
  (one). Keep the PodcastFetch references but make them relative:
  "PodcastFetch (private sibling project) `adclass.py`" in `CLAUDE.md:13`,
  an `ADVTT_STT_PYTHON` env var or `--python` flag in `CLAUDE.md:74` and
  `build_fixtures.py:48`, "private, not in this repository" in `CLAUDE.md:80`,
  `cd "$(dirname "$0")/.."` in `overnight_jre.sh:6`, and repo-relative names
  in the two research files. The same lines exist in history; they reveal only
  the login name, so no history rewrite is needed for them.
- [ ] **Decide on the commit author email** (still open, see the history note below). All 22 commits carry the owner's
  personal Gmail address as author and committer. It becomes public with the
  repository. Either accept it, or rewrite history once, before the first
  public push, to the GitHub noreply address (`git filter-repo --mailmap`)
  and set `user.email` to match for future commits. Rewriting later is
  disruptive for anyone who has cloned.

### Applied 2026-09-07 (working tree only)

Items marked [x] were applied in the working tree the same day. They do
not remove anything from git history: the 177 replay files with session
ids, the five JRE draft files, and `PROGRESS.md` all remain in earlier
commits. Before the public flip, either rewrite history (`git filter-repo`)
or publish from a fresh single-commit snapshot of the clean tree; the
author-email decision is made in the same step.

## Should do

- [x] **Add a CI workflow** (declined 2026-09-07: tests run locally, no hosted CI) (`.github/workflows/ci.yml`, none exists) running
  `PYTHONPATH=src python3 -m advtt.cli --self-test` and
  `pip install -e .[dev] && pytest -q tests` on Python 3.11 to 3.14, Ubuntu
  and macOS. Both pass locally today (self-test all ok; 15 tests pass).
- [x] **Complete `pyproject.toml` metadata**: add `authors`, `[project.urls]`
  (Homepage, Repository, Issues), per-version `Programming Language :: Python
  :: 3.11` to `3.14` classifiers and `Operating System :: OS Independent`.
- [x] **Add the customary community files**: `CONTRIBUTING.md` (how to run
  the tests, the `prompt_version` and `LADDER_VERSION` rule, never commit
  transcripts or audio), `SECURITY.md` (contact and scope), `CHANGELOG.md`
  (one `0.1.0.dev0` entry). A code of conduct is optional at this size.
- [x] **Decide what to do with `PROGRESS.md`.** It is an internal overnight
  work log: coordination notes, PDT timestamps, subscription usage limits
  (lines 21, 50) and the line "never public without explicit approval"
  (line 17). Either move it to gitignored `Research/local/` and update
  `CLAUDE.md:88`, or keep it and delete lines 17 and the usage-limit notes.
- [x] **Genericise the environment table in
  `Research/12-research-evaluation-and-classifier-plan.md:106-108`.** It lists
  which API keys exist in the owner's private `.env` (names only, no values).
  Reword to "Gladia was the only paid STT key available" and drop the rest.
- [x] **Replace hardcoded Homebrew tool paths** in `scripts/build_fixtures.py:47`
  (`ffprobe`) and `scripts/sb_align.py:18` (`ffmpeg`) with `shutil.which`
  plus the Homebrew path as a fallback, as `src/advtt/stt.py:535` already does.
- [x] **Mark `scripts/overnight_jre.sh` as machine-specific** (it commits and
  pushes unattended and depends on local data), or move it to `Research/local/`.
- [x] **Add a "Run the tests" line to `README.md`** (the pytest command is
  only in `CLAUDE.md` and `docs/architecture.md:71`).
- [x] **Align the exporter list in `CLAUDE.md:11-12`** ("EDL, chapters,
  SponsorBlock JSON, WebVTT, SRT twin, labels") with `exporters.py:25` and the
  `README.md` table, which also have `ffmeta` and `rttm`.
- [ ] **GitHub settings when flipping public** (checked with `gh repo view`):
  description is empty, no topics, no homepage, no tags or releases, issues
  on, discussions and wiki off, default branch `main`. Set the description to
  the `pyproject.toml` one-liner; add topics `podcast`, `advertising`,
  `sponsorship`, `transcript`, `webvtt`, `sponsorblock`, `llm`, `python`;
  after the flip enable branch protection on `main` (unavailable on the free
  plan while private) requiring the CI check; tag `v0.1.0.dev0` once CI is
  green; keep wiki off; Discussions optional.

## Nice to have

- [x] Add a `NOTICE` file or a copyright line ("Copyright 2026 David
  Karnowski") somewhere; `LICENSE` is the unmodified Apache-2.0 text and no
  file carries a copyright notice.
- [x] Drop `Research/11-notebooklm-podcast-transcript.gladia.json` (716 KB)
  from the tree: it duplicates `Research/11-*.md` and
  `tests/fixtures/notebooklm/*_stt.json` (owner's own NotebookLM content,
  three copies, about 1.2 MB). It is the largest blob in history, but under
  1 MB, so no rewrite is needed.
- [x] Change `"annotator": "dk"` in
  `tests/fixtures/notebooklm/ai_hunts_for_host-read_ads_ads.truth.json:5` to a
  neutral value such as `"owner"`.
- [ ] Agent names and PDT timestamps in `Research/research-log/{K,L,M}-*.md`
  and "the user's subscription" in `K-experiments.md:7` and `CLAUDE.md:70`
  are harmless; reword only for a cleaner public voice.
- [x] Register `docs/release-checklist.md` in `CLAUDE.md`'s "Where things
  are" table, or delete it after release.

## Verified clean

- Secrets: no API-key, token, private-key or password patterns in the working
  tree or in any commit (`git grep` over every revision, `git log -p`).
  `.env` (58 bytes) and `keys.json` are gitignored and were never committed.
- Session links: no `claude.ai/code` URLs, `Claude-Session:` trailers or
  conversation ids in any file or commit message; every commit has exactly
  one `Co-Authored-By` trailer where one is present.
- Emails and hostnames: none in tracked files (only the git author metadata
  noted above). The one `@` match is a Zenodo DOI citation.
- Copyrighted transcripts: no `_stt.json`, audio, `data/` or `eval-out/` file
  of a real episode was ever committed. `tests/replay/` (177 files, 708 KB)
  holds 436 evidence quotes totalling 3,352 words, median 8 words, longest 19
  words (126 characters); no file has more than 102 quoted words and no
  `raw_text` exceeds 1,005 characters. `tests/fixtures/truth-drafts/` (22
  files) is indices, timings, Megaphone campaign ids and notes only; its
  longest string (387 characters) is an explanatory note.
  `tests/fixtures/manifest.json` is labels only. `tests/fixtures/synthetic/`
  and `examples/episode-112.*` are invented text (Harbor Report, Acme).
  `tests/fixtures/notebooklm/` and `Research/11-*` are the owner's own
  NotebookLM-generated episode. Research logs quote web sources briefly
  (under 50 words) with source URLs.
- Large files: largest blobs in history are 731 KB and 424 KB; nothing over
  1 MB. `.git` is 3.0 MB. The 74 MB `Research/*.m4a` is ignored and absent
  from history.
- `.gitignore` covers `.env`, `.env.*`, `keys.json`, `data/`, `eval-out/`,
  `Research/local/`, `Research/*.m4a|mp3`, `*.advtt.json`, `*.analysis.json`
  (with the `examples/` exception), caches and `.DS_Store`.
- Documentation: exit codes are identical in `advtt --help`, `--describe`
  and `README.md:174`; every `--flag` in `README.md`, `docs/architecture.md`
  and `CLAUDE.md` exists (`--chapters-file`, `--editable` are mpv/pip flags;
  `--stt-dirs`, `--runs`, `--python` are script flags and exist); exporter
  names and file suffixes match between `exporters.py`, `README.md` and
  `docs/architecture.md:17`; `advtt --version` matches `pyproject.toml`.
  Every README command was executed offline: `--help`, `--describe`,
  `--self-test`, `--list-providers`, `--dry-run --stt`, `--dump-prompt`,
  `--stt ... --provider replay --export all`, `--export all --record`,
  `--captions` (vtt and srt), `--eval ... --provider replay --offline`.
- Scripts: all eight Python scripts have usage docstrings;
  `overnight_jre.sh` has a header comment.
- Feed URLs, GUIDs and enclosure SHA-256s in the manifest and truth drafts
  are public RSS facts; the PDB enclosure URLs are the public Podtrac
  redirects.
