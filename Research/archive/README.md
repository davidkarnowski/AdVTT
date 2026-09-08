# Archived pre-spike design (2026-09-01)

These six documents are the preliminary design written before the research
spike. `08-recommendation-and-trajectory.md` supersedes them where they
differ (its §2 lists every reversal) and `12-research-evaluation-and-classifier-plan.md`
decision C.9 moved them here on 2026-09-06. They are kept because parts are
still load-bearing:

| File | Still authoritative for | Superseded on |
|---|---|---|
| `01-extraction-plan.md` | which symbols moved and why, the regression protocol, the `TaskExtension` idea | experiment order (12 C.6), fixture shipping (12 C.7) |
| `02-webvtt-profile.md` | the two-line cue payload | NOTE header, vocabulary, WebVTT as primary (08 §4) |
| `03-srt-strategy.md` | the visible SRT twin | inline SRT marking is dropped (08 §4.3) |
| `04-cli-design.md` | amendment workflow, `--offline`, drift concerns | flag surface (see `src/advtt/cli.py`) |
| `05-html-player.md` | browser `kind=metadata` caveats | player reads the record, not only the VTT (08 §9 Phase 2) |
| `06-open-questions.md` | the questions | every answer is in 08 §10 |
