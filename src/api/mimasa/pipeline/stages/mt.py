from datetime import timedelta

from django.utils import timezone

from pipeline.models import Artifact, Job, StageExecution
from pipeline.orchestrator import transition_job


def _translate_segments_placeholder(transcript: dict, target_language: str) -> dict:
    segments = transcript.get("segments", [])
    translated_segments = []
    for segment in segments:
        translated_segments.append(
            {
                **segment,
                "translated_text": f"[{target_language}] {segment.get('text', '')}",
            }
        )

    return {
        "source_language": transcript.get("language", "unknown"),
        "target_language": target_language,
        "segments": translated_segments,
        "generated_at": timezone.now().isoformat(),
    }


def run_mt_stage(job: Job, *, idempotency_key: str, target_language: str) -> dict:
    existing_done = job.transition_events.filter(idempotency_key=idempotency_key, to_state=Job.Status.MT_DONE).first()
    if existing_done:
        translation_artifact = (
            job.artifacts.filter(artifact_type=Artifact.ArtifactType.TRANSLATION_V1).order_by("-created_at").first()
        )
        return {
            "idempotent_replay": True,
            "stage_execution_id": "",
            "artifact_id": str(translation_artifact.id) if translation_artifact else "",
        }

    transcript_artifact = job.artifacts.filter(artifact_type=Artifact.ArtifactType.TRANSCRIPT_V1).order_by("-created_at").first()
    if not transcript_artifact:
        raise ValueError("MT stage requires TRANSCRIPT_V1 artifact")

    stage_execution = StageExecution.objects.create(
        job=job,
        stage_name=StageExecution.StageName.MT,
        status=StageExecution.Status.RUNNING,
        started_at=timezone.now(),
        attempt=1,
    )

    transcript_payload = transcript_artifact.metadata or {}
    translation_payload = _translate_segments_placeholder(transcript_payload, target_language)

    translation_artifact = Artifact.objects.create(
        job=job,
        stage_execution=stage_execution,
        artifact_type=Artifact.ArtifactType.TRANSLATION_V1,
        uri=f"artifact://translation/{job.id}/{stage_execution.id}",
        checksum=f"placeholder-translation:{stage_execution.id}",
        version="v1",
        metadata=translation_payload,
    )

    stage_execution.status = StageExecution.Status.SUCCESS
    stage_execution.ended_at = timezone.now() + timedelta(milliseconds=1)
    stage_execution.save(update_fields=["status", "ended_at"])

    transition_result = transition_job(
        job=job,
        to_state=Job.Status.MT_DONE,
        idempotency_key=idempotency_key,
        trace_id=job.trace_id,
        reason_code="MT_STAGE_COMPLETED",
    )

    return {
        "idempotent_replay": transition_result.idempotent_replay,
        "stage_execution_id": str(stage_execution.id),
        "artifact_id": str(translation_artifact.id),
    }
