import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Artifact, Job, ReviewCorrection, ReviewDecision
from .orchestrator import InvalidTransitionError, transition_job
from .serializers import ReviewCorrectionSerializer, ReviewDecisionRequestSerializer


class ReviewDashboardView(LoginRequiredMixin, View):
    def get(self, request):
        jobs = Job.objects.filter(status__in=[Job.Status.QA_PENDING, Job.Status.QA_FAILED, Job.Status.QA_PASSED]).order_by(
            "-updated_at"
        )
        return render(request, "pipeline/review_dashboard.html", {"jobs": jobs})


class ReviewJobDetailView(LoginRequiredMixin, View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        artifacts = Artifact.objects.filter(job=job).order_by("-created_at")
        decisions = job.review_decisions.order_by("-created_at")
        corrections = job.review_corrections.order_by("-created_at")
        return render(
            request,
            "pipeline/review_job.html",
            {"job": job, "artifacts": artifacts, "decisions": decisions, "corrections": corrections},
        )


class ReviewDecisionAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = ReviewDecisionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        decision = serializer.validated_data["decision"]
        to_state = Job.Status.QA_PASSED if decision == ReviewDecision.Decision.APPROVE else Job.Status.QA_FAILED

        try:
            transition_job(
                job=job,
                to_state=to_state,
                idempotency_key=serializer.validated_data["idempotency_key"],
                reason_code=f"REVIEW_{decision}",
                trace_id=job.trace_id,
            )
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        ReviewDecision.objects.create(
            job=job,
            decision=decision,
            reviewer=serializer.validated_data.get("reviewer") or request.user.get_username() or "reviewer",
            comments=serializer.validated_data.get("comments", ""),
        )

        return Response({"job_id": str(job.id), "decision": decision, "new_status": to_state}, status=status.HTTP_200_OK)


class ReviewCorrectionListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewCorrectionSerializer

    def get_queryset(self):
        return ReviewCorrection.objects.filter(job_id=self.kwargs["job_id"]).order_by("-created_at")

    def perform_create(self, serializer):
        job = get_object_or_404(Job, id=self.kwargs["job_id"])
        serializer.save(job=job, reviewer=serializer.validated_data.get("reviewer") or self.request.user.get_username())


class ReviewDecisionFormView(LoginRequiredMixin, View):
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        decision = request.POST.get("decision", ReviewDecision.Decision.REJECT)
        idempotency_key = request.POST.get("idempotency_key") or str(uuid.uuid4())
        reviewer = request.POST.get("reviewer") or request.user.get_username() or "reviewer"
        comments = request.POST.get("comments", "")

        to_state = Job.Status.QA_PASSED if decision == ReviewDecision.Decision.APPROVE else Job.Status.QA_FAILED

        try:
            transition_job(
                job=job,
                to_state=to_state,
                idempotency_key=idempotency_key,
                reason_code=f"REVIEW_{decision}",
                trace_id=job.trace_id,
            )
            ReviewDecision.objects.create(job=job, decision=decision, reviewer=reviewer, comments=comments)
        except InvalidTransitionError:
            pass

        return redirect("review_job", job_id=job_id)


class ReviewCorrectionFormView(LoginRequiredMixin, View):
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        payload = {
            "segment_key": request.POST.get("segment_key", ""),
            "source_text": request.POST.get("source_text", ""),
            "corrected_text": request.POST.get("corrected_text", ""),
            "language": request.POST.get("language", job.target_language),
            "artifact_type": request.POST.get("artifact_type", ReviewCorrection.ArtifactType.TRANSLATION_V1),
            "reviewer": request.POST.get("reviewer") or request.user.get_username() or "reviewer",
        }
        serializer = ReviewCorrectionSerializer(data=payload)
        if serializer.is_valid():
            serializer.save(job=job)

        return redirect("review_job", job_id=job_id)
