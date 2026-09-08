# A — Prior art: products, apps and open-source projects that detect or skip ads in podcasts, radio and audio/video
Accessed: 2026-09-01

## Status
COMPLETE — 2026-09-01. 63 sources (S1–S63); 56 fetched from primary/raw sources, 7 marked snippet-only or partially fetched. WebSearch budget (200/200) was exhausted mid-run; the remainder was fetched with curl/GitHub API/Wayback. Documented gaps: TiVo SkipMode mechanics; Veritone and Barometer pages (JS-only, empty); live SponsorBlock wiki (Anubis) read via Wayback; kodi.wiki (Cloudflare) read via Wayback; id3.org (HTTP 500) replaced by mutagen source.

## Method note
Search queries run (WebSearch, first run): "github podcast ad detection open source whisper LLM remove ads"; "adblock radio Alexandre Storelli github machine learning"; "sponsorblock podcasts podcast version effort"; "SponsorBlock wiki segment categories actionType mute full poi chapter API docs"; "podcast app skip chapters auto-skip chapters Pocket Casts Overcast AntennaPod Podcast Addict"; "podcast app AI ad skipping feature 2025 2026"; "Podscribe Magellan AI Barometer podcast ad detection transcription methodology host-read"; "comskip EDL format commercial detection black frame silence logo accuracy"; "SponsorBlock database license CC BY-NC-SA mirror sb.ltn.fi dump"; "Podchaser Ad Intelligence podcast ad detection transcripts how it works"; "Veritonic Barometer ArtsAI podcast ad detection transcript machine learning brand"; "Overcast chapters Podcasting 2.0 JSON chapters support apps list Castamatic Podverse Fountain Podcast Guru"; "Snipd podcast app skip ads AI chapters feature"; "Dish Hopper AutoHop how it works commercial detection"; "mpv_sponsorblock lua script; Jellyfin SponsorBlock plugin; Kodi SponsorBlock addon"; "ffmetadata chapters format example"; "mplayer EDL file format 0 = skip 1 = mute"; "comskip .txt output format FILE PROCESSING COMPLETE edl edlp chp"; "yt-dlp info.json chapters sponsorblock_chapters _categories"; "Jellyfin media segments types Intro Outro Preview Recap Commercial"; "ajayyy SponsorBlock github issue podcast support"; "Pocket Casts deselect chapters skip chapter Overcast AntennaPod"; "Apple Podcasts chapters support Spotify chapters ID3 JSON 2024 2025"; "Barometer podcast brand suitability transcription AI"; "Chartable shutdown Spotify Ad Analytics"; "Veritonic audio ad detection competitive intelligence"; "radio ad monitoring audio fingerprinting Media Monitors Veritone"; "Plex skip intro credits detection how it works"; "Podcastindex podcast-namespace issue sponsor ad segments skip markers chapters proposal".
GitHub star/commit metadata below was pulled live from api.github.com on 2026-09-01.
The SponsorBlock wiki (wiki.sponsor.ajay.app) is behind an Anubis anti-bot challenge; its pages were read via the Wayback Machine (2025 snapshots) — noted per source.

## Sources

### S1. adblockradio/adblockradio (Alexandre Storelli) — https://github.com/adblockradio/adblockradio
- Type: repo
- Verified: fetched (README + GitHub API metadata)
- Key facts: "An adblocker for live radio streams and podcasts. Machine learning meets Shazam." Two engines: (a) time-frequency analyser — ~1 s PCM chunks at 22050 Hz mono classified by a neural net (Keras/TF or TensorFlow.js); (b) landmark audio-fingerprint matcher against a `hotlist.sqlite` of known ads/jingles/music. Output is JSON per time slice with `class` in {`0-ads`,`1-speech`,`2-music`,`3-jingles`,`9-unsure`}, raw + temporally-smoothed softmax arrays, hotlist match counts, gain dB. Example: `{"ml":{"class":"0-ads","softmax":[0.941,0.02,0.039]},"hotlist":{"class":"9-unsure","matches":1,"total":7},"class":"0-ads"}`. `predictor-file.js` handles podcasts/recordings with post-processing to ms-level boundaries. Licence MPL-2.0. 1,488 stars, 63 forks; created 2018-07-09; **archived 2021-04-10** (read-only). No accuracy figures in README (search snippets attribute training data of "66 hours of ads, 96 of talk and 73 of music" as of Nov 2018 to press coverage — snippet-only).
- Relevance to AdVTT: The only mature acoustic (non-transcript) approach; designed for produced radio spots and jingles, not host-read reads. Its 3-class + `unsure` output with smoothed softmax is a useful precedent for emitting per-window confidence. Dead since 2021.

### S2. ttlequals0/minuspod (MinusPod) — https://github.com/ttlequals0/minuspod
- Type: repo
- Verified: fetched (README, docs index, GitHub API)
- Key facts: "self-hosted server that removes ads before you ever hit play." Whisper (faster-whisper local, whisper.cpp, Groq, OpenVINO, OpenAI-compatible) → "First-pass LLM detection over sliding windows, plus an automatic verification pass on the re-cut audio." Audio-side signals: loudness analysis, DAI-transition detection, pre/post-roll identification, VAD-gap detection. "Cross-episode pattern learning from your corrections, scoped podcast to network to global"; opt-in community pattern sync ("one-PR submission back"). "Confidence scoring with a review queue; rejected detections stay visible for auditing." Emits re-cut audio (ads removed or beep-replaced), rewritten RSS with regenerated Podcasting 2.0 transcripts and chapters and AI-content disclosure tags. LLMs: Claude, OpenRouter, Ollama, any OpenAI-compatible. Has `benchmarks/llm/results/report.md` ("Per-model F1, JSON compliance, latency, and cost"). MIT. 379 stars, 32 forks; created 2025-11-26; last push 2026-09-01 (very active; 1,342 commits).
- Relevance to AdVTT: Closest living competitor in architecture (Whisper → windowed LLM → verification → confidence/review). Differences: MinusPod *cuts* audio and republishes feeds; AdVTT emits metadata. Its verification-pass-on-recut-audio and cross-episode sponsor-pattern cache are ideas AdVTT lacks. Its per-model F1 benchmark is a direct comparable for AdVTT's fixtures.

### S3. jdcb4/podcast-ad-remover (AGPAR) — https://github.com/jdcb4/podcast-ad-remover
- Type: repo
- Verified: fetched
- Key facts: Self-hosted Docker app; downloads episodes, transcribes with Whisper/faster-whisper, LLM ad detection via Gemini/OpenAI/Anthropic/OpenRouter, FFmpeg cuts, publishes replacement RSS (per-podcast + unified); optional AI summaries/TTS intros. No accuracy claims, no review UI or confidence threshold documented. MIT. 28 stars, 9 forks; created 2025-12-20; pushed 2026-08-11.
- Relevance to AdVTT: Another cut-and-refeed design; confirms the pattern that hobby projects output modified audio, not portable time-range metadata.

### S4. hemant6488/podcast-server — https://github.com/hemant6488/podcast-server
- Type: repo
- Verified: fetched
- Key facts: "Self-hosted podcast proxy that strips out ads before they hit your ears." Whisper transcription with timestamps → Claude API identifies ad segments → FFmpeg removes and inserts audio markers; Flask proxy serves modified RSS. No accuracy statements or safeguards; "for personal use only" disclaimer. CPU-only processing is slower than real time. MIT. 189 stars, 6 forks; created 2025-11-25; pushed 2026-08-20.
- Relevance to AdVTT: Same design family as S2/S3; no metadata output.

### S5. nocdn/ad-segment-trimmer — https://github.com/nocdn/ad-segment-trimmer
- Type: repo
- Verified: GitHub API only (README snippet-only)
- Key facts: "removes ads from audio/video with openai whisper and llms, self-hostable as an api". MIT. 9 stars; created 2024-08-21; pushed 2026-03-26. Search snippet: Whisper word-level timestamps → gpt-4o identifies ad segments → pydub removes them.
- Relevance to AdVTT: Confirms the Whisper→LLM→cut recipe predates 2025.

### S6. mebezac/Podcast-AdBlock — https://github.com/mebezac/Podcast-AdBlock ; Kayetic/podcast-ad-trimmer — https://github.com/Kayetic/podcast-ad-trimmer
- Type: repo
- Verified: GitHub API (Podcast-AdBlock: 0 stars, MIT, created 2026-01-31); Kayetic repo returned no metadata (404/renamed) — snippet-only
- Key facts: Both described as Whisper + LLM ad removal. Negligible adoption.
- Relevance to AdVTT: Long tail; nothing to borrow.

### S7. adamc199/podcast-ad-cleaner — https://github.com/adamc199/podcast-ad-cleaner
- Type: repo
- Verified: fetched (README)
- Key facts: CLI; Whisper transcription + Ollama llama3.2:3b scanning ~5-minute transcript chunks for "sponsor reads," "product promotions," "calls to action". Outputs MP3 with ID3 chapter embedding (visible in Apple Podcasts/Overcast), WebVTT transcript, and Podcasting 2.0 JSON chapters; chapters "auto-generated from topic changes". Self-assessed: "Very good for clearly marked ads and obvious sponsor reads", "may miss subtle product placements or conversational ads." MIT. 6 stars; created 2026-03-20.
- Relevance to AdVTT: One of very few OSS tools that emit *chapters* (ID3 CHAP + JSON) rather than only cutting — evidence that chapter formats are the de-facto interchange for podcast time ranges.

### S8. ericmedina024/podcast-sponsor-block — https://github.com/ericmedina024/podcast-sponsor-block
- Type: repo
- Verified: fetched
- Key facts: "SponsorBlock integration for podcasts": for podcasts that are also on YouTube, it downloads the YouTube audio "with the configured SponsorBlock segments removed" and serves a generated RSS. Documented limitations: "Finding the YouTube video that corresponds to a podcast episode can be unreliable" and "Podcast audio can differ between platforms which would cause the SponsorBlock offsets to be inaccurate". MIT. 101 stars; created 2024-01-30; last push 2024-04-06 (stale).
- Relevance to AdVTT: Demonstrates why crowdsourced offsets don't transfer across podcast copies — timestamps must be anchored to *this* file's audio (or to transcript text), which is AdVTT's evidence-quote approach.

### S9. Hacker News: "Need someone to create a platform agnostic sponsorblock for any podcast app" — https://news.ycombinator.com/item?id=39289665
- Type: forum
- Verified: fetched (via hn.algolia.com API; HN itself returned 429)
- Key facts: Top reply (WesleyLivesay): "most podcast ads these days are dynamically inserted at time of stream/download… some listeners get them and some listeners don't", "dynamic based on geographic location… drastically different ad loads". OP points to S8.
- Relevance to AdVTT: Restates the core reason a shared timestamp DB fails for podcasts; per-file analysis (AdVTT's model) is the only general solution.

### S10. SponsorBlock extension repo — https://github.com/ajayyy/SponsorBlock
- Type: repo
- Verified: fetched
- Key facts: Code GPL-3.0-or-later. 13,725 stars; created 2019-07-10; pushed 2026-09-01. Lists ports/integrations: mpv, Kodi, Chromecast, iOS, NeuralBlock. Database download at https://sponsor.ajay.app/database.
- Relevance to AdVTT: The reference crowdsourced-segment ecosystem; its category vocabulary is the most widely deployed segment taxonomy in existence.

### S11. SponsorBlock Database and API License — https://github.com/ajayyy/SponsorBlock/wiki/Database-and-API-License (also on https://sponsor.ajay.app/database)
- Type: legal
- Verified: fetched (raw wiki markdown + database page)
- Key facts: "The API and database follow CC BY-NC-SA 4.0 unless you have explicit permission." Attribution template gist linked. Database page lists CSV tables: sponsorTimes, userNames, categoryVotes, lockCategories, warnings, vipUsers, unlistedVideos, videoInfo, ratings, titles, titleVotes, thumbnails, thumbnailTimestamps, thumbnailVotes, casualVotes, casualVoteTitles. "For bandwidth reasons, CSV downloads have been disabled. Please use the sb-mirror project." `database.json` reports dbVersion 46 (2026-09-01). Mirrors: sb.ltn.fi (30-min), mirror.sb.mchang.xyz (10-min), sb.minibomba.pro (90-min).
- Relevance to AdVTT: NC licence means SponsorBlock data cannot be bundled into a commercial product without permission; fine for research/eval. AdVTT should decide its own data licence explicitly (and consider CC BY-SA or ODbL for any shared label set).

### S12. SponsorBlock API Docs — https://wiki.sponsor.ajay.app/w/API_Docs
- Type: spec
- Verified: fetched via Wayback Machine 2025 snapshot (live page blocked by Anubis)
- Key facts: `GET /api/skipSegments?videoID=&categories=[]&actionTypes=[]&service=` → array of `{segment:[start,end] (float seconds), UUID, category, videoDuration (float, "0 when unknown. +- 1 second"), actionType, locked:int, votes:int, description ("title for chapters, empty string for other segments")}`. Privacy variant `GET /api/skipSegments/:sha256HashPrefix` (first 4–32 hex chars of sha256(videoID); "4 is recommended") returns `[{videoID, segments:[...]}]`. `POST /api/skipSegments` takes `startTime, endTime, category, actionType (default "skip"), userID (random 30-char local), userAgent ("[BOT] Name/Version" for bots), videoDuration, description`; "Automating submissions is not allowed." Votes: `type` 0 down / 1 up / 20 undo; category-change votes. `service` defaults 'YouTube'. Also /api/searchSegments, /api/segmentInfo, lockCategories, webhook + OpenAPI docs.
- Relevance to AdVTT: The data model AdVTT should be able to *export to* and *import from*: `[start,end]` float seconds + category + actionType + votes + UUID + videoDuration-as-staleness-check. The `videoDuration` field is the mechanism for detecting that a label set no longer matches the media — AdVTT should carry an equivalent (duration + audio hash).

### S13. SponsorBlock Guidelines / Segment Categories — https://wiki.sponsor.ajay.app/w/Guidelines (redirect target of /w/Segment_Categories)
- Type: spec
- Verified: fetched via Wayback Machine 2025 snapshot (page "last edited on 27 September 2025")
- Key facts: Category definitions — Sponsor: "Part of a video promoting a product or service not directly related to the creator. The creator will receive payment or compensation". Interaction Reminder: "Explicit reminders to like, subscribe or interact". Unpaid/Self Promotion: Self Promotion = "product or service that is directly related to the creator themselves… merchandise or… monetized platforms"; Unpaid Promotion = "creator will not receive any payment… charity drives or free shout outs". Intermission/Intro Animation; Highlight (poi, "only one highlight per video"); Endcards/Credits (Outro); Preview/Recap; Hook/Greetings; Tangents/Jokes (filler, includes "Fake Sponsors"); Music: Non-Music Section; Exclusive Access (full-video label only); Chapter. Category *types*: skip (default), Mute ("visually contain important information but have audio underneath that belongs in one of the categories"), Full Video Labels (Sponsor, Exclusive Access, Unpaid/Self Promo). Boundary rules: "Include segues when possible"; "Segments should start before the visual change, or a little earlier if needed for audio"; "Segments at the start should start at 00:00.0 and segments at the end should go to the very end". "Don't make segments covering the entire video" — use a Full Video Label instead.
- Relevance to AdVTT: (1) The sponsor / selfpromo / interaction three-way split maps directly onto AdVTT's ADVERTISEMENT / PROMOTION(house) / (interaction) needs and is already understood by users of yt-dlp, mpv, Kodi, Jellyfin. (2) "Full video label" is a precedent for AdVTT's episode-level over-label gate: when >35% is ad, emit a whole-episode label rather than spans. (3) Boundary guidance ("include segues", "start a little earlier for audio") is a crowd-validated rule AdVTT's edge-refinement could adopt.

### S14. yt-dlp SponsorBlock options — https://github.com/yt-dlp/yt-dlp#sponsorblock-options and postprocessor source https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/postprocessor/sponsorblock.py
- Type: spec/repo
- Verified: fetched (README section + raw source)
- Key facts: `--sponsorblock-mark CATS` creates chapters for categories "sponsor, intro, outro, selfpromo, preview, filler, interaction, music_offtopic, hook, poi_highlight, chapter, all and default (=all)"; `--sponsorblock-remove CATS` cuts them (default "all,-filler"; poi_highlight/chapter not removable); `--sponsorblock-chapter-title` default `"[SponsorBlock]: %(category_names)l"` with fields start_time, end_time, category, categories, name, category_names; `--sponsorblock-api` default https://sponsor.ajay.app; `--embed-chapters`, `--remove-chapters REGEX`, `--force-keyframes-at-cuts`. Source: queries `/api/skipSegments/{sha256[:4]}` with `actionTypes=["skip","poi","chapter"]`; drops segments whose `videoDuration` differs from actual by ≥1 s unless <5 s and <5% of segment length ("Some SponsorBlock segments are from a video of different duration"); snaps starts ≤1 s to 0 and ends within 1 s of duration to duration; POI made 1 s long. Friendly names: sponsor→"Sponsor", intro→"Intermission/Intro Animation", outro→"Endcards/Credits", selfpromo→"Unpaid/Self Promotion", preview→"Preview/Recap", filler→"Filler Tangent", interaction→"Interaction Reminder", music_offtopic→"Non-Music Section", hook→"Hook/Greetings". Each chapter dict: `{start_time, end_time, category, title, type (actionType), _categories}`; stored in `info['sponsorblock_chapters']`.
- Relevance to AdVTT: The most widely deployed "segments → chapters" bridge. If AdVTT can emit chapters titled e.g. `[AdVTT]: Sponsor` it slots into an existing user mental model and every chapter-aware player. yt-dlp's duration-tolerance and edge-snapping rules are directly reusable validation logic.

### S15. SponsorBlockServer schema — https://github.com/ajayyy/SponsorBlockServer (databases/_sponsorTimes.db.sql)
- Type: repo/spec
- Verified: fetched (raw SQL)
- Key facts: `sponsorTimes(videoID TEXT, startTime REAL, endTime REAL, votes INT, UUID TEXT UNIQUE, userID TEXT, timeSubmitted INT, views INT, category TEXT, shadowHidden INT)` (base schema; later migrations add actionType, service, videoDuration, locked, hidden, description, hashedVideoID). AGPL-3.0; 1,055 stars; pushed 2026-08-02.
- Relevance to AdVTT: Minimal persisted record = (media id, start, end, category, votes, UUID, submitter, time submitted). AdVTT's per-span record should be a superset (adds confidence, evidence, provenance).

### S16. SponsorBlock issue #994 "[Feature] Podcast Support" — https://github.com/ajayyy/SponsorBlock/issues/994 (dup of #515)
- Type: forum
- Verified: fetched (GitHub API)
- Key facts: Opened 2021-10-08, closed as duplicate 2021-10-14. Maintainer ajayyy: "I don't listen to podcasts myself so I don't really understand the ecosystem." Suggested gPodder integration.
- Relevance to AdVTT: No first-party SponsorBlock podcast effort exists; the door is open for a compatible vocabulary but nobody owns it.

### S17. AntennaPod issue #4159 "Introduce SponsorBlock to allow blocking/skipping audio ads" — https://github.com/AntennaPod/AntennaPod/issues/4159
- Type: forum
- Verified: fetched (GitHub API, 20 comments)
- Key facts: Opened 2020-05-16, still open, locked 2020-10-29 pending forum discussion. Maintainer tonytamsf: "I don't think we will run a web service"; later "adding the integration to Auto Skip ads would have a bad look for the app and is bad for the ecosystem at this moment." ajayyy (2020-06-17): "I'd be up for adding a 'service' column to the db to support more than YouTube." Ethical objections (Aypac): "podcast producers are really reliant on ad-revenue". keunes: "that moral choice is for the user to make."
- Relevance to AdVTT: Ecosystem politics are a real adoption barrier; open-source players explicitly declined auto-skip. Supports AdVTT's default-off, metadata-not-cut posture, and suggests framing (disclosure/navigation, "chapter" style) that players can adopt without reputational cost.

### S18. Spot SponsorBlock (Spotify podcasts) — https://github.com/Spot-SponsorBlock/Spot-SponsorBlock-Extension
- Type: repo
- Verified: fetched (README + API)
- Key facts: "open-source crowdsourced browser extension to skip sponsor segments in Spotify podcasts… also supports… intros, outros and self promotions." Backend is ajayyy's SponsorBlockServer (uses the `service` column). GPL-3.0; 79 stars; pushed 2026-08-10. Chrome/Firefox/Edge/Android.
- Relevance to AdVTT: The only live "SponsorBlock for podcasts" — works because Spotify serves one canonical stream per episode (no per-listener DAI variation in the web player), which is exactly the condition the open-RSS world lacks. Reuses SponsorBlock categories verbatim.

### S19. xenova/sponsorblock-ml — https://github.com/xenova/sponsorblock-ml
- Type: repo
- Verified: fetched
- Key facts: "Automatically detect in-video YouTube sponsorships, self/unpaid promotions, and interaction reminders" from transcripts; T5-based segment extractor + classifier trained on SponsorBlock labels (used under CC BY-NC-SA 4.0). HuggingFace Spaces demo. No headline metrics in README. GPL-3.0; 172 stars; last push 2023-11-27.
- Relevance to AdVTT: Prior art for transcript-only ML classification into exactly the 3 SponsorBlock ad-like categories; stale.

### S20. andrewzlee/NeuralBlock — https://github.com/andrewzlee/NeuralBlock
- Type: repo
- Verified: fetched (README)
- Key facts: Keras BiLSTM over YouTube transcripts, labels from SponsorBlock timestamps (DB as of 2020-03-03); top-10k sponsorship vocabulary tokenizer. Noted label noise: "we don't know the moment a word is spoken, only an approximate time." 252 stars; last push 2023-10-04; no licence.
- Relevance to AdVTT: Early evidence that word-timing precision is the limiting factor for training from crowd labels — AdVTT's word-timestamp edge refinement addresses exactly this.

### S21. heidonomm/AdDetection (Snackable.ai) — https://github.com/heidonomm/AdDetection
- Type: repo
- Verified: fetched
- Key facts: Podcast-transcript ad detection with GloVe-25 embeddings + logistic regression / Naive Bayes; reported precision ~63%, recall ~17%. 4 stars; 2021.
- Relevance to AdVTT: Baseline showing classic shallow NLP fails at host-read ads; LLM approaches (S2, S7) are a step change.

### S22. Podcasting 2.0 JSON Chapters spec — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/examples/chapters/jsonChapters.md
- Type: spec
- Verified: fetched
- Key facts: Version 1.2 (2021-04-15). Required: `version`, `chapters[]`; per chapter required `startTime` (float s); optional `endTime`, `title`, `img`, `url`, `toc` (bool), `location`. `toc:false` → "this chapter should not display visibly to the user in either the table of contents or as a jump-to point". Example: `{"version":"1.2.0","chapters":[{"startTime":0,"title":"Intro"},{"startTime":168,"title":"Hearing Aids","img":"…"}]}`. No ad/skip semantics defined.
- Relevance to AdVTT: The native podcast time-range format. `endTime` is optional (chapters are usually open-ended), and there is no `type` field — AdVTT would need a title convention or a sidecar to carry category/confidence. `toc:false` allows hidden machine-only chapters.

### S23. Podcasting 2.0 namespace proposals — <podcast:disclosure> discussion #669 https://github.com/Podcastindex-org/podcast-namespace/discussions/669 ; <podcast:dynamic-ads-adjusted> issue #254 https://github.com/Podcastindex-org/podcast-namespace/issues/254 ; chapter extension #400/#469
- Type: spec (proposals)
- Verified: snippet-only (WebFetch quota hit before fetch; to be fetched via API)
- Key facts (snippets): #669 proposes a disclosure tag for affiliates, AI, sponsorships, "sponsored segments"; #254 addresses "varying-length dynamic ads inserted into the stream can affect the accuracy of… timestamps, such as transcripts, chapters, and soundbites"; #400/#469 propose chapter text blocks for disclosures/promo codes.
- Relevance to AdVTT: The namespace community already recognises (a) DAI breaks timestamped metadata and (b) sponsorship disclosure needs a tag. No adopted tag exists for ad time ranges — a gap AdVTT could fill by proposing one.

### S24. Podnews: Spotify tests "Skip ahead" for podcast ads — https://podnews.net/update/spotify-skip-ahead
- Type: blog (trade press)
- Verified: fetched
- Key facts: 2026-08-04. Spotify testing a "Skip ahead" button "in podcast ads and sponsorship messages", including host-read ("creators talking about their Patreon-style premium subscriptions") and Spotify-sold ads. Method of detection not stated. Industry reaction: concern, "whether blocking Spotify's own sold ads constitutes fraudulent behavior".
- Relevance to AdVTT: The largest platform is now shipping in-player ad-boundary detection (presumably transcript-based) — validates the product category and the "offer a skip, don't auto-cut" UX.

### S25. Podnews: "Another app promises to cut out the ads" (Podtastic) — https://podnews.net/update/skipping-ad-player
- Type: blog
- Verified: fetched
- Key facts: 2026-07-22. Podtastic (Freewheel Group Ltd), $2.99/mo, "automatically skip past the interruptions other listeners skip" (crowd/behavioural signal); downloads appear as Safari in logs. Also notes PodcastAdBlock (Ben Bowler) which "removed ads… and sold ad-free copies", "pulled down by May 2026".
- Relevance to AdVTT: (1) Behavioural crowdsourcing (skip telemetry) is a third detection signal besides acoustic and transcript. (2) Redistributing edited audio got a product taken down — reinforces AdVTT's metadata-only stance.

### S26. Herd: Ad-Free Podcast App (App Store) — https://apps.apple.com/us/app/herd-ad-free-podcast-app/id6670315567
- Type: product
- Verified: fetched
- Key facts: "Host-read ads," "Dynamically inserted ads," "External advertisement segments"; "automatically analyzes podcast episodes and identifies advertisements while you listen". Developer Bryce Altman; v2.0.14, updated 2024-08-18; $2.99/wk, $7.99/mo, $44.99/yr. Reviews report detection failures attributed by dev to "third-party outages" (implies cloud processing).
- Relevance to AdVTT: Commercial proof of demand; no methodology or accuracy published.

### S27. Skipper: Auto Skip Podcast Ads (App Store) — https://apps.apple.com/us/app/skipper-auto-skip-podcast-ads/id6757127240
- Type: product
- Verified: fetched
- Key facts: "Skipper detects sponsor segments on-device and converts them into Sponsor Cards" showing "brand, promo code, and offer"; "all detection and extraction happens on your device. No login, no tracking, no cloud processing." Free for 2 podcasts; Pro $9.99 one-time. v1.5.7 (July [2026]) "New and improved ad detection model". Dev: Pineridge Ranch Technologies. "Skipper isn't 100% accurate, nor is it ever claimed to be."
- Relevance to AdVTT: Closest UX analogue to AdVTT's `advertiser label` — extracting brand/promo code/offer per segment into a card. On-device model shows feasibility; still no published metrics.

### S28. ZeroAds blog: "Is There a Podcast App That Skips Ads? (2026)" — https://zeroads.ai/blog/podcast-app-that-skips-ads/
- Type: blog (vendor)
- Verified: fetched
- Key facts: ZeroAds is server-side: analyses episode audio, removes ads, republishes a private RSS; "Catches about 97-98% of ad time" vs hand-labelled episodes (vendor claim, no methodology). Works with "47+ apps"; not Spotify/Amazon. Argues "podcast ads are stitched into the audio file itself through dynamic ad insertion", so app-level DBs can't work.
- Relevance to AdVTT: A vendor already quotes an *ad-time recall* metric — AdVTT's `ad_recall_sec` is the same shape; publishing content-loss alongside would differentiate.

### S29. podcastadblock.app: "Best Podcast Apps with Built-in Ad-Skip Features (2026)" — https://podcastadblock.app/best-podcast-apps-with-ad-skip-features-2026/
- Type: blog
- Verified: fetched
- Key facts: 2026-07-13 (upd. 07-24). Herd = on-device AI; SiriusXM Podcasts+ = ad-free feeds (~60 shows); ZeroAds = server-side; AntennaPod/Overcast/Pocket Casts = no detection, but accept custom RSS. Claims services report "90-97% accuracy on hand-labelled test sets as of 2026" with "occasional ad fragments or brief content loss (~1 in 20 episodes)".
- Relevance to AdVTT: Mainstream players have *no* ad detection; the gap is filled by feed-rewriting services. Reported error mode ("brief content loss") is precisely AdVTT's asymmetry concern.

### S30. Snipd — Show HN thread https://news.ycombinator.com/item?id=30454639 (+ snippets from snipd.com)
- Type: forum/product
- Verified: fetched (Algolia API)
- Key facts: Co-founder KevinBenSmith: "decided against a dedicated feature doing exactly this… we do not want to hurt podcaster's ability to monetize", but "with the automatically generated chapters in our app, you do already get a good sense of where the ads are." Snippets: Snipd auto-generates AI chapters and can auto-skip intros/outros per show.
- Relevance to AdVTT: Second major AI podcast app that chose *chapters* as the socially acceptable way to expose ad boundaries. Strong signal for AdVTT to emit chapter-shaped output.

### S31. Pocket Casts Auto Skipping — https://support.pocketcasts.com/knowledge-base/auto-skipping/ ; Preselect Chapters — https://support.pocketcasts.com/knowledge-base/preselect-chapters/ (snippet)
- Type: product doc
- Verified: Auto Skipping fetched; Preselect Chapters snippet-only (to fetch)
- Key facts: Auto-skip = per-podcast "Skip First"/"Skip Last" seconds, free tier, synced. Preselect Chapters (Plus/Patron): "choose only the episode chapters you wish to play and skip the rest." No ad detection.
- Relevance to AdVTT: A chapter-deselect UI already exists in a top-3 app; ad chapters from AdVTT would be immediately actionable there.

### S32. AntennaPod chapter skip request — https://forum.antennapod.org/t/mark-individual-chapters-to-skip/7695 (snippet); AntennaPod auto-skip intro/outro (snippets)
- Type: forum
- Verified: snippet-only (to fetch)
- Key facts: Feature request to mark individual chapters to skip exists; AntennaPod supports chapters (ID3/Podlove/JSON) and skip-intro/outro seconds.
- Relevance to AdVTT: Same as S31 — chapter skipping is the requested primitive.

### S33. Apple Podcasts chapters (Podnews FAQ https://podnews.net/article/apple-chapters-faq ; james.cridland.net 2025; Castopod blog) — snippets
- Type: blog/product
- Verified: snippet-only (to fetch)
- Key facts: Apple Podcasts supports ID3 chapters, JSON Chapters (Podcasting 2.0 `podcast:chapters`), and timestamp lists in episode notes; iOS 26.2 adds auto-generated chapters and "timed links". Spotify reads feed chapters "titles only, no images or links" and auto-generates English chapters if absent.
- Relevance to AdVTT: All major players now read JSON chapters → chapters are the universal delivery vehicle for episode time ranges.

### S34. Comskip (erikkaashoek/Comskip; readme.txt; tuning.htm) — https://github.com/erikkaashoek/Comskip ; https://www.kaashoek.com/files/readme.txt ; https://kaashoek.com/files/tuning.htm
- Type: repo/product doc
- Verified: fetched (tuning.htm, readme.txt changelog; GitHub API)
- Key facts: "A free commercial detector", GPL-2.0, 704 stars, last push 2025-04-18. Signals: black frames, silence/volume, logo, scene change, aspect ratio, closed captions, cutscenes, combined by "a heuristics or Fuzzy Logic scoring process" (`detect_method` bitmask, e.g. 47). Outputs: `.txt` ("start and ending frame numbers"), `.csv` per-frame features, `.log`, `.logo.txt`; changelog shows `output_edl=1` (default "to ensure correct skipping in SageTV and NPVR"), `edl_skip_field` ("Set to edl_skip_field=3 to have better skipping on XBMC"), `edl_offset`, `output_edlp` (PTS-based for mencoder), `output_edlx`, `output_vdr` (VDR marks "used by XBMC to autoskip"), `output_chapters` (.chap frame list), `output_ipodchap` ("chapter marker before and after each commercial"), `output_scf` (mkvmerge simple chapters), videoredo/videoredo3 XML, `output_dvrmstb`, `output_bsplayer`, Avisynth, cuttermaran, mpeg2schnitt, ZoomPlayer chapters (seconds). `.txt` v2 header (per snippet): `FILE PROCESSING COMPLETE 678900 FRAMES AT 2500` then `startframe<TAB>endframe` pairs. Accuracy: "Comskip may not be able to deliver acceptable results on certain recordings… because the required information is simply not available in the broadcast." No numbers.
- Relevance to AdVTT: (1) Comskip solved interoperability by emitting *many* formats; EDL became the lingua franca for players. (2) Its approach of writing a chapter before and after each commercial is exactly the "ad as chapter" idea. (3) Frame-based formats are irrelevant for audio; second-based EDL and chapters are.

### S35. MythTV Commercial detection — https://wiki.mythtv.org/wiki/Commercial_detection
- Type: product doc
- Verified: fetched
- Key facts: Methods: Blank Frame; Blank Frame + Scene Change; Scene Change; Logo; "All" (blocks scored on "scene change frequency and logo presence"). "Strict Commercial Detection" option. No accuracy figures. Cutlist storage format not described on page.
- Relevance to AdVTT: Video-only signals; the transferable idea is block scoring with multiple weak signals (silence + loudness + music bed for audio).

### S36. Jellyfin intro-skipper — https://github.com/intro-skipper/intro-skipper
- Type: repo
- Verified: fetched
- Key facts: "Automatically detect and skip intro/credit sequences in Jellyfin"; Chromaprint audio fingerprints compared across episodes, plus silence and black-frame detection. GPL-3.0; 2,702 stars; pushed 2026-09-01. Disclaims liability for "missed detections, false positives". Requires Jellyfin 10.11.11+.
- Relevance to AdVTT: Cross-episode fingerprint matching finds *repeated* audio (produced spots, jingles, DAI creatives) with high precision — a cheap complementary signal for non-host-read ads across an AdVTT corpus.

### S37. Jellyfin Media Segments — https://jellyfin.org/docs/general/server/metadata/media-segments/ ; rrhett/EdlToMediaSegments https://github.com/rrhett/EdlToMediaSegments
- Type: spec/repo
- Verified: EdlToMediaSegments README fetched; Jellyfin doc snippet-only (to fetch)
- Key facts: Jellyfin 10.10 introduced typed media segments: Commercial, Preview, Recap, Outro, Intro; client actions None, Skip, PromptToSkip, Mute (snippet). "Unlike chapters, which have no type, media segments can contain type information." EdlToMediaSegments reads `Movie.edl` next to media, lines `start stop type` in seconds with type 0 Intro, 1 Preview, 2 Recap, 3 Commercial, 4 Outro; example `0 90 0` / `270.5 300 3`. GPL-3.0; 2025-09.
- Relevance to AdVTT: A second, independently designed typed-segment vocabulary (Intro/Preview/Recap/Commercial/Outro) with per-type action (Skip/PromptToSkip/Mute). AdVTT's kinds should map cleanly onto both SponsorBlock and Jellyfin enums; "PromptToSkip" is the exact default-safe behaviour AdVTT wants.

### S38. MPlayer EDL format — https://mplayerhq.hu/DOCS/HTML/en/edl.html
- Type: spec
- Verified: fetched
- Key facts: "[begin second] [end second] [action]", floats, action 0 = skip, 1 = mute. Example: `5.3 7.1 0` / `15 16.7 1` / `420 422 0`. `-edlout` writes a file from `i` keypresses during playback. Kodi extends actions (snippet: 2 scene marker, 3 commercial break) and also reads Comskip .txt/VideoReDo/BeyondTV; kodi.wiki page itself was Cloudflare-blocked.
- Relevance to AdVTT: Simplest possible interchange; AdVTT should offer an `.edl` exporter (action 3 for Kodi commercial-break semantics = "show skip button", action 0 = hard cut).

### S39. FFmpeg ffmetadata — https://ffmpeg.org/ffmpeg-formats.html#Metadata-2
- Type: spec
- Verified: fetched
- Key facts: Header `;FFMETADATA1`; `[CHAPTER]` sections with `TIMEBASE=1/1000`, `START=`, `END=`, `title=`; special chars `= ; # \` and newline escaped with backslash; example `[CHAPTER] TIMEBASE=1/1000 START=0 END=60000 title=chapter \#1`. Extract with `ffmpeg -i IN -f ffmetadata F`, reinsert with `-map_metadata 1 -codec copy`.
- Relevance to AdVTT: The write path into MP3/M4A chapter atoms/ID3 CHAP without extra libraries; note `END` is required per chapter (unlike JSON chapters).

### S40. Commercial vendors (snippet-level): Podscribe https://podscribe.com/llm-info (fetched) ; Magellan AI https://www.magellan.ai/products/competitive-intelligence (fetched) ; Barometer (snippets: adexchanger, radioink, podnews press) ; Veritonic https://www.veritonic.com/audio-ad-search/ (snippet) ; Podchaser transcripts (snippet) ; Chartable closure https://podnews.net/update/chartable-closes (snippet) ; Veritone attribution (snippet) ; AdMon Radio https://ivitec.com/admon-radio-advertisement-monitoring.html (snippet)
- Type: product
- Verified: mixed (as marked)
- Key facts: Podscribe: "Real-time Aircheck AI for transcript-based ad-read validation", "18 quality & brand-safety checks", NLP in Python/Rust microservices, "AI automation and human QA"; claims to share "error-rate statistics from its verification engine" but none on the page. Magellan AI: detects "programmatic, run of network, and host-read placements", shows "full searchable transcripts" and placement on a show timeline, "thousands of podcasts"; snippet: "captures all ads, whether host-read or pre-recorded, baked-in or dynamically inserted"; Nov 2024 added "promotional formats" (house/cross-promo) measurement. Barometer: AI transcribes episodes, scores GARM-style brand suitability; partnered with Spotify Ad Exchange, Acast, Libsyn, SiriusXM, Basis (2026-08). Veritonic: "Audio Ad Search" — full ad transcripts, voice gender, ad length, brand mentions, CTAs. Podchaser: human-in-the-loop transcripts, "sponsor detection and brand safety" for top 5,000 English podcasts. Chartable shut down 2024-12-12; SmartLinks/SmartPromos moved into Megaphone. Veritone: verifies pre-recorded spots by "audio fingerprint" vs playout log and "live reads through NLP-driven watchlists". AdMon Radio (ivitec) claims "up to 99.9% accuracy" for fingerprint-based spot detection (vendor claim).
- Relevance to AdVTT: The industry standard at scale is transcription + NLP/ML + human QA, classifying host-read vs produced and pre/mid/post position — same taxonomy AdVTT proposes. None publish precision/recall. Fingerprinting gets near-perfect results only for *known, repeated* creatives; host-read is handled by transcript NLP everywhere.

### S41. Kodi wiki: Edit decision list — https://kodi.wiki/view/Edit_decision_list
- Type: spec
- Verified: fetched (Wayback 2025 snapshot; live page Cloudflare-blocked)
- Key facts: Kodi reads, in order, `<name>.Vprj` (VideoReDo), `<name>.edl` (MPlayer EDL), `<name>.txt` (Comskip), `<name>.<ext>.chapters.xml` (BeyondTV). Extended EDL actions: `0 - Cut`, `1 - Mute`, `2 - Scene Marker`, `3 - Commercial Break`. Commercial Break semantics: "each commercial break is automatically skipped once during playback. Since commercial detection is rarely 100% accurate, commercial breaks that have already been skipped can be re-entered by seeking backwards". Scene markers are auto-placed at start/end of each commbreak. Times may be seconds, `HH:MM:SS.sss`, or `#frames`; 3-decimal precision. Comskip users must set `edl_skip_field=3` or Kodi treats entries as hard Cuts ("a 30 minute video would appear as 22 minutes"). Kodi v19+ ignores lines beginning `##` (comments). Example: `5.3 7.1 0` / `15 16.7 1` / `420 822 3` / `1 255.3 2` / `720.1 2`.
- Relevance to AdVTT: Kodi's action 3 is the exact "soft skip, recoverable" behaviour AdVTT's false-positive asymmetry calls for; an `.edl` exporter should default to action 3, never 0. `##` comment lines give a place for an AdVTT provenance header.

### S42. SponsorBlock Types (developer reference) — https://wiki.sponsor.ajay.app/w/Types
- Type: spec
- Verified: fetched (Wayback 2025 snapshot; page last edited 2025-08-14)
- Key facts: Categories: `sponsor selfpromo interaction intro outro preview hook filler`; POI: `poi_highlight` (start==end, poi actionType only); full-video only: `exclusive_access`; chapter only: `chapter`. Action types: `skip mute full poi chapter`; `full` "will always have start time and end time equal to 0, and means that the entire video is labelled as this category". Service: `YouTube` (Spot SponsorBlock adds Spotify via the same column, S18). "Warning: the filler category is very aggressive… strongly recommended to not use this in a client by default". Rating: 0 downvote, 1 upvote. Note `music_offtopic` appears in yt-dlp/API but not on this page's headline list.
- Relevance to AdVTT: Canonical machine token list to be compatible with. The `full` action with (0,0) is the precedent for an episode-level label. The filler warning is a precedent for shipping a low-precision category *off by default* — AdVTT could do likewise for "PROMOTION"/house reads.

### S43. Jellyfin docs: Media segments — https://jellyfin.org/docs/general/server/metadata/media-segments/
- Type: spec
- Verified: fetched
- Key facts: "first introduced in 10.10"; "Unlike chapters, which have no type, media segments can contain type information, allowing different actions based on the type". Segments "include a begin and end -Timestamp, followed by a type". Types: Commercial, Preview, Recap, Outro, Intro. Provided by plugins; official "Chapter Segments Provider plugin that creates media segments based on chapters and chapter-names" (i.e. chapter *titles* are parsed into typed segments). Clients set per-type actions (snippet: None / Skip / PromptToSkip / Mute).
- Relevance to AdVTT: Confirms a real-world path "chapter title → typed segment → per-type client action". If AdVTT writes chapters with recognisable titles (e.g. "Commercial"/"Sponsor"), Jellyfin's official plugin will already convert them into skippable segments — zero new consumer code.

### S44. MinusPod docs: How It Works & Detection Pipeline — https://github.com/ttlequals0/minuspod/blob/main/docs/how-it-works.md
- Type: repo (design doc)
- Verified: fetched (raw markdown)
- Key facts: Sliding windows "default 10 minutes" with "default 3 minutes" overlap ("a 60-minute episode is processed as 9 overlapping windows"), duplicates merged. Post-detection validation → ACCEPT / REVIEW / REJECT; "Rejected ads appear in a separate 'Rejected Detections' section". Confidence policy: ">=80% confidence: cut (configurable); 50-79%: kept for review". Position heuristics "Boosts confidence for typical ad positions (pre-roll, mid-roll, post-roll)". Verification pass = second LLM sweep "on the processed audio"; standalone misses held with reason `verification_miss` (floor 0.60). **Segment categories**: "Sponsor covers paid host-read or produced reads, dynamic ad insertion, and platform pre/post-rolls; cross-promo covers other-show and network promos; self-promo covers Patreon, merch, and subscribe/donate asks for the show itself; interaction covers follow/rate/review prompts. These four are always detected. Intro, outro, and recap… detected only when show-segments detection resolves to on"; per-category action map (remove / keep / beep). Audio side: EBU R128 loudness anomalies; "abrupt frame-to-frame loudness jumps that indicate dynamically inserted ad (DAI) boundaries"; MFCC "Audio Cue Templates" (learned ding/stinger) snap ad edges — "The cue never cuts on its own"; Chromaprint fingerprints identify DAI-inserted ads; TF-IDF/fuzzy text patterns at global/network/podcast scope. **Cross-Fetch Differential**: "MinusPod downloads the episode a second time with a different client signature and compares the two copies. Audio that differs between the fetches cannot be part of the show" (correlation ceiling default 0.60; candidates hold for review unless corroborated). Nearby-ad merge measured "in speech content from the transcript, not wall-clock time" (default 12 s). "Keep content only" mode has safety gates: content ≥55% of runtime, ≤45% removed, no cut >25% or 7 min. Chapters: keeps embedded chapters remapped onto cut audio, else LLM topic chapters ≥3 min apart; served as `podcast:chapters` JSON *and* embedded ID3 frames "for players like Castro that only read embedded chapters".
- Relevance to AdVTT: (1) Its category set (sponsor / cross-promo / self-promo / interaction / intro / outro / recap) is a podcast-native refinement of SponsorBlock's and is a strong candidate vocabulary for AdVTT. (2) Cross-fetch differential is a genuinely novel, transcript-free DAI detector AdVTT could adopt (PodcastFetch already downloads). (3) Its 55%/45%/25% episode-level safety gates parallel AdVTT's 35% over-label gate. (4) Speech-gap (not wall-clock) merging and cue-snapping are concrete boundary-refinement ideas. (5) Emitting both JSON chapters and ID3 CHAP is the observed compatibility requirement.

### S45. MinusPod LLM Benchmark Report — https://github.com/ttlequals0/minuspod/blob/main/benchmarks/llm/results/report.md
- Type: dataset/benchmark
- Verified: fetched (raw markdown)
- Key facts: Metric: F1/F0.5 "against the human-verified ground-truth ad spans… Uses IoU >= 0.5… after both sides are canonicalized to per-break spans"; 12 ad-bearing episodes + 2 verified no-ad negative-control episodes (16 windows; "PASS = zero predictions"); also cost/episode, p50/p95 latency, JSON compliance, F1 stdev, moderation-blocked %; 84 models; tiers by paired one-sided t-test (95%). Corpus transcripts by faster-whisper, "which sets an upper bound on what every benchmarked LLM can find." Headline (F0.5 @ IoU≥0.5, 95% CI ≈ ±0.10–0.13): `claude-haiku-4-5-20251001` 0.861 (P 0.848 / R 0.944 / F1 0.885, $1.08/ep); `qwen/qwen3.5-plus-02-15` 0.819; `google/gemini-3.5-flash-lite` 0.814 ($0.36/ep, 0.7 s p50); `claude-sonnet-4-6` 0.813; **`openai/gpt-5.5` 0.792 (P 0.783 / R 0.868) flagged "(!) brittle JSON (!) fails no-ad control", JSON compliance 0.87, $7.68/ep**; `claude-fable-5` 0.769 (R 0.928, $10.76/ep); `claude-opus-4-7` 0.758; `deepseek/deepseek-v3.2` P 0.861 / R 0.595; many cheap/open models "fails no-ad control". Best-tier precision tops out ≈0.85. Also reports mean absolute START/END boundary error per model.
- Relevance to AdVTT: The only public, per-model podcast-ad benchmark found. Directly challenges AdVTT's default of gpt-5.5 (false positives on no-ad episodes = the exact failure AdVTT's asymmetry forbids; Haiku 4.5 scores higher at 1/7 the cost). Its IoU≥0.5 span metric differs from AdVTT's `content_loss_sec`/`boundary_err_sec`; publishing both on the same fixtures would let the two projects be compared. Small CI (n=12) is a caveat.

### S46. MinusPod docs: Podcasting 2.0 handling + community pattern set — https://github.com/ttlequals0/minuspod/blob/main/docs/podcasting-2.0.md ; https://github.com/ttlequals0/minuspod/blob/main/patterns/README.md
- Type: repo (design doc / dataset)
- Verified: fetched (raw markdown)
- Key facts: Classifies every Podcast Namespace tag as Pass through / Regenerate / Strip / Always emit; timeline-bound tags (transcript, chapters, soundbite) are regenerated because "Passing these tags through would make the feed describe audio that no longer exists." Always emits `podcast:txt purpose="ai-content"` = true and `podcast:locked` yes for the private re-feed; passes `podcast:value*` through untouched ("MinusPod does not insert itself into the payment split"). Benchmark corpus: 14 episodes. Community patterns: one JSON file per sponsor (`sponsor`, `text_template`, `intro_variants`, `outro_variants`, genre `tags`), opt-in manifest sync, quality gates on submit, GitHub-Action validation.
- Relevance to AdVTT: (1) A worked example of which feed metadata becomes invalid once the *timeline* changes — for AdVTT (which does not cut) the inverse applies: its labels are valid only for the exact audio analysed. (2) The community sponsor-pattern JSON is the nearest thing to a shared podcast-ad label dataset; AdVTT could consume it as a prior or contribute to it. (3) `podcast:txt purpose="ai-content"` is an existing disclosure hook AdVTT-derived feeds could set.

### S47. Pocket Casts support: Preselect Chapters — https://support.pocketcasts.com/knowledge-base/preselect-chapters/
- Type: product doc
- Verified: fetched
- Key facts: "Plus/Patron feature that allows you to choose only the episode chapters you wish to play and skip the rest"; iOS, Android, Web, Desktop, Apple Watch, CarPlay (not Wear OS); selections sync across devices; "Chapter selection is not available for your custom user files."
- Relevance to AdVTT: The skip primitive exists in a top-tier app but only for *feed* chapters, not sideloaded files — so AdVTT output reaches Pocket Casts users only via feed chapters (JSON `podcast:chapters` or ID3 in the served MP3), which is exactly what PodcastFetch could inject.

### S48. AntennaPod forum: "Mark individual chapters to skip" — https://forum.antennapod.org/t/mark-individual-chapters-to-skip/7695
- Type: forum
- Verified: fetched (Discourse JSON)
- Key facts: 2025-11-13, AntennaPod 3.10.1, single post, no developer response as of fetch. Requests swipe-to-mark chapters to skip (use case: government press-conference podcast topics). Together with S17 (SponsorBlock request locked since 2020) AntennaPod has no chapter-skip or ad-skip.
- Relevance to AdVTT: Demand exists; the open-source Android player has neither primitive, so an AdVTT-aware player/plugin would be a first.

### S49. Podnews: "Apple Podcasts: automatic chapters FAQ" (James Cridland) — https://podnews.net/article/apple-chapters-faq
- Type: blog (trade press)
- Verified: fetched
- Key facts: Updated 2026-04-21 (first 2025-11-04). Since iOS/iPadOS 26.2 "almost every podcast now has chapters": Apple auto-generates chapters for episodes ≥10 min (not trailers), labelled as automatically created; creators opt out by supplying their own. Apple supports three formats: ID3 tags in MP3/AAC; "Episode Notes" timestamp lists (also read by Spotify); and JSON Chapters (Podcasting 2.0). "Chapters are also supported in Spotify (no chapter images though); in YouTube; and in many other apps".
- Relevance to AdVTT: Chapters are now universal on the biggest player and Apple itself runs an ML chapterer; an AdVTT-labelled ad chapter would render natively in Apple Podcasts, Spotify and YouTube without any client work.

### S50. Podcast Namespace issue #254 "Proposal: <podcast:dynamic-ads-adjusted>" — https://github.com/Podcastindex-org/podcast-namespace/issues/254
- Type: spec proposal
- Verified: fetched (GitHub API)
- Key facts: Opened 2021-05-26 (by a Facebook engineer), 30 comments, **closed 2026-03-04** without adoption. Problem: DAI "ads of varying lengths are inserted into the stream… any other data… that utilizes timestamps (ex. srt transcripts, chapters, soundbites, etc.) will be rendered inaccurate". Proposed `isAdjusted="true|false|not-applicable"`. Key line: "We considered having a tag to mark the insertion points and duration of the ads but feel like this can be abused by ad blockers so adoption by hosts would be limited."
- Relevance to AdVTT: The standards body explicitly rejected publishing ad time ranges in feeds for fear of ad blockers — so **no publisher-side ad-range tag will exist**; third-party per-file detection (AdVTT) is the only route. Also confirms timestamp metadata must be tied to a rendition.

### S51. Podcast Namespace tags: `podcast:chapters` and `podcast:transcript` — https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/chapters.md ; https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/tags/transcript.md
- Type: spec
- Verified: fetched (raw markdown)
- Key facts: `podcast:chapters url= type="application/json+chapters"` (single per item). Rationale: "chapters do not require altering audio files, and the chapters can be edited after publishing… can be displayed by a wider range of playback tools, including web browsers (which typically have no access to ID3 tags)"; "The data held is compatible with normal ID3 tags". `podcast:transcript url= type=` (multiple) with types `text/plain, text/html, text/vtt, application/json, application/x-subrip`; `rel="captions"` marks a closed-caption file where "time codes are assumed to be present".
- Relevance to AdVTT: (1) External JSON chapters are the sanctioned sidecar for time metadata — an AdVTT sidecar can reuse the same `podcast:chapters` slot rather than a new WebVTT track. (2) WebVTT *is* a recognised podcast transcript type, so an `.ads.vtt` is not alien to the ecosystem, but the namespace has no "metadata track" concept.

### S52. Inside Radio: "Magellan AI Adds Promotional Formats To Ad Measurement Offerings" — https://www.insideradio.com/free/magellan-ai-adds-promotional-formats-to-ad-measurement-offerings/article_79d199f6-a326-11ef-8838-478d8685d86b.html
- Type: product (trade press)
- Verified: fetched
- Key facts: 2024-11-15. Beyond "host-read ads and produced spots", Magellan now measures "sponsored interviews, branded podcasts, feed drops, and podcast cross-promotions… whether as standalone episodes or post-roll content" via "Special Episode Monitors". No methodology or accuracy stated.
- Relevance to AdVTT: The industry taxonomy of "kinds" is wider than ad/sponsor: cross-promo, feed drop, sponsored interview, branded episode. AdVTT's kind enum should at least reserve cross-promo and whole-episode-branded.

### S53. Podscribe: Podcast Ad Verification — https://podscribe.com/solutions/ad-verification/podcast-ad-verification
- Type: product
- Verified: fetched
- Key facts: "Track podcast ads in real time with 18-point verification and alerts"; error classes: "Wrong Placement", "Script & Length Errors ('Hosts veer off script')", "Audio Quality Issues", "Missed or Cut Ads"; "Time-stamped proof prevents make-goods". No public accuracy figures.
- Relevance to AdVTT: Vendors already produce time-stamped ad-read records with brand and script-compliance checks — the same primitive AdVTT emits, aimed at advertisers rather than listeners. Suggests a dual-use framing (verification/disclosure) that avoids the "ad blocker" stigma seen in S17/S50.

### S54. Podchaser: transcripts across 150k podcasts — https://www.podchaser.com/articles/announcements/podcast-transcripts-podchaser-provides-coverage-across-24k-podcasts
- Type: product (announcement)
- Verified: fetched
- Key facts: 2024-12-10. Transcribes top 150,000 US podcasts + top 500–1,000 in 9 other countries; "For the top 5,000 English-language podcasts, ongoing sponsor detection and brand safety analysis will continue"; newly added shows "do not include sponsorship… features". Also ingests RSS `podcast:transcript` files.
- Relevance to AdVTT: Sponsor detection at scale is a paid-data product on ~5,000 shows; nothing for the long tail or for listeners — AdVTT's niche.

### S55. Overcast podcaster info — https://overcast.fm/podcasterinfo
- Type: product doc
- Verified: fetched
- Key facts: "Overcast displays MP3 and M4A chapter markers with titles, images, and/or link URLs." (Embedded chapters only; no mention of JSON chapters or chapter skipping.)
- Relevance to AdVTT: For Overcast/Castro-class apps, ID3 CHAP / M4A chapter atoms embedded in the file are the only path — supports S44's "emit both JSON and embedded".

### S56. W3C WebVTT: The Web Video Text Tracks Format — https://www.w3.org/TR/webvtt1/
- Type: spec
- Verified: fetched (searched text)
- Key facts: Metadata cues: "Metadata can be any string and is often provided as a JSON construct"; WebVTT defines the metadata text track kind for HTML `<track kind="metadata">`. No chapter/metadata *vocabulary* is defined by the spec; chapters kind exists separately.
- Relevance to AdVTT: The preliminary design is spec-legal, but nothing in the podcast/player ecosystem surveyed (S1–S55) consumes a WebVTT metadata track for skipping; it is only useful inside AdVTT's own HTML player and browsers.

### S57. Podcast Namespace discussion #669 "Proposal: <podcast:disclosure> for affiliates, AI, sponsorships, etc." — https://github.com/Podcastindex-org/podcast-namespace/discussions/669
- Type: spec proposal
- Verified: fetched (HTML)
- Key facts: Proposes `<podcast:disclosure type="compensation|ai|association|license" context="links|content|ad|images|audio">` at item or channel level, e.g. `type="compensation" context="ad"` → "This episode contains paid ad placements." Motivation: legal disclosure (FTC-style compensation, AI). No time ranges. Reaction: "Tags with legal implications… really need to be driven by Apple+Spotify"; TrueFans already shows an "AI hosted" icon. Not adopted (discussion, 2024–).
- Relevance to AdVTT: The only namespace-level ad *disclosure* concept is episode-level and boolean. AdVTT could position its output as a machine-generated, time-resolved disclosure — complementary rather than adversarial — but there is no slot to publish it in a feed today.

### S58. Fluendo blog: "Advertisement detection in multimedia content with artificial intelligence" — https://fluendo.com/blog/ai-ad-detector/
- Type: product/blog
- Verified: fetched
- Key facts: Edge/offline pipeline: audio extraction → noise filtering → sliding-window segmentation → audio fingerprinting against "a stored database of known ads" → "Timestamp refinement & advertisement classification"; speech/music differentiation; "optimized for detecting explicitly structured advertisements". Has a "Detection accuracy by language" section but no numbers survived extraction (page is a marketing post).
- Relevance to AdVTT: Another fingerprint-first product that by design cannot catch novel host-read copy; corroborates the split — fingerprints for repeated creatives, transcript+LLM for host-read.

### S59. ZeroAds: "How to Remove Podcast Ads in 2026" — https://zeroads.ai/blog/2025-09-22-remove-podcast-ads-guide/
- Type: blog (vendor)
- Verified: fetched
- Key facts: "The service transcribes the entire audio file… Cuts ads automatically. In our accuracy tests against hand-labeled episodes, ZeroAds catches about 97-98% of ad time, about 85% of every second it cuts lands on labeled ad time, and every cut is listed with timestamps in an episode report". Credits **Podly**: "the open-source project this category owes a lot to. ZeroAds started as a fork of it… Free, self-hosted, bring your own server and LLM API keys… one-click Railway deploy".
- Relevance to AdVTT: First vendor to publish *both* a recall (97–98% of ad seconds) and a precision (~85% of cut seconds) figure — i.e. roughly 15% of removed audio is content, a content-loss rate far above AdVTT's ≤5 s gate. This is the number AdVTT should beat and publish against. Podly is a further OSS predecessor (S62).

### S60. Adblock Radio README — file-analysis output — https://github.com/adblockradio/adblockradio/blob/master/README.md
- Type: repo
- Verified: fetched (raw markdown)
- Key facts: For recordings/podcasts "An additional post-processing specific to recordings hides the uncertainties in predictions and shows big chunks for each class, with time stamps in milliseconds, making it ready for slicing." Output objects carry `tStart`/`tEnd` (ms) per prediction, `softmaxraw` and `softmax` smoothed with `slotsPast`=5 / `slotsFuture`=4 windows; `saveMetadata` writes a JSON of predictions.
- Relevance to AdVTT: Precedent for (a) ms-resolution `tStart/tEnd` chunks per class, (b) temporal smoothing of per-window probabilities before emitting spans — a technique AdVTT could apply to per-chunk LLM confidences.

### S61. Wikipedia: Commercial skipping — https://en.wikipedia.org/wiki/Commercial_skipping
- Type: encyclopedia (secondary)
- Verified: fetched
- Key facts: "The first DVR with a built-in commercial skipping feature was ReplayTV… In 2002, the main television networks and movie studios sued ReplayTV". (Dish AutoHop 2012 lawsuits and Fox settlement — 7-day delay for Fox — from search snippets only.) TiVo SkipMode: **not found** in fetched pages (Wikipedia TiVo articles and TiVo support page yielded no "SkipMode" text) — documented gap; snippets elsewhere describe it as human-tagged for selected primetime shows, unverified.
- Relevance to AdVTT: TV ad-skipping history is dominated by litigation against *distributors who cut or hide ads at scale* (ReplayTV, Dish) — another reason AdVTT should ship metadata and leave the skip decision to the user's own player.

### S62. podly-pure-podcasts/podly_pure_podcasts (Podly) — https://github.com/podly-pure-podcasts/podly_pure_podcasts
- Type: repo
- Verified: fetched (README + GitHub API)
- Key facts: "Ad-block for podcasts. Create an ad-free RSS feed." "Podly uses Whisper and Chat GPT to remove ads from podcasts." Flow: request episode → download → Whisper → "LLM labels ad segments" → remove → serve ad-free RSS. Cost table: $0 (all local) to $10/mo (Railway + remote STT/LLM); lists "$5.99/mo https://zeroads.ai/ production fork of podly". MIT; **520 stars** (largest OSS podcast ad remover found); created 2024-05-21; pushed 2026-07-25; Discord community; one-click Railway deploy.
- Relevance to AdVTT: The most-starred OSS project in this space and the ancestor of the only vendor publishing precision/recall (S59). Same cut-and-refeed model; no portable metadata output. Its cost table is a useful framing for AdVTT's local-vs-remote STT/LLM options.

### S63. ID3v2 Chapter Frame Addendum (CHAP/CTOC) as implemented in mutagen — https://github.com/quodlibet/mutagen/blob/main/mutagen/id3/_frames.py (spec: https://id3.org/id3v2-chapters-1.0, unreachable 2026-09-01 — HTTP 500 and Wayback landing page only)
- Type: spec (via reference implementation)
- Verified: fetched (mutagen source)
- Key facts: `CHAP` frame = `element_id` (Latin-1), `start_time` (uint32 ms), `end_time` (uint32 ms), `start_offset`/`end_offset` (uint32 bytes, default 0xFFFFFFFF = unused), `sub_frames` (embedded ID3 frames such as TIT2 title, WXXX url, APIC image). `CTOC` = `element_id`, `flags` (top-level / ordered), `child_element_ids[]`, `sub_frames`.
- Relevance to AdVTT: Embedded chapters are ms-resolution with *required* end times and can carry a URL sub-frame (WXXX) — a place to link an AdVTT provenance/analysis URL per ad chapter without inventing a new container. Millisecond integers ⇒ AdVTT should emit ms-rounded boundaries.


## Synthesis

**1. Nobody ships what AdVTT proposes: portable, typed, confidence-bearing ad time-range metadata for arbitrary podcast files.** Every open-source podcast ad tool of the 2024–26 wave — Podly (520★, S62), MinusPod (379★, S2/S44), podcast-server (189★, S4), AGPAR (S3), ad-segment-trimmer (S5), podcast-ad-cleaner (S7) — follows the same recipe: Whisper → windowed LLM → FFmpeg cut → rewritten private RSS. Only podcast-ad-cleaner (S7) and MinusPod (S44) also emit chapters; none emit a standalone segment file another player can consume. The commercial listener apps (Herd S26, Skipper S27, Podtastic S25, Castria/Hypercast/STFUAI snippets) are closed and skip in-player. Spotify is now testing an in-player "Skip ahead" button on ads (S24). So the *detection* problem is crowded; the *interchange* problem is open.

**2. MinusPod is the state of the art and a direct benchmark rival.** It has a 7-category vocabulary (sponsor / cross-promo / self-promo / interaction / intro / outro / recap), per-category actions (remove/keep/beep), 10-min windows with 3-min overlap, a verification pass on the re-cut audio, ACCEPT/REVIEW/REJECT gating at 0.80/0.50, speech-gap (not wall-clock) merging, EBU R128 loudness and DAI-transition detection, MFCC cue-template edge snapping, Chromaprint fingerprint reuse, cross-episode/community sponsor patterns, and a *cross-fetch differential* that downloads the episode twice to isolate DAI splices (S44). Its 14-episode LLM benchmark (12 ad-bearing + 2 no-ad controls; F0.5 @ IoU ≥ 0.5; 84 models) is the only public per-model podcast-ad benchmark found (S45). Notably `openai/gpt-5.5` scores F0.5 0.792 with flags "brittle JSON" and "fails no-ad control", behind `claude-haiku-4-5` (0.861, $1.08/ep) and `gemini-3.5-flash-lite` (0.814, $0.36/ep). Caveat: n=12, CI ±0.10–0.13.

**3. Published accuracy is nearly absent; where it exists, content loss is high.** ZeroAds (Podly's production fork) reports "97-98% of ad time" caught but only "about 85% of every second it cuts lands on labeled ad time" (S59) — i.e. ~15% of removed audio is programme. A review site quotes 90–97% with "brief content loss (~1 in 20 episodes)" (S29). Skipper says "isn't 100% accurate" (S27). Classic NLP baseline: 63% P / 17% R (S21). Commercial ad-intelligence vendors (Podscribe S40/S53, Magellan S40/S52, Barometer S40, Podchaser S54, Veritonic S40) describe transcription + ML + human QA and time-stamped proofs but publish no precision/recall. Fingerprint vendors (AdMon "up to 99.9%", Veritone, Fluendo S58) achieve high accuracy only for *known, repeated* creatives.

**4. Crowdsourced timestamp databases do not transfer to open podcasts.** DAI yields per-listener renditions (S9, S8, S50); SponsorBlock's maintainer closed the podcast request (S16), AntennaPod declined integration on ecosystem/ethics grounds (S17), and podcast-sponsor-block (S8) only works for YouTube-mirrored shows with documented offset drift. Spot SponsorBlock (S18) works only because Spotify's web player is one canonical stream. The Podcast Index namespace explicitly *rejected* a publisher-side ad-range tag "because this can be abused by ad blockers" (S50), and its disclosure proposal (S57) is episode-level and boolean. Per-file analysis bound to the exact rendition is therefore the only general architecture — and labels must carry a rendition identity (SponsorBlock's `videoDuration` staleness check, S12/S14, is the precedent).

**5. Two typed-segment vocabularies are already deployed in consumers; AdVTT's v0.1 is a third, incompatible one.** SponsorBlock: `sponsor selfpromo interaction intro outro preview hook filler music_offtopic poi_highlight exclusive_access chapter`, actionTypes `skip mute full poi chapter`, where `full` = (0,0) whole-video label and `filler` is shipped off-by-default because it is "very aggressive" (S12, S13, S42). Consumers: yt-dlp (S14), mpv (630★), Kodi (155★), Jellyfin plugins, Invidious. Jellyfin Media Segments: `Intro Preview Recap Commercial Outro` with client actions `None Skip PromptToSkip Mute`, fed by an official plugin that parses *chapter names* into typed segments (S37, S43). MinusPod's podcast-native set (S44) sits between them. AdVTT's ADVERTISEMENT / SPONSORSHIP / PROMOTION / PROGRAM distinguishes ad from sponsorship (which no other vocabulary does) but lacks selfpromo-vs-paid, interaction, cross-promo, intro/outro, and a whole-episode label.

**6. Chapters are the socially accepted, universally parsed carrier of episode time ranges.** Snipd refused an ad-skip feature but exposes ads through AI chapters (S30); Apple Podcasts (iOS 26.2) auto-generates chapters and reads ID3, JSON and show-notes chapters (S49); Spotify and YouTube read chapters (S49); Pocket Casts has chapter *deselection* (Preselect Chapters, S47); Overcast/Castro read embedded MP3/M4A chapters only (S55, S44); Podcasting 2.0 JSON chapters (`podcast:chapters`, S22/S51) are supported by Fountain, Podverse, Castamatic, Podcast Guru, Podcast Addict (snippets). Comskip's `output_ipodchap` ("chapter marker before and after each commercial", S34) and yt-dlp `--sponsorblock-mark` (S14) are prior "ads as chapters" bridges. The limitation: JSON chapters have no `type` field and optional `endTime` (S22); ID3 CHAP has required ms `end_time` and can embed a WXXX URL (S63).

**7. Format landscape for time ranges.** MPlayer EDL `start end action` in float seconds, 0 skip / 1 mute (S38); Kodi extends to 2 scene-marker / 3 commercial-break, where 3 = "automatically skipped once… can be re-entered by seeking backwards" and `##` comments are allowed (S41); Jellyfin EDL variant uses type codes 0 Intro … 3 Commercial, 4 Outro (S37); Comskip `.txt` frame pairs with `FILE PROCESSING COMPLETE N FRAMES AT fps*100` header plus ~15 other outputs (S34); ffmetadata `[CHAPTER] TIMEBASE=1/1000 START END title` (S39); SponsorBlock JSON `{segment:[s,e],category,actionType,UUID,votes,videoDuration,locked,description}` (S12); Adblock Radio per-class chunks with `tStart/tEnd` ms and smoothed softmax (S1, S60); Podcasting 2.0 JSON chapters (S22). **WebVTT `kind=metadata` is consumed by none of the surveyed tools** (S56) — it is legal and fine for AdVTT's own HTML player, but as the canonical interchange it would be an island.

**8. Acoustic signals are complementary, not competitive.** Adblock Radio's NN + landmark fingerprints (S1), intro-skipper's cross-episode Chromaprint (2,702★, S36), Plex's per-season audio histogram matching (snippet), Comskip/MythTV black-frame/silence/logo scoring (S34, S35) all find *repeated* or *structurally marked* material. For host-read copy in the host's voice, every serious system — MinusPod, Podly, Skipper, Podscribe, Magellan, Barometer, Veritone live-reads — uses transcript + NLP/LLM. MinusPod's loudness-jump and cross-fetch tricks are the useful audio-side additions for DAI.

**Contradictions / uncertainties.** Vendor accuracy claims (S28, S29, S59) are self-reported on unpublished sets. MinusPod's benchmark ranks are only meaningful across tiers (paired t-test) given n=12 (S45). Herd's 2024 last-update (S26) vs review-site claims of on-device processing (S29) conflict with developer replies blaming "third-party outages" (cloud). TiVo SkipMode mechanics could not be verified (S61).

## Implications for AdVTT

1. **Adopt an existing vocabulary as the interop layer instead of inventing v0.1 tokens.** Map: ADVERTISEMENT/SPONSORSHIP → `sponsor` (SponsorBlock S13/S42; Jellyfin `Commercial` S43); house/self reads → `selfpromo`; cross-show promos → MinusPod `cross-promo` (S44); rate/subscribe asks → `interaction`; keep `intro`/`outro`/`preview`(recap) as optional classes. Keep AdVTT's ad-vs-sponsorship distinction as a *sub-kind* attribute, not a top-level category, so exports to SponsorBlock/Jellyfin are lossless in the direction that matters. Ship low-precision classes (house reads, filler-like) off by default as SponsorBlock does with `filler` (S42).
2. **Make chapters the primary delivery format; keep WebVTT as one exporter.** Emit (a) Podcasting 2.0 JSON chapters with `endTime` set and `toc:false` machine chapters where appropriate (S22, S51); (b) embedded ID3 CHAP / M4A chapters via ffmetadata for Overcast/Castro-class apps (S39, S55, S63) with a WXXX URL to the analysis record; (c) chapter titles that Jellyfin's Chapter Segments Provider and yt-dlp users recognise (e.g. `[AdVTT] Sponsor: Squarespace`, cf. `[SponsorBlock]: Sponsor`, S14, S43). Evidence: S30, S47, S49 show players and even ad-averse vendors treat ad chapters as acceptable, while cut audio has been litigated or pulled (S25, S61).
3. **Add EDL and SponsorBlock-JSON exporters, with soft-skip semantics by default.** `.edl` with Kodi action 3 (re-enterable commercial break) rather than 0 (hard cut), `##` provenance header (S41); Jellyfin EDL type 3 (S37) → clients' `PromptToSkip` (S43); SponsorBlock-shaped JSON with `actionType:"skip"` only above a high confidence and `full` (0,0) for the >35% whole-episode case (S12, S13, S42). This operationalises the false-positive asymmetry in formats consumers already honour.
4. **Bind labels to the rendition.** Store duration (±1 s), byte length and an audio hash/Chromaprint per label set; reject on mismatch using yt-dlp's tolerance rule (<1 s, or <5 s and <5% of span, S14). DAI renditions (S9, S50) make unbound timestamps actively harmful.
5. **Benchmark against MinusPod and ZeroAds, and publish.** Re-run AdVTT's fixtures with MinusPod's IoU≥0.5 span F0.5 and add 2+ no-ad negative-control episodes (S45); report `content_loss_sec` alongside ZeroAds' "85% of cut seconds are ad" (S59). Re-evaluate the gpt-5.5 default: MinusPod finds it fails the no-ad control and produces brittle JSON, while Haiku 4.5 / Gemini Flash-Lite score higher at a fraction of the cost (S45). Publishing precision *and* content-loss would be unique in the field (S21, S28, S29, S40).
6. **Borrow four MinusPod mechanisms** (S44): verification pass over the *remaining* audio (second LLM sweep, standalone misses held not auto-accepted); nearby-ad merge measured in speech seconds, not wall-clock; cross-episode sponsor-pattern cache scoped podcast→network→global (its community pattern JSON, S46, is importable); and cross-fetch differential for DAI, which PodcastFetch — already a downloader — is uniquely placed to implement.
7. **Add a cheap acoustic second channel for repeated creatives**: Chromaprint/landmark fingerprints of accepted ad spans re-matched across the corpus (S1, S36, S44), plus loudness-jump DAI boundary candidates (S44) to snap edges — while keeping the transcript LLM as sole authority for host-read copy (S58, S40).
8. **Frame the product as time-resolved disclosure/verification, not an ad blocker.** The namespace rejected ad-range tags over blocker fears (S50), AntennaPod locked its SponsorBlock thread on ethics (S17), Snipd declined the feature (S30). Positioning AdVTT output as machine-generated disclosure (cf. `<podcast:disclosure type="compensation" context="ad">`, S57; `podcast:txt purpose="ai-content"`, S46) and as a verification record (Podscribe's "time-stamped proof", S53) widens adoption and pre-empts the objections that killed prior efforts.
9. **Licence the label data deliberately.** SponsorBlock's CC BY-NC-SA 4.0 (S11) blocks commercial reuse; if AdVTT ever publishes a shared fixture/label set, choose CC BY-SA or ODbL and state it up front.

## Open questions / things that need an experiment

- Do Apple Podcasts, Spotify and Pocket Casts render `toc:false` JSON chapters, and does Pocket Casts' Preselect Chapters let a listener deselect them? (device test; S22, S47, S49)
- Does Jellyfin's Chapter Segments Provider map a chapter titled "Commercial"/"Sponsor" to the `Commercial` type out of the box, and does Kodi honour EDL action 3 for audio-only files? (S41, S43)
- Reproduce MinusPod's benchmark harness on AdVTT's 4 fixtures: how do IoU≥0.5 span F0.5 and AdVTT's `content_loss_sec`/`boundary_err_sec` disagree, and does gpt-5.5 fail a no-ad control in AdVTT's pipeline too? (S45)
- Is cross-fetch differential viable from PodcastFetch (two downloads per episode doubles publisher stats; correlation ceiling 0.60 default) and how often does it fire on the author's feeds? (S44)
- Can MinusPod's community sponsor patterns (S46) be consumed as an LLM prior without importing its cut semantics?
- Would the Podcast Index community accept a chapter-title convention or a `podcast:chapters` extension carrying `type`/`confidence`, given #254's rejection? (S23, S50, S57)
- Unverified: TiVo SkipMode's labelling method (human vs automated) and Herd's on-device vs cloud processing (S26, S61).
