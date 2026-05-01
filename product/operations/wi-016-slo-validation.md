# WI-016 — SLO Validation Under Staged Load

**Owner:** MLOps & SRE Engineer  
**Date:** 2026-05-01

## Objective
Validate Phase A operational SLOs using alert-derived metrics and explicit violation reporting.

## Command
```bash
python src/api/mimasa/manage.py validate_phase_a_slos --out product/operations/reports/slo-validation.json
```

## Default SLO Thresholds
- Job failure rate <= 10%
- Stage P95 latency <= 120s
- Open dead-letter count <= 5
- Webhook failure rate <= 20%

## Pass Rule
- `passed=true` only when there are zero active violations.

## Output Contract
- `window_hours`
- `violations[]`
- `passed`
- `check_count`
- `alerts_result`
