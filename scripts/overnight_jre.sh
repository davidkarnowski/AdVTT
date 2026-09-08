#!/bin/zsh
# Unattended JRE pipeline: wait for Gladia transcripts, fill gaps with retries,
# classify with three models (replay recorded), build truth drafts, compare
# against SponsorBlock silver labels, log to data/logs/overnight-jre.log and
# the work log, commit and push. Safe to rerun: every step skips finished work.
# Machine-specific: depends on local data/ and an authenticated claude CLI.
cd "$(dirname "$0")/.." || exit 1
PROGRESS=Research/local/PROGRESS.md
LOG=data/logs/overnight-jre.log
say() { echo "[$(date -u +%FT%TZ)] $*" | tee -a "$LOG"; }
prog() { echo "- [overnight-jre $(date +%H:%M)] $*" >> "$PROGRESS"; }
say "pipeline start"
# 1. wait for the running Gladia script, then rerun until all five transcripts exist (max 3 rounds)
while pgrep -f transcribe_gladia.py >/dev/null; do sleep 30; done
for round in 1 2 3; do
  n=$(ls data/fixtures/jre/*_stt.json 2>/dev/null | wc -l | tr -d ' ')
  [ "$n" -ge 5 ] && break
  say "round $round: $n/5 JRE transcripts, rerunning Gladia for the gaps"
  python3 scripts/transcribe_gladia.py --show jre >> data/logs/transcribe-gladia-jre.stdout 2>&1
done
n=$(ls data/fixtures/jre/*_stt.json 2>/dev/null | wc -l | tr -d ' ')
say "transcripts available: $n/5"; prog "Gladia transcripts available: $n/5"
[ "$n" -eq 0 ] && { say "no transcripts; stopping"; exit 2; }
# 2. classify with three models, replay recorded (each JRE episode ~13 chunks)
for spec in claude-sonnet-5:sonnet5-default claude-opus-5:opus5-default claude-haiku-4-5:haiku45-default; do
  m=${spec%%:*}; d=${spec##*:}
  for f in data/fixtures/jre/*_stt.json; do
    s=$(basename "$f" _stt.json)
    [ -f "eval-out/$d/$s.analysis.json" ] && continue
    say "classify $m $s"
    PYTHONPATH=src python3 -m advtt.cli --stt "$f" --media "data/episodes/jre/$s.a.mp3" --provider claude-cli --model "$m" \
      --record-replay --replay-store tests/replay --out-dir "eval-out/$d" --force --export all >> "$LOG" 2>&1 \
      || say "classify FAILED $m $s (exit $?)"
  done
  prog "JRE classified with $m ($(ls eval-out/$d/*.analysis.json 2>/dev/null | grep -c jre_ ) files)"
done
# 3. truth drafts: inserted channel from stitch maps (now mappable onto segments), consensus across models
python3 scripts/stitchmap_to_truth.py --stt-dir data/fixtures/jre --out-dir tests/fixtures/truth-drafts > data/logs/stitchmap-jre.txt 2>&1
python3 scripts/consensus.py --stt-dirs data/fixtures/jre --runs eval-out/sonnet5-default eval-out/opus5-default eval-out/haiku45-default \
  --out-dir tests/fixtures/truth-drafts --min-agree 2 --json data/logs/consensus-jre.json > data/logs/consensus-jre.txt 2>&1
python3 scripts/compare_models.py --stt-dirs data/fixtures/jre --runs eval-out/sonnet5-default eval-out/opus5-default eval-out/haiku45-default \
  --json data/logs/compare-jre.json > data/logs/compare-jre.txt 2>&1
# 4. against SponsorBlock silver labels (host-read channel), per model
for d in sonnet5-default opus5-default haiku45-default; do
  python3 scripts/sb_compare.py --run "eval-out/$d" --silver-dir data/sponsorblock --json "data/logs/sb-compare-$d.json" > "data/logs/sb-compare-$d.txt" 2>&1
done
say "analysis written: data/logs/{stitchmap-jre,consensus-jre,compare-jre,sb-compare-*}.txt"
prog "JRE analysis complete; see data/logs/compare-jre.txt, consensus-jre.txt, sb-compare-*.txt (tables to be folded into K-experiments)"
# 5. commit labels-only artefacts
git add tests/fixtures/manifest.json tests/fixtures/truth-drafts tests/replay >/dev/null 2>&1
git commit -q -m "Overnight JRE pipeline: transcripts via Gladia, three-model runs, truth drafts

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" && git push -q && say "committed and pushed" || say "nothing to commit or push failed"
say "pipeline done"
