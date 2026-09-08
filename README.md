# AdVTT

AdVTT finds host-read sponsorship and advertising inside transcripts of
finished audio, podcasts first, using a large language model, and writes the
result as a canonical JSON record with provenance. From that record it exports
the formats players and editors already act on: EDL, ffmetadata chapters,
Podcasting 2.0 JSON chapters, SponsorBlock JSON, WebVTT, an SRT twin, Audacity
labels and RTTM. It never cuts audio. What to do with the marks is up to the
player, the archive, or the ingestion pipeline that reads them.

It was extracted from PodcastFetch, a private podcast downloader where the
classifier was first built and tuned, and stands on its own as a Python
package with no hard dependencies.

## Why this exists

Most of the written web has already been used as training data. What is new
each week is spoken: podcasts, shows, interviews. That is where current
speech, argument and culture live, and it will feed the next generation of
models. Podcast audio carries a problem with it: the same sponsor reads,
repeated across hundreds of episodes and thousands of shows, are not content.
An ingestion pipeline that cannot tell the two apart stores ad copy at scale
and dilutes the material it actually wanted.

AdVTT marks where the ads are, at time resolution, so a pipeline can keep the
show and drop the sponsorship messaging. The same record serves listeners:
chapters that name the ad, a skip list for a player, a label track for an
editor.

## The design pillar

Silently skipping real content is worse than missing an ad. Every default
follows from that asymmetry:

- A span is `action: skip` only when its confidence is at or above the ad
  threshold (0.75). Between 0.40 and 0.75 it is `uncertain`: shown, not
  skipped.
- `selfpromo` (the show's own products) is never auto-skipped.
- An evidence quote that does not verify against the transcript halves the
  span's confidence instead of dropping the span.
- An episode that fails an episode-level gate produces no marks, not partial
  ones.
- The ship gate is `content_loss_sec <= 5` per episode: at most five seconds
  of real content falsely marked as ad.

## Quick start

Python 3.11 or newer. The package itself has no dependencies; the model
adapters use `urllib` and `subprocess` only, so there are no SDKs to install.

```bash
uv tool install --editable .        # or: pip install -e .
advtt --self-test                   # the validation ladder, offline, free
advtt --describe                    # capabilities as JSON: providers, models, exporters, exit codes
advtt --list-providers              # which model and STT backends are usable on this machine
```

Classify an existing transcript (`{"segments": [{start, end, text, words?}]}`),
see the plan first, then run it and export everything:

```bash
advtt --dry-run --stt episode_stt.json --model claude-sonnet-5
advtt --stt episode_stt.json --provider claude-cli --model claude-sonnet-5 \
      --export all --record-replay --log-json run.jsonl --out-dir out/
```

Other inputs and a few more commands:

```bash
advtt --captions episode.vtt --media episode.mp3      # from a caption file (cue-level edges)
advtt episode.mp3 --stt-provider whisper-mlx          # transcribe locally first, then classify
advtt --export all --record episode.advtt.json        # re-render an existing record
advtt --dump-prompt episode_stt.json                  # print exactly what the model is asked
advtt --eval 'tests/fixtures/notebooklm/*_stt.json' --classify \
      --provider replay --model claude-sonnet-5 --offline --out-dir eval-out/replay
```

The default live provider is `claude-cli`, which runs `claude -p` with a JSON
schema and an effort level and uses the CLI's own login, so no API key is
needed. A `claude` Messages API adapter, `openai` and `gemini` adapters (not
exercised here) and local `ollama` and `omlx` adapters exist as well. Keys are
read from the environment, then `$ADVTT_ENV`, `./.env`, or
`~/.config/advtt/.env`. The tool never falls back from a local provider to a
cloud one.

## How it works

```text
media file ─► STT (whisper-mlx | parakeet-mlx | gladia | openai) ─┐
caption file (.vtt/.srt) ─► cue reader ────────────────────────────┤
transcript JSON ───────────────────────────────────────────────────┘
                              │
                 segments [{start, end, text, words?}]
                              │
        chunk planner: ~6,000-token tiled windows, 12 read-only context segments each side
                              │
        model call per chunk, with thinking, returning spans + a verbatim evidence quote
                              │
        validation ladder: parse ► range ► duration ► merge ► verbatim evidence
                           ► dialogue density ► over-label gate ► empty-is-valid
                              │
        word-precise start edges (the end edge is never trimmed to the quote)
                              │
        <stem>.advtt.json (shareable)  +  <stem>.analysis.json (local)  +  exports
```

The tool is STT-agnostic: any transcript with timed segments works, and word
timings, when present, make the start edge word-precise. Each chunk is sent
with its neighbours as read-only context so an ad that straddles a window
boundary is still seen whole. The model returns start and end indices, a
confidence, and a short verbatim quote from the first segment of the span. The
ladder then checks every span mechanically: indices in range, no span over
240 seconds, overlaps merged (minimum confidence wins), the quote actually
present in the transcript, the span not reading like interview dialogue, and
no episode more than 35 percent ad. An empty result is a valid result.

Two facts were learned by measurement and are easy to "fix" by mistake:

- **Chunking is an accuracy mechanism.** Given a whole 3,919-segment
  transcript in one call, a frontier model found the right sponsor text and
  reported it at segment 1245 instead of 445. Tiled 6,000-token windows
  matched ground truth exactly. Chunking stays even when the context window
  would fit the episode.
- **Thinking is an accuracy mechanism.** Haiku 4.5 with thinking disabled
  falsely marked 77.5 seconds of Joe Rogan Experience journalism as
  advertising; with a 4,000-token thinking budget, 2 seconds. The cheap
  setting is the dangerous one under the asymmetry above.

## Outputs

Two files are written beside the input (or in `--out-dir`), three when the
input is a media file (the transcript is kept as `<stem>_stt.json`, written
before the model is called, so a failed classification never costs the
transcription and a rerun can start from `--stt`):

- `<stem>.advtt.json`: the canonical record, profile `advtt/1.0`, schema in
  `src/advtt/schema/advtt-1.0.json`. It carries the STT identity, classifier
  identity and `prompt_version`, the thresholds in force, the media
  fingerprint (duration, bytes, SHA-256) and the transcript hash, and one
  entry per span: `start`, `end`, `category` (SponsorBlock and Jellyfin ids
  such as `sponsor`, `selfpromo`, `interaction`, `crosspromo`), `form`
  (`host_read`, `produced`, `sponsorship_credit`), `position`, `delivery`,
  `action` (`none`, `prompt`, `skip`, `mute`), `confidence` and its source,
  `advertiser`, edge mode and provenance. `action` is policy and is the only
  field a player should branch on.
- `<stem>.analysis.json`: the local tier. Evidence quotes, per-chunk token
  and cost records, and every ladder rejection with its reason. It contains
  transcript text and stays on the machine.

`--export all` (or a comma list) renders the record into:

| Format | File | For |
|---|---|---|
| `edl` | `<stem>.edl` | Kodi and mpv EDL, action 3 (commercial break); `skip` spans only |
| `ffmeta` | `<stem>.ffmeta` | ffmetadata chapters for `mpv --chapters-file` and ffmpeg embedding |
| `chapters` | `<stem>.chapters.json` | Podcasting 2.0 JSON Chapters with an `advtt` extension object |
| `sponsorblock` | `<stem>.sponsorblock.json` | SponsorBlock-shaped JSON for local-mode clients; `skip` spans only |
| `vtt` | `<stem>.ads.vtt` | WebVTT metadata track, one JSON payload per cue |
| `srt` | `<stem>.ads.srt` | a visible subtitle twin showing `[Ad] Acme` during ads |
| `audacity` | `<stem>.labels.txt` | Audacity label track for review and editing |
| `rttm` | `<stem>.rttm` | NIST RTTM for pyannote-style scoring |
| `captions-vtt` | `<stem>.captions.vtt` | the full transcript as a subtitle track, ad cues prefixed `[Ad]` and styled via `::cue(.advtt-ad)` |
| `captions-srt` | `<stem>.captions.srt` | the same full transcript as SRT, `[Ad]` / `[Ad?]` prefixes only |

Every exporter is a pure function of the record, except the two `captions-*`
formats, which also need the transcript (they come for free when the run
starts from media, `--stt` or `--captions`; with `--export --record` pass
`--stt` or keep the `<stem>_stt.json` beside the record). Where a span edge
falls inside a segment with word timings, the caption cue is cut at that
word, so the marked text is exactly the marked audio. Skip-oriented formats
carry only spans whose `action` is `skip`; descriptive formats carry every
span.

## Run the tests

```bash
PYTHONPATH=src python3 -m advtt.cli --self-test     # the validation ladder, offline
PYTHONPATH=src pytest -q tests                      # the full suite, offline, no keys
```

Tests run locally; there is no hosted CI. `CONTRIBUTING.md` has the rules
for changes that touch the prompt or the ladder.

## Verify a run in a player

`examples/player-demo.html` is a single offline page with a native HTML5
player, made for checking a run's output by ear and eye. Run the pipeline
with `--export all`, double-click the page, and drop in the media file with
its `<stem>.captions.vtt` (add the `.ads.vtt` or `.advtt.json` to see
confidence and category). The episode plays with the full transcript as
native captions, the ad spans are drawn on the seek bar, an AD banner shows
the span's title, confidence and time remaining while an ad block is
playing, the transcript panel follows playback with ad cues marked, and a
skip button jumps past the block. Seek to a marked span and listen to both
edges; a span that starts late or ends early is the most common finding.
Auto-skip is off by default and the media file is never modified.
`examples/README.md` has the details and keyboard shortcuts.

## For agents

An agent preparing training material or sorting an archive can drive the
tool end to end without a human:

| Need | Mechanism |
|---|---|
| Discover what it can do | `advtt --describe`: providers with availability, models, effort levels, exporters, schema path, exit codes, event names, gates |
| Predict cost and side effects | `--dry-run`: chunk windows, token and cost estimate, output paths, whether the network would be used |
| Act without ambiguity | `--json` prints the record to stdout; `--out-dir`; `--force` is required to overwrite |
| Observe while running | `--log-json PATH` (or `-` for stderr): JSON Lines events `run.start`, `input.loaded`, `provider.ready`, `chunk.start`, `chunk.done`, `chunk.error`, `gate`, `output.written`, `output.exported`, `run.done`, `error` |
| Branch on the outcome | stable exit codes: 0 ok, 1 usage, 2 classification not ok, 3 output exists, 4 provider unavailable or refused by `--offline`, 5 input unreadable, 6 self-test or eval gate failed |
| Reproduce | `--record-replay` stores every raw model response under `tests/replay/`; `--provider replay` reruns the same inputs with no network |
| Stay inside a boundary | `--offline` refuses every cloud provider and STT upload (exit 4) |
| Compose | `classify_segments`, `build_record` and `exporters.render` are plain functions |

```python
from advtt import classify_segments, providers
from advtt.record import build_record
from advtt import exporters

result = classify_segments(segments, providers.make_provider("claude-cli", model="claude-sonnet-5"))
record = build_record(result, media={...}, stt={...})
edl = exporters.render(record, "edl")
```

The result dict keeps `rejections`, `chunks` and `incomplete_chunks` so partial
failure stays visible; a caller that drops them would cache a transient error
as an ad-free episode.

## Evaluation

`advtt --eval GLOB` scores predictions against `<stem>_ads.truth.json` beside
each transcript. Metrics are time-weighted and the gates are:

| Metric | Meaning | Gate |
|---|---|---|
| `content_loss_sec` | content seconds falsely marked ad at the skip threshold | at most 5 s per episode, the ship gate |
| `ad_recall_sec` | ad seconds correctly caught | at least 0.70 |
| `hostread_recall_sec` | recall on host-read truth only | at least 0.70 |
| `inserted_recall_sec` | recall on dynamically inserted creatives | reported, not gated |
| `boundary_err_sec` | mean end-edge error over matched blocks | at most 3 s |

Recall is split by delivery because a dynamically inserted creative is
already labelled exactly by the host's stitch map (Megaphone publishes one in
the `x-megaphone-payload-2` response header). A model that catches every
inserted creative and misses every host read can score 0.9 total recall on a
long episode and still be useless, so the classifier is judged on host-read
spans. Delivery comes from a `delivery` field on each truth span or from a
sibling `<stem>_ads.truth.inserted.json` (written by
`scripts/stitchmap_to_truth.py`; looked up beside the transcript, then in
`--inserted-dir`, default `tests/fixtures/truth-drafts/`). An inserted file
with no spans declares a copy with no dynamic insertion, so all of its ads
are host-read.

What ships in this repository: two synthetic fixtures
(`tests/fixtures/synthetic/`), one real ad-free control
(`tests/fixtures/notebooklm/`, an AI-generated episode about this project
that talks about ads constantly and contains none), a labels-only manifest
(`tests/fixtures/manifest.json`), labels-only truth drafts and stitch-map
labels (`tests/fixtures/truth-drafts/`), and the replay store. The four
hand-labelled development fixtures are transcripts of copyrighted episodes
and are not in the repository. On that dev set Claude Sonnet 5 at default
effort scored zero content loss and full recall, but the same four episodes
were used to tune the prompt, so that number is necessary, not sufficient.
Experiment results are logged in `Research/research-log/K-experiments.md`.

## Status and limits

- Research stage, version `0.1.0.dev0`. The pipeline, ladder, record,
  exporters, evaluation and agent surface all work and are tested offline;
  the accuracy numbers come from a small fixture set from two shows.
- English podcasts only so far. Prompt and ladder constants were tuned on
  those.
- The focus is host-read sponsorship. Dynamically inserted creatives are
  better handled by the host's own stitch map where one exists; the
  evaluation treats them as reported, not gated, for that reason.
- Changing `prompts.py`, `chunking.py`, `validate.py` or `refine.py` is a
  `prompt_version` (or `LADDER_VERSION`) bump, because recorded results and
  replay keys depend on them.
- Not a general ad blocker, and not an audio editor. It writes metadata about
  a file the user already holds; transcripts and evidence quotes stay local.

Deeper reading: `docs/architecture.md` (module map, provider contract, how to
evaluate the code), `CLAUDE.md` (the operational version for agents working
in the repository), and `Research/` (the research and plan behind the design).

## Third-party data

The pipeline needs no external labels. Two outside sources appear in the
evaluation only:

- **SponsorBlock** (https://sponsor.ajay.app, CC BY-NC-SA 4.0). Community
  sponsor segments were used as an independent reference point for host-read
  timing on a few episodes. No SponsorBlock data is in this repository or the
  package, nothing in the pipeline reads it, and the `sponsorblock` export is
  a file format, not data. See `NOTICE`.
- **Megaphone stitch maps.** The `x-megaphone-payload-2` header the hosting
  service returns with each audio response gives the byte positions of the
  creatives it inserted into that copy. The repository keeps the decoded
  positions as labels; no audio or transcript of any third-party episode is
  committed.

## License

Apache-2.0, see `LICENSE`. The reasoning behind the release policy is in
`Research/research-log/G-legal-ethics-and-release-policy.md`.
