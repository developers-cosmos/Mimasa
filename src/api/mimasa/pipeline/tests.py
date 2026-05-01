from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from pipeline.alerting import evaluate_alerts, sync_alert_events
from pipeline.alerting_views import TelemetryAlertsView
from pipeline.models import AlertEvent, Artifact, DeadLetterEvent, DeliveryRecord, Job, StageExecution
from pipeline.qa_acceptance import evaluate_phase_a_acceptance
from pipeline.qa_scorecard import build_quality_scorecard
from pipeline.release_readiness import build_release_readiness_report
from pipeline.slo_validation import validate_phase_a_slos


class AlertingTests(TestCase):
    def setUp(self):
        self.job = Job.objects.create(name="job-1", source_language="en", target_language="es", status=Job.Status.FAILED_FATAL)
        stage = StageExecution.objects.create(
            job=self.job,
            stage_name=StageExecution.StageName.ASR,
            status=StageExecution.Status.SUCCESS,
            started_at=timezone.now() - timedelta(seconds=150),
            ended_at=timezone.now(),
        )
        artifact = Artifact.objects.create(
            job=self.job,
            stage_execution=stage,
            artifact_type=Artifact.ArtifactType.LOCALIZED_VIDEO_V1,
            uri="artifact://localized",
            checksum="chk",
            version="v1",
            metadata={},
        )
        DeadLetterEvent.objects.create(
            job=self.job,
            stage_name=StageExecution.StageName.ASR,
            failed_attempt=1,
            error_code="ASR_FAILURE",
            error_message="failure",
        )
        DeliveryRecord.objects.create(
            job=self.job,
            artifact=artifact,
            token="tok",
            expires_at=timezone.now() + timedelta(hours=1),
            webhook_status=DeliveryRecord.WebhookStatus.FAILED,
        )

    def test_evaluate_alerts_returns_triggered_checks(self):
        payload = evaluate_alerts(
            window_hours=24,
            max_job_failure_rate_pct=5,
            max_stage_p95_seconds=100,
            max_open_dead_letters=0,
            max_webhook_failure_rate_pct=0,
        )
        triggered_keys = {item["key"] for item in payload["triggered"]}
        self.assertIn("job_failure_rate", triggered_keys)
        self.assertIn("stage_latency_p95", triggered_keys)
        self.assertIn("open_dead_letters", triggered_keys)
        self.assertIn("webhook_failure_rate", triggered_keys)

    def test_sync_alert_events_open_and_resolve(self):
        payload = evaluate_alerts(
            window_hours=24,
            max_job_failure_rate_pct=5,
            max_stage_p95_seconds=100,
            max_open_dead_letters=0,
            max_webhook_failure_rate_pct=0,
        )
        sync_result = sync_alert_events(payload)
        self.assertGreaterEqual(sync_result["opened"], 1)
        self.assertGreater(AlertEvent.objects.filter(status=AlertEvent.Status.OPEN).count(), 0)

        recovery_payload = evaluate_alerts(
            window_hours=24,
            max_job_failure_rate_pct=100,
            max_stage_p95_seconds=1000,
            max_open_dead_letters=100,
            max_webhook_failure_rate_pct=100,
        )
        sync_result_2 = sync_alert_events(recovery_payload)
        self.assertGreaterEqual(sync_result_2["resolved"], 1)

    def test_alerts_view_persist_flag(self):
        factory = APIRequestFactory()
        request = factory.get("/api/v1/telemetry/alerts/?persist=true")
        response = TelemetryAlertsView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("sync", response.data)


class PhaseAAcceptanceTests(TestCase):
    def test_acceptance_report_shape(self):
        report = evaluate_phase_a_acceptance()
        self.assertIn("summary", report)
        self.assertIn("checks", report)
        self.assertEqual(report["summary"]["total_checks"], 4)

    def test_acceptance_delivery_rate_passes_for_delivered_job(self):
        Job.objects.create(name="job-ok", source_language="en", target_language="es", status=Job.Status.DELIVERED)
        report = evaluate_phase_a_acceptance(min_delivery_rate_pct=50.0)
        checks = {item["key"]: item for item in report["checks"]}
        self.assertTrue(checks["delivery_completion_rate"]["passed"])


class QualityAndReleaseTests(TestCase):
    def test_quality_scorecard_shape(self):
        payload = build_quality_scorecard()
        self.assertIn("recommendation", payload)
        self.assertIn("scorecard", payload)

    def test_slo_validation_shape(self):
        payload = validate_phase_a_slos()
        self.assertIn("passed", payload)
        self.assertIn("violations", payload)

    def test_release_readiness_shape(self):
        payload = build_release_readiness_report()
        self.assertIn(payload["go_no_go"], {"GO", "NO_GO"})
        self.assertIn("quality", payload)
        self.assertIn("slo", payload)
