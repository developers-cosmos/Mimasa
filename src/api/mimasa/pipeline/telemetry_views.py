from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Job, JobTransitionEvent, StageExecution


class TelemetrySummaryView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        since = timezone.now() - timedelta(hours=24)

        jobs_by_status = Job.objects.values("status").annotate(total=Count("id")).order_by("status")
        stage_by_status = StageExecution.objects.values("status").annotate(total=Count("id")).order_by("status")

        transition_24h = JobTransitionEvent.objects.filter(created_at__gte=since).count()
        total_jobs = Job.objects.count()

        return Response(
            {
                "request_id": getattr(request, "request_id", ""),
                "total_jobs": total_jobs,
                "jobs_by_status": list(jobs_by_status),
                "stage_executions_by_status": list(stage_by_status),
                "transition_events_last_24h": transition_24h,
            }
        )
