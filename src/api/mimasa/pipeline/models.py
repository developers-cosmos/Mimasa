import uuid

from django.db import models


class Job(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        PREPROCESSING = "PREPROCESSING", "Preprocessing"
        ASR_RUNNING = "ASR_RUNNING", "ASR Running"
        ASR_DONE = "ASR_DONE", "ASR Done"
        MT_RUNNING = "MT_RUNNING", "MT Running"
        MT_DONE = "MT_DONE", "MT Done"
        TTS_RUNNING = "TTS_RUNNING", "TTS Running"
        TTS_DONE = "TTS_DONE", "TTS Done"
        COMPOSITING_RUNNING = "COMPOSITING_RUNNING", "Compositing Running"
        RENDERED = "RENDERED", "Rendered"
        QA_PENDING = "QA_PENDING", "QA Pending"
        QA_PASSED = "QA_PASSED", "QA Passed"
        QA_FAILED = "QA_FAILED", "QA Failed"
        DELIVERING = "DELIVERING", "Delivering"
        DELIVERED = "DELIVERED", "Delivered"
        FAILED_FATAL = "FAILED_FATAL", "Failed Fatal"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    source_language = models.CharField(max_length=16)
    target_language = models.CharField(max_length=16)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    trace_id = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.id})"


class StageExecution(models.Model):
    class StageName(models.TextChoices):
        PREPROCESSING = "PREPROCESSING", "Preprocessing"
        ASR = "ASR", "ASR"
        MT = "MT", "MT"
        TTS = "TTS", "TTS"
        COMPOSITING = "COMPOSITING", "Compositing"
        QA_EVAL = "QA_EVAL", "QA Eval"
        DELIVERY = "DELIVERY", "Delivery"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="stage_executions", on_delete=models.CASCADE)
    stage_name = models.CharField(max_length=32, choices=StageName.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempt = models.PositiveIntegerField(default=1)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=64, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["job", "stage_name", "attempt"])]


class Artifact(models.Model):
    class ArtifactType(models.TextChoices):
        SOURCE_VIDEO = "SOURCE_VIDEO", "Source Video"
        NORMALIZED_VIDEO = "NORMALIZED_VIDEO", "Normalized Video"
        EXTRACTED_AUDIO = "EXTRACTED_AUDIO", "Extracted Audio"
        TRANSCRIPT_V1 = "TRANSCRIPT_V1", "Transcript V1"
        SPEAKER_SEGMENTS_V1 = "SPEAKER_SEGMENTS_V1", "Speaker Segments V1"
        TRANSLATION_V1 = "TRANSLATION_V1", "Translation V1"
        SYNTH_VOICE_V1 = "SYNTH_VOICE_V1", "Synth Voice V1"
        LOCALIZED_VIDEO_V1 = "LOCALIZED_VIDEO_V1", "Localized Video V1"
        DELIVERY_AUDIO_V1 = "DELIVERY_AUDIO_V1", "Delivery Audio V1"
        QUALITY_REPORT_V1 = "QUALITY_REPORT_V1", "Quality Report V1"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="artifacts", on_delete=models.CASCADE)
    stage_execution = models.ForeignKey(
        StageExecution,
        related_name="artifacts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    artifact_type = models.CharField(max_length=64, choices=ArtifactType.choices)
    uri = models.TextField()
    checksum = models.CharField(max_length=128)
    version = models.CharField(max_length=32, default="v1")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["job", "artifact_type", "version"])]


class JobTransitionEvent(models.Model):
    """Tracks state transitions and enforces idempotency via job+idempotency_key uniqueness."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="transition_events", on_delete=models.CASCADE)
    from_state = models.CharField(max_length=32, choices=Job.Status.choices)
    to_state = models.CharField(max_length=32, choices=Job.Status.choices)
    idempotency_key = models.CharField(max_length=128)
    trace_id = models.CharField(max_length=64, blank=True, default="")
    reason_code = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["job", "idempotency_key"], name="uniq_job_idempotency")]
        indexes = [models.Index(fields=["job", "created_at"])]


class DeliveryRecord(models.Model):
    class WebhookStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="deliveries", on_delete=models.CASCADE)
    artifact = models.ForeignKey(Artifact, related_name="deliveries", on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)
    webhook_url = models.URLField(blank=True, default="")
    webhook_status = models.CharField(max_length=16, choices=WebhookStatus.choices, default=WebhookStatus.PENDING)
    webhook_attempts = models.PositiveIntegerField(default=0)
    webhook_last_response = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["job", "created_at"]), models.Index(fields=["token"])]

class AlertEvent(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        RESOLVED = "RESOLVED", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    severity = models.CharField(max_length=16, default="MEDIUM")
    value = models.FloatField(default=0.0)
    threshold = models.FloatField(default=0.0)
    details = models.JSONField(default=dict, blank=True)
    first_seen_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["key", "status", "updated_at"]) ]

class DeadLetterEvent(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        REPLAYED = "REPLAYED", "Replayed"
        DISMISSED = "DISMISSED", "Dismissed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="dead_letters", on_delete=models.CASCADE)
    stage_name = models.CharField(max_length=32, choices=StageExecution.StageName.choices)
    failed_attempt = models.PositiveIntegerField()
    max_attempts = models.PositiveIntegerField(default=3)
    error_code = models.CharField(max_length=64, blank=True, default="")
    error_message = models.TextField(blank=True, default="")
    retry_after_seconds = models.PositiveIntegerField(default=0)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    replayed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["job", "status", "created_at"])]

class ReviewCorrection(models.Model):
    class ArtifactType(models.TextChoices):
        TRANSCRIPT_V1 = "TRANSCRIPT_V1", "Transcript V1"
        TRANSLATION_V1 = "TRANSLATION_V1", "Translation V1"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="review_corrections", on_delete=models.CASCADE)
    artifact_type = models.CharField(max_length=64, choices=ArtifactType.choices, default=ArtifactType.TRANSLATION_V1)
    segment_key = models.CharField(max_length=128)
    source_text = models.TextField(blank=True, default="")
    corrected_text = models.TextField()
    language = models.CharField(max_length=16)
    reviewer = models.CharField(max_length=120, default="reviewer")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["job", "artifact_type", "segment_key", "created_at"])]

class ReviewDecision(models.Model):
    class Decision(models.TextChoices):
        APPROVE = "APPROVE", "Approve"
        REJECT = "REJECT", "Reject"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, related_name="review_decisions", on_delete=models.CASCADE)
    decision = models.CharField(max_length=16, choices=Decision.choices)
    reviewer = models.CharField(max_length=120, default="reviewer")
    comments = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
