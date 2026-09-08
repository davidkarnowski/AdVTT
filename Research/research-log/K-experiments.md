# K — Experiments on the extracted classifier

Status: **in progress** (opened 2026-09-06). Written incrementally: every run is
appended when it finishes, never held back for a summary.

Scope: Research/12 WP2 exit run and the WP4 experiments K1–K5. All model calls
go through the `claude` CLI on the user's subscription (decision C.3 as
clarified: no paid API access). Cost figures are the CLI's own
`total_cost_usd`, reported for sizing, not billed separately.

Dev set: the four PodcastFetch fixtures (3 × The President's Daily Brief,
1 × Joe Rogan Experience), referenced by path, scored with `advtt --eval`.
They were used to tune the prompt and cannot support a public claim (track I).

Gates: `content_loss_sec ≤ 5` per episode (ship), `ad_recall_sec ≥ 0.70`,
`boundary_err_sec ≤ 3`.

---

## K0 — Extraction regression (WP1 exit), 2026-09-06

| Check | Result |
|---|---|
| `advtt --dump-prompt` vs `adclass.py --dump-prompt`, `--provider claude-cli`, all 4 fixtures | **byte-identical** (43,369 / 29,804 / 28,384 / 246,623 bytes) |
| Ported self-test (ladder items 1–15 + seam case) | all pass |
| pytest suite (11 tests: scripted-provider classification, extension byte-stability, captions reader, record mapping, replay round trip, offline mode) | all pass |

## K0b — CLI structured output probe, 2026-09-06

`claude -p --output-format json --json-schema <schema> --tools "" --exclude-dynamic-system-prompt-sections --effort low --model claude-haiku-4-5`
on a trivial prompt: envelope carries `structured_output` (parsed object) and
`result` (same JSON as a string); `num_turns` 2, `stop_reason` `tool_use`
(structured output is implemented as an internal tool call); usage shows
8,572 cache-creation tokens for the fixed prefix and `thinking_tokens` under
`output_tokens_details`; `total_cost_usd` 0.0187. `--effort` accepted.

## K0c — Live smoke test (WP2 exit, part 1), 2026-09-06

`advtt --stt <PDB 2026-08-07_2140> --provider claude-cli --model claude-sonnet-5 --record-replay`
(default effort, `--json-schema` on):

| Item | Value |
|---|---|
| segments / duration | 192 / 738.3 s |
| chunks | 1 |
| wall | 14.5 s |
| cost | $0.1039 |
| spans | ad-0001 sponsor 323.6–470.1 s conf 0.97 → skip; ad-0002 selfpromo (house) 679.8–688.6 s conf 0.90 → prompt |
| rejections | none |

Truth for this fixture has three spans (see PodcastFetch fixtures README);
scoring is in K0d below.

## K0d — Four-fixture eval, claude-sonnet-5, default effort (WP2 exit, part 2)

Command: `advtt --eval '<fixtures>/*/*_stt.json' --classify --provider claude-cli --model claude-sonnet-5 --record-replay`
(default effort, `--json-schema` on, prompt_version 2026-08-g). Run 2026-09-06 03:53–03:58 PT.

| Episode | Chunks | Wall (s) | CLI cost | True ad (s) | `content_loss_sec` | `ad_recall_sec` | `boundary_err_sec` | Spans found |
|---|---|---|---|---|---|---|---|---|
| PDB 2026-08-03_1000 | 2 | 39.0 | $0.111 | 212.6 | 0.0 | 1.000 | 0.00 | midroll 83–92, midroll 177–202, postroll 247–251 |
| PDB 2026-08-03_2252 (Israel trap) | 1 | 24.5 | $0.066 | 204.8 | 0.0 | 1.000 | 0.00 | midroll 74–97, house 143, postroll 146–157 |
| PDB 2026-08-07_2140 | 1 | 14.3 | $0.022 | 155.0 | 0.0 | 1.000 | 0.00 | midroll 81–125, house 178–179 |
| JRE 2026-08-07_1700 (foundation trap at 3179–3185) | 13 | 104.3 | $0.708 | 737.6 | 0.0 | 1.000 | 0.00 | 7 midrolls + postroll 3865–3918 |
| **Aggregate** | 17 | 182 | **$0.908** | 1310.0 | **0.0 PASS** | **1.000 PASS** | **0.00 PASS** | |

Observations:
- Every gate passes with zero content loss and full recall on the dev set,
  including both hand-built traps (the "support for Israel" phrasing in PDB and
  the guest's own-foundation pitch in JRE). No confidence was halved, no chunk
  failed, no rejections beyond none.
- Sonnet 5 at default effort through the CLI costs about $0.05 per PDB
  bulletin and $0.71 for a 156-minute JRE episode; the third PDB call cost a
  fifth of the same call in K0c because the Claude Code prefix was cache-warm.
- Chunk records carry `thinking_tokens`, cache read/write tokens and
  `cost_usd`, so K1's effort sweep can report cost and latency per setting
  without re-instrumenting.
- Caveat that stands: these four fixtures were used to tune the prompt. A
  perfect dev-set score is necessary, not sufficient (track I, rule of three).

## K0e — Offline replay reproduction, 2026-09-06

`--provider replay --model claude-sonnet-5 --offline` over the same fixtures
reproduces spans, flags and stats identically from `tests/replay/` (17
recorded responses) with no network. This is the WP2 exit criterion's second
half and the property the regression suite tests from now on.

## K0f — Real-audio no-ad control (WP3 exit), 2026-09-06

The NotebookLM episode (`Research/AI_hunts_for_host-read_ads.m4a`, 39.3 min,
Gladia transcript with word timings, 906 segments) is now a fixture under
`tests/fixtures/notebooklm/` with an empty truth file. It is a hard negative:
the two hosts talk about sponsor reads, promo codes and skipping for forty
minutes without ever delivering one.

`advtt --stt <fixture> --media <m4a> --provider claude-cli --model claude-sonnet-5 --record-replay`:

| Item | Value |
|---|---|
| chunks / wall / cost | 4 / 20.3 s / $0.173 |
| status / spans | ok / **0** (empty-is-valid rung) |
| record | `advtt/1.0`, media bound by duration 2359.333 s, 75,933,355 bytes, sha256 3b4e385f… |

This is the first no-ad control in the dev set (track I asked for ≥5); the
four PodcastFetch fixtures all contain ads. Its four responses are in the
replay store, so the control is part of the offline suite.

## K1a — Model comparison at default effort, dev set + control (overnight 2026-09-06)

Same four fixtures plus the NotebookLM control, `claude-cli`, default effort,
`--json-schema` on, replay recorded. Sonnet row from K0d.

| Model | Episodes | Total CLI cost | Total wall (s) | Σ content_loss | min recall | max boundary err | Any gate fail | Notes |
|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5 | 4 (+control $0.17) | $0.908 | 182 | 0.0 | 1.000 | 0.00 | no | perfect on dev set |
| claude-opus-5 | 4 (+control $0.45) | $2.633 | 121 | 0.0 | 0.961 | 2.70 | no | trims two PDB spans short (8 s and 5.4 s of ad left unmarked); faster wall than Sonnet; ~2.9× the cost |
| claude-haiku-4-5 | 4 (+control $0.13) | $1.105 | 1030 | 0.0 | 0.961 | 0.00 | no | recall 0.987 aggregate; under-marks three span tails by 2–7 s; 5.6× Sonnet's wall time (serial thinking) and ~20% more expensive than Sonnet through the CLI |

Reading: on this dev set Sonnet 5 is the best on every axis. Opus buys nothing
at three times the price; Haiku is both slower and dearer than Sonnet through
the CLI because its default thinking budget dominates (510 s for the JRE
episode). All misses on all three models are under-inclusion at span tails,
the safe direction under the asymmetry; no model marked any journalism. The
control episode is clean on all three.

## K2 — Five new PDB episodes (no hand labels yet), Sonnet 5 vs Opus 5, 2026-09-06 ~05:00

Fixtures from `scripts/build_fixtures.py` (seed 20260906; 2 morning briefs,
1 afternoon bulletin, 2 weekend Situation Reports; whisper-small transcripts).
Haiku 4.5 still running at the time of writing; drafts in
`tests/fixtures/truth-drafts/*_ads.truth.draft.json` (status `needs_human_review`).

| Episode | Sonnet spans / ad s / cost | Opus spans / ad s / cost | Jaccard | Disputed |
|---|---|---|---|---|
| Situation Report 2026-08-08 (60 min) | 2 / 93.9 / $0.25 | 3 / 152.4 / $0.59 | 0.616 | 58.5 s: a LEAN supplement read at 1727–1786 s |
| Morning 2026-08-18 | 3 / 236.9 / $0.12 | 3 / 236.9 / $0.28 | 1.000 | none |
| Morning 2026-08-19 | 2 / 224.1 / $0.11 | 2 / 224.1 / $0.27 | 1.000 | none |
| Situation Report 2026-08-22 (58 min) | 3 / 160.8 / $0.26 | 3 / 160.8 / $0.63 | 1.000 | none |
| Afternoon 2026-08-25 | 3 / 216.1 / $0.09 | 2 / 203.6 / $0.15 | 0.942 | 12.6 s: the PDBpremium sign-off (`house`) at 707–720 s |

Both disputes are recall differences, not false positives, and both resolve
by reading the transcript:

- **2026-08-08, 1727–1786 s** is a genuine host-read ad ("Hey, Mike Baker here
  with a word about personal health and weight loss … promo code PDB at take
  lean dot com"). Sonnet *did* find it (span 334–344) but its evidence quote
  failed rung 5 (not verbatim in segment 334) and the confidence was halved to
  0.475, i.e. `uncertain` / `action: prompt`. The ladder did what it is
  designed to do (demote, not drop), but this is a real recall loss at the
  skip threshold and is exactly the case the quote-anchoring experiment (K3)
  is meant to fix. Opus quoted the segment correctly.
- **2026-08-25, 707–720 s** is the paid PDBpremium pitch, which the fixture
  convention labels `house`. Sonnet is right; Opus folded it into content.

Draft truth for the morning review therefore = the consensus spans plus both
single-model regions.

**Haiku 4.5 column (added 04:58 after its run finished).** Haiku found the
same spans as the other two models on all five episodes (chunks 1:1 with
Sonnet's), but four of its evidence quotes failed rung 5 and those spans
were demoted to `uncertain` (confidence 0.475): 2026-08-08 both mid-rolls
(173–188, 334–344), 2026-08-18 the first mid-roll (89–105), 2026-08-22 the
second mid-roll (570–595). At the skip threshold that reads as ad seconds
4.4 / 141 / 103 s against Sonnet's 94 / 237 / 161 s, and pairwise Jaccard vs
Sonnet of 0.05 / 0.60 / 0.64; counting `uncertain` spans the three models
agree almost exactly. Cost $0.82 for the five episodes, wall 1007 s (6× Sonnet).

So across all three models tonight, every recall difference on the new PDB
episodes is rung 5 (evidence quote not matched in the start segment), never
a missed ad. The quote check is the dominant recall lever, and it is safe
(demote, not drop) but blunt.

Root cause of the Sonnet demotion, for K3: the quote `"Hey, Mike Baker here
with a word about personal health and weight loss."` straddles the boundary
between segment 334 (`… Stick around. Hey, Mike Baker here with a word`) and
335 (`about personal health and weight loss. Now …`). Rung 5 checks the quote
against the start segment only; token overlap is 7/12 = 58%, under the 70%
floor. The model located the ad exactly and quoted the transcript verbatim;
the check was too narrow. Candidate fix (a ladder change, so versioned):
match the quote against `segments[start_index] + " " + segments[start_index+1]`
before failing. Not applied tonight.

## K4 — Against published sponsor blocks (SponsorBlock), 2026-09-06

On JRE #2537, the one JRE episode with hand truth, SponsorBlock's two sponsor
segments map to RSS 1262–1305 s and 3399–3447 s (piecewise shift by inserted
seconds; details in track L). All three models caught both at the skip
threshold: AdVTT recall against SponsorBlock is 1.0, with zero content loss
against the hand truth. SponsorBlock in turn covers 90 of the 791 ad seconds
in the RSS copy, because 701 s are Megaphone-inserted creatives absent from
YouTube. For the five new JRE episodes, SponsorBlock silver labels can be
derived the same way once transcripts exist; the inserted channel already has
exact truth from the stitch maps (`tests/fixtures/truth-drafts/*_ads.truth.inserted.json`).

## K3 — Ladder 2026-09-a: evidence quote may straddle the next segment (approved by the user 2026-09-06 04:50)

Change: rung 5 tries `segments[start] + " " + segments[start+1]` when the
start segment alone fails (`EVIDENCE_LOOKAHEAD = 1`, `LADDER_VERSION =
"2026-09-a"`, results carry `prompt_version 2026-08-g+2026-09-a`; the prompt
text and the replay keys are unchanged, `--dump-prompt` still byte-identical).
Measured by replaying every recorded response offline (no model calls):

| Set | Model | Before → after |
|---|---|---|
| Dev set (4 fixtures, hand truth) | all three | unchanged: 0.0 s content loss, recall 1.000 / 0.961 / 0.961, no gate change |
| New PDB, Situation Report 2026-08-08 | Haiku ad s | 4.4 → 150.9 (both mid-rolls promoted from `uncertain` to `ad`) |
| New PDB, 2026-08-18 | Haiku ad s | 141 → 237 |
| New PDB, 2026-08-22 | Haiku ad s | 103 → 161 |
| New PDB, 2026-08-08 | Sonnet LEAN read | promoted to `ad`; dispute with Opus 58.5 s → 11.8 s (edge placement only) |
| New PDB, single-model regions | all | 2 episodes with one → 1 episode with one (the `house` sign-off Opus omits) |
| New PDB, pairwise Jaccard Sonnet~Haiku | | 0.047 / 0.595 / 1.0 / 0.643 / 0.942 → 0.916 / 0.936 / 1.0 / 0.981 / 0.942 |

No span was newly created and no content was newly marked: the change only
restores confidence that rung 5 had halved on quotes that were verbatim but
ran across a segment boundary. Consensus drafts in
`tests/fixtures/truth-drafts/` were regenerated from the replayed runs.

## K6 — Recall split by delivery: host-read vs inserted (2026-09-07)

Why: the Megaphone stitch map (track M) labels every dynamically inserted
creative exactly, so on a DAI show two thirds of the truth seconds are spans a
model earns nothing for finding. A model that catches all 13 creatives and
misses both host reads scores ~0.9 total recall on a JRE episode. The
evaluator now reports `hostread_recall_sec` and `inserted_recall_sec` beside
the total (`advtt.evaluate`, `scripts/compare_models.py`), and the 0.70 recall
target is applied to host-read recall where delivery is known. Delivery is
per truth segment: explicit `delivery` on the span, else index overlap with a
sibling `<stem>_ads.truth.inserted.json`, else unknown. An inserted file with
no spans means "no dynamic insertion on this copy". Overlays added under
`tests/fixtures/truth-drafts/`: David Sinclair (six stitched breaks and two
host reads, from the M-dai-check cross-check table) and empty files for all
eight PDB episodes (no DAI, track M). No model calls; every number below is a
rescoring of recorded runs.

Dev set, current ladder (the K3 replay directories):

| Model | content loss | recall (total) | host-read recall | inserted recall | host-read truth s | inserted truth s |
|---|---|---|---|---|---|---|
| Sonnet 5 | 0.0 | 1.000 | 1.000 | 1.000 | 659 | 652 |
| Opus 5 | 0.0 | 0.961 min | 0.961 min | 1.000 | 659 | 652 |
| Haiku 4.5 | 0.0 | 0.961 min | 0.961 min | 1.000 | 659 | 652 |

Per episode the split changes one reading: Haiku on Sinclair is 0.997 total
but 0.974 host-read, i.e. its only miss on that episode is on a host read
(2.3 s of the Superpower/BetterHelp reads), while every stitched creative is
caught in full. Opus's 0.961/0.965 on the two PDB bulletins are host-read
misses by definition (PDB has no insertion). All three models still pass the
host-read target on the dev set.

New JRE episodes, Sonnet 5 (the only model whose run survived the quota
window, see the 2026-09-06 log), inserted-only truth from the stitch map:

| Episode | inserted recall | boundary err s | note |
|---|---|---|---|
| MMA #184 Aljamain Sterling | 0.976 | 2.57 | one break edge |
| #2540 Travis Barker | 1.000 | 0.0 | |
| #2542 Steve Hilton | 1.000 | 0.0 | |
| #2547 Daniel Everett | 1.000 | 0.0 | |
| #2548 Brian Simpson | 0.530 | 0.0 | chunks 7-13 errored (usage limit); record still says `ok` |

The Simpson row is the partial-failure gap noted in PROGRESS: `classify.py`
only fails an episode when every chunk errored, so a half-quota run is
reported as a clean result with half the ads. To be fixed before the reruns.

SponsorBlock silver against the same Sonnet run (`scripts/sb_compare.py`,
which until today looked for `_ads.json` and reported "no prediction" for
every `.advtt.json` record):

| Episode | SB s | overlap s | SB recall by AdVTT | SB-only residue |
|---|---|---|---|---|
| MMA #184 | 119.7 | 118.8 | 0.992 | four sub-second edges |
| #2540 Travis Barker | 103.8 | 102.5 | 0.987 | four sub-second edges |
| #2542 Steve Hilton | 68.3 | 59.9 | 0.876 | one 7.5 s start edge at 1345.7 |
| #2547 Daniel Everett | 129.5 | 125.6 | 0.970 | 2.2 s at file start + edges |
| #2548 Brian Simpson | 159.9 | 156.4 | 0.978 | 2.1 s at file start + edges |

SponsorBlock only labels host reads (K4), so this is host-read recall on JRE
by another route: 0.88-0.99 on five episodes, with every miss a boundary
rather than a whole read. The six "AdVTT-only" spans per episode are the
stitched breaks, absent from the YouTube master SponsorBlock is aligned to.

Merged truth (same day): `scripts/merge_truth_sources.py` joins the stitch
map (inserted) and the SponsorBlock silver labels (host-read) into
`data/truth-drafts/<stem>_ads.truth.draft.json` (gitignored: SponsorBlock
spans about copyrighted episodes stay off the public repo) with `delivery`
and `source` on every span. No model is involved. The five JRE drafts now hold
6 inserted breaks plus 1-3 host reads each, 847-924 ad seconds per episode
(7.3-9.2 %), zero overlaps between the two sources (they are disjoint by
construction). Two 2-second SponsorBlock marks at 0.0 s (a YouTube opening
card before any speech) map to no transcript segment and are kept under
`unmapped`. The earlier Sonnet-only consensus drafts were replaced.

Sonnet 5 against the merged drafts as full truth:

| Episode | content loss s | recall | host-read recall | inserted recall | boundary err s |
|---|---|---|---|---|---|
| MMA #184 Aljamain Sterling | 0.0 | 0.979 | 1.000 | 0.976 | 1.93 |
| #2540 Travis Barker | 0.0 | 1.000 | 1.000 | 1.000 | 0.00 |
| #2542 Steve Hilton | 0.0 | 0.985 | 0.819 | 1.000 | 0.12 |
| #2547 Daniel Everett | 0.0 | 1.000 | 0.999 | 1.000 | 0.01 |
| #2548 Brian Simpson | 0.0 | 0.608 | 0.997 | 0.530 | 0.00 |

Zero content loss on 14.7 h of JRE with these labels; the host-read target
passes on all five. The two readings the split isolates: Steve Hilton's
0.819 is a 7.5 s late start on the one host read (SponsorBlock 1345.7 s,
Sonnet 1353.2 s), which the total recall of 0.985 hides; Simpson's 0.608
total is the quota-truncated run and its host-read recall of 0.997 shows
the surviving chunks were fine. Caveats: SponsorBlock coverage is
community-sourced, so an unsubmitted host read is missing from the truth and
would be invisible here; every draft is still `needs_human_review`.

## K7 — STT segmentation shapes span boundaries (observation, 2026-09-07)

Same episode (TWiT Hands-On Tech 283, 13 min video, private test, nothing in
the repo), same classifier (Sonnet 5, same prompt and ladder), two STT
engines. Both transcripts contain the same words (0.974 word-level
similarity) and both runs found the same two host reads with no false
positive, but the NetSuite read's edges differ by 5 s at the start and 4 s
at the end: whisper-small included "Let's take a quick break so I can tell
you about this week's sponsor" and "Thank you, NetSuite, for sponsoring this
week's episode"; Gladia's span started at the product name and ended at the
call-to-action URL. The ladder rejected nothing in either run; the model
chose the indices.

Cause: the classifier can only cut at segment boundaries and quotes its end
evidence from the last segment, and the two engines segment very
differently.

| Transcript | segments | under 1 s | median length |
|---|---|---|---|
| whisper-small, HOT 283 | 205 | 9.8 % | 3.30 s |
| Gladia solaria-1, HOT 283 | 334 | 39.5 % | 1.49 s |
| Gladia, five JRE episodes | 23,769 | 46.8 % | 1.08 s |
| whisper-small, five PDB episodes | 2,179 | 4.3 % | 4.72 s |

Gladia split the thank-you into three sub-second fragments ("Thank you," /
"NetSuite," / "for sponsoring this week's episode of Hands-On Tech.") and
the model stopped before them. The opposite shape appears on JRE #2542
(Steve Hilton, Gladia): one 11.5 s segment runs from show content into the
first words of the Blue Chew read, the model correctly refused it (marking it
would cost 4.5 s of content) and the span started 7.5 s late, which is the
`hostread_recall 0.819` reading in K6.

Not fixed. Backlog item in `docs/backlog.md`: a segment normalisation step
at ingestion (merge sub-second fragments into a neighbour, split run-on
segments at sentence ends using the word timings both engines provide),
before chunking, so the classifier sees sentence-shaped segments whatever
the engine. It changes prompt text, so measuring it needs fresh model calls
on the Gladia JRE transcripts; the replay store cannot answer it.

## Next: K1 effort sweep

Planned settings: `claude-sonnet-5` effort low / medium / high (default) and
`claude-opus-5` effort low / high; `claude-haiku-4-5` with `ADVTT_CLI_THINKING`
0 / 1024 / 4000. Each setting is one `--eval --classify --record-replay` run
into its own `--out-dir`; the table above is the baseline row.
