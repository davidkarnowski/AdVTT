# D — Speech-to-text and word-level timing for ad-boundary precision
Accessed: 2026-09-01

## Status
COMPLETE — 73 sources (S1–S73) logged 2026-09-01/02; Synthesis, Implications and Open questions written.
Run notes: the session-wide WebSearch budget (200/200) was exhausted and WebFetch hit a session limit
part-way through the first run (nothing reached disk then); this run re-logged everything incrementally.
Entries marked "snippet-only" come from WebSearch result summaries, not a fetched page. Failed fetches
are recorded as gaps (see "Failed fetches this run" after S70 and the Open questions).

## Sources

### Search log (queries issued in first run, before fetching)
- "Voxtral Mistral open weights transcription word timestamps Voxtral Mini Transcribe 2 pricing 2026" → mistral.ai/news/voxtral-transcribe-2, simonwillison.net/2026/Feb/4/voxtral-2, venturebeat
- "Qwen3-ASR open source release word timestamps forced aligner 2026" → arxiv 2601.21337, github QwenLM/Qwen3-ASR, HF Qwen/Qwen3-ForcedAligner-0.6B-hf
- "Whisper word timestamp accuracy evaluation cross-attention DTW whisper-timestamped paper milliseconds" → arxiv 2408.16589 (CrisperWhisper), nyrahealth/CrisperWhisper
- "perceptual threshold audio edit point gap detection milliseconds speech cut imperceptible" → PMC gap-detection papers
- "pyannote speaker-diarization 4.0 community-1 release 2025 DER benchmark" → HF pyannote/speaker-diarization-community-1, pyannote.ai/blog/community-1
- "Kyutai STT 2.6B word timestamps open weights release" → kyutai.org/stt, HF kyutai/stt-2.6b-en
- "NVIDIA Sortformer diarization streaming 4 speakers NeMo 2025 DER; DiariZen pyannote WavLM" → arxiv 2509.26177, HF nvidia/diar_streaming_sortformer_4spk-v2
- "Qwen3-Omni audio timestamps; Audio Flamingo 3 long audio 10 minutes; Kimi-Audio open source ASR timestamps" → github QwenLM/Qwen3-Omni/discussions/1, arxiv 2507.08128, arxiv 2504.18425
- "Whisper long-form transcription drift chunked vs sequential ..." → arxiv 2303.00747 (WhisperX), HF post sanchit-gandhi
- "Deepgram Nova-3 word timestamps accuracy smart_format diarize documentation; Speechmatics word timestamps" → deepgram.com/learn/introducing-nova-3..., docs.speechmatics.com/speech-to-text/batch/output
- "Open ASR Leaderboard 2026 top models average WER parakeet canary whisper large-v3 ranking" → northflank.com blog, assemblyai blog
- "Gemma 3n audio speech recognition timestamps 30 seconds limit ASR WER" → ai.google.dev/gemma/docs/capabilities/audio, HF discussion
- "Koenecke Careless Whisper hallucination ..." → arxiv 2402.08021
- "Gemini audio timestamp accuracy evaluation transcription timestamps drift" → discuss.ai.google.dev threads 129501, 52587, 66777, 72114; towardsdatascience pipeline article
- "forced alignment word boundary accuracy evaluation 20 ms tolerance MFA WhisperX MMS_FA TIMIT Buckeye" → arxiv 2406.19363, arxiv 2406.02560, arxiv 2509.09987
- "gpt-4o-transcribe word timestamps not supported timestamp_granularities whisper-1 only" → developers.openai.com API reference, community threads
- "whisper.cpp DTW token-level timestamps --dtw alignment heads accuracy" → linto-ai/whisper-timestamped, transformers issue 28365, hollance gist
- "audio editing splice crossfade length imperceptible click ms" → descript blog, podcastengineeringschool, USPTO 7292902
- "Amazon Transcribe pricing $0.024 per minute tier 1 batch standard 2026"; "Azure speech to text pricing standard $1 per hour ..." → costgoat, brasstranscripts, azure pricing page
- FAILED (budget exhausted): "parakeet-mlx speed Apple Silicon", "Google Cloud Speech-to-Text V2 Chirp 3 pricing", "Speechmatics pricing per hour", "mlx-whisper large-v3 benchmark", "Whisper hallucination music", "gpt-4o audio tokens per minute", "AssemblyAI Universal-2 timestamp accuracy".

### S1. Open ASR Leaderboard (HF Space) — https://huggingface.co/spaces/hf-audio/open_asr_leaderboard
- Type: dataset/leaderboard
- Verified: fetch attempted; page is a Gradio app, only the header rendered — table NOT retrievable by WebFetch. Numbers below come from S2/S3 and model cards (S4–S6, S20) that quote the leaderboard.
- Key facts: none directly retrievable.
- Relevance to AdVTT: leaderboard is the canonical WER/RTFx reference; must be read in a browser or via the GitHub repo (S2).

### S2. huggingface/open_asr_leaderboard (GitHub repo README) — https://github.com/huggingface/open_asr_leaderboard
- Type: repo
- Verified: fetched
- Key facts: English short-form = the "Main Test Sets" of hf-audio/open-asr-leaderboard (AMI, Earnings-22, GigaSpeech, LibriSpeech clean/other, SPGISpeech, TED-LIUM, VoxPopuli); long-form suite = earnings21, earnings22, CORAAL; multilingual = FLEURS, MCV, MLS; a chunked Earnings22 set with session-level refs. As of July 2026 evaluations run on HF Jobs, 1x H200 (141 GB). Example full English short-form run cost: parakeet-tdt-0.6b-v3 $2.92, whisper-large-v3-turbo $4.75, Qwen3-ASR-1.7B $5.58. Trade-off plots added March 2026.
- Relevance: RTFx numbers on the board are H200 GPU numbers — not indicative of Apple Silicon/CPU speed. Long-form (earnings21/22) suite is closer to podcast audio than short-form.

### S3. Northflank, "Best open source STT model in 2026 (with benchmarks)" — https://northflank.com/blog/best-open-source-speech-to-text-stt-model-in-2026-benchmarks
- Type: blog (secondary; quotes leaderboard "as of late 2026")
- Verified: fetched
- Key facts (leaderboard avg WER / RTFx): Canary Qwen 2.5B 5.63% / 418; IBM Granite Speech 3.3 8B 5.85%; Whisper large-v3 7.4%; Whisper large-v3-turbo 7.75% / 216; Distil-Whisper large-v3 "close to v3", ~5–6x faster; Parakeet TDT 1.1B ~8.0% / >2000. Snippet-only from a companion AssemblyAI blog: Parakeet 6.05% at 4264 RTFx; NLE 5.79% (4th).
- Relevance: the accuracy leaders (Canary-Qwen, Granite) are LLM-decoder models without word timestamps (S6, S20); the timestamp-capable models (Parakeet TDT, Whisper) sit 0.5–2 WER points behind — acceptable for ad classification where the LLM reads meaning, not exact words.

### S4. nvidia/parakeet-tdt-0.6b-v3 model card — https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3
- Type: product/model card
- Verified: fetched
- Key facts: 600M FastConformer + TDT decoder; 25 European languages with auto language detection; "accurate word-level and segment-level timestamps" plus char-level; Open ASR avg WER 6.34% (LibriSpeech clean 1.93% … Earnings-22 11.42%); RTFx 3332.74; CC-BY-4.0; up to 24 min per pass with full attention (A100 80 GB), up to 3 h with `rel_pos_local_attn`; released 2025-08-14.
- Relevance: current parakeet-mlx default (S13); timestamps come from TDT frame durations (80 ms frames), no separate aligner needed; Earnings-22 (long-form business speech) WER 11.4% is the realistic podcast-like figure.

### S5. nvidia/parakeet-tdt-0.6b-v2 model card — https://huggingface.co/nvidia/parakeet-tdt-0.6b-v2
- Type: model card
- Verified: fetched
- Key facts: English-only; avg WER 6.05% on Open ASR; RTFx 3386 (batch 128, GPU); word/segment/char timestamps; punctuation + capitalisation; 24 min single pass full attention; CC-BY-4.0; released 2025-05-01; 16 kHz mono WAV/FLAC input.
- Relevance: for English podcasts v2 is 0.3 WER better than v3 on the same board; both are the local timestamp-capable workhorses.

### S6. nvidia/canary-qwen-2.5b model card — https://huggingface.co/nvidia/canary-qwen-2.5b
- Type: model card
- Verified: fetched
- Key facts: avg WER 5.63% (leaderboard #1 at the time of S3); RTFx 418; English only; CC-BY-4.0; "maximum audio duration in training was 40s", degradation beyond; no word/segment timestamp support mentioned; released 2025-07-17.
- Relevance: top-WER model is unusable for boundary timing without an external aligner; confirms the WER-vs-timestamps trade-off.

### S7. openai/whisper-large-v3-turbo model card — https://huggingface.co/openai/whisper-large-v3-turbo
- Type: model card
- Verified: fetched
- Key facts: decoder pruned 32→4 layers; 809M params (vs 1550M); MIT; "way faster, at the expense of a minor quality degradation"; long-form: sequential (sliding window, better accuracy) vs chunked (30 s chunks, faster, parallel); `return_timestamps="word"` supported in transformers pipeline. Leaderboard WER 7.75% (S3).
- Relevance: turbo is the sensible Whisper default for local runs; word timestamps still come from cross-attention DTW (see S36–S38), so precision issues carry over.

### S8. ggml-org/whisper.cpp README — https://github.com/ggml-org/whisper.cpp
- Type: repo
- Verified: fetched
- Key facts: "Apple Silicon first-class citizen" — ARM NEON, Accelerate, Metal, Core ML; word-level timestamps "experimental" via `-ml 1`/`--max-len`; integer quantisation; Silero-VAD models supported for pre-filtering; MIT; per-machine benchmarks live in issue #89 and `bench.py` (no numbers in README). Snippet-only (from S44 search): whisper.cpp's default word timing uses timestamp-token probabilities after each token, which whisper-timestamped's authors say "lacks robustness"; an experimental `--dtw` cross-attention mode also exists (snippet-only, not verified in README).
- Relevance: fastest zero-Python path on Mac, but its word timestamps are the least principled of the Whisper family — needs a downstream aligner if used for edges.

### S9. SYSTRAN/faster-whisper README — https://github.com/SYSTRAN/faster-whisper
- Type: repo
- Verified: fetched
- Key facts: CTranslate2 backend; RTX 3070 Ti, 13 min audio, large-v2 beam 5: openai-whisper 2m23s/4708 MB vs faster-whisper 1m03s/4525 MB (FP16) and 59 s/2926 MB (INT8); `word_timestamps=True`; Silero VAD filter, default removes silence >2 s, tunable via `vad_parameters` (e.g. `min_silence_duration_ms=500`); `BatchedInferencePipeline`; `condition_on_previous_text` exposed; CPU INT8 supported; GPU needs CUDA 12 + cuDNN 9; MIT.
- Relevance: best cross-platform (Linux/Windows CPU+GPU) Whisper backend for a public CLI; VAD filter and `condition_on_previous_text=False` are the standard hallucination mitigations.

### S10. mlx-whisper (ml-explore/mlx-examples/whisper) — https://github.com/ml-explore/mlx-examples/tree/main/whisper
- Type: repo
- Verified: fetched
- Key facts: `pip install mlx-whisper`, needs ffmpeg; `word_timestamps=True` supported; `convert.py -q` 4-bit quantisation; pre-converted models in mlx-community. No speed numbers or licence in README (mlx-examples is MIT at repo level — not verified in this fetch).
- Relevance: AdVTT's current Apple Silicon Whisper path; word timestamps are the same cross-attention DTW as upstream Whisper.

### S11. lightning-whisper-mlx — https://github.com/mustafaaljadery/lightning-whisper-mlx
- Type: repo
- Verified: fetched
- Key facts: claims "10x faster than Whisper CPP, 4x faster than current MLX Whisper"; batching (default batch 12); 4/8-bit quant; 17 commits total; no word-timestamp support mentioned; licence not shown.
- Relevance: speed via batching drops word timestamps and is a low-activity repo — not suitable as AdVTT's default.

### S12. m-bain/whisperX README — https://github.com/m-bain/whisperX
- Type: repo
- Verified: fetched
- Key facts: "70x realtime transcription using whisper large-v2" (batched, faster-whisper backend); wav2vec2 phoneme-CTC forced alignment for word timestamps because Whisper's utterance timestamps "can be inaccurate by several seconds"; pyannote diarization; VAD pre-segmentation reduces hallucination; limitations: words with non-dictionary characters ("2014.", "£13.60") get no timing, overlapping speech poor, language-specific alignment model needed; BSD-2-Clause; CUDA 12.8 for GPU, <8 GB VRAM for large-v2; CPU supported, Apple Silicon compatible (no MPS acceleration claims).
- Relevance: the reference "Whisper + CTC aligner" architecture; the unaligned-numerals limitation matters for ads (prices, promo codes, URLs) — exactly the tokens near ad edges.

### S13. senstella/parakeet-mlx — https://github.com/senstella/parakeet-mlx
- Type: repo
- Verified: fetched
- Key facts: default model `mlx-community/parakeet-tdt-0.6b-v3`; supports ParakeetTDT/RNNT/CTC/TDTCTC classes (no Canary); results carry `AlignedToken{text,start,end,duration}` → word/sentence timing; long audio via `chunk_duration` (default 120 s) and `overlap_duration` (default 15 s); Apache 2.0; no Apple Silicon speed numbers in README.
- Relevance: AdVTT's current local default; the 120 s/15 s chunking with global offsets is already a "preserve global timestamps" strategy (Q7). Speed on M-series not documented → needs local measurement.

### S14. Kyutai STT — https://kyutai.org/stt/ (model: https://huggingface.co/kyutai/stt-2.6b-en)
- Type: product/model page
- Verified: fetched (kyutai.org); WER/RTFx/licence figures snippet-only (from HF card summaries in search)
- Key facts: `stt-1b-en_fr` (1B, EN/FR, 500 ms delay) and `stt-2.6b-en` (2.6B, EN, 2.5 s delay); "comes with word-level timestamps"; semantic VAD (Rust only); 400 real-time streams on one H100; L40S Rust server 64 streams at RTF 3x; MLX implementation for Mac/iPhone. Snippet-only: 2.6B WER 6.4%, RTFx 88.37, weights CC-BY-4.0.
- Relevance: a streaming (delayed-streams) architecture with native word timestamps and MLX support — a credible local alternative on Mac; timestamp accuracy not published.

### S15. moonshine-ai/moonshine README — https://github.com/moonshine-ai/moonshine
- Type: repo
- Verified: fetched
- Key facts: streaming-first, "tiny 1MB models" upward; claims "higher accuracy than Whisper Large V3" on its leaderboard placement (no WER in README); MIT by default for all sizes/languages, except legacy non-English non-streaming models under a non-commercial "Moonshine Community License"; no word-timestamp support mentioned.
- Relevance: edge/live oriented; no documented word timestamps → not a fit for boundary timing.

### S16. Mistral, "Voxtral transcribes at the speed of sound" (Voxtral Transcribe 2) — https://mistral.ai/news/voxtral-transcribe-2/
- Type: product announcement
- Verified: fetched
- Key facts (2026-02-04): Voxtral Mini Transcribe V2 (batch API) "approximately 4% WER on FLEURS", word-level timestamps, diarization, context biasing up to 100 words/phrases, 13 languages, max 3 h per request, $0.003/min (= $0.18/h); Voxtral Realtime (4B params) $0.006/min via API and open weights under Apache 2.0 on HF; claims to beat GPT-4o mini Transcribe, Gemini 2.5 Flash, AssemblyAI Universal, Deepgram Nova on accuracy and to be ~3x faster than ElevenLabs Scribe v2 at one-fifth the cost. Corroborating snippet: simonwillison.net/2026/Feb/4/voxtral-2/.
- Relevance: cheapest word-timestamped cloud STT found ($0.18/h) with 3 h input limit (no chunking needed for most episodes); context biasing = brand-vocabulary hook. Open-weights Realtime 4B is a candidate for local use but word-timestamp precision unpublished.

### S17. Mistral, Voxtral (July 2025, Small 24B / Mini 3B) — https://mistral.ai/news/voxtral
- Type: product announcement
- Verified: NOT fetched (session limit hit). Gap: confirm Apache-2.0 open weights for Mini 3B/Small 24B, ~30–40 min context, and whether the open models emit word timestamps (Transcribe 2 API does; open Mini 3B reportedly did not).

### S18. Qwen3-ASR Technical Report (arXiv 2601.21337) — https://arxiv.org/html/2601.21337v2
- Type: paper (2026-01/02)
- Verified: fetched
- Key facts: Qwen3-ASR-0.6B / 1.7B, 52 languages+dialects, unified streaming/offline, max audio 1200 s per request, offline RTF 0.00923 (0.6B) / 0.01482 (1.7B) on GPU; LibriSpeech clean/other WER 1.63/3.38 (1.7B), 2.11/4.55 (0.6B). Qwen3-ForcedAligner-0.6B: "first LLM-based speech forced aligner"; Accumulated Average Shift (AAS) 27.8 ms on human-labelled sets vs MFA 49.9 ms vs NFA 88.6 ms; on 300 s concatenated audio 24.8 ms vs NFA 140.0 ms; "relative reduction of 67%~77% in accumulated average shift".
- Relevance: strongest published word-timing accuracy of any open aligner (≈25–28 ms mean shift), and it accepts transcripts from any ASR — a drop-in "edge refinement" stage for AdVTT.

### S19. Qwen/Qwen3-ForcedAligner-0.6B-hf model card — https://huggingface.co/Qwen/Qwen3-ForcedAligner-0.6B-hf
- Type: model card
- Verified: fetched
- Key facts: 11 languages (zh, en, yue, fr, de, it, ja, ko, pt, ru, es); ≤5 min audio per inference; Apache 2.0; released 2026-01-29; two-stage use: any ASR transcript + audio → word/arbitrary-unit timestamps; "surpassing E2E-based forced-alignment models in accuracy" (numbers in S18).
- Relevance: 5-min window means AdVTT would align per ad candidate (≤240 s max duration rule fits), not whole episodes. No MLX port found (gap) — PyTorch/transformers on Mac would be CPU/MPS.

### S20. ibm-granite/granite-speech-3.3-8b model card — https://huggingface.co/ibm-granite/granite-speech-3.3-8b
- Type: model card
- Verified: fetched
- Key facts: 9B params BF16; Open ASR mean WER 5.74; Apache 2.0; EN/FR/DE/ES/PT ASR+AST; two-pass design (transcribe, then LLM); released 2025-06-19 (rev 3.3.2); no word-timestamp capability documented.
- Relevance: high accuracy, no timestamps, 9B on Mac is heavy → not a boundary-timing candidate.

### S21. Gemma 3n audio (Google docs / HF discussion) — https://ai.google.dev/gemma/docs/capabilities/audio ; https://huggingface.co/google/gemma-3n-E4B-it/discussions/37
- Type: docs/forum
- Verified: snippet-only
- Key facts: USM-based audio encoder, one token per 160 ms (6.25 tokens/s); encoder "implemented to process audio clips up to 30 seconds"; ASR/AST via prompt; no timestamp output documented; the model does not receive explicit timestamps for frames.
- Relevance: not usable for episode-scale timing; only relevant as a tiny on-device ASR.

### S22. OpenAI Speech-to-text guide — https://developers.openai.com/api/docs/guides/speech-to-text
- Type: spec/docs
- Verified: fetched (301 from platform.openai.com)
- Key facts: models `gpt-transcribe` (recommended), `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, `gpt-4o-transcribe-diarize`, `whisper-1` (legacy). "Use `whisper-1` when you need word or segment timestamps"; `timestamp_granularities[]` is "only supported for `whisper-1`". `gpt-4o-transcribe-diarize` returns `diarized_json` (segments with speaker + timing, not words). 25 MB max file; `prompt` on whisper-1 max 224 tokens; `keywords` param on gpt-transcribe; `chunking_strategy:"auto"` for >30 s on the diarize model. Corroborated by snippet-only community/API-reference results (costgoat, community.openai.com thread 733182).
- Relevance: OpenAI's newer, more accurate models cannot give AdVTT word edges; whisper-1 is the only OpenAI option for word timing and it carries all Whisper timing caveats (S36). 25 MB limit forces chunking of episodes (Q7).

### S23. OpenAI API pricing — https://developers.openai.com/api/docs/pricing
- Type: product pricing
- Verified: fetched (openai.com/api/pricing returned 403)
- Key facts: whisper-1 $0.006/min ($0.36/h); gpt-4o-transcribe $0.006/min; gpt-4o-mini-transcribe $0.003/min ($0.18/h); gpt-4o-transcribe-diarize $0.006/min. Audio-token input: gpt-realtime / gpt-realtime-2 / 2.1 / gpt-audio / gpt-audio-1.5 $32.00 per 1M audio input tokens; gpt-realtime-mini / gpt-audio-mini $10.00 per 1M. Audio tokens-per-second not stated on the page (gap; see Synthesis).
- Relevance: cloud STT cost baseline; audio-native GPT path priced per audio token.

### S24. Deepgram pricing — https://deepgram.com/pricing
- Type: product pricing
- Verified: fetched
- Key facts: Nova-3 pre-recorded monolingual $0.0043/min PAYG (= $0.258/h), $0.0036 Growth; multilingual $0.0052/min ($0.312/h); streaming $0.0048/min promo (regular $0.0077); Whisper Large hosted $0.0048/min; speaker diarization included at no cost for pre-recorded ($0.002/min streaming); Growth = prepaid ≥$4K/yr, "save up to 20%".
- Relevance: word timestamps returned by default (S25); cheapest big-name option with free diarization.

### S25. Deepgram, "Introducing Nova-3" / timestamps guide — https://deepgram.com/learn/introducing-nova-3-speech-to-text-api ; https://deepgram.com/learn/working-with-timestamps-utterances-and-speaker-diarization-in-deepgram
- Type: blog/docs
- Verified: snippet-only (fetch blocked by session limit)
- Key facts: Nova-3 lists "greater word-level timestamp precision" among improvements; word start/end returned by default; `utterances=true`, `diarize=true`, `smart_format=true` give structured output in one call; vendor claims 54.3% (streaming) / 47.4% (batch) WER reduction vs competitors; keyterm prompting.
- Relevance: candidate cloud default for Linux/Windows users; no absolute ms figure for timestamp precision published.

### S26. AssemblyAI pricing — https://www.assemblyai.com/pricing
- Type: product pricing
- Verified: fetched
- Key facts: Universal-3.5 Pro (`universal-3-5-pro`) $0.21/h; Universal-2 $0.15/h; SLAM-1 deprecated ("migrate to Universal-3.5 Pro"); Nano routes to universal-2; streaming U3.5 Pro Realtime $0.45/h, Universal-Streaming $0.15/h; diarization add-on +$0.02/h async (+$0.065 experimental); Keyterms prompting +$0.05/h async; PII redaction +$0.08/h; streaming billed per session duration.
- Relevance: Word timestamps are a standard field of AssemblyAI transcripts (not re-verified in this fetch — treat as snippet-level knowledge); Slam-1 (the prompt-tunable model named in the brief) is already deprecated.

### S27. Gladia pricing — https://www.gladia.io/pricing
- Type: product pricing
- Verified: fetched
- Key facts: Starter PAYG async $0.61/h, real-time $0.75/h; Growth "as low as $0.20/hr" async / $0.25 real-time; Enterprise custom; Solaria-1 ("universal STT") and Solaria-3 ("9.6% WER on real English audio" vendor claim); diarization and "word-level timestamps" included on all plans; 100+ languages; €50 one-time free credit (~80 h async).
- Relevance: AdVTT's current cloud seam is 2–3x the price of Deepgram/AssemblyAI/Voxtral at PAYG; only competitive at committed volume.

### S28. Speechmatics pricing — https://www.speechmatics.com/pricing (+ https://docs.speechmatics.com/speech-to-text/batch/output)
- Type: product pricing / docs
- Verified: fetched (pricing page partially rendered); output docs snippet-only
- Key facts: "$100 in credit, no card required"; a "Pro" figure of "$0.129" shown without a clear unit in the rendered text (likely per hour — approx., unverified); volume discounts above 500 h. Docs (snippet-only): default JSON output includes per-word `start_time`/`end_time` and confidence; current model family named "Melia-1" in a third-party doc.
- Relevance: word timestamps standard; price unit needs confirmation before tabulating.

### S29. ElevenLabs Scribe docs — https://elevenlabs.io/docs/capabilities/speech-to-text
- Type: docs
- Verified: fetched
- Key facts: Scribe v2 and Scribe v2 Realtime; "precise word-level timestamps"; diarization up to 32 speakers; output types `word`, `spacing`, `audio_event` (laughter, applause…); 3 GB max file; 10 h max duration; 90+ languages (tiers ≤5% WER … >10–20%).
- Relevance: `audio_event` tags and 10 h limit are attractive; music/jingle detection could come free with the transcript.

### S30. ElevenLabs API pricing — https://elevenlabs.io/pricing/api
- Type: product pricing
- Verified: fetched
- Key facts: Speech to Text $0.22/h at every tier (Starter $6/mo includes 4.5 h; Creator $22 → 27 h; Pro $99 → 100 h; Scale $299 → 450 h; Business $990 → 1,359 h); entity detection +$0.07/h; keyterm prompting +$0.05/h; billed per audio minute.
- Relevance: mid-priced with word timestamps + audio events.

### S31. Google Cloud Speech-to-Text pricing / word time offsets — https://cloud.google.com/speech-to-text/pricing ; https://cloud.google.com/speech-to-text/docs/async-time-offsets
- Type: product pricing / docs
- Verified: pricing fetch returned no table (dynamic page); time-offsets doc snippet-only
- Key facts: word time offsets (`enableWordTimeOffsets`) documented for V1/V2. Chirp 3 per-minute price NOT obtained (search budget exhausted before the query ran). Gap.
- Relevance: cannot tabulate Google's price from primary evidence; treat as unknown pending a retry.

### S32. Amazon Transcribe pricing — https://aws.amazon.com/transcribe/pricing/
- Type: product pricing
- Verified: fetched (dynamic tier table not rendered; only worked examples) + snippet-only secondary pages (costgoat, brasstranscripts)
- Key facts: page examples show "$0.006 per minute" batch and "$0.01 per minute" streaming (US East) billed per second, no minimum. Secondary snippets give the legacy tiered rate: Tier 1 $0.024/min (0–250k min/mo) → $0.0078 at 5M+; one snippet states "standard batch $0.006/min ($0.36/hr) and streaming $0.01/min ($0.60/hr)… flat rates with no volume tiers". CONTRADICTION between the $0.024 and $0.006 figures — the fetched page's own example supports $0.006/min ($0.36/h) for standard batch as of 2026-09.
- Relevance: at $0.36/h Amazon is price-competitive; word timestamps are standard in Transcribe JSON (not re-verified here).

### S33. Azure Speech pricing — https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/
- Type: product pricing
- Verified: fetched (prices render as "$-" without sign-in) + snippet-only secondary (brasstranscripts, blocksentient)
- Key facts: 5 free audio hours/month (F0). Secondary snippets: standard real-time $1/h, fast transcription $0.36/h, batch $0.18/h; diarization/language ID add-ons $0.30/h/feature for real-time, included for batch; commitment tiers down to $0.50/h.
- Relevance: batch at ~$0.18/h (approx., snippet) is among the cheapest; word timestamps available in batch (`wordLevelTimestampsEnabled`) — not re-verified.

### S34. Rev.ai pricing — https://www.rev.ai/pricing
- Type: product pricing
- Verified: fetched
- Key facts: Reverb async $0.20/h; Reverb Turbo $0.10/h; Reverb foreign language $0.30/h; hosted Whisper Large / Whisper Fusion $0.005/min ($0.30/h); 5 free hours; streaming price not shown; human transcription $1.99/min.
- Relevance: Reverb Turbo at $0.10/h is the cheapest cloud rate found; word-timestamp support not confirmed on the pricing page (Rev.ai JSON normally has per-word `ts`/`end_ts` — snippet-level knowledge, unverified).

### S35. Community/secondary confirmation that only whisper-1 has word timestamps — https://community.openai.com/t/timestamp-granularities-word-does-not-match-generated-transcript/733182 ; https://costgoat.com/pricing/openai-transcription
- Type: forum / blog
- Verified: snippet-only
- Key facts: "For word or segment timestamps, whisper-1 remains the only OpenAI-hosted option"; word-timestamp generation "incurs additional latency"; a 2024 thread reports whisper-1 word timestamps not matching the generated text in places.
- Relevance: corroborates S22.

### S36. CrisperWhisper (Zusag et al., INTERSPEECH 2024, arXiv 2408.16589) — https://arxiv.org/html/2408.16589
- Type: paper
- Verified: fetched
- Key facts: word-timestamp F1 at 50 ms collar on their synthetic set — CrisperWhisper 84.7% clean / 79.5% noisy; WhisperX 76.7% / 59.0%; WhisperT (large-v2 + cross-attention DTW) 74.7% / 68.3%; AMI results reported mainly as mIoU. Root cause of Whisper drift: BPE attaches spaces to word starts, "only 13% of spaces in the original transcripts are mapped to the explicit space token", so pauses get "inadvertently integrated" into adjacent word spans. Removing tokens with duration <50 ms kills residual repetition loops; no harmful hallucinations on AphasiaBank set that broke large-v2.
- Relevance: vanilla Whisper word edges are wrong by pause-length amounts precisely where ads start/end (after a breath/pause). Any Whisper-based edge should be re-aligned or snapped to VAD silence.

### S37. Rousso et al., "Tradition or Innovation: A Comparison of Modern ASR Methods for Forced Alignment" (INTERSPEECH 2024, arXiv 2406.19363) — https://arxiv.org/pdf/2406.19363
- Type: paper
- Verified: fetched (PDF text partially extracted) + snippet detail
- Key facts (word level, TIMIT): MFA 41.6% of boundaries within 10 ms, 72.8% within 25 ms, 89.4% within 50 ms, F1@20 ms 65.7%; WhisperX 22.4% within 10 ms, 52.7% within 20 ms; MMS (wav2vec2 CTC) lowest at 10 ms; gaps "narrow considerably" at 25 ms and become "marginal" at 50–100 ms. Conclusion: MFA still best at strict tolerances; neural aligners comparable at ≥50 ms.
- Relevance: with any modern aligner ~90% of word boundaries land within 50 ms; that is the achievable edge precision — 1–2 orders of magnitude tighter than AdVTT's current 3 s `boundary_err_sec` gate.

### S38. "Whisper Has an Internal Word Aligner" (Yeh, Meng et al., arXiv 2509.09987) + HF transformers issue #28365 — https://arxiv.org/pdf/2509.09987 ; https://github.com/huggingface/transformers/issues/28365
- Type: paper / forum
- Verified: paper fetched (PDF summary only, no numbers extracted); issue snippet-only
- Key facts: specific decoder cross-attention heads align to word boundaries; claims results "competitive with or exceed" WhisperX / whisper-timestamped / CrisperWhisper on LibriSpeech/AMI (numbers not extracted — gap). Snippet-only: "simply averaging heads is better than the pre-defined heads"; a practitioner measured "average 200ms accuracy for token timestamps, with accuracy on the best 80% being 40ms" for a custom model; cross-attention timestamps for the same tokens can differ 100–400 ms between Whisper variants (from S36 search snippet).
- Relevance: Whisper-internal timing can be good on average but has a heavy tail (~20% of words off by >40 ms, some by hundreds of ms) — the tail is what produces audible bad cuts.

### S39. Huang et al., "Less Peaky and More Accurate CTC Forced Alignment by Label Priors" (arXiv 2406.02560) — https://arxiv.org/html/2406.02560
- Type: paper
- Verified: fetched
- Key facts: standard CTC is "peaky" (non-blank on one frame), fine for ASR but bad for alignment; label-prior loss → Buckeye phoneme boundary error 30 ms vs MFA 27 ms; standard CTC predicted phone duration 21 ms (=frame size) vs 74 ms with priors vs 82 ms ground truth; recipe and models released in TorchAudio (basis of `MMS_FA`).
- Relevance: torchaudio's MMS_FA is a reasonable aligner (~30 ms phone error) but still slightly behind MFA; word onsets from CTC aligners are systematically late/early by up to a frame (20 ms) unless priors are used.

### S40. MahmoudAshraf97/ctc-forced-aligner — https://github.com/MahmoudAshraf97/ctc-forced-aligner (torchaudio MMS_FA tutorial: https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_for_multilingual_data_tutorial.html — redirect, NOT fetched)
- Type: repo
- Verified: fetched
- Key facts: default model MMS-300m-1130-forced-aligner (1130 languages); "at least 5X less memory" than torchaudio's API; optional romanisation (uroman) for non-Latin scripts; word-level timestamps default, sentence/char optional, JSON output; CUDA float16 or CPU float32; code BSD, but the default model is CC-BY-NC 4.0 → "commercial applications require using an alternative model".
- Relevance: the NC licence on the default MMS aligner is a blocker for a public tool with commercial users; Qwen3-ForcedAligner (Apache-2.0, S19) or a wav2vec2-base-960h CTC model (as WhisperX uses) avoids it.

### S41. NVIDIA NeMo Forced Aligner (NFA) docs — https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/tools/nemo_forced_aligner.html
- Type: docs
- Verified: fetched
- Key facts: token/word/segment timestamps from NeMo CTC or hybrid CTC-Transducer (CTC branch) models; pure transducer (TDT) not supported; CTM and ASS outputs; "can be used on long audio files of 1+ hours" without duration fields; no accuracy numbers (Qwen3 report measured NFA AAS 88.6 ms, S18).
- Relevance: cannot align with parakeet-tdt directly (needs the hybrid CTC variant); accuracy measured worst of the three aligners in S18.

### S42. Montreal Forced Aligner docs — https://montreal-forced-aligner.readthedocs.io/en/latest/
- Type: docs
- Verified: fetched (homepage only)
- Key facts: current version 3.4; new model formats integrating Hugging Face; conda-forge/PyPI distribution. (Kaldi GMM-HMM basis and MIT licence known from general knowledge — not verified in this fetch.)
- Relevance: most accurate at ≤10–25 ms tolerances (S37) but heavy Kaldi dependency; poor fit for a pip-installable CLI.

### S43. jianfch/stable-ts — https://github.com/jianfch/stable-ts
- Type: repo
- Verified: fetched
- Key facts: post-processes Whisper word timestamps: `suppress_silence=True` (default) snaps timestamps away from detected silence, Silero VAD option, `min_word_dur`, regrouping (`split_by_gap/punctuation/length`), `align()` text-to-audio, `refine()` iteratively mutes audio and watches token probabilities to find "the latest start and earliest end"; backends openai-whisper, faster-whisper, HF transformers, **mlx-whisper**; MIT; no quantitative accuracy claims.
- Relevance: cheapest possible upgrade to AdVTT's existing mlx-whisper path — silence-snapping directly addresses the S36 pause-absorption bug without a second model.

### S44. linto-ai/whisper-timestamped — https://github.com/linto-ai/whisper-timestamped
- Type: repo
- Verified: snippet-only
- Key facts: DTW over cross-attention weights, per-model alignment heads; authors note whisper.cpp's timestamp-token-probability approach "lacks robustness because Whisper models have not been trained to output meaningful timestamps after each word"; hollance gist lists alignment heads for HF models.
- Relevance: explains why whisper.cpp `-ml 1` word times are less trustworthy than DTW-based ones.

### S45. Perceptual thresholds for edits — gap detection: https://pmc.ncbi.nlm.nih.gov/articles/PMC4131718/ ; https://hearinghealthmatters.org/pathways-society/2022/part-1-gap-detection-the-past-present-and-future/ ; crossfade practice: https://www.descript.com/blog/article/crossfade-audio-what-crossfade-is-and-how-to-edit-it ; https://podcastengineeringschool.com/crossfading-when-editing-audio/ ; US patent 7,292,902
- Type: paper / blog / legal(patent)
- Verified: snippet-only
- Key facts: gap-detection threshold in silence/noise ≈2–5 ms for normal hearing; gaps near sound onset must be >50 ms to be perceptible; crossfades <5 ms are "not as effective at suppressing audible clicks", "a few milliseconds to low tens of milliseconds" renders thumps inaudible; >100 ms crossfade makes the mixed content "apparent and most likely annoying"; "a few milliseconds is enough for a hard edit in speech". No source found that measures listener detection of *content* discontinuity (a mid-word cut) as a function of boundary error — gap.
- Relevance: two separate budgets: (a) click/thump — solved by a 5–20 ms crossfade regardless of timestamp accuracy; (b) content — a cut landing inside a word/phoneme is audible; keeping edges within ~50 ms of a word boundary and snapping into the adjacent pause (≥100–200 ms typical inter-sentence pause) makes the skip effectively invisible. 50 ms is achievable (S37).

### S46. Koenecke et al., "Careless Whisper: Speech-to-Text Hallucination Harms" (FAccT 2024, arXiv 2402.08021) — https://arxiv.org/abs/2402.08021
- Type: paper
- Verified: fetched (abstract page)
- Key facts: "roughly 1% of audio transcriptions contained entire hallucinated phrases or sentences" absent from the audio; 38% of those hallucinations carry explicit harms; hallucinations concentrate on speakers with longer non-vocal durations (pauses) — Whisper "seeded by noise rather than actual speech"; Whisper (2023 API) tested; no mitigation prescribed.
- Relevance: podcast ads are preceded/followed by pauses and music beds — the exact trigger condition; a hallucinated sentence at an ad boundary can (a) fail the verbatim-evidence rung or (b) shift the boundary.

### S47. Sanchit Gandhi (HF) on `return_timestamps=True` and hallucination — https://huggingface.co/posts/sanchit-gandhi/950358996719386
- Type: forum/blog post
- Verified: fetched
- Key facts: forcing timestamp prediction constrains repeated tokens: "it's impossible to fit 3 copies of 'on the' within the time allocation given to the segment"; author labels it a hypothesis needing validation. Search snippet (Distil-Whisper paper, arXiv 2311.00430): 30 s is the optimal chunk for chunked long-form; long pauses in long-form raise hallucination propensity.
- Relevance: always request timestamps from Whisper even when only text is needed; it is a free hallucination damper.

### S48. WhisperX paper (Bain et al., INTERSPEECH 2023, arXiv 2303.00747) — https://arxiv.org/abs/2303.00747
- Type: paper
- Verified: snippet-only (README S12 fetched)
- Key facts: buffered/sliding-window long-form "is prone to drifting, hallucination & repetition"; VAD "Cut & Merge" into ≤30 s speech-only chunks lets Whisper run all chunks in parallel, "lowers word error rate and cuts hallucination", and removes reliance on decoded timestamp tokens.
- Relevance: VAD-first chunking is the proven strategy for preserving global timestamps over 2 h+ episodes (Q7) while suppressing music/silence hallucination (Q4).

### S49. snakers4/silero-vad — https://github.com/snakers4/silero-vad
- Type: repo
- Verified: fetched
- Key facts: "One audio chunk (30+ ms) takes less than 1ms" on one CPU thread; ~2 MB JIT model; ONNX runtime "up to 4-5x faster"; 8/16 kHz; trained on 6000+ languages; MIT, no telemetry/keys; ports in C++, Rust, Go, Java, C#.
- Relevance: near-zero-cost pre-segmentation and silence-snapping oracle for edges; used by faster-whisper (S9), whisper.cpp (S8), stable-ts (S43), WhisperX (S12).

### S50. Gemini API — Audio understanding — https://ai.google.dev/gemini-api/docs/audio
- Type: docs
- Verified: fetched
- Key facts: 13+ formats; "9.5 hours of audio per prompt"; "32 tokens per second of audio (1 minute = 1,920 tokens)" → 115,200 tokens/hour; audio downsampled to 16 kbps, channels mixed to mono; timestamps referenced as `MM:SS` in prompts (e.g. "transcript from 02:30 to 03:29"); no accuracy guarantee stated; inline requests ≤20 MB, Files API above that; examples use `gemini-3.7-flash`.
- Relevance: an entire 2 h episode fits one prompt (230k audio tokens) — the "send the audio, ask for ad ranges" path is technically possible and cheap (S51) but see S52–S53 for timing reliability.

### S51. Gemini API pricing — https://ai.google.dev/gemini-api/docs/pricing
- Type: product pricing
- Verified: fetched
- Key facts (per 1M input tokens, audio): Gemini 2.5 Pro $1.00 (output $10); 2.5 Flash $1.00 (output $2.50); 2.5 Flash-Lite $0.30 (output $0.40); Gemini 3 Flash Preview $1.00 (output $3.00); 3.1 Flash-Lite $0.50 (output $1.50); 3.7/3.6 Flash audio $1.00 (text $0.75 in / $3.75 out through 2026-12-31); Batch/Flex ≈50% off. Derived: 1 h audio = 115,200 tokens → $0.115/h (Flash-class), $0.035/h (2.5 Flash-Lite), $0.058/h (3.1 Flash-Lite); batch halves these.
- Relevance: audio-native Gemini is 2–5x cheaper per hour than any word-timestamped cloud STT — cost is not the obstacle, timing is.

### S52. Google AI forum bug: "Gemini 3 Flash and 3.1 Pro: progressive timestamp drift in audio transcription" — https://discuss.ai.google.dev/t/bug-gemini-3-flash-and-3-1-pro-progressive-timestamp-drift-in-audio-transcription/129501
- Type: forum (bug report with measurements)
- Verified: fetched
- Key facts: 11:49 Arabic lecture; Gemini 3 Flash timestamps span only 0:00–9:14, drift reaching −157 s (≈22% clock-rate error); 3.1 Pro −16 s by the end, non-linear; 3.1 Flash-Lite mean absolute drift 1.25–2.09 s with no progressive drift; 3.5 Flash reported to share the issue; no Google response as of Aug 2026; workarounds: ≤5-min chunks, two-pass (Flash-Lite for timing, Pro for text), minimal thinking.
- Relevance: even the best case (Flash-Lite, ~1–2 s MAE) is 20–40x worse than forced alignment; worst case is minutes. Disqualifies raw audio-LLM timestamps as the edge source; still viable as a coarse (±10 s) candidate finder.

### S53. Towards Data Science, "Building a scalable and accurate audio interview transcription pipeline with Google Gemini" — https://towardsdatascience.com/building-a-scalable-and-accurate-audio-interview-transcription-pipeline-with-google-gemini/
- Type: blog (practitioner measurements)
- Verified: fetched
- Key facts: Gemini 2.0 Flash: few-minute files drift 5–10 s; hour-long interviews "over 10 minutes" of drift when continuing past the output-token limit; fix = 10-minute audio chunks with 30 s overlap → drift "5 to 10 seconds max" over >1 h, also suppressed the repetition bug and cut cost.
- Relevance: independent confirmation of S52; also shows chunk-level timestamp anchoring is mandatory for any audio-LLM path.

### S54. Other Gemini timestamp threads — https://discuss.ai.google.dev/t/gemini-pro-timestamp-accuracy-issues-in-audio-transcription/52587 ; https://discuss.ai.google.dev/t/audio-timestamp-accuracy-issue-in-gemini-2-0-ga-models/72114 ; https://github.com/google-gemini/cookbook/issues/733 ; https://news.ycombinator.com/item?id=45971339
- Type: forum
- Verified: snippet-only
- Key facts: 2.0 GA models lost timestamp accuracy that preview had; wrapping the same audio in a video container restored accurate timestamps (video frames carry explicit timing); "refer to timestamps" prompt returns random portions; HN commenter: "Gemini has no insight into the time stamps" beyond token counting.
- Relevance: the video-container trick suggests audio-LLM timing comes from token position, not perception; a pipeline could exploit it (mux audio into a black-frame MP4) but this is a hack, not a guarantee.

### S55. Qwen3-Omni discussion #1: subtitling timestamps — https://github.com/QwenLM/Qwen3-Omni/discussions/1
- Type: forum
- Verified: fetched
- Key facts: timestamps "not precise (usually starts too early)" and "about 1 minute into the transcription the precision of the timestamps become very poor"; maintainer acknowledged, pointed to a transformers PR and a vLLM fork commit; temperature 0 helps marginally.
- Relevance: same failure class as Gemini in an open omni model; audio-native timestamps are not yet trustworthy anywhere.

### S56. Qwen3.5-Omni report (arXiv 2604.15804), Audio Flamingo 3 (arXiv 2507.08128), Kimi-Audio (arXiv 2504.18425) — https://arxiv.org/html/2604.15804v2 ; https://arxiv.org/html/2507.08128 ; https://arxiv.org/html/2504.18425v1
- Type: papers
- Verified: snippet-only
- Key facts: Qwen3.5-Omni prepends explicit second-valued timestamp strings to audio/video temporal patches and inserts them at random intervals in audio, with a temporal ID every 160 ms — a training-time fix for the S55 drift (accuracy not reported in snippet); Audio Flamingo 3 processes 30 s windows up to a 10-minute cap; Kimi-Audio derives training timestamps from Paraformer (character-level) — no native timestamp output claimed.
- Relevance: vendors know the drift problem and are training against it (Qwen3.5-Omni), but no published ms-level evaluation exists — gap.

### S57. pyannote/speaker-diarization-community-1 — https://huggingface.co/pyannote/speaker-diarization-community-1 (blog: https://www.pyannote.ai/blog/community-1)
- Type: model card / blog
- Verified: model card fetched; DER table snippet-only (pyannote.ai benchmark, updated 2025-09)
- Key facts: released with pyannote.audio 4.0 (~2 years after 3.1); "improved speaker assignment and counting", same segmentation as 3.1; exclusive-speaker mode ("only one speaker active at any time") to simplify STT word↔speaker alignment; CC-BY-4.0, gated (contact info), "will always remain freely accessible"; 16 kHz mono, CPU default, GPU via torch. Snippet DER: AMI SDM 19.9%, VoxConverse 11.2%, DIHARD3 20.2%, CALLHOME 26.7%, AliMeeting 20.3% (vs 24.5% for 3.1).
- Relevance: open diarization baseline; exclusive mode maps cleanly onto word streams; MPS/Apple speed not documented (gap).

### S58. Lanzendörfer et al., "Benchmarking Diarization Models" (arXiv 2509.26177) — https://arxiv.org/pdf/2509.26177
- Type: paper
- Verified: fetched (PDF partially extracted) + snippet
- Key facts: compares pyannote 3.1, community-1, DiariZen (WavLM + pyannote clustering), Sortformer, NeMo, and commercial pyannoteAI/AssemblyAI/Deepgram; 4-speaker DER: pyannoteAI 10.1%, DiariZen 12.7%, Sortformer v2-streaming 13.2%; DiariZen overall 13.3%, VoxConverse 5.2%; "Sortformer v2-streaming, DiariZen, and the commercial PyannoteAI models perform the best overall".
- Relevance: open models are within ~3 DER points of the best commercial; 2-speaker (host + guest) cases are much easier than these averages.

### S59. nvidia/diar_streaming_sortformer_4spk-v2 — https://huggingface.co/nvidia/diar_streaming_sortformer_4spk-v2
- Type: model card
- Verified: fetched
- Key facts: ≤4 speakers (degrades at 5+); 117M params; DER with post-processing (10 s latency config): DIHARD III 1–4 spk 13.75%, CALLHOME 2-spk 6.05%, 3-spk 9.88%, 4-spk 11.72%; latency presets 30.4 s (RTF 0.002) … 0.32 s (RTF 0.180) on RTX 6000 Ada; CC-BY-4.0; released 2025-07-24.
- Relevance: small enough for CPU/MPS; 2-speaker DER ~6% is good for host/guest podcasts; no MLX port found (gap).

### S60. AssemblyAI / Deepgram diarization pricing (from S24, S26)
- Type: product pricing
- Verified: fetched (as part of S24/S26)
- Key facts: Deepgram pre-recorded diarization included at $0; AssemblyAI +$0.02/h; ElevenLabs Scribe includes diarization (S29); Gladia includes it (S27); OpenAI diarization only via gpt-4o-transcribe-diarize at $0.36/h with segment-level output (S22–S23).
- Relevance: speaker-change signal is essentially free from cloud STT; locally it costs a second model.

### S61. Chunking / long-file limits (cross-reference of fetched facts)
- Type: synthesis of S4, S7, S12, S13, S16, S18, S22, S29
- Verified: fetched (each underlying fact)
- Key facts: OpenAI 25 MB/request (≈ 2 h 15 min of 24 kbps mono MP3 — approx., derived) (S22); Parakeet TDT 24 min full attention / 3 h local attention (S4); parakeet-mlx 120 s chunks + 15 s overlap (S13); Whisper 30 s windows, chunked vs sequential (S7); WhisperX VAD cut&merge ≤30 s (S48); Qwen3-ASR 1200 s max (S18); Qwen3-ForcedAligner 5 min (S19); Voxtral Mini Transcribe V2 3 h (S16); ElevenLabs Scribe 10 h / 3 GB (S29); Gemini 9.5 h per prompt (S50). ffmpeg demux: not fetched (no budget); the standard command `ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le out.wav` is general knowledge, unverified against docs in this run.
- Relevance: every local model needs a chunker that carries a global offset; every cloud vendor except OpenAI accepts ≥3 h whole files.

### S62. Mistral, "Voxtral" (July 2025 open-weights release) — https://mistral.ai/news/voxtral
- Type: product announcement
- Verified: fetched (resolves gap S17)
- Key facts (2025-07-15): Voxtral 24B and Voxtral Mini 3B, both Apache 2.0; "audios up to 30 minutes for transcription, or 40 minutes for understanding" (32k context); claims to "comprehensively outperform Whisper large-v3" and beat GPT-4o mini Transcribe, Gemini 2.5 Flash, Scribe on their benchmarks; API from $0.001/min; **word-level timestamps explicitly listed under "Coming up"**, i.e. NOT in the July-2025 open models.
- Relevance: the open Voxtral 3B/24B weights cannot supply word edges; only the Feb-2026 API (S16) does.

### S63. mistralai/Voxtral-Mini-4B-Realtime-2602 model card — https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602
- Type: model card
- Verified: fetched
- Key facts: 4B (≈3.4B LM + ≈0.97B audio encoder); Apache 2.0; 13 languages; FLEURS avg WER 8.72% at 480 ms delay; delay configurable 80 ms–2.4 s; inference via vLLM (recommended), transformers ≥5.2, ExecuTorch; community ports in C, Rust, MLX and mlx-audio; paper arXiv 2602.11298 (2026-02-11); word-timestamp output NOT documented.
- Relevance: an MLX-runnable open streaming model, but no documented word timing → would still need an aligner.

### S64. torchaudio MMS_FA forced-alignment tutorial — https://docs.pytorch.org/audio/stable/tutorials/forced_alignment_for_multilingual_data_tutorial.html
- Type: docs
- Verified: fetched (resolves gap in S40)
- Key facts: 20 ms frames; acoustic model trained on "23,000 hours of audio from 1100+ languages"; word spans from token frame spans; text must be lowercased, romanised (uroman), stripped of punctuation; tokenizer has ~29 characters; **"APIs are deprecated in 2.8 and will be removed in 2.9"** (torchaudio forced-alignment API being removed).
- Relevance: torchaudio's built-in aligner is going away — do not build on `torchaudio.functional.forced_align`; use ctc-forced-aligner (S40, NC model) or Qwen3-ForcedAligner (S19).

### S65. nvidia/canary-1b-v2 model card — https://huggingface.co/nvidia/canary-1b-v2
- Type: model card
- Verified: fetched
- Key facts: 25 European languages; Open ASR mean WER 7.15%, RTFx 749; "word and segment level timestamps" via NeMo `.transcribe(timestamps=True)`; long-form via dynamic chunking with 1 s overlap beyond 40 s; CC-BY-4.0; released 2025-08-14.
- Relevance: a timestamp-capable encoder-decoder alternative to Parakeet, but slower (RTFx 749 vs 3333) and worse WER than parakeet-tdt-0.6b-v3 on the same board (6.34%) — Parakeet TDT remains the better local choice.

### S66. kyutai/stt-2.6b-en model card — https://huggingface.co/kyutai/stt-2.6b-en
- Type: model card
- Verified: fetched (upgrades S14 figures from snippet to fetched)
- Key facts: Open ASR mean WER 6.4, AMI 12.17; RTFx 88.37; CC-BY 4.0; 2.5 s delay; word timestamps recovered "by subtracting the model's text stream offset (0.5 or 2.5 seconds) from the frame's offset" (frame-based, so 80 ms-granular — approx., inferred from Mimi frame rate, not stated); semantic VAD only in the 1B en_fr model.
- Relevance: competitive WER with native frame-level word timing; RTFx 88 on GPU means it is slow relative to Parakeet — on Mac expect roughly real-time-ish (unmeasured).

### S67. linto-ai/whisper-timestamped README — https://github.com/linto-ai/whisper-timestamped
- Type: repo
- Verified: fetched (upgrades S44)
- Key facts: DTW on cross-attention (Jong Wook Kim notebook lineage), `get_alignment_heads()`; VAD via Silero (v3.1/v4.0), auditok or custom; disfluency `[*]` tokens; word confidence; critiques timestamp-token-probability methods (whisper.cpp / early stable-ts): "can produce results that are totally out-of-sync on some periods of time"; **AGPL-3.0**; backends openai-whisper and HF transformers (no faster-whisper).
- Relevance: AGPL is incompatible with a permissively licensed public CLI unless isolated; prefer stable-ts (MIT, S43) or a CTC/LLM aligner.

### S68. Deepgram, "Introducing Nova-3" — https://deepgram.com/learn/introducing-nova-3-speech-to-text-api
- Type: blog (vendor benchmark)
- Verified: fetched (upgrades S25)
- Key facts: median WER 5.26% batch / 6.84% streaming on a 2,703-file, 81.69 h, nine-domain set that includes a **Podcast** domain; "Greater word-level timestamp precision" claimed without a number; keyterm prompting up to 100 terms; 10 languages real-time; "starting at $0.0077 per minute" streaming.
- Relevance: keyterms (brand names/promo codes) + free diarization + default word timestamps make Nova-3 the most complete cloud package for AdVTT; timestamp precision remains unquantified by the vendor.

### S69. AssemblyAI word-level timestamps docs — https://www.assemblyai.com/docs/speech-to-text/pre-recorded-audio/word-level-timestamps
- Type: docs
- Verified: fetched
- Key facts: each word has `text`, `start` (ms), `end` (ms), `confidence` (0–1), `speaker`; no accuracy statement; no per-model caveats listed.
- Relevance: confirms AssemblyAI returns ms-unit word timestamps at the base price (S26).

### S70. pyannoteAI benchmark page — https://www.pyannote.ai/benchmark
- Type: product benchmark
- Verified: fetched (table is a graphic; numbers not extractable)
- Key facts: compares Precision-2, OSS Community-1 and 8 competitors over 10 DIHARD-style domains, ~67 h audio, pyannote.metrics; last updated 2026-09-02. DER values in S57 (snippet) could not be re-verified here.
- Relevance: none beyond corroborating that community-1 is the open baseline vendors compare against.

### Failed fetches this run (recorded as gaps)
- https://cloud.google.com/speech-to-text/pricing (and docs.cloud.google.com redirect) — dynamic table, no prices retrieved. Chirp 3 price unknown.
- https://docs.speechmatics.com/introduction/pricing — 404. Speechmatics per-hour price unit unverified (S28).
- https://developers.openai.com/api/docs/guides/audio — no audio-token-rate information; tokens/second for gpt-audio/gpt-realtime unverified.
- https://openai.com/api/pricing/ — 403 (pricing taken from developers.openai.com instead, S23).

### S71. ffmpeg documentation (ffmpeg.html) — https://ffmpeg.org/ffmpeg.html
- Type: spec/docs
- Verified: fetched
- Key facts: `-vn` disables video; `-ac 1` mono; `-ar 16000` sets sample rate; `-c:a pcm_s16le` 16-bit PCM WAV; `-ss` before `-i` seeks via input seek points ("seek to the closest seek point before position") and with default `-accurate_seek` the extra segment "will be decoded and discarded" when transcoding, so cuts are sample-accurate; `-t` limits duration. Command for AdVTT: `ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le out.wav` (16 kHz mono ≈ 115 MB/h uncompressed — derived).
- Relevance: one-line demux for video inputs; `-ss/-t` with accurate seek is also how to cut ≤5-min windows for a forced aligner without timestamp offset error.

### S72. OpenAI gpt-realtime model page — https://developers.openai.com/api/docs/models/gpt-realtime
- Type: docs
- Verified: fetched
- Key facts: 32,000-token context; audio input $32 per 1M tokens; max audio length and audio-tokens-per-second NOT stated; no timestamp output documented.
- Relevance: a 32k context cannot hold an hour of audio at any plausible token rate (at even 10 tok/s an hour is 36k tokens — approx.), so GPT-audio is unusable for whole-episode classification; per-hour cost cannot be computed from primary sources (gap).

### S73. Gemma audio understanding docs — https://ai.google.dev/gemma/docs/capabilities/audio
- Type: docs
- Verified: fetched (upgrades S21)
- Key facts: Gemma 3n and Gemma 4 (E2B/E4B/12B) accept audio; "Audio supports a maximum length of 30 seconds"; 25 tokens/s (Gemma 4), 6.25 tokens/s (3n); tasks: ASR and speech translation; no timestamp or speaker features documented.
- Relevance: 30 s cap rules Gemma out for anything but a per-chunk local ASR fallback.

## Synthesis

**Q1 — Local STT with word timestamps (WER = Open ASR avg unless noted; RTFx are H200/GPU figures, S2).**

| Model | Avg WER | Word timestamps | Speed note | Licence | Src |
|---|---|---|---|---|---|
| parakeet-tdt-0.6b-v2 (EN) | 6.05% | native (TDT durations) | RTFx 3386 GPU; parakeet-mlx on Mac (speed undocumented) | CC-BY-4.0 | S5, S13 |
| parakeet-tdt-0.6b-v3 (25 langs) | 6.34% | native | RTFx 3333; 24 min/pass, 3 h local-attn | CC-BY-4.0 | S4 |
| canary-1b-v2 | 7.15% | native (NeMo `timestamps=True`) | RTFx 749 | CC-BY-4.0 | S65 |
| canary-qwen-2.5b | 5.63% (#1) | none | RTFx 418; 40 s training max | CC-BY-4.0 | S6 |
| whisper large-v3 / v3-turbo | 7.4% / 7.75% | cross-attention DTW (drifty, S36) | turbo RTFx 216; mlx-whisper, whisper.cpp, faster-whisper | MIT | S3, S7–S10 |
| kyutai stt-2.6b-en | 6.4% | native frame offsets | RTFx 88; MLX port | CC-BY-4.0 | S14, S66 |
| Qwen3-ASR 0.6B/1.7B | LibriSpeech 1.63/3.38 (1.7B); board avg not obtained | via Qwen3-ForcedAligner (AAS ≈25–28 ms) | RTF 0.009–0.015 GPU; 1200 s/request | aligner Apache-2.0; ASR licence not verified | S18, S19 |
| granite-speech-3.3-8b | 5.74% | none | 9B | Apache-2.0 | S20 |
| Voxtral Mini 3B / 24B (open) | vendor claims > Whisper v3 | none ("coming up") | 30 min max | Apache-2.0 | S62 |
| Voxtral Realtime 4B (open) | FLEURS 8.72% @480 ms | not documented | MLX/mlx-audio ports | Apache-2.0 | S63 |
| Moonshine | vendor claim > Whisper v3 | not documented | edge/streaming | MIT | S15 |
| Gemma 3n / 4 | not published | none; 30 s cap | on-device | Gemma terms | S73 |

Contradiction/gap: the leaderboard itself could not be fetched (S1); WER values are as quoted by model cards and a late-2026 secondary (S3). No Apple-Silicon throughput number was obtainable for any model from primary sources (search budget exhausted) — every "speed on Mac" claim in this track is unmeasured.

Pattern: the two accuracy leaders (Canary-Qwen, Granite) are LLM-decoder models with **no** timestamps; the timestamp-native models (Parakeet TDT, Canary-1b, Kyutai) trail by 0.5–1.5 WER points. Whisper is the only family whose word timing is derived post hoc from attention and it has a documented systematic error (pauses absorbed into adjacent words, only 13% of spaces tokenised explicitly — S36).

**Q2 — Cloud STT, $/hour, word timestamps (2026-09 list prices).**

| Provider / model | $/h (PAYG) | Word timestamps | Notes | Src |
|---|---|---|---|---|
| OpenAI whisper-1 | 0.36 | yes (`timestamp_granularities`) | 25 MB/request; 224-token prompt | S22, S23 |
| OpenAI gpt-transcribe / gpt-4o-transcribe | 0.36 | **no** | `keywords` param | S22, S23 |
| OpenAI gpt-4o-mini-transcribe | 0.18 | **no** | | S22, S23 |
| OpenAI gpt-4o-transcribe-diarize | 0.36 | segment-level only | | S22, S23 |
| Deepgram Nova-3 (mono / multi) | 0.258 / 0.312 (Growth 0.216) | yes, default | diarization free; 100 keyterms | S24, S68 |
| AssemblyAI Universal-2 / U-3.5 Pro | 0.15 / 0.21 | yes (ms) | diarization +0.02; keyterms +0.05; Slam-1 deprecated | S26, S69 |
| Gladia Solaria | 0.61 (Growth "as low as" 0.20) | yes | diarization incl. | S27 |
| ElevenLabs Scribe v2 | 0.22 | yes + `audio_event` | 10 h / 3 GB; keyterms +0.05 | S29, S30 |
| Mistral Voxtral Mini Transcribe V2 | 0.18 | yes | 3 h/request; 100-term context bias; diarization | S16 |
| Rev.ai Reverb / Turbo | 0.20 / 0.10 | not verified | | S34 |
| Amazon Transcribe batch | 0.36 (page example; legacy tier snippets say 1.44) | standard (not re-verified) | contradiction noted | S32 |
| Azure batch / real-time | ≈0.18 / 1.00 (snippet-only) | standard (not re-verified) | 5 h/mo free | S33 |
| Speechmatics | not verified (a "$0.129" figure, unit unclear) | yes (snippet) | $100 credit | S28 |
| Google Chirp 3 | not obtained | yes (docs snippet) | gap | S31 |

Headline: OpenAI's current models are the *only* major cloud STT family without word timestamps (S22). Gladia (AdVTT's present cloud seam) is the most expensive PAYG option found, 2–4x Deepgram/AssemblyAI/Voxtral (S27 vs S24/S26/S16).

**Q3 — Achievable timestamp accuracy.** Forced aligners on read/conversational English: MFA puts 72.8% of word boundaries within 25 ms and 89.4% within 50 ms (TIMIT); WhisperX 52.7% within 20 ms (S37). CTC aligners with label priors reach ~30 ms phone-boundary error (S39). Qwen3-ForcedAligner reports 27.8 ms accumulated average shift, 24.8 ms on 300 s audio, vs MFA 49.9 / NFA 88.6 ms on its own human-labelled sets (S18). Raw Whisper cross-attention timing: F1@50 ms ≈ 75% clean / 68% noisy for large-v2, 84.7/79.5 for CrisperWhisper, WhisperX 76.7/59.0 (S36); practitioner measurements show a heavy tail (average 200 ms, best-80% 40 ms; 100–400 ms variant-to-variant disagreement — S38, snippet). So: **≈50 ms word-onset accuracy is routinely achievable with an aligner; 25–30 ms mean with the best; unaligned Whisper is in the 100–400 ms tail regime.**
Perceptual side (S45, snippet-level): clicks/thumps are a separate problem solved by a 5–20 ms crossfade; crossfades >100 ms become audible as a blend; gap-detection thresholds are 2–5 ms but a *content* discontinuity (cut inside a word) is what listeners notice. No study directly measuring "acceptable skip-edge error in speech" was found — gap. Reasonable engineering target: land edges within 50 ms of a word boundary and prefer snapping into the adjacent pause (typical inter-sentence pauses are hundreds of ms), then crossfade 10–20 ms.

**Q4 — Whisper failure modes.** ~1% of transcriptions contain wholly hallucinated sentences, concentrated where non-vocal stretches are long (S46) — i.e. at music beds and pauses around ads. Sliding-window long-form "is prone to drifting, hallucination & repetition" (S48). Mitigations with evidence: VAD cut-and-merge into ≤30 s speech-only chunks (S48, S12), Silero VAD at <1 ms/chunk (S49), `return_timestamps=True` (S47), drop tokens <50 ms to kill loops (S36), `condition_on_previous_text=False` and `vad_filter` in faster-whisper (S9), silence-snapping in stable-ts (S43). Brand vocabulary: whisper-1 `prompt` (224 tokens), Deepgram/Voxtral 100 keyterms, AssemblyAI keyterms (+$0.05/h), gpt-transcribe `keywords` (S22, S68, S16, S26). Not found: a published measurement of Whisper on spelled-out URLs/promo codes — but WhisperX documents that tokens with digits/symbols ("£13.60") receive **no** alignment (S12), which is exactly the ad-edge vocabulary.

**Q5 — Audio-native LLMs.** Gemini accepts 9.5 h per prompt at 32 tokens/s (S50) → a 2 h episode ≈ 230k tokens ≈ $0.23 at Flash rates, $0.07 at 2.5 Flash-Lite, half in batch (S51) — cheaper than any STT. But measured timestamp behaviour is bad: Gemini 3 Flash −157 s drift over an 11:49 clip (22% clock error), 3.1 Pro −16 s, 3.1 Flash-Lite 1.25–2.09 s MAE (S52); Gemini 2.0 Flash >10 min drift on hour-long audio, 5–10 s with 10-min chunks (S53); Qwen3-Omni "very poor" after ~1 min (S55); OpenAI gpt-audio/realtime has a 32k context and no timestamps (S72). Qwen3.5-Omni now trains with explicit timestamp strings and 160 ms temporal IDs (S56) — a signal that vendors are fixing this, but no ms-level evaluation exists. Verdict: audio-native models cannot supply edges today; they might supply cheap *coarse* candidates (±5–10 s) if chunked to ≤5–10 min with explicit offsets.

**Q6 — Diarization.** Open baselines: pyannote community-1 (CC-BY-4.0, exclusive-speaker mode designed for word alignment; DER 11–27% across hard sets — S57), Sortformer streaming v2 (≤4 speakers, 117M params, CALLHOME 2-spk DER 6.05% — S59), DiariZen 12.7–13.3% (S58). Commercial pyannoteAI ~10% at 4 speakers (S58). Cloud STT bundles diarization at $0–0.02/h (S60). No Apple-Silicon speed figures were obtainable (gap). For AdVTT's target (host-read ads in the host's voice — brief), speaker change is by construction absent at most ad edges; it is a strong signal only for produced/third-party spots and guest→host transitions.

**Q7 — Practical.** Demux: `ffmpeg -i in.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le out.wav`; `-ss` before `-i` with default accurate seek gives sample-exact cuts for aligner windows (S71). Long files: Parakeet 24 min/pass (3 h with local attention) (S4), parakeet-mlx 120 s/15 s overlap (S13), Whisper 30 s windows (S7), Qwen3-ASR 1200 s (S18), Qwen3-ForcedAligner 5 min (S19), Voxtral API 3 h (S16), Scribe 10 h (S29), Gemini 9.5 h (S50), OpenAI 25 MB (≈1.7 h at 32 kbps mono, approx.) (S22). Drift-free strategy with evidence: VAD-derived chunks with global offsets, parallel decode, timestamps from chunk start + offset (S48); avoid buffered/sliding-window decoding.

## Implications for AdVTT

1. **Default STT per platform.** macOS/Apple Silicon: keep `parakeet-mlx` with `parakeet-tdt-0.6b-v2` for English (6.05% WER, native word timestamps, no attention-DTW pathology) and `-v3` for other languages (S4, S5, S13); use `mlx-whisper large-v3-turbo` only as fallback and then always through `stable-ts` silence-snapping (S7, S43). Linux/Windows: `faster-whisper large-v3-turbo` with `vad_filter=True`, `word_timestamps=True`, `condition_on_previous_text=False`, temperature 0 (S9) — or NeMo Parakeet if a CUDA GPU is present. Cloud default: **Deepgram Nova-3** ($0.26/h, word timestamps + free diarization + 100 keyterms, podcast domain in its benchmark — S24, S68), with **Voxtral Mini Transcribe V2** ($0.18/h, 3 h per request, context biasing — S16) and **AssemblyAI Universal-2** ($0.15/h — S26) as alternates. Demote Gladia (2–4x price — S27) and drop OpenAI `gpt-4o-transcribe` from the STT seam entirely: it returns no word timestamps (S22); keep `whisper-1` only for users who insist on OpenAI.
2. **Add a scoped forced-alignment/snap stage for edges — yes.** The current ship gate `boundary_err_sec ≤ 3 s` is ~60x looser than what aligners deliver (≈50 ms for 90% of words — S37; 25–28 ms mean with Qwen3-ForcedAligner — S18). Do not align whole episodes: cut a ≤5-min window around each candidate edge with `ffmpeg -ss … -t …` (S71) and run `Qwen3-ForcedAligner-0.6B` (Apache 2.0, accepts any transcript — S19) or, cheaper, snap the LLM-chosen word edge to the nearest Silero-VAD silence boundary (S49, S43). Avoid `torchaudio.functional.forced_align` (deprecated 2.8, removed 2.9 — S64), the default MMS aligner in `ctc-forced-aligner` (CC-BY-NC — S40), and `whisper-timestamped` (AGPL — S67). New metric: `edge_err_ms` with a target ≤100 ms, plus a player-side 10–20 ms crossfade (S45).
3. **Audio-native LLMs are not a replacement path in 2026** for edges (drift of seconds to minutes — S52, S53, S55; OpenAI 32k context, no timestamps — S72). They *are* worth one experiment as a cheap first-pass candidate finder: Gemini 2.5/3.1 Flash-Lite at $0.035–0.058/h (S51) on 5–10-min chunks with explicit start offsets, feeding candidates into the existing STT→LLM validation ladder. Cost is a non-issue; precision is the whole question.
4. **Harden the Whisper path against ad-adjacent hallucination.** Music beds and pauses are Whisper's known hallucination triggers (S46, S48). Make VAD pre-segmentation mandatory for Whisper backends, always request timestamps (S47), drop <50 ms tokens (S36), and treat any segment whose text has no VAD speech under it as suspect. Because digits/symbols are un-alignable in wav2vec2 aligners (S12), the **verbatim evidence-quote rung should match on a normalised form** (strip punctuation/case, fold digits) or it will halve confidence exactly on promo codes and URLs.
5. **Brand vocabulary is a first-class input, not a Whisper-only trick.** Every recommended backend has a keyterm hook: Deepgram/Voxtral 100 terms, AssemblyAI keyterms, whisper-1 224-token prompt, gpt-transcribe `keywords` (S68, S16, S26, S22). Expose an `--advertisers` list in the CLI and pass it through the seam; it improves both transcript fidelity and evidence-quote matching.
6. **Diarization: optional flag, not a core boundary signal.** For host-read ads the speaker does not change (brief), so speaker turns cannot mark most edges; they do help for produced spots and to demote guest dialogue (the dialogue-density rung). Use cloud diarization when it is free (Deepgram — S24) and pyannote community-1 exclusive mode locally when requested (S57); attach `speaker` to words in the internal word stream so the LLM windows can see turns.
7. **Provenance in the output track.** Record for each cue edge how it was placed (`stt-word`, `aligner`, `vad-snap`, `llm-coarse`) and the estimated error (ms); the false-positive asymmetry principle then lets the player pad skips conservatively (start late, end early) when provenance is coarse (S52 vs S18 accuracy gap).
8. **Chunking contract.** Standardise the seam on 16 kHz mono PCM (S71), VAD cut-and-merge chunks ≤ backend max (30 s Whisper; 120 s parakeet-mlx; 1200 s Qwen3-ASR; whole-file for cloud except OpenAI's 25 MB) and *always* express words in absolute episode seconds (S48, S61). For OpenAI whisper-1, re-encode to ~32 kbps mono before chunking so ≥1.5 h fits one request (approx.).

## Open questions / things that need an experiment

1. **Apple Silicon throughput** for parakeet-mlx (v2/v3), mlx-whisper large-v3-turbo, Kyutai MLX, Voxtral Realtime MLX and Qwen3-ForcedAligner on MPS/CPU — no primary numbers exist; measure hours-of-audio-per-minute on an M-series box.
2. **Measured word-onset error of Parakeet TDT** vs an aligner on AdVTT's 4 fixtures: TDT emits frame-quantised durations (80 ms frames — inferred, not verified); is that already ≤100 ms at ad edges, making the aligner unnecessary?
3. **Pause statistics at real ad edges**: how often is there ≥200 ms of silence within ±1 s of the true boundary (making VAD-snap sufficient)? Needs measurement on labelled episodes.
4. **Gemini Flash-Lite coarse-candidate experiment**: recall and ±s error of "list ad time ranges" on 5–10-min chunks, versus the current pipeline's candidate stage; cost per episode.
5. **Evidence-quote robustness**: rate at which verbatim matching fails on brand names/URLs/prices per backend; whether normalised matching removes those failures without admitting false matches.
6. **Pricing gaps**: Google Chirp 3 and Speechmatics per-hour prices; Amazon batch $0.36 vs legacy $1.44 tier; verify OpenAI audio-token rate to cost gpt-audio (S31, S28, S32, S72).
7. **Open ASR long-form (earnings21/22, CORAAL) table**: which timestamp-capable model wins on long-form specifically (S2) — needs a browser read of the leaderboard.
8. **ElevenLabs `audio_event` tags** as a free jingle/music-bed detector for produced-spot edges (S29): precision on podcast audio unknown.
9. **Qwen3-ASR licence and leaderboard WER** (only the aligner's Apache-2.0 was verified — S19); and whether an MLX port of Qwen3-ForcedAligner exists.
10. **Perceptual tolerance study**: no source quantifies how far a skip edge can stray from a word boundary before listeners notice; a small ABX on the fixtures (edge offsets 0/50/100/250 ms, 10 ms crossfade) would settle the `edge_err_ms` target.
