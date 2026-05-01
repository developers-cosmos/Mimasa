from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .alerting import evaluate_alerts, sync_alert_events
from .models import AlertEvent
from .serializers import AlertEventSerializer


class TelemetryAlertsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        payload = evaluate_alerts(
            window_hours=getattr(settings, "PIPELINE_ALERT_WINDOW_HOURS", 24),
            max_job_failure_rate_pct=getattr(settings, "PIPELINE_ALERT_MAX_JOB_FAILURE_RATE_PCT", 10.0),
            max_stage_p95_seconds=getattr(settings, "PIPELINE_ALERT_MAX_STAGE_P95_SECONDS", 120.0),
            max_open_dead_letters=getattr(settings, "PIPELINE_ALERT_MAX_OPEN_DEAD_LETTERS", 5),
            max_webhook_failure_rate_pct=getattr(settings, "PIPELINE_ALERT_MAX_WEBHOOK_FAILURE_RATE_PCT", 20.0),
        )

        persist = request.query_params.get("persist", "false").lower() in {"1", "true", "yes"}
        if persist:
            payload["sync"] = sync_alert_events(payload)

        return Response(payload)


class AlertEventListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AlertEventSerializer
    queryset = AlertEvent.objects.all().order_by("-updated_at")
