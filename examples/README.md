# AdVTT examples

## player-demo.html

A single-file demo of AdVTT output in a native HTML5 player. It plays a local
media file, shows the full transcript as native captions from `<stem>.captions.vtt`
(or `.captions.srt`, converted in the page), draws the ad spans on a seek bar,
shows an AD banner with title, confidence, category and time remaining while an
ad block is playing, offers "Skip this ad" and an auto-skip toggle (off by
default: skipping is a policy decision), and lists the transcript and the
chapters (Part 1, Ad, Part 2, ...) with click-to-seek. It marks and optionally
skips during playback; the media file is never modified.

Open it by double-clicking the file (it works from `file://`, no server, no
network). Then pick or drag in:

1. the media file (mp3, m4a, mp4, webm, ...),
2. `<stem>.captions.vtt` or `<stem>.captions.srt`,
3. optionally `<stem>.ads.vtt` or `<stem>.advtt.json` for the span metadata.

Without 3, spans are derived from the caption cues themselves (`ad-0001.N` cue
ids or `[Ad]` / `[Ad?]` prefixes). Without 1, the timeline, transcript and
chapters still render and the seek bar moves a virtual playhead.

Files dropped together are routed by suffix: `.captions.vtt`, `.captions.srt`,
`.ads.vtt` (also the older `.media-events.vtt`), `.ads.srt`, `.advtt.json` (also
`.analysis.json`); other `.vtt` files are sniffed, and anything else is treated
as media. When the page is served over http, a button loads the bundled
`episode-112` excerpt (transcript and spans only, there is no audio).

Keyboard: Space play/pause, Left/Right seek 5 s, S skip the current ad.

Browsers draw native captions only on a video surface, so audio files play
through a short `<video>` element while "caption surface for audio files" is
checked; uncheck it for a plain `<audio>` element (captions then show only in
the transcript panel). If a browser refuses the blob-URL `<track>`, the same
cues are added through the TextTrack API and a message says so.

The `episode-112.*` files are a synthetic excerpt in the earlier `advtt/0.1`
layout, kept as a format sample.
