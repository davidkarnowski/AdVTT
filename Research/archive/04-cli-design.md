# 04 — CLI design

One binary, `advtt`. Two input modes (media, or existing captions), one pipeline,
several writers. Everything that costs money or leaves the box is explicit.

## 1. Synopsis

```text
advtt [INPUT] [options]
advtt --captions FILE [--media FILE] --amend [options]
advtt --self-test | --eval GLOB | --dump-prompt INPUT | --list-providers | --validate FILE
```

`INPUT` is a media file (`.mp3 .m4a .wav .flac .ogg .mp4 .mkv .webm .mov`).
Video is demuxed to 16 kHz mono WAV with `ffmpeg` before STT.

## 2. Input

| Switch | Default | Meaning |
|---|---|---|
| `INPUT` | — | media file; positional |
| `--captions FILE` | — | existing `.vtt`/`.srt` to read instead of transcribing |
| `--media FILE` | — | the media the captions belong to; enables drift checking and word-precise edges |
| `--transcript FILE` | — | a PodcastFetch-shaped `_stt.json`, or any JSON with `segments[]` |
| `--amend` | off | required with `--captions`: produce an amended copy rather than a fresh caption file |

`--captions` without `--media` is legal and useful (classification is textual),
but disables drift checking and forces `edges.mode: "segment"`. That degradation
is recorded in the output header, not inferred by the reader.

## 3. Transcription

| Switch | Default | Meaning |
|---|---|---|
| `--stt ENGINE` | `auto` | `whisper-mlx`, `parakeet-mlx`, `gladia`, `openai`, `auto` |
| `--stt-model ID` | per engine | override the model |
| `--words` / `--no-words` | `--words` | request word-level timings (~1.11× transcription time; enables word-precise edges and splits) |
| `--language CODE` | auto | passed through where the engine supports it |
| `--save-transcript PATH` | `<base>.stt.json` | keep the transcript; it is the expensive artefact |
| `--stt-workers N` | `0` | 0 = 1 for local engines (GPU-bound, model loads once), 4 for cloud |

`auto` resolves in order `whisper-mlx → parakeet-mlx → gladia → openai` and
**never** silently promotes a local request to a cloud engine. Naming a local
engine that is unavailable is an error with a reason, not a fallback.

If the chosen engine returns `timing: "proportional"`, AdVTT continues but sets
`edges.mode: "segment"`, refuses `--words`, and prints one warning: those
timestamps are character-count fiction and word-precise edges over them would be
confident nonsense.

## 4. Classification

| Switch | Default | Meaning |
|---|---|---|
| `--provider NAME` | `openai` | `openai`, `omlx`, `ollama`, `claude`, `claude-cli`, `gemini` |
| `--model ID` | per provider | override |
| `--endpoint URL` | per provider | for `ollama`/`omlx` |
| `--chunk N` | provider's `max_chunk_tokens` | labelling-window size in tokens |
| `--timeout S` | `180` | per request |
| `--max-fraction F` | `0.35` | episode over-label gate |
| `--ad-threshold F` | `0.75` | `state: "ad"` and `skippable` cut-off |
| `--uncertain-threshold F` | `0.40` | below this a span is dropped entirely |
| `--hint TEXT` | filename stem | show/episode hint given to the model |
| `--no-classify` | off | transcribe and write captions only |

`--chunk` is documented in `--help` as an accuracy control, not a cost control.
Raising it because the model has a big context window is the specific mistake the
help text warns against: index tracking degrades over long inputs regardless of
context size.

Lowering `--ad-threshold` is allowed and is a foot-gun; `--help` says so. Raising
`--max-fraction` above 0.5 requires `--yes`.

## 5. Output

| Switch | Default | Meaning |
|---|---|---|
| `--format {vtt,srt,both,events,none}` | `both` | caption output format(s) |
| `--events` / `--no-events` | `--events` | write the `.media-events.vtt` track |
| `--analysis` / `--no-analysis` | `--analysis` | write `analysis.json` |
| `--output-dir DIR` | alongside the input | where everything goes |
| `--basename NAME` | input stem | stem for every artefact |
| `--in-place` | off | amend the source caption file itself; requires `--backup` |
| `--backup` | off | write `<name>.orig.<ext>` before touching anything |
| `--emit LIST` | `ads` | `ads`, `program`, `all` — which cue types reach the events track |
| `--srt-twin` | off | additionally write the visible `.ads.srt` |
| `--srt-inline {none,cue,tag}` | `none` | inline SRT marking; warns (see 03-) |
| `--srt-bom` | off | write a UTF-8 BOM for Windows tooling |
| `--force` | off | ignore a cached result for this transcript hash |

Default artefact set for `advtt episode.mp3`:

```text
episode.stt.json              the transcript (durable; the expensive one)
episode.vtt                   captions
episode.srt                   captions
episode.media-events.vtt      the markings
episode.analysis.json         the full record
```

## 6. Diagnostics and gates

| Switch | Meaning |
|---|---|
| `--list-providers` | availability of every LLM and STT adapter; never touches the network |
| `--probe` | one live 16-token call per selected provider; catches a key that exists but cannot be used |
| `--dump-prompt INPUT` | print the exact system prompt, chunk plan and per-chunk user prompts, then exit |
| `--self-test` | the validation ladder offline; no network, no cost |
| `--eval GLOB` | score against `*.truth.json`; `content_loss_sec ≤ 5` is the ship gate |
| `--validate FILE` | check a `.media-events.vtt` against the profile's rules (02- §12) |
| `--json` | machine-readable result on stdout |
| `-v` / `-q` | verbosity |
| `--dry-run` | resolve everything, print the plan and the artefacts that would be written, touch nothing |

`--dump-prompt` and `--dry-run` are the two commands that answer "is this
configured correctly" without spending anything, and they are named in `--help`
as such.

## 7. Exit codes

| Code | Meaning |
|---|---|
| 0 | ok |
| 2 | classification produced no marking (rejected by a gate, or provider failed) — artefacts still written, with `status` set |
| 3 | input error: unreadable media, unparseable captions, drift check failed |
| 4 | provider unavailable or not configured |
| 5 | validation failure (`--validate`, `--self-test`, `--eval` below gate) |

A rejected episode exits 2 and writes a `status != "ok"` events file with **no
cues**. It does not write a partially-marked file. That is the asymmetry as an
exit code.

## 8. The amendment workflow

```bash
advtt --captions episode.srt --media episode.mp3 --amend --format both --output-dir out/
```

Steps, in order:

1. **Read** the caption file into segments: `{start, end, text, cue_id}` per cue.
   No word timings exist, so `has_words` is false.
2. **Drift check** (below). Abort with exit 3 if it fails and no override was given.
3. **Classify** exactly as for a transcript. The chunk planner, the ladder and the
   gates are unchanged — they operate on segments and do not care where the
   segments came from.
4. **Refine edges**: skipped when there are no words. `edges.mode: "segment"`.
5. **Write**: a copy of the caption file with `NOTE ADVTT` blocks (VTT), or an
   untouched copy plus companions (SRT); the events track; the analysis JSON.

### Segment boundaries that are not the classifier's

Someone else's caption cues are typically shorter and denser than STT segments —
often two lines of ≤42 characters, split for reading speed rather than at pauses.
Three consequences, each handled explicitly:

- **More segments, smaller each.** The chunk planner is token-budgeted, not
  segment-counted, so it adapts by itself. No change needed.
- **A cue that straddles an ad boundary cannot be split**, because there are no
  word timings. The straddling cue is **excluded** from the ad span. Following the
  asymmetry: excluding it means the listener hears a fragment of the ad; including
  it means a fragment of journalism is skipped, and that is the worse error.
  `analysis.json` records the excluded cue so the choice is auditable.
- **Evidence matching still works** and is still required. The evidence quote is
  matched against the caption text, not against a word stream, using the same
  `quote_matches` normalisation. Caption files sometimes carry speaker prefixes
  (`- JULIE:`) and sound descriptions (`[MUSIC]`); the reader strips a leading
  speaker prefix and bracketed non-speech before classification, and records that
  it did.

Optionally, `--media` plus `--words` enables the best of both: transcribe for word
timings, keep the *user's* caption text as the output, and use the word stream
only to place edges. This is `--realign words`, and it is the recommended
invocation when the media is present, because it recovers mid-cue splits without
altering a single caption.

### Timing drift

The failure mode: a caption file made for a different cut, a different frame rate,
or with baked-in ad breaks the user's copy does not have. Every marking then lands
in the wrong place — and a *confidently* wrong ad marking is precisely the failure
the whole design tries to avoid.

| Switch | Default | Meaning |
|---|---|---|
| `--check-drift` / `--no-check-drift` | on when `--media` is present | verify captions align with the audio |
| `--drift-tolerance S` | `1.5` | acceptable mean offset |
| `--offset S` | `0` | shift every caption time by S seconds (may be negative) |
| `--rate R` | `1.0` | multiply every caption time by R; `--rate 25/23.976` for the classic PAL/NTSC transfer |
| `--realign {none,probe,words}` | `probe` when `--media`, else `none` | how alignment is verified/repaired |

`--realign probe` transcribes three 30-second probes (10 %, 50 %, 90 % of
duration), matches each against the caption text by normalised quote matching, and
computes offset and rate by least squares over the three anchors. Three points, not
two, because two cannot distinguish "shifted" from "shifted and stretched" from
"one bad anchor". If the residual exceeds `--drift-tolerance`, AdVTT **refuses**
and prints the measured offset and rate so the user can decide, rather than
guessing. Cost is about 90 seconds of audio through STT — cheap, and far cheaper
than a mis-timed skip.

Sanity checks that run even without `--media`: the last cue must end at or before
the media duration when known; cue times must be monotonic; a caption file whose
duration differs from the media by more than 2 % is reported.

## 9. Worked examples

```bash
# Simplest: transcribe, classify, write everything beside the file.
advtt episode.mp3

# Fully local. Nothing leaves the machine — enforced, not requested.
advtt episode.mp3 --stt whisper-mlx --provider omlx --model qwen3-8b

# I already have captions and the audio. Best-quality amendment: keep my caption
# text, use a fresh word stream only to place the ad edges precisely.
advtt --captions episode.vtt --media episode.mp3 --amend --realign words

# I have captions and no audio. Segment-aligned edges, no drift check, and the
# output says so.
advtt --captions episode.srt --amend --format srt --srt-twin --output-dir out/

# A 25 fps SRT against a 23.976 fps master.
advtt --captions episode.srt --media episode.mkv --amend --rate 0.95904 --offset -1.2

# Amend in place, with a backup, because this archive is organised by filename.
advtt --captions episode.vtt --amend --in-place --backup

# Video, ads track only, no caption output at all.
advtt talk.mp4 --format events --emit ads,program

# What will this cost and what will it write? Nothing is spent.
advtt episode.mp3 --dry-run
advtt episode.mp3 --dump-prompt | head -60

# Is the classifier still good? Free, then cheap.
advtt --self-test
advtt --eval 'fixtures/*/*.truth.json'

# Someone handed me an events file. Is it conforming?
advtt --validate episode.media-events.vtt
```

## 10. Configuration

Precedence: CLI flag → environment → `~/.config/advtt/config.json` → default.
Keys (`OPENAI_API_KEY`, `GOOGLE_STUDIO_API_KEY`, `ANTHROPIC_API_KEY`,
`GLADIA_API_KEY`, `HF_TOKEN`) come from the environment or a `.env` next to the
package, matching the existing loader. No key is ever written to config by the
tool, and no artefact contains one — the header records provider and model names
only.

## 11. What the CLI deliberately does not have

- **No `--yes-really-skip` / burn-in mode.** AdVTT annotates; it never renders a
  cut media file. Removing advertising from someone's file is a different tool
  with different consequences.
- **No batch/glob mode in v1.** A shell loop is clearer, and per-file failure
  handling in a batch runner is exactly the place where a partial result gets
  cached as a success.
- **No auto-download of models.** `ollama` needs its model pulled; that stays an
  explicit act.
- **No provider fallback chain.** `--provider a,b,c` is not offered. One provider,
  one answer, one provenance record.
