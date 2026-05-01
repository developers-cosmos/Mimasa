from django.contrib import admin

from .models import AlertEvent, Artifact, DeadLetterEvent, DeliveryRecord, Job, JobTransitionEvent, ReviewCorrection, ReviewDecision, StageExecution


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "source_language", "target_language", "status", "created_at")
    list_filter = ("status", "source_language", "target_language")
    search_fields = ("id", "name", "trace_id")


@admin.register(StageExecution)
class StageExecutionAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "stage_name", "status", "attempt", "created_at")
    list_filter = ("stage_name", "status")
    search_fields = ("id", "job__id", "error_code")


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "artifact_type", "version", "created_at")
    list_filter = ("artifact_type", "version")
    search_fields = ("id", "job__id", "checksum", "uri")


@admin.register(JobTransitionEvent)
class JobTransitionEventAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "from_state", "to_state", "idempotency_key", "created_at")
    list_filter = ("from_state", "to_state")
    search_fields = ("id", "job__id", "idempotency_key", "trace_id", "reason_code")


@admin.register(ReviewDecision)
class ReviewDecisionAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "decision", "reviewer", "created_at")
    list_filter = ("decision",)
    search_fields = ("id", "job__id", "reviewer", "comments")


@admin.register(ReviewCorrection)
class ReviewCorrectionAdmin(admin.ModelAdmin):
    list_display = ("job", "artifact_type", "segment_key", "reviewer", "created_at")
    list_filter = ("artifact_type", "language", "reviewer")
    search_fields = ("job__id", "segment_key", "reviewer", "source_text", "corrected_text")


@admin.register(DeadLetterEvent)
class DeadLetterEventAdmin(admin.ModelAdmin):
    list_display = ("job", "stage_name", "failed_attempt", "status", "created_at", "replayed_at")
    list_filter = ("stage_name", "status")
    search_fields = ("job__id", "error_code", "error_message")


@admin.register(DeliveryRecord)
class DeliveryRecordAdmin(admin.ModelAdmin):
    list_display = ("job", "artifact", "expires_at", "download_count", "webhook_status", "created_at")
    list_filter = ("webhook_status",)
    search_fields = ("job__id", "artifact__id", "token", "webhook_url")


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ("key", "status", "severity", "value", "threshold", "updated_at")
    list_filter = ("status", "severity", "key")
    search_fields = ("key",)
