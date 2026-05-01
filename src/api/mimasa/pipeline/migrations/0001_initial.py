# Generated manually for pipeline app bootstrap.

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Job",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("source_language", models.CharField(max_length=16)),
                ("target_language", models.CharField(max_length=16)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CREATED", "Created"),
                            ("PREPROCESSING", "Preprocessing"),
                            ("ASR_RUNNING", "ASR Running"),
                            ("ASR_DONE", "ASR Done"),
                            ("MT_RUNNING", "MT Running"),
                            ("MT_DONE", "MT Done"),
                            ("TTS_RUNNING", "TTS Running"),
                            ("TTS_DONE", "TTS Done"),
                            ("COMPOSITING_RUNNING", "Compositing Running"),
                            ("RENDERED", "Rendered"),
                            ("QA_PENDING", "QA Pending"),
                            ("QA_PASSED", "QA Passed"),
                            ("QA_FAILED", "QA Failed"),
                            ("DELIVERING", "Delivering"),
                            ("DELIVERED", "Delivered"),
                            ("FAILED_FATAL", "Failed Fatal"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        default="CREATED",
                        max_length=32,
                    ),
                ),
                ("trace_id", models.CharField(blank=True, default="", max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="ReviewDecision",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "decision",
                    models.CharField(choices=[("APPROVE", "Approve"), ("REJECT", "Reject")], max_length=16),
                ),
                ("reviewer", models.CharField(default="reviewer", max_length=120)),
                ("comments", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="review_decisions", to="pipeline.job"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StageExecution",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "stage_name",
                    models.CharField(
                        choices=[
                            ("PREPROCESSING", "Preprocessing"),
                            ("ASR", "ASR"),
                            ("MT", "MT"),
                            ("TTS", "TTS"),
                            ("COMPOSITING", "Compositing"),
                            ("QA_EVAL", "QA Eval"),
                            ("DELIVERY", "Delivery"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("RUNNING", "Running"), ("SUCCESS", "Success"), ("FAILED", "Failed")],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("attempt", models.PositiveIntegerField(default=1)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("error_code", models.CharField(blank=True, default="", max_length=64)),
                ("error_message", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stage_executions", to="pipeline.job"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReviewCorrection",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "artifact_type",
                    models.CharField(
                        choices=[("TRANSCRIPT_V1", "Transcript V1"), ("TRANSLATION_V1", "Translation V1")],
                        default="TRANSLATION_V1",
                        max_length=64,
                    ),
                ),
                ("segment_key", models.CharField(max_length=128)),
                ("source_text", models.TextField(blank=True, default="")),
                ("corrected_text", models.TextField()),
                ("language", models.CharField(max_length=16)),
                ("reviewer", models.CharField(default="reviewer", max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="review_corrections", to="pipeline.job"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="JobTransitionEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "from_state",
                    models.CharField(
                        choices=[
                            ("CREATED", "Created"),
                            ("PREPROCESSING", "Preprocessing"),
                            ("ASR_RUNNING", "ASR Running"),
                            ("ASR_DONE", "ASR Done"),
                            ("MT_RUNNING", "MT Running"),
                            ("MT_DONE", "MT Done"),
                            ("TTS_RUNNING", "TTS Running"),
                            ("TTS_DONE", "TTS Done"),
                            ("COMPOSITING_RUNNING", "Compositing Running"),
                            ("RENDERED", "Rendered"),
                            ("QA_PENDING", "QA Pending"),
                            ("QA_PASSED", "QA Passed"),
                            ("QA_FAILED", "QA Failed"),
                            ("DELIVERING", "Delivering"),
                            ("DELIVERED", "Delivered"),
                            ("FAILED_FATAL", "Failed Fatal"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "to_state",
                    models.CharField(
                        choices=[
                            ("CREATED", "Created"),
                            ("PREPROCESSING", "Preprocessing"),
                            ("ASR_RUNNING", "ASR Running"),
                            ("ASR_DONE", "ASR Done"),
                            ("MT_RUNNING", "MT Running"),
                            ("MT_DONE", "MT Done"),
                            ("TTS_RUNNING", "TTS Running"),
                            ("TTS_DONE", "TTS Done"),
                            ("COMPOSITING_RUNNING", "Compositing Running"),
                            ("RENDERED", "Rendered"),
                            ("QA_PENDING", "QA Pending"),
                            ("QA_PASSED", "QA Passed"),
                            ("QA_FAILED", "QA Failed"),
                            ("DELIVERING", "Delivering"),
                            ("DELIVERED", "Delivered"),
                            ("FAILED_FATAL", "Failed Fatal"),
                            ("CANCELLED", "Cancelled"),
                        ],
                        max_length=32,
                    ),
                ),
                ("idempotency_key", models.CharField(max_length=128)),
                ("trace_id", models.CharField(blank=True, default="", max_length=64)),
                ("reason_code", models.CharField(blank=True, default="", max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transition_events", to="pipeline.job"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Artifact",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "artifact_type",
                    models.CharField(
                        choices=[
                            ("SOURCE_VIDEO", "Source Video"),
                            ("NORMALIZED_VIDEO", "Normalized Video"),
                            ("EXTRACTED_AUDIO", "Extracted Audio"),
                            ("TRANSCRIPT_V1", "Transcript V1"),
                            ("SPEAKER_SEGMENTS_V1", "Speaker Segments V1"),
                            ("TRANSLATION_V1", "Translation V1"),
                            ("SYNTH_VOICE_V1", "Synth Voice V1"),
                            ("LOCALIZED_VIDEO_V1", "Localized Video V1"),
                            ("DELIVERY_AUDIO_V1", "Delivery Audio V1"),
                            ("QUALITY_REPORT_V1", "Quality Report V1"),
                        ],
                        max_length=64,
                    ),
                ),
                ("uri", models.TextField()),
                ("checksum", models.CharField(max_length=128)),
                ("version", models.CharField(default="v1", max_length=32)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="artifacts", to="pipeline.job"),
                ),
                (
                    "stage_execution",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="artifacts",
                        to="pipeline.stageexecution",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="stageexecution",
            index=models.Index(fields=["job", "stage_name", "attempt"], name="pipeline_sta_job_id_d2733c_idx"),
        ),
        migrations.AddIndex(
            model_name="reviewcorrection",
            index=models.Index(
                fields=["job", "artifact_type", "segment_key", "created_at"],
                name="pipeline_rev_job_id_6be35c_idx",
            ),
        ),
        migrations.AddConstraint(
            model_name="jobtransitionevent",
            constraint=models.UniqueConstraint(fields=("job", "idempotency_key"), name="uniq_job_idempotency"),
        ),
        migrations.AddIndex(
            model_name="jobtransitionevent",
            index=models.Index(fields=["job", "created_at"], name="pipeline_job_job_id_86b918_idx"),
        ),
        migrations.AddIndex(
            model_name="artifact",
            index=models.Index(fields=["job", "artifact_type", "version"], name="pipeline_art_job_id_974cc2_idx"),
        ),
    ]
