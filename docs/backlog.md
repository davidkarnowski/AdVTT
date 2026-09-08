# Backlog

Work agreed but not scheduled. Each item names the evidence behind it.

## Sprint: transcript segmentation and chunking refinement

Decided 2026-09-07. Evidence: `Research/research-log/K-experiments.md` K6
(Steve Hilton late start, host-read recall 0.819) and K7 (same episode, two
STT engines, 9 s of span-edge difference from segmentation alone).

- [ ] Segment normalisation at ingestion, before `plan_chunks`: merge
      sub-second fragments into a neighbour and split run-on segments at
      sentence ends, using word timings. Engine-agnostic; whisper output
      should pass through nearly unchanged.
- [ ] Keep the original segments in the transcript sidecar and record the
      normalisation in the record's `stt` block, so a caption file or an
      evaluator can map back.
- [ ] Measure on the five Gladia JRE transcripts against the merged truth
      drafts (`data/truth-drafts/`): boundary error and host-read recall
      before and after. Needs fresh model calls (prompt text changes, no
      replay hits); budget one model, Sonnet 5, about five dollars.
- [ ] Revisit the chunk planner with normalised segments: window sizes and
      the 12-segment context are tuned for whisper-sized segments, and
      Gladia's 1 s segments make the context window a fraction of the time.
- [ ] Decide whether `refine_span_edges` should extend a span across an
      adjacent segment that is a sponsor sign-off ("thank you X for
      sponsoring") when the evidence quote ends on the call to action.
      Ladder-only change, `LADDER_VERSION` bump, measurable offline by replay.

## Smaller items

- [ ] Fill the record's `advertiser` field from the evidence quote; the
      prompt is frozen, so this is a post-processing extraction.
- [ ] Set `delivery` on record spans when a stitch map is available.
- [ ] Partial-chunk failure should not report `status: ok`
      (`classify.py`; seen when the usage limit hit mid-episode).
