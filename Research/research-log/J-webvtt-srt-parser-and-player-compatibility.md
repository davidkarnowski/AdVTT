# J — WebVTT/SRT parser and player compatibility
Accessed: 2026-09-01

## Status
COMPLETE — 2026-09-01 ~17:35 PDT. 61 source entries (S1–S61; S26 = documented 404, later covered by S48). WebSearch budget was exhausted before this track ran (200/200), and DeepWiki's public endpoint refused every query, so all evidence is from WebFetch/curl of primary sources (raw source files, specs, vendor docs); several player-vendor pages (Plex fetched via curl+UA; Kodi via MediaWiki API; Infuse/Jellyfin docs/Apple HLS spec not retrievable) — see gaps in Synthesis.

Method note: entries marked "fetched" via WebFetch carry an LLM summary's approximate line numbers; entries marked "curl, grepped" carry exact line numbers from the raw file. S21 and S23 were corrected after grep found the WebFetch summaries wrong/incomplete.

Fetch failures logged: code.videolan.org raw URLs blocked by Anubis anti-bot page (use github.com/videolan/vlc mirror); raw.githubusercontent.com/pbs/pycaption/main/pycaption/webvtt.py → 404 (try `master`); gsantiago/subtitle.js `main` README and src/Parser.ts → 404 (try `master`, other paths).

## Sources

### S1. webvtt-py `webvtt/vtt.py` (glut23) — https://raw.githubusercontent.com/glut23/webvtt-py/master/webvtt/vtt.py
- Type: repo
- Verified: fetched
- Key facts:
  - NOTE blocks are parsed into `WebVTTCommentBlock` objects (approx. lines 95–125), attached to adjacent items as `item.comments` (approx. line 177) and written back before their item on save (approx. lines 221–230). Comment regex: `NOTE\s(.*?)\Z` (approx. line 101).
  - Cue identifiers extracted in `WebVTTCueBlock.from_lines()` (approx. line 71), stored as `Caption.identifier` (approx. line 204), written back in `format_lines()` (approx. line 89).
  - Payload lines kept verbatim as a list (`payload.append(line)`, approx. line 75) and written back line by line (`*caption.lines`).
  - Timing regex `\s*((?:\d+:)?\d{2}:\d{2}.\d{3})\s*-->\s*((?:\d+:)?\d{2}:\d{2}.\d{3})` (approx. line 34); no special handling of `{`, `<`, `&`, or digit-leading lines — they are just payload.
- Relevance to AdVTT:
  - Full round-trip of NOTE header + identifier + two-line payload in the most-used Python VTT lib. Comments are attached to the *following* cue, so a header NOTE before cue 1 survives as `captions[0].comments`.

### S2. pysubs2 `formats/webvtt.py` — https://raw.githubusercontent.com/tkarabela/pysubs2/master/pysubs2/formats/webvtt.py
- Type: repo
- Verified: fetched
- Key facts:
  - `WebVTTFormat(SubripFormat)` (line 15): WebVTT is parsed by the SRT code path with a different timestamp regex `(\d{0,4}:)?(\d{2}):(\d{2})\.(\d{2,3})` (approx. lines 26–33). `guess_format` = text starts with `WEBVTT`. Writer emits only `WEBVTT\n` then SRT-style cues, sorted by start (approx. lines 47–55).
  - Consequently NOTE blocks, identifiers, STYLE etc. are not modelled at all; they fall through SubripFormat's logic (S3).
- Relevance to AdVTT: pysubs2 will silently drop the NOTE header and identifiers, and will treat the token line and JSON line as a two-line subtitle joined with `\N`.

### S3. pysubs2 `formats/subrip.py` — https://raw.githubusercontent.com/tkarabela/pysubs2/master/pysubs2/formats/subrip.py
- Type: repo
- Verified: fetched
- Key facts:
  - A line is a timing line iff `len(cls.TIMESTAMP.findall(line)) == 2` (approx. line 72). Everything before the first timing line is discarded (approx. line 84) — so a preamble/NOTE never errors, it just vanishes.
  - Sequence numbers are not required; a trailing numeric line is stripped by `re.sub(r"\n+ *\d+ *$", "", s)` (approx. line 101). **Side effect:** a cue whose *last* text line is purely digits loses that line (it is assumed to be the next index).
  - Tag handling: default converts `<i><b><u><s>` to ASS overrides and strips unknown HTML tags (approx. lines 106–113); `keep_unknown_html_tags=True` keeps them; `keep_ssa_tags` controls `{\...}` pass-through (approx. line 159). Lines are joined and `\n` → `\N` (approx. lines 99, 119).
- Relevance to AdVTT: `<ad>` would be stripped by default (invisible) — but only in pysubs2; a cue 0 or preamble is harmless here.

### S4. node-webvtt `lib/parser.js` (osk) — https://raw.githubusercontent.com/osk/node-webvtt/master/lib/parser.js
- Type: repo
- Verified: fetched
- Key facts:
  - NOTE blocks skipped: `if (lines.length > 0 && lines[0].trim().startsWith('NOTE'))` returns null (approx. line 127) and is filtered out (approx. line 94). Not exposed.
  - Identifier exposed as `cue.identifier` when the second line contains `-->` (approx. lines 135–137, 160). Payload `text = lines.join('\n')` (approx. line 158) — verbatim, multi-line.
  - Errors thrown: "Cue identifier cannot be standalone" (approx. 130), "Invalid cue timestamp" (145), strict-mode "Start timestamp greater than end" / "End must be greater than start" (149–152). No special treatment of `-->` or digits inside payload lines; header `meta:true` option parses `Key: value` header lines (approx. 67–75).
- Relevance to AdVTT: strict mode rejects zero-duration cues (end must be > start). Two-line payload is fine. NOTE header lost, but harmless. A JSON header could alternatively ride in the WEBVTT header block as key:value lines (node-webvtt exposes those; nothing else does).

### S5. W3C reference parser `webvtt.js/parser.js` (Anne van Kesteren) — https://raw.githubusercontent.com/w3c/webvtt.js/main/parser.js
- Type: repo (reference implementation)
- Verified: fetched
- Key facts:
  - NOTE: `if(/^NOTE($|[ \t])/.test(cue.id))` then skip lines until blank (approx. lines 103–110). Not stored.
  - Identifier stored as `cue.id` (approx. 88); if a line lacks `-->` and the next line lacks it too: error "Cue identifier needs to be followed by timestamp" (approx. 125).
  - Text joined with `\n` (approx. 160–165). A payload line containing `-->` → error "Blank line missing before cue" and is re-processed as a new timing line (approx. 158).
  - Cue-text parser: `&` starts an escape and is matched against the entity map / numeric refs (approx. 436–460); `<` starts tag parsing (approx. 418); unknown tag → error "Incorrect start tag" (approx. 360) and is dropped from the tree; `{` is plain text.
- Relevance to AdVTT: confirms the three escaping hazards (`-->`, `<`, `&`) in the profile are real; `{`/`}` and `"` are safe. Raw `cue.text` is unaffected — only the *cue-text-to-DOM* parser (i.e. `getCueAsHTML()`) mangles.

### S6. ffmpeg `libavcodec/srtdec.c` — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/srtdec.c
- Type: repo
- Verified: fetched
- Key facts:
  - The decoder itself only handles X1/Y1 position side data (scaling 720x480 → ASS play-res, emitting `{\an5}{\pos(x,y)}`, approx. lines 9–23) and delegates all text conversion to `ff_htmlmarkup_to_ass()` in `htmlsubtitles.c` (approx. lines 30–31).
- Relevance to AdVTT: the answer to "does ffmpeg strip `<ad>` / escape `{`" lives in htmlsubtitles.c (to fetch).

### S7. Matroska "Subtitles" spec page — https://www.matroska.org/technical/subtitles.html
- Type: spec
- Verified: fetched
- Key facts:
  - S_TEXT/WEBVTT: "This CodecPrivate contains all global blocks before the first subtitle entry" (WEBVTT signature, STYLE, REGION, NOTE blocks before cue 1).
  - Block = the cue text only; timings come from Block timestamp/BlockDuration. BlockAdditions (BlockAddID 1) carry three lines: line 1 "the ... optional WebVTT cue settings list", line 2 "the ... optional WebVTT cue identifier", line 3+ "all WebVTT comment block(s) that precede the current WebVTT cue block"; each line LF-terminated.
  - Timestamps inside cues must be relative to the Block timestamp. Page notes WebM uses `D_WEBVTT/...` IDs "but does not recommend them for Matroska".
  - S_TEXT/UTF8 (SRT): "Because there are no general settings for SRT, the CodecPrivate is left blank." No mention of tags.
- Relevance to AdVTT: In MKV the NOTE header, identifiers and per-cue NOTEs are all storable losslessly (CodecPrivate + BlockAdditions). Whether any muxer/player actually writes/reads BlockAdditions is the open question.

### S8. Matroska codec specs (codec IDs) — https://www.matroska.org/technical/codec_specs.html
- Type: spec
- Verified: fetched
- Key facts:
  - `S_TEXT/UTF8` "Basic text subtitles", no init data. `S_TEXT/WEBVTT`: "The CodecPrivate contains the WebVTT file body up to the first WebVTT cue block"; "Intermediate non-Cue Blocks SHOULD be stored in BlockAdditions. The BlockAddID ... MUST be 1."
  - No `D_WEBVTT/*` entries in the Matroska codec list — those are WebM-only (S16).
- Relevance to AdVTT: two incompatible container conventions (Matroska S_TEXT/WEBVTT vs WebM D_WEBVTT/METADATA); a "metadata" *kind* is only expressible in WebM's IDs, not in Matroska's.

### S9. MDN `<track>` — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/track
- Type: spec-adjacent docs
- Verified: fetched
- Key facts:
  - `kind=metadata`: "Tracks used by scripts. Not visible to the user." `default`: enabled unless user prefs choose another; only one per media element.
  - `src` "must have the same origin as the document — unless the <audio> or <video> parent element ... has a crossorigin attribute." Baseline widely available since July 2015.
- Relevance to AdVTT: same-origin rule is what bites `file://` in Chromium (each file:// document is an opaque origin; to be confirmed against a Chromium source — not found yet in this run). The HTML prototype must either inline the VTT (blob:/data: URL or `addCue` from parsed text) or be served over http.

### S10. Podcasting 2.0 transcripts doc — https://raw.githubusercontent.com/Podcastindex-org/podcast-namespace/main/docs/examples/transcripts/transcripts.md
- Type: spec
- Verified: fetched
- Key facts:
  - VTT is the recommended format; speaker names via `<v>` voice spans; "Apple Podcasts supports these speaker names, and will ingest them into its transcript tool." Recommends ≤65-char lines (`--split-on-word --max-len 65` for whisper-cpp).
  - SRT: max 2 lines / 32 chars per line; speaker as `Name:` prefix; "An SRT file can be generated programmatically from a VTT file (and vice-versa)."
  - NOTE blocks and cue identifiers are not mentioned at all.
- Relevance to AdVTT: the transcript ecosystem's contract is caption-shaped; nothing promises apps will tolerate non-caption cues. An `.ads.vtt` must never be published in `<podcast:transcript>` as if it were a transcript.

### S11. `srt` Python library (cdown) `srt.py` — https://raw.githubusercontent.com/cdown/srt/develop/srt.py
- Type: repo
- Verified: fetched
- Key facts:
  - Regexes (approx. lines 14–51): `RGX_TIMESTAMP_MAGNITUDE_DELIM = r"[,.:，．。：]"`, `RGX_INDEX = r"-?[0-9]+\.?[0-9]*"`, `RGX_PROPRIETARY = r"[^\r\n]*"` (text after timings), `RGX_CONTENT = r".*?"` with `re.DOTALL`.
  - Index optional (`raw_index=None`, approx. 456; written as 0 by `to_srt` default, approx. 234). Unmatched text before/between cues: `_check_contiguity` raises `SRTParseError` unless `ignore_errors=True` (approx. 485–515); leading whitespace/BOM tolerated.
  - No special handling of `{}` / `<>`. Zero-duration allowed at parse; `sort_and_reindex(skip=True)` (default) drops subs where `start >= end` (approx. 203–209, 326–327).
- Relevance to AdVTT: a preamble in SRT is a *hard error* in the strict default of the most common Python SRT lib. Zero-duration marker cues get silently deleted by the common `sort_and_reindex` call. Cue 0 is fine.

### S12. Mozilla `vtt.js` `lib/vtt.js` — https://raw.githubusercontent.com/mozilla/vtt.js/master/lib/vtt.js
- Type: repo (basis of videojs-vtt.js used by video.js / hls.js)
- Verified: fetched
- Key facts:
  - NOTE: `/^NOTE($|[ \t])/` → state "NOTE", lines ignored until blank (approx. 887–889); nothing emitted.
  - Identifier → `self.cue.id = line` (approx. 905). Text joined with `\n` (approx. 920–922). A CUETEXT line containing `-->` ends the cue and is re-read as a new timing line (approx. 916).
  - `parseContent()` (used for rendering only): ESCAPE map decodes `&amp; &lt; &gt; &nbsp; &lrm; &rlm;` (approx. 426, 505); `<` splits via `/^([^<]*)(<[^>]+>?)?/` (approx. 481); `{` untouched. Digit-leading lines in ID state are identifiers, not timestamps.
- Relevance to AdVTT: identical model to S5; the raw `cue.text` is safe for JSON with `{`, `"`; `<`/`&`/`-->` need the profile's escapes only if someone renders; `-->` is the one that corrupts parsing.

### S13. ffmpeg `libavformat/webvttdec.c` (demuxer) — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/webvttdec.c
- Type: repo
- Verified: fetched
- Key facts:
  - Probe: optional BOM then `WEBVTT` followed by EOF/whitespace (approx. 39–47).
  - Skips whole blocks starting `WEBVTT`, `STYLE`, `REGION`, `NOTE` via `continue` (approx. 78–82) — NOTE content is discarded.
  - Identifier: line before the `-->` line, stored as packet side data `AV_PKT_DATA_WEBVTT_IDENTIFIER` (approx. 84–97, 128). Settings after end time → `AV_PKT_DATA_WEBVTT_SETTINGS` (approx. 118–129). Payload stored verbatim, `strlen(p)`, newlines preserved (approx. 112–115).
- Relevance to AdVTT: `ffmpeg -i x.vtt -c:s copy` keeps id + settings + multi-line payload as-is; NOTE header is lost on any ffmpeg pass. `-c:s webvtt` (re-encode) goes through libavcodec and will normalise text (to check in libavcodec/webvttdec.c + webvttenc.c).

### S14. ffmpeg `libavformat/webvttenc.c` (muxer) — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/webvttenc.c
- Type: repo
- Verified: fetched
- Key facts:
  - Writes `WEBVTT\n` header only (approx. 49–54); no NOTE/STYLE/REGION output at all. Per cue: blank line, identifier from `AV_PKT_DATA_WEBVTT_IDENTIFIER` if size>0 (approx. 60–65), timings, settings side data (approx. 72–77), payload via `avio_write(pb, pkt->data, pkt->size)` (approx. 79–81).
- Relevance to AdVTT: an ffmpeg round-trip (`-c:s copy`) preserves everything in the design except the NOTE header. Header data must therefore be reconstructible without the NOTE, or duplicated in `analysis.json`.

### S15. ffmpeg `libavformat/srtdec.c` (SRT demuxer) — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/srtdec.c
- Type: repo
- Verified: fetched
- Key facts:
  - Probe (approx. 33–52): skips leading CR/LF, then first non-empty line must parse via `strtol` as a number ≥0 (value not checked, so `0` passes), second line must be a `-->` timing line. **A non-numeric preamble fails the probe** (file not recognised as SRT).
  - Reader (approx. 145–175): does not require the index; a numeric line that is not a timing is cached and flushed into the payload if followed by text (approx. 156–172) — so a *text line consisting only of digits* is preserved if it is not directly followed by a timing line. X1/X2/Y1/Y2 parsed into side data (approx. 81–107).
  - Duration = end − start with no validation of zero/negative (approx. 87).
- Relevance to AdVTT: matrix option 5 (preamble) = ❌ for ffmpeg (probe fails; whole file unrecognised, unless format forced). Cue `0` = ✅. Zero-duration = tolerated (⚠️).

### S16. WebM container guidelines (WebVTT section) — https://www.webmproject.org/docs/container/
- Type: spec
- Verified: fetched
- Key facts:
  - "The CodecID for a WebVTT track is "D_WEBVTT/kind", where kind is one of SUBTITLES, CAPTIONS, DESCRIPTIONS, or METADATA."
  - Block = [identifier or empty line] LF, [settings or empty line] LF, payload; "The WebVTT cue timings is not written to the WebM Block"; "No WebVTT data is stored in the CodecPrivate element of the WebM Track header."
- Relevance to AdVTT: WebM has a first-class METADATA kind but **no place for the NOTE header or per-cue comments** (no CodecPrivate); Matroska has the header but no kind. Either way, the NOTE header does not survive container embedding in WebM.

### S17. MDN `TextTrack.mode` — https://developer.mozilla.org/en-US/docs/Web/API/TextTrack/mode
- Type: docs
- Verified: fetched
- Key facts:
  - disabled: "the user agent won't attempt to obtain the track's cues"; hidden: cues obtained, `activeCues` maintained, events fire, nothing drawn; showing: drawn.
  - "The default mode is disabled, unless the default Boolean attribute is specified, in which case the default mode is showing." "When a text track is loaded in the disabled state, the corresponding WebVTT file is not loaded until the state changes to either showing or hidden."
- Relevance to AdVTT: `track.cues` is `null`/empty until the script sets `mode="hidden"`; the player prototype must set mode then wait for the track `load` event before reading cues (cannot read synchronously). Per-browser default for `kind=metadata default` still to confirm from the HTML spec (metadata tracks with `default` should become `hidden`, not `showing`).


### Fetch plan batch 2a (logged before fetching)
- https://raw.githubusercontent.com/videolan/vlc/master/modules/demux/subtitle.c
- https://raw.githubusercontent.com/videolan/vlc/master/modules/demux/webvtt.c
- https://raw.githubusercontent.com/videolan/vlc/master/modules/codec/subsdec.c
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/htmlsubtitles.c
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/webvttdec.c
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/matroskaenc.c
- https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/matroskadec.c

### S18. VLC `modules/demux/subtitle.c` (GitHub mirror) — https://raw.githubusercontent.com/videolan/vlc/master/modules/demux/subtitle.c
- Type: repo
- Verified: fetched (mirror; code.videolan.org raw blocked by Anubis)
- Key facts:
  - Autodetection loop scans the first 256 lines for a timing line: `sscanf(s, "%d:%d:%d,%d --> %d:%d:%d,%d", ...) == 8 || sscanf(s, "%d:%d:%d --> %d:%d:%d", ...) == 6` (approx. lines 1119–1134); it does **not** require a sequence number, and text before the first timing is tolerated (read until a timing line matches).
  - `else if( !strncasecmp( s, "WEBVTT",6 ) ) { /* FAIL */ break; }` (approx. line 1158) — WebVTT is refused here and handled by a separate demux module (S19).
  - `ParseSubRipSubViewer` appends every non-blank line after the timing as text; a digits-only line is ordinary text (approx. 1007–1042). `subtitle_ParseSubRipTiming` (approx. 1068–1081) locates `" --> "`.
- Relevance to AdVTT: VLC is lenient: preamble text, cue 0, missing/duplicate indices all load. Matrix option 5 for VLC = ✅ loads (but the preamble text is not shown, since text is only collected after a timing line).

### S19. VLC `modules/demux/webvtt.c` — https://raw.githubusercontent.com/videolan/vlc/master/modules/demux/webvtt.c
- Type: repo
- Verified: fetched
- Key facts:
  - Probe: `WEBVTT` + newline/space/tab/CR, optional BOM (approx. 577–591).
  - STYLE and REGION header blocks are appended to memstreams and become codec extradata (`MakeExtradata`, approx. 235–237, 357–373). NOTE blocks are not stored (no handling shown).
  - Each cue is converted to ISO-14496-30 style boxes: `iden` box for the identifier when present (approx. 171–173), `payl` box for the payload (approx. 183), settings in `sttg`. Seekable mode reads all cues, sorts and indexes them; streaming mode emits per cue (approx. 255–276).
- Relevance to AdVTT: VLC keeps identifier + full multi-line payload and sorts cues (out-of-order tolerated). NOTE header dropped. A metadata-only VTT loaded as a subtitle track in VLC will *display* the token+JSON lines as subtitles (subsvtt renders payl text) — expected, since VLC has no metadata kind.

### S20. VLC `modules/codec/subsdec.c` (SRT/plain-text decoder) — https://raw.githubusercontent.com/videolan/vlc/master/modules/codec/subsdec.c
- Type: repo
- Verified: fetched
- Key facts:
  - Known tags `<b> <i> <u> <s> <br> <font ...>` push style segments (`ParseSubtitles`, approx. line 1000+).
  - Unknown tags: comment "This is an unknown tag. We need to hide it if it's properly closed, and display it otherwise" (approx. line 1060). So `<ad>...</ad>` is hidden, but a bare `<ad>` without `</ad>` is displayed literally.
  - `{\an1}`–`{\an9}` consumed (approx. 1130); MicroDVD `{Y:i}`, `{C:$BBGGRR}`, `{F:}`, `{S:}` consumed; "All unrecognized {x:y} constructs are silently removed" (approx. 1150–1240).
- Relevance to AdVTT: corrects the matrix — VLC strips `<ad>` **only if closed**; and `{ad}` (no colon) is not an `{x:y}` construct, so its fate is unverified — `{ad:1}` would be stripped, `{ad}` probably printed. Safest SRT tag form for VLC is a closed pair `<ad></ad>`.

### S21. ffmpeg `libavcodec/htmlsubtitles.c` (`ff_htmlmarkup_to_ass`, used by srtdec and others) — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/htmlsubtitles.c
- Type: repo
- Verified: fetched
- Key facts:
  - Design comment (approx. lines 176–180): "The general politic of the convert is to mask unsupported tags or formatting errors ... without dropping any actual text content for the final user."
  - `{`: `handle_open_brace()` (approx. 59–76) — `{\an%d}` is honoured; comment "skip all {\xxx} substrings except for {\an%d}" (approx. 58); other braces are treated as text (escaped for ASS).
  - Tags: single-letter `bisu` handled (approx. 323–325), `<font>` stack (approx. 285), `<br>` → `\N` (327). Unknown tags: skipped if `likely_a_tag` (approx. 330), otherwise the `<` is output literally (approx. 332).
- Relevance to AdVTT: In ffmpeg-based players (mpv, Jellyfin/Plex transcodes, Kodi's ffmpeg path) `<ad>` is stripped, `{ad}` is shown literally (not a `{\...}` override). Matches the matrix's ffmpeg column; refines the `{ad}` row: `{\ad}` would be stripped by ffmpeg but that is ASS-override folklore, not a convention.

### S22. ffmpeg `libavcodec/webvttdec.c` (WebVTT→ASS decoder, used when re-encoding `-c:s ass/srt/webvtt`) — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavcodec/webvttdec.c
- Type: repo
- Verified: fetched
- Key facts:
  - `webvtt_tag_replace` table (approx. 34–38): `&amp;`→`&`, `&lt;`→`<`, `&gt;`→`>`, `&nbsp;`→`\h`, `&lrm;`/`&rlm;`→ marks; literal `{` → `\{` (approx. 35). Only `<b><i><u>` are converted (`webvtt_valid_tags`, approx. 40–44); `<c>`, `<v>`, `<ruby>` and unknown tags are discarded. Newlines → `\N` (approx. 130).
- Relevance to AdVTT: any ffmpeg *re-encode* of the metadata track (e.g. `-c:s srt`, or muxing into MP4 as `mov_text`) destroys the JSON (`{` escaped, `\N` joins lines, a bare `&` left alone, `<`-anything eaten). Only `-c:s copy` is lossless → document that.

### S23. ffmpeg `libavformat/matroskaenc.c` — https://raw.githubusercontent.com/FFmpeg/FFmpeg/master/libavformat/matroskaenc.c
- Type: repo
- Verified: fetched (WebFetch summary truncated the file; codec-ID section seen, block writer not seen — re-verify by curl/grep below)
- Key facts (from the seen part):
  - Codec ID chosen by disposition: `D_WEBVTT/CAPTIONS`, `D_WEBVTT/DESCRIPTIONS`, `D_WEBVTT/METADATA`, default `D_WEBVTT/SUBTITLES` (approx. lines 1870–1880, `mkv_write_track`). WebM allow-list message: "Only VP8 or VP9 or AV1 video and Vorbis or Opus audio and WebVTT subtitles are supported for WebM." (approx. 1883).
  - CodecPrivate is skipped for WebVTT (`if (!IS_WEBM(mkv) || par->codec_id != AV_CODEC_ID_WEBVTT)` approx. 1915–1920 per summary — see grep verification).
- Relevance to AdVTT: ffmpeg writes the *WebM* flavour (`D_WEBVTT/*`) even into `.mkv`, and a `-disposition:s:0 metadata` flag yields `D_WEBVTT/METADATA`. Confirm block layout + BlockGroup usage via grep (next).

### Fetch plan batch 2b (logged before fetching; DeepWiki attempted for AntennaPod, hls.js, mpv, podverse — public endpoint returned an auth error every time, so DeepWiki is unusable here)
- mkvtoolnix.download/doc/mkvmerge.html; w3.org/TR/webvtt1; pycaption (master); pysrt srtitem.py/srtfile.py; go-astisub webvtt.go/srt.go; gsantiago/subtitle.js README; androidx/media Webvtt*.java + SubripParser.java; docs.rs/subparse; sandflow/ttconv README; podcasters.apple.com/support/5316; WICG/datacue README

### S24. mkvmerge manual — https://mkvtoolnix.download/doc/mkvmerge.html
- Type: product docs
- Verified: fetched
- Key facts: the man page has **no WebVTT-specific section** — nothing about codec IDs, BlockAdditions, or limitations. Only generic text-subtitle handling (charset, `--language`, `--sync`).
- Relevance to AdVTT: mkvmerge's WebVTT behaviour must come from its source/NEWS (attempted below); documented gap.

### S25. W3C WebVTT (TR/webvtt1) — https://www.w3.org/TR/webvtt1/
- Type: spec
- Verified: fetched (summary-level; sections 6.3/6.4 not surfaced by the fetch — grep pass below)
- Key facts:
  - "A WebVTT comment block is ignored by the parser." Comment block = `NOTE` + optional text, terminated by blank line.
  - Cue payload "must not contain the substring '-->'"; payload types are "zero or more characters" (empty cue text is syntactically allowed).
  - Ordering: "Cues are always listed ordered by their start time"; "must be greater than or equal to the start time offsets of all previous cues" (authoring requirement; parsers still accept out-of-order — see S5/S12 which never check order).
  - "WebVTT metadata text cues are only useful for scripted applications."
  - Syntax: cue text spans "cannot contain '&' or '<'" unescaped (authoring rule).
- Relevance to AdVTT: NOTE content is by design unreachable from any conforming consumer — the header can never be *read* from the browser TextTrack API; it is a file-level convenience only. Out-of-order cues are non-conforming for authors (AdVTT should always sort).

### S26. pycaption `pycaption/webvtt.py` — https://raw.githubusercontent.com/pbs/pycaption/{main,master}/pycaption/webvtt.py
- Type: repo
- Verified: fetch failed (404 on both branches) — gap; try GitHub contents API below.

### S27. pysrt `srtitem.py` + `srtfile.py` — https://raw.githubusercontent.com/byroot/pysrt/master/pysrt/srtitem.py , https://raw.githubusercontent.com/byroot/pysrt/master/pysrt/srtfile.py
- Type: repo
- Verified: fetched (both)
- Key facts:
  - Index optional: `if cls.TIMESTAMP_SEPARATOR not in lines[0]: index = lines.pop(0)` (srtitem approx. 61–63); non-integer index tolerated (approx. 34–35). Body `'\n'.join(lines[1:])` — digit-only text lines kept verbatim (approx. 63).
  - `RE_TAG = re.compile(r'<[^>]*?>')` used by `text_without_tags` (approx. 50) — strips *all* angle tags incl. `<ad>` when the consumer asks for tag-less text; braces untouched.
  - `stream()` splits on blank lines (srtfile approx. 108–131); malformed blocks handled per `error_handling`: default `ERROR_PASS` silently skips (approx. 126), `ERROR_RAISE` throws. A preamble block therefore is silently dropped by default.
- Relevance to AdVTT: pysrt: preamble ✅(dropped), cue 0 ✅, `<ad>` invisible only if the consumer uses `text_without_tags`.

### S28. go-astisub `webvtt.go` + `srt.go` — https://raw.githubusercontent.com/asticode/go-astisub/master/webvtt.go , https://raw.githubusercontent.com/asticode/go-astisub/master/srt.go
- Type: repo
- Verified: fetched (both)
- Key facts:
  - WebVTT: `case strings.HasPrefix(line, "NOTE "):` → `comments = append(comments, strings.TrimPrefix(line, "NOTE "))` (approx. 276–278); comments attached to the next item (approx. 349) and written back (approx. 586–591). **Identifier is parsed with `strconv.Atoi(line)` (approx. 367–369)** — a non-numeric id like `ad-001` becomes 0 and the writer emits sequential numeric indices (approx. 592): identifiers are *not* round-tripped. Payload lines → `Item.Lines` (approx. 361); `<v> <c> <b> <i> <u>` parsed, HTML entities unescaped/escaped on read/write (approx. 493, 641).
  - SRT: index optional; a numeric-only *last* line of a block is consumed as the next index (approx. 58–64, "Remove last item of previous subtitle since it should be the index"); other digit-only lines are content (approx. 90–93). `<b><i><u><font>` tokenised; braces not parsed on read (approx. 101–121, 189).
- Relevance to AdVTT: another mainstream lib that rewrites identifiers to integers → the profile must not rely on identifiers surviving a round trip; keep the id inside the JSON (already done: `"id":"ad-001"`). Also JSON `&`/`<` written through astisub's `escapeHTML` would be re-escaped to `&amp;`/`&lt;` — another argument for the `\u00XX` escapes.

### S29. `subtitle` npm (gsantiago/subtitle.js) README — https://raw.githubusercontent.com/gsantiago/subtitle.js/master/README.md
- Type: repo
- Verified: fetched
- Key facts: "partial support for WebVTT"; nodes are only `header` and `cue` — "Soon, it will support more types like comment"; cue = {start,end,text,settings}; no cue identifier field documented.
- Relevance to AdVTT: NOTE blocks and identifiers are outside this parser's model (NOTE fate unspecified — needs experiment); multi-line text presumably preserved as `text`.

### S30. Media3/ExoPlayer `WebvttParser.java` — https://raw.githubusercontent.com/androidx/media/release/libraries/extractor/src/main/java/androidx/media3/extractor/text/webvtt/WebvttParser.java
- Type: repo
- Verified: fetched
- Key facts: header validated via `WebvttParserUtil.validateWebvttHeaderLine` (approx. 89–92; throws `IllegalArgumentException`). `COMMENT_START = "NOTE"` (approx. 55) → `skipComment()` consumes to blank line (approx. 102–104). STYLE must precede cues. Any other non-empty line is `EVENT_CUE` (approx. 135–140).
- Relevance to AdVTT: NOTE header fine; Android players (ExoPlayer-based podcast apps, Jellyfin Android, etc.) skip it.

### S31. Media3 `WebvttCueParser.java` — https://raw.githubusercontent.com/androidx/media/release/libraries/extractor/src/main/java/androidx/media3/extractor/text/webvtt/WebvttCueParser.java
- Type: repo
- Verified: fetched
- Key facts: identifier parsed only for CSS matching, **not stored in the Cue** (approx. 359–360, 555). Text lines individually `trim()`ed and joined with `\n` (approx. 379–386). `isSupportedTag` = b, c, i, lang, ruby, rt, u, v (approx. 533–546); unknown tags skipped. Entities: only `&lt; &gt; &nbsp; &amp;` (approx. 518–531); others → `Log.w(... "ignoring unsupported entity")` and dropped. `{` is plain text (approx. 514).
- Relevance to AdVTT: ExoPlayer *always* runs the cue-text markup parser (no raw-text path for file-loaded cues) — so a JSON payload containing a raw `<` or `&` would be corrupted in ExoPlayer; `<`/`&` escapes are needed for any Android consumer, not only for `getCueAsHTML()`. Also: leading/trailing whitespace in JSON lines is trimmed (harmless).

### S32. Media3 `SubripParser.java` — https://raw.githubusercontent.com/androidx/media/release/libraries/extractor/src/main/java/androidx/media3/extractor/text/subrip/SubripParser.java
- Type: repo
- Verified: fetched
- Key facts: expects a numeric index; non-numeric → `Log.w "Skipping invalid index"` and continue (approx. 135). Timing regex `\s*(TIMECODE)\s*-->\s*(TIMECODE)\s*` else "Skipping invalid timing" (approx. 150). Lines joined with `<br>` then `Html.fromHtml(...)` (approx. 157–164); `{\anN}` extracted via `\{\\an[1-9]\}` (approx. 78) and any `\{\\.*?\}` removed (approx. 189–199).
- Relevance to AdVTT: ExoPlayer SRT: preamble → skipped with a warning (✅ loads); cue 0 ✅; `<ad>` → `Html.fromHtml` drops unknown tags (⚠️ inferred from Android Html behaviour, not verified here); `{ad}` printed literally (only `{\...}` removed).

### S33. Rust `subparse` crate docs — https://docs.rs/subparse/latest/subparse/
- Type: repo docs
- Verified: fetched
- Key facts: formats: SRT, SSA/ASS, IDX, MicroDVD; **no WebVTT**; "non-destructive parsing, meaning that formatting and other information are preserved if not explicitely changed."
- Relevance to AdVTT: not a WebVTT consumer; only relevant as an SRT round-tripper that preserves unknown text.

### S34. ttconv README — https://raw.githubusercontent.com/sandflow/ttconv/master/README.md
- Type: repo
- Verified: fetched
- Key facts: inputs: SCC, IMSC, EBU STL, SRT, WebVTT; outputs: SRT, IMSC, WebVTT, SCC. SRT reader options: extended tags `{bold} <bold> {b} {italic} <italic> {i} ...` (off by default), `{\anN}` (off by default).
- Relevance to AdVTT: ttconv is a *model-based* converter (WebVTT → IMSC document model → out); NOTE blocks, identifiers and JSON are certain to be lost/re-flowed. Also note a professional tool treats `{b}`-style brace tags as *formatting* — `{ad}` is not safe in SRT even for "strip braces" consumers.

### S35. Apple Podcasts "Transcripts on Apple Podcasts" — https://podcasters.apple.com/support/5316-transcripts-on-apple-podcasts
- Type: product docs
- Verified: fetched
- Key facts: accepts "VTT or SRT"; "Providing a VTT file allows you to identify every speaker with each line."; "All transcripts are subject to quality standards. Files that do not meet standards will not be displayed."; no syntax spec published.
- Relevance to AdVTT: Apple's ingest is a black box with a quality gate — a transcript VTT containing non-caption cues (ad markers) or unexpected blocks risks the *whole transcript* being withheld. Never merge ad cues into the transcript VTT that goes in `<podcast:transcript>`.

### S36. WICG DataCue README — https://raw.githubusercontent.com/WICG/datacue/main/README.md
- Type: spec (incubation)
- Verified: fetched
- Key facts: DataCue is a WICG incubation ("Draft Spec"), implemented in WebKit/Safari only; proposals include "Expose TextTrackCue constructor". Not standardised.
- Relevance to AdVTT: no cross-browser structured-data cue exists; `VTTCue` with `kind=metadata` + text payload remains the only portable in-browser vehicle — which is what the design already uses.

### S23 (correction, verified by curl + grep of the raw file, exact line numbers)
- `libavformat/matroska.c` lines 62–65 map `D_WEBVTT/SUBTITLES|CAPTIONS|DESCRIPTIONS|METADATA` → `AV_CODEC_ID_WEBVTT`; line 67–68 `S_TEXT/UTF8` → SUBRIP/TEXT. **`S_TEXT/WEBVTT` is absent from ffmpeg's codec-tag table** (both the mkv and webm tables, lines 62–70 and 118–121): ffmpeg neither writes nor recognises Matroska's official WebVTT codec ID.
- `matroskaenc.c` 1981–2000: codec_id string chosen from disposition (`D_WEBVTT/METADATA` when `AV_DISPOSITION_METADATA`); 2160/2172: CodecPrivate skipped only when `IS_WEBM && WEBVTT` — so in `.mkv` a CodecPrivate *is* written (from extradata; the webvtt demuxer provides none, so empty). 2828–2851 `webm_reformat_vtt`: block = `id` `\n` `settings` `\n` payload (exactly the WebM layout, S16). 3173–3177: "The WebM spec requires WebVTT to be muxed in BlockGroups; so we force it even for packets without duration." Reformat is installed for every WebVTT track (3592–3593), mkv or webm.
- `matroskadec.c` 3140–3147: `D_WEBVTT/METADATA` → `AV_DISPOSITION_METADATA`; 3891ff `matroska_parse_webvtt` splits id / settings / text on `\n`, restores `AV_PKT_DATA_WEBVTT_IDENTIFIER` and `AV_PKT_DATA_WEBVTT_SETTINGS` (3962, 3973).
- Relevance: ffmpeg mkv/webm round-trip preserves identifier, settings, multi-line payload and the *metadata kind* (as a disposition) — but not the NOTE header, and it produces files with WebM-style IDs that spec-following Matroska players may not recognise as WebVTT (see mkvtoolnix, next).

### S37. MDN "WebVTT: Web Video Text Tracks Format" — https://developer.mozilla.org/en-US/docs/Web/API/WebVTT_API/Web_Video_Text_Tracks_Format
- Type: docs
- Verified: fetched
- Key facts:
  - "NOTE blocks ... are intended for those reading the file and are not seen by users."
  - "A cue text payload cannot contain the string -->, the ampersand character (&), or the less-than sign (<)." — followed by: **"Note that if you are using the WebVTT file for metadata these restrictions do not apply."**
  - Identifier: "must not contain a newline and cannot contain the string -->."
  - Payload "may contain newlines but cannot contain two consecutive newlines".
- Relevance to AdVTT: MDN explicitly blesses raw `&`/`<` in metadata payloads (browsers keep `cue.text` raw). But the restriction *does* still bite (a) `getCueAsHTML()`, (b) ExoPlayer (S31), (c) any lib that HTML-unescapes (astisub S28, ffmpeg re-encode S22). Keep the `<`/`&` escapes — they cost nothing.

### S38. MDN `VTTCue.getCueAsHTML()` — https://developer.mozilla.org/en-US/docs/Web/API/VTTCue/getCueAsHTML
- Type: docs
- Verified: fetched
- Key facts: returns "a DocumentFragment containing the cue content" (i.e. the cue text run through the WebVTT cue-text parser); Baseline since July 2015.
- Relevance to AdVTT: the profile's rule "consumers must read `cue.text`, never `getCueAsHTML()`" is necessary; the fragment would decode `&amp;`, drop unknown `<...>`, and lose the JSON.

### S39. Wikipedia "SubRip" — https://en.wikipedia.org/wiki/SubRip
- Type: encyclopaedia (de-facto description)
- Verified: fetched
- Key facts: four parts "A numeric counter ... / The time ... followed by --> ... / Subtitle text itself on one or more lines / A blank line"; "Unofficially the format has very basic text formatting" (`<b> <i> <u> <font color>`); some players "apply the style of the first tag that appears in the line to the entire line"; "Also unofficially, text coordinates can be specified at the end of the timestamp line as X1:… X2:… Y1:… Y2:…"; **no mention of comments or metadata**.
- Relevance to AdVTT: confirms 03-srt-strategy §1 — no comment mechanism exists in any de-facto SRT description (S7 Matroska, S15 ffmpeg, S11 srt lib, S18 VLC, this).

### S40. AntennaPod transcript parsers (`VttTranscriptParser.java`, `SrtTranscriptParser.java`, `TranscriptParser.java`) — https://github.com/AntennaPod/AntennaPod/tree/develop/parser/transcript/src/main/java/de/danoeh/antennapod/parser/transcript
- Type: repo
- Verified: fetched (all three raw files)
- Key facts:
  - Dispatch is by MIME type only (`TranscriptType.fromMime`; JSON/VTT/SRT; else null) — no content sniffing (approx. lines 14–21).
  - VTT: normalises line endings, then **skips every line that does not contain `-->`** (approx. 52–54) — WEBVTT header, NOTE blocks and identifiers are all silently ignored; timings parsed by regex `HH:MM:SS.mmm` (approx. 108–115); `<v Speaker>` regex `<v(?:\.[^\t\n\r &<>.]+)*[ \t]([^\n\r&>]+)>` (approx. 17). No exceptions on malformed content.
  - SRT: lines with `-->` start a segment; index lines ignored; text lines until blank are concatenated with spaces (approx. 41–59); a line containing `": "` is treated as `Speaker: text` (approx. 68–72); bad timecodes → `continue`.
- Relevance to AdVTT: AntennaPod would happily *display* AdVTT cues as transcript text if the ads track were ever wired as a transcript (`ADVERTISEMENT {"v":...}`). NOTE blocks are safe. In SRT, a marker like `[ADVERTISEMENT: Acme]` would be mis-parsed as speaker "[ADVERTISEMENT" — avoid `: ` inside SRT twin text.

### Fetch failures in this batch (documented gaps)
- support.plex.tv article 200471133 → HTTP 403; kodi.wiki/view/Subtitles → 403; Infuse article 215090947 is the *metadata naming* page (wrong article, no format list); jellyfin.org external-files page returned empty body; Apple HLS authoring spec page is JS-rendered (empty). Retrying some via curl with a UA below; otherwise these player columns stay ❓ from documentation and must be tested.

### S41. WHATWG HTML Standard, media section (text tracks) — https://html.spec.whatwg.org/multipage/media.html
- Type: spec
- Verified: fetched (curl; grepped the tag-stripped text)
- Key facts:
  - kind `metadata`: "Tracks intended for use from script." (not displayed).
  - "time marches on" steps drive cue activation; the `timeupdate` guard is "in the past 15 to 250ms" — i.e. cue enter/exit is evaluated on the playback-position update cadence, granularity 15–250 ms, not sample-accurate. `cuechange` fires from these steps.
  - Automatic track selection: metadata tracks with a `default` attribute are set to **hidden** (not showing) — confirmed by both engine implementations S42/S43 which cite this step.
- Relevance to AdVTT: skip logic must tolerate ~250 ms latency at cue boundaries (use `cue.startTime` for the seek target, not the moment the event fired). Putting `default` on a metadata `<track>` is the spec-sanctioned way to get cues loaded without script setting mode.

### S42. Chromium Blink `automatic_track_selection.cc` + `text_track_loader.cc` — https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/core/html/track/automatic_track_selection.cc , https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/core/loader/text_track_loader.cc
- Type: repo (browser engine)
- Verified: fetched (curl, base64-decoded, grepped)
- Key facts:
  - `EnableDefaultMetadataTextTracks` (lines 141–156): comment cites the spec step for metadata tracks "that correspond to track elements with a default attribute" and sets `TextTrackMode::kHidden` (line 156). Metadata tracks are otherwise disabled by default (lines 200–202 comment: "all metadata tracks are disabled by default").
  - `text_track_loader.cc` 119–129: track fetch is "a potential-CORS request ... with the same-origin" mode; when `crossorigin` is absent → `RequestMode::kSameOrigin` (124–126).
- Relevance to AdVTT: Chrome: `<track kind=metadata default>` → mode hidden, cues load; without `default`, script must set `mode='hidden'`. Same-origin request mode is why `file://` pages fail (each file: URL is a distinct/opaque origin in Chromium unless `--allow-file-access-from-files` — see S46). The single-file HTML prototype cannot rely on `<track src="x.vtt">` from disk.

### S43. WebKit `HTMLMediaElement.cpp` — https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/html/HTMLMediaElement.cpp
- Type: repo (browser engine; Safari)
- Verified: fetched (curl, grepped)
- Key facts: line 5613 comment: metadata tracks "that correspond to track elements with a default attribute set whose text track mode..." → implements the same default→hidden step; line 5318 sets in-band metadata dispatch type for kind metadata; 8899–8900 map `Kind::Metadata` → platform `MetaData`.
- Relevance to AdVTT: Safari follows the spec for `default` on metadata tracks. (Safari-specific bugs about metadata cue delivery could not be searched this session — gap; needs a real-device test.)

### S44. Firefox `dom/media/webvtt/vtt.sys.mjs` (vtt.js fork) — https://hg.mozilla.org/mozilla-central/raw-file/tip/dom/media/webvtt/vtt.sys.mjs
- Type: repo (browser engine)
- Verified: fetched (curl, grepped)
- Key facts: line 1424: `if (this.isPrevLineBlank && /^NOTE($|[ \t])/.test(line))` → `LOG("Ignore comment that starts with 'NOTE'")`. **Firefox only recognises a NOTE block when the previous line was blank**; a `NOTE` line directly under `WEBVTT` (no blank line) is *not* a comment there — it becomes part of the header block (harmless) or, after a cue, would be read as a cue identifier/garbage. Text lines appended with `"\n"` (1670–1672).
- Relevance to AdVTT: emit a blank line between `WEBVTT` and `NOTE ADVTT/0.1` (the profile's current example puts NOTE on the line right after WEBVTT — change it). Also a JSON header inside the NOTE whose lines contain `-->` would end the NOTE in every parser; never put `-->` in the header.

### S45. hls.js `src/controller/id3-track-controller.ts`, `src/utils/vttparser.ts`, `src/utils/webvtt-parser.ts` — https://github.com/video-dev/hls.js/tree/master/src
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts:
  - Timed metadata (ID3/EMSG) goes into a TextTrack created as `createTrackNode(media, 'metadata', 'id3', '', 'hidden')` (id3-track-controller.ts 174) using `VTTCue` or `TextTrackCue`/`WebKitDataCue` when available (27, 33–35); cue payloads are ID3 frames, not WebVTT text.
  - WebVTT parsing is a TypeScript port of vtt.js: `case 'NOTE': // Ignore NOTE blocks.` (vttparser.ts 379–389); identifier → `cue.id = line` (401); webvtt-parser.ts 122–126 *synthesises* an id (`generateCueId(start,end,text)`, prefixed `hlsjscc<cc>_`) when none is present.
- Relevance to AdVTT: an HLS subtitle rendition carrying AdVTT would load, but hls.js exposes WebVTT only as subtitle tracks (kind subtitles/captions) — no metadata kind for sidecar VTT; the ad track would need to stay a sidecar `<track>` or be delivered as ID3/EMSG (a different design). Two-line payload survives.

### S46. mpv `sub/lavc_conv.c` — https://raw.githubusercontent.com/mpv-player/mpv/master/sub/lavc_conv.c
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts: mpv has no native SRT/WebVTT parser: text subtitles are decoded by libavcodec with `sub_text_format=ass` (lines 88–92); "Most text subtitles are srt/html style anyway." → `format = "subrip"` (51–53); WebVTT from Matroska is re-assembled by `parse_webvtt()` from identifier/settings side data (126–135, 202–213) — the `webvtt-webm` hack.
- Relevance to AdVTT: mpv's behaviour on `<ad>`, `{ad}`, preambles and zero-duration cues is exactly ffmpeg's (S15, S21, S22) plus libass rendering: `<ad>` stripped, `{ad}` printed literally, preamble tolerated by the lavf demuxer only if the probe passes (S15: numeric first line required for autodetect).

### S47. MKVToolNix `src/common/webvtt.cpp` (Codeberg mirror; gitlab.com raw is Cloudflare-blocked, GitHub mirror 404) — https://codeberg.org/mbunkus/mkvtoolnix/raw/branch/main/src/common/webvtt.cpp
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts: line 125: `additional = settings_list + "\n" + label + "\n" + mtx::string::join(m->local_blocks, "\n");` — i.e. BlockAdditional = settings ⏎ identifier ⏎ preceding NOTE blocks — exactly the Matroska S_TEXT/WEBVTT layout (S7), the *opposite order* from ffmpeg/WebM (identifier ⏎ settings in the Block body, S23). Debug line 130 logs "label … settings list … additional … content".
- Relevance to AdVTT: mkvmerge preserves per-cue NOTE blocks and identifiers (in BlockAdditions) and — per S7/S8 — the pre-cue header (incl. `NOTE ADVTT/0.1`) in CodecPrivate. So an MKV made by **mkvmerge** is the only container path that keeps the whole profile intact; an MKV made by **ffmpeg** keeps id/settings/payload/kind but not the NOTE header; and the two conventions are mutually unintelligible unless the player implements both (mpv/ffmpeg only read `D_WEBVTT/*`; S23 shows `S_TEXT/WEBVTT` is not in ffmpeg's table — so an mkvmerge-made WebVTT track is not even decoded as WebVTT by ffmpeg/mpv/Jellyfin/Plex transcoders).

### S48. pycaption `pycaption/webvtt/reader.py`, `constants.py`, `writer.py` (found via GitHub contents API; webvtt is a package dir now) — https://github.com/pbs/pycaption/tree/main/pycaption/webvtt
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts: `TIMING_LINE_PATTERN = r"^(\S+)\s+-->\s+(\S+)(?:\s+(.*?))?\s*$"` (constants.py 11); `_is_note_start` = `NOTE` / `NOTE ` / `NOTE\t` (124–126); reader state machine skips NOTE/STYLE/REGION blocks until blank (reader.py 237–294); cue ids registered with a duplicate warning (309–316); raises `CaptionReadSyntaxError` for empty file / missing blank line after header / bad timestamps (183–201, 424–426) and `CaptionReadNoCaptions` when no cues (167). Writer escapes `-->` in text as `--&gt;` (writer.py 567).
- Relevance to AdVTT: NOTE header safe; strict about the blank line after the header block. pycaption converts into its own caption model (styling nodes), so JSON text would be re-escaped (`&`→`&amp;`) on output → another reason for `&`.

### S49. Podverse `src/lib/transcriptHelpers.ts` → depends on the `transcriptator` npm package — https://raw.githubusercontent.com/podverse/podverse-rn/develop/src/lib/transcriptHelpers.ts
- Type: repo
- Verified: fetched (curl)
- Key facts: `import { convertFile, Options, TimestampFormatter } from 'transcriptator'` (line 2); all VTT/SRT/JSON/HTML parsing is delegated to `convertFile(data)` (81, 103); errors are caught and logged, returning an empty transcript.
- Relevance to AdVTT: Podverse's tolerance = transcriptator's (to inspect next). A parse failure yields *no transcript*, silently.

### S50. Kodi `DVDSubtitleParserSubrip.cpp`, `DVDSubtitleTagSami.cpp`, `webvtt/WebVTTHandler.cpp` — https://github.com/xbmc/xbmc/tree/master/xbmc/cores/VideoPlayer/DVDSubtitles
- Type: repo
- Verified: fetched (curl, grepped; detail extraction pending)
- Key facts: Kodi has its own SRT parser that runs every line through `CDVDSubtitleTagSami::ConvertLine` (Subrip 29–74), which recognises `<b>`, `<i>`, `<font ...>` (TagSami 94–148) and converts to ASS overrides (`{\c&H..&}` etc.); WebVTTHandler.cpp converts VTT cue CSS to ASS tags (112–172).
- Relevance to AdVTT: Kodi is a third independent tag engine (after ffmpeg and VLC); unknown-tag behaviour to be confirmed from the TagSami source (next extraction).

### S51. Jellyfin `SubtitleEditParser.cs` + `SubtitleEncoder.cs` — https://github.com/jellyfin/jellyfin/tree/master/MediaBrowser.MediaEncoding/Subtitles
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts: external text subtitles are parsed with Nikse **SubtitleEdit** LibSE format classes (`SubRip`, `WebVTT`; parser tries each format registered for the extension and accepts the first with `ErrorCount == 0`, lines 36–74 — otherwise `ArgumentException("Unsupported format")`). Embedded/other subtitles are extracted via ffmpeg `-c:s copy|srt` (`IsCodecCopyable` 504–510 lists srt/subrip/ass/ssa; 839: `-map 0:{1} -an -vn -c:s {2}`).
- Relevance to AdVTT: Jellyfin's SRT tolerance is SubtitleEdit's (LibSE `SubRip.LoadSubtitle` — not fetched; LibSE is known to be lenient but counts errors, and Jellyfin rejects a file with *any* error → a preamble could make the whole sidecar unusable). Embedded WebVTT is converted to SRT via ffmpeg (`-c:s srt`) → JSON mangled per S22.

### S52. RFC 8216 (HLS) §3.5 WebVTT — https://www.rfc-editor.org/rfc/rfc8216.txt
- Type: spec
- Verified: fetched (curl, grepped lines 430–470)
- Key facts: "Each WebVTT Segment MUST either start with a WebVTT header or have an EXT-X-MAP"; "an X-TIMESTAMP-MAP metadata header SHOULD be added to each WebVTT header" mapping cue time to MPEG-TS time.
- Relevance to AdVTT: HLS delivery of a VTT ad track would need segmenting + X-TIMESTAMP-MAP; Apple's authoring spec (JS page, not fetchable here) requires WebVTT subtitles but has no "metadata" rendition type — out of scope for v0.1.

### S53. MKVToolNix `src/output/p_webvtt.cpp`, `src/input/r_webvtt.cpp`, `NEWS.md` (Codeberg mirror) — https://codeberg.org/mbunkus/mkvtoolnix/src/branch/main/src
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts: packetizer constructed with `MKV_S_TEXTWEBVTT` (p_webvtt.cpp 23) — i.e. Matroska `S_TEXT/WEBVTT`; reader sets `m_ti.m_private_data = m_parser->get_codec_private()` (r_webvtt.cpp 54) — the pre-cue header (WEBVTT line, STYLE, REGION, **NOTE**) becomes CodecPrivate (parser: `parsing_global_data ? global_blocks : local_blocks`, webvtt.cpp ~102). NEWS: "mkvmerge: new feature: added support for reading WebVTT subtitles from WebVTT and Matroska files" and "mkvextract: ... extracting WebVTT subtitles" (NEWS.md 5277–5279; release 12.0.0 era, 2017); later "the parser now follows the specs' rules for parsing" (1906).
- Relevance to AdVTT: mkvmerge = lossless container path for the full profile (header + ids + per-cue NOTEs); mkvextract restores the .vtt. But the codec ID is the one ffmpeg does not know (S23), so ffmpeg-based players will show the track as an unknown codec.

### S54. Chromium `content/public/common/content_switches.cc` — https://chromium.googlesource.com/chromium/src/+/main/content/public/common/content_switches.cc
- Type: repo
- Verified: fetched (curl, base64-decoded)
- Key facts: `kAllowFileAccessFromFiles[] = "allow-file-access-from-files"` (line 15), preceded by the comment that by default file:// URIs cannot read other file:// URIs and this switch is "an override for developers who need the old behavior for testing" (14).
- Relevance to AdVTT: combined with S42 (same-origin request mode for `<track>`), a `file://` HTML player cannot load a sidecar `.vtt` via `<track src>` in Chrome without a flag. The prototype must inline the VTT text (`<script type="text/vtt">` + parse + `addCue`) or use a `Blob` URL, or be served over HTTP. Firefox/Safari behaviour for file:// tracks not verified here (gap).

### S55. Kodi wiki "Subtitles" (via MediaWiki API; HTML page is Cloudflare-blocked) — https://kodi.wiki/view/Subtitles
- Type: product docs
- Verified: fetched (API wikitext)
- Key facts: "Text-based subtitle formats supported: SubRip/SRT, VPlayer, SAMI, MPL2, MicroDVD, SubStation Alpha ... SSA/ASS, Closed caption EIA-608/EIA-708, Timed text/TX3G, WebVTT {{note|New on Kodi 20}}".
- Relevance to AdVTT: external `.vtt` sidecars work in Kodi ≥ 20 (2023); Kodi's own VTT parser has a `WebvttSection::NOTE` state (S50: WebVTTHandler.cpp 298–300 `else if (line == "NOTE")`) — **note it matches only a bare `NOTE` line**; `NOTE ADVTT/0.1` on one line may not be recognised as a comment start (needs test; cf. Firefox quirk S44).

### S56. Plex "Adding local subtitles to your media" — https://support.plex.tv/articles/200471133-adding-local-subtitles-to-your-media/
- Type: product docs
- Verified: fetched (curl with browser UA; WebFetch got 403)
- Key facts: supported sidecar formats listed: "SRT (.srt)", "SMI (.smi)", "SSA (or ASS) (.ssa or .ass)", "WebVTT (.vtt)"; naming `Movie (Year).en.srt`, `.en.forced.ass`, `.en.sdh.srt`.
- Relevance to AdVTT: an `.ads.vtt`/`.ads.srt` twin named per Plex's convention (`episode.en.ads.srt` is *not* a recognised suffix — only `forced`/`sdh`/`cc` flags) would be picked up as an ordinary subtitle track only if named `episode.<lang>.srt`; a second sidecar needs a distinct language/flag to coexist. Plex's own text parser behaviour (tags, preamble) not documented → ❓ remains.

### S57. SubtitleEdit LibSE `SubRip.cs` (used by Jellyfin S51 and the SubtitleEdit editor) — https://raw.githubusercontent.com/SubtitleEdit/subtitleedit/main/src/libse/SubtitleFormats/SubRip.cs
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts: state machine `ExpectingLine {Number, TimeCodes, Text}` (30–39); `IsMine` = `Paragraphs.Count > _errorCount` (59); in `Number` state a non-numeric line increments `_errorCount` (186) and a bad timecode line increments it too (203); a text line that is an integer followed by a timecode line ends the paragraph (208–214) — a digits-only *last* text line is swallowed as the next index.
- Relevance to AdVTT: a preamble is an *error* here (not fatal for SubtitleEdit, but Jellyfin accepts a file only when `ErrorCount == 0`, S51 → preamble = ❌ in Jellyfin's sidecar path). Digits-only last line hazard same as pysubs2/astisub.

### S58. SubtitleEdit LibSE `WebVTT.cs` — https://raw.githubusercontent.com/SubtitleEdit/subtitleedit/main/src/libse/SubtitleFormats/WebVTT.cs
- Type: repo
- Verified: fetched (curl, grepped)
- Key facts: NOTE recognised only when the previous line is empty: `if (index > 0 && string.IsNullOrEmpty(lines[index - 1]) && (line == "NOTE" || line.StartsWith("NOTE ", ...)))` (255–256); the header (everything before the first cue) is accumulated and kept (250–262); STYLE only before the first paragraph (265); timing-line parse failures `_errorCount++` (376). Timing regexes require `-->` with `.`-millisecond timestamps (18–34).
- Relevance to AdVTT: same "blank line before NOTE" requirement as Firefox (S44) — two independent implementations, so treat it as a de-facto rule: **always precede NOTE with a blank line.** LibSE keeps the header verbatim (useful for SubtitleEdit users) but rewrites cues through its paragraph model.

### S59. Firefox `dom/media/webvtt/TextTrackManager.cpp` — https://hg.mozilla.org/mozilla-central/raw-file/tip/dom/media/webvtt/TextTrackManager.cpp
- Type: repo (browser engine)
- Verified: fetched (curl, grepped)
- Key facts: line 334 comment "Step 4: Set all TextTracks with a kind of metadata that are disabled" and 338 `if (track->Kind() == TextTrackKind::Metadata && TrackIsDefault(track) && ...)` → hidden.
- Relevance to AdVTT: all three engines (S42 Chromium, S43 WebKit, S59 Gecko) implement `default` → hidden for metadata tracks; the prototype can rely on `<track kind="metadata" default>`.

### S60. Chromium Blink `vtt_parser.cc` — https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/core/html/track/vtt/vtt_parser.cc
- Type: repo (browser engine)
- Verified: fetched (curl, base64-decoded)
- Key facts: the parser has **no NOTE-specific code** (grep for NOTE/comment: none). States: kHeader → (REGION/STYLE) → kId → kTimingsAndSettings → kCueText → kBadCue (150–205). A `NOTE ...` line in kId state is taken as a cue identifier (`CollectCueId`); the following non-timing line sends the parser to kBadCue, which "Discard[s] lines until an empty line or a potential timing line is seen" (199–203). Header lines (before the first blank) are consumed in kHeader (293–318, `CheckAndRecoverCue` looks for `-->`).
- Relevance to AdVTT: NOTE blocks are dropped in Chrome via the bad-cue recovery path — functionally fine, but it means **any line of the NOTE body that contains `-->` starts a real cue** (also true of S5/S12). The header JSON must never contain `-->` (already in the profile's escaping rules; extend the rule to the header explicitly). Multi-line NOTE bodies are otherwise safe in all engines.

### S21 (correction after reading the raw file, exact lines) — ffmpeg `libavcodec/htmlsubtitles.c`
- `handle_open_brace` (69–87): only `{\...}` sequences (when not the single honoured `{\anN}`) and MicroDVD `{C:|c:|F:|f:|o:|P:|S:|s:|Y:|y:}` blocks are skipped (76–81); **any other `{` is written through unescaped** — `av_bprint_chars(dst, *in, 1)` (86). Unknown `<tag>`: `av_log(... "Unrecognized tag %s\n")` and skipped (291–293); a `<` that is not `likely_a_tag` (e.g. `<<`) is output literally (183–199, 295).
- Consequence (inferred, needs experiment): an SRT cue text `{ad}` arrives in the ASS event as `{ad}` *unescaped*, and libass treats `{...}` as an override block, silently ignoring unknown tags — so in **mpv (and any ffmpeg→libass pipeline) `{ad}` would most likely be invisible**, not "❌ literal" as the matrix says. VLC (S20) and ExoPlayer (S32) show it literally. This makes `{ad}` the *least* predictable marker: hidden in some players, shown in others.

### S61. `transcriptator` npm (stevencrader/transcriptator; the parser behind Podverse S49) `src/formats/vtt.ts`, `src/formats/srt.ts` — https://github.com/stevencrader/transcriptator/tree/master/src/formats
- Type: repo
- Verified: fetched (curl; `main` branch 404, `master` works; v1.1.4 on npm)
- Key facts:
  - `isVTT` = `data.startsWith("WEBVTT")` (vtt.ts 15–16); `parseVTT` strips the literal `WEBVTT` token, `trimStart()`s and hands the rest to `parseSRT(..., true)` (31–32) — VTT is parsed as SRT with an optional index.
  - `isSRT` validates by parsing **the first 20 lines as one segment**: `parseSRTSegment(data.split(...).slice(0, 20), dataIsVTT)`; any throw → `false` → `parseSRT` throws `TypeError("Data is not valid SRT format")` (srt.ts ~130–150) — i.e. **the whole transcript is rejected**.
  - `parseSRTSegment`: `let index = Number(lines[0]); if (!index) { if (indexOptional) {currentIndex = 0} else throw "First line of SRT segment is not a number" }` (58–68); then `if (!timestampLine.includes("-->")) throw` (70–73). So: SRT cue numbered **`0` is rejected** (0 is falsy); a VTT whose first block is a **NOTE**, a **header line**, or a cue with a **non-numeric identifier** (`ad-001`) makes the *first-20-lines* probe throw → **entire VTT rejected**. Later malformed segments are only logged (`console.error`, ~160–166) and skipped.
  - Speaker detection via `parseSpeaker(bodyLines.shift())` (first body line, `Name:` convention).
- Relevance to AdVTT: (1) never put `NOTE ADVTT/0.1` first in any VTT that could be consumed as a *transcript*; (2) caption VTTs meant for `<podcast:transcript>` must use numeric identifiers or none; (3) an SRT twin must start at `1`, not `0`; (4) the ads track itself must be published under a distinct role/URL, never as a transcript.

## Synthesis

**Universal facts (every parser fetched agrees):**
- Multi-line cue payloads are preserved as separate lines or `\n`-joined text by every WebVTT consumer that keeps text at all: webvtt-py (S1), vtt.js/Firefox/hls.js (S12, S44, S45), node-webvtt (S4), W3C parser (S5), Chromium (S60), ExoPlayer (S31, with per-line trim), VLC (S19), ffmpeg demux/copy (S13, S14), astisub (S28), pycaption (S48), LibSE (S58). Only lossy *re-encoders* alter it: pysubs2 joins with `\N` (S3), ffmpeg `-c:s srt/ass/webvtt` re-encode converts to ASS (`\N`, `\{`, entity decoding, tags eaten) (S22), ttconv re-flows (S34). **Two-line token+JSON is therefore no less portable than JSON-only**; the token line costs nothing anywhere.
- `{` `}` and `"` are inert in every WebVTT parser (S5, S12, S31, S60 — no brace handling). `-->` inside *any* line (cue text or NOTE body) starts a new cue in vtt.js/W3C/Chromium/Firefox/pycaption/AntennaPod/transcriptator (S5, S12, S48, S60, S40, S61). `<` and `&` are only dangerous where cue-text markup parsing runs: `getCueAsHTML()` (S38), ExoPlayer always (S31), ffmpeg re-encode (S22), astisub/pycaption writers re-escape (S28, S48). MDN explicitly says the `&`/`<` restriction "do[es] not apply" for metadata use (S37) — browsers' `cue.text` stays raw.
- NOTE blocks are unreadable by design ("ignored by the parser", S25; "not seen by users", S37) and are dropped by ffmpeg (S13/S14), VLC (S19), pysubs2 (S2), node-webvtt (S4), W3C (S5), vtt.js family (S12/S44/S45), ExoPlayer (S30), pycaption (S48), Chromium (S60). Only webvtt-py (S1), astisub (S28), LibSE (S58, header only) and mkvmerge (S53) preserve them.
- **NOTE recognition quirks:** Firefox (S44) and LibSE (S58) require a *blank line before* `NOTE`; Kodi's handler matches only a bare `NOTE` line (S50/S55); transcriptator rejects a VTT whose first block is NOTE (S61); Chromium has no NOTE code and relies on bad-cue recovery (S60). So `WEBVTT⏎NOTE ADVTT/0.1` (no blank line) as drawn in 02-webvtt-profile §2 is non-portable.
- Cue identifiers: kept by browsers, VLC, ffmpeg (side data), webvtt-py, node-webvtt, hls.js; **rewritten to integers** by astisub (S28); **not stored** by ExoPlayer (S31); dropped by pysubs2 (S2); **fatal for the whole file** in transcriptator when non-numeric on the first cue (S61). Identifiers cannot be load-bearing.
- Browser text tracks: default mode `disabled` → no cues fetched (S17); `<track kind=metadata default>` → `hidden` in Chromium (S42), WebKit (S43), Gecko (S59) per the HTML spec (S41). Cue activation runs on the 15–250 ms "time marches on" cadence (S41). `<track src>` is a same-origin fetch unless `crossorigin` (S9, S42); Chromium treats file:// as isolated without `--allow-file-access-from-files` (S54). DataCue is WebKit-only incubation (S36).
- SRT: no spec, no comments, in every de-facto description (S7, S11, S15, S18, S39). Parsers disagree on the preamble: **fatal** for the `srt` lib (S11), ffmpeg autodetect/mpv (S15, S46), Jellyfin via LibSE error counting (S51, S57), transcriptator (S61); **tolerated** by VLC (S18), pysubs2 (S3), pysrt (S27), ExoPlayer (S32), AntennaPod (S40), Kodi (S50). Cue `0`: fine everywhere except transcriptator (S61). Digits-only *last* text line is swallowed as the next index by pysubs2 (S3), astisub (S28), LibSE (S57) — relevant to any inline marker design that ends a cue with a number.
- SRT tags: `<ad>` stripped with a warning by ffmpeg/mpv (S21, S46), by Kodi's regex (S50), by pysubs2 default (S3); hidden by VLC **only if closed** (S20); ExoPlayer `Html.fromHtml` (S32, behaviour inferred). `{ad}`: shown literally by VLC (S20) and ExoPlayer (S32), but passed *unescaped* into ASS by ffmpeg (S21 correction) so libass-based players (mpv, Kodi) most likely hide it; ttconv treats `{b}`-style as formatting (S34). Zero-duration: unvalidated by ffmpeg (S15); dropped by `srt.sort_and_reindex` (S11); rejected in node-webvtt strict mode (S4); WebVTT authoring requires end > start (S25).
- Containers: Matroska's official `S_TEXT/WEBVTT` (header in CodecPrivate; settings⏎id⏎NOTEs in BlockAdditions — S7, S8, mkvmerge S47/S53) vs WebM's `D_WEBVTT/<KIND>` (id⏎settings⏎payload in the Block; no CodecPrivate — S16), and **ffmpeg only implements the WebM flavour, even in .mkv, and does not list `S_TEXT/WEBVTT` at all** (S23). mpv re-parses the WebM flavour (S46). `D_WEBVTT/METADATA` maps to a *disposition*, not to non-display behaviour (S23).
- Podcast transcript apps: AntennaPod ignores everything but `-->` lines (S40); Podverse/transcriptator is fragile (S61); Apple applies an opaque quality gate (S35); the P2.0 doc is caption-shaped and silent on NOTE/identifiers (S10).

**Contradictions/gaps:** WebFetch summaries of large files were sometimes wrong (S23 initially claimed no VTT block writer; corrected by grep). Plex/Infuse/Jellyfin *player* parsing behaviour for tags/preambles is undocumented (S56; Infuse page not found). Safari-specific metadata-cue bugs, Fountain/Castamatic parsers, AVPlayer sidecar VTT, and libass's exact handling of `{ad}` were not verifiable this session (WebSearch budget exhausted; DeepWiki auth-blocked).

## Implications for AdVTT

1. **Keep the two-line token+JSON payload.** No parser fetched treats line 1 differently from line 2; the only consumers that damage it (pysubs2 `\N`, ffmpeg re-encode, ttconv) would damage JSON-only identically (S3, S22, S34). Do not switch to JSON-only for portability reasons — the degradation argument in 02-§1 stands. (S1, S4, S5, S12, S13, S19, S31, S60)
2. **Make the NOTE header optional and non-load-bearing** — effectively a "NOTE-free" design with an optional human-readable NOTE. Every machine-relevant field (`v`, `id`, `type`, thresholds actually applied, `status`) must be recoverable from cues + `analysis.json`; consumers must never need the NOTE (S13, S14, S19, S30, S60). Because a non-`ok` status yields zero cues, the "no cues" case must be distinguishable without the NOTE → write `analysis.json` always, and consider a single zero-length `PROGRAM`-type or `STATUS` cue at 00:00:00.000 → 00:00:00.001 as the in-band status carrier (needs the zero-duration experiment below).
3. **NOTE placement rules:** blank line between `WEBVTT` and `NOTE`; NOTE marker on its own line or `NOTE ADVTT/0.1` only after a blank; never `-->` anywhere in the NOTE body (`-->` if it must appear); never let the ads VTT be served as a `<podcast:transcript>` (S44, S58, S55, S60, S61, S35).
4. **Identifiers:** keep them (browsers/VLC/ffmpeg/webvtt-py preserve them) but treat them as cosmetic; the JSON `id` is normative. For *caption* VTTs AdVTT emits, use numeric identifiers or none, because transcriptator rejects non-numeric first identifiers (S28, S31, S61).
5. **Escaping:** keep `<`/`&`/`-->` JSON escapes — ExoPlayer runs the markup parser unconditionally (S31), astisub/pycaption re-escape on write (S28, S48), `getCueAsHTML()` decodes (S38). Add a normative sentence: consumers MUST read `cue.text`, MUST NOT use `getCueAsHTML()`.
6. **HTML player:** use `<track kind="metadata" default>` (→ hidden in all three engines, S42/S43/S59) *and* set `mode='hidden'` defensively; wait for the track `load` event before reading `cues` (S17). Because of same-origin + file:// isolation (S42, S54), the single-file prototype must embed the VTT text and `addCue()` it (or accept a file picker → `URL.createObjectURL`), not `<track src="episode.ads.vtt">`. Compute skip targets from `cue.startTime/endTime`, tolerate 250 ms event latency (S41).
7. **SRT matrix revisions (03-§3):** row 5 (preamble): ❌ for ffmpeg/mpv autodetect (S15), `srt` lib (S11), Jellyfin sidecar (S51/S57), Podverse (S61); ✅ VLC, ExoPlayer, AntennaPod, Kodi, pysrt, pysubs2 — keep the verdict "no". Cue `0`: ✅ everywhere except Podverse (S61) — still "no" for twins/inline. Row 4 `<ad>`: stripped by ffmpeg/mpv/Kodi/pysubs2; VLC only when closed → if ever offered, emit `<ad></ad>` pairs (S20, S21, S50). Row 4b `{ad}`: change "❌ literal" for mpv/ffmpeg to "❓ probably hidden (unescaped into ASS)" (S21 corrected) — the row is now *inconsistent across players*, which is a stronger reason to drop it than "always literal". Row 3b zero-duration: add "dropped by `srt.sort_and_reindex` (S11), rejected by node-webvtt strict (S4)". Row 2 twin: avoid `Speaker: ` colon-space in the marker text (AntennaPod S40, transcriptator S61 treat it as a speaker) — use `[ADVERTISEMENT — Acme]` with a dash, never a colon; start numbering at 1. Digits-only last line hazard (S3, S28, S57): never end a cue with a bare number.
8. **MKV/WebM embedding is viable as transport, not as semantics.** `ffmpeg -i ep.mkv -i ep.ads.vtt -c copy -disposition:s:1 metadata` yields `D_WEBVTT/METADATA` with id/settings/payload intact and round-trips back to VTT via `-c:s copy` (S13, S14, S23), losing only the NOTE header (fine given #2). But: players treat it as a subtitle track that would *display* `ADVERTISEMENT {json}` if selected (S19, S46); mkvmerge writes the incompatible `S_TEXT/WEBVTT` that ffmpeg/mpv/Jellyfin/Plex cannot even decode (S23, S53); WebM allows only WebVTT text tracks (S23). Offer `--embed mkv|webm` as an *opt-in archival* feature built on ffmpeg's convention, document the two-convention split, and keep the sidecar primary. MP4/`wvtt` and HLS (S52) are out of scope for v0.1.
9. **Chapters are a distraction for this problem, but a `kind=chapters` twin is a cheap, visible degradation path** — same file shape, rendered by browsers as chapter markers; keep in mind as an alternative to the SRT visible twin for web players (not evidenced here; experiment).

## Open questions / things that need an experiment

- Zero-duration and 1 ms cues: do Chrome/Firefox/Safari fire `cuechange`/`enter` for `start == end`? (spec requires end > start for authoring, S25; browser behaviour untested).
- libass on `{ad}` from ffmpeg's unescaped SRT conversion (S21) — confirm hidden vs shown in mpv and Kodi; confirm ExoPlayer `Html.fromHtml` drops `<ad>`.
- Kodi WebVTTHandler with `NOTE ADVTT/0.1` on one line (S50/S55): comment or garbage cue?
- Safari: any WebKit bug where `kind=metadata` cues are not delivered for `<audio>` (not `<video>`) elements; file:// behaviour of `<track>` in Safari/Firefox (S54 covers Chromium only).
- Plex, Infuse, Fountain, Castamatic, Apple Podcasts: closed parsers — build a fixture pack (NOTE-first VTT, non-numeric identifiers, cue 0, preamble, `<ad></ad>`, `{ad}`, zero-duration) and test manually.
- Whether any player treats `D_WEBVTT/METADATA` as non-display (S23) — probably none; verify in mpv/VLC/Kodi.
- Podcast Index / P2.0 reaction to a `rel`/`type` for ad-marker tracks in the transcript tag (governance question for another track).
