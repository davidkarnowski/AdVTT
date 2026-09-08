# B — Academic and technical literature on ad / sponsorship / segment detection
Accessed: 2026-09-01

## Status
COMPLETE — 2026-09-02. 54 numbered sources (S1–S54; ~34 verified by fetching primary PDF/HTML, remainder snippet-only and marked). WebSearch budget exhausted at 200/200 early in the run; Semantic Scholar API 429; arXiv API used for the final sweep. Sections Synthesis / Implications / Open questions written.

Method note: searches were run via WebSearch (queries logged under `### Search:` lines); primary sources fetched via WebFetch or `curl`+`pdftotext`. "Verified: fetched" means the primary PDF/HTML was read; "snippet-only" means only a search-engine snippet or an abstract page was seen.

## Sources

### Search: "podcast advertisement detection transcript paper arXiv"
Candidates: arxiv 2103.02585 (Reddy et al.), Melamed & Kim "Automatic detection of audio advertisements", arxiv 2110.07096 (Jing et al., introductions), arxiv 2004.04270 (Spotify Podcast Dataset), USPTO 12190871 patent.
### Search: "SponsorBlock dataset sponsor segment detection transformer YouTube paper"
Candidates: github xenova/sponsorblock-ml, cs230 DeepSponsorBlock report, anaselmhamdi medium (SkipSponsor), sciencedirect S2665963825000193 (Chan & Kok-Shun), github mtrentz/sponsorblock-analysis.
### Search: "\"host-read\" ad detection podcast machine learning"
Candidates: github heidonomm/AdDetection, github amsterg/Podcast-Ad-Detection, Show HN ZeroAds (news.ycombinator.com/item?id=45185650), USPTO 12190871, USPTO 11870949 (skip-based content detection).

### S1. Detecting Extraneous Content in Podcasts (Reddy, Yu, Pappu, Sivaraman, Rezapour, Jones; Spotify; EACL 2021) — https://arxiv.org/abs/2103.02585
- Type: paper
- Verified: fetched (PDF via curl + pdftotext)
- Key facts:
  - Task: sentence-level detection of "extraneous content" (EC: ads, promos of other podcasts, boilerplate) in episode descriptions and ASR transcripts drawn from the Spotify Podcast Dataset (105,360 episodes).
  - Annotation: manual, with doccano, on a random subset; sentence labelled extraneous if >50% of it is inside an annotated EC span. Boundaries "may start or end mid-sentence".
  - Silver labels from *listener retention dips*: aggregated listening data Jan–Sep 2020; dips located on the retention curve then manually checked. 38.4% of dips contained no EC (mostly episode intros listeners skip). For true-EC dips, mean absolute boundary error vs manual = 16.0 words (start), 35.2 words (end). Silver set: 6,401 dips across 4,930 episodes.
  - Models: BERT-base-cased, domain-adapted on the podcast corpus, single sentence vs sentence + preceding sentence; post-hoc smoothing / change-point / BiLSTM-CRF on top.
  - Results (Table 3, F1): transcripts (gold) BERT 0.710 single-sentence, 0.769 with context; descriptions 0.920 / 0.940. On transcripts precision (0.690) < recall (0.870) — "the model mistakenly identifies sentences" that merely sound promotional. Table 4 sentence accuracy on transcripts: 96.6% (BERT) → 97.0% (BERT + smoothing); document-level exact match 60.8% → 66.7%.
  - Downstream: removing EC before summarisation improved ROUGE-L; fine-tuned BART produced EC in 73.2% fewer cases when trained on cleaned data (approx., from text).
  - Code/data: no public release of the annotated set found in the paper text; listener data is proprietary.
- Relevance to AdVTT:
  - The only peer-reviewed podcast-specific ad/EC detector found. It is a *sentence-level encoder classifier*, not an LLM; the false-positive pattern (promotional-sounding content mislabelled) is exactly AdVTT's content_loss risk.
  - Boundary error of the silver labels (16–35 words) gives a calibration point: word-level precision needs an explicit refinement step, as AdVTT already does.
  - Confirms ~1-sentence context helps (+0.06 F1); AdVTT's 12-segment context is far larger than anything tested here.

### S2. Identifying Introductions in Podcast Episodes from Automatically Generated Transcripts (Jing, Schneck, Egan, Waterman; PodRecs @ RecSys 2021) — https://arxiv.org/abs/2110.07096
- Type: paper + dataset
- Verified: fetched (abs page + PDF)
- Key facts: 417 episodes, 20 topical categories, volunteers labelled start/end *words* of the episode introduction; 117 episodes triple-annotated — 72/117 perfect agreement on start, 41 majority, 4 none; 96.6% usable after majority vote. BERT token-labelling models vs static-embedding baseline; metrics = boundary accuracy and span "overlap score"; augmentation adds up to +3 pts accuracy. Split stratified by programme (seen/unseen programmes). Notes that "Music and advertisements may also appear before or after the introductions." Dataset published on Zenodo (link in abs comments).
- Relevance to AdVTT: closest public podcast dataset with *word-position* span labels on ASR transcripts; shows inter-annotator agreement on span edges in podcasts is imperfect even for humans — a ceiling for `boundary_err_sec`. Possible evaluation proxy for "PROGRAM/house intro" segment kind.

### S3. The Spotify Podcast Dataset (Clifton et al. 2020) — https://arxiv.org/abs/2004.04270 ; portal https://podcastsdataset.byspotify.com/
- Type: dataset
- Verified: abs fetched; portal fetch failed (DNS `ENOTFOUND` on 2026-09-01); discontinuation status snippet-only
- Key facts: ~100K English episodes, "over 47,000 hours of transcribed audio", Google Speech-to-Text transcripts with word-level timestamps (per S5). Search snippets state the dataset "is no longer maintained" and Spotify stopped taking access requests in December 2023 (snippet-only; portal unreachable).
- Relevance to AdVTT: the natural public benchmark for podcast segment work is effectively closed to new users; AdVTT cannot rely on it for a public evaluation set.

### S4. TREC 2020 Podcasts Track Overview (Jones et al.) — https://arxiv.org/abs/2103.15953
- Type: paper
- Verified: fetched (PDF)
- Key facts: >100,000 episodes, transcripts from Google Speech-to-Text API "as of early 2020"; tasks = 2-minute segment retrieval and summarisation; 15 teams; deep learning dominant. Summarisation participants removed "extraneous content such as boilerplate, ads, promotions" from descriptions; one run passed descriptions "through a model to detect and remove ads" (Spotify team, cf. S1). No ad-span labels were released.
- Relevance to AdVTT: confirms no TREC gold labels exist for ad spans; ad removal appeared only as preprocessing.

### S5. TREC 2021 Podcasts Track Overview — https://trec.nist.gov/pubs/trec30/papers/Overview-Pod.pdf
- Type: paper
- Verified: fetched (PDF via pdftotext)
- Key facts: same corpus; 2021 added audio-aware reranking criteria (Entertaining / Subjective / Discussion) and audio-clip summaries. Participation: 377 downloaded transcripts, 26 downloaded audio. "The provided transcripts have word-level timestamps." UCL submitted BM25 + audio-feature classifier runs. No advertisement task or labels.
- Relevance to AdVTT: no segment-type (ad/program) ground truth exists in TREC Podcasts; the corpus was transcript-centric.

### S6. xenova/sponsorblock-ml — https://github.com/xenova/sponsorblock-ml
- Type: repo
- Verified: fetched (README)
- Key facts: two-stage pipeline: T5 (t5-small … t5-11b) fine-tuned to *extract* candidate segments from YouTube transcripts, then a classifier assigns probability. Categories: sponsor, self/unpaid promotion, interaction reminder. Data: SponsorBlock DB (CC BY-NC-SA 4.0); transcripts pulled from YouTube. Pipeline: transcribe → preprocess/dedupe → generate segments → split → train transformer → train classifier. No metrics in README; code GPL-3.0; 148 commits.
- Relevance to AdVTT: a generative "extract the sponsor text" stage followed by classification mirrors AdVTT's "quote evidence then validate". The NC licence on SponsorBlock data blocks commercial training but not evaluation reporting.

### S7. DeepSponsorBlock: Detecting Sponsored Content in YouTube Videos (Stanford CS230, Fall 2020) — http://cs230.stanford.edu/projects_fall_2020/reports/55822706.pdf ; code https://github.com/DeepSponsorBlock/DeepSponsorBlock
- Type: paper (course report)
- Verified: fetched (PDF via pdftotext)
- Key facts: ~36,000 SponsorBlock video IDs with ≥5 upvotes; split 30,000/3,000/3,000; frames at 1 fps → 33.6M frames, ~1.5M positive; ResNet-50 frame baseline vs CNN-encoder/RNN-decoder predicting start/end frames. Metric: 1-D IoU. Test median IoU ≈0.69 (encoder-decoder) vs <0.2 (baseline). Of 16 sampled zero-IoU cases, half were due to "incorrect or incomplete SponsorBlock labels" (videos with multiple sponsors but one labelled). Cites NeuralBlock (BiLSTM on time-annotated transcripts, ">90%" accuracy) as prior art.
- Relevance to AdVTT: (i) SponsorBlock labels are noisy — ~50% of gross errors were label errors — so any SponsorBlock-derived benchmark needs cleaning; (ii) 1-D IoU is the segment metric used; (iii) vision-only detection is weak, transcript-based is the established route.

### S8. Leveraging ChatGPT for Sponsored Ad Detection and Keyword Extraction in YouTube Videos (Chan & Kok-Shun; arXiv 2502.15102; also IEEE 11024962 and Software Impacts vol. 24, June 2025) — https://arxiv.org/abs/2502.15102
- Type: paper
- Verified: fetched (arXiv PDF); Software Impacts page returned 403
- Key facts: 421 transcripts (243 auto-generated, 178 manual) from 623 videos on 6 educational channels; ad spans identified by prompt-engineered `gpt-4o-2024-08-06` ("RETURN A LIST OF DICTIONARIES…"); KeyBERT + GPT-4o for categories. Evaluation "was done by manually checking a small sample"; no precision/recall/F1 reported; authors state labels "are not validated by humans" and plan P/R/F1 in future work. Ads found in 45% (auto) / 57% (manual) of videos.
- Relevance to AdVTT: the only published LLM-transcript sponsor detector — and it has *no quantitative accuracy*. The transcript+LLM approach is therefore not "state of the art" in any measured sense in the literature; AdVTT's 4-fixture metrics already exceed what is published.

### S9. SkipSponsor / "Detecting sponsored content in YouTube videos" (El Mhamdi) — https://anaselmhamdi.medium.com/detecting-sponsored-content-in-youtube-videos-7701c113d81f ; Chrome store listing
- Type: blog + product
- Verified: snippet-only (medium returned 403)
- Key facts: model "trained on the transcripts of over 300,000 videos, annotated by the crowd-sourced dataset SponsorBlock" (snippet).
- Relevance to AdVTT: evidence that SponsorBlock supplies ≥300k transcript-aligned sponsor labels — the largest weak-label corpus for spoken sponsor reads; YouTube sponsor reads are stylistically close to host-read podcast ads.

### S10. nikals99/sponsorblock-net — https://github.com/nikals99/sponsorblock-net
- Type: repo
- Verified: fetched (README)
- Key facts: bag-of-words (NB, LR), BERT text classifier and frame-based video classifier; 70/20/10 split "that respects channel boundaries"; reports P/R/F1 and ROC in notebooks (numbers not in README); 24 commits.
- Relevance to AdVTT: channel-stratified splitting is the right protocol (S2 does the same by programme) — AdVTT fixtures should be split by show, never by episode.

### S11. labofsahil/sponsorblock-dataset (Hugging Face mirror) — https://huggingface.co/datasets/labofsahil/sponsorblock-dataset
- Type: dataset
- Verified: fetched
- Key facts: mirror of SponsorBlock CSV dumps (sponsorTimes, ratings, categoryVotes …); licence CC-BY-NC-4.0; HF viewer broken by heterogeneous CSV schemas; fields include videoID, startTime, endTime, category, votes.
- Relevance to AdVTT: raw material for a public *evaluation* set (NC licence) of spoken sponsor reads with timestamps; would need transcript alignment and vote-based cleaning (cf. S7).

### S12. heidonomm/AdDetection (Snackable.ai interview task) — https://github.com/heidonomm/AdDetection
- Type: repo
- Verified: fetched
- Key facts: sentence-level binary ad detection on podcast transcripts; GloVe-25 Twitter mean embeddings + K preceding sentences → 50-d vector; logistic regression precision ≈63%, recall ≈17%; Naive Bayes inverse trade-off. IOB-encoded data folder `ml_interview_ads_data` (size not stated).
- Relevance to AdVTT: shallow baselines fail badly on host-read ads; confirms the need for contextual models.

### S13. US Patent 12,190,871 "Deep learning-based automatic detection and labeling of dynamic advertisements in long-form audio content" — https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12190871
- Type: legal (patent)
- Verified: fetched (PDF is image-only; pdftotext returned 0 words) — details snippet-only
- Key facts (snippet): claims detection of dynamically inserted ads in long-form audio using transcript + audio, sentence embeddings and a "context of previous sentences"; motivates by DAI variability ("two audio files for the same content can have significant differences" in ad number/location).
- Relevance to AdVTT: prior-art awareness for a public release; also a reminder that DAI copies differ per download, so cached labels must be keyed to a specific audio file hash, not the episode GUID.

### S14. Automatic Detection of Audio Advertisements (Melamed & Kim, AT&T Labs; Interspeech 2009) — https://www.isca-archive.org/interspeech_2009/melamed09_interspeech.pdf ; patent US8606585B2
- Type: paper
- Verified: fetched (PDF via curl)
- Key facts: ads heard on hold in call-centre recordings; five methods incl. two baselines, a *Pitch Dynamics* method (ads show "long segments of emphatic stresses" = sharp F0 slopes), *word n-grams from ASR output*, and a combination; designed to need no per-ad references ("impractical for us to keep track of when new ads come out"); "much more accurate than a baseline HMM method". Explicitly rules out fingerprinting known ads for deployability.
- Relevance to AdVTT: the earliest text+prosody ad detector; pitch-dynamics cue is plausible for produced ads but *not* for host-read ads in the host's normal voice. The n-gram-from-ASR route is the ancestor of AdVTT's transcript approach.

### S15. Show HN: ZeroAds (Sept 2025) — https://news.ycombinator.com/item?id=45185650
- Type: forum / product
- Verified: fetched
- Key facts: Whisper transcription → LLM classifies segments → FFmpeg cuts → new RSS feed; claims "~90%+ on host reads/dynamic insertions/network promos in our tests"; known failures: sponsor mentions woven into content, brief bumpers, poor audio; "prioritizes avoiding content loss over aggressive cutting"; $5.99/mo. HN thread dominated by copyright/redistribution and incentive concerns.
- Relevance to AdVTT: the commercial state of practice is identical to AdVTT's architecture, with unpublished, unverifiable accuracy; AdVTT's measured metrics plus a metadata-only (non-redistributing) output are a differentiator, and the legal thread argues *for* emitting a sidecar track rather than cut audio.

### S16. MinusPod — https://github.com/ttlequals0/minuspod
- Type: repo
- Verified: fetched (README)
- Key facts: self-hosted; faster-whisper or remote Whisper API; LLM over transcript with sliding-window processing plus "an automatic verification pass"; *audio-side signals*: "loudness analysis, DAI transition detection, pre/post-roll, and a VAD-gap detector"; optional ad-reviewer LLM stage; "cross-episode pattern learning from your corrections, scoped podcast to network to global"; confidence scoring with review queue; categories sponsor, cross-promo, self-promo, interaction, opt-in intro/outro/recap; BYO LLM (Claude, Ollama, OpenRouter, OpenAI-compatible); MIT; 379 stars; 1,342 commits; last update 2026-08-31 (search snippet).
- Relevance to AdVTT: the most complete open-source competitor. Ideas AdVTT lacks: loudness/DAI-transition cues fused with the LLM, corrections that feed a per-show/network pattern memory, and a taxonomy that includes cross-promo/interaction reminders (SponsorBlock-style). AdVTT's vocabulary v0.1 has no "interaction"/"self-promo" split.

### S17. jdcb4/podcast-ad-remover — https://github.com/jdcb4/podcast-ad-remover
- Type: repo
- Verified: fetched (README)
- Key facts: whisper/faster-whisper local; LLM via Gemini (recommended), OpenAI, Anthropic, OpenRouter or OpenAI-compatible endpoints with cascading fallback; removes "ads, promo, intro, and outro"; outputs rewritten RSS; MIT; 267 commits; no accuracy or false-positive discussion.
- Relevance to AdVTT: second open-source LLM-over-Whisper remover; none of these projects publish metrics — a public benchmark from AdVTT would be novel.

### S18. Adblock Radio (Alexandre Storelli, 2018–2019) — https://github.com/adblockradio/adblockradio
- Type: repo / product
- Verified: snippet-only (search results; repo described as archived)
- Key facts: live-radio ad blocker; time-frequency CNN classifies chunks as speech/music/ad from spectral features, plus Shazam-like fingerprint matcher against a crowdsourced ad/jingle DB; core engine open source; repository archived.
- Relevance to AdVTT: acoustic-only classification works for *produced* radio spots (music beds, compression, jingles) and is the right tool for DAI network spots; it has nothing to key on for host-read reads in the host's own voice.

### Search: "TV commercial detection audio fingerprint repeated commercials shot boundary black frame survey"; "Lienhart commercial detection 1997 TRECVID …"; "Duygulu Chen Hauptmann 2004 commercial detection …"
Candidates: Lienhart, Kuhmünch & Effelsberg ICMCS 1997; Duygulu, Chen & Hauptmann ICME 2004; Sadlier/O'Connor "Audio and Video Processing for Automatic TV Advertisement Detection"; Fusing audio-visual fingerprint (Computers & Electrical Eng. 2011); patents US20170070774A1, US9258604; IJACSA "Unsupervised Ads Detection in TV Transmissions".

### S19. Classic TV commercial detection (Lienhart et al. 1997; Duygulu, Chen & Hauptmann ICME 2004; audio-visual fingerprint fusion; IJACSA 2018 "Unsupervised Ads Detection in TV Transmissions") — https://thesai.org/Downloads/Volume9No4/Paper_53-Unsupervised_Ads_Detection_in_TV_Transmissions.pdf (fetched); others snippet-only
- Type: paper(s)
- Verified: IJACSA PDF fetched; Lienhart/Duygulu/fingerprint papers snippet-only
- Key facts:
  - Lienhart 1997 uses "black frames, scene cuts and a measure of motion"; commercial breaks show "restricted temporal length, a high cut frequency … delimiting black frames and silences" (snippets).
  - Duygulu/Chen/Hauptmann 2004: two cues — "repetitive use of commercials over time" and distinctive colour/audio features; acoustic matches validated by the visual channel (snippet).
  - Repetition/fingerprint detectors ran over "10+ TV channels over more than 4 years"; known false-positive class: repeated programme signature tunes (snippet, patent US20170070774A1).
  - IJACSA 2018 (fetched): for channels that do not use black frames, uses *absence of the channel logo* and *repetition threshold* over key-frame histograms; notes "there was no real silence present in between ads" and silence blocks occur *inside* ads; surveys prior results in the 80–99% P/R range on TV.
  - No TRECVID *commercial-detection* task was found; TRECVID references in this literature are to shot-boundary detection only (gap noted).
- Relevance to AdVTT: of the classic cues — black frames, cut rate, logo absence, silence, duration prior, repetition/fingerprint — only **duration prior** and **cross-episode repetition of the same read** transfer to host-read podcast ads. Silence/loudness cues transfer only to DAI splice points. Repetition detection (same sponsor copy across episodes of one show) is a strong, cheap, LLM-free signal AdVTT does not yet use (MinusPod S16 does a version of it).

### Search: "Spotify Podcast Dataset TREC Podcasts Track 2021 segment retrieval advertisement"; "\"Segment Any Text\" 2024 …"; "topic segmentation podcast transcripts neural TextTiling Pk WindowDiff LLM 2024 2025"; "automatic podcast chapter generation LLM transcript chapterization paper 2024 2025"
Candidates: trec.nist.gov Overview-Pod.pdf (2021), arxiv 2103.15953 (2020), aclanthology 2024.emnlp-main.665 / arxiv 2406.16678 (SaT), webis thesis chaitanya-valaboju_2025, arxiv 2601.02128, arxiv 2605.30668 (CobSeg), github bmmidei/SliceCast, arxiv 2410.16148 (PODTILE), arxiv 2504.00072 (Chapter-Llama), arxiv 2505.23908 (podcast preview generation).

### S20. Segment Any Text (SaT) — Frohmann, Sterner, Vulić, Minixhofer, Schedl; EMNLP 2024 — https://arxiv.org/abs/2406.16678 ; code https://github.com/segment-any-text/wtpsplit
- Type: paper + repo
- Verified: fetched (abs)
- Key facts: sentence segmentation with "a new pretraining scheme that ensures less reliance on punctuation"; 85 languages, no language code needed; "threefold gain in speed over the previous state of the art"; "outperforms all baselines - including strong LLMs - across 8 corpora"; strongest gains on lyrics/legal (poorly punctuated); MIT licence; LoRA domain adaptation supported.
- Relevance to AdVTT: ASR output (esp. parakeet/whisper without punctuation) is exactly SaT's target; using SaT to define the *segment units* the LLM indexes would make indices stable across STT backends and reduce mid-sentence spans (S1 notes ads start/end mid-sentence).

### S21. Topic Segmentation using Large Language Models (Valaboju, MSc thesis, Webis/Leipzig 2025) — https://downloads.webis.de/theses/papers/chaitanya-valaboju_2025.pdf
- Type: paper (thesis)
- Verified: fetched (PDF via pdftotext)
- Key facts: podcast transcripts, manually annotated; three methods — TextTiling baseline, "LLM-based similarity thresholding" (llama3-8b-8192 extracts ≤5 topics, sentences embedded and assigned by cosine similarity, threshold ≈0.4 optimal), and DistilBERT+CRF BIO tagging on 20-sentence chunks with LOOCV. Metrics F1, Pk, WindowDiff. TextTiling: F1 0.53, Pk 0.44, WD 0.45 (Table 4.1; other rows not captured). Reproduction of Xing et al. neural segmenter failed (WD 0.4718 reproduced vs 0.282 reported).
- Relevance to AdVTT: LLM used *not* to emit boundaries directly but to produce topic labels used by an embedding similarity pass — an alternative to index-emitting prompts. Also a caution that published neural-segmentation numbers on conversational data may not reproduce.

### S22. PODTILE: Facilitating Podcast Episode Browsing with Auto-generated Chapters (Spotify; CIKM 2024) — https://arxiv.org/abs/2410.16148
- Type: paper
- Verified: fetched (HTML + PDF)
- Key facts: LongT5 (~220M params) seq2seq; transcripts average ~16,000 tokens → chunks of 8,000 words (7,000 text + 1,000 static/dynamic context); avg 1.75 chunks/episode. Input is augmented "by adding index numbers" to sentences; output format `${first_sentence_index} := ${title}` separated by `||`; a chunk with no boundary outputs a fixed "No chapter boundaries were found." Dynamic context = titles predicted in earlier chunks. Data: 10,800 episodes with creator chapters (8k/1k/1k). Boundary metric: WindowDiff. GPT-4 zero-shot (gpt-4-0125-preview, 128k, May 2024) WinDiff 0.448, ROUGE-L 0.134 vs PODTILE ROUGE-L 0.231. Deployed April 2024: +88.12% chapter-initiated plays. Inference ≈1 h per 1,100 episodes. No ad handling discussed.
- Relevance to AdVTT: production-grade evidence for AdVTT's exact design pattern — sentence-index-emitting output over overlapping chunks with carried-forward context — from Spotify at scale; and evidence that a small fine-tuned encoder-decoder beat zero-shot GPT-4 on boundary placement. The "empty-is-valid" fixed string is also standard practice.

### S23. Chapter-Llama: Efficient Chaptering in Hour-Long Videos with LLMs (2025) — https://arxiv.org/abs/2504.00072
- Type: paper
- Verified: fetched (HTML)
- Key facts: ASR segments are prepended with "HH:MM:SS" start times; the LLM emits chapters as text "a timestamp in HH:MM:SS format followed by a free-form chapter title"; trained on ~20k VidChapters-7M videos; metrics F1 averaged over IoU 0.5–0.95 and mean tIoU; 45.3 vs 26.7 F1 over Vid2Seq; long videos handled by "iterative prediction" over ~1-hour windows.
- Relevance to AdVTT: an alternative to sentence indices — inline timestamps as tokens the model copies back. Copying a timestamp that is literally present in the input is a "quote" operation, which S31/S32 suggest LLMs do more reliably than computing offsets.

### S24. Towards Multi-Level Transcript Segmentation: LoRA Fine-Tuning for Table-of-Contents Generation (2026) — https://arxiv.org/abs/2601.02128
- Type: paper
- Verified: fetched (HTML)
- Key facts: AMI (139 meetings, 73 h), Videoaula (34 lectures), LectureDE (96 lectures); baselines TextTiling+BERT, MiniSeg, CS-BERT, SegmentLLM; LoRA-tuned Mistral Nemo / Qwen2.5; metrics F1 and Fournier's boundary similarity B (extended hierarchically); adding *pause duration* helped fine-tuned models (best 30.34 F1 on AMI) but "degraded zero-shot performance".
- Relevance to AdVTT: (i) acoustic pause features help *trained* segmenters but hurt prompted LLMs — so fuse audio cues in a post-LLM validator, not in the prompt; (ii) boundary similarity B is the modern replacement for Pk/WindowDiff.

### Search: "Lost in the Middle Liu 2023 …"; "RULER benchmark long-context needle in a haystack Hsieh 2024 …"; "LLM line number reference errors … span extraction"; "LLM attributed extraction quote grounding verbatim citation …"; "chunking overlap context window long document LLM extraction sliding window …"; "aider edit format line numbers unreliable …"
Candidates: arxiv 2307.03172, 2404.06654, 2410.01985 (Lost-in-Distance), 2406.16008 (Found in the Middle), 2403.11802 (Counting-Stars), 2608.21237, micro1.ai LongExtractionBench, 2606.00898, mattyyeung.github.io/deterministic-quoting, aclanthology 2024.findings-acl.838, 2503.17952 (SLIDE), 2602.23370, aider.chat/docs/unified-diffs.html, github anthropics/claude-code issue 25775 (hashline).

### S25. Lost in the Middle: How Language Models Use Long Contexts (Liu et al., 2023; TACL 2024) — https://arxiv.org/abs/2307.03172
- Type: paper
- Verified: fetched (PDF)
- Key facts: multi-document QA and synthetic key-value retrieval; models MPT-30B-Instruct, LongChat-13B (16K), GPT-3.5-Turbo (incl. 16K), Claude-1.3; "U-shaped performance curve" — primacy and recency bias; with the answer document in the middle of 20 documents GPT-3.5-Turbo falls *below its closed-book* accuracy (56.1%); encoder-decoder models are robust only within training length; even base models show the U-shape; query-aware contextualisation (query before and after) helps key-value retrieval.
- Relevance to AdVTT: explains the measured whole-episode failure ("right text, wrong segment index") and justifies chunking. Suggests placing the task instruction both before and after the transcript chunk, and keeping the *target* window short relative to read-only context.

### S26. RULER: What's the Real Context Size of Your Long-Context Language Models? (Hsieh et al., 2024) — https://arxiv.org/abs/2404.06654
- Type: paper / benchmark
- Verified: fetched (abs)
- Key facts: 13 synthetic tasks (NIAH variants, multi-hop tracing, aggregation, QA), configurable length 4K–128K; 17 models evaluated; "only half of them can maintain satisfactory performance at the length of 32K" despite claiming ≥32K; effective context length is well below the advertised window.
- Relevance to AdVTT: supports keeping LLM windows at or below ~8K tokens (AdVTT: ~6K + context) even for models advertising 128K–1M; "effective context" should be measured per backend (Ollama/MLX models especially).

### S27. NoLiMa: Long-Context Evaluation Beyond Literal Matching (Modarressi et al., 2025) — https://arxiv.org/abs/2502.05167
- Type: paper / benchmark
- Verified: fetched (abs via curl; lead supplied by coordinator)
- Key facts: NIAH variant where needle and question share minimal lexical overlap; 13 models claiming ≥128K; "At 32K … 11 models drop below 50% of their strong short-length baselines"; GPT-4o falls from 99.3% to 69.7%; CoT/reasoning does not rescue long contexts; attention struggles "when literal matches are absent".
- Relevance to AdVTT: ad detection is *not* a literal-match task (no keyword marks an ad), so it is in the regime where degradation is steepest; this is the strongest published argument for small windows and for turning the task into a literal-match one where possible (e.g., a second pass that verifies a quoted string).

### S28. Classifier Context Rot: Monitor Performance Degrades with Context Length (2026) — https://arxiv.org/abs/2605.12366
- Type: paper
- Verified: fetched (abs via curl; lead supplied by coordinator)
- Key facts: frontier models used as classifiers over long agent transcripts (Opus 4.6, GPT 5.4, Gemini 3.1) "miss these actions 2× to 30× more often when they occur after 800K tokens of benign activity than when they occur on their own"; partial mitigation via "periodic reminders throughout the transcript"; evaluations ignoring long-context degradation "overestimating monitor performance".
- Relevance to AdVTT: directly analogous — an ad late in a long benign transcript is a rare event in a long context; recall collapses with context length. Periodic re-injection of the instruction (or per-chunk instruction, as AdVTT does) is the published mitigation. AdVTT's `ad_recall_sec` fixtures should include long episodes with a single late midroll.

### S29. LongExtractionBench (micro1, 2026) — https://www.micro1.ai/benchmark/long-extraction
- Type: benchmark (vendor)
- Verified: fetched
- Key facts: 225 documents averaging 358 pages and ~88,700 ground-truth fields; frontier LLMs completed fewer documents than dedicated extractors (Claude 116/225, Gemini 112/225, GPT-5.5 198/225) due to "context overflow, output truncation, and page limits", not per-item accuracy; "row matching is key-based, never positional"; "Recall is the greatest differentiator."
- Relevance to AdVTT: (i) output-truncation and completion failures, not judgement, dominate long-input extraction — parse failures should be counted as recall loss in AdVTT metrics; (ii) a benchmark author explicitly refuses positional matching in favour of key-based matching — the same lesson as evidence-quote matching over indices.

### S30. Indexing Long Documents for LLM-Based Analysis (Pham & Ma, 2026) — https://arxiv.org/abs/2608.21237
- Type: paper
- Verified: fetched (HTML)
- Key facts: "as the input grows, the model fabricates answers more often at a rate that climbs steeply with context length"; hierarchical plain-text index (B+-tree-like) with leaf links back to source spans; 55.9% judge accuracy vs 52.9% full-document baseline and 43.7% GraphRAG; ~40% fewer tokens than DocETL (3.9K vs 41K tokens per question).
- Relevance to AdVTT: an episode-level index (sponsor names, section titles) built once could route a cheap second pass; less directly applicable than S22's chunk-with-carried-context.

### S31. Unified diffs make GPT-4 Turbo 3× less lazy (aider, Dec 2023) — https://aider.chat/docs/unified-diffs.html ; hashline proposal https://github.com/anthropics/claude-code/issues/25775
- Type: blog (engineering report) + issue
- Verified: snippet-only (WebFetch rate-limited at time of first attempt; see later entry if re-fetched)
- Key facts (snippets): "GPT is terrible at working with source code line numbers"; aider deliberately avoids "brittle specifiers like line numbers or line counts"; SEARCH/REPLACE format scored 20% vs unified-diff 61% for GPT-4 Turbo on aider's editing benchmark. A 2026 comparison (hashline) reports content-hash-anchored line addressing "matched or beat search/replace for every model tested" across 16 models × 180 tasks.
- Relevance to AdVTT: the most practical evidence on *indices vs quotes*: code-editing tools converged on anchoring edits to *verbatim text* rather than line numbers because LLMs miscount. AdVTT's "index + verbatim quote from the first line" is already the hybrid; the hashline result suggests a third option — give every segment a short opaque ID (hash-like) that the model must copy, which is a literal-match operation (cf. S27) rather than arithmetic.

### S32. Deterministic Quoting: Making LLMs Safer for Healthcare (Yeung, Apr 2024) — https://mattyyeung.github.io/deterministic-quoting
- Type: blog (method report)
- Verified: fetched
- Key facts: LLM emits *reference IDs* inside tags; a deterministic lookup substitutes the verbatim source text, so quoted material "has never passed through an LLM". N=60 evaluation: 0% hallucination inside quotes, 2% outside (vs 12% baseline), relevance 92% vs 90%.
- Relevance to AdVTT: formalises the "point, don't paraphrase" principle — have the model return segment IDs and let code resolve the verbatim text and timestamps; the model-produced quote then becomes a *cross-check* rather than the source of truth.

### S33. Citation Grounding Measures the Oracle (2026) — https://arxiv.org/abs/2606.00898
- Type: paper
- Verified: fetched (abs)
- Key facts: hallucination rates measured by checking citations against a database depend on database completeness: same outputs scored 0.791–0.855 on a 470k-record oracle vs 0.989–0.999 on a 330M-record one; sparse oracle gave "100% false-positive rate" on independent check.
- Relevance to AdVTT: the verbatim-quote validator is only as reliable as the transcript it is matched against — STT normalisation differences (numbers, punctuation, disfluencies) will produce false "quote mismatch" demotions; measure the mismatch rate per STT backend before halving confidence on it.

### S34. Sliding-window / overlap chunking for extraction (SLIDE, arXiv 2503.17952; "Toward General Semantic Chunking…", arXiv 2602.23370) — https://arxiv.org/abs/2503.17952 ; https://arxiv.org/abs/2602.23370
- Type: paper(s)
- Verified: snippet-only
- Key facts (snippets): SLIDE gives each chunk context from neighbouring chunks (window 10 → 5 before/after) and reports +24% entity / +39% relation extraction in English; the semantic-chunking paper keeps "a fixed overlap ratio (about 10%) to avoid unstable predictions when a potential boundary lies near a window edge".
- Relevance to AdVTT: independent confirmation of the "read-only context either side" design and of the boundary-near-window-edge hazard; suggests measuring boundary error as a function of distance from the window edge.

### Search: "LLM confidence calibration verbalized confidence \"just ask for calibration\" 2023"; "\"verbalized confidence\" prompt template near-constant regardless of accuracy LLM paper 2024 2025"
Candidates: aclanthology 2023.emnlp-main.330 (Tian et al.), arxiv 2306.13063 (Xiong et al.), arxiv 2601.07767, ICLR 2025 "Do LLMs estimate uncertainty well in instruction-following", arxiv 2406.13415, arxiv 2510.12587, arxiv 2503.00172 (survey).

### S35. Just Ask for Calibration (Tian, Mitchell, Zhou, Sharma, Rafailov, Yao, Finn, Manning; EMNLP 2023) — https://aclanthology.org/2023.emnlp-main.330/
- Type: paper
- Verified: fetched (abs)
- Key facts: for RLHF models (ChatGPT, GPT-4, Claude) "verbalized confidences emitted as output tokens are typically better-calibrated than the model's conditional probabilities", "often reducing the expected calibration error by a relative 50%" on TriviaQA, SciQ, TruthfulQA.
- Relevance to AdVTT: supports asking for a numeric confidence per span (as AdVTT does) over using logprobs — for API models where logprobs are unavailable anyway.

### S36. Can LLMs Express Their Uncertainty? (Xiong et al., 2023; ICLR 2024) — https://arxiv.org/abs/2306.13063
- Type: paper
- Verified: fetched (abs)
- Key facts: LLMs "tend to be overconfident, potentially imitating human patterns"; failure-prediction AUROC only 0.522–0.605; sampling/aggregation help modestly; "none of these techniques consistently outperform others".
- Relevance to AdVTT: a raw verbalised confidence is weakly discriminative; AdVTT's confidence should be *composed* from validator outcomes (quote match, duration, dialogue density, cross-episode repetition) with the LLM number as one feature, and re-calibrated on fixtures (isotonic/Platt) before being exposed in the VTT payload.

### S37. Are LLM Decisions Faithful to Verbal Confidence? (2026) — https://arxiv.org/abs/2601.07767
- Type: paper
- Verified: fetched (abs)
- Key facts: models are "neither cost-aware when articulating their verbal confidence, nor strategically responsive" under high-penalty conditions; they almost never abstain even when abstention is optimal ("utility collapse").
- Relevance to AdVTT: do not expect the model to honour the false-positive asymmetry by itself; the asymmetric cost must be enforced by thresholds in code (which AdVTT's ladder does).

### S38. Reasoning's Razor (2025) — https://arxiv.org/abs/2510.21049
- Type: paper
- Verified: fetched (abs via curl; lead supplied by coordinator)
- Key facts: classification under strict low-FPR regimes (safety, hallucination detection); "Think On … improves overall accuracy, but underperforms at the low-FPR thresholds"; "Think Off … dominates in these precision-sensitive regimes"; "token-based scoring substantially outperforms self-verbalized confidence for precision-sensitive deployments"; ensemble of both modes recovers strengths.
- Relevance to AdVTT: AdVTT operates at a low-FPR point (content_loss ≤ 5 s). Evidence that (a) reasoning/thinking modes may *hurt* at that operating point, (b) logprob/token scoring beats verbalised confidence where available (local MLX/Ollama, OpenAI logprobs), (c) a no-think + think ensemble is a cheap gain. Contradicts S35 partially — S35 measured average calibration, S38 the low-FPR tail, which is what matters here.

### Search: "LLM data annotation distillation train small BERT token classification cost accuracy 2024 2025"; "LLM label distillation encoder sequence labeling weak supervision GPT-4 teacher DeBERTa student"; "ModernBERT token classification distillation …"
Candidates: arxiv 2406.17633, 2504.15432, 2504.15022, 2503.03261, researchgate "LLM on a Budget: Active Knowledge Distillation", arxiv 2302.05454, 2501.12332, mdpi 2076-3417/16/8/3632 (Kazakh sequence labelling), philschmid ModernBERT fine-tune, arxiv 2502.17125 (LettuceDetect), vLLM blog HaluGate (ModernBERT token classifier).

### S39. Knowledge Distillation in Automated Annotation: Supervised Text Classification with LLM-Generated Training Labels (Pangakis & Wolken, 2024) — https://arxiv.org/abs/2406.17633
- Type: paper
- Verified: fetched (PDF)
- Key facts: 14 real computational-social-science classification tasks (post-contamination corpora); students BERT/RoBERTa/DistilBERT trained on 1,000 GPT-4 labels vs 1,000 or 250 human labels. Median F1 gap human-vs-GPT-4-trained "is only 0.039". Table 1 medians: BERT human-1000 F1 0.62 (P 0.71, R 0.54); BERT GPT-4-1000 F1 0.59 (P 0.50, R 0.74); GPT-4 few-shot F1 0.59 (P 0.51, R 0.80). Students on GPT labels are *recall-heavy, precision-light* (precision 0.214 lower than human-trained BERT). Labelling 6.2M tweets with GPT-4 estimated at "nearly $9,000".
- Relevance to AdVTT: distillation to a small encoder is viable at near-teacher F1 — but the inherited error is *over-prediction* (low precision), the wrong direction for AdVTT's asymmetry; the student must be thresholded/calibrated for precision and trained on validator-filtered (not raw) LLM labels.

### S40. Feeding LLM Annotations to BERT Classifiers at Your Own Risk (Lu & Smith, 2025) — https://arxiv.org/abs/2504.15432
- Type: paper
- Verified: fetched (PDF)
- Key facts: roberta-base students on LLM (3B/7B) labels vs gold across four datasets; on one dataset 3B labels give 66.05% vs 96.26% gold accuracy, 7B labels 92.74%; systematic (non-random) error propagation → premature plateaus; prediction instability: Krippendorff's α 84.30 (gold) → 52.72 (3B labels); entropy filtering and consistency ensembles "recover only 60–75% of the gold-label performance gap" and do not fix instability.
- Relevance to AdVTT: small local LLMs are poor teachers; if AdVTT distils, use the strongest teacher plus validator filtering, keep a human-gold test set, and expect run-to-run instability — pin seeds and ensemble checkpoints.

### S41. LLM-assisted weak supervision for sequence labelling (MDPI Applied Sciences 16(8):3632, 2026, Kazakh NER) — https://www.mdpi.com/2076-3417/16/8/3632
- Type: paper
- Verified: snippet-only (403 on fetch)
- Key facts (snippet): LLM as candidate span generator with "schema-constrained prompting, self-consistency confidence, threshold-based filtering, and CRF decoding" before training a student tagger.
- Relevance to AdVTT: a template for turning LLM span labels into token-level training data: self-consistency (multiple samples) → confidence → threshold → CRF-smoothed spans.

### S42. HaluGate: token-level hallucination detection with ModernBERT (vLLM blog, Dec 2025) and LettuceDetect (arXiv 2502.17125) — https://blog.vllm.ai/2025/12/14/halugate.html ; https://arxiv.org/abs/2502.17125
- Type: blog + paper
- Verified: snippet-only
- Key facts (snippets): ModernBERT (8,192-token context) fine-tuned with a token-classification head labels each token supported/unsupported; inputs built as context + question + answer up to 4,096 tokens; deployed as a real-time gate.
- Relevance to AdVTT: ModernBERT's 8K context fits a whole AdVTT window; a token-classification "ad/not-ad" head trained on validated LLM spans is the concrete distillation target, runnable on CPU/Apple Silicon at near-zero marginal cost.

### Search: "\"sponsored content\" OR \"advertorial\" OR \"promotional\" text detection classifier native advertising NLP paper"; "Touché 2025 Advertisement in Retrieval-Augmented Generation task overview detection results"
Candidates: arxiv 2509.14256 (JU-NLP), PMC12181363 / Nature Sci Data s41597-024-04341-6 (Electronic News Dataset for Native Advertisement Detection), IEEE 9902953, touche.webis.de task pages (clef25, clef26), zenodo 14699130 and 15270283, ceur-ws Vol-4038 papers 378/379/382/384, Schmidt et al. WWW'24 "Detecting Generated Native Ads in Conversational Search".

### S43. Touché 2025 Task 4 — Advertisement in Retrieval-Augmented Generation (overview slides; Heineking, Zelch, Potthast, Hagen) — https://touche.webis.de/clef25/touche25-organization/touche25-task4-overview.pdf ; task page https://touche.webis.de/clef25/touche25-web/advertisement-detection.html ; data https://zenodo.org/records/15270283
- Type: benchmark / dataset
- Verified: fetched (PDF slides; zenodo record)
- Key facts: Webis Generated Native Ads 2024: "17k generated responses, 6k with inserted advertisements" (CC BY 4.0; from Schmidt et al., WWW '24). Sub-task 2 (detection): 6,748 private test responses (2,055 with ads, 4,693 without), scored by F1; 4 teams, 17 runs, mostly fine-tuned encoders. Sub-task 1 (generation) scored by the FNR of a fine-tuned `modernbert-embed-base` classifier ("Evasion Score"); best evasion 0.279 (JU-NLP ORPO Mistral-7B) — i.e., the encoder still caught 72% of adversarially hidden ads with precision 1.000. JU-NLP notebook (arXiv 2509.14256, fetched): DeBERTa-v3-base F1 0.773 (P 0.788, R 0.758); CrossEncoder P 0.977 / R 0.346.
- Relevance to AdVTT: the only active shared task on *native/covert* ad detection in text. Its 2025 conclusion — fine-tuned encoders detect even adversarially embedded ads with high precision — is evidence that an encoder classifier over transcript text is competitive for the "PROMOTION woven into content" case AdVTT struggles with (S15).

### S44. Touché 2026 — Advertisement in RAG (adds span identification) — https://touche.webis.de/clef26/touche26-web/advertisement-detection.html
- Type: benchmark
- Verified: fetched
- Key facts: three sub-tasks: (1) classify ad presence — top F1 0.985 (zhaw CompactQueryClassifier); (2) identify "exact character spans of ads" — "adapted F1-score based on span overlap", baseline MiniLM 0.697; (3) remove ads preserving fluency (human 0–3 + LLM 0–1 scoring). Dataset: Webis Generated Native Ads 2025 with advertiser name, product and character-level span annotations. Run deadline 21 May 2026. No spoken/podcast content.
- Relevance to AdVTT: the closest public *span-level* benchmark for promotional text; span-overlap F1 is its metric. AdVTT could evaluate its text-side classifier here (text only, no timing) and borrow the advertiser/product annotation schema for its `advertiser` field.

### S45. Electronic News Dataset for Native Advertisement Detection (Scientific Data, 2024/2025) — https://www.nature.com/articles/s41597-024-04341-6 ; PMC12181363
- Type: dataset
- Verified: snippet-only (Nature redirected to IdP; PMC not yet fetched)
- Key facts (snippets): labelled electronic-news articles for native-ad vs editorial detection; companion IEEE paper compares BERT/GloVe/FastText embeddings with BiLSTM/CNN/LSTM.
- Relevance to AdVTT: written-text native-ad corpus; useful for pre-training a promotional-language encoder but stylistically far from spoken host reads.

### Search: "pyannote.metrics diarization purity coverage segmentation boundary tolerance metrics paper"; "temporal action localization evaluation mAP tIoU vs frame-level metrics …"; "Fournier 2013 boundary similarity segmentation evaluation Pk WindowDiff critique near-miss"
Candidates: isca-archive bredin17_interspeech.pdf, pyannote.github.io/pyannote-metrics reference, aclanthology P13-1167 (Fournier 2013), segeval.readthedocs.io, LREC 2014 931_Paper.pdf, arxiv 1902.05488, HACS challenge page, "Temporal Action Segmentation: An Analysis of Modern Techniques".

### S46. pyannote.metrics: a toolkit for reproducible evaluation, diagnostic, and error analysis of speaker diarization systems (Bredin, Interspeech 2017) — https://www.isca-archive.org/interspeech_2017/bredin17_interspeech.pdf ; docs https://pyannote.github.io/pyannote-metrics/reference.html
- Type: paper + library
- Verified: fetched (PDF)
- Key facts: detection metrics on *durations*: detection error rate = (false alarm + missed detection) / total, where false alarm is "the duration of non-speech incorrectly classified as speech" and missed detection the dual; both components are reported separately. Segmentation: boundary precision/recall need a tolerance and "very sensitive to the tolerance parameter"; segment purity/coverage are tolerance-free duals (over-segmentation → high purity, low coverage). Collar convention: "remove from evaluation a 500ms collar around each speaker turn boundary (250ms before and after)". DER = (FA + miss + confusion) / total.
- Relevance to AdVTT: `content_loss_sec` is exactly pyannote's *false-alarm duration* (un-normalised) and `ad_recall_sec` maps to 1 − missed-detection rate; reporting them as the two DER components (with an explicit collar) puts AdVTT's metrics in a recognised framework. pyannote.metrics can compute them from RTTM/Annotation objects directly.

### S47. Evaluating Text Segmentation using Boundary Edit Distance (Fournier, ACL 2013) + SegEval — https://aclanthology.org/P13-1167.pdf ; https://segeval.readthedocs.io/
- Type: paper + library
- Verified: fetched (PDF)
- Key facts: Pk and WindowDiff "under-penalize errors at the beginning" and are "biased towards segmentations containing few or tightly clustered boundaries"; boundary edit distance models full misses as add/delete and near misses as n-wise transpositions (default n_t = 2 units); Boundary Similarity B = 1 − normalised edit cost; supports inter-coder agreement (κ, π) for segmentation. SegEval recommends B over Pk/WD.
- Relevance to AdVTT: if AdVTT ever reports boundary quality as a single number, B with a time-based transposition span (e.g., 3 s) is the defensible choice; more importantly, B's inter-coder coefficients allow AdVTT to report *annotator agreement* on its fixtures (S2 shows this is non-trivial).

### S48. Temporal action localisation / segmentation metrics (survey snippets) — e.g. https://arxiv.org/abs/1902.05488 ; HACS challenge http://hacs.csail.mit.edu/challenge.html
- Type: paper(s)
- Verified: snippet-only
- Key facts (snippets): segment-level mAP at tIoU thresholds {0.3…0.7} (THUMOS-14) or 0.5:0.05:0.95 (ActivityNet/HACS); frame-level metrics (MoF, per-frame P/R/F1) obtained by rasterising segments to a label sequence; segmentation adds edit score and F1@{10,25,50}% overlap.
- Relevance to AdVTT: no source in this survey uses an asymmetric duration-cost metric; the closest precedents are pyannote's separated FA/miss durations (S46) and the low-FPR operating-point framing of S38. AdVTT's `content_loss_sec` is therefore unusual but easily expressed as "false-alarm seconds at a fixed operating point" — a documented gap and an opportunity to define it publicly.

### S14 (addendum, 2026-09-02). Melamed & Kim 2009 — Table 1 (5-fold CV, P / R / F1): 2-state HMM .38/.90/.54; 3-state HMM .42/.89/.57; pitch dynamics .75/.93/.83; ASR word n-grams .85/.93/.89; combined .92/.93/.92 ("error rate … 81% lower than that of the best" baseline). Data: 100 annotated customer-service calls of 5–20 min, 6 kHz audio, one annotator. Note: the n-gram method works because *the same ads recur* across calls ("ads can be detected as frequently occurring" n-grams) — i.e., it is a repetition detector on text, which transfers directly to recurring host-read copy across a show's episodes.

### S31 (addendum, 2026-09-02) — now Verified: fetched. Exact figures: gpt-4-1106-preview scored 20% with SEARCH/REPLACE and 61% with unified diffs (lazy comments 12/89 vs 4/89 tasks); the format "omit line numbers entirely from diff hunks" and treats hunks as content-anchored search/replace. Quote: "GPT is terrible at working with source code line numbers." The hashline claim remains snippet-only.

### Gap notes (2026-09-02)
- Semantic Scholar Graph API returned HTTP 429 (rate limit, no key) on three attempts; no Semantic Scholar sweep was possible. Google Scholar not fetchable. arXiv API used instead (see next Search entry).
- PMC12181363 (Electronic News native-ad dataset) served a reCAPTCHA; Nature redirected to an IdP; dl.acm.org (Schmidt et al. WWW'24) returned 403; ScienceDirect (Software Impacts) 403; medium.com 403; MDPI 403. Those five remain snippet-only.
- No paper was found that (a) evaluates an *LLM* on podcast ad-span detection with published precision/recall, or (b) publishes a public, timestamped, human-labelled podcast ad dataset. Both are documented gaps.

### Search (arXiv API, 2026-09-02): all:podcast AND (advertisement|advertising|sponsorship|sponsor); all:SponsorBlock OR (sponsored AND segments AND YouTube); (commercial|advertisement) AND detection AND (broadcast|radio) AND audio; "topic segmentation" AND transcripts AND LLM
Candidates not previously logged: 2601.02306 (Cold-Starting Podcast Ads and Promotions… Spotify, 2026-01), 2506.18735 (Audio-centric Multi-task Learning for Streaming Ads Targeting on Spotify, 2025-06), 2608.19165 (ChildSafeAds Shared Task 2026: Commercial Content in Child-Facing YouTube Videos, 2026-08), 1811.02411 (audio-only advertisement detection in broadcast TV, 2018-11), 2403.03538 (RADIA — Radio Advertisement Detection with Intelligent Analytics, 2024-03), 1806.08612 (Ad-Net audio-visual CNN, 2018-06), 1507.01209 (TV news commercials, 2015), 2407.12028 (TreeSeg hierarchical topic segmentation of large transcripts, 2024-06). "LLM on a Budget: Active Knowledge Distillation" not found on arXiv (ResearchGate-only; 403) — remains snippet-only and is dropped.

### S49. RADIA — Radio Advertisement Detection with Intelligent Analytics (Álvarez, Armenteros, Torrón, Ortega-Martín, Ardoiz, García; arXiv 2403.03538, Mar 2024) — https://arxiv.org/abs/2403.03538
- Type: paper
- Verified: fetched (abs via curl; PDF details in addendum below if retrieved)
- Key facts: radio ad detection by "advanced speech recognition and text classification"; no prior knowledge of the spots, so it detects "impromptu and newly introduced advertisements"; model "trained on carefully segmented and tagged text data, achieves an F1-macro score of 87.76 against a theoretical maximum of 89.33" (the ceiling reflects ASR/segmentation error); use-case is broadcast-contract compliance monitoring.
- Relevance to AdVTT: the closest published analogue to AdVTT's STT→text-classifier pipeline, on *radio* (live, host-read spots included), with a measured F1 and an explicit ASR-imposed ceiling. Supports transcript classification as the state of practice for unseen spoken ads.

### S50. ChildSafeAds Shared Task 2026: Commercial Content in Child-Facing YouTube Videos (Bertaglia, Goanta, Spanakis, Acar; arXiv 2608.19165, Aug 2026) — https://arxiv.org/abs/2608.19165
- Type: dataset / shared task
- Verified: fetched (abs via curl)
- Key facts: 3,360 videos from 939 channels; "Each instance begins with a segment submitted to SponsorBlock", paired with transcript, video/channel metadata and the linked sales page; sub-tasks: offer type (ST1), product category (ST2), legal risk flags (ST3); four cumulative evidence-access levels from transcript upward; 45.5% of videos lacked the "Includes paid promotion" label; labels produced by GPT-5.4 after expert review, dev set independently labelled by GPT-5.6-luna.
- Relevance to AdVTT: (i) a brand-new, transcript-aligned SponsorBlock-derived corpus — the best public candidate for evaluating AdVTT's *advertiser/kind labelling* (not timing); (ii) an academic precedent for LLM-as-labeller with expert-reviewed taxonomy, and for reporting results per evidence-access level (AdVTT could report transcript-only vs transcript+audio-cue tiers); (iii) sub-task 3 (legal risk flags) is a vocabulary extension AdVTT has not considered.

### S51. An audio-only method for advertisement detection in broadcast television content (Ramires, Cocharro, Davies; arXiv 1811.02411, 2018) — https://arxiv.org/abs/1811.02411
- Type: paper
- Verified: fetched (abs via curl)
- Key facts: detects "short silences which exist at the boundaries between programming and advertising, as well as between the advertisements themselves"; low-energy points → multiple linear regression rejects non-boundary silences using local-context features → long-term grouping into ad regions; 26 h annotated Portuguese TV; Matthews correlation coefficient > 0.87; beats a free audio-visual tool.
- Relevance to AdVTT: the cleanest statement of the *silence-boundary* cue. It transfers only to DAI splice points and produced spots in podcasts (MinusPod's "VAD-gap detector", S16); host-read ads have no such boundary. Useful as a cheap candidate-boundary generator for edge refinement, not as a detector.

### S52. Ad-Net: Audio-Visual CNN for Advertisement Detection in Videos (Minaee et al., arXiv 1806.08612, 2018) — https://arxiv.org/abs/1806.08612
- Type: paper
- Verified: fetched (abs via curl)
- Key facts: two-stream audio+visual CNN fused for commercial detection and categorisation; >50k regular/commercial shots; audio+visual "significantly improves" over either alone and over hand-crafted features; goal is ad *replacement*.
- Relevance to AdVTT: relevant to the later video phase only; reinforces that acoustic style cues work for produced commercials, not host reads.

### S53. TreeSeg: Hierarchical Topic Segmentation of Large Transcripts (Gklezakos, Misiak, Bishop; arXiv 2407.12028, 2024) — https://arxiv.org/abs/2407.12028
- Type: paper
- Verified: fetched (abs via curl)
- Key facts: off-the-shelf embeddings + divisive clustering → binary-tree segmentation; robust to ASR noise; motivated partly by "breaking down large inputs in order to fit them into the context window" of LLMs; beats baselines on ICSI and AMI; introduces TinyRec (small manually annotated corpus).
- Relevance to AdVTT: an embedding-only, LLM-free segmenter that could define chunk boundaries at topic shifts rather than fixed token counts, reducing the chance an ad straddles a window edge (S34).

### S54. Spotify podcast-ads *targeting* papers — Cold-Starting Podcast Ads and Promotions with MTL (WSDM 2026, arXiv 2601.02306) and CAMoE audio-centric ads targeting (KDD 2025, arXiv 2506.18735) — https://arxiv.org/abs/2601.02306 ; https://arxiv.org/abs/2506.18735
- Type: paper(s)
- Verified: fetched (abs via curl)
- Key facts: both are ad-*serving* models (CTR/eCPS optimisation; 22% eCPS reduction; 14.5% CTR lift for audio ads); neither detects ads in content.
- Relevance to AdVTT: negative result for the search — Spotify's recent public work on podcast ads is on targeting, not detection; the S1 EC detector (2021) remains their only published detection work.

### S49 (addendum) — RADIA, PDF fetched. Pipeline: OpenAI Whisper → text windows → fine-tuned RoBERTa binary "ad"/"no-ad". Data: 7 high-audience Spanish stations, 183 h 40 min, labelled in LabelStudio with full coverage and a per-region confidence value; station self-promos "have been excluded". Two segmentation modes: "non-exact" (transcribe 10-min audio, cut text on Whisper timestamps) vs "exact" (cut audio into n-second chunks, transcribe each). Window label = majority content type; windows non-overlapping; classification is *non-sequential* (each window independent). Test = 3-hour contiguous blocks per station/day, ~4:1 split. The 89.33 "theoretical maximum" is the F1 achievable by perfect window labels given window-majority quantisation — i.e., an explicit *boundary-quantisation ceiling*. Relevance: AdVTT's word-level edge refinement attacks exactly this ceiling; RADIA's exclusion of house promos shows the PROMOTION/house class is treated as out-of-scope by compliance-monitoring users.

### S50 (addendum) — ChildSafeAds, PDF fetched. SponsorBlock snapshot downloaded 5 May 2026; one eligible interval kept per video; instances carry "Segment text, start and end time" (access level 1 = transcript only); 60 instances lack transcripts. Labels: GPT-5.4 as judge with an expert-iterated taxonomy; GPT-5.6-luna relabelled the 504-item dev set — cross-model exact agreement on ST3 flag sets 44.4%, per-flag "no flag" 77.2%; "No human inter-annotator agreement figure is available." Metric: macro-F1 per sub-task. Licence: SponsorBlock-derived data retain CC BY-NC-SA 4.0; a data-use agreement "prohibits redistribution" of video-derived fields; competition on CodaBench. Relevance: confirms (a) LLM-only labelling yields only moderate cross-model agreement on fine-grained categories — a warning for AdVTT's `kind`/`advertiser` labels; (b) NC licence again.

### S49 (addendum 2) — RADIA hyperparameters: transcription windows of 10, 20 and 40 s with Whisper large-v2 / medium / small; radio ads "typically last between 20 and 30 seconds"; "smaller window lengths yield higher theoretical F1-macro scores" (finer quantisation) at the cost of much longer transcription time, and "models trained with longer window lengths perform worse when evaluated with shorter ones". Relevance: window granularity, not classifier quality, bounded their accuracy — the same trade-off AdVTT's segment unit (SaT sentences vs STT segments) controls.

## Synthesis

**Q1 — Podcast ad/sponsorship detection papers.** The peer-reviewed literature is thin. The only podcast-specific detector with numbers is Spotify's 2021 sentence-level BERT (S1: transcript F1 0.77 with one sentence of context; precision 0.69 < recall 0.87), trained partly on listener-skip "dips" whose boundaries are 16–35 words off. Radio's analogue is RADIA (S49: Whisper → RoBERTa windows, F1-macro 87.76 on 183 h of Spanish radio, with an 89.33 ceiling imposed by window quantisation). The only published *LLM-on-transcript* sponsor detector (S8, GPT-4o on 421 YouTube transcripts) reports no precision/recall at all. Open-source practice (ZeroAds S15, MinusPod S16, podcast-ad-remover S17) is uniformly Whisper→LLM→cut with unpublished accuracy. Melamed & Kim 2009 (S14) is the ancestor: ASR n-grams + pitch dynamics, F1 0.92 on hold-music ads, and its n-gram method works *because the same copy recurs*. There is no public, timestamped, human-labelled podcast ad dataset; the Spotify Podcast Dataset is closed to new users (S3, snippet-only) and never had ad labels (S4, S5). SponsorBlock (S6, S7, S9, S11, S50) is the only large weak-label corpus of spoken sponsor reads: ≥300k transcripts (S9), CC BY-NC-SA, and noisy — half of DeepSponsorBlock's gross failures were label errors (S7). ChildSafeAds (S50, Aug 2026) is the newest SponsorBlock-derived, transcript-aligned corpus, LLM-labelled.

**Q2 — Classic TV/radio cues and transfer.** TV detectors key on black frames, cut rate, logo absence, inter-spot silences, duration priors and repetition/fingerprints (S19, S51, S52, S18). For host-read podcast ads: visual cues are absent; silences mark only DAI splices and produced spots (S51, S16); prosodic "pitch dynamics" (S14) marks produced reads, not a host's normal voice; *repetition of the same copy across episodes* (S14 n-grams, S19 fingerprints, S16 pattern memory) and *duration priors* transfer directly and are LLM-free. S24 adds a subtle result: acoustic pause features help fine-tuned segmenters but *hurt* zero-shot LLMs — so fuse audio cues after the LLM, not in the prompt.

**Q3 — Spoken-content segmentation.** TextTiling is weak on podcasts (S21: F1 0.53, Pk 0.44). Spotify's production chapteriser PODTILE (S22) is AdVTT's design pattern validated at scale: sentence indices printed inline, 7,000+1,000-word chunks, carried-forward context, a fixed "no boundaries" string — and a 220M LongT5 beat zero-shot GPT-4-128k on WindowDiff (0.448 for GPT-4). Chapter-Llama (S23) instead makes the model *copy inline HH:MM:SS timestamps*. SaT (S20) gives punctuation-robust sentence units for ASR text; TreeSeg (S53) gives embedding-only topic chunking. Boundary metrics have moved from Pk/WindowDiff (biased, S47) to Fournier's boundary similarity B (S24, S47) or IoU-based F1 (S7, S23, S48).

**Q4 — LLM-as-labeller over long transcripts.** Position effects are robust: U-shaped recall (S25), effective context far below advertised (S26), and — most relevant — NoLiMa (S27) shows that when the target has no literal overlap with the query (as with ads), 11/13 models lose >50% at 32K; Classifier Context Rot (S28) shows rare events late in long benign contexts are missed 2–30× more often. Long-input extraction fails mostly by truncation/incompletion (S29). On *indices vs quotes*: code-editing tooling abandoned line numbers ("GPT is terrible at working with source code line numbers", S31: 20% → 61%) in favour of content anchors; Deterministic Quoting (S32) has the model emit IDs and code resolve verbatim text (0% quote hallucination). The apparent contradiction with PODTILE's successful indices (S22) resolves as: indices work when they are *literal tokens adjacent to each sentence in a short chunk* (copying), and fail when they require counting or span a long context — which matches AdVTT's own whole-episode failure. Overlap/neighbour-context chunking is standard (S34), with a known hazard for boundaries near window edges. Calibration: verbalised confidence beats logprobs on average calibration for RLHF models (S35) but is overconfident (S36), not cost-faithful (S37), and at *low-FPR operating points* token scoring beats verbalised confidence and no-reasoning beats reasoning (S38) — the operating point AdVTT lives at.

**Q5 — Distillation.** Students trained on GPT-4 labels reach within 0.039 median F1 of human-label students (S39) but inherit *recall-heavy, low-precision* behaviour (precision −0.21); small-LLM teachers are far worse and unstable (S40: α 84→53, mitigations recover 60–75%). Touché 2025/26 (S43, S44) shows fine-tuned encoders detect even adversarially hidden native ads with precision ≈1.0 and span-overlap F1 ≈0.70 baseline; RADIA (S49) and Reddy (S1) are the same recipe on speech. ModernBERT's 8K context makes a token-classification student that spans a whole AdVTT window feasible (S42). Net: for *detection*, the measured state of the art is a fine-tuned encoder over ASR text; the LLM's comparative advantage is zero-shot coverage of novel formats, advertiser extraction and cheap labelling.

**Q6 — Metrics.** Duration-based false-alarm and missed-detection components with a collar (pyannote, S46) are the recognised form of AdVTT's `content_loss_sec`/`ad_recall_sec`; boundary quality is best reported as B (S47) or IoU@τ (S7, S48); text-side spans use span-overlap F1 (S44); RADIA's "theoretical maximum" (S49) is a useful ceiling concept. No source uses an explicitly asymmetric duration-cost metric; the closest precedents are separated FA/miss durations (S46) and the low-FPR framing of S38. Gaps: no Semantic Scholar sweep (429), several paywalled pages (see Gap notes).

## Implications for AdVTT

1. **Reposition the LLM from detector to teacher/arbiter.** The measured state of the art for spoken-ad detection is a fine-tuned encoder over ASR text (S1, S49, S43, S44); no published LLM detector has metrics (S8). Trajectory: keep the current LLM pipeline as the *labelling* engine, distil a ModernBERT token classifier (S42) on validator-passed spans, run it as the cheap default, and call the LLM only for low-confidence windows, advertiser/kind extraction and novel formats. Expect the student to over-predict (S39) — threshold it for precision and keep a human-gold test set (S40).
2. **Make span references literal, not arithmetic.** Print an ID/index token inline beside every segment (PODTILE, S22) or short opaque IDs (hashline, S31), or inline timestamps (Chapter-Llama, S23), so the model copies rather than counts; resolve text and times in code (S32) and keep the verbatim quote as a cross-check, measuring per-STT quote-mismatch rates before halving confidence (S33). Keep windows ≤ ~8K tokens (S26, S27), repeat the instruction after the chunk (S25, S28), and log boundary error vs distance from the window edge (S34).
3. **Add two LLM-free signals to the ladder.** (a) Cross-episode repetition of sponsor copy within a show/network (S14, S16, S19) — high precision, near-zero cost, and it directly serves the false-positive asymmetry; (b) silence/loudness/DAI-splice candidates (S51, S16) used only for edge refinement of DAI spots. Fuse these *after* the LLM, not in the prompt (S24).
4. **Rebuild confidence for the low-FPR operating point.** Do not expose raw verbalised confidence (S36, S37); compose it from validator outcomes plus, where available, token logprobs; prefer think-off mode or a think-on/think-off ensemble (S38); calibrate on fixtures before it appears in the VTT payload (S35).
5. **Express metrics in recognised terms and publish a benchmark.** Report `content_loss_sec` and `ad_recall_sec` as pyannote false-alarm/miss durations with an explicit collar (S46), add IoU@τ or boundary similarity B (S47, S48), and report per evidence tier (transcript-only vs +audio cues) as ChildSafeAds does (S50). No public timed podcast-ad benchmark exists: releasing AdVTT's fixtures (with inter-annotator B, S2/S47) would be the first, and a cleaned, vote-filtered SponsorBlock evaluation split (S7, S11; NC licence, evaluation only) plus Touché-26 spans for the text side (S44) gives external checkpoints.
6. **Widen the vocabulary and mind licences.** SponsorBlock-style *self-promo / cross-promo / interaction-reminder* classes (S6, S16), advertiser/product fields (S44) and a disclosure flag (S50) are established; SponsorBlock data (CC BY-NC-SA) may evaluate but not train a commercially licensed model (S11, S50). RADIA's users exclude house promos (S49) — PROMOTION should stay a separate, skippable-by-choice class.
7. **Sidecar metadata is the defensible product shape.** The ZeroAds thread (S15) shows redistributing cut audio draws copyright and incentive objections; a metadata track consumed by the player avoids both and matches the preliminary design.

## Open questions / things that need an experiment

1. A/B on the 4 fixtures (then a larger set): inline numeric index vs opaque ID vs inline timestamp as the span reference; measure `boundary_err_sec` and index-off-by-N rate (S22, S23, S31).
2. Boundary error as a function of distance from window edge; does 10% overlap (S34) or topic-aligned chunking (S53) reduce straddled ads?
3. Quote-mismatch rate per STT backend (whisper-mlx, parakeet, Gladia, OpenAI) before treating a mismatch as evidence against the span (S33).
4. Think-on vs think-off vs ensemble at the content_loss ≤ 5 s operating point (S38); does token-logprob scoring (local models, OpenAI) beat the verbalised number for ranking spans (S35, S36)?
5. Cross-episode repetition detector: on 20+ episodes of three shows, what fraction of host-read spans recur (n-gram or embedding match) and with what precision (S14, S16)?
6. Distil ModernBERT on validator-passed LLM spans: precision at fixed recall vs the teacher; seed-to-seed instability (S40); cost per episode on Apple Silicon (S42).
7. Inter-annotator agreement on fixture boundaries via boundary similarity (S47), given podcast intro agreement was 72/117 perfect (S2) — sets a realistic floor for `boundary_err_sec`.
8. Does performance on YouTube sponsor reads (SponsorBlock/ChildSafeAds, S7, S50) predict performance on podcast host reads? If yes, a public leaderboard becomes possible.
9. Is the 240 s max-duration rung right? SponsorBlock duration distributions (S11) and RADIA's ad-block statistics (S49) would calibrate it.
10. How stable are LLM `kind`/`advertiser` labels across models? ChildSafeAds saw 44–77% cross-model agreement on fine categories (S50).
