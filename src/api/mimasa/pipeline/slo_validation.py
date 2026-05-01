from .alerting import evaluate_alerts


def validate_phase_a_slos(
    *,
    max_job_failure_rate_pct: float = 10.0,
    max_stage_p95_seconds: float = 120.0,
    max_open_dead_letters: int = 5,
    max_webhook_failure_rate_pct: float = 20.0,
    window_hours: int = 24,
):
    result = evaluate_alerts(
        window_hours=window_hours,
        max_job_failure_rate_pct=max_job_failure_rate_pct,
        max_stage_p95_seconds=max_stage_p95_seconds,
        max_open_dead_letters=max_open_dead_letters,
        max_webhook_failure_rate_pct=max_webhook_failure_rate_pct,
    )
    violations = [c for c in result["checks"] if c["triggered"]]
    return {
        "window_hours": window_hours,
        "violations": violations,
        "passed": len(violations) == 0,
        "check_count": len(result["checks"]),
        "alerts_result": result,
    }
