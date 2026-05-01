from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .models import AlertEvent, DeadLetterEvent, DeliveryRecord, Job, StageExecution


def _percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 2)


def _p95_stage_duration_seconds(window_start):
    durations = []
    rows = StageExecution.objects.filter(
        ended_at__isnull=False,
        started_at__isnull=False,
        created_at__gte=window_start,
    ).values_list("started_at", "ended_at")
    for started_at, ended_at in rows:
        durations.append((ended_at - started_at).total_seconds())

    if not durations:
        return 0.0

    durations.sort()
    index = max(0, int(round(0.95 * (len(durations) - 1))))
    return round(durations[index], 3)


def _severity_for_check(key: str, value: float, threshold: float) -> str:
    if threshold <= 0:
        return "MEDIUM"
    ratio = value / threshold
    if ratio >= 2.0:
        return "CRITICAL"
    if ratio >= 1.25:
        return "HIGH"
    return "MEDIUM"


def evaluate_alerts(
    *,
    window_hours: int,
    max_job_failure_rate_pct: float,
    max_stage_p95_seconds: float,
    max_open_dead_letters: int,
    max_webhook_failure_rate_pct: float,
):
    now = timezone.now()
    window_start = now - timedelta(hours=window_hours)

    jobs_qs = Job.objects.filter(created_at__gte=window_start)
    total_jobs = jobs_qs.count()
    failed_jobs = jobs_qs.filter(status=Job.Status.FAILED_FATAL).count()
    failure_rate = _percent(failed_jobs, total_jobs)

    p95_stage_seconds = _p95_stage_duration_seconds(window_start)
    open_dead_letters = DeadLetterEvent.objects.filter(status=DeadLetterEvent.Status.OPEN, created_at__gte=window_start).count()

    delivery_rollup = DeliveryRecord.objects.filter(created_at__gte=window_start).aggregate(
        total=Count("id"), failed=Count("id", filter=Q(webhook_status=DeliveryRecord.WebhookStatus.FAILED))
    )
    webhook_fail_rate = _percent(delivery_rollup["failed"] or 0, delivery_rollup["total"] or 0)

    checks = [
        {
            "key": "job_failure_rate",
            "value": failure_rate,
            "threshold": max_job_failure_rate_pct,
            "comparator": ">",
            "triggered": failure_rate > max_job_failure_rate_pct,
            "unit": "percent",
            "description": "FAILED_FATAL job rate over alert window",
        },
        {
            "key": "stage_latency_p95",
            "value": p95_stage_seconds,
            "threshold": max_stage_p95_seconds,
            "comparator": ">",
            "triggered": p95_stage_seconds > max_stage_p95_seconds,
            "unit": "seconds",
            "description": "Stage execution P95 latency over alert window",
        },
        {
            "key": "open_dead_letters",
            "value": open_dead_letters,
            "threshold": max_open_dead_letters,
            "comparator": ">",
            "triggered": open_dead_letters > max_open_dead_letters,
            "unit": "count",
            "description": "Open dead-letter events over alert window",
        },
        {
            "key": "webhook_failure_rate",
            "value": webhook_fail_rate,
            "threshold": max_webhook_failure_rate_pct,
            "comparator": ">",
            "triggered": webhook_fail_rate > max_webhook_failure_rate_pct,
            "unit": "percent",
            "description": "Delivery webhook failure rate over alert window",
        },
    ]

    return {
        "window_hours": window_hours,
        "evaluated_at": now.isoformat(),
        "triggered": [check for check in checks if check["triggered"]],
        "checks": checks,
    }


@transaction.atomic
def sync_alert_events(alert_payload: dict) -> dict:
    changed = {"opened": 0, "resolved": 0}

    for check in alert_payload["checks"]:
        existing = AlertEvent.objects.filter(key=check["key"], status=AlertEvent.Status.OPEN).order_by("-updated_at").first()
        if check["triggered"]:
            severity = _severity_for_check(check["key"], float(check["value"]), float(check["threshold"]))
            if existing:
                existing.value = float(check["value"])
                existing.threshold = float(check["threshold"])
                existing.severity = severity
                existing.details = check
                existing.save(update_fields=["value", "threshold", "severity", "details", "updated_at"])
            else:
                AlertEvent.objects.create(
                    key=check["key"],
                    severity=severity,
                    value=float(check["value"]),
                    threshold=float(check["threshold"]),
                    details=check,
                )
                changed["opened"] += 1
        elif existing:
            existing.status = AlertEvent.Status.RESOLVED
            existing.resolved_at = timezone.now()
            existing.details = check
            existing.save(update_fields=["status", "resolved_at", "details", "updated_at"])
            changed["resolved"] += 1

    return changed
