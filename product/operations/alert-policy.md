# Mimasa Phase A — Alert Policy (WI-013)

## Source
Alert checks are computed by `GET /api/v1/telemetry/alerts/`.

## Rules
| Alert Key | Trigger | Default Threshold | Severity | Owner |
|---|---|---:|---|---|
| `job_failure_rate` | `FAILED_FATAL` rate over window > threshold | 10% | Critical | Workflow + MLOps |
| `stage_latency_p95` | Stage P95 seconds > threshold | 120s | High | MLOps |
| `open_dead_letters` | Open dead-letter count > threshold | 5 | Critical | Workflow |
| `webhook_failure_rate` | Delivery webhook failure rate > threshold | 20% | Medium | Backend + MLOps |

## Environment overrides
- `PIPELINE_ALERT_WINDOW_HOURS` (default `24`)
- `PIPELINE_ALERT_MAX_JOB_FAILURE_RATE_PCT` (default `10`)
- `PIPELINE_ALERT_MAX_STAGE_P95_SECONDS` (default `120`)
- `PIPELINE_ALERT_MAX_OPEN_DEAD_LETTERS` (default `5`)
- `PIPELINE_ALERT_MAX_WEBHOOK_FAILURE_RATE_PCT` (default `20`)

## Notification policy
- Critical: page on-call immediately.
- High: investigate in <= 30 minutes.
- Medium: investigate in same business day.
