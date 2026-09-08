# C — Time-based metadata standards for audio/video timelines (and what AdVTT should emit)
Accessed: 2026-09-01

Method note: WebSearch budget for this session was exhausted (200/200) after the second
batch of queries, before the incremental-writing rule was in force. The entries below
marked "snippet-only" came from those searches; everything marked "fetched" was read via
WebFetch of the primary URL or verified locally (ffmpeg 8.1.1 on this Mac). Remaining
work falls back to WebFetch of primary spec URLs plus local experiments.

## Status
COMPLETE — 2026-09-01 ~17:20 PT. 72 source entries (≈45 fetched or locally verified, remainder snippet-only and marked), 2 local experiments, synthesis, 10 implications, open questions.

## Sources

### S1. WebVTT: The Web Video Text Tracks Format (W3C) — https://www.w3.org/TR/webvtt1/
- Type: spec
- Verified: fetched
- Key facts:
  - Status line: "W3C Candidate Recommendation Draft, 20 May 2026", Timed Text WG, Recommendation track. (Still not a REC after ~15 years.)
  - Metadata payload: "WebVTT metadata text consists of any sequence of zero or more characters other than U+000A LINE FEED (LF) characters and U+000D CARRIAGE RETURN (CR) characters, each optionally separated from the next by a WebVTT line terminator" (sec 4.2.1). i.e. multi-line allowed.
  - Blank-line rule (intro Metadata example): "you cannot provide blank lines inside a metadata block, because the blank line signifies the end of the WebVTT cue."
  - "-->" is forbidden inside any cue payload; a line containing "-->" is parsed as a new cue's timing line.
  - Cue identifier: "any sequence of one or more characters not containing the substring '-->' ... nor containing any LF or CR". Should be unique; in practice parsers do not enforce it.
  - Escaping: "&" and "<" restrictions (character references) apply to *cue text* (captions/subtitles, sec 4.2.2), NOT to metadata text. Metadata text may contain literal "<" and "&". Browsers still expose `cue.text` raw; only `getCueAsHTML()` parses.
  - NOTE comment block: "NOTE" followed by space/tab/line terminator; ends at first blank line; must not contain "-->".
- Relevance to AdVTT:
  - The two-line payload (token line + JSON line) is spec-legal metadata text as long as the JSON is a single line with no blank line, and JSON strings never contain "-->" or raw CR/LF (JSON escapes \n anyway; must escape "-->" e.g. as "-->").
  - `NOTE ADVTT/0.1` header is legal but it is a *comment*; parsers drop it (browsers do not expose NOTE blocks to script). Version signalling must also live inside cues or the header line after "WEBVTT".

### S2. Requirements for Media Timed Events (W3C IG Note) — https://www.w3.org/TR/media-timed-events/
- Type: spec (Interest Group Note)
- Verified: fetched
- Key facts:
  - Published 25 June 2020 by the Media & Entertainment IG.
  - Use case 1 is dynamic content insertion / ad insertion driven by SCTE-35, needing "frame accuracy".
  - Gap: DataCue "is not implemented in all of the main browser engines"; WebKit had a proprietary `type`/`value` extension.
  - Gap: "time marches on" fires cue events "in some cases with a delay up to 250 milliseconds"; recommends cue events "within 20 milliseconds"; `timeupdate` polling "explicitly discouraged".
  - Gap: cannot create a cue whose end is the end of a live stream (recommends Infinity end time).
  - WebVTT metadata cues acknowledged as the existing workaround: serialize JSON into the cue text and deserialize on enter.
- Relevance to AdVTT:
  - Confirms the JSON-in-WebVTT-metadata-cue pattern is the recognised web workaround.
  - Skip UIs that rely on `cuechange` can be up to 250 ms late; a skip button must use cue start time, not the moment of the event, to compute the seek target.

### S3. WICG DataCue repository — https://github.com/WICG/datacue
- Type: repo (incubation)
- Verified: fetched (repo page; explainer body not rendered)
- Key facts: describes DataCue as "a TextTrackCue based interface for arbitrary timed metadata"; 68 commits; links to TextTrackCue-constructor and TextTrackCue-enhancement proposals. No browser-support table on the page.
- Relevance: DataCue never became a cross-browser API; do not design for it.

### S4. WICG datacue — text-track-cue-constructor.md — https://github.com/WICG/datacue/blob/main/text-track-cue-constructor.md
- Type: spec proposal
- Verified: fetched (raw)
- Key facts:
  - DataCue "was implemented and matured in Apple's WebKit, though that feature was subsequently dropped in accordance with W3C rules because this was only implemented in a single browser."
  - Proposal: expose the `TextTrackCue` constructor so JS can subclass it; subclass name ≈ `DataCue.type`, subclass fields ≈ `DataCue.value`.
  - No dates or browser positions in the doc (search snippet: added March 2025).
- Relevance: The realistic web API for metadata cues remains `VTTCue` with a text payload; anything richer is still incubation in 2025–26.

### S5. W3C Media & Entertainment IG minutes, 11 March 2025 — https://www.w3.org/2025/03/11-me-minutes.html
- Type: minutes
- Verified: fetched
- Key facts:
  - "DataCue does not actually exist in practice across browsers"; group leaning to refocus DataCue on in-band (emsg/ID3) scenarios only.
  - Rob Smith (WebVMT author) proposed exposing the TextTrackCue constructor: "The only change is to allow access to the constructor of TextTrackCue."
  - Apple's separate "TextTrackCue with HTML" proposal adds a `cueNode` DocumentFragment attribute (rendering, not metadata).
- Relevance: Two live proposals (constructor; HTML cueNode); neither shipped cross-browser as of the minutes. VTTCue text remains the only portable carrier.

### S6. HTML Living Standard — media elements / text track model — https://html.spec.whatwg.org/multipage/media.html
- Type: spec
- Verified: fetched
- Key facts:
  - Kind `metadata`: "Tracks intended for use from script. Not displayed by the user agent."
  - Modes: disabled / hidden / showing. Metadata `<track>` elements default to disabled; script must set `track.mode = "hidden"` to get cues loaded and `cuechange` fired without rendering.
  - `cuechange` fires on the TextTrack and on the `<track>` element when the active cue set changes; "time marches on" runs at least every 250 ms (approx., snippet of the spec text).
  - Cue fields: identifier, start time, end time, pause-on-exit.
- Relevance: The single-file player must set mode="hidden"; `pauseOnExit` is a cheap way to implement "pause at end of ad" preview mode.

### S7. Podcast Namespace — `<podcast:chapters>` tag — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/chapters.md
- Type: spec
- Verified: fetched (raw)
- Key facts: Parent `<item>`, Count: Single. Attributes `url` (required), `type` (required): "Mime type of file - JSON prefered, 'application/json+chapters'." Format defined in jsonChapters.md.
- Relevance: One chapters file per episode; an ad-marker file would have to *be* the chapters file (with toc:false entries) or ride a different tag.

### S8. Podcast Namespace — JSON Chapters format v1.2 — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/examples/chapters/jsonChapters.md
- Type: spec
- Verified: fetched (raw)
- Key facts:
  - Version "1.2 (Updated 2021.04.15)". Top level: `version` (req), `chapters` (req), optional `author`, `title`, `podcastName`, `description`, `fileName`, `waypoints`.
  - Chapter object: `startTime` (float seconds, required); optional `title`, `img`, `url`, `endTime` (float seconds), `toc` (boolean), `location` {name, geo (RFC 5870 geoURI), osm}.
  - `toc: false`: "this chapter should not display visibly to the user in either the table of contents or as a jump-to point".
  - No `kind`/`type`/`skip` field; unknown properties are not forbidden but not defined either.
- Relevance:
  - AdVTT can emit spec-conformant JSON chapters today: ad blocks as chapters with `title:"Ad: <advertiser>"`, `endTime`, and either `toc:true` (visible, user jumps past) or `toc:false` (hidden marker). Extra fields (e.g. `"x-advtt": {...}`) would be tolerated by JSON parsers but are non-standard.

### S9. Podcast Namespace — `<podcast:transcript>` tag — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/transcript.md
- Type: spec
- Verified: fetched (raw)
- Key facts: attrs `url`, `type` (required), `language`, `rel="captions"`. Listed types: text/plain, text/html, text/vtt, application/json, application/x-subrip. Multiple tags per item allowed.
- Relevance: A WebVTT ad-marker file must NOT be published as a `podcast:transcript` (apps would render it as captions). The transcript tag is the right place for the STT output AdVTT already produces.

### S10. Podcast Namespace — transcript format examples — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/examples/transcripts/transcripts.md
- Type: spec
- Verified: fetched (raw)
- Key facts: Formats: WebVTT, HTML, JSON, SRT. WebVTT recommended as "the most flexible" if only one is offered; speaker via `<v>` tags; "Apple Podcasts supports this format". JSON transcript: `version` ("1.0.0"), `segments[]` with `speaker`, `startTime`, `endTime`, `body` — seconds as decimals.
- Relevance: The JSON transcript segment schema (startTime/endTime floats, body) is the vocabulary podcast apps already parse; an ad-segment JSON that mirrors it costs implementers nothing.

### S11. Podcast Namespace — `<podcast:soundbite>` — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/soundbite.md
- Type: spec
- Verified: fetched (raw)
- Key facts: attrs `startTime`, `duration` (required, seconds; 15–120 s suggested); node value = title ≤128 chars; parent `<item>`; multiple allowed. Purpose: previews, audiograms, highlights.
- Relevance: Precedent for **time ranges expressed as start+duration in seconds inside RSS**; the same shape (startTime/duration) recurs in valueTimeSplit (S12). If AdVTT ever proposes an RSS tag, copy this shape.

### S12. Podcast Namespace — `<podcast:valueTimeSplit>` — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/value-time-split.md
- Type: spec
- Verified: fetched (raw)
- Key facts: parent `<podcast:value>`; attrs `startTime` (req, seconds), `duration` (req, seconds), `remoteStartTime`, `remotePercentage`; content: `valueRecipient`s or one `remoteItem`. Purpose: switch payment splits for a time range (e.g. a guest's segment). No mention of ads.
- Relevance: Formalised proof that the namespace already carries episode-internal time ranges; a hypothetical `podcast:segment`/ad-disclosure tag would be a small step, not a new concept.

### S13. Podcast Namespace discussion #669 — Proposal: `<podcast:disclosure>` — https://github.com/Podcastindex-org/podcast-namespace/discussions/669
- Type: forum (proposal)
- Verified: fetched
- Key facts: opened 16 Oct 2024 by Daniel J. Lewis; `type` (compensation, ai, association, license) and `context` (links, content, ad, images, audio, music); **no time-range attributes**; still "Ideas"/"proposal"/"help wanted" as of mid-2026, unformalised; James Cridland: adoption depends on Apple/Spotify.
- Relevance: Nobody in the namespace has proposed time-ranged ad markers; the closest thing (disclosure) is un-timed and stalled. A gap AdVTT could fill — but adoption politics (host + app commitment) are the blocker, not syntax.

### S14. Castopod blog — "Apple Podcasts Embraces Chapters" — https://blog.castopod.org/apple-podcasts-embraces-chapters-another-victory-for-podcasting-2-0/
- Type: blog
- Verified: fetched
- Key facts: 5 Nov 2025. With iOS 26.2 (Dec 2025) Apple reads chapters from (1) episode description timestamps (≥3, first at 00:00:00), (2) RSS `<podcast:chapters>`, (3) file metadata "MP4 headers or ID3/AAC tags"; auto-generates AI chapters otherwise (opt-out). Recalls Apple adopting `<podcast:transcript>` in March 2024. Points to Apple support doc 5482.
- Relevance: As of Dec 2025 the largest podcast app consumes both Podcasting 2.0 JSON chapters and ID3 CHAP — the two chapter carriers AdVTT should emit.

### S15. Podnews — "Why you should be using podcast chapters" — https://podnews.net/article/why-to-use-podcast-chapters
- Type: blog
- Verified: fetched
- Key facts: "some podcast apps (including Apple Podcasts, Spotify, and Overcast) have started auto-chaptering episodes when no chapters are provided". No detail on JSON vs ID3.
- Relevance: Auto-chaptering means an AdVTT chapter export competes with/overrides app-generated chapters — publishing ad chapters as the *only* chapters would suppress content chapters in Apple.

### S16. ID3v2 Chapter Frame Addendum v1.0 (2005, BBC R&D / Dan O'Neill) — https://id3.org/id3v2-chapters-1.0 (id3.org returned HTTP 500; read the mutagen-specs mirror https://mutagen-specs.readthedocs.io/en/latest/id3/id3v2-chapters-1.0.html)
- Type: spec
- Verified: fetched (mirror)
- Key facts:
  - CHAP: Element ID (null-terminated), Start time ms (32-bit), End time ms (32-bit), Start offset bytes, End offset bytes ("If these bytes are all set to 0xFF then the value should be ignored"), optional embedded sub-frames (TIT2 title, TIT3, WXXX, APIC...).
  - CTOC: Element ID, flags `%000000ab` (a = top-level, b = ordered), entry count (8-bit → max 255 children), child IDs, optional sub-frames; "multiple 'CTOC' frames can also be used to define a hierarchical (multi-level) table of contents".
  - Times are 32-bit ms → max ~49.7 days; ms precision only. No "hidden"/"kind" flag.
- Relevance: AdVTT can embed ad ranges losslessly at ms precision as CHAP frames (TIT2 = "Ad: Acme"); ad-kind and confidence must go in TIT3/TXXX/WXXX sub-frames or a second, non-top-level CTOC ("advtt") so ordinary players' TOC is unaffected.

### S17. Matroska — Chapters — https://www.matroska.org/technical/chapters.html
- Type: spec
- Verified: fetched
- Key facts: EditionEntry ⊃ ChapterAtom (nestable). "ChapterTimeStart is the timestamp of the start of Chapter with nanosecond accuracy and is not scaled by TimestampScale"; end ≥ start. EditionFlagDefault/Ordered; ordered chapters define a virtual timeline (players MUST play in stored order). ChapterFlagHidden "works independently of Parent Chapters". ChapProcess (CodecID 0 Matroska script, 1 DVD menu). Page does not mention ChapterSkipType (see RFC 9559, later source).
- Relevance: Multiple editions = a lossless home for an "ad map" edition alongside content chapters; ordered chapters could even define an ad-free virtual timeline (skip by construction) — only mpv/MKV-native players honour ordered chapters.

### S18. Matroska — Codec specs (subtitles) — https://www.matroska.org/technical/codec_specs.html
- Type: spec
- Verified: fetched
- Key facts: `S_TEXT/WEBVTT`: "The CodecPrivate contains the file body preceding the first cue block"; non-cue content between cues stored as BlockAdditions with BlockAddID 1. No mapping of WebVTT `kind` to Matroska flags.
- Relevance: In .mkv a WebVTT metadata track survives (header incl. NOTE preserved in CodecPrivate), but its *kind* is lost — players will treat it as a subtitle track and may render the JSON on screen.

### S19. WebM Container Guidelines — WebVTT — https://www.webmproject.org/docs/container/
- Type: spec
- Verified: fetched
- Key facts: "the CodecID for a WebVTT track is 'D_WEBVTT/kind', where kind is one of SUBTITLES, CAPTIONS, DESCRIPTIONS, or METADATA." "TrackType ... 0x11 for WebVTT SUBTITLES and CAPTIONS, and 0x21 for WebVTT DESCRIPTIONS, and METADATA." Block = [identifier LF][settings LF]payload.
- Relevance: WebM is the one container with a first-class *metadata-kind* WebVTT track type; an AdVTT track can be muxed into WebM with kind preserved (ffmpeg: `-kind metadata` on the demuxer, see S21).

### S20. ffmpeg CLI docs (doc/ffmpeg.texi) — https://ffmpeg.org/ffmpeg.html#Main-options
- Type: spec/docs
- Verified: fetched (raw texi)
- Key facts: `-map_chapters input_file_index`: "Copy chapters from input file ... If no chapter mapping is specified, then chapters are copied from the first input file with at least one chapter. Use a negative file index to disable any chapter copying." `-map_metadata` supports `c:chapter_index` per-chapter metadata. Chapter metadata is not filtered by `-metadata` filtering.
- Relevance: `ffmpeg -i ep.mp3 -i ads.ffmeta -map_metadata 1 -map_chapters 1 -c copy out.m4a` is the canonical zero-re-encode path to write chapters into MP3/M4A/MKV.

### S21. Local verification: ffmpeg 8.1.1 `-h demuxer=webvtt` (this Mac, 2026-09-01)
- Type: product (local)
- Verified: fetched (ran locally)
- Key facts: WebVTT demuxer option `-kind` with values subtitles(0), captions(65536), descriptions(131072), metadata(262144) — sets the stream disposition used by the WebM muxer to pick `D_WEBVTT/METADATA`. Muxer `webvtt` mime `text/vtt`. No mkvmerge/mp4box/mpv installed here.
- Relevance: Toolchain exists to round-trip an AdVTT .vtt into WebM with kind intact; experiment pending (see Open questions).

### S22. HLS 2nd edition, draft-pantos-hls-rfc8216bis-22 (1 May 2026) — https://datatracker.ietf.org/doc/html/draft-pantos-hls-rfc8216bis
- Type: spec (IETF draft)
- Verified: fetched
- Key facts: EXT-X-DATERANGE attrs: ID (req), CLASS, START-DATE (req), END-DATE, DURATION, PLANNED-DURATION, `X-` client attributes (reverse-DNS names), SCTE35-CMD/OUT/IN ("big-endian binary representation of the splice_info_section()"), END-ON-NEXT, CUE (PRE, POST, ONCE). Appendix D: Interstitials schema (CLASS com.apple.hls.interstitial — details from Apple PDF, S33).
- Relevance: HLS's vocabulary for arbitrary timed ranges is *CLASS + X-attributes*, i.e. a namespaced class string plus key/values — structurally identical to AdVTT's "token line + JSON line". Reverse-DNS class naming (e.g. `org.advtt.ad`) is a proven convention worth copying.

### S23. Broadpeak.io docs — SCTE-35 markers — https://developers.broadpeak.io/docs/dai-scte35
- Type: product docs
- Verified: fetched
- Key facts: HLS carriers: EXT-X-DATERANGE (SCTE35-OUT/CMD hex), EXT-X-CUE-OUT[:DURATION]/EXT-X-CUE-IN, EXT-OATCLS-SCTE35, EXT-X-SPLICEPOINT-SCTE35. DASH: EventStream schemeIdUri `urn:scte:scte35:2014:xml+bin` or `urn:scte:scte35:2013:xml`. Commands: splice_insert (0x05), time_signal (0x06)+segmentation descriptors. Ad-triggering type IDs: 0x22 Break Start, 0x30 Provider Ad Start, 0x32 Distributor Ad Start, 0x34/0x36 Placement Opportunity Start — "identical ad-server behavior".
- Relevance: In DAI practice the fine SCTE-35 taxonomy collapses to "ad break start/end"; AdVTT should not over-model provider/distributor distinctions.

### S24. SCTE-35 segmentation_type_id table (docs.rs `scte35` crate enum) — https://docs.rs/scte35/latest/scte35/types/enum.SegmentationType.html
- Type: repo (mirrors ANSI/SCTE 35 table 22; the SCTE PDF itself is paywalled/registration)
- Verified: fetched
- Key facts: 0x00 Not Indicated, 0x01 Content Identification, 0x10 Program Start, 0x11 Program End, 0x20/0x21 Chapter Start/End, 0x22/0x23 Break Start/End, 0x24–0x27 Opening/Closing Credit (deprecated), 0x30/0x31 Provider Advertisement Start/End, 0x32/0x33 Distributor Advertisement Start/End, 0x34–0x37 Provider/Distributor Placement Opportunity, 0x38–0x3B Overlay Placement Opportunity, 0x3C/0x3D Provider Promo Start/End, 0x3E/0x3F Distributor Promo, 0x40/0x41 Unscheduled Event, 0x42/0x43 Alternate Content Opportunity, 0x44/0x45 Provider Ad Block, 0x46/0x47 Distributor Ad Block, 0x50/0x51 Network Start/End.
- Relevance: The only widely deployed *industry* vocabulary distinguishing Advertisement vs Promo vs Program vs Chapter vs Credits. AdVTT's ADVERTISEMENT/PROMOTION/PROGRAM map cleanly to 0x30, 0x3C, 0x10; SPONSORSHIP has no SCTE-35 equivalent (broadcast treats sponsor billboards as ads). Worth publishing a mapping table, not adopting the numeric IDs.

### S25. AWS Elemental MediaTailor — DASH ad markers — https://docs.aws.amazon.com/mediatailor/latest/ug/dash-ad-markers.html
- Type: product docs
- Verified: fetched
- Key facts: Requires EventStream `schemeIdUri=urn:scte:scte35:2013:xml` (or 2014:xml+bin), SpliceInsert with `outOfNetworkIndicator="true"`, or TimeSignal + SegmentationDescriptor with segmentationTypeId in {0x22,0x23,0x30,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39}. Example decoded splice_insert shows `break_duration` 24 s.
- Relevance: Same collapse as S23: the DAI ecosystem consumes "avail start + duration" and ignores finer semantics. Confirms start+duration (not start+end) is the broadcast idiom.

### S26. WebVMT: The Web Video Map Tracks Format (draft) — https://w3c.github.io/sdw/proposals/geotagging/webvmt/
- Type: spec (W3C Note / draft)
- Verified: fetched
- Key facts: W3C Note, "experimental only", "not widely reviewed"; borrows WebVTT's "HTML binding and its block and cue structures"; payloads are JSON commands (map pan/zoom/paths) rather than text.
- Relevance: Direct precedent for a WebVTT-derived, JSON-payload timed-metadata format going through W3C (Spatial Data on the Web); shows the community path exists but has stayed in Note/draft status for ~7 years — a caution on expectations.

### S27. Google Search Central — Video structured data (Key moments) — https://developers.google.com/search/docs/appearance/structured-data/video
- Type: spec/product docs
- Verified: fetched
- Key facts: `hasPart` → `Clip` requires `name`, `startOffset` (seconds from start), `url` (deep link); `endOffset` recommended. `SeekToAction` alternative uses `target` URL template with `{seek_to_second_number}` and `startOffset-input`. BroadcastEvent for LIVE badges. YouTube handled via description timestamps.
- Relevance: schema.org `Clip` (startOffset/endOffset in seconds) is the web-indexable way to expose segments; an AdVTT JSON-LD export (`Clip` with `name:"Advertisement"`) would be valid but Google shows clips as navigation, so labelling ads as key moments is of dubious value.

### S28. YouTube Help — Video chapters — https://support.google.com/youtube/answer/9884579
- Type: product docs
- Verified: fetched
- Key facts: "Make sure that the first timestamp you list starts with 00:00"; at least three timestamps; "The minimum length for video chapters is 10 seconds"; ascending order; automatic chapters on by default; no ad/sponsor chapter type.
- Relevance: Apple copied exactly these rules (S14/S45). Any chapter-based export must synthesise a 00:00 content chapter and satisfy the ≥3 / ≥10 s rules or the whole chapter list is ignored.

### S29. W3C Community and Business Group Process — https://www.w3.org/community/about/process/
- Type: legal/process
- Verified: fetched
- Key facts: A CG proposal is complete with a name, scope and "Five individuals" supporting it. Reports: Draft Community Group Report (under CLA) vs Final Specification (participants sign the Final Specification Agreement; "published on the W3C Web site"). Must not cause "confusion about [the specification's] status ... with respect to W3C Technical Reports". FSA smooths IPR transition to a Working Group.
- Relevance: Cheapest credible publication path with a w3.org URL: form or join a CG (five people), publish a Draft CG Report of "ADVTT profile of WebVTT metadata". Realistic alternative: publish under the project's own domain with a versioned URL and register nothing.

### S30. Praat — TextGrid file formats — https://www.fon.hum.uva.nl/praat/manual/TextGrid_file_formats.html
- Type: spec (tool manual)
- Verified: fetched
- Key facts: header `File type = "ooTextFile"`, `Object class = "TextGrid"`; xmin/xmax seconds; IntervalTier (intervals with xmin, xmax, text) and TextTier (points with number, mark); long vs short text formats, both read by Praat.
- Relevance: A trivial exporter (one IntervalTier "ads") makes AdVTT output inspectable in Praat next to the waveform — useful for the hand-labelling workflow behind the 4 fixtures, not for end users.

### S31. IAB Tech Lab — Podcast Measurement Technical Guidelines v2.3 (public comment draft, July 2026) — https://iabtechlab.com/wp-content/uploads/2026/07/PubComment-PodcastMeasurement_v2.3.pdf
- Type: spec (industry guideline)
- Verified: fetched (PDF saved; first-pass extraction poor — pdftotext pass pending, see later entry)
- Key facts (from search snippets of v2.2, https://iabtechlab.com/wp-content/uploads/2024/02/PodcastMeasurement_v2.2_final.pdf, snippet-only): Pre-roll = "first two minutes of podcast content, either before the content starts or after a quick intro"; Mid-roll = within content; Post-roll = after content and credits. Distinguishes "integrated" (baked-in, historically host-read) from "dynamically inserted" ads; defines "Ad Delivered" by bytes of the ad portion downloaded.
- Relevance: IAB's position taxonomy (pre/mid/post) and delivery taxonomy (integrated vs dynamically inserted) are the industry's words; AdVTT's `kind` should reuse them (`preroll|midroll|postroll` + `delivery: baked-in|dai|unknown`) rather than inventing new ones.

### S32. IAB Tech Lab — VAST 4.2 (June 2019) — https://iabtechlab.com/wp-content/uploads/2019/06/VAST_4.2_final_june26.pdf
- Type: spec
- Verified: fetched (PDF saved; text extraction pending)
- Key facts: pending pdftotext pass (Ad `sequence` attribute/Ad Pods, `adType` audio, `Category` with `authority`).
- Relevance: pending.

### S33. Apple — Getting Started with HLS Interstitials (PDF) — https://developer.apple.com/streaming/GettingStartedWithHLSInterstitials.pdf
- Type: spec
- Verified: fetched (PDF saved; text extraction pending)
- Key facts: pending pdftotext pass (CLASS com.apple.hls.interstitial; X-ASSET-URI/LIST, X-RESUME-OFFSET, X-PLAYOUT-LIMIT, X-RESTRICT SKIP/JUMP, X-SNAP, CUE PRE/POST/ONCE).
- Relevance: pending.

### S34. Search: "Apple Podcasts transcripts podcast:transcript ..." — candidates: Apple Newsroom 2024-03 https://www.apple.com/newsroom/2024/03/apple-introduces-transcripts-for-apple-podcasts/ ; Apple creators support https://podcasters.apple.com/support/5316-transcripts-on-apple-podcasts ; Podnews FAQ https://podnews.net/article/apple-podcasts-transcriptions-faq ; 9to5mac 2025-11-06 iOS 26.2 chapters
- Type: product / blog
- Verified: snippet-only
- Key facts: Apple Podcasts implemented `<podcast:transcript>` in March 2024 accepting VTT and SRT; 13 languages by Nov 2025 (approx., snippet); back catalogue transcribed. iOS 26.2 adds AI chapters and "timed links that surface as a banner at the right moment".
- Relevance: Apple accepts creator VTT — but only as transcripts. "Timed links" (a banner at a moment) is the first Apple UI that is an in-episode timed *event*, adjacent to what an ad marker would drive.

### S35. Search: SponsorBlock categories/actionTypes — candidates: https://wiki.sponsor.ajay.app/w/Segment_Categories ; https://blog.ajay.app/categories-sponsorblock/ ; sponsorblock.py API reference
- Type: product / repo
- Verified: snippet-only (API page fetch pending)
- Key facts: categories sponsor, selfpromo, interaction, intro, outro, preview, music_offtopic, poi_highlight, filler (+ exclusive_access, chapter per API); action types include skip (also mute/full/poi/chapter per API docs, to verify).
- Relevance: The de-facto crowd-sourced ad-skip vocabulary for video with millions of users; `sponsor` vs `selfpromo` vs `interaction` maps onto AdVTT's ADVERTISEMENT/SPONSORSHIP vs PROMOTION(house) vs (new) INTERACTION. Compatibility with SponsorBlock's JSON (segment [start,end], category, actionType) is cheap and gives immediate consumers (many players have SponsorBlock plugins).

### S36. Search: Podcast Namespace proposal process — candidates: repo README https://github.com/Podcastindex-org/podcast-namespace ; "Phase 7 - The Plan" discussion #554; "Phase 6 - The Plan" #493
- Type: process
- Verified: snippet-only
- Key facts: adoption requires "consensus around a tag's usefulness and either commitment to adoption by at least 1 host and 1 app" or existing in-the-wild use; phases 1–7 closed, Phase 8 open; proposals live as GitHub Discussions with phase labels.
- Relevance: The concrete bar for an RSS-level ad-marker tag: one host + one app committed. AdVTT + PodcastFetch could be "the app"; a host is the missing partner.

### S37. Search: comskip / MPlayer EDL — candidates: Kodi wiki https://kodi.wiki/view/Edit_decision_list (403 on fetch); MPlayer manual; comskip forum
- Type: product docs
- Verified: snippet-only
- Key facts: EDL line = `start<TAB>end<TAB>action`, seconds; actions 0 Cut, 1 Mute, 2 Scene Marker, 3 Commercial Break (Kodi extension; comskip `edl_skip_field=3` since 0.81.052). Kodi: cut removes the range from the timeline entirely; commercial break shows a skip prompt (approx., snippet).
- Relevance: The oldest living "ad skip" interchange format, consumed by Kodi, MPlayer, Plex/Jellyfin (via comskip), LosslessCut. Emitting `.edl` with action 3 is one line of code and gives AdVTT immediate consumers on the video side; action 3 vs 0 maps exactly to AdVTT's "offer skip" vs "auto-skip" policy.

### S38. Search: RTTM — candidates: dscore README https://github.com/nryant/dscore ; LDC docs
- Type: spec (NIST RT eval)
- Verified: snippet-only (raw README fetch pending)
- Key facts: space-delimited, 10 fields: Type (SPEAKER), File ID, Channel (1), Onset s, Duration s, Ortho (NA), Speaker type (NA), Speaker name, Confidence (NA), Lookahead (NA).
- Relevance: Diarization tools (pyannote etc.) emit RTTM; AdVTT can read RTTM to add "speaker changes at ad boundaries" as a feature, and could emit RTTM-shaped rows (`SPEAKER file 1 onset dur <NA> <NA> AD <NA> conf`) for scoring with dscore's DER tooling — a ready-made boundary-error metric.

### S39. Search: Audacity label track format — candidates: https://manual.audacityteam.org/man/importing_and_exporting_labels.html
- Type: product docs
- Verified: snippet-only
- Key facts: tab-separated `.txt`: start seconds, end seconds, label text; point labels have start==end; optional spectral rows.
- Relevance: Cheapest human-review round-trip: export ads as Audacity labels, reviewer nudges edges, re-import as ground truth for the fixtures.

### S40. Search: QuickTime/Nero MP4 chapters — candidates: ffmpeg-cvslog 2014-08 "movenc: Add option to disable nero chapters" https://ffmpeg.org/pipermail/ffmpeg-cvslog/2014-August/080079.html ; mp4v2 mp4chaps ; atldotnet wiki "Focus on Chapter metadata"
- Type: repo / docs
- Verified: snippet-only
- Key facts: Two MP4 chapter mechanisms: QuickTime chapter *text track* referenced via `tref/chap`, and Nero `moov.udta.chpl`. ffmpeg movenc writes both by default; `-movflags disable_chpl` writes only the QT track (Nero chapters broke iTunes 11.3/mp3Tag 2.61a).
- Relevance: M4A podcast chapters are readable by Apple via the QT chapter track; AdVTT via ffmpeg gets both for free. No hidden/kind flag exists in either, so ad chapters are always visible chapters in MP4.

### S41. Search: SCTE-224 ESNI — candidates: ANSI webstore SCTE 224 2015/2018/2020r1/2021
- Type: spec (paywalled)
- Verified: snippet-only
- Key facts: XML data model of Media/MediaPoint/Policy/ViewingPolicy/Audience for schedule- and signal-based events; "ViewingPolicy actions for advertisement inclusion, exclusion"; latest ANSI/SCTE 224 2021.
- Relevance: Policy-layer (who may see what), not a marker format; not worth mapping. Documented as out of scope.

### S42. Search: apps supporting podcast:chapters — candidates: AntennaPod PR #5630 "Support for podcast 2.0 chapters"; Pocket Casts forum "Support for better chapter"; Audacity PR #9935 "podcast chapters json export"; Captivate/Buzzsprout help
- Type: repo / forum
- Verified: snippet-only
- Key facts: AntennaPod merged JSON chapters (PR #5630); Pocket Casts "started looking into" Podlove/PC2.0 chapters, no timeline (forum, undated snippet); Audacity 3 has a JSON-chapters export PR; "most Podcasting 2.0 apps support cloud chapters" (snippet). No authoritative machine-readable support matrix found — podcastindex.org/apps not fetched (gap).
- Relevance: JSON chapters are consumed by AntennaPod, Apple (Dec 2025), Castopod, and the PC2.0 app family; ID3 CHAP by Apple, Overcast, Pocket Casts (approx., long-standing). Emit both.

### S43. Search: Apple automatic chapters FAQ — candidates: Podnews https://podnews.net/article/apple-chapters-faq ; 9to5mac 2025-11-04; Apple support 5482
- Type: blog / product
- Verified: snippet-only (Apple support page fetch pending)
- Key facts: Apple reads ID3, episode-notes timestamps and "JSON Chapters (the Podcasting 2.0 standard)"; requirements "first chapter starts at 00:00:00 and you have at least three chapters"; no auto chapters for trailers or episodes < 10 min; creator chapters override auto ones.
- Relevance: See S28 — any AdVTT chapter export must include content chapters (or merge into existing ones) to be accepted.

### S44. Search: CMX3600 EDL — candidates: pycmx https://github.com/iluvcapra/pycmx ; OpenTimelineIO cmx_3600 adapter
- Type: spec (de-facto, 1970s CMX)
- Verified: snippet-only
- Key facts: columns: event number (001–999), reel (≤8 chars), track (V, A, AA, AA/V...), transition (C/D/W), source in/out, record in/out timecodes.
- Relevance: Editing-suite interchange (Resolve/Premiere via OTIO). Only relevant if AdVTT is used to *cut* ads out for re-publication; a CMX3600 with "C" events omitting ad ranges is a possible optional export. Low priority.

### S45. Search: ELAN EAF — candidates: CLARIN SIS "ELAN Annotation Format" https://standards.clarin.eu/sis/views/view-spec.xq?id=SpecEAF ; MPI manual
- Type: spec
- Verified: snippet-only
- Key facts: XML ANNOTATION_DOCUMENT ⊃ TIME_ORDER/TIME_SLOT (ms), TIER ⊃ ALIGNABLE_ANNOTATION (TIME_SLOT_REF1/2). Linguistics tool.
- Relevance: Niche; skip unless an academic collaborator asks. Documented for completeness.

### S46. Search: IMSC / TTML2 / EBU-TT — candidates: https://www.w3.org/TR/ttml-imsc1.2/ (REC 4 Aug 2020); W3C news 2026 "Proposed advancement of IMSC Text Profile 1.3"; EBU Tech 3350/3380 (not fetched)
- Type: spec
- Verified: snippet-only
- Key facts: IMSC 1.2 is a W3C Recommendation (2020-08-04); IMSC 1.3 proposed REC in 2026; TTML2 REC 2018-11-08; EBU-TT-D is the broadcast profile these converge with.
- Relevance: TTML has a real `ttm:`/metadata model and is a REC (WebVTT is not), but no browser renders TTML natively and podcast apps ignore it; not a target. Note the irony: the more "standard" format has the fewer consumers.

### S47. Search: "application/json+chapters" IANA — candidates: RFC 6838, RFC 6839, IANA media-types registry, podcasting2.org chapters doc
- Type: spec / registry
- Verified: snippet-only (negative result)
- Key facts: No IANA registration found for `application/json+chapters`; RFC 6838 §4.2.8 structured-syntax suffix convention is `application/chapters+json` (suffix last). The Podcasting 2.0 type is therefore unregistered and syntactically backwards, yet universally used by hosts and apps.
- Relevance: Precedent that the podcast ecosystem tolerates unregistered media types; if AdVTT defines a JSON format, use the correct `application/<name>+json` shape and consider an IANA vendor-tree (`application/vnd.advtt+json`) or just document it.

### S48. Search: HLS ID3 timed metadata vs DASH emsg — candidates: Unified Streaming docs (ID3, SCTE-35, SMIL timed metadata) https://docs.unified-streaming.com/documentation/vod/id3.html ; THEOplayer "Timed Metadata"; AWS MediaLive insert-timed-metadata
- Type: product docs
- Verified: snippet-only
- Key facts: HLS: in-band ID3 in TS/CMAF (`emsg` with ID3 scheme for fMP4) + out-of-band EXT-X-DATERANGE; DASH: MPD EventStream + in-band `emsg`. Used for "dynamic content replacement, ad insertion, presentation of supplemental content".
- Relevance: All streaming carriers are *manifest- or segment-level*; none apply to a downloaded podcast MP3. The only in-file carriers for podcasts remain ID3 (CHAP/CTOC, or TXXX/PRIV private frames) and MP4 chapter tracks.

### S49. Search: TextTrackCue with HTML / constructor — candidates: WebKit explainers https://github.com/WebKit/explainers/tree/main/texttracks ; Chromium blink-dev "Intent to Deprecate: TextTrackCue constructor" (2014) ; W3C 2019-09-18 "Next Generation TextTrackCue" minutes
- Type: repo / minutes
- Verified: snippet-only (WebKit README fetch pending)
- Key facts: Blink deprecated the TextTrackCue constructor ~2014; WebKit's explainer proposes `new TextTrackCue(start, end, cueNode: DocumentFragment)`; ten years of incubation.
- Relevance: Reinforces S4/S5: design for `VTTCue` + text payload; treat everything else as future.


### S50. ffmpeg doc/metadata.texi — FFMETADATA1 — https://ffmpeg.org/ffmpeg-formats.html#Metadata-2 (read raw https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/doc/metadata.texi)
- Type: spec/docs
- Verified: fetched
- Key facts: file starts `;FFMETADATA1`; `key=value` global tags; `[CHAPTER]` sections with optional `TIMEBASE=num/den` (default nanoseconds), required `START=`/`END=` positive integers, `title=`; `[STREAM]` sections; `=`, `;`, `#`, `\` and newline escaped with backslash; lines starting `;` or `#` are comments; whitespace is significant.
- Relevance: One-file, no-re-encode chapter injection into MP3/M4A/MKV via `-map_chapters`; ideal "sidecar you can apply yourself" export. Only title + arbitrary key=value per chapter, so kind/confidence ride as extra chapter tags (ffmpeg preserves unknown chapter tags in MKV, not in ID3 CHAP — see S62).

### S51. Apple Podcasts for Creators — Using chapters on Apple Podcasts — https://podcasters.apple.com/support/5482-using-chapters-on-apple-podcasts
- Type: product docs
- Verified: fetched
- Key facts: Three sources: episode description timestamps; RSS "the <podcast:chapters> tag"; "chapters in the header of an MP4 file or by modifying the ID3 tags of an MP3 or AAC file". Rules: "Start the first chapter at 00:00:00", "Include at least three chapters", "Provide chapters if your episode is more than 10 minutes long". Auto chapters: "creates chapters for full and bonus episodes in English", opt-out in Availability tab. Images only via hosting provider (JSON). No precedence documented.
- Relevance: Confirms both JSON chapters and ID3 CHAP are consumed by Apple; confirms the ≥3 / 00:00:00 constraints that make a chapters-only ad export impractical without content chapters.

### S52. Podlove Simple Chapters 1.1 — https://podlove.org/simple-chapters/
- Type: spec
- Verified: fetched
- Key facts: XML namespace `http://podlove.org/simple-chapters`; `<psc:chapters version>` ⊃ `<psc:chapter start title href image>`; `start` in Normal Play Time (e.g. `01:35:52`, `35:12.250`, `37`); no end time, no kind. Widely used in German-speaking podcasting (Podlove/Ultraschall, Podcast Addict, AntennaPod support — approx., not verified here).
- Relevance: Third chapter dialect podcast apps parse (in-RSS). Cheap to emit for completeness; start-only semantics mean an ad "chapter" needs a following content chapter to bound it.

### S53. schema.org `Clip` — https://schema.org/Clip
- Type: spec (vocabulary)
- Verified: fetched
- Key facts: `startOffset`/`endOffset`: Number or HyperTocEntry, "number of seconds from the beginning of the work"; `clipNumber`; `partOfEpisode`; subtypes MovieClip, RadioClip, TVClip, VideoGameClip. (Also `HyperToc`/`HyperTocEntry` exist for tables of contents.)
- Relevance: A JSON-LD `hasPart: [Clip]` export is the only SEO-visible segment vocabulary; possible for episode web pages, but Google surfaces clips as navigation (S27), so labelling ads is low value. `RadioClip` is the podcast-appropriate subtype.

### S54. RFC 6906 — The 'profile' Link Relation Type — https://www.rfc-editor.org/rfc/rfc6906
- Type: spec (IETF Informational, March 2013)
- Verified: fetched
- Key facts: profile = "conforms to a certain profile, without affecting the non-profile semantics of the resource representation"; "A profile MUST NOT change the semantics of the resource representation when processed without profile knowledge".
- Relevance: Gives AdVTT the right word and the right constraint: an "ADVTT profile of text/vtt" must remain a valid WebVTT file to profile-ignorant parsers (it does — S1, S61). A profile URI (e.g. `https://advtt.dev/profile/0.1`) can be carried in the WEBVTT header line text and in `Link: rel="profile"`.

### S55. WebVMT: The Web Video Map Tracks Format (W3C Note) — https://www.w3.org/TR/webvmt/
- Type: spec
- Verified: fetched
- Key facts: "This document is a Note, it has not been widely reviewed and should be considered as experimental only." Published 19 September 2023 by the Spatial Data on the Web WG. WebVTT-derived block/cue structure with JSON payloads.
- Relevance: The closest precedent for an AdVTT-like "WebVTT-shaped, JSON-payload" format reaching a /TR/ URL; it took a Working Group (not a CG) and still ended as an experimental Note. Sets expectations for the "publish a profile" question (Q7).

### S56. WebKit explainers — TextTrackCue enhancements — https://github.com/WebKit/explainers/tree/main/texttracks
- Type: repo (explainer)
- Verified: fetched (raw README)
- Key facts: proposes `new TextTrackCue(startTime, endTime, cueNode)` with a DocumentFragment; "TextTrackCue has no constructor today"; authors Eric Carlson, Theresa O'Connor, Marcos Cáceres; "initially presented at TPAC 2019 and again at TPAC 2023"; no shipping status.
- Relevance: Rendering-oriented; not a metadata carrier. Reinforces: VTTCue.text is the only portable payload in 2026.

### S57. MDN — TextTrack.mode — https://developer.mozilla.org/en-US/docs/Web/API/TextTrack/mode
- Type: docs
- Verified: fetched
- Key facts: `disabled`: no cues active, no events, file not even loaded; `hidden`: "active but cues aren't being displayed", events fire, `activeCues` maintained; `showing`: displayed. Default `disabled` unless `<track default>`. Safari quirk: needs `default` for custom controls to show subtitles.
- Relevance: Player prototype must set `track.mode = "hidden"` (or `addTextTrack("metadata")`) — a metadata `<track>` without that line silently never loads.

### S58. MDN — `<track>` element — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/track
- Type: docs
- Verified: fetched
- Key facts: `kind` values subtitles (default), captions, descriptions, chapters, metadata ("Tracks used by scripts. Not visible to the user."); invalid values fall back to metadata; Baseline "Widely available" since July 2015.
- Relevance: `kind=metadata` WebVTT is universally supported in browsers; the only interoperability risk is the payload convention, not the carrier.

### S59. AudioSet — download page / CSV format — https://research.google.com/audioset/download.html
- Type: dataset
- Verified: fetched
- Key facts: `# YTID, start_seconds, end_seconds, positive_labels`; e.g. `-0RWZT-miFs, 420.000, 430.000, "/m/03v3yw,/m/0k4j"`; fixed 10 s segments; labels are Knowledge Graph mids mapped via class_labels_indices.csv.
- Relevance: Template for a *research CSV* export of AdVTT labels (episode_id, start, end, labels) that ML people will recognise; not a distribution format.

### S38 (update). RTTM via dscore README — https://github.com/nryant/dscore — Verified: fetched
- Confirmed 10 fields; example `SPEAKER CMU_20020319-1400_d01_NONE 1 130.430000 2.350 <NA> <NA> juliet <NA> <NA>`; fields 6, 7, 9, 10 are `<NA>`. Note the confidence field exists but "should always be <NA>" in dscore's convention.

### S36 (update). Podcast Namespace README — https://github.com/Podcastindex-org/podcast-namespace — Verified: fetched
- Exact criterion: "consensus around a tag's usefulness and either commitment to adoption by at least 1 host and 1 app, or a recognition that the tag is already being used in the wild." Phases 1–7 closed (Phase 7 closed 2024-07-01, 2 tags); Phase 8 open; proposals via GitHub Discussions.

### S60. Podnews — Apple Podcasts: automatic chapters FAQ — https://podnews.net/article/apple-chapters-faq
- Type: blog
- Verified: fetched
- Key facts: first published 4 Nov 2025, updated 21 Apr 2026. Apple reads ID3, Episode Notes, JSON Chapters; JSON "also supports links and full-resolution images"; on `toc="false"`: "We've not tested that Apple supports this"; auto chapters only for ≥10-minute episodes; nothing on dynamic ad insertion or `endTime`.
- Relevance: `toc:false` behaviour in Apple is unverified → an experiment for AdVTT (publish a test feed with hidden ad chapters).

### S31 (update). IAB Podcast Technical Measurement Guidelines v2.3 — text extracted with pdftotext
- "Draft for Public Comment released July 21st, 2026"; comments due August 21st, 2026.
- §4.2 Integrated Ads: "These ads are part of the content and included, or 'baked-in,' with the episode". §4.3 Dynamically Inserted Ads: "ads to be targeted and dynamically inserted at the time of [request]". "Ads that directly sponsor a podcast episode have typically been host-read, or integrated"; sponsorships "can be dynamically inserted".
- Pre/mid/post-roll: see snippet-verified v2.2 wording in original S31 entry; v2.3 text mentions "a 30 second pre-roll ad" in the validity example.
- Relevance: Industry taxonomy = {integrated/baked-in, dynamically inserted} × {pre, mid, post}. Note IAB treats "host-read" as a *style* typically co-occurring with "integrated", not as a category — AdVTT should keep `delivery` and `read_style` as separate optional fields.

### S32 (update). VAST 4.2 — text extracted with pdftotext
- §1.4 Audio Ad Support: DAAST (2014) merged back into VAST 4.x; `<Ad>` gains optional `adType` attribute (video | audio | hybrid); "icons are not a requirement when the adType is 'audio' or 'hybrid'".
- §3.3.1 Ad Pods and Stand-Alone Ads: pods "are distinguished by using the sequence attribute for an <Ad>, denoting which ad plays first, second, and so on."
- §3.4.5 Category element with `authority` attribute (IAB content taxonomy URL); error 204 "Ad category was required but not provided".
- Relevance: VAST is a *serving* template, not a timeline annotation; the reusable ideas are `sequence` (ordinal within a break) and `Category`+`authority` (categorisation with an explicit taxonomy URL). AdVTT could adopt `authority`-style taxonomy URIs for its kind vocabulary.

### S33 (update). Apple — Getting Started with HLS Interstitials, Version 1.0b3, May 12 2021 — text extracted with pdftotext
- "The CLASS attribute is required. Its value must be 'com.apple.hls.interstitial'." X-ASSET-URI (single asset) or X-ASSET-LIST (JSON) — exactly one. X-RESUME-OFFSET (seconds, default = interstitial duration; 0 for ads that do not consume primary timeline). X-PLAYOUT-LIMIT (seconds cap). X-SNAP (SNAP-OUT/SNAP-IN to segment boundaries). X-RESTRICT: "Navigation Restriction Identifiers ... SKIP and JUMP"; SKIP = client should not allow seeking within the interstitial; JUMP = must not seek across it from before to after. Vendors may add `X-<REVERSE-DNS>` attributes (example `X-COM-EXAMPLE-BEACON=123`). Example: `ID="ad1",CLASS="com.apple.hls.interstitial",...,DURATION=15.0,...,X-RESTRICT="SKIP,JUMP"`.
- Relevance: The most modern Apple-authored ad-marking grammar: an ID, a reverse-DNS CLASS, a start + DURATION, and a *policy* (SKIP/JUMP restrictions). AdVTT's inverse ("skippable: true/false", "auto_skip_allowed") mirrors X-RESTRICT and should use the same explicit-policy style rather than implying policy from the kind.

### S61. Local experiment (this Mac, ffmpeg 8.1.1, 2026-09-01): two-line AdVTT payload through ffmpeg/WebM/MKV/MP4
- Type: experiment
- Verified: ran locally (files under scratchpad/vtt)
- Setup: `ads.vtt` with header `WEBVTT ADVTT/0.1`, a `NOTE ADVTT/0.1 ...` block, cue ids `ad-1`/`ad-2`, payload line 1 = token (`ADVERTISEMENT`), line 2 = JSON containing `<Co>`, `&`, and the literal `-->` inside a string.
- Results:
  - ffprobe with `-kind metadata` sets `disposition:metadata=1`; muxing to WebM (`-c:s copy`) yields a webvtt stream with `disposition:metadata=1` (→ `D_WEBVTT/METADATA`, S19). Muxing to MKV: stream is webvtt but `disposition:metadata=0` (kind lost, S18).
  - Extracting back to .vtt from WebM: **both payload lines byte-identical**, including the `-->` inside the JSON string and `<Co> &`; but the header text after `WEBVTT` and the NOTE block were **dropped** (ffmpeg's webvtt muxer writes a bare `WEBVTT`), and timestamps re-serialised as `00:05.000` (mm:ss). Semantically lossless for cues, lossy for header/NOTE.
  - MKV round trip: same, plus a **+25 ms shift** on every cue (`00:05.025`) — MP3 decoder delay/priming offset applied by the muxer. Not a WebVTT problem, but a real boundary error source (boundary_err_sec gate is 3 s so tolerable; still, document it).
  - MP4: `webvtt` codec "not currently supported in container" (ffmpeg has no ISO 14496-30 WebVTT muxer path here); `-c:s mov_text` works but the JSON came back as `\{{}"advertiser":"Acme  & Sons"...` — braces mangled and `<Co>` stripped as markup. **MP4 text tracks are not a safe carrier for JSON payloads via ffmpeg.**
- Relevance: (1) Two-line payload survives real parsers; (2) `NOTE ADVTT/0.1` does not survive any remux, so version/profile info must be in-cue or in a sidecar JSON; (3) recommend WebM/MKV embedding as optional, MP4 embedding via chapters only.

### S62. Local experiment (ffmpeg 8.1.1): FFMETADATA1 chapters → MP3 ID3 CHAP/CTOC, M4A, MKA, and back
- Type: experiment
- Verified: ran locally
- Results: `-map_metadata 1 -map_chapters 1 -c copy -id3v2_version 3` wrote 3 `CHAP` + 1 `CTOC` frames into the MP3; ffprobe reads back 3 chapters with titles. M4A got both a QuickTime chapter track (`tref/chap`, stream `bin_data`) and a Nero `chpl` atom (matches S40). MKA chapters stored at 1/1e9 timebase exactly. **Round-trip MP3 → ffmetadata shifted every chapter by −25 ms (START=4975)**, again the MP3 priming/delay offset — ID3 CHAP times are file-absolute ms and ffmpeg subtracts start_time on read.
- Relevance: The full chapter tool-chain works with zero re-encode; expect ±1 MP3 frame (26 ms) drift between "seconds into decoded audio" and "ID3 CHAP ms". AdVTT should define its time origin explicitly (decoded-sample time = what STT reports) and note that CHAP writers may differ by one frame.


### S63. Matroska element list — ChapterSkipType — https://www.matroska.org/technical/elements.html (normative text also in RFC 9559, Oct 2024, Standards Track — https://www.rfc-editor.org/rfc/rfc9559.html)
- Type: spec
- Verified: fetched (elements page; RFC page fetched but truncated before this section)
- Key facts: `ChapterSkipType`, EBML ID 0x4588, path Chapters/EditionEntry/ChapterAtom, uinteger, minver Matroska v4. Definition: "Indicates what type of content the ChapterAtom contains and might be skipped. It can be used to automatically skip content based on the type." Values: 0 No Skipping, 1 Opening Credits, 2 End Credits, 3 Recap, 4 Next Preview, 5 Preview, **6 Advertisement**, 7 Intermission. `ChapterFlagHidden`: "Hidden chapters SHOULD NOT be available to the user interface". `ChapterFlagEnabled`: "When disabled, the movie SHOULD skip all the content between the TimeStart and TimeEnd of this chapter".
- Relevance: **The only container standard with an explicit "Advertisement — may be auto-skipped" chapter type.** For MKV/WebM/MKA output AdVTT can write ChapterSkipType=6 on ad chapters (plus FlagHidden if desired) — a lossless, standards-blessed carrier. Player support (mpv/VLC) unverified (see Open questions). Also a vocabulary precedent: Matroska separates *content type* (Advertisement, Preview, Recap) from *policy* (Enabled/Hidden), exactly the split AdVTT should make.

### S64. sponsorblock.py API reference (documents the SponsorBlock server schema) — https://sponsorblockpy.readthedocs.io/en/latest/api_reference.html (primary wiki https://wiki.sponsor.ajay.app/w/API_Docs returned "Access Denied"/Anubis)
- Type: repo docs
- Verified: fetched (secondary); primary blocked
- Key facts: Segment fields: `category`, `start`, `end` (seconds), `uuid`, `duration` (video duration, used to detect re-uploads), `action_type`, `locked`, `votes`, `description` ("chapter title for chapter segments"). Categories: sponsor, selfpromo, interaction, intro, outro, preview, hook, music_offtopic, poi_highlight, filler, exclusive_access, chapter. Action types: skip, mute, full, poi, chapter.
- Relevance: The de-facto JSON schema for community ad-skipping (YouTube; supported in mpv, NewPipe, Kodi, many players). Two lessons: (1) *category × actionType* — content type separate from what to do about it (skip / mute / full = whole video is sponsored); (2) `videoDuration` as a cheap "is this the same file" fingerprint. AdVTT can emit a SponsorBlock-shaped JSON (`sponsor`/`selfpromo`, actionType `skip`) for players with SponsorBlock plugins.

### S65. MPlayer documentation — Edit Decision Lists — https://mplayerhq.hu/DOCS/HTML/en/edl.html
- Type: docs
- Verified: fetched
- Key facts: line = `[begin second] [end second] [action]`, floats in seconds; 0 = skip, 1 = mute; `-edl file`, `-edlout file`; example `5.3 7.1 0`. (Kodi adds 2 = scene marker, 3 = commercial break — snippet-only, S37.)
- Relevance: 20-year-old, still-consumed skip format; AdVTT `.edl` export (action 3 for "commercial break" where Kodi shows a skip prompt; 0 only when the user opts into auto-skip) costs nothing and respects the false-positive asymmetry.

### S66. Overcast — Podcaster info — https://overcast.fm/podcasterinfo
- Type: product docs
- Verified: fetched
- Key facts: "Overcast displays MP3 and M4A chapter markers with titles, images, and/or link URLs." No mention of `podcast:chapters` JSON.
- Relevance: Second-tier apps still rely on in-file chapters (ID3 CHAP / M4A); embedding is required to reach them.

### S67. Podnews — Spotify enhances chapter support — https://podnews.net/update/spotify-chapters
- Type: blog
- Verified: fetched
- Key facts: 3 Jan 2023; Spotify chapters come from **timestamps in the episode description** only; "does not support ID3 embedded chapters or the podcast namespace standard" (as of that date; no newer primary source found this session).
- Relevance: The second-largest app reads none of the machine-readable chapter carriers — description timestamps are the lowest common denominator, and a place where "Ad: Acme 12:05" lines would be user-visible but unstructured.

### S68. Podcast Namespace example.json (chapters) — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/examples/chapters/example.json
- Type: spec example
- Verified: fetched
- Key facts: `"version": "1.2.0"`, nine chapters using only startTime/title/img/url; no toc/endTime/location in the canonical example.
- Relevance: Real-world parsers are tested against start-only chapters; `endTime` and `toc:false` are the least-exercised parts of the spec (matches Podnews' "not tested" in S60). Do not rely on them for ad boundaries without a fallback content chapter after each ad.

### S69. Search attempts that failed this session (documented gaps)
- podcastindex.org/apps (HTTP 403) — no machine-readable per-app chapter-support matrix obtained.
- VMAP 1.0.1 PDF at iab.com (404 on both guessed URLs) — VMAP AdBreak `timeOffset`/`breakType` details not verified from the primary; the IAB overview page (fetched) only states VMAP is "an XML template that video content owners can use to describe the structure for ad inventory insertion".
- Kodi wiki EDL page (403 twice) — Kodi action-3 behaviour is snippet-only.
- GitHub Discussions search for "ad markers" in podcast-namespace (page failed to render). No namespace proposal for time-ranged ad markers was found by any route; nearest are #669 disclosure (untimed) and #548 "Signal to auto-refresh chapters and transcripts" (2023-06-26, seen in the partial render).
- SCTE-35 and SCTE-224 primary PDFs are behind SCTE registration; the segmentation table was verified against two independent implementations (S24, S25).


### S70. Podcast Namespace discussion #548 — "Signal to auto-refresh chapters and transcripts" — https://github.com/Podcastindex-org/podcast-namespace/discussions/548
- Type: forum (spec proposal)
- Verified: fetched
- Key facts: ryan-lp, 26 Jun 2023; problem includes "dynamic content insertion ... can cause chapters and transcripts to become misaligned with downloaded audio"; proposes HTTP 503 + Retry-After while assets are processing; alternatives: `final="YES/NO"` attribute, ETags, metadata inside the chapter/transcript files; no consensus, 8 participants.
- Relevance: The namespace community knows sidecar timings break under DAI but has no fix. AdVTT's output is computed *from the delivered file*, so it is DAI-safe by construction — a differentiator worth stating; but AdVTT must fingerprint the exact file (bytes/duration, cf. SponsorBlock `videoDuration`, S64) so consumers can detect a mismatch.

### S71. mpv manual (master) — https://mpv.io/manual/master/ ; mkvmerge manual — https://mkvtoolnix.download/doc/mkvmerge.html
- Type: docs
- Verified: fetched (both; searched for skip-type support)
- Key facts: mpv documents `--chapters-file`, `--chapter-seek-threshold`, `edl://` (its own EDL dialect), but **nothing about ChapterSkipType or auto-skipping chapters**. mkvmerge documents simple (`CHAPTER01=…/CHAPTER01NAME=…`) and XML chapters (ChapterTimeStart/End, ChapterDisplay) but its manual page does not mention ChapterSkipType or WebVTT options (mkvmerge does mux WebVTT in practice — approx., not verified here).
- Relevance: ChapterSkipType=6 is standardised (S63) but has no visible player support in the two most likely tools; writing it is harmless and future-proof, but it cannot be AdVTT's primary skip carrier today.

### S72. podcasting2.org/apps — https://podcasting2.org/apps
- Type: product directory
- Verified: fetched (feature matrix is JS-rendered; only names visible)
- Key facts: lists apps "sorted by most features": TrueFans, Fountain, Podverse, AntennaPod, Pocket Casts, Apple Podcasts, Spreaker… Per-app chapter support not extractable.
- Relevance: Gap remains; the qualitative picture from S14, S42, S51, S66, S67 is: JSON chapters → Apple, AntennaPod, PC2.0 apps; ID3/M4A chapters → Apple, Overcast (and others); description timestamps → Apple, Spotify, YouTube.

### S31 (correction after full-text grep of v2.3). The IAB Podcast Technical Measurement Guidelines v2.3 text contains **no definitions of pre-roll/mid-roll/post-roll** (the only hit is an example "a 30 second pre-roll ad"). The "first two minutes" wording in the earlier snippet came from a third-party search summary (likely Acast's explainer https://www.acast.com/en-us/news-and-insights/pre-roll-mid-roll-post-roll-podcast-ads), not from IAB. IAB's own taxonomy is limited to delivery method: §4.2 Integrated ("baked-in"), §4.3 Dynamically Inserted, §4.4 Sponsorship Ads ("typically been host-read, or integrated"). Position vocabulary (pre/mid/post) is industry vernacular, not an IAB-defined term. The 2016 "IAB Podcast Ad Metrics Guidelines" (https://iabtechlab.com/wp-content/uploads/2016/07/Podcast-Metrics_September_2016.pdf) was not fetched — possible gap.

## Synthesis

**1. WebVTT metadata is legal, universal, and under-specified — exactly the right amount.**
WebVTT is still a Candidate Recommendation Draft (20 May 2026, S1) after 15 years, yet `<track kind="metadata">` has been Baseline in every browser since 2015 (S58). The spec deliberately says nothing about metadata payload structure beyond "no blank lines, no `-->`, no raw CR/LF" (S1). Metadata text is *not* subject to the `<`/`&` escaping rules that apply to cue text (S1), and the local experiment confirmed a two-line payload with literal `<Co> &` and a `-->` inside a JSON string survives ffmpeg's parser and WebM/MKV remux byte-for-byte (S61). The W3C Media Timed Events note explicitly recognises "JSON serialised into a WebVTT cue" as the working pattern (S2). The replacements (DataCue, TextTrackCue constructor, TextTrackCue-with-HTML) are all still incubation in 2025–26 and DataCue was *removed* from WebKit (S3–S5, S49, S56). So: VTTCue.text is the only portable browser API for the foreseeable future.

**Caveats found:** (a) `NOTE` blocks and WEBVTT-header text are comments — browsers never expose them and ffmpeg drops them on remux (S1, S61); a `NOTE ADVTT/0.1` header is documentation, not a version signal. (b) Blank line inside JSON = new cue; JSON must be minified or indented without empty lines. (c) `cuechange` may lag up to 250 ms (S2, S6) — skip logic must seek to `cue.endTime`, never to "now". (d) Metadata tracks default to `disabled`; script must set `mode="hidden"` (S6, S57). (e) MP4 (`mov_text`) mangles JSON braces and strips `<…>` (S61) — never carry the payload as an MP4 text track.

**2. The podcast ecosystem's timeline vocabulary is chapters, and chapters are now everywhere.**
Apple Podcasts (iOS 26.2, Dec 2025) reads JSON `podcast:chapters`, ID3/MP4 chapters and description timestamps, and auto-generates chapters otherwise (S14, S51, S60). AntennaPod, Castopod and the PC2.0 app family read JSON chapters (S42); Overcast reads MP3/M4A embedded chapters (S66); Spotify reads only description timestamps (S67, 2023). JSON Chapters 1.2 offers `startTime`, optional `endTime`, `toc:false` (hidden), `img`, `url` (S8) — but `endTime`/`toc` are absent from the canonical example (S68) and Podnews has "not tested that Apple supports" `toc:false` (S60). Apple/YouTube impose "first chapter at 00:00:00, ≥3 chapters" (S28, S51), so an ad-only chapter file will be rejected; ad chapters must be merged into a full chapter list. Nobody in the namespace has proposed time-ranged ad markers; the nearest proposals are un-timed disclosure (#669, stalled, S13) and "chapters drift under DAI" (#548, no consensus, S70). The namespace's adoption bar is explicit: "at least 1 host and 1 app" (S36). The namespace already carries in-episode time ranges as `startTime`+`duration` seconds in soundbite and valueTimeSplit (S11, S12) — that is the idiom to copy if a tag is ever proposed.

**3. Container-level carriers exist and are lossless at ms precision.**
ID3v2 CHAP/CTOC (S16): 32-bit ms start/end, sub-frames for title/URL/image, hierarchical CTOCs, no kind flag. ffmpeg writes them from FFMETADATA1 with `-map_chapters`, zero re-encode (S20, S50, S62). MP4 gets both a QuickTime chapter track and Nero `chpl` (S40, S62). Matroska has nanosecond chapters, multiple editions, hidden/enabled flags **and `ChapterSkipType` with value 6 = Advertisement, "can be used to automatically skip content based on the type"** (S17, S63; RFC 9559, Oct 2024) — the only container standard that names ads as skippable — though neither mpv nor mkvmerge document support (S71). WebM is the only container with a *metadata-kind* WebVTT track (`D_WEBVTT/METADATA`, TrackType 0x21, S19); plain MKV stores `S_TEXT/WEBVTT` but loses the kind (S18, S61). Timing drift: MP3 priming shifts chapters/cues by one frame (≈25 ms) through ffmpeg round-trips (S61, S62) — well inside the 3 s boundary gate but must be documented.

**4. Broadcast/streaming ad signalling has a rich vocabulary that collapses in practice.**
SCTE-35 segmentation_type_id distinguishes Program (0x10), Chapter (0x20), Break (0x22), Provider/Distributor Advertisement (0x30/0x32), Placement Opportunity (0x34/0x36), Promo (0x3C/0x3E), Ad Block (0x44/0x46), credits (deprecated) (S24). Every DAI vendor examined (Broadpeak, AWS MediaTailor) treats the five "start" ids identically as "ad avail" and consumes *start + duration* (S23, S25). HLS carries this as `EXT-X-DATERANGE` with a reverse-DNS `CLASS` plus `X-` attributes (S22), and Apple's Interstitials add explicit *policy* attributes — `X-RESTRICT="SKIP,JUMP"`, `X-RESUME-OFFSET`, `X-PLAYOUT-LIMIT` (S33). DASH uses EventStream/emsg with `urn:scte:scte35:…` schemes (S23, S25). None of these apply to a downloaded MP3 (S48); their value to AdVTT is vocabulary and structure: *class string + key/values*, *content type separate from playback policy*, *start+duration*. SCTE-224 is a policy/audience layer, out of scope (S41).

**5. IAB gives delivery taxonomy, not position or timeline.**
IAB Podcast Measurement v2.3 (public comment July 2026) defines Integrated/"baked-in", Dynamically Inserted and Sponsorship (typically host-read) — nothing about pre/mid/post-roll or timeline markup (S31 corrected). VAST 4.2 contributes `adType` audio/hybrid, `sequence` (pod ordinal) and `Category authority="…"` (S32); VMAP's `timeOffset`/`breakType` could not be verified from a primary this session (S69). Position words (pre/mid/post-roll) are vernacular — safe to use, but do not claim IAB authority for them.

**6. The nearest "ad skipping" formats are grassroots and trivially simple.**
SponsorBlock: `{segment:[start,end], category, actionType, videoDuration, UUID, votes, locked}` with categories sponsor/selfpromo/interaction/intro/outro/preview/filler/hook/exclusive_access/… and actionTypes skip/mute/full/poi/chapter (S64) — millions of users, many player plugins. MPlayer/Kodi EDL: `start<TAB>end<TAB>action` seconds, 0 cut / 1 mute / (Kodi) 3 commercial break (S37, S65). Both separate *what it is* from *what to do*. Research/annotation formats (Audacity labels S39, Praat TextGrid S30, RTTM S38, AudioSet CSV S59, ELAN S45, CMX3600 S44) are each a 10-line exporter and matter for the *labelling and evaluation* workflow, not distribution. schema.org `Clip` (S27, S53) is the only SEO-visible carrier and is navigation-oriented.

**7. Publication path.**
A W3C CG needs five supporters and can publish a Draft CG Report on w3.org under the CLA (S29); WebVMT — the closest analogue (WebVTT-shaped, JSON payloads) — took a WG and is still an "experimental" Note after 2023 (S26, S55). RFC 6906 "profile" gives the right framing: an ADVTT *profile* of text/vtt "MUST NOT change the semantics of the resource representation when processed without profile knowledge" (S54) — which the design satisfies. The podcast world tolerates unregistered media types (`application/json+chapters` is unregistered and even has the `+json` suffix in the wrong place, S47). The Podcast Namespace's bar for a tag is 1 host + 1 app (S36).

**Contradictions/gaps:** ChapterSkipType is standardised but unsupported by the players checked (S63 vs S71). IAB position definitions attributed in snippets are not in the IAB text (S31). No per-app chapter feature matrix could be fetched (S69, S72). VMAP primary not verified (S69). Apple's handling of `toc:false`/`endTime` untested by anyone (S60).

## Implications for AdVTT

1. **Keep WebVTT `kind=metadata` as the primary interchange file; the two-line payload is spec-legal and parser-safe** (S1, S58, S61). Harden it: emit JSON minified on one line; escape `-->` inside JSON strings as `-->`; forbid raw CR/LF; require a cue identifier per cue (`ad-0001`) because parsers preserve identifiers but drop NOTE blocks (S1, S61). Consider making line 1 machine-friendlier than a bare token — e.g. HLS-style reverse-DNS class `org.advtt.ad.midroll` (S22, S33) — while keeping it a single token so `text.split("\n",1)` works.
2. **Move version/profile signalling out of `NOTE` and into (a) the WEBVTT header line text (`WEBVTT - profile=https://…/advtt/0.1`, legal per S1) and (b) each cue's JSON (`"v":"0.1"`)**; NOTE blocks are dropped by remuxers and invisible to browsers (S1, S61). Cite RFC 6906 "profile" semantics (S54).
3. **Separate content type from playback policy, as Matroska, SponsorBlock and Apple Interstitials all do** (S63, S64, S33): vocabulary `ADVERTISEMENT | SPONSORSHIP | PROMOTION | PROGRAM` (+ consider `INTERACTION`/`SELF_PROMO` from SponsorBlock, S64) and a distinct policy field (`action: skip|mute|none`, default `none` — enforcing the false-positive asymmetry in the data, not just the UI). Add optional `position: preroll|midroll|postroll` and `delivery: baked_in|dai|unknown` using IAB's delivery words (S31) and vernacular position words.
4. **Emit chapters as a second native output, in three carriers, always merged with content chapters**: Podcasting 2.0 JSON Chapters 1.2 (`title:"Ad: <advertiser>"`, `endTime`, optional `toc:false`) (S8, S14, S51); ID3v2 CHAP/CTOC via FFMETADATA1 + `ffmpeg -map_chapters` (S16, S50, S62); MP4/M4A chapter track for M4A feeds (S40, S62). Synthesise a `00:00:00` first chapter and ≥3 chapters or Apple/YouTube ignore the file (S28, S51). Never publish a WebVTT ad track as `podcast:transcript` (S9).
5. **Add two zero-cost skip-format exports for immediate consumers**: SponsorBlock-shaped JSON (`category:"sponsor"|"selfpromo"`, `actionType:"skip"`, `videoDuration`) (S64) and MPlayer/Kodi EDL (action 3 "commercial break" by default; 0 only with explicit auto-skip opt-in) (S37, S65). These reach mpv/Kodi/Jellyfin/NewPipe users without any new standard.
6. **For MKV/WebM/MKA outputs, write Matroska chapters with `ChapterSkipType=6`** and optionally a separate hidden "AdVTT" edition (S17, S63); mux the .vtt as a `D_WEBVTT/METADATA` track only in WebM (S19, S61); do not embed the JSON payload in MP4 text tracks (S61).
7. **Define the time origin and fingerprint the file.** State that times are seconds of decoded audio as delivered (DAI-safe by construction, unlike RSS sidecars, S70); include `duration_sec`, byte length and a content hash in the header JSON so consumers detect mismatched files (SponsorBlock `videoDuration` precedent, S64); document the ≈25 ms MP3 priming offset seen in CHAP/WebVTT round-trips (S61, S62).
8. **Publish a mapping table, not an adoption, of SCTE-35 ids** (ADVERTISEMENT→0x30/0x31, PROMOTION→0x3C/0x3D, PROGRAM→0x10/0x11; SPONSORSHIP has no SCTE equivalent) (S24) — useful for anyone bridging to HLS DATERANGE/DASH later (S22, S23), and it lends the vocabulary credibility.
9. **Publication path: ship the spec as a versioned profile document on the project's own domain first**, using RFC 6906 "profile" language (S54); then seek a W3C Community Group Draft Report (five supporters) if there is external interest (S29), with WebVMT's seven-year Note status as the expectation-setter (S26, S55). For the podcast side, the realistic route is not a new tag but demonstrating "already used in the wild" via chapters + one cooperating host (S36).
10. **Evaluation tooling**: export Audacity labels and RTTM (S39, S38) so the 4 fixtures can be edited in Audacity and scored with dscore-style DER/boundary metrics; export Praat TextGrid for word-level edge inspection (S30).

## Open questions / things that need an experiment

- Does Apple Podcasts honour JSON `toc:false` and `endTime`? Publish a test feed and observe (S60, S68). Same for AntennaPod/Podverse/Fountain (no matrix fetched, S69/S72).
- Does any player act on Matroska `ChapterSkipType=6` (mpv, VLC, Kodi, Jellyfin, Plex)? Manuals show nothing (S71) — needs a test file and, failing that, a feature request with the RFC 9559 citation (S63).
- Browser test matrix for the two-line payload: Safari/Chrome/Firefox `VTTCue.text` with `<`/`&`/`-->`-inside-JSON and CRLF line endings; confirm `getCueAsHTML()` is never used (S1, S57).
- Does ffmpeg's ISO 14496-30 WebVTT-in-MP4 path exist on a build with it enabled (this build refused) — relevant only if MP4 embedding is ever wanted (S61).
- Verify VMAP 1.0.1 `timeOffset` grammar from the primary PDF (404 this session, S69) before citing it.
- Fetch the 2016 IAB Podcast Ad Metrics Guidelines to check whether pre/mid/post-roll are defined anywhere by IAB (S31 correction).
- Measure the MP3 priming offset across encoders (LAME vs others) and decide whether AdVTT compensates or documents (S61, S62).
- Whether to register `application/vnd.advtt+json` (or `text/vtt; profile=…` parameter) with IANA — check WebVTT's IANA section 10 for permitted parameters (not re-verified this session, S1).
