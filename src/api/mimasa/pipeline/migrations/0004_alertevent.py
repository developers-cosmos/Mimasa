import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pipeline", "0003_deliveryrecord"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlertEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("key", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(choices=[("OPEN", "Open"), ("RESOLVED", "Resolved")], default="OPEN", max_length=16),
                ),
                ("severity", models.CharField(default="MEDIUM", max_length=16)),
                ("value", models.FloatField(default=0.0)),
                ("threshold", models.FloatField(default=0.0)),
                ("details", models.JSONField(blank=True, default=dict)),
                ("first_seen_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AddIndex(
            model_name="alertevent",
            index=models.Index(fields=["key", "status", "updated_at"], name="pipeline_ale_key_028728_idx"),
        ),
    ]
