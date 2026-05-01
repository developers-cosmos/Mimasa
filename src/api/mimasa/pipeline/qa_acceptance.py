from dataclasses import dataclass, asdict

from django.db.models import Count, Q

from .models import DeadLetterEvent, DeliveryRecord, Job


@dataclass(frozen=True)
class AcceptanceCheck:
    key: str
    description: str
    value: float
    threshold: float
    unit: str
    passed: bool


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 2)


def evaluate_phase_a_acceptance(
    *,
    min_delivery_rate_pct: float = 70.0,
    min_qa_pass_rate_pct: float = 80.0,
    min_dead_letter_resolution_rate_pct: float = 75.0,
    min_webhook_success_rate_pct: float = 80.0,
):
    total_jobs = Job.objects.count()
    delivered_jobs = Job.objects.filter(status=Job.Status.DELIVERED).count()
    delivery_rate = _ratio(delivered_jobs, total_jobs)

    qa_rollup = Job.objects.aggregate(
        qa_total=Count("id", filter=Q(status__in=[Job.Status.QA_PASSED, Job.Status.QA_FAILED])),
        qa_passed=Count("id", filter=Q(status=Job.Status.QA_PASSED)),
    )
    qa_pass_rate = _ratio(qa_rollup["qa_passed"] or 0, qa_rollup["qa_total"] or 0)

    deadletter_rollup = DeadLetterEvent.objects.aggregate(
        total=Count("id"), resolved=Count("id", filter=Q(status=DeadLetterEvent.Status.REPLAYED))
    )
    deadletter_resolution_rate = _ratio(deadletter_rollup["resolved"] or 0, deadletter_rollup["total"] or 0)

    webhook_rollup = DeliveryRecord.objects.aggregate(
        total=Count("id"), sent=Count("id", filter=Q(webhook_status=DeliveryRecord.WebhookStatus.SENT))
    )
    webhook_success_rate = _ratio(webhook_rollup["sent"] or 0, webhook_rollup["total"] or 0)

    checks = [
        AcceptanceCheck(
            key="delivery_completion_rate",
            description="Percent of jobs that reached DELIVERED",
            value=delivery_rate,
            threshold=min_delivery_rate_pct,
            unit="percent",
            passed=delivery_rate >= min_delivery_rate_pct,
        ),
        AcceptanceCheck(
            key="qa_pass_rate",
            description="Percent of QA-reviewed jobs with QA_PASSED",
            value=qa_pass_rate,
            threshold=min_qa_pass_rate_pct,
            unit="percent",
            passed=qa_pass_rate >= min_qa_pass_rate_pct,
        ),
        AcceptanceCheck(
            key="deadletter_resolution_rate",
            description="Percent of dead-letter events replayed by operators",
            value=deadletter_resolution_rate,
            threshold=min_dead_letter_resolution_rate_pct,
            unit="percent",
            passed=deadletter_resolution_rate >= min_dead_letter_resolution_rate_pct,
        ),
        AcceptanceCheck(
            key="webhook_success_rate",
            description="Percent of deliveries with successful webhook callbacks",
            value=webhook_success_rate,
            threshold=min_webhook_success_rate_pct,
            unit="percent",
            passed=webhook_success_rate >= min_webhook_success_rate_pct,
        ),
    ]

    return {
        "summary": {
            "total_checks": len(checks),
            "passed_checks": sum(1 for c in checks if c.passed),
            "all_passed": all(c.passed for c in checks),
        },
        "checks": [asdict(check) for check in checks],
    }
