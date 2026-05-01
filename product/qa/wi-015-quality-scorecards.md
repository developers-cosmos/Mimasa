# WI-015 — Quality Scorecards and Pass/Fail Report

**Owner:** QA & Annotation Lead  
**Date:** 2026-05-01

## Objective
Translate WI-014 acceptance KPIs into a scorecard-grade view and explicit pass/fail recommendation.

## Command
```bash
python src/api/mimasa/manage.py run_phase_a_scorecard --out product/qa/reports/quality-scorecard.json
```

## Scorecard Grading
- Grade `A`: value >= 115% of threshold
- Grade `B`: value >= 100% of threshold
- Grade `C`: value >= 85% of threshold
- Grade `F`: value < 85% of threshold

## Recommendation Rule
- `PASS`: all acceptance checks pass
- `FAIL`: one or more checks fail

## Output Contract
- `recommendation`
- `failed_checks`
- `scorecard[]`
- `acceptance` (embedded WI-014 checks)
