# L. SponsorBlock silver labels for JRE (YouTube mirrors vs RSS audio)

Status: COMPLETE — 2026-09-06 04:52 PDT (agent `sponsorblock`). 15/15 JRE episodes matched on YouTube with SponsorBlock coverage; 5 fixture silver files written with `method: stitch-map-shift` (3 cross-checked by envelope alignment, residual ≤ 0.1 s); RSS = YouTube master + Megaphone-stitched creatives. Step log: `data/logs/sponsorblock.log`.

Licence note (applies to everything in this file and in `data/sponsorblock/`): SponsorBlock data is **CC BY-NC-SA 4.0** (wiki "Database-and-API-License", see I-S1/I-S2). It is used here for **evaluation only** and must never be used to train, fine-tune or tune prompts. Attribution: "SponsorBlock data, https://sponsor.ajay.app, CC BY-NC-SA 4.0".

Inputs/outputs:
- `data/logs/jre-feed-items.json` — JRE RSS items (last 30 days) with guid/title/pubDate/enclosure/duration.
- `data/sponsorblock/<video_id>.json` — raw SponsorBlock API responses.
- `data/sponsorblock/<stem>_silver.json` — segments mapped into RSS time (when alignment succeeds).
- `data/sponsorblock/summary.json` — one entry per episode.

## Method

1. Fetch `https://feeds.megaphone.fm/GLT1412515089` (stdlib urllib, UA `AdVTT/0.1`), parse with `xml.etree`, keep items with pubDate in the last 30 days. Durations from `itunes:duration` (no audio downloaded by this agent).
2. For each item, `uvx yt-dlp --dump-json --flat-playlist "ytsearch10:Joe Rogan Experience #<n> <guest>"`; accept the hit whose channel is PowerfulJRE and whose duration is within 10% of the RSS duration.
3. `GET https://sponsor.ajay.app/api/skipSegments?videoID=<id>&categories=[...]` (3 retries, backoff). `locked` = gold, `votes >= 2` = silver.
4. Alignment (up to 3 episodes, only if the other agent's RSS copy exists at `data/episodes/jre/<stem>.a.mp3`): 8 kHz mono PCM via ffmpeg, 100 ms energy envelope, cross-correlation in three windows (first 5 min, around each sponsor segment, last 5 min). Offsets that disagree by > 1 s are reported as evidence of dynamic insertion / different cuts.

## Findings (appended as they arrive)

### Feed (fetched 2026-09-06 04:11 PDT)

`https://feeds.megaphone.fm/GLT1412515089` returned 5.39 MB, 2747 items; **15 items in the last 30 days** (2026-08-07 .. 2026-09-03): 13 numbered episodes (#2537–#2549) plus 2 "JRE MMA Show" episodes (#184, #185). Durations (itunes:duration) 9037–16470 s (2.5–4.6 h). Saved to `data/logs/jre-feed-items.json`.

### YouTube matches (yt-dlp 2026.08.19 via uvx, `ytsearch10`, no bot-check encountered)

All **15/15** episodes have a full-length upload on PowerfulJRE (`UCzQUP1qoWDoEbmsQxvdjxgQ`). Every match is the first search hit; other hits are clips, summaries and re-uploads.

| Episode | RSS itunes:duration (s) | YouTube id | YouTube duration (s) | RSS − YT (s) |
|---|---|---|---|---|
| #2549 - Jared Diamond | 9254 | `t6Jrww8kG24` | 8895 | 359 |
| JRE MMA Show #185 with Ethyn Ewing | 9756 | `efwqfxt717Q` | 9397 | 359 |
| #2548 - Brian Simpson | 10196 | `x04pr4QLl7o` | 9837 | 359 |
| #2547 - Daniel Everett | 9828 | `EmgKSK-YMOU` | 9469 | 359 |
| #2546 - Michael Button | 9468 | `rnt0wEc9YmI` | 9109 | 359 |
| #2545 - Jesse Michels | 11349 | `33Fc_mLqY90` | 10990 | 359 |
| #2544 - Chris Williamson | 10835 | `vh8FkZaQ06I` | 10476 | 359 |
| #2543 - MrBallen | 10937 | `fddF7pRu9Fs` | 10578 | 359 |
| #2542 - Steve Hilton | 11132 | `BYVQfLi6wMA` | 10773 | 359 |
| #2541 - Thomas Campbell | 10382 | `v2oBLSDCZaY` | 10023 | 359 |
| #2540 - Travis Barker | 9381 | `9iENvZ2siTo` | 9022 | 359 |
| #2539 - Protect Our Parks 17 | 16470 | `OBH4F5a6zAA` | 16111 | 359 |
| #2538 - Joe DeRosa | 10047 | `pCH-R3L6QTc` | 9688 | 359 |
| JRE MMA Show #184 with Aljamain Sterling | 10507 | `xEBeQH39CZI` | 10148 | 359 |
| #2537 - David Sinclair | 9037 | `hxid7FofhMw` | 8678 | 359 |

**Finding L1 — constant 359 s delta.** RSS `itunes:duration` exceeds the YouTube duration by exactly 359 s on all 15 episodes. A per-episode edit would not produce a constant; this looks like a fixed ad allotment that Megaphone declares in the feed (e.g. a 5:59 DAI budget: pre-roll + mid-rolls) added to the programme length, with the YouTube upload being the programme cut. Whether the delivered MP3 is actually 359 s longer than the YouTube cut is for the differential-download agent (`M-dai-check.md`) to confirm; the `itunes:duration` may be a declared value rather than a measured one. Either way the RSS and YouTube versions are **not the same cut**, and any SponsorBlock timestamp transfer must account for inserted ad time that shifts the offset as the episode progresses.

### SponsorBlock coverage (API queried 2026-09-06 ~04:15 PDT; raw JSON in `data/sponsorblock/<id>.json`)

**15/15 videos have SponsorBlock segments** (HTTP 200 for all). Totals: 72 segments, 33 `sponsor` segments (1854 s, mean 124 s/episode, 2.2 segments/episode). Segments with votes >= 2: **1** of 72. Locked: **0**.

| Episode | YT id | Segs | By category | Sponsor segs | Sponsor s | Sponsor spans (YouTube time) | votes>=2 | locked | videoDuration / YT / RSS |
|---|---|---|---|---|---|---|---|---|---|
| #2549 - Jared Diamond | `t6Jrww8kG24` | 6 | intro:2, outro:1, sponsor:3 | 3 | 114 | 0–2 (2s, v0); 1105–1177 (72s, v0); 3226–3265 (39s, v0) | 0 | 0 | 8894.403 / 8895 / 9254 |
| JRE MMA Show #185 with Ethyn Ewing | `efwqfxt717Q` | 5 | intro:2, outro:1, sponsor:2 | 2 | 111 | 1098–1166 (68s, v0); 3211–3255 (44s, v0) | 0 | 0 | 9396.744 / 9397 / 9756 |
| #2548 - Brian Simpson | `x04pr4QLl7o` | 6 | intro:2, outro:1, sponsor:3 | 3 | 160 | 0–2 (2s, v0); 1134–1222 (87s, v0); 3317–3387 (70s, v0) | 0 | 0 | 9837 / 9837 / 10196 |
| #2547 - Daniel Everett | `EmgKSK-YMOU` | 6 | intro:2, outro:1, sponsor:3 | 3 | 130 | 0–2 (2s, v0); 1146–1205 (59s, v0); 3240–3308 (68s, v0) | 0 | 0 | 9469 / 9469 / 9828 |
| #2546 - Michael Button | `rnt0wEc9YmI` | 5 | intro:2, outro:1, sponsor:2 | 2 | 140 | 1209–1276 (68s, v2); 3309–3382 (72s, v1) | 1 | 0 | 9109 / 9109 / 9468 |
| #2545 - Jesse Michels | `33Fc_mLqY90` | 4 | intro:1, sponsor:3 | 3 | 138 | 1133–1211 (78s, v1); 3190–3246 (56s, v0); 3654–3657 (3s, v0) | 0 | 0 | 10990 / 10990 / 11349 |
| #2544 - Chris Williamson | `vh8FkZaQ06I` | 4 | intro:1, outro:1, sponsor:2 | 2 | 147 | 1122–1212 (90s, v0); 3309–3366 (57s, v0) | 0 | 0 | 10475 / 10476 / 10835 |
| #2543 - MrBallen | `fddF7pRu9Fs` | 5 | intro:2, outro:1, sponsor:2 | 2 | 150 | 1138–1215 (78s, v0); 2859–2932 (72s, v0) | 0 | 0 | 10578 / 10578 / 10937 |
| #2542 - Steve Hilton | `BYVQfLi6wMA` | 3 | intro:1, outro:1, sponsor:1 | 1 | 68 | 1146–1214 (68s, v0) | 0 | 0 | 10772 / 10773 / 11132 |
| #2541 - Thomas Campbell | `v2oBLSDCZaY` | 4 | intro:1, outro:1, sponsor:2 | 2 | 137 | 984–1074 (91s, v1); 3403–3449 (46s, v0) | 0 | 0 | 10022.561 / 10023 / 10382 |
| #2540 - Travis Barker | `9iENvZ2siTo` | 6 | intro:2, outro:2, sponsor:2 | 2 | 104 | 1143–1199 (57s, v0); 3114–3161 (47s, v0) | 0 | 0 | 9022 / 9022 / 9381 |
| #2539 - Protect Our Parks 17 | `OBH4F5a6zAA` | 3 | intro:1, sponsor:2 | 2 | 126 | 1081–1168 (87s, v0); 3215–3255 (39s, v1) | 0 | 0 | 16111 / 16111 / 16470 |
| #2538 - Joe DeRosa | `pCH-R3L6QTc` | 5 | intro:2, outro:1, sponsor:2 | 2 | 120 | 1162–1221 (59s, v0); 3299–3359 (60s, v0) | 0 | 0 | 9688 / 9688 / 10047 |
| JRE MMA Show #184 with Aljamain Sterling | `xEBeQH39CZI` | 5 | intro:2, outro:1, sponsor:2 | 2 | 120 | 1075–1147 (72s, v0); 3177–3224 (47s, v0) | 0 | 0 | 10148 / 10148 / 10507 |
| #2537 - David Sinclair | `hxid7FofhMw` | 5 | intro:2, outro:1, sponsor:2 | 2 | 91 | 1104–1147 (43s, v0); 3153–3201 (47s, v0) | 0 | 0 | 8678 / 8678 / 9037 |

**Finding L2 — coverage is broad but shallow.** Every recent JRE upload has segments, but the crowd has barely voted (nearly all `votes: 0`, one segment at 2, none locked). By the brief's tiers there is no gold and almost no silver; what exists is "bronze" (single-submitter, unvoted, not hidden — the API already filters hidden/shadowHidden/negative segments). For evaluation these are still usable: the pattern is extremely regular across episodes, which is itself corroboration.

**Finding L3 — a stable JRE ad structure in the YouTube cut.** Almost every episode has: `intro` 0–12 s (the JRE cold-open sting; sometimes a 0–2 s `sponsor` stub in front of it), a first host-read `sponsor` block at ~1075–1220 s (about 18–20 min in, 43–90 s long), a second at ~2860–3450 s (about 53–57 min in, 39–73 s long), and an `intro`+`outro` pair in the last ~15 s. Per-episode sponsor load is 68–160 s (1.1–2.7 min) over a 2.4–4.5 h show, i.e. ~0.5–1 min of host-read sponsorship per hour in the YouTube cut. The RSS copy carries a further 359 s of (declared) ad time that does not exist on YouTube at all (L1), so a classifier run on the RSS audio should find the two host-read blocks *plus* whatever Megaphone inserted.

Caveats on the labels themselves: SponsorBlock's `sponsor` boundaries here are crowd-drawn on the video; the 0–2 s "sponsor" stubs (#2549, #2548, #2547) and the 3 s stub at 3654–3657 in #2545 are noise; #2542 (Steve Hilton) has only one sponsor segment labelled (the second block may be unlabelled — DeepSponsorBlock found half of gross errors were missing labels, I-S5). #2540 (Travis Barker) has an `outro` at 8857–8859 well before the end, likely mis-categorised.

### The President's Daily Brief — quick check (one search, one API call, 04:14 PDT)

`ytsearch10:The President's Daily Brief full episode` returns ten videos, all on the channel **"The President's Daily Brief"** (`UCbWraa1DoXrFwX3oK1zattQ`), durations 810–3793 s — the same range as the RSS episodes (morning brief ~23 min, afternoon bulletin ~14 min, longer weekend/sitrep shows), so full episodes are on YouTube, not only clips. SponsorBlock for `gzBxYg0e1vI` ("U.S. Launches 'Tanker for Tanker' Strikes Against Iran", 1356 s): HTTP 200, **3 `sponsor` segments — 336–400, 941–1003, 1261–1324 s (189 s total, ~14% of the video)**, votes 0, none locked (raw in `data/sponsorblock/pdb/gzBxYg0e1vI.json`). So PDB is also a candidate for SponsorBlock silver labels; its RSS copies were found to be DAI-identical by the `fixtures-pdb` agent, so a single global offset may suffice there — worth a follow-up, not done in this pass.

Title match for that PDB video: RSS item "September 3rd, 2026: U.S. Launches “Tanker for Tanker” Strikes Against Iran", itunes:duration 00:23:00 = 1380 s vs YouTube 1356 s (RSS − YT = 24 s, not the JRE-style 359 s), so the PDB YouTube cut is close to but not identical with the feed's declared length; a pre-roll-sized difference.

### Alignment tool (`scripts/sb_align.py`) — validated on synthetic data

Before any real alignment, the tool was tested on a PDB RSS file with 30 s of pink noise prepended and 45 s inserted at 400 s (a stand-in for pre-roll + one mid-roll). Recovered offsets: first-5-min window +30.0 s, window around a "sponsor" at 100 s +30.0 s, window around a "sponsor" at 600 s +75.0 s, last-5-min window +75.0 s; NCC peak 1.00 with the runner-up at 0.11–0.13; verdict "different cut: offset varies by window". Offset convention: `rss_time = yt_time + offset`; resolution 100 ms; lag search −120..+720 s (widened per episode if needed).

### Draft answers to (d) and (e) — to be refined after real alignment

**(d) What a comparison of AdVTT spans against these labels needs.**
1. A time map from YouTube to RSS time per episode (`data/sponsorblock/<stem>_silver.json` carries `rss_segment` per segment plus the window offset and a confidence; use only `confidence: high/medium`). Because the offset steps at each inserted ad (L1), never apply one global offset to a 3-hour JRE file.
2. Category mapping: SponsorBlock `sponsor` ↔ AdVTT host-read sponsorship/advertisement; `selfpromo` ↔ AdVTT promotion/crosspromo (none present in these 15); `intro`/`outro`/`preview`/`interaction` are not ads and must be excluded from the ad-recall denominator (the 0–12 s JRE sting is `intro`, not an ad).
3. The silver set is **incomplete by construction**: it covers only what exists in the YouTube cut. The 359 s of DAI/pre-roll material in the RSS copy has no SponsorBlock label at all, so AdVTT spans that fall in the offset "steps" (between two windows whose offsets differ) are *unlabelled*, not false positives. The comparison must treat those regions as "ignore" (like TRECVID's don't-care regions), or the M-dai-check agent's differential download must supply labels for them.
4. Tolerance: the crowd boundaries are drawn by eye on video; the 0–2 s "sponsor" stubs and the 3 s stub in #2545 show ±2–3 s jitter and junk segments < 5 s. Use the project's 3 s detection tolerance and drop SponsorBlock segments shorter than 5 s before scoring; report both event-level P/R (segment overlap) and second-level P/R.
5. Vote tiers: with 1 of 72 segments at votes ≥ 2 and none locked, "silver" per the brief is essentially empty. Score against all non-hidden segments (the API already excludes hidden/shadow-hidden/negative-score ones) and report vote counts alongside, rather than filtering to an empty set.
6. Duration binding: the RSS rendition AdVTT is run on must be the same file that was aligned (sha256 in `tests/fixtures/manifest.json`); a DAI-different second download invalidates the map.

**(e) Licence.** SponsorBlock data (API responses, the derived `_silver.json` files, and any tables here) is **CC BY-NC-SA 4.0**. Use: evaluation and reporting only. Do not train, fine-tune, few-shot, or tune prompts/thresholds on it, and do not redistribute it under a different licence; if published, attribute "SponsorBlock (https://sponsor.ajay.app), CC BY-NC-SA 4.0" and keep the SA terms. `data/` is gitignored, so none of it is committed.

### Correction to L1 (04:27 PDT, after the `fixtures-jre` downloads landed)

The five RSS copies the `fixtures-jre` agent downloaded (`ffprobe` durations) versus their YouTube uploads:

| Episode | RSS file (s) | itunes:duration (s) | YouTube (s) | file − YT (s) | file − declared (s) |
|---|---|---|---|---|---|
| #2548 Brian Simpson | 10600.8 | 10196 | 9837 | 764 | 405 |
| #2547 Daniel Everett | 10229.7 | 9828 | 9469 | 761 | 402 |
| #2542 Steve Hilton | 11551.1 | 11132 | 10773 | 778 | 419 |
| #2540 Travis Barker | 9820.4 | 9381 | 9022 | 798 | 439 |
| JRE MMA #184 Aljamain Sterling | 10884.9 | 10507 | 10148 | 737 | 378 |

So the feed's `itunes:duration` is a **declared** value (programme + a fixed 359 s allowance) and the delivered file is 737–798 s longer than the YouTube cut — roughly 12–13 min of Megaphone-stitched ads per episode, twice the declared allowance. The `fixtures-jre` agent's `x-megaphone-payload-2` header for #2548 lists 13 stitched ads (3 pre, 8 mid, 2 post) totalling 764.0 s, which matches file − YT = 764 s exactly. Consequences: (1) any consumer that trusts `itunes:duration` to bind a record to a rendition will be ~400 s off for JRE; (2) the YouTube→RSS offset must step at each of the 13 insertion points, so per-window alignment is mandatory (confirmed empirically below).



## Orchestrator section: comparison on the one JRE episode with hand truth (#2537), 2026-09-06 04:40 PDT

SponsorBlock on `hxid7FofhMw` (YouTube master, 8678 s): 2 `sponsor` segments,
1104–1147 s (43 s) and 3153–3201 s (47 s), plus intro/outro; 0 votes, unlocked.
The RSS fixture copy (9037 s = 8678 + 359) carries eight ad pods in the hand
truth: six inserted pods (701 s) and two host-read reads (90 s). Mapping
YouTube time to RSS time by adding the inserted seconds that precede each
point (no audio alignment needed; the YouTube upload is the ad-free master):

| SponsorBlock (YouTube) | → RSS time | Hand truth (RSS) | Δ |
|---|---|---|---|
| sponsor 1104–1147 | 1262–1305 | Superpower host-read 1263–1306 | ≤ 1 s |
| sponsor 3153–3201 | 3399–3447 | BetterHelp host-read 3400–3447 | ≤ 1 s |

So on this episode:

- **AdVTT recall against SponsorBlock: 100%** (both host-read segments caught
  by Sonnet 5, Opus 5 and Haiku 4.5 at the skip threshold; K1a).
- **SponsorBlock recall against the RSS copy: 90 / 791 s = 11%.** The other
  701 s are Megaphone-inserted creatives that do not exist on YouTube, so no
  YouTube-side label set can ever describe them. The Megaphone stitch map
  (track M) is the ground truth for that channel.
- Precision of AdVTT against the hand truth is unaffected (0 s content loss).
- The piecewise-shift mapping is validated to sub-second accuracy on this
  episode, which means silver labels for the other JRE episodes can be
  produced from SponsorBlock + the stitch map alone, without downloading
  YouTube audio. The energy-envelope alignment remains useful as a check.

Implication for the benchmark: SponsorBlock is a usable silver source for
**host-read** reads on JRE and a useless one for inserted creatives; the two
channels must be scored separately, which is what the `delivery` field is for.
### Alignment results (3 episodes audio-aligned, 04:33–04:37 PDT; 2 more via header maps)

YouTube audio (`yt-dlp -f bestaudio -x --audio-format m4a`, ~2 min per episode, no bot check) for #2548, #2547, #2542; RSS copies from `fixtures-jre` (copy a, DAI-identical to copy b). `scripts/sb_align.py`, 100 ms resolution, lag search −120..+1000 s.

| Episode | Window | YT time | Offset (s) | NCC peak | Header-map offset (s) |
|---|---|---|---|---|---|
| #2548 Brian Simpson | first 5 min | 0–300 | 0.0 | 1.000 | 0.0 |
| | around sponsor 1134–1222 | 1028–1328 | 195.9 | 0.988 | 195.9 |
| | around sponsor 3317–3387 | 3202–3502 | 298.8 | 0.982 | 298.8 |
| | last 5 min | 9537–9837 | 629.3 | 0.911 | 629.3 |
| | 10-min profile | 600…9000 | 195.9 ×3, 298.8 ×3, 408.5 ×2, 531.0 ×3, 629.3 ×4 | 0.54–0.99 | identical |
| #2547 Daniel Everett | first 5 min | 0–300 | 0.0 | 1.000 | 0.0 |
| | around sponsor 1146–1205 | 1026–1326 | 171.0 | 0.952 | 171.0 |
| | around sponsor 3240–3308 | 3124–3424 | 275.1 | 0.997 | 275.1 |
| | last 5 min | 9169–9469 | 626.4 | 0.984 | 626.4 |
| | 10-min profile | 600…9000 | 171.0, 275.1, 394.8, 525.6, 626.4 plateaus; 2 windows straddling a splice not confident | | identical |
| #2542 Steve Hilton | first 5 min | 0–300 | 0.0 | 1.000 | 0.0 |
| | around sponsor 1146–1214 | 1030–1330 | 200.2 | 1.000 | 200.2 |
| | last 5 min | 10472–10772 | 644.3 | 0.906 | 644.3 |
| | 10-min profile | 600…10200 | 200.2, 309.6, 435.7, 527.2, 644.3 plateaus | 0.76–1.00 | identical (max |diff| 0.1 s) |

**Finding L4 — the key windows never agree; the offset is a staircase.** In all three episodes the first-5-min offset is 0 (the YouTube upload and the RSS programme start together — no RSS pre-roll before the cold open), the first sponsor window sits on the first plateau (171–200 s), the second on the next (275–299 s), and the last 5 minutes on the final plateau (626–644 s). Each step equals the summed duration of the Megaphone ads stitched at that point, and the independently computed NCC offsets match the `x-megaphone-payload-2` header map (`M-dai-check.md`) within **0.1 s** at every confident window (`header_check` in each `_silver.json`). The RSS "pre-roll" slot is not at 0 s: it is stitched ~415–545 s into the programme (after JRE's cold open), so even the first minutes are not safe for a "global offset" assumption beyond ~7 min.

**Finding L5 — two labelled layers, disjoint.** SponsorBlock labels only the two host-read sponsor blocks (in the programme, present on both platforms, ~40–90 s each at ~19 min and ~55 min). The 13 stitched ads per episode (~12.5 min: 3 "pre" at ~9 min, 4 pairs of mid-rolls at ~38, ~75, ~97, ~130 min, 2 post-rolls after the outro) are absent from YouTube and therefore unlabelled by SponsorBlock, but the Megaphone header gives their positions byte-exactly. For the RSS rendition, the reference set is the **union**: SponsorBlock host-read segments mapped through the staircase + Megaphone stitched slots. The two never overlap (the host reads sit inside plateaus).

Mapped host-read sponsor segments in RSS time (`confidence: high` = NCC-aligned; `medium` = header-derived, no audio check):

| Episode | Silver file | Sponsor segments (RSS s) | Confidence |
|---|---|---|---|
| #2548 Brian Simpson | `2026-09-01_1700_2548_Brian_Simpson_silver.json` | 1330.1–1417.5, 3615.8–3686.3 (+ 0–2.1 stub) | high |
| #2547 Daniel Everett | `2026-08-27_1700_2547_Daniel_Everett_silver.json` | 1317.0–1376.4, 3515.1–3583.0 (+ 0–2.2 stub) | high |
| #2542 Steve Hilton | `2026-08-19_1700_2542_Steve_Hilton_silver.json` | 1345.7–1414.0 (only one labelled) | high |
| #2540 Travis Barker | `2026-08-14_1700_2540_Travis_Barker_silver.json` | 1351.2–1407.8, 3427.1–3474.4 | medium (header) |
| JRE MMA #184 | `2026-08-11_1700_JRE_MMA_Show_184_with_Aljamain_Sterling_silver.json` | 1274.9–1347.4, 3456.3–3503.6 | medium (header) |

Each silver file also carries `megaphone_ads_rss_time` (the 13 stitched slots) so the orchestrator can score both layers.

## Answers

**(a) Fraction of recent JRE episodes with a YouTube mirror and SponsorBlock coverage: 15/15 (100%).** Every JRE RSS item from the last 30 days (13 numbered episodes + 2 MMA Shows) has a full-length upload on PowerfulJRE, found as the first `ytsearch10` hit, and every one of those videos returns SponsorBlock segments (72 in total). Coverage is broad but thin: 71 of 72 segments have votes < 2 and none is locked, so by the brief's tiers there is no gold and one silver segment; the usable set is single-submitter "bronze".

**(b) Sponsor segments per episode and their length.** 33 `sponsor` segments over 15 episodes: 2.2 per episode, but after dropping the four ≤3 s stubs it is **2 real host-read blocks per episode** (one episode, #2542, has only one labelled), each **39–90 s** (median ≈ 62 s), **68–160 s per episode** (mean 124 s ≈ 2.1 min) in a 2.4–4.5 h show. They sit at remarkably fixed positions in the YouTube cut: ~1075–1220 s (18–20 min) and ~2860–3450 s (48–57 min). The RSS rendition adds 13 Megaphone-stitched ads (~12.5 min, 737–799 s) that SponsorBlock does not see.

**(c) Are RSS and YouTube the same cut? No — same programme, different rendition.** Audio alignment on three episodes shows offset 0 for the first ~7 minutes, then a staircase of five plateaus (e.g. 0 → 195.9 → 298.8 → 408.5 → 531.0 → 629.3 s for #2548), each step equal to a Megaphone ad slot to within 0.1 s of the byte-exact header map. There is no cut/added programme material: outside the stitched ads the envelopes correlate at NCC 0.9–1.0, and the pre-roll slot is stitched after JRE's cold open, not at 0 s. The feed's `itunes:duration` is a declared value (YouTube + 359 s on all 15) and undercounts the delivered file by ~400 s. A single global offset would misplace the second sponsor block by ~100 s and the last-minute segments by ~630 s.

**(d) What a comparison of AdVTT spans needs** (see the draft list above, now confirmed): the per-segment `rss_segment` values from `data/sponsorblock/<stem>_silver.json` (five episodes: three `high`, two `medium`), the category map (`sponsor` → ad/sponsorship; `intro`/`outro` excluded), the Megaphone slot list in the same files as a second reference layer for the RSS-only ads, a ≥5 s minimum on reference segments, the project's 3 s detection tolerance, and rendition binding by sha256 to the aligned copy a. Score the two layers separately: SponsorBlock host-read blocks test whether AdVTT hears an in-programme read; Megaphone slots test whether it catches produced spots. Regions with no label in either layer are programme.

**(e) Licence.** SponsorBlock data is CC BY-NC-SA 4.0: evaluation and reporting only; never for training, fine-tuning, prompt tuning or threshold tuning; attribute SponsorBlock; keep it under `data/` (gitignored). The Megaphone header ad map is our own measurement and carries no such restriction.

**PDB.** The President's Daily Brief has its own YouTube channel with full episodes (`UCbWraa1DoXrFwX3oK1zattQ`) and SponsorBlock coverage (3 sponsor segments, 189 s, on the one video checked; RSS − YT = 24 s). Its RSS copies were DAI-identical, so a near-global offset is plausible there; not aligned in this pass.

## Failures and limits

- No YouTube bot-check occurred; no search or download failed (one spurious rename error on the third download, resolved on retry).
- Alignment was run on 3 of the 5 drawn episodes (download budget); #2540 and MMA #184 have header-derived offsets only (`confidence: medium`).
- The 10 undrawn episodes have YouTube ids and SponsorBlock segments but no RSS copy, so no RSS-time mapping.
- Vote-based silver/gold tiers are empty in practice; the labels are single-submitter and include four junk stubs ≤3 s and one probably missing second block (#2542).
- Whisper transcripts from `fixtures-jre` were not yet available for a text check of every mapped segment; two short slices of #2548 were transcribed directly (see the final section).


## Coordinator update applied (04:50 PDT) and final summary

Per the coordinator: no further YouTube downloads (three m4a files exist, none added), and the five fixture-episode silver files were **rewritten** to the agreed schema — `stem`, `video_id`, `method: "stitch-map-shift"`, `segments[{start,end,category,votes,locked}]` in RSS seconds (sponsor/selfpromo only; intro/outro kept separately in YouTube time under `sponsorblock_non_ad_segments_yt_time`), `segments_in_rss_time: true`, `offset_consistent: true` (no segment straddles a stitched break), `inserted_breaks_used` (the 7 breaks per episode with content position, creatives, inserted seconds and cumulative shift), and `cross_check` (the envelope alignment, where available). References above to `rss_segment`/`confidence` fields describe the superseded first version. `data/sponsorblock/summary.json` was refreshed to match.

Cross-check of the stitch-map shift against the envelope alignment (residual = NCC offset − stitch-map shift at each 5-min window centre):

| Episode | Windows | Confident | Max abs residual |
|---|---|---|---|
| #2548 Brian Simpson | 19 | 19 | 0.0 s |
| #2547 Daniel Everett | 19 | 17 | 0.0 s (the 2 non-confident windows straddle a break) |
| #2542 Steve Hilton | 20 | 20 | 0.1 s |

Text evidence (whisper-small on two RSS slices of #2548): the mapped SponsorBlock span 1330–1417 s is Rogan reading a DraftKings promo ("new DraftKings customers sign up with code Rogan…"), and the Megaphone pre-roll creative at 533.5–593.6 s is a *produced* DraftKings spot for the same campaign ("…the crown is yours. Event trading offered by DraftKings Predictions…"). Same advertiser, two delivery channels, only one of them visible to SponsorBlock.

### Summary table (all 15 JRE episodes in the 30-day window)

| Episode | RSS duration (s, feed) | YouTube id | YouTube (s) | SponsorBlock segments | Alignment result |
|---|---|---|---|---|---|
| #2537 - David Sinclair | 9037 | `hxid7FofhMw` | 8678 | 5 (2 sponsor, 91 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2538 - Joe DeRosa | 10047 | `pCH-R3L6QTc` | 9688 | 5 (2 sponsor, 120 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2539 - Protect Our Parks 17 | 16470 | `OBH4F5a6zAA` | 16111 | 3 (2 sponsor, 126 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2540 - Travis Barker | 9381 | `9iENvZ2siTo` | 9022 | 6 (2 sponsor, 104 s) | stitch-map-shift OK; no audio cross-check; RSS spans 1351–1408; 3427–3474 |
| #2541 - Thomas Campbell | 10382 | `v2oBLSDCZaY` | 10023 | 4 (2 sponsor, 137 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2542 - Steve Hilton | 11132 | `BYVQfLi6wMA` | 10773 | 3 (1 sponsor, 68 s) | stitch-map-shift OK; NCC residual ≤0.1 s (20 windows); RSS spans 1346–1414 |
| #2543 - MrBallen | 10937 | `fddF7pRu9Fs` | 10578 | 5 (2 sponsor, 150 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2544 - Chris Williamson | 10835 | `vh8FkZaQ06I` | 10476 | 4 (2 sponsor, 147 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2545 - Jesse Michels | 11349 | `33Fc_mLqY90` | 10990 | 4 (3 sponsor, 138 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2546 - Michael Button | 9468 | `rnt0wEc9YmI` | 9109 | 5 (2 sponsor, 140 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| #2547 - Daniel Everett | 9828 | `EmgKSK-YMOU` | 9469 | 6 (3 sponsor, 130 s) | stitch-map-shift OK; NCC residual ≤0.0 s (17 windows); RSS spans 1317–1376; 3515–3583 |
| #2548 - Brian Simpson | 10196 | `x04pr4QLl7o` | 9837 | 6 (3 sponsor, 160 s) | stitch-map-shift OK; NCC residual ≤0.0 s (19 windows); RSS spans 1330–1417; 3616–3686 |
| #2549 - Jared Diamond | 9254 | `t6Jrww8kG24` | 8895 | 6 (3 sponsor, 114 s) | not aligned (not in fixtures-jre draw; no RSS copy) |
| JRE MMA Show #184 with Aljamain Sterling | 10507 | `xEBeQH39CZI` | 10148 | 5 (2 sponsor, 120 s) | stitch-map-shift OK; no audio cross-check; RSS spans 1275–1347; 3456–3504 |
| JRE MMA Show #185 with Ethyn Ewing | 9756 | `efwqfxt717Q` | 9397 | 5 (2 sponsor, 111 s) | not aligned (not in fixtures-jre draw; no RSS copy) |

RSS durations are the feed's declared `itunes:duration`; delivered files for the five fixtures are 737–799 s longer than YouTube (see Correction to L1). The envelope-alignment tool is `scripts/sb_align.py`; YouTube audio (3 files, ~900 MB) is in `data/youtube/` and can be deleted once the orchestrator no longer needs it.
