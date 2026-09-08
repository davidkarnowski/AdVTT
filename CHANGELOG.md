# Changelog

## 0.1.0.dev0 (unreleased)

First public snapshot. Extracted from a private podcast downloader and
rebuilt as a standalone, stdlib-only package.

- Canonical `advtt/1.0` JSON record with provenance, plus a local analysis
  file with evidence quotes and per-chunk cost.
- Exports: Kodi EDL, ffmetadata and Podcasting 2.0 JSON chapters,
  SponsorBlock JSON, WebVTT disclosure track, SRT twin, Audacity labels,
  RTTM, and full-transcript captions (VTT and SRT) with the ad cues marked.
- Chunked classification with thinking and a mechanical validation ladder;
  measured on a small hand-labelled set with zero content loss.
- Evaluation with recall split by delivery (host-read vs inserted).
- Agent surface: `--describe`, `--dry-run`, `--json`, `--log-json`, stable
  exit codes, replay store, `--offline`.
- `examples/player-demo.html`: native HTML5 player that shows the captions
  and marks ad blocks during playback.
