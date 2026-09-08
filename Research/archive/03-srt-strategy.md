# 03 — SRT: the hard case

## 1. What SRT actually is

SubRip has no specification. It has a de-facto grammar, and every player
implements a slightly different superset of it:

```text
<integer sequence number>
HH:MM:SS,mmm --> HH:MM:SS,mmm
<one or more lines of text>
<blank line>
```

That is the entire format. Specifically, it has:

- **no header** — the first thing in the file must be a cue;
- **no comment syntax** — there is no `NOTE`, no `#`, no `;`;
- **no cue identifiers** — the sequence number is a number, and most parsers
  either require it to be sequential or ignore it entirely;
- **no cue settings** — no place to hang a key/value that is not text;
- **no track kind** — SRT is always subtitles; there is no `metadata` mode;
- **no defined escaping**, and only a folklore subset of HTML-ish inline tags
  (`<b> <i> <u> <font color=…>`) that some players honour, some strip, and some
  print literally.

The consequence, stated plainly because everything below follows from it:

> **There is no way to place a marking inside an SRT file that is both
> machine-readable and invisible to existing players.** WebVTT has `NOTE`; SRT has
> nothing that a renderer is contractually obliged to ignore. Any bytes in an SRT
> file are either inside a cue (and therefore may be displayed) or malformed
> (and therefore may abort the parse).

Everything in this document is a way of choosing which half of that sentence to
accept.

## 2. Option catalogue

### Option 1 — Untouched `.srt` + `.ads.vtt` companion  **(recommended default)**

```text
episode.srt          byte-identical to what the user had, or a plain conversion
episode.ads.vtt      the AdVTT media-events track (profile of 02-)
```

The caption file stays a caption file. The markings go in the format that has a
place for them. A player that wants ad regions loads two files; every other player
loads one and behaves exactly as before.

- **Player risk: none.** Nothing about the SRT changed.
- **Cost:** two files, and a consumer that only accepts SRT gets no markings.
- **Why it is the default:** it is the only option with zero downside for the
  common case, and it composes — the same `.ads.vtt` serves the SRT user, the VTT
  user, and the HTML player.

### Option 2 — `.ads.srt` visible twin  **(recommended opt-in, `--srt-twin`)**

A second, separate SRT whose cues *are* the ad intervals:

```srt
1
00:12:31,200 --> 00:12:59,800
[ADVERTISEMENT — Acme Corporation]
```

Loaded as a second subtitle track in VLC, mpv, Plex, Jellyfin, Infuse, or an
external player's "add subtitle file". Nothing about it is a hack — it is a valid
SRT that says what it means.

- **Player risk: none.** It is an ordinary subtitle track.
- **Cost:** the marking is *visible when enabled*, which is the point. It cannot
  drive a skip button; a human reads it.
- **Machine readability:** poor but non-zero. `[ADVERTISEMENT — …]` is greppable
  and parseable by convention, and the machine-readable copy is the `.ads.vtt`
  next to it.
- **Refinement:** carry the state in the text — `[ADVERTISEMENT]` vs
  `[ADVERTISEMENT?]` for `uncertain` — so a viewer sees the difference the format
  is making.

### Option 3 — Inline extra cues in the caption `.srt`  (`--srt-inline=cue`)

Insert a cue at each boundary:

```srt
197
00:12:31,200 --> 00:12:33,200
[ADVERTISEMENT]
```

- **Player risk: moderate but bounded.** Structurally valid; every player renders
  it as a subtitle for two seconds. Sequence numbers must be renumbered, which
  breaks any external reference to cue numbers (rare, but subtitle-editing tools
  do it).
- **Honest verdict:** it works, and it puts text on screen that the caption author
  did not write. Acceptable for personal archives, not for redistribution.
- **Zero-duration variant** (`00:12:31,200 --> 00:12:31,200`): do not. mpv and
  ffmpeg tolerate it; several hardware players and some JS parsers divide by the
  duration or drop the cue, and at least one common parser treats end ≤ start as a
  file error and stops.

### Option 4 — Tag the existing cue text  (`--srt-inline=tag`)

Prefix the ad cues' text with a marker: `{ad}` (SSA-style braces) or `<!--ad-->`
or `<ad>`.

- **`{ad}`**: SubStation override blocks are stripped by SSA-aware renderers, but
  in an *SRT* file most players print the braces literally. Fails.
- **`<ad>`**: ffmpeg's subrip decoder strips unknown angle-bracket tags, and VLC
  largely does too — so it is invisible *there*. Many web players (video.js,
  Plyr with a JS SRT converter) HTML-escape the text and show `<ad>` on screen.
  Browsers' native `<track>` does not accept SRT at all, so any web use converts
  first and the conversion decides. **Unreliable across the field.**
- **Verdict:** the tag approach is the one that looks cleverest and is the least
  predictable. It is offered only behind an explicit flag and prints a warning
  naming the players it is known to break in.

### Option 5 — Header/preamble before cue 1

Text before the first sequence number, or a cue numbered `0`.

- Some parsers skip leading garbage; many treat the first non-blank line as a
  sequence number and fail the whole file. A cue `0` is displayed by players that
  ignore numbering, and rejected by those that require `1`.
- **Verdict: no.** This is the option that risks the caption file not loading at
  all, which is the worst outcome available — the user loses captions to gain a
  marking.

### Option 6 — A JSON sidecar keyed to cue numbers

```json
{"file":"episode.srt","sha256":"…","spans":[{"cues":[197,213],"type":"ADVERTISEMENT"}]}
```

- Machine-readable, zero player risk, and robust to cue-numbering.
- But it is a second format to specify, and it duplicates what the `.ads.vtt`
  already says with better tooling and better player support.
- **Verdict:** not a separate deliverable. `analysis.json` already carries the
  span↔cue-index mapping, so the capability exists; a dedicated SRT-shaped sidecar
  would be a third spelling of the same fact.

## 3. Compatibility matrix

Assessed from format semantics and known parser behaviour; **this table is a
design hypothesis and should be verified against real players before Phase 2
ships.** Nothing here was tested for this document.

| Option | VLC | mpv | ffmpeg | Plex/Jellyfin | Web (converted) | Hardware/TV | Machine-readable |
|---|---|---|---|---|---|---|---|
| 1 untouched + `.ads.vtt` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (in the VTT) |
| 2 `.ads.srt` twin | ✅ visible | ✅ visible | ✅ | ✅ visible | ✅ | ✅ visible | ⚠️ by convention |
| 3 inline extra cue | ⚠️ visible | ⚠️ visible | ⚠️ visible | ⚠️ visible | ⚠️ visible | ⚠️ visible | ⚠️ by convention |
| 3b zero-duration cue | ⚠️ | ⚠️ | ⚠️ | ❓ | ❌ some parsers | ❌ | ⚠️ |
| 4 `<ad>` tag | likely stripped | likely stripped | stripped | ❓ | ❌ literal | ❌ literal | ✅ if it survives |
| 4b `{ad}` braces | ❌ literal | ❌ literal | ❌ literal | ❌ literal | ❌ literal | ❌ literal | ✅ |
| 5 preamble / cue 0 | ❓ | ❓ | ❓ | ❓ | ❌ | ❌ | ✅ |
| 6 JSON sidecar | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

✅ no user-visible change · ⚠️ works but shows text · ❌ breaks or shows junk ·
❓ unverified

## 4. What AdVTT does

```text
--format srt                    → episode.srt   (unmodified/converted)
                                  episode.ads.vtt
--format srt --srt-twin         → + episode.ads.srt
--format srt --srt-inline=cue   → markings inserted; prints a warning; the
                                  original is preserved as episode.orig.srt
--format srt --srt-inline=tag   → as above, plus a louder warning naming
                                  the players known to render the tag literally
--format both                   → vtt + srt + ads.vtt + analysis.json
```

`--srt-inline` never operates on the user's file in place without `--in-place
--backup`. The rule from PodcastFetch — never modify the record — applies with
more force here, because unlike the WebVTT case there is no invisible place to
put the annotation and therefore no lossless amendment.

## 5. Conversions and precision

- SRT uses `,` as the decimal separator and milliseconds; WebVTT uses `.`. Both
  are millisecond-precision, so VTT→SRT loses nothing temporally.
- SRT→VTT loses nothing either, but a converted file must not claim to be an
  AdVTT profile file unless it carries the header.
- WebVTT cue settings, regions, styling and identifiers have no SRT equivalent and
  are dropped on conversion. AdVTT emits none of them in caption output, so the
  conversion is lossless for files AdVTT produced — which is worth stating,
  because it means `--format both` yields two files that genuinely agree.
- SRT has no defined encoding. AdVTT writes UTF-8 without a BOM and says so; a
  BOM is offered behind `--srt-bom` for the Windows tools that need one.

## 6. The recommendation, one paragraph

Treat SRT as an **output format for captions and a non-format for metadata**.
Convert or copy the captions faithfully, put every marking in the companion
`.ads.vtt`, and offer the visible `.ads.srt` twin for people whose player can only
load subtitles. Ship the inline options because someone will genuinely want them
for a personal archive, gate them behind a flag, warn on use, and never let them
be reached by a default. The alternative — inventing an SRT convention and hoping
players cooperate — trades a guaranteed working caption file for a marking that
some fraction of players will render as garbage, and that trade is on the wrong
side of the asymmetry this whole project is organised around.
