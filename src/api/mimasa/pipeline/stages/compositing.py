from datetime import timedelta

from django.utils import timezone

from pipeline.models import Artifact, Job, StageExecution
from pipeline.orchestrator import transition_job


def _build_compositing_metadata(video_uri: str, synth_payload: dict) -> dict:
    return {
        "video_source": video_uri,
        "target_language": synth_payload.get("target_language", "unknown"),
        "segments": synth_payload.get("segments", []),
        "mux_strategy": "placeholder-audio-video-mux",
        "generated_at": timezone.now().isoformat(),
    }


def run_compositing_stage(job: Job, *, idempotency_key: str) -> dict:
    existing_done = job.transition_events.filter(idempotency_key=idempotency_key, to_state=Job.Status.RENDERED).first()
    if existing_done:
        localized_video = (
            job.artifacts.filter(artifact_type=Artifact.ArtifactType.LOCALIZED_VIDEO_V1).order_by("-created_at").first()
        )
        return {
            "idempotent_replay": True,
            "stage_execution_id": "",
            "artifact_id": str(localized_video.id) if localized_video else "",
        }

    video_artifact = (
        job.artifacts.filter(artifact_type=Artifact.ArtifactType.NORMALIZED_VIDEO).order_by("-created_at").first()
        or job.artifacts.filter(artifact_type=Artifact.ArtifactType.SOURCE_VIDEO).order_by("-created_at").first()
    )
    synth_artifact = job.artifacts.filter(artifact_type=Artifact.ArtifactType.SYNTH_VOICE_V1).order_by("-created_at").first()

    if not video_artifact:
        raise ValueError("Compositing stage requires NORMALIZED_VIDEO or SOURCE_VIDEO artifact")
    if not synth_artifact:
        raise ValueError("Compositing stage requires SYNTH_VOICE_V1 artifact")

    stage_execution = StageExecution.objects.create(
        job=job,
        stage_name=StageExecution.StageName.COMPOSITING,
        status=StageExecution.Status.RUNNING,
        started_at=timezone.now(),
        attempt=1,
    )

    meta = _build_compositing_metadata(video_artifact.uri, synth_artifact.metadata or {})

    delivery_audio = Artifact.objects.create(
        job=job,
        stage_execution=stage_execution,
        artifact_type=Artifact.ArtifactType.DELIVERY_AUDIO_V1,
        uri=f"artifact://delivery-audio/{job.id}/{stage_execution.id}",
        checksum=f"placeholder-delivery-audio:{stage_execution.id}",
        version="v1",
        metadata={"source": synth_artifact.uri, "generated_at": timezone.now().isoformat()},
    )

    localized_video = Artifact.objects.create(
        job=job,
        stage_execution=stage_execution,
        artifact_type=Artifact.ArtifactType.LOCALIZED_VIDEO_V1,
        uri=f"artifact://localized-video/{job.id}/{stage_execution.id}",
        checksum=f"placeholder-localized-video:{stage_execution.id}",
        version="v1",
        metadata={**meta, "delivery_audio_artifact_id": str(delivery_audio.id)},
    )

    stage_execution.status = StageExecution.Status.SUCCESS
    stage_execution.ended_at = timezone.now() + timedelta(milliseconds=1)
    stage_execution.save(update_fields=["status", "ended_at"])

    transition_result = transition_job(
        job=job,
        to_state=Job.Status.RENDERED,
        idempotency_key=idempotency_key,
        trace_id=job.trace_id,
        reason_code="COMPOSITING_STAGE_COMPLETED",
    )

    return {
        "idempotent_replay": transition_result.idempotent_replay,
        "stage_execution_id": str(stage_execution.id),
        "artifact_id": str(localized_video.id),
        "delivery_audio_artifact_id": str(delivery_audio.id),
    }
