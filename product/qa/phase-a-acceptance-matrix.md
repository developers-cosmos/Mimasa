# WI-014 — Phase A Acceptance Matrix

**Owner:** QA & Annotation Lead  
**Date:** 2026-04-27

## Objective
Execute an objective acceptance matrix across workflow correctness, reliability, review quality, and delivery integrity before Sprint 4 release recommendation.

## Matrix Dimensions
- **Language pairs:** EN→ES, EN→FR, EN→DE (expand in Sprint 4 week 2)
- **Scenarios:** clean speech, overlapping speakers, noisy audio, long-form (>10 min), webhook outage simulation
- **Quality checks:** lifecycle completeness, QA pass rate, dead-letter recovery, webhook success

## Automated Acceptance Checks (current implementation)
Run:

```bash
python src/api/mimasa/manage.py run_phase_a_acceptance --out product/qa/reports/latest.json
```

| Check Key | Description | Pass Threshold |
|---|---|---:|
| `delivery_completion_rate` | % jobs reaching `DELIVERED` | >= 70% |
| `qa_pass_rate` | % QA-reviewed jobs with `QA_PASSED` | >= 80% |
| `deadletter_resolution_rate` | % dead-letter events replayed | >= 75% |
| `webhook_success_rate` | % deliveries with webhook `SENT` | >= 80% |

## Manual Acceptance Tracks (must be logged)
1. Reviewer correction + approve/reject flow correctness.
2. Replay path from dead-letter to successful stage completion.
3. Delivery token expiry behavior and invalid token rejection.
4. Alert escalation path from `/telemetry/alerts` to on-call response.

## Exit Criteria for WI-014
- Automated acceptance report generated and stored.
- Manual tracks executed with evidence links.
- Defect list triaged into block/non-block with owners.
