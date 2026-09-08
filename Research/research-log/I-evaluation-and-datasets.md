# I — Evaluation methodology, ground-truth datasets, and labelling tooling
Accessed: 2026-09-01

## Status
COMPLETE — 68 sources (S1–S68), 2026-09-01. WebSearch was capped session-wide after 11 queries; remaining sources were primary-URL fetches. Unresolved fetches: NPR ToU (timeout), Audacity manual (521), SponsorBlock wiki (anti-bot wall), Prodigy/bbc audio-annotator (404).

## Sources

### Search log (first attempt, WebSearch; 11 queries succeeded before the search budget was exhausted)
- "SponsorBlock database export mirror sponsorTimes.csv size segments count" → sponsor.ajay.app/database, HF labofsahil/sponsorblock-dataset, phiresky/youtube-sponsorship-stats, towardsdatascience article, wereii/gosb
- "Mathet gamma agreement unitizing pygamma-agreement" → JOSS paper, readthedocs, MIT Press COLI 41(3), arXiv 2603.06865 (IAA survey)
- "promptfoo vs inspect-ai vs DeepEval 2026" → inference.net, arize, scrolltest, qaskills, aitestingguide
- "Creative Commons licensed podcast CC BY with sponsor reads" → CC blog on CBC podcasts (BY-NC-ND), player.fm list, CC wiki podcasting
- "SponsorBlock database license CC BY-NC-SA 4.0" → wiki Database-and-API-License, xenova/sponsorblock-ml, mchangrh/sb-mirror
- "podcast advertisement detection dataset Hugging Face Kaggle Zenodo" → Zenodo 10.5281/zenodo.17469222, morenolq/spotify-podcast-advertising-classification, ylacombe/podcast_fillers_by_license, ESpeech-podcasts
- "Spotify Podcast Dataset availability withdrawn" → podcastsdataset.byspotify.com ("no longer maintains"), COLING 2020 paper
- "Adblock Radio dataset" → github adblockradio/adblockradio (archived), ohadmich/Adetector
- "pyannote.metrics DetectionErrorRate ... tolerance purity coverage" → pyannote.github.io reference, Interspeech 2017 paper
- "SponsorBlock machine learning sponsor segment detection ... metrics" → xenova/sponsorblock-ml, DeepSponsorBlock CS230 PDF, arXiv 2502.15102, nikals99/sponsorblock-net
- "Label Studio audio segmentation template export" → labelstud.io/templates/audio_regions, /guide/export
- "SponsorBlock wiki segment categories votes locked hidden shadowHidden" → wiki.sponsor.ajay.app/w/API_Docs, FAQ
- "audio offset alignment ... audio-offset-finder OR audalign" → bbc/audio-offset-finder, benfmiller/audalign, norihiro/alignaudio
- "TRECVID shot boundary detection evaluation metric" → doras.dcu.ie/4080 (Smeaton, Over, Doherty "Seven years of TRECVid"), NIST tvpubs
- "TV commercial detection dataset public" → UCI #326, OpenBMAT (TISMIR 10.5334/tismir.29), arXiv 1811.02411
- "Audacity label track export format" → manual.audacityteam.org importing_and_exporting_labels, crowsetta docs
- "Krippendorff alpha unitizing temporal segments" → Artstein IAA (DTIC), Krippendorff "reliability of unitizing continuous data", ACL 2024 "Estimating Agreement by Chance for Sequence Annotation"
- "bootstrap confidence intervals ... how many examples needed LLM eval" → medium (Olamendy), assorted arXiv
- "Open ASR Leaderboard credibility held-out ... LiveBench ... SWE-bench Lite" → arXiv 2510.06961, HF blog ffasr-leaderboard, Appen blog, arXiv 2507.00460 "Pitfalls of Evaluating LMs with Open Benchmarks"
- Not run (budget exhausted): TWiT/Jupiter Broadcasting licences; model drift (arXiv 2307.09009); RadioTalk/MediaSum/SPGISpeech/PodcastMix sizes.

### S1. SponsorBlock database dumps — https://sponsor.ajay.app/database
- Type: dataset
- Verified: fetched
- Key facts: page lists 16 CSV tables (sponsorTimes, userNames, categoryVotes, lockCategories, warnings, vipUsers, unlistedVideos, videoInfo, ratings, titles, titleVotes, thumbnails, thumbnailTimestamps, thumbnailVotes, casualVotes, casualVoteTitles); "Last updated: Tue, 01 Sep 2026 22:40:01 GMT"; "CSV downloads have been disabled" for bandwidth — "use the sb-mirror project"; JSON index at /database.json; licence "CC BY-NC-SA 4.0", with "contact me ... I may grant you access under a different license". Page gives no row counts or column spec.
- Relevance to AdVTT: the only large, public, time-aligned sponsor-segment corpus; NC licence blocks bundling it into a commercially usable benchmark without a separate grant; get the dump via sb-mirror, not the CSV links.

### S2. SponsorBlock wiki — Database and API License — https://github.com/ajayyy/SponsorBlock/wiki/Database-and-API-License
- Type: legal
- Verified: fetched
- Key facts: "CC BY-NC-SA 4.0" unless explicit permission; attribution template supplied; maintainer (Ajay Ramachandran) may grant alternative licence on request.
- Relevance: any derived podcast-truth set inherits BY-NC-SA; a public AdVTT benchmark built from it must be NC-SA or negotiated.

### S3. labofsahil/sponsorblock-dataset (Hugging Face mirror) — https://huggingface.co/datasets/labofsahil/sponsorblock-dataset
- Type: dataset
- Verified: fetched
- Key facts: 17 CSV files, total 8.38 GB; card says licence "cc-by-nc-4.0" (drops the SA clause of the upstream licence — inconsistent with S1/S2); dataset viewer broken ("DatasetGenerationCastError ... 5 new columns and 2 missing columns"); search snippet said sponsorTimes.csv alone is approx. 5 GB (snippet-only).
- Relevance: convenient mirror but mis-licensed; cite upstream licence, not the card.

### S4. xenova/sponsorblock-ml — https://github.com/xenova/sponsorblock-ml
- Type: repo
- Verified: fetched (README); preprocess.py/evaluate.py fetch failed (session limit) — retry
- Key facts: T5-family seq2seq ("Xenova/sponsorblock-small", t5-small/base/large) over YouTube transcripts; preprocessing flags "--min_votes -1 --min_views 0 --min_date 01/01/2000 --max_date 01/01/9999 --keep_duplicate_segments"; evaluation reports "Missing segments: ... predicted by the model, but are not in the database" and "Incorrect segments: ... in the database, but the model did not predict" (note: the README's naming is inverted relative to the usual sense); data "licensed used under CC BY-NC-SA 4.0". Categories: sponsor, selfpromo, interaction.
- Relevance: prior art for transcript→segment detection trained on SponsorBlock; its metric is set-level segment match, no boundary tolerance published in README.

### S5. DeepSponsorBlock (Athreya, Gokmen, Yang; Stanford CS230, Fall 2020) — http://cs230.stanford.edu/projects_fall_2020/reports/55822706.pdf
- Type: paper (course report)
- Verified: fetched (PDF read in full)
- Key facts: dataset "~36,000 video IDs from SponsorBlock with at least five upvotes"; split 30,000/3,000/3,000; frames at 1 fps, 33.6 M frames, 1.5 M positive; metric = 1-D IoU; encoder-decoder median IoU 0.69, mean 0.54 on test (bimodal, big spike at 0); error analysis of 16 zero-IoU cases: 8 "Dataset Error" (4 videos had multiple sponsor segments with only one labelled; 2 predicted a different real segment; 2 "SponsorBlock's timestamps don't actually correspond to a sponsored segment"), 3 Bayes error, 5 model error. Assumed one segment per video.
- Relevance: quantifies SponsorBlock label noise (~half of gross failures were label problems at ≥5 votes); shows IoU alone hides multi-segment issues; argues for per-segment matching plus a completeness check of ground truth.

### S6. Kok-Shun & Chan, "Leveraging ChatGPT for Sponsored Ad Detection and Keyword Extraction in YouTube Videos" — https://arxiv.org/abs/2502.15102
- Type: paper (arXiv, submitted 2025-02-20)
- Verified: fetched (abstract page)
- Key facts: 421 YouTube transcripts (auto + manual); prompt-engineered GPT-4o for ad detection, KeyBERT for keywords; taxonomy of 9 content / 4 ad categories; no SponsorBlock ground truth mentioned; no temporal metric reported in abstract.
- Relevance: closest published LLM-based sponsor detection; no boundary metrics — a gap AdVTT can fill.

### S7. pygamma-agreement — Principles — https://pygamma-agreement.readthedocs.io/en/latest/principles.html
- Type: spec/docs
- Verified: fetched
- Key facts: Units (segment + category) in a Continuum per annotator; positional dissimilarity grows with start/end differences relative to combined duration; categorical dissimilarity via 0–1 matrix; combined d = α·d_pos + β·d_cat; chance correction by sampling N random continua, γ = 1 − δ_best/δ_random; input CSV "annotator, annotation, segment_start, segment_end".
- Relevance: gamma is the right IAA for unitising ad spans (handles gaps, boundary fuzz and category disagreement in one number); CSV input trivially produced from AdVTT truth JSON.

### S8. morenolq/spotify-podcast-advertising-classification — https://huggingface.co/morenolq/spotify-podcast-advertising-classification
- Type: model card
- Verified: fetched
- Key facts: BERT-base-cased binary sentence classifier (ad / not-ad) with previous-sentence context, trained on manually annotated sentences from Spotify podcast *descriptions* (not audio transcripts); test split 396 samples; accuracy 0.92; class-1 P 0.88 / R 0.91; paper Vaiani et al., "Leveraging Multimodal Content for Podcast Summarization", ACM SAC 2022; full TSV on GitHub; no licence stated.
- Relevance: only public podcast-ad classifier found; labels are description sentences, not time-aligned audio — not usable as temporal truth.

### S9. pyannote.metrics 4.1 reference — https://pyannote.github.io/pyannote-metrics/reference.html
- Type: spec/docs
- Verified: fetched
- Key facts: DetectionErrorRate = (false alarm + missed) / total positive duration; DetectionPrecision = tp/(tp+fp), DetectionRecall = tp/(tp+fn) by duration; DetectionCostFunction = "0.25 × false alarm rate + 0.75 × miss rate" (NIST OpenSAT 2019), params fa_weight=0.25, miss_weight=0.75; SegmentationPrecision/Recall match boundaries within `tolerance` (default 0.0 s); SegmentationPurity/Coverage duration-weighted, default tolerance 0.5 s; `collar` = "Duration (in seconds) of collars removed from evaluation around boundaries of reference segments (one half before, one half after)", default 0.0.
- Relevance: gives AdVTT a citable, off-the-shelf vocabulary: duration-based detection P/R, a cost function with asymmetric weights (AdVTT's asymmetry is the inverse of OpenSAT's: weight false alarms high), boundary F1 with tolerance, and a collar to forgive annotation fuzz.

### S10. Label Studio — Audio Classification with Segments template — https://labelstud.io/templates/audio_regions
- Type: product docs
- Verified: fetched
- Key facts: config `<Labels name="label" toName="audio" choice="multiple">…</Labels><Audio name="audio" value="$url"/>`; supports segmentation + classification; export JSON structure not shown on template page (see /guide/export — retry).
- Relevance: a 4-label config (ADVERTISEMENT/SPONSORSHIP/PROMOTION/PROGRAM) is a one-line change; regions export as start/end seconds.

### S11. Adblock Radio — https://github.com/adblockradio/adblockradio
- Type: repo
- Verified: fetched
- Key facts: archived 2021-04-10, read-only; MPL-2.0; classes ads / speech / music (+jingle, unsure) on ~1 s PCM chunks via time-frequency NN plus fingerprint "hotlist.sqlite"; model files served from adblockradio.com/models/; no labelled dataset released.
- Relevance: no reusable dataset; confirms the audio-only approach targets jingled radio ads, not host-read podcast reads.

### S12. SponsorBlock API docs (segment fields) — https://wiki.sponsor.ajay.app/w/API_Docs
- Type: spec
- Verified: snippet-only (fetch blocked; retry)
- Key facts (snippet): /api/segmentInfo returns videoID, startTime, endTime, votes, locked, UUID, userID, timeSubmitted, views, category, service, videoDuration, hidden, reputation, shadowHidden; FAQ: "When a submission reaches the score of -2 or lower, it gets removed" but stays in the DB; locked segments "will be prioritized over any other segment. VIPs' segments are always locked".
- Relevance: filtering recipe for truth derivation: drop hidden=1, shadowHidden=1, votes ≤ −2; prefer locked; de-duplicate overlapping submissions for the same video.

### S13. BBC audio-offset-finder — https://github.com/bbc/audio-offset-finder
- Type: repo
- Verified: snippet-only (fetch blocked; retry)
- Key facts (snippet): "cross-correlation of standardised Mel-Frequency Cepstral Coefficients to be robust to noise, encoding, and compression"; outputs offset in seconds and a "standard score" for peak prominence. Also seen: benfmiller/audalign (fingerprint / correlation / spectrogram alignment, PyPI), norihiro/alignaudio (sweeps offset, compensates clock drift).
- Relevance: the tool to align an RSS MP3 with a YouTube audio track to transfer SponsorBlock timestamps; single global offset is insufficient when YouTube has different pre-roll — need piecewise alignment (see Synthesis).

### S14. TRECVID shot boundary evaluation (Smeaton, Over, Doherty, "Video shot boundary detection: seven years of TRECVid activity") — https://doras.dcu.ie/4080/1/sbretro.pdf
- Type: paper
- Verified: snippet-only (fetch blocked; retry)
- Key facts (snippet): a transition counts as detected if it overlaps the reference by at least one frame (post-2001 rule to tolerate decoder frame-numbering differences); gradual transitions additionally scored with frame-based precision/recall on overlapping frames; one snippet mentions a 5 s absolute tolerance region (unverified).
- Relevance: precedent for a two-level report — event-level P/R with a tolerance, plus frame/second-level P/R for the gradual (fuzzy-edge) cases, which is exactly the ad-read fade-in/out problem.

### S15. TV commercial datasets — UCI #326 "TV News Channel Commercial Detection" — https://archive.ics.uci.edu/dataset/326/tv+news+channel+commercial+detection+dataset ; OpenBMAT — https://transactions.ismir.net/articles/10.5334/tismir.29 ; Portuguese TV ads (arXiv 1811.02411) — https://arxiv.org/abs/1811.02411
- Type: dataset / paper
- Verified: snippet-only (fetches blocked; retry OpenBMAT and 1811.02411)
- Key facts (snippets): UCI: features (not raw media) of shots from 150 h of TV news, 5 channels × 30 h (CNN-IBN, NDTV, TimesNow, BBC, CNN), 61.3 MB, shot-level commercial/non-commercial labels; OpenBMAT: 27+ h TV audio, 1647 one-minute excerpts, 4 countries, music-detection labels, 3 cross-annotators with high agreement; 1811.02411: >26 h / 28 programmes annotated at two levels (programme-vs-ad-block boundaries and per-commercial boundaries), audio-only method.
- Relevance: none of these carry host-read audio ads; the two-level annotation scheme in 1811.02411 (block boundaries + per-ad boundaries) is a good model for AdVTT truth (block = midroll break, unit = individual sponsor read).

### S16. Audacity label export format — https://manual.audacityteam.org/man/importing_and_exporting_labels.html (also crowsetta docs https://crowsetta.readthedocs.io/en/stable/formats/seq/aud-seq.html)
- Type: spec
- Verified: snippet-only (retry)
- Key facts (snippet): tab-delimited .txt, column 1 start seconds, column 2 end seconds, column 3 label text; point labels have start == end.
- Relevance: the lowest-friction truth-labelling path for a solo maintainer — open MP3 in Audacity, drag regions, type the label, Export Labels; conversion to truth JSON is ~10 lines of stdlib Python.

### S17. Krippendorff unitising alpha / Artstein IAA — https://apps.dtic.mil/sti/pdfs/AD1158943.pdf ; Krippendorff "On the Reliability of Unitizing Continuous Data" (ResearchGate listing)
- Type: paper
- Verified: snippet-only
- Key facts (snippet): Krippendorff's uα family measures agreement on unitising (boundary placement in a continuum) and labelling; α = 1 − Do/De; handles >2 annotators and missing data. ACL 2024 "Estimating Agreement by Chance for Sequence Annotation" (aclanthology 2024.acl-long.278) addresses chance agreement for span annotation.
- Relevance: alternative to gamma; gamma (S7) has a maintained Python implementation, uα does not (no maintained package found — gap).

### S18. Spotify Podcast Dataset / TREC Podcasts — https://podcastsdataset.byspotify.com/ (DNS now fails) ; paper https://aclanthology.org/2020.coling-main.519.pdf
- Type: dataset
- Verified: snippet-only (site unreachable: getaddrinfo ENOTFOUND on 2026-09-01)
- Key facts (snippet): 100,000+ episodes, approx. 60,000 h audio with Google ASR transcripts, used for TREC Podcasts 2020–21; site stated "due to shifting priorities, Spotify no longer maintains the dataset"; today the host does not resolve at all. No ad labels were part of the release.
- Relevance: not available; TREC Podcasts never labelled ads. Dead end for truth data.

### S19. Open ASR Leaderboard paper (arXiv 2510.06961, Oct 2025) and HF/Appen blogs — https://arxiv.org/abs/2510.06961 ; https://huggingface.co/blog/asr-benchmark-optimization ; https://www.appen.com/blog/hugging-face-open-llm-leaderboard
- Type: paper / blog
- Verified: snippet-only (retry arXiv)
- Key facts (snippets): 86 systems × 12 datasets, English short/long-form + multilingual tracks; all loaders and code open; Appen contributed a private held-out track "evaluated only by Hugging Face"; a "Benchmark fitting" tab quantifies reference error rates / orthographic switching to expose training-on-test.
- Relevance: template for credibility = open harness + public dev split + private held-out split + explicit contamination analysis.

### S20. LLM eval framework comparisons (promptfoo / DeepEval / Braintrust) — https://qaskills.sh/blog/promptfoo-vs-deepeval-2026 ; https://scrolltest.com/llm-regression-testing-promptfoo-vs-deepeval/ ; https://inference.net/content/llm-evaluation-tools-comparison/
- Type: blog
- Verified: snippet-only
- Key facts (snippets): promptfoo = TypeScript/Node CLI, "30+ assertions", exits non-zero on failed assertions for GitHub Actions; DeepEval = Python, pytest-native, "14 built-in metrics"; Braintrust hosted. None mention inspect-ai in these comparisons.
- Relevance: all three are heavier than a stdlib-first CLI wants; the pattern to copy is "assertions + non-zero exit + cached responses", not the framework.

### S21. Bootstrap / statistics snippets — https://medium.com/@juanc.olamendy/the-statistical-reality-of-llm-evaluation-what-works-what-doesnt-and-when-it-matters-7d9ba6ecdfca (and assorted arXiv)
- Type: blog
- Verified: snippet-only
- Key facts (snippets): common practice 1,000–10,000 bootstrap resamples; paired bootstrap of score differences, significant if 95% CI excludes 0; half-widths "around 3–5 percentage points" at typical eval sizes. Weak source; superseded by S-entries on Miller 2024 / Anthropic if fetched.
- Relevance: bootstrap over episodes is the standard, cheap CI method for a tiny eval set.

### S22. Zenodo podcast corpus (10.5281/zenodo.17469222) "Podcasts as Data: Building a Dataset for Large-Scale Audio Content Analysis" — https://doi.org/10.5281/zenodo.17469222 ; paper https://anthology.ach.org/volumes/vol0003/podcasts-as-data-building-dataset-for-large-scale/10.63744@QgeF94c0fP7D.pdf
- Type: dataset
- Verified: snippet-only (redirect to zenodo.org not followed yet — retry)
- Key facts (snippet): podcast dataset covering Aug 2019–Apr 2025; content type (audio vs metadata/transcripts) and licence unknown.
- Relevance: candidate source of episode metadata; unlikely to carry ad labels.

### S23. PodcastFillers — https://podcastfillers.github.io/ ; HF ylacombe/podcast_fillers_by_license
- Type: dataset
- Verified: snippet-only (retry)
- Key facts (snippet): 199 full-length English podcast episodes with manually annotated filler words; HF re-split "by license" suggests the episodes are CC-licensed podcasts.
- Relevance: a ready list of ~199 CC-licensed podcast episodes with known licences — a shortlist for a redistributable ad benchmark if any of those shows carry sponsor reads.

### S24. Creative Commons podcast licences (CC blog on CBC) — https://creativecommons.org/2010/10/10/on-cbc-podcasts-and-cc-licensed-music-available-for-commercial-use/
- Type: blog/legal
- Verified: snippet-only
- Key facts (snippet): CBC podcasts CC BY-NC-ND; NC licences bar use in ad-supported distribution; only BY / BY-SA permit commercial reuse.
- Relevance: a redistributable benchmark needs BY or BY-SA shows, or ND-tolerant handling (whole-episode redistribution with ND is allowed; clips are derivatives).

### Note on tooling (2026-09-01 second attempt)
WebSearch is hard-capped for this session (200/200 used across tracks) — the reset did not restore it. All further sources are direct WebFetch of primary URLs. wiki.sponsor.ajay.app is behind an Anubis anti-bot wall ("Access Denied"); falling back to the GitHub wiki copies.

### S25. mchangrh/sb-mirror — https://github.com/mchangrh/sb-mirror
- Type: repo
- Verified: fetched
- Key facts: "Docker containers to mirror the SponsorBlock database + API"; rsync-based with optional SQLite generation; README states "There are no longer any public mirrors that offer rsync downloads"; data "CC BY-NC-SA 4.0 from https://sponsor.ajay.app".
- Relevance: contradiction with S1 (which says to use sb-mirror because CSV downloads are disabled) — practical access path today is unclear; the HF mirror (S3) or /database.json may be the only working bulk routes. Needs a hands-on check.

### S26. xenova/sponsorblock-ml src/preprocess.py — https://raw.githubusercontent.com/xenova/sponsorblock-ml/main/src/preprocess.py
- Type: repo (code)
- Verified: fetched
- Key facts: PreprocessArguments defaults: min votes 0, min views 5, max segment duration 180 s, date window 20/08/2021–15/04/2022, min words-per-second 1.5; drops `service != 'YouTube'`, videoID len != 11, `hidden == '1' or shadowHidden == '1'`, categories outside allow-list, actionType outside ACTION_OPTIONS; drops whole videos having any segment > max duration or "non-locked segments [that] do not have enough views"; words aligned to segments by timestamp (`segment.extract_segment(video_words, start, end)`); WPS filter removes music/silence segments.
- Relevance: a concrete, reusable SponsorBlock cleaning recipe (hidden/shadowHidden/votes/views/duration/WPS) — adopt as the baseline filter for any podcast-truth derivation; the 180 s cap is comparable to AdVTT's 240 s max-duration rung.

### S27. xenova/sponsorblock-ml src/evaluate.py — https://raw.githubusercontent.com/xenova/sponsorblock-ml/main/src/evaluate.py
- Type: repo (code)
- Verified: fetched
- Key facts: each prediction matched to the DB segment with highest Jaccard (IoU) — "no explicit threshold"; predictions with no match flagged; DB segments with wps < 1.5 or `locked` are skipped in the "incorrect" check; reports accuracy, precision, recall, F (zero-division → P/R = 1, F = 0).
- Relevance: prior art is weak on temporal rigour (no IoU threshold, no boundary tolerance, no duration weighting) — AdVTT can differentiate by publishing a properly specified metric suite.

### S28. sed_eval (DCASE) sound-event metrics — https://tut-arg.github.io/sed_eval/sound_event.html
- Type: spec/docs
- Verified: fetched
- Key facts: segment-based metrics on a fixed grid, default `time_resolution=1.0` s; event-based metrics use onset collar `t_collar=0.2` s and offset tolerance `percentage_of_length=0.5` (offset within max(t_collar, 50% of event length)); error rate ER = (ΣS + ΣD + ΣI)/ΣN with S = min(FN,FP), D = max(0, FN−FP), I = max(0, FP−FN); F = 2PR/(P+R), micro or macro averaging.
- Relevance: a second mature template alongside pyannote (S9): AdVTT should report both a per-second (segment-based, 1 s grid) view and an event-based view with explicit onset/offset collars; the length-proportional offset collar is a good fit for ad reads whose tails are fuzzy.

### S29. Label Studio export guide — https://labelstud.io/guide/export
- Type: product docs
- Verified: fetched
- Key facts: generic formats JSON, JSON_MIN, CSV cover audio projects; audio-specific ASR_MANIFEST (NeMo) example has `offset` and `duration` seconds; the guide does not print an audio-region JSON example (region fields start/end/labels/channel are documented under the Audio tag page — not fetched).
- Relevance: JSON_MIN export is the target for a converter; expect per-region `value: {start, end, labels[], channel}` in seconds (from the tag docs; treat as unverified until checked against a real export).

### S30. Rule of three (statistics) — https://en.wikipedia.org/wiki/Rule_of_three_(statistics)
- Type: reference
- Verified: fetched
- Key facts: "If a certain event did not occur in a sample with n subjects, the interval from 0 to 3/n is a 95% confidence interval"; from (1−p)^n = 0.05 → n ln(1−p) ≈ −3; Hanley & Lippman-Hand (1983), JAMA 249(13):1743–5.
- Relevance: directly answers Q5: to claim "no episode exceeds 5 s content loss" with 95% confidence you need ≥ 60 episodes with zero violations (3/60 = 5% per-episode violation rate); 4 fixtures can only bound the violation rate at ≤ 75%.

### S31. Miller, "Adding Error Bars to Evals" — https://arxiv.org/abs/2411.00640
- Type: paper (arXiv, 2024-11-01, 14 pp.)
- Verified: fetched (abstract)
- Key facts: treat eval questions as a sample from an unseen population; CLT standard errors; clustered standard errors when questions are grouped (e.g., by source); paired differences for model comparison; power analysis to plan the eval size; formulas for measuring differences and planning.
- Relevance: episodes cluster by show (ad style is show-specific) → report clustered SEs by show; compare prompt versions with paired per-episode differences, not raw means.

### S32. promptfoo caching docs — https://www.promptfoo.dev/docs/configuration/caching/
- Type: product docs
- Verified: fetched
- Key facts: disk cache at `~/.promptfoo/cache` (cache-manager + keyv-file); key = provider id + request digest + provider config + vars; default TTL 14 days; errors not cached; `--repeat` uses separate namespaces; disable via `--no-cache`; CI via `PROMPTFOO_CACHE_TYPE=disk`, `PROMPTFOO_CACHE_PATH`; cached responses are not designed to be committed for deterministic replay.
- Relevance: promptfoo's cache is a cost saver, not a replay fixture; AdVTT needs its own recorded-response store (chunk-hash → response JSON) committed to the repo for offline CI.

### S33. Inspect (UK AI Security Institute) — https://inspect.aisi.org.uk/
- Type: product docs
- Verified: fetched
- Key facts: "framework for frontier AI evaluations developed by the UK AI Security Institute and Meridian Labs"; Dataset / Solver / Scorer; `pip install inspect-ai`; logs viewable via `inspect view`; has a Caching section for model outputs; open source (licence in repo).
- Relevance: well-designed but Python-package-heavy; AdVTT's eval can mirror the Dataset/Solver/Scorer split in-house without the dependency.

### S34. Chen, Zaharia, Zou, "How is ChatGPT's behavior changing over time?" — https://arxiv.org/abs/2307.09009
- Type: paper (arXiv, 2023-07-18, v3 2023-10-31)
- Verified: fetched (abstract)
- Key facts: GPT-4 March→June 2023 on prime identification 84% → 51%; attributed partly to "a drop in GPT-4's amenity to follow chain-of-thought prompting"; more formatting errors in code generation; GPT-3.5 improved on the same task; more refusals on sensitive questions.
- Relevance: canonical evidence for silent drift under a stable model name; AdVTT must pin dated snapshots where available and run a drift canary (fixed recorded set, alert on metric change).

### S35. Open ASR Leaderboard paper — https://arxiv.org/abs/2510.06961
- Type: paper (arXiv 2025-10-08, v4 2026-03-30)
- Verified: fetched (abstract)
- Key facts: Srivastav et al.; "86 open-source and proprietary systems across 12 datasets"; English short/long-form + multilingual tracks; "All code and dataset loaders are open-sourced"; standardised text normalisation across toolkits; public HF Space + GitHub repo. (Private held-out track and "benchmark fitting" analysis are from S19 snippets.)
- Relevance: minimum ingredients of a credible small benchmark: open harness, fixed normalisation, multiple tracks, public leaderboard with reproducible submissions.

### S36. Titeux & Riad, "pygamma-agreement" JOSS 6(62):2989, 2021 — https://doi.org/10.21105/joss.02989
- Type: paper
- Verified: fetched (PDF read)
- Key facts: implements Mathet et al. (2015) γ; constraints handled at once: "segmentation, unitizing, categorization, weighted categorization and the support for any number of annotators", chance-corrected; κ and Krippendorff's α "cannot address all of them at once"; formats: "RTTM, ELAN, TextGrid, CSV and pyannote.core.Annotation"; CLI `pygamma-agreement corpus/*.csv --confidence_level 0.02 --output_csv results.csv`; ~10 s to compute; reported γ: clinical turn-taking 0.64, speech activity in child recordings 0.46 (i.e., temporal γ values are typically well below the 0.8 folk threshold for κ). Paper CC BY 4.0.
- Relevance: use γ for AdVTT IAA; expect and document modest absolute values; report γ with and without categories (positional-only γ isolates boundary disagreement).

### S37. promptfoo CI/CD integration docs — https://www.promptfoo.dev/docs/integrations/ci-cd/
- Type: product docs
- Verified: fetched
- Key facts: GitHub Actions workflow triggered on `prompts/**` and `promptfooconfig.yaml` changes; `--fail-on-error`; custom thresholds by parsing JSON output and `exit 1`; `--share` yields `shareableUrl`; no specific guidance on nondeterminism beyond assertions.
- Relevance: the CI contract to copy (path-triggered, JSON results, non-zero exit, artifact upload) is trivially reproducible with a stdlib script.

### S38. LiveBench (White et al.) — https://arxiv.org/abs/2406.19314
- Type: paper (arXiv 2024-06-27; v3 2025-04-18; ICLR 2025 spotlight)
- Verified: fetched (abstract)
- Key facts: contamination limited by (1) "Questions are added and updated on a monthly basis", (2) recent source material, (3) scoring "automatically according to objective ground-truth values" — no LLM judge; top models "below 70% accuracy".
- Relevance: credibility levers for PodAd-Bench: refresh with newly published episodes on a schedule; objective ground truth (human span labels), no LLM-as-judge.

### S39. SWE-bench Lite — https://www.swebench.com/lite.html
- Type: benchmark docs
- Verified: fetched
- Key facts: "300 tasks from the full benchmark" plus "23 development instances"; seven filters (no images/links/SHAs, ≥40-word statements, single-file, ≤3 hunks, no file create/delete, no error-message tests), then random sample; motivation: "Reduce evaluation costs while maintaining benchmark quality", faster iteration, accessible entry point.
- Relevance: explicit, published selection filters and a separate small dev split are what make a subset credible; PodAd-Bench should publish its inclusion rules (show licence, has ≥1 host-read ad, duration band, language) and keep a dev split disjoint from test.

### S40. Jupiter Broadcasting — https://www.jupiterbroadcasting.com/
- Type: product (podcast network)
- Verified: fetched
- Key facts: shows released under "Creative Commons BY-SA 4.0"; shows: LINUX Unplugged, This Week in Bitcoin, The Launch, Jupiter EXTRAS; site has a "Sponsors" nav item (sponsor reads exist in episodes; Linux Unplugged historically carries host-read sponsor reads — snippet/knowledge, unverified here).
- Relevance: the strongest candidate for a redistributable benchmark: BY-SA permits redistribution of episodes and derivative clips; archive is long (LINUX Unplugged has 600+ episodes — approx., not verified) and host-read ads are in the host's voice, matching AdVTT's target.

### S41. Hacker Public Radio — https://hackerpublicradio.org/
- Type: product (podcast)
- Verified: fetched
- Key facts: episodes "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)" unless stated; latest episode hpr4717 (≥4,700 episodes since 2005); no advertising found.
- Relevance: a large BY-SA source of ad-free negative controls (episodes where the correct answer is "no ads") — valuable for measuring false-positive rate; useless for recall.

### S42. Anthropic, "A statistical approach to model evaluations" — https://www.anthropic.com/research/statistical-approach-to-model-evals
- Type: blog (companion to S31)
- Verified: fetched
- Key facts: report SEM, 95% CI = mean ± 1.96·SEM; "Clustered standard errors on popular evals can be over three times as large as naive standard errors"; resample per question and average (variance reduction); paired differences (model score correlation 0.3–0.7 gives "free" variance reduction); power analysis to size the eval.
- Relevance: AdVTT episodes are clustered by show and by STT backend — cluster on show; compare prompt versions by paired per-episode deltas; resample LLM runs (e.g., 3×) per episode to separate model noise from prompt effect.

### S43. VCR.py — https://vcrpy.readthedocs.io/en/latest/
- Type: product docs
- Verified: fetched
- Key facts: records HTTP interactions to YAML "cassettes" and replays; modes once / new_episodes / none / all; patches requests, urllib3, httpx, aiohttp, urllib; MIT; goals "work offline", "completely deterministic tests".
- Relevance: viable for the OpenAI/Gemini HTTP backends but not for `claude-cli`, Ollama-over-socket or MLX in-process; an AdVTT-level record/replay at the classifier-call seam (hash of chunk text + prompt_version + model → JSON) is provider-agnostic and needs no dependency.

### S44. OpenAI models page — https://developers.openai.com/api/docs/models
- Type: product docs
- Verified: fetched
- Key facts: models expose an alias and a dated/named ID (e.g., alias `gpt-5.6` → `gpt-5.6-sol`); a deprecations page exists (/api/docs/deprecations, not fetched); explicit "pin snapshots" advice not visible on this page.
- Relevance: record the resolved model ID (from the API response `model` field), not the alias, in `analysis.json` provenance; treat a change in the resolved ID as a drift trigger.

### S45. OpenBMAT (Meléndez-Catalán, Molina, Gómez; TISMIR 2019) — https://transactions.ismir.net/articles/10.5334/tismir.29
- Type: dataset/paper
- Verified: fetched
- Key facts: 27.4 h TV audio, 1647 one-minute excerpts; 6 music-presence classes; 3 annotators; full agreement 94.78% (MD mapping) / 89.1% (RMLE), partial agreement ~100%; licence CC BY 4.0; access "through a request form"; annotated with BAT (open-source web annotation tool).
- Relevance: model for how to report cross-annotation (3 annotators, agreement under two label mappings); CC BY 4.0 with request form is a workable access pattern if audio redistribution is sensitive.

### S46. RadioTalk — https://github.com/social-machines/RadioTalk
- Type: dataset
- Verified: fetched
- Key facts: talk-radio ASR transcripts, JSONL, ~9.3 GB compressed at `s3://radio-talk/v1.0/`; fields include show, callsign, city, state; ads not labelled; licence not stated in repo.
- Relevance: no ad labels; not useful as truth.

### S47. MediaSum — https://github.com/zcgzcgzcg1/MediaSum
- Type: dataset
- Verified: fetched
- Key facts: 463.6K NPR/CNN interview transcripts with summaries; "restrict your usage of this dataset to research purpose only"; no statement on ads.
- Relevance: not useful as temporal truth (text only, no timestamps, ads unmarked).

### S48. PodcastMix (MTG) — https://github.com/MTG/Podcastmix
- Type: dataset
- Verified: fetched
- Key facts: speech/music separation dataset; synthetic set ~480 GB (Jamendo music + VCTK speech) plus small real podcast partitions (with/without reference); Interspeech 2022; no ad labels.
- Relevance: not useful for ad truth.

### S49. PodcastFillers — https://podcastfillers.github.io/ (Zenodo record 7121457)
- Type: dataset
- Verified: fetched
- Key facts: "199 full-length podcast episodes in English", "145 hours of audio from over 350 speakers"; 85,803 annotated events (≈35k uh/um + ≈50k non-filler); audio "sourced from SoundCloud" and "CC-licensed", gender-balanced; annotations under a non-commercial licence; ads not labelled.
- Relevance: a vetted list of 199 CC-licensed full episodes with known licence per episode — the quickest route to a redistributable candidate pool; need to check which shows carry sponsor reads (likely few, as SoundCloud indie podcasts).

### S50. "Podcasts as Data" (Verreyen; Zenodo 17469222) — https://zenodo.org/doi/10.5281/zenodo.17469222
- Type: dataset
- Verified: fetched
- Key facts: bag-of-words matrices (not audio) for >15,000 episodes / 1,900 shows across 19 Apple genres, Distil-Whisper-Large-v3 transcripts; 44.5 MB; CC BY 4.0; no ad labels.
- Relevance: not useful as temporal truth.

### S51. Ramires, Cocharro, Davies, "An audio-only method for advertisement detection in broadcast television content" — https://arxiv.org/abs/1811.02411
- Type: paper
- Verified: fetched (abstract)
- Key facts: "26 hour annotated database" of Portuguese TV; detects boundary silences then rejects non-boundary silences with multiple linear regression; metric: Matthews correlation coefficient > 0.87; dataset availability not stated.
- Relevance: MCC is a sensible single-number companion for imbalanced per-second classification (ads ≈ 5–10% of an episode); TV approach (silence gaps) does not transfer to host-read reads with no gap.

### S52. audio-offset-finder (BBC) — https://github.com/bbc/audio-offset-finder ; audalign — https://github.com/benfmiller/audalign
- Type: repo
- Verified: fetched
- Key facts: BBC tool: MFCC cross-correlation; `audio-offset-finder --find-offset-of file1.wav --within file2.wav`; outputs offset (s) and standard score — "A score greater than ten is likely to be correct; less than five is unlikely"; accuracy ~0.01 s; default 8 kHz / 128-sample hop = 0.016 s; `--trim` to analyse only the first N seconds; Apache-2.0. audalign: fingerprint / correlation / spectrogram / visual recognizers, MIT, PyPI.
- Relevance: alignment recipe for SponsorBlock transfer: run offset-finder on several windows (start, each SponsorBlock segment ±60 s, end) and require consistent offsets with score >10; inconsistent offsets = different edits (extra pre-roll/dynamic ads) → discard the pair or align piecewise.

### S53. yt-dlp SponsorBlock options — https://github.com/yt-dlp/yt-dlp
- Type: product docs
- Verified: fetched
- Key facts: `--sponsorblock-mark CATS` writes chapters for categories (sponsor, intro, outro, selfpromo, preview, filler, interaction, music_offtopic, hook, poi_highlight, chapter, all, default); `--sponsorblock-remove`; `default` = "all,-filler"; chapter title template default "[SponsorBlock]: %(category_names)l"; `--sponsorblock-api` default https://sponsor.ajay.app.
- Relevance: a zero-code way to pull served (already vote-filtered) segments per video as chapters; the served set is the de-facto "consensus" label, complementing raw DB rows.

### Gaps / failures logged
- wiki.sponsor.ajay.app (Anubis wall) and the GitHub wiki copies (moved) both blocked: segment field semantics remain snippet-only (S12). Will try SponsorBlockServer schema on raw.githubusercontent.
- twit.tv/about/faq 404; democracynow podcasting page carries no licence text; NPR ToU timed out — retry.
- bbc/audio-annotator and prodi.gy/docs/audio returned 404 — audio-annotator likely archived/renamed; Prodigy docs moved. Recorded as unverified.
- manual.audacityteam.org returned 521 twice — Audacity format stays snippet-only (S16).
- COLING 2020 and TRECVID PDFs saved locally; reading with the PDF reader next.

### S54. Smeaton, Over, Doherty, "Video Shot Boundary Detection: Seven Years of TRECVid Activity" (preprint 2009-03-12) — https://doras.dcu.ie/4080/1/sbretro.pdf
- Type: paper
- Verified: fetched (PDF pp.1–8 read)
- Key facts: SBD ran 2001–2007, 57 groups, ~6 h test video/year, groundtruth by one NIST annotator with VirtualDub (so "Analysis of annotator variation ... was not possible"); detection "required only a single frame overlap between the submitted transitions and the reference transition ... to make the detection independent of the accuracy of the detected boundaries"; abrupt cuts treated as 2 frames and "expanded by 5 frames in each direction" before matching (decoder frame-numbering tolerance); gradual transitions ≤5 frames treated as cuts; accuracy of matched graduals measured with frame-based precision/recall on overlapping frames; primary measures P, R, F = 2RP/(R+P).
- Relevance: TRECVID separates *detection* (did we find the event, with a generous tolerance) from *accuracy* (how well do the frames overlap) and reports both — the right structure for AdVTT (event-level detection F1 at a tolerance + duration-level precision/recall on matched events). Also a warning: single-annotator truth forecloses IAA analysis.

### S55. Clifton et al., "100,000 Podcasts: A Spoken English Document Corpus", COLING 2020 — https://aclanthology.org/2020.coling-main.519.pdf
- Type: paper
- Verified: fetched (PDF pp.1–4 read)
- Key facts: 105,360 episodes sampled Jan 2019–Mar 2020, "nearly 60,000 hours", 18,376 shows; ~10% professional creators; Google Cloud STT word timings + diarization, sample WER 18.1%; episodes "all Spotify owned-and-operated, for copyright reasons"; paper CC BY 4.0 but the data was access-controlled via podcastsdataset.byspotify.com (host now unresolvable, S18). No ad annotation anywhere in the paper.
- Relevance: confirms the dataset is unavailable and never had ad labels; Gimlet/Spotify O&O shows contain dynamically inserted ads that would in any case differ per download — a general caveat for any RSS-derived truth (see Synthesis).

### S56. SponsorBlockServer SQLite schema — https://raw.githubusercontent.com/ajayyy/SponsorBlockServer/master/databases/_sponsorTimes.db.sql
- Type: repo (schema)
- Verified: fetched
- Key facts: base `sponsorTimes` columns: videoID TEXT, startTime REAL, endTime REAL, votes INTEGER, UUID TEXT UNIQUE, userID, timeSubmitted INTEGER, views INTEGER, category TEXT, shadowHidden INTEGER; later migrations add locked, hidden, actionType, service, videoDuration, reputation, description, hashedVideoID (present in API output per S12 and in the dump CSV per S26 code which reads `hidden`, `shadowHidden`, `actionType`, `service`).
- Relevance: authoritative column list for the CSV parser; start/end are floating seconds relative to the YouTube video.

### S57. SponsorBlock issue #1736 "Major loss of data in database" (2023-05-01) — https://github.com/ajayyy/SponsorBlock/issues/1736
- Type: forum (issue)
- Verified: fetched
- Key facts: public DB dump shrank "2.3 GB → 235 MB → 909 KB within hours"; reporter: "practically all entries have been removed form the sponsorblock database"; resolution not on the page.
- Relevance: dumps are operationally fragile; pin a specific dump date/hash in any derived truth set and archive it.

### S58. Audino v2.0 — https://github.com/midas-research/audino
- Type: repo
- Verified: fetched
- Key facts: web audio annotation with projects/tasks/jobs, multi-user, export "in specific formats"; licence CC BY-NC 4.0 (non-commercial); "actively under development".
- Relevance: NC licence and server footprint make it a poor fit for a stdlib CLI's contributors; Label Studio (S10/S29/S62) or Audacity (S16) are simpler.

### S59. OpenAI deprecations policy — https://developers.openai.com/api/docs/deprecations
- Type: product docs
- Verified: fetched
- Key facts: notice "At least 6 months" for GA models, "At least 3 months" for specialised variants, previews "such as 2 weeks"; dated snapshots (e.g., `gpt-5-2025-08-07`) are retired in favour of newer IDs; deprecation is immediate on announcement, legacy models "no longer receive updates".
- Relevance: a pinned snapshot buys at most ~6 months of stability; the eval harness must re-baseline on every forced migration, and `analysis.json` must record the exact model ID so cached classifications can be invalidated per model.

### S60. PodcastFillers Zenodo record 7121457 — https://zenodo.org/record/7121457
- Type: dataset
- Verified: fetched
- Key facts: annotations under an Adobe "noncommercial research purposes only" licence; audio per-episode CC "CC-BY-3.0, CC-BY-SA 3.0 and CC-BY-ND-3.0" recorded in `podcast_episode_license.csv`; 25.3 GB total (zip + 3 split parts + 21.7 MB CSV); per-episode CSVs carry annotator confidence (0–1) and crowd agreement counts.
- Relevance: the per-episode licence CSV is exactly the provenance a redistributable PodAd-Bench needs; ND episodes can be redistributed whole but not clipped; only the BY/BY-SA subset supports clip-level fixtures.

### S61. TWiT.tv about page — https://twit.tv/about (licence page /about/license not fetched; /about/faq 404)
- Type: product
- Verified: fetched (partial)
- Key facts: footer links to a "CC License" page; site has "Advertise" and "Sponsors" sections (host-read ads are TWiT's business model). Exact licence type not confirmed on this page (commonly cited as BY-NC-ND — unverified here).
- Relevance: if BY-NC-ND is confirmed, TWiT episodes can be redistributed whole, non-commercially, unmodified — usable as a benchmark's audio source under an NC benchmark licence, but not clipped and not for commercial evaluators.

### S62. Label Studio Audio tag docs — https://labelstud.io/tags/audio
- Type: product docs
- Verified: fetched
- Key facts: region result example: `{"original_length": 18, "value": {"start": 3.1, "end": 8.2, "channel": 0, "labels": ["Voice"]}}`; params include `defaultzoom` (1–1500), `spectrogram`, `decoder` (webaudio/ffmpeg), `hotkey`, `sync`.
- Relevance: the exact fields a converter needs (`value.start/end` seconds, `value.labels[]`); `sync` can tie the waveform to a transcript view for evidence-quote capture.

### S63. Hasan et al., "Pitfalls of Evaluating Language Models with Open Benchmarks" — https://arxiv.org/abs/2507.00460
- Type: paper (arXiv 2025-07-01; withdrawn by authors 2026-06-03 for overlap with prior work)
- Verified: fetched (abstract)
- Key facts: models fine-tuned on public test sets "fail terribly to generalize to comparable unseen testing sets"; recommends complementing open benchmarks with "private or dynamically generated benchmarks" and paraphrase-based safeguards.
- Relevance (with caution given withdrawal): supports a private held-out episode set alongside the public split.

### S64. NeuralBlock (andrewzlee) — https://github.com/andrewzlee/NeuralBlock
- Type: repo
- Verified: fetched
- Key facts: Keras BiLSTM over YouTube transcripts labelled by SponsorBlock timestamps; 10k-word vocabulary; README "somewhat outdated", DB snapshot 2020-03-03; no metrics in README (S5 cites ">90%" accuracy — text-classification accuracy, not temporal).
- Relevance: another prior-art project with no temporal metric — reinforces the opening for a properly specified benchmark.

### S65. Democracy Now! about page — https://www.democracynow.org/about
- Type: product
- Verified: fetched
- Key facts: accepts no "government funding, corporate sponsorship, underwriting or advertising revenue"; licence not stated on this page (CC BY-NC-ND per S24-era knowledge — unverified).
- Relevance: ad-free news → negative-control episodes only.

### Gaps (final)
- NPR Terms of Use timed out twice; NPR content is not CC and NPR shows carry dynamically inserted + host-read ads — treat as non-redistributable (unverified this session).
- SponsorBlock served-segment selection logic (vote threshold in getSkipSegments) not verified; API docs remain snippet-only (S12).
- No maintained implementation of Krippendorff's unitising uα found; γ (S7/S36) is the practical choice.
- No published podcast↔YouTube SponsorBlock alignment dataset or paper was found in any search — a documented gap and an opportunity.
- Prodigy audio docs and bbc/audio-annotator URLs 404 — not evaluated.

### S66. SponsorBlockServer getSkipSegments.ts — https://raw.githubusercontent.com/ajayyy/SponsorBlockServer/master/src/routes/getSkipSegments.ts
- Type: repo (code)
- Verified: fetched
- Key facts: served segments exclude `segment.hidden || segment.votes < -1 || segment.shadowHidden === Visibility.MORE_HIDDEN`; shadow-hidden segments shown only to the submitter's hashed IP; `getBestChoice` weight = `choice.votes + boost` (boost = submitter reputation), shuffled then sorted descending, locked segments prioritised; `chooseSegments` returns one segment per overlapping group (one Full, one POI).
- Relevance: the exact consensus rule to reproduce offline: keep votes ≥ −1, not hidden/shadowHidden, pick the highest (votes + reputation) per overlap group, prefer locked. This is what yt-dlp (S53) receives.

### S67. TWiT.tv licence page — https://twit.tv/about/license
- Type: legal
- Verified: fetched
- Key facts: "Creative Commons Attribution Non-Commercial No-Derivatives 4.0 International"; "distribute these shows freely as long as you attribute them to TWiT.tv"; "You may not distribute our shows for monetary gain of any kind"; "Nor may you create derivatives of our shows, including but not limited to, removing commercials, without express written consent".
- Relevance: TWiT explicitly forbids removing commercials as a derivative — a benchmark can redistribute whole TWiT episodes non-commercially with labels alongside (labels are separate facts, not a derivative of the audio), but must not ship ad-stripped or clipped versions; and TWiT-derived evaluation must be non-commercial. Strong candidate for the NC public split (large back-catalogue, host-read ads).

### S68. LINUX Unplugged site — https://linuxunplugged.com/
- Type: product
- Verified: fetched
- Key facts: episode 682 dated 2026-08-30; licence shown as "CC Attribution + NonCommercial (BY-NC)" — contradicts the network homepage (S40: "BY-SA 4.0"); Memberful "Core Contributor" membership; YouTube channel "jupiterbroadcasting".
- Relevance: licence must be confirmed per show/episode (RSS `<copyright>`/`<creativeCommons:license>` tag) before redistribution; the YouTube mirror makes JB shows candidates for SponsorBlock-derived labels (Q2) — check SponsorBlock coverage of that channel.

## Synthesis

**Q1 — Existing time-aligned ad/sponsor datasets.** Only one large public corpus has time-aligned sponsor labels: SponsorBlock (S1, S56). Its dump is a set of CSVs (16–17 tables; ~8.4 GB on the HF mirror, S3), updated daily (S1), licensed CC BY-NC-SA 4.0 (S2) — the HF mirror mislabels it BY-NC (S3). Bulk access is currently awkward: the official page disables CSV downloads and points at sb-mirror (S1), whose README says no public rsync mirrors remain (S25); the HF mirror and `/database.json` are the practical routes. No row/segment count could be verified from a primary source this session (gap); a 2020 course project already used ~36k videos at ≥5 votes (S5). Everything else is a dead end for temporal ad truth: the Spotify Podcast Dataset (100k episodes, 60k h) is withdrawn and never carried ad labels (S18, S55); TREC Podcasts likewise; RadioTalk (S46), MediaSum (S47), PodcastMix (S48), "Podcasts as Data" (S50) and PodcastFillers (S49, S60) have no ad labels; the only podcast-ad classifier found is sentence-level on *descriptions* (S8); Adblock Radio released no dataset (S11); TV commercial sets (UCI features only, S15; Portuguese 26 h not confirmed public, S51; OpenBMAT is music-detection, S45) target jingled spot ads, not host-read reads. "Podcastle" and "SPGISpeech" (redirects to a marketing page) yielded nothing relevant. **Finding: there is no public podcast benchmark with time-aligned host-read ad labels. AdVTT would be first.**

**Q2 — Deriving podcast truth from SponsorBlock.** Feasible but with three caveats the evidence makes concrete. (a) *Label noise*: at ≥5 upvotes, half of a sample of gross model failures were label errors — multiple sponsor segments with only one labelled, or timestamps that were not sponsors at all (S5). The server's own consensus rule (votes ≥ −1, not hidden/shadowHidden, weight = votes + reputation, prefer locked; S66) and the sponsorblock-ml recipe (drop hidden/shadowHidden, min views 5, max 180 s, ≥1.5 words/s; S26) are the two filters to compose; treat "locked" as gold, "votes ≥ 2 and unlocked" as silver, and always take *all* consensus segments per video, never one. (b) *Offset*: YouTube uploads differ from RSS audio in pre-roll and in dynamically inserted ads (Spotify O&O shows, S55). BBC audio-offset-finder gives sub-20 ms offsets with a confidence z-score ("greater than ten is likely to be correct", S52), but a single global offset is insufficient; align per window (start, around each candidate segment, end) and reject pairs whose offsets disagree — disagreement itself flags dynamic-ad insertion. (c) *Category mapping*: SponsorBlock's `sponsor` ≈ AdVTT SPONSORSHIP/ADVERTISEMENT, `selfpromo` ≈ PROMOTION, `interaction`/`intro`/`outro` ≈ not-ad (S53 lists the category set; definitions page blocked by the wiki's anti-bot wall — S12 snippet-only). Candidate shows with YouTube mirrors and host-read reads: Jupiter Broadcasting (S40, S68), TWiT (S67). **No published podcast↔YouTube SponsorBlock alignment or dataset was found (gap/opportunity).** Licence: anything derived is BY-NC-SA (S2) unless Ajay grants otherwise (S1).

**Q3 — Metrics.** Three mature families converge on the same two-level structure: pyannote.metrics (duration-based DetectionPrecision/Recall/ErrorRate, DetectionCostFunction with asymmetric fa/miss weights, SegmentationPrecision/Recall with a boundary tolerance, purity/coverage, and a collar around reference boundaries; S9), sed_eval (segment-based on a 1 s grid plus event-based with 200 ms onset collar and offset collar = max(collar, 50% of event length); S28) and TRECVID (event detection with generous tolerance, then frame-based P/R for accuracy of matched events; S54). Prior sponsor-detection work is weak here: unthresholded best-Jaccard matching (S27), single-segment IoU (S5), text-classification accuracy (S64, S6). AdVTT's existing `content_loss_sec` is a DetectionCostFunction with fa_weight=1, miss_weight=0 in pyannote's terms; `boundary_err_sec ≤ 3 s` is a SegmentationPrecision tolerance. MCC is a sensible single scalar for imbalanced per-second labels (S51). Contradiction to note: OpenSAT's default weights (0.25 fa / 0.75 miss, S9) are the *opposite* of AdVTT's asymmetry — cite the mechanism, invert the weights, say so.

**Q4 — Labelling tooling.** Label Studio's audio template exports `value.start/end` seconds and `labels[]` per region (S10, S29, S62); Audacity exports tab-separated `start\tend\tlabel` (S16, snippet-only — manual unreachable twice); Audino is CC BY-NC and server-based (S58); Prodigy and bbc/audio-annotator URLs 404 (not evaluated). For IAA, γ (Mathet 2015; pygamma-agreement, S7, S36) handles unitising + categorisation + boundary fuzz in one chance-corrected number, reads CSV/RTTM/TextGrid/ELAN, and its authors report temporal γ of 0.46–0.64 on real corpora — expect and publish modest values. No maintained uα implementation was found (S17). OpenBMAT's 3-annotator, two-mapping agreement report (S45) is a good reporting model; TRECVID's single-annotator truth is a cautionary tale (S54).

**Q5 — Statistical rigour.** Rule of three (S30): zero violations in n episodes bounds the per-episode violation rate at 3/n with 95% confidence, so "content_loss ≤ 5 s per episode" needs ≥ 60 clean episodes; 4 fixtures bound it at ≤ 75%. Miller (S31) and Anthropic (S42): report SEM/95% CI, cluster standard errors by show ("over three times as large as naive"), use paired per-episode differences to compare prompt versions, resample LLM runs per episode, and run a power analysis before adding fixtures. The current 4 fixtures from 2 shows were also used to tune the prompt — by the standards in S19/S35/S39/S63 they are a dev set, not a test set; any public number from them would be contaminated by construction.

**Q6 — Regression testing.** promptfoo (S32, S37), DeepEval, Braintrust (S20) and Inspect (S33) all add a runtime (Node or a Python stack); promptfoo's cache is a cost saver, explicitly not a committed replay fixture (S32). VCR.py (S43) gives deterministic HTTP replay but cannot cover `claude-cli`, Ollama or in-process MLX. Silent drift is real (GPT-4 84% → 51% on one task between two months under the same name, S34); OpenAI aliases move between snapshots and snapshots retire with ≥6 months' notice (S44, S59). Lightweight pattern: record at the classifier seam (hash(prompt_version, model_id, chunk text) → response JSON) committed to the repo; CI replays with zero network; a scheduled live "canary" run compares to the recorded baseline and fails on metric deltas — the Inspect Dataset/Solver/Scorer split (S33) and promptfoo's path-triggered CI with non-zero exit (S37) are copied as conventions, not dependencies.

**Q7 — Public benchmark.** Credibility ingredients from S19/S35 (open harness and loaders, fixed normalisation, public + private held-out tracks, contamination analysis), S38 (scheduled refresh with new material, objective ground truth, no LLM judge), S39 (published inclusion filters, separate dev split, small size to keep cost low). Redistribution: SponsorBlock-derived labels are BY-NC-SA (S2); TWiT audio is BY-NC-ND and explicitly bans ad removal as a derivative (S67); Jupiter Broadcasting is BY-SA per the network page but BY-NC per the show page (S40 vs S68 — must be resolved per feed); HPR is BY-SA and ad-free (S41) — negative controls; Democracy Now is ad-free (S65); NPR is not CC (ToU unreachable, S-gap); PodcastFillers supplies 199 CC episodes with per-episode licence CSV (S60) but likely few sponsor reads. **A minimum viable PodAd-Bench is therefore: labels-only public release (JSON with episode GUID, enclosure URL + SHA-256, spans) for shows whose licences permit redistribution or which remain fetchable from the original feed; audio mirrored only for BY/BY-SA shows; a private held-out split for the maintainers; NC licence on the SponsorBlock-derived portion.**

## Implications for AdVTT

1. **Adopt a two-level metric suite and publish its definitions.** Level A (duration-based, per episode): `content_loss_sec` (false-alarm seconds, pyannote DetectionCostFunction with fa_weight=1, miss_weight=0 — S9), `ad_recall_sec` (DetectionRecall by duration — S9), per-second MCC (S51), all computed on a 1 s grid (sed_eval segment-based — S28) with a 0.5 s collar around reference boundaries (S9). Level B (event-based): detection precision/recall/F1 where a predicted span matches a reference span if IoU ≥ 0.5 *or* both boundaries fall within tolerance; onset tolerance 3 s, offset tolerance max(3 s, 20% of span) (sed_eval's length-proportional offset collar — S28; TRECVID's detection-vs-accuracy split — S54). Report boundary error as median and 90th percentile absolute error over matched events, not a single threshold pass/fail. Keep the current gates (≤5 s, ≥0.70, ≤3 s) but attach a 95% CI (S30, S31, S42).

2. **Report cost-weighted results explicitly and invert the OpenSAT convention on purpose.** State: "DCF_AdVTT = 1.0·FA_sec + 0.1·MISS_sec per episode" (weights are a product decision; the 0.1 is a placeholder to be argued in the README), and cite that OpenSAT's defaults (0.25/0.75) reflect the opposite asymmetry (S9). Present per-show breakdowns (S31/S42 clustering) and a table of worst-case episodes, because the ship gate is a per-episode maximum, not a mean.

3. **Re-classify the 4 fixtures as the dev set and build a disjoint test set of ≥ 60 episodes from ≥ 10 shows before quoting any public number.** 60 is the rule-of-three minimum for a zero-violation claim at 95% (S30); ≥10 shows because errors cluster by show (S42). Never tune the prompt on the test set again; log every prompt_version that touched dev (S39, S63).

4. **Bootstrap truth from SponsorBlock, but as silver, not gold.** Pipeline: pick shows with YouTube mirrors (S40/S68, S67); pull served segments via yt-dlp `--sponsorblock-mark` (S53) *and* raw rows from the dump filtered per S66/S26; align RSS audio to YouTube audio with audio-offset-finder on multiple windows, requiring consistent offsets with score > 10 (S52); reject episodes with inconsistent offsets (dynamic ads). Hand-verify a stratified 20% sample and report the observed label-error rate — DeepSponsorBlock's ~50% of gross failures being label errors (S5) is the prior to beat. Pin the dump date and checksum (S57). Everything derived is BY-NC-SA (S2).

5. **Labelling workflow: Audacity or Label Studio → truth JSON, two annotators on a 20% overlap, γ reported.** Truth JSON gains `annotator`, `tool`, `source` (human | sponsorblock-silver), and per-span `boundary_confidence`. Converters: Audacity `start\tend\tlabel` (S16) and Label Studio `value.start/end/labels` (S62) are each <30 lines of stdlib Python. Compute γ with pygamma-agreement on the overlap (S36) and publish positional-only γ separately from combined γ, plus the median inter-annotator boundary distance — this is also the empirical justification for the 3 s tolerance in (1).

6. **Provenance must carry the resolved model ID, prompt_version and STT backend; add a recorded-response replay store and a drift canary.** Aliases move and snapshots retire (S44, S59); behaviour changes silently (S34). Store `classifier_cache/<sha256(prompt_version|model_id|chunk_text)>.json` in-repo for the dev set so CI runs offline in seconds with zero dependencies (VCR.py is an option only for HTTP backends — S43); run a weekly live job against the same inputs and fail if any Level-A metric moves beyond its bootstrap CI (S31). Copy promptfoo's conventions — path-triggered workflow, JSON results artifact, non-zero exit — without adopting Node (S32, S37).

7. **Minimum viable "PodAd-Bench" (public).** (a) Labels-only repository: episode GUID, feed URL, enclosure URL, SHA-256 and duration of the exact file, spans with kind + advertiser, annotator/source, licence of the underlying audio; (b) audio mirrored only for BY / BY-SA episodes (resolve the JB BY-SA vs BY-NC contradiction per feed — S40/S68; HPR for ad-free negatives — S41); TWiT episodes referenced by URL only, whole-file, non-commercial, never clipped (S67); (c) a `dev` (public, ~20 episodes) / `test` (public, ≥60) / `private` (maintainer-held, ≥20, refreshed with newly published episodes each quarter per LiveBench — S38) split with the inclusion filters written down SWE-bench-Lite style (S39); (d) an eval harness that downloads from the original enclosures and verifies hashes, so the benchmark never redistributes what it may not; (e) a results table with per-show CIs, a "label-noise" tab quantifying silver-label error (S5), and a contamination statement (which episodes were ever used for prompt tuning) modelled on Open ASR Leaderboard's benchmark-fitting tab (S19/S35).

8. **Challenge to the current design:** the 240 s max-duration rung and 35% over-label gate are hyperparameters tuned on 4 episodes; SponsorBlock's ecosystem uses 180 s (S26) and long-form shows (TWiT, JB) routinely run multi-minute ad blocks. Re-derive both from the ≥60-episode test set's empirical span-length distribution and report them as data-driven, with the fraction of true ads they would clip.

## Open questions / things that need an experiment

1. How many SponsorBlock-covered YouTube uploads exist for the candidate podcast shows (JB, TWiT, others), and what fraction align to RSS audio with a single consistent offset? (One afternoon with yt-dlp + audio-offset-finder on 30 episodes.)
2. Empirical inter-annotator boundary distance for host-read reads — is 3 s the right tolerance, or are ad-read edges fuzzier (host banter into the read)? Two annotators × 20 episodes, γ and boundary-distance histogram.
3. Actual segment/video counts in the current SponsorBlock dump and whether `/database.json` or the HF mirror is the reliable bulk path (S1 vs S25 contradiction).
4. Confirm the Jupiter Broadcasting licence per feed (BY-SA vs BY-NC; S40 vs S68) via the RSS `<copyright>` element, and ask TWiT whether labels-alongside-whole-episodes is acceptable under their ND reading (S67).
5. Whether Ajay Ramachandran would grant a non-NC licence for a labels-only derived benchmark (S1/S2 invite the request).
6. Does dynamic ad insertion in RSS enclosures change between downloads for the candidate shows (hash the same enclosure over 3 days)? If yes, the benchmark must ship hashes and possibly mirrored audio for BY/BY-SA shows only.
7. Power analysis (S31): given observed per-episode `content_loss_sec` variance on the dev set, how many test episodes are needed to detect a 2 s mean regression between prompt versions at 80% power?
8. Whether Audacity's exported label format includes the extended `\` frequency lines by default (manual unreachable — S16) — affects the converter's parser.

