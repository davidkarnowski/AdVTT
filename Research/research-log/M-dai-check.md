# M — Differential-download (dynamic ad insertion) check

Status: **done** (created 2026-09-06 04:18 PDT by agent `fixtures-jre`, finished 04:33 PDT). Downloads and DAI checks complete for both shows; JRE transcription was stopped by the coordinator (machine low on memory) and is pending.

## Question

When the same podcast enclosure URL is fetched twice, do the bytes differ? If
a host does dynamic ad insertion (DAI) at request time, two copies of "the
same" episode carry different ads, possibly different durations, and any
timestamped label set (ours, SponsorBlock's, a YouTube-derived one) is only
valid for the specific copy it was made against. This decides whether
fixtures can be identified by enclosure URL alone or must be pinned by
sha256, and whether YouTube versions of the same episode can be aligned by a
single offset.

## Method

`scripts/build_fixtures.py` downloads every selected enclosure twice
(copies `.a` and `.b`, independent `urllib` requests, User-Agent `AdVTT/0.1`,
no cookies), records the host the redirect chain ends at, and compares
sha256, byte size and `ffprobe` duration. When the copies differ it also
reports whether the first 64 KB differs (ID3 tag region), the ID3v2 tag
length of each copy, and whether the audio after the ID3v2 tag is
byte-identical. Copy `.b` is deleted when identical.

Shows tested 2026-09-06, seed 20260906, window = last 30 days:

| show | feed | episodes |
|---|---|---|
| PDB (The President's Daily Brief) | `feeds.megaphone.fm/THFD6217271651` | 5 |
| JRE (The Joe Rogan Experience) | `feeds.megaphone.fm/GLT1412515089` | 5 (excl. existing fixture #2537) |

## Redirect chains and delivery headers (probed 2026-09-06 11:19 UTC with a 1-byte Range request)

PDB enclosure `www.podtrac.com/pts/redirect.mp3/pdst.fm/e/mgln.ai/e/101/clrtpod.com/m/pscrb.fm/rss/p/arttrk.com/p/MG4HN/speakeasystudio.ai/m/<id>.mp3`:

    302 www.podtrac.com -> pdst.fm -> mgln.ai -> clrtpod.com -> pscrb.fm -> prefix-v4.pscrb.fm -> arttrk.com -> speakeasystudio.ai -> cdn-media.speakeasystudio.ai
    final: 206, server AmazonS3, stable ETag, Last-Modified set, no cache-control; URL is a plain object path + `?t=<ms>`

Eight measurement/attribution redirects (Podtrac, Podsights, Magellan, Claritas, Podscribe, Artsai) in front of a static S3 object. Nothing in that chain can rewrite audio; the host of record is a static file.

JRE enclosure `traffic.megaphone.fm/GLT3310404935.mp3`:

    302 traffic.megaphone.fm -> dcs-spotify.megaphone.fm
    final: 206, server envoy, no ETag, no Last-Modified, `cache-control: max-age=0, no-cache, no-store`;
    URL gains `?key=<hex>&request_event_id=<uuid>&session_id=<uuid>&timetoken=`

That is Megaphone's dynamic content service: a per-request session id and `no-store` are exactly what a stitching endpoint looks like. Whether it actually stitches different bytes per request is what the double download measures.

## Results

### PDB (agent `fixtures-pdb`, from `data/logs/fixtures-pdb.log`)

- Redirect chain: `traffic.megaphone.fm` -> ... -> `cdn-media.speakeasystudio.ai` (final host on every episode).
- All five PDB episodes: copy a and copy b byte-identical (sha256, size, ffprobe duration), fetched seconds apart, `AdVTT/0.1` UA. One transient `502 BAD_GATEWAY` on a copy-b fetch succeeded on retry 1.
- ffprobe duration matches the feed `itunes:duration` to within 1 s on all five (+0.0 .. +0.9 s), so the feed describes the delivered file and nothing is added at request time. Consistent with the delivery path: a static S3 object behind eight measurement redirects; the response has a stable ETag and Last-Modified.
- PDB ads are therefore baked into the master (host-read or producer-inserted at publish time), which is why every copy is identical and why the classifier has to find them from the transcript.

| episode | date | bytes | ffprobe s | itunes:duration | delta | verdict |
|---|---|---|---|---|---|---|
| PDB Situation Report Aug 8 | 2026-08-08 | 87,784,109 | 3643.0 | 1:00:43 | +0.0 | identical |
| Aug 18 morning | 2026-08-18 | 33,470,874 | 1382.2 | 0:23:02 | +0.2 | identical |
| Aug 19 morning | 2026-08-19 | 34,650,991 | 1418.9 | 0:23:38 | +0.9 | identical |
| PDB Situation Report Aug 22 | 2026-08-22 | 83,368,335 | 3459.2 | 0:57:39 | +0.2 | identical |
| PDB Afternoon Bulletin Aug 25 | 2026-08-25 | 19,943,253 | 819.1 | 0:13:39 | +0.1 | identical |

### JRE (agent `fixtures-jre`, from `data/logs/fixtures-jre.log`)

- Feed parse note: the megaphone JRE feed writes pubDate with `-0000`, which RFC 5322 defines as "no zone information"; `email.utils.parsedate_to_datetime` returns a naive datetime for it. Fixed in `build_fixtures.py` (treat naive as UTC) before the run; stems are now `YYYY-MM-DD_1700_...`.
- Draw (seed 20260906): #2548 Brian Simpson (2026-09-01), #2540 Travis Barker (08-14), #2547 Daniel Everett (08-27), JRE MMA Show #184 Aljamain Sterling (08-11), #2542 Steve Hilton (08-19).

| episode | date | host | copy a bytes | copy b bytes | size delta | duration a (ffprobe) | duration b | verdict | where | feed |
|---|---|---|---|---|---|---|---|---|---|---|
| JRE MMA Show #184 with Aljamain Sterling | 2026-08-11 | dcs-spotify.megaphone.fm | 152,454,436 | 152,454,436 | +0 | 10884.885 | 10884.885 | identical | - | itunes_duration=10507 |
| #2540 - Travis Barker | 2026-08-14 | dcs-spotify.megaphone.fm | 137,551,840 | 137,551,840 | +0 | 9820.369 | 9820.369 | identical | - | itunes_duration=9381 |
| #2542 - Steve Hilton | 2026-08-19 | dcs-spotify.megaphone.fm | 161,781,709 | 161,781,709 | +0 | 11551.138 | 11551.138 | identical | - | itunes_duration=11132 |
| #2547 - Daniel Everett | 2026-08-27 | dcs-spotify.megaphone.fm | 143,274,910 | 143,274,910 | +0 | 10229.655 | 10229.655 | identical | - | itunes_duration=9828 |
| #2548 - Brian Simpson | 2026-09-01 | dcs-spotify.megaphone.fm | 148,473,135 | 148,473,135 | +0 | 10600.777 | 10600.777 | identical | - | itunes_duration=10196 |

All five: sha256 identical, size delta 0, duration delta 0. Downloads were ~10 s apart, same IP, User-Agent `AdVTT/0.1`, no cookies. Run: `data/logs/fixtures-jre.log` (11:18-11:20 UTC, 0 failures, no retries needed).



### JRE: the identical pairs were a same-client artefact — Megaphone does stitch per client

Extra probes on #2548 (11:21-11:27 UTC, `data/logs/fixtures-jre.log` lines `PROBE` and `ADMAP`):

| copy | User-Agent | time | bytes | ffprobe duration | sha256 |
|---|---|---|---|---|---|
| a | `AdVTT/0.1` | 11:18 | 148,473,135 | 10600.777 | 14c8726c... |
| b | `AdVTT/0.1` | 11:18 (+9 s) | 148,473,135 | 10600.777 | = a |
| e | `AdVTT/0.1` | 11:22 | 148,473,135 | 10600.777 | = a |
| f | `AdVTT/0.1` | 11:24 | 148,473,135 | 10600.777 | = a |
| b' (phase-2 re-fetch) | `AdVTT/0.1` | 11:24 | 148,473,135 | 10600.777 | = a |
| c | `AppleCoreMedia/1.0.0 (iPhone ...)` | 11:22 | 148,440,952 | 10598.478 | a6c4689a... |
| d | same Apple UA | 11:22 (+14 s) | 148,440,952 | 10598.478 | = c |

- Same UA, same IP: byte-identical across at least 6 minutes and five fetches. The `?key=` in the final URL is stable per UA (`e354382d` for AdVTT, `e5323bbd` for Apple), `session_id` changes per request.
- Different UA: a different stitch. a vs c: -32,183 bytes, -2.30 s; ID3v2 tag identical (62,257 bytes both); first 64 KB identical; first differing byte at offset 7,530,880 = the start of the first stitched ad (7,530,875 per the header map below); the last 64.7 MB are identical (the post-roll region happened to get the same creatives).

**Megaphone publishes the stitch map in the response headers.** Every audio response from `dcs-spotify.megaphone.fm` carries `x-megaphone-payload-2`, a comma list of
`<ad_id>#<end_byte>#<pre|mid|post>#<slot_index>#<start_byte>#<campaign_id>#false#false`, terminated by `@<episode_guid>#<bitrate_bps>#<id3v2_bytes>` (JRE: 112000 bps CBR, ID3 60-67 KB). Bytes convert to seconds as `(byte - id3v2_bytes) / (bitrate/8)`. The decoded maps for the five fixture copies are in `data/fixtures/jre/<stem>.megaphone-ads.json` (raw headers kept), fetched with the same UA and verified sha256-identical to copy a.

| episode | ads (pre/mid/post) | stitched ad sec | file sec (ffprobe) | content sec = file - ads | feed itunes:duration | itunes - content |
|---|---|---|---|---|---|---|
| JRE MMA #184 Aljamain Sterling | 13 (3/8/2) | 737.9 | 10884.885 | 10147.0 | 10507 | 360.0 |
| #2540 Travis Barker | 13 (3/8/2) | 799.1 | 9820.369 | 9021.3 | 9381 | 359.7 |
| #2542 Steve Hilton | 13 (3/8/2) | 778.9 | 11551.138 | 10772.2 | 11132 | 359.8 |
| #2547 Daniel Everett | 13 (3/8/2) | 761.1 | 10229.655 | 9468.6 | 9828 | 359.4 |
| #2548 Brian Simpson | 13 (3/8/2) | 764.0 | 10600.777 | 9836.8 | 10196 | 359.2 |

Break layout is the same on every episode: three "pre" creatives back-to-back at ~7-9 min (after the cold open), four mid breaks of two creatives each (~38-40 min, ~75-77 min, ~96-98 min, ~130-135 min of file time), two "post" creatives that run to the last byte. Creatives are 33-78 s; total 12.3-13.3 min per 2.5-3 h episode (~7 %). 13 distinct ad_ids per copy.

`file - stitched ads = itunes:duration - 359 s` on all five (spread 0.8 s). The SponsorBlock agent measured "RSS minus YouTube duration = exactly 359 s on every episode" (`data/logs/sponsorblock.log`), so **YouTube = the ad-free master** and the served MP3 = master + 13 stitched creatives. The 359 s in the feed duration is a Megaphone constant (probably the configured ad allotment at publish time), not audio.

## Cross-check against the hand-labelled #2537 fixture

A 1-byte Range request for #2537 (David Sinclair, the existing PodcastFetch fixture, downloaded by PodcastFetch in August with a different client) also returns the stitch map. Fresh stitch (AdVTT UA, 2026-09-06): 13 creatives, 733.8 s, breaks at 544.7 (pre x3), 2229.6 (mid x2), 4421.3 (mid x2), 5803.0 (mid x2), 7860.5 (mid x2), 9275.8 (post x2, to end of file ~9411 s). The truth file (`tests/fixtures/jre/2026-08-07_1700_2537_David_Sinclair_ads.truth.json`, 8 spans, file length 9382.2 s) has:

| truth span (old copy) | fresh stitch break | note |
|---|---|---|
| 544.7 - 703.0 midroll | pre 544.7 - 740.6 | start identical to 0.1 s; the old copy had 37.6 s less creative in this break |
| 1262.6 - 1305.6 midroll | none | **host-read ad baked into the master** |
| 2192.5 - 2279.9 midroll | mid 2229.6 - 2338.0 | old start = fresh start - 37.1 s, i.e. the accumulated difference |
| 3400.0 - 3446.8 midroll | none | **host-read ad baked into the master** |
| 4363.7 - 4494.1 | mid 4421.3 - 4555.5 | shifted by accumulated difference |
| 5741.6 - 5839.1 | mid 5803.0 - 5870.7 | |
| 7829.7 - 7926.3 | mid 7860.5 - 7952.3 | |
| 9250.0 - 9382.2 postroll | post 9275.8 - 9411 | runs to the end of the file in both |

The byte-to-time conversion of the header is exact (0.1 s at the first break), the six stitched breaks are at the same *content* positions across copies, and the header knows nothing about the two host-read spans (~90 s per episode) that the label set also contains.

## Implications

1. **A JRE fixture is a specific stitch, not an episode.** Two clients (or one client after the stitch key rotates) get different bytes, different durations and different ad creatives at the same content positions. The manifest must pin sha256 + byte size + the `x-megaphone-payload-2` header of the copy that was transcribed (done: `data/fixtures/jre/<stem>.megaphone-ads.json`, and `downloads[].sha256` in `tests/fixtures/manifest.json`). Re-downloading "the same episode" later will not reproduce the transcript or the labels; keep copy a.
2. **Same-client fetches are stable for at least ~11 minutes** (five fetches 11:18-11:29 UTC, identical), so a double download from one client is *not* a DAI test on Megaphone; the script's DAI check needs a second User-Agent to be meaningful. Recommended change to `build_fixtures.py`: fetch copy b with a different UA (e.g. an Apple Podcasts string), and record the `x-megaphone-payload*` headers for both copies. Until then, the "identical" verdicts for JRE in `manifest.json` mean "stable stitch for this client", nothing more.
3. **The header is a free, exact ground truth for the stitched portion of JRE ads** (13 creatives, ~12-13 min per episode, 7 breaks). It can (a) seed the truth files for the five new JRE fixtures without listening, (b) score the classifier's ad-span recall on stitched breaks with byte precision, (c) reveal what the classifier is really being asked to do: the stitched creatives are third-party produced spots, while the ~2 host-read spans per episode are the hard case and are *not* in the header. Both kinds must remain in the truth.
4. **YouTube comparison.** The YouTube upload is the ad-free master (duration = file - stitched ads = itunes:duration - 359 s, on all five plus the SponsorBlock agent's 15/15). SponsorBlock segments on YouTube are therefore host-read/self-promo spans in content time; mapping them onto an RSS copy is a piecewise shift: `t_rss = t_yt + sum(duration of stitched creatives with start_sec < t_rss)`, computable directly from that copy's header map (no audio cross-correlation needed, though the SponsorBlock agent's envelope alignment should agree within its 100 ms grid). Conversely, YouTube-derived labels can never contain the stitched creatives, so a "silver" set from SponsorBlock alone under-labels JRE by ~13 min per episode.
5. **PDB needs none of this.** Static file, ads baked in, feed duration exact, so labels transfer across copies and the PDB YouTube channel (if the same cut) can be aligned with a single offset. Verify that assumption once per show rather than assuming either model.
6. The feed's `itunes:duration` is unreliable for Megaphone shows (declared master + a 359 s constant, ~400 s short of the delivered file); use ffprobe on the actual copy for any duration-based gate.
