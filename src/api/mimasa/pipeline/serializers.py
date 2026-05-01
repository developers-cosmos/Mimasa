from rest_framework import serializers

from .models import AlertEvent, Artifact, DeadLetterEvent, DeliveryRecord, Job, JobTransitionEvent, ReviewCorrection, ReviewDecision, StageExecution


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "name",
            "source_language",
            "target_language",
            "status",
            "trace_id",
            "created_at",
            "updated_at",
        ]


class StageExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageExecution
        fields = [
            "id",
            "job",
            "stage_name",
            "status",
            "attempt",
            "started_at",
            "ended_at",
            "error_code",
            "error_message",
            "created_at",
        ]


class ArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artifact
        fields = [
            "id",
            "job",
            "stage_execution",
            "artifact_type",
            "uri",
            "checksum",
            "version",
            "metadata",
            "created_at",
        ]


class JobTransitionRequestSerializer(serializers.Serializer):
    to_state = serializers.ChoiceField(choices=Job.Status.choices)
    idempotency_key = serializers.CharField(max_length=128)
    trace_id = serializers.CharField(max_length=64, required=False, allow_blank=True)
    reason_code = serializers.CharField(max_length=64, required=False, allow_blank=True)


class JobTransitionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobTransitionEvent
        fields = [
            "id",
            "job",
            "from_state",
            "to_state",
            "idempotency_key",
            "trace_id",
            "reason_code",
            "created_at",
        ]


class ASRStageRunRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)
    language = serializers.CharField(max_length=16, required=False, default="en")


class MTStageRunRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)
    target_language = serializers.CharField(max_length=16)


class TTSStageRunRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)


class CompositingStageRunRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)


class VerticalSliceRunRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)
    source_video_uri = serializers.CharField(max_length=1024)
    target_language = serializers.CharField(max_length=16)


class AlertEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertEvent
        fields = [
            "id",
            "key",
            "status",
            "severity",
            "value",
            "threshold",
            "details",
            "first_seen_at",
            "updated_at",
            "resolved_at",
        ]

class DeliveryRecordSerializer(serializers.ModelSerializer):
    artifact_type = serializers.CharField(source="artifact.artifact_type", read_only=True)
    artifact_uri = serializers.CharField(source="artifact.uri", read_only=True)

    class Meta:
        model = DeliveryRecord
        fields = [
            "id",
            "job",
            "artifact",
            "artifact_type",
            "artifact_uri",
            "expires_at",
            "download_count",
            "last_downloaded_at",
            "webhook_url",
            "webhook_status",
            "webhook_attempts",
            "webhook_last_response",
            "created_at",
        ]


class DeliveryCreateRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)
    ttl_minutes = serializers.IntegerField(min_value=1, max_value=1440, required=False, default=60)
    webhook_url = serializers.URLField(required=False, allow_blank=True, default="")

class DeadLetterEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeadLetterEvent
        fields = [
            "id",
            "job",
            "stage_name",
            "failed_attempt",
            "max_attempts",
            "error_code",
            "error_message",
            "retry_after_seconds",
            "payload",
            "status",
            "replayed_at",
            "created_at",
        ]


class RetryJobRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)
    stage_name = serializers.ChoiceField(choices=StageExecution.StageName.choices, required=False)


class ReplayDeadLetterRequestSerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(max_length=128)
    dead_letter_id = serializers.UUIDField()

class ReviewCorrectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewCorrection
        fields = [
            "id",
            "job",
            "artifact_type",
            "segment_key",
            "source_text",
            "corrected_text",
            "language",
            "reviewer",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "job"]

class ReviewDecisionRequestSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=ReviewDecision.Decision.choices)
    idempotency_key = serializers.CharField(max_length=128)
    reviewer = serializers.CharField(max_length=120, required=False, default="reviewer")
    comments = serializers.CharField(required=False, allow_blank=True, default="")
