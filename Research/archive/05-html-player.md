# 05 — The HTML player

Prototype: `player-prototype.html` in this directory. Single file, no build, no
dependencies, works from `file://`. Open it and press play — it runs a built-in
demo timeline at 20× with a sample events track embedded. Drag in a real media
file and a real `.vtt` to drive it with your own data.

## 1. What it is for

Three things, in order of importance:

1. **Prove the profile is consumable.** If a 400-line single file cannot draw ad
   regions and skip them from an `advtt/0.1` track, the profile is wrong.
2. **Demonstrate the asymmetry as an interface.** `uncertain` regions are drawn in
   a different colour, the skip button is *disabled* on them, and the status line
   says why. The whole design argument is visible in ten seconds.
3. **Be the reference for the reading rules** — token/JSON agreement, the
   `edges.start_exact` preference, `skippable` as a field rather than a
   computation.

It is not a media player anyone should ship. It has no volume, no chapters, no
captions rendering.

## 2. Reading the track: two paths, one parser

The obvious approach is the `<track kind="metadata">` element and `track.cues`:

```html
<audio controls src="episode.mp3">
  <track kind="metadata" src="episode.media-events.vtt" default>
</audio>
```

```js
const tt = audio.textTracks[0];
tt.mode = "hidden";              // NOT "disabled" -- cues stay empty otherwise
tt.addEventListener("cuechange", …);
```

Three reasons the prototype does not rely on it alone, and neither should a real
consumer:

- **`mode` matters and is easy to get wrong.** A `metadata` track defaults to
  `disabled` in some engines; `track.cues` is then `null` or empty and the code
  looks broken rather than misconfigured. `hidden` is the correct mode: cues are
  active, nothing renders.
- **`file://` and CORS.** A `<track src>` is a subresource fetch. From `file://`
  most browsers refuse it, and over HTTP a cross-origin track needs
  `crossorigin` plus CORS headers. A tool whose output must be openable by
  double-clicking cannot depend on that.
- **NOTE blocks are not exposed.** The `TextTrack` API gives you cues; it does not
  give you comments. The AdVTT header — profile version, status, thresholds,
  provenance — lives in a `NOTE` block precisely so ordinary parsers ignore it,
  which means the API cannot see it either. **A consumer that reads only
  `track.cues` cannot know the file's thresholds or whether `status` was `ok`.**
  That is a real cost of the header-in-NOTE decision and it is why the reference
  reader parses the text itself.

So: one small parser (~60 lines), fed either by a `fetch()`/drop or by the
element. `cuechange` remains useful as a clock, but the data comes from the text.

## 3. Rules the player implements, and why

**Prefer `edges.start_exact` / `end_exact` over the cue timings.** The cue times
are segment-aligned; the exact edges are word-precise when `edges.mode === "word"`.
Both are in the file because a naive consumer should get something sensible from
the cue alone.

**Skip only `skippable === true`.** Never re-derive it from `confidence`. The
producer knows the thresholds it used and whether the episode passed its gates; a
player author guessing 0.5 is exactly the failure the field exists to prevent.

**Auto-skip is off by default** and is a checkbox, not a setting buried in a menu.

**Auto-skip is a wall-clock timer aimed at the boundary, not `timeupdate`
polling.** `timeupdate` fires roughly four times a second, so a poll-driven skip
leaks up to a quarter-second of every ad and, worse, is silently rate-dependent.
The timer computes `(boundary - now) / playbackRate` and re-arms on every seek,
rate change and track load.

**Every manual seek arms a guard.** Scrub, J/L jog, or click a row in the cue
table, and auto-skip stands down for four seconds. A user who deliberately seeks
into an ad — to hear what the sponsor actually said — should not be fought.

**A trailing ad ends playback** rather than seeking into the ad it was asked to
skip. Seeking to `duration` on a postroll is the correct end-of-episode behaviour.

**Regions carry a tooltip with type, times, label, confidence and skippability.**
The user can always find out why a stripe is on the bar. An annotation the viewer
cannot interrogate is an annotation they have to trust blindly, and this one is
machine-generated.

## 4. Visual language

| State | Colour | Skip |
|---|---|---|
| `ADVERTISEMENT` / `SPONSORSHIP` with `state: "ad"` | red | offered |
| `state: "uncertain"` | amber | button disabled, reason shown |
| `PROGRAM` (when emitted) | green, low opacity | n/a |

Two colours for two verdicts, not a gradient over confidence. A gradient invites
the viewer to do the thresholding, which is the producer's job.

## 5. What a production player would add

- Render the caption track alongside, and highlight the caption cues that fall
  inside a marked region — the amended `captions.vtt` and the events track
  side by side.
- Honour `edges.mode: "segment"` by drawing a soft (gradient) edge, so the user
  can see that the boundary is approximate.
- A "report this marking" affordance writing a human-review overlay file (§13,
  §30: the correction is a data edit, and the media is never touched).
- Keyboard: `[` / `]` to jump between events, which is the navigation §24 says the
  annotation layer buys you for free.
- `MediaSession` metadata so the OS-level controls show what is playing.

## 6. Known limitations of the prototype

- No caption rendering; the events track only.
- The demo clock is a `requestAnimationFrame` loop, so it drifts slightly relative
  to a real media element. With real media, the element is the clock.
- Drag-and-drop only accepts one `.vtt`; there is no UI for a separate caption
  track.
- No validation UI. `advtt --validate` is the place for that.
