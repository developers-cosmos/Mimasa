from django.conf import settings
from django.core.management.base import BaseCommand

from pipeline.alerting import evaluate_alerts, sync_alert_events


class Command(BaseCommand):
    help = "Evaluate pipeline alert checks and persist alert events"

    def handle(self, *args, **options):
        payload = evaluate_alerts(
            window_hours=getattr(settings, "PIPELINE_ALERT_WINDOW_HOURS", 24),
            max_job_failure_rate_pct=getattr(settings, "PIPELINE_ALERT_MAX_JOB_FAILURE_RATE_PCT", 10.0),
            max_stage_p95_seconds=getattr(settings, "PIPELINE_ALERT_MAX_STAGE_P95_SECONDS", 120.0),
            max_open_dead_letters=getattr(settings, "PIPELINE_ALERT_MAX_OPEN_DEAD_LETTERS", 5),
            max_webhook_failure_rate_pct=getattr(settings, "PIPELINE_ALERT_MAX_WEBHOOK_FAILURE_RATE_PCT", 20.0),
        )
        changes = sync_alert_events(payload)
        self.stdout.write(
            self.style.SUCCESS(
                f"Alerts evaluated at {payload['evaluated_at']}; opened={changes['opened']} resolved={changes['resolved']}"
            )
        )
