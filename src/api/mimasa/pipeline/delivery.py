import json
import secrets
from dataclasses import dataclass
from datetime import timedelta
from urllib import error, request

from django.db import transaction
from django.http import Http404
from django.utils import timezone

from .models import Artifact, DeliveryRecord, Job
from .orchestrator import InvalidTransitionError, transition_job


@dataclass(frozen=True)
class DeliveryResult:
    delivery: DeliveryRecord
    download_url: str


def _build_download_url(*, job_id: str, delivery_id: str, token: str) -> str:
    return f"/api/v1/jobs/{job_id}/deliveries/{delivery_id}/download/?token={token}"


@transaction.atomic
def create_signed_delivery(
    *,
    job: Job,
    idempotency_key: str,
    ttl_minutes: int = 60,
    webhook_url: str = "",
) -> DeliveryResult:
    localized_video = (
        job.artifacts.filter(artifact_type=Artifact.ArtifactType.LOCALIZED_VIDEO_V1).order_by("-created_at").first()
    )
    if not localized_video:
        raise ValueError("Delivery requires LOCALIZED_VIDEO_V1 artifact")

    try:
        if job.status != Job.Status.DELIVERING:
            transition_job(
                job=job,
                to_state=Job.Status.DELIVERING,
                idempotency_key=f"{idempotency_key}:start-delivery",
                trace_id=job.trace_id,
                reason_code="DELIVERY_STARTED",
            )

        token = secrets.token_urlsafe(32)
        delivery = DeliveryRecord.objects.create(
            job=job,
            artifact=localized_video,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=max(ttl_minutes, 1)),
            webhook_url=webhook_url or "",
        )

        transition_job(
            job=job,
            to_state=Job.Status.DELIVERED,
            idempotency_key=f"{idempotency_key}:complete-delivery",
            trace_id=job.trace_id,
            reason_code="DELIVERY_COMPLETED",
        )
    except InvalidTransitionError as exc:
        raise ValueError(str(exc)) from exc

    return DeliveryResult(delivery=delivery, download_url=_build_download_url(job_id=str(job.id), delivery_id=str(delivery.id), token=token))


def resolve_delivery_download(*, job: Job, delivery: DeliveryRecord, token: str) -> Artifact:
    if delivery.job_id != job.id:
        raise Http404("Delivery does not belong to requested job")
    if token != delivery.token:
        raise Http404("Invalid delivery token")
    if timezone.now() > delivery.expires_at:
        raise Http404("Delivery token expired")

    delivery.download_count += 1
    delivery.last_downloaded_at = timezone.now()
    delivery.save(update_fields=["download_count", "last_downloaded_at"])
    return delivery.artifact


def dispatch_webhook_callback(*, delivery: DeliveryRecord, download_url: str) -> None:
    if not delivery.webhook_url:
        return

    payload = {
        "job_id": str(delivery.job_id),
        "delivery_id": str(delivery.id),
        "status": "DELIVERED",
        "download_url": download_url,
        "expires_at": delivery.expires_at.isoformat(),
        "event_time": timezone.now().isoformat(),
    }

    delivery.webhook_attempts += 1

    req = request.Request(
        delivery.webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            delivery.webhook_status = DeliveryRecord.WebhookStatus.SENT
            delivery.webhook_last_response = body[:2000]
    except (error.URLError, TimeoutError) as exc:
        delivery.webhook_status = DeliveryRecord.WebhookStatus.FAILED
        delivery.webhook_last_response = str(exc)[:2000]

    delivery.save(update_fields=["webhook_attempts", "webhook_status", "webhook_last_response"])
