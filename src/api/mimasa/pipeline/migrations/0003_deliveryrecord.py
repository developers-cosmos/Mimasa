import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0002_deadletterevent"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryRecord",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("token", models.CharField(max_length=128, unique=True)),
                ("expires_at", models.DateTimeField()),
                ("download_count", models.PositiveIntegerField(default=0)),
                ("last_downloaded_at", models.DateTimeField(blank=True, null=True)),
                ("webhook_url", models.URLField(blank=True, default="")),
                (
                    "webhook_status",
                    models.CharField(
                        choices=[("PENDING", "Pending"), ("SENT", "Sent"), ("FAILED", "Failed")],
                        default="PENDING",
                        max_length=16,
                    ),
                ),
                ("webhook_attempts", models.PositiveIntegerField(default=0)),
                ("webhook_last_response", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "artifact",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="deliveries", to="pipeline.artifact"),
                ),
                (
                    "job",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="deliveries", to="pipeline.job"),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="deliveryrecord",
            index=models.Index(fields=["job", "created_at"], name="pipeline_del_job_id_b4c84b_idx"),
        ),
        migrations.AddIndex(
            model_name="deliveryrecord",
            index=models.Index(fields=["token"], name="pipeline_del_token_5eb8c0_idx"),
        ),
    ]
