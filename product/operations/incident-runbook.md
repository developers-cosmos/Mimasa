# Mimasa Phase A — Incident Response Runbook (WI-013)

## Scope
Applies to the Phase A pipeline control plane (`/api/v1/jobs/*`) and stage chain (ASR→MT→TTS→Compositing→Delivery).

## SLO targets
- Job failure rate (`FAILED_FATAL`) < 10% over 24h.
- Stage P95 latency < 120s over 24h.
- Open dead-letter events <= 5.
- Delivery webhook failure rate < 20%.

## Detection
Use:
- `GET /api/v1/telemetry/summary/`
- `GET /api/v1/telemetry/alerts/`
- `GET /api/v1/telemetry/alert-events/`
- `GET /api/v1/jobs/{job_id}/dead-letters/`
- `python src/api/mimasa/manage.py check_pipeline_alerts` (scheduled sync)

## Triage steps
1. Confirm alert trigger from `/telemetry/alerts/` and record `evaluated_at` timestamp.
2. Identify impacted jobs with `status=FAILED_FATAL` and inspect transition events.
3. Inspect latest dead-letter entries to identify failing stage and attempt counts.
4. Verify dependent infra status (Redis/Celery/DB/object store/webhook receiver).

## Mitigation playbooks
### Stage failure spike
- Pause new submissions if queue saturation is observed.
- Replay by stage using:
  - `POST /api/v1/jobs/{job_id}/retry/` or
  - `POST /api/v1/jobs/{job_id}/replay/` for specific dead-letter event.
- Escalate to ML Lead for model/runtime errors if same stage fails across jobs.

### Delivery/webhook degradation
- Use `POST /api/v1/jobs/{job_id}/deliver/` to re-issue signed delivery records.
- If webhook endpoint is down, continue tokenized delivery and queue manual customer notification.

## Escalation matrix
- Workflow failures: Workflow Orchestration Engineer (primary)
- Runtime/infra failures: MLOps & SRE Engineer (primary)
- Model accuracy/latency regressions: ML Lead
- Release decisions: Product Lead + QA & Annotation Lead

## Post-incident
- Document timeline, root cause, remediation, and prevention actions.
- Update alert thresholds if too noisy or missing incidents.
