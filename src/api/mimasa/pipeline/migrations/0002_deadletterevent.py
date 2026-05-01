import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeadLetterEvent",
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
                ("failed_attempt", models.PositiveIntegerField()),
                ("max_attempts", models.PositiveIntegerField(default=3)),
                ("error_code", models.CharField(blank=True, default="", max_length=64)),
                ("error_message", models.TextField(blank=True, default="")),
                ("retry_after_seconds", models.PositiveIntegerField(default=0)),
                ("payload", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("OPEN", "Open"), ("REPLAYED", "Replayed"), ("DISMISSED", "Dismissed")],
                        default="OPEN",
                        max_length=16,
                    ),
                ),
                ("replayed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dead_letters", to="pipeline.job"),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="deadletterevent",
            index=models.Index(fields=["job", "status", "created_at"], name="pipeline_dea_job_id_9b2fa3_idx"),
        ),
    ]
