# NotebookLM deep-dive prompt — AdVTT

Paste the block below into NotebookLM's Audio Overview customisation field after
loading these sources: `README.md`, `Research/01`–`06`, `07-research-log.md`,
`08-recommendation-and-trajectory.md`, `09-project-brief.md`, and every file in
`Research/research-log/` (the brief, local grounding, and tracks A–J).

---

Produce a deep-dive episode about AdVTT, an open-source tool that finds
advertising and sponsorship inside finished podcast audio and writes the result
as time-based metadata instead of cutting the audio. Treat
`08-recommendation-and-trajectory.md` as the authoritative current plan and
`09-project-brief.md` as the summary; the numbered documents 01 to 06 are the
earlier design that the research spike partly superseded, so when they
disagree with 08, say what changed and why. The track files A through J are the
evidence; cite specific findings from them where they make the story concrete.

Cover these points, in roughly this order:

1. The problem. Podcast ads are mostly host-read in the host's own voice, with
   no jingle or speaker change, so detection must be semantic over a
   transcript. Explain the governing principle: silently skipping journalism is
   far worse than failing to skip an ad, and every default (auto-skip off,
   conservative thresholds, rejected episodes produce no marks, the five-second
   content-loss ship gate) follows from that asymmetry.

2. What already works. The classifier extracted from PodcastFetch: tiled
   6,000-token windows with context margins, an LLM returning spans with a
   verbatim evidence quote, and the eight-rung validation ladder. Mention the
   measured facts: a single whole-episode call found the right sponsor text at
   the wrong position by about 800 segments, and a small model with thinking
   disabled falsely marked 77 seconds of journalism, which is why chunking and
   validation are accuracy mechanisms rather than cost workarounds.

3. The prior-art surprise. Several open-source tools (Podly, MinusPod, ZeroAds)
   already do transcript-plus-LLM detection, but all of them cut audio into a
   private feed. None publishes a portable, typed, confidence-bearing record.
   MinusPod's public benchmark and its tricks (verification pass, differential
   download, loudness-jump detection) are worth describing. The interchange
   problem is open even though detection is crowded.

4. The format reversal. The original plan made a WebVTT metadata track the
   product. Research showed real players skip on chapters (ID3, MP4,
   Podcasting 2.0 JSON) and EDL files (Kodi, mpv, Jellyfin), and no surveyed
   player reads a WebVTT metadata track. The new design is a canonical JSON
   record, bound to the exact file by hash and duration, exported to many
   formats ranked by what works today. WebVTT stays as one exporter, hardened
   because its NOTE header is dropped by most parsers.

5. Vocabulary and policy. Adopt the categories SponsorBlock and Jellyfin
   already use, keep the advertisement-versus-sponsorship distinction as a
   sub-field, and separate what a segment is from what a player should do with
   it. Explain why self-promotion and funding asks are never in the default
   skip set.

6. Pipeline changes with evidence. Quote-anchored spans instead of index-based
   ones, and the research on positional errors in long contexts. Replacing the
   thinking-budget knob with an intersection ensemble of a reasoning-on and a
   reasoning-off pass, and why agreement is a better confidence signal than a
   model's self-reported number. Local versus cloud model tiers and the rough
   cost per episode, from fractions of a cent to about fifteen cents.

7. Audio signals. Dynamic ad insertion carries about 92 percent of US podcast
   ad revenue while host reads are still about 46 percent of spend. Loudness
   steps and silence find splices, fingerprints find repeated produced spots,
   transcripts find host reads. Forced aligners can place edges within tens of
   milliseconds, while audio-native LLMs drift by seconds to minutes and cannot
   be trusted for edges.

8. Evaluation honesty. Four fixtures from two shows, also used to tune the
   prompt, cannot support a public accuracy claim; the rule of three says sixty
   clean episodes are needed. Describe the two-level metric suite, per-show
   confidence intervals, the replay store and drift canary, silver labels
   bootstrapped from SponsorBlock, and the proposed public labels-only
   benchmark, PodAd-Bench, which would be the first of its kind.

9. Legal and community posture. Fox v. Dish approved an ad-skip design with
   markers in a separate file, off by default, media untouched. The Podcast
   Index rejected an ad-range tag over ad-blocker fears; Pocket Casts and
   AntennaPod declined auto-skip. Hence annotation-only, local-only, Apache-2.0,
   transcripts never redistributed, opt-outs honoured, and the framing of
   time-resolved advertising disclosure rather than ad blocking. Say clearly
   that this is analysis, not legal advice.

10. The trajectory. Phase 0 decisions and five cheap experiments; Phase 1
    extraction with byte-identical regression; Phase 2 exporters and reference
    player; Phase 3 test set and benchmark; Phase 4 edge precision and acoustic
    channel; Phase 5 PodcastFetch re-consuming AdVTT and serving chapters over
    a private RSS feed; Phase 6 a distilled local proposer model and spec
    publication. Close with the biggest open risks: ensemble recall loss,
    untested Apple chapter behaviour, community reception, and model churn.

Tone: two curious, technically literate hosts explaining to a developer
audience. Be concrete with numbers and named sources, flag where evidence is
thin or contested, and do not invent features the documents do not describe.
Target length: 25 to 35 minutes.
