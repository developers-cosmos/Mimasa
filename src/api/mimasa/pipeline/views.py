from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Artifact, DeadLetterEvent, DeliveryRecord, Job, JobTransitionEvent, StageExecution
from .orchestrator import InvalidTransitionError, transition_job
from .delivery import create_signed_delivery, dispatch_webhook_callback, resolve_delivery_download
from .retry_controls import record_stage_failure, replay_dead_letter, retry_latest_failed_stage
from .stages.asr import run_asr_stage
from .stages.compositing import run_compositing_stage
from .stages.mt import run_mt_stage
from .stages.tts import run_tts_stage
from .stages.vertical_slice import run_vertical_slice
from .serializers import (
    ArtifactSerializer,
    ASRStageRunRequestSerializer,
    CompositingStageRunRequestSerializer,
    DeadLetterEventSerializer,
    DeliveryCreateRequestSerializer,
    DeliveryRecordSerializer,
    JobSerializer,
    JobTransitionEventSerializer,
    JobTransitionRequestSerializer,
    MTStageRunRequestSerializer,
    ReplayDeadLetterRequestSerializer,
    RetryJobRequestSerializer,
    StageExecutionSerializer,
    TTSStageRunRequestSerializer,
    VerticalSliceRunRequestSerializer,
)


class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class JobRetrieveView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]


class JobStageListView(generics.ListAPIView):
    serializer_class = StageExecutionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return StageExecution.objects.filter(job_id=self.kwargs["job_id"]).order_by("created_at")


class JobArtifactListView(generics.ListAPIView):
    serializer_class = ArtifactSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Artifact.objects.filter(job_id=self.kwargs["job_id"]).order_by("created_at")


class JobTransitionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        request_serializer = JobTransitionRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            result = transition_job(job=job, **request_serializer.validated_data)
        except InvalidTransitionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        event_serializer = JobTransitionEventSerializer(result.event)
        return Response(
            {
                "idempotent_replay": result.idempotent_replay,
                "event": event_serializer.data,
                "current_job_status": result.event.to_state,
            },
            status=status.HTTP_200_OK,
        )


class JobTransitionEventListView(generics.ListAPIView):
    serializer_class = JobTransitionEventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return JobTransitionEvent.objects.filter(job_id=self.kwargs["job_id"]).order_by("created_at")


class JobDeadLetterListView(generics.ListAPIView):
    serializer_class = DeadLetterEventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return DeadLetterEvent.objects.filter(job_id=self.kwargs["job_id"]).order_by("-created_at")


class JobRetryView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = RetryJobRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            replay_result = retry_latest_failed_stage(
                job=job,
                idempotency_key=serializer.validated_data["idempotency_key"],
                stage_name=serializer.validated_data.get("stage_name"),
            )
        except (ValueError, InvalidTransitionError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(replay_result, status=status.HTTP_200_OK)


class JobReplayDeadLetterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = ReplayDeadLetterRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dead_letter = get_object_or_404(DeadLetterEvent, id=serializer.validated_data["dead_letter_id"], job=job)
        try:
            replay_result = replay_dead_letter(
                job=job,
                dead_letter=dead_letter,
                idempotency_key=serializer.validated_data["idempotency_key"],
            )
        except (ValueError, InvalidTransitionError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(replay_result, status=status.HTTP_200_OK)


class JobDeliveryListView(generics.ListAPIView):
    serializer_class = DeliveryRecordSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return DeliveryRecord.objects.filter(job_id=self.kwargs["job_id"]).order_by("-created_at")


class JobDeliveryCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = DeliveryCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = create_signed_delivery(
                job=job,
                idempotency_key=serializer.validated_data["idempotency_key"],
                ttl_minutes=serializer.validated_data.get("ttl_minutes", 60),
                webhook_url=serializer.validated_data.get("webhook_url", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        dispatch_webhook_callback(delivery=result.delivery, download_url=result.download_url)

        return Response(
            {
                "delivery": DeliveryRecordSerializer(result.delivery).data,
                "download_url": result.download_url,
            },
            status=status.HTTP_201_CREATED,
        )


class JobDeliveryDownloadView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, job_id, delivery_id):
        job = get_object_or_404(Job, id=job_id)
        delivery = get_object_or_404(DeliveryRecord, id=delivery_id, job=job)
        token = request.query_params.get("token", "")

        try:
            artifact = resolve_delivery_download(job=job, delivery=delivery, token=token)
        except Http404 as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "delivery_id": str(delivery.id),
                "artifact_id": str(artifact.id),
                "artifact_type": artifact.artifact_type,
                "artifact_uri": artifact.uri,
                "expires_at": delivery.expires_at,
            },
            status=status.HTTP_200_OK,
        )


class ASRStageRunView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = ASRStageRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if job.status not in {Job.Status.ASR_RUNNING, Job.Status.ASR_DONE}:
            return Response(
                {"detail": f"ASR can run only when job status is ASR_RUNNING/ASR_DONE. Current: {job.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = run_asr_stage(job, **serializer.validated_data)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as exc:
            dead_letter = record_stage_failure(
                job=job,
                stage_name=StageExecution.StageName.ASR,
                error_message=str(exc),
                failure_idempotency_key=serializer.validated_data["idempotency_key"],
            )
            return Response(
                {"detail": str(exc), "dead_letter_id": str(dead_letter.id), "failed_attempt": dead_letter.failed_attempt},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MTStageRunView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = MTStageRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if job.status not in {Job.Status.MT_RUNNING, Job.Status.MT_DONE}:
            return Response(
                {"detail": f"MT can run only when job status is MT_RUNNING/MT_DONE. Current: {job.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = run_mt_stage(job, **serializer.validated_data)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as exc:
            dead_letter = record_stage_failure(
                job=job,
                stage_name=StageExecution.StageName.MT,
                error_message=str(exc),
                failure_idempotency_key=serializer.validated_data["idempotency_key"],
            )
            return Response(
                {"detail": str(exc), "dead_letter_id": str(dead_letter.id), "failed_attempt": dead_letter.failed_attempt},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TTSStageRunView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = TTSStageRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if job.status not in {Job.Status.TTS_RUNNING, Job.Status.TTS_DONE}:
            return Response(
                {"detail": f"TTS can run only when job status is TTS_RUNNING/TTS_DONE. Current: {job.status}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = run_tts_stage(job, **serializer.validated_data)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as exc:
            dead_letter = record_stage_failure(
                job=job,
                stage_name=StageExecution.StageName.TTS,
                error_message=str(exc),
                failure_idempotency_key=serializer.validated_data["idempotency_key"],
            )
            return Response(
                {"detail": str(exc), "dead_letter_id": str(dead_letter.id), "failed_attempt": dead_letter.failed_attempt},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CompositingStageRunView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = CompositingStageRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if job.status not in {Job.Status.COMPOSITING_RUNNING, Job.Status.RENDERED}:
            return Response(
                {
                    "detail": "Compositing can run only when job status is COMPOSITING_RUNNING/RENDERED. "
                    f"Current: {job.status}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = run_compositing_stage(job, **serializer.validated_data)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as exc:
            dead_letter = record_stage_failure(
                job=job,
                stage_name=StageExecution.StageName.COMPOSITING,
                error_message=str(exc),
                failure_idempotency_key=serializer.validated_data["idempotency_key"],
            )
            return Response(
                {"detail": str(exc), "dead_letter_id": str(dead_letter.id), "failed_attempt": dead_letter.failed_attempt},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerticalSliceRunView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        serializer = VerticalSliceRunRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = run_vertical_slice(job, **serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)
