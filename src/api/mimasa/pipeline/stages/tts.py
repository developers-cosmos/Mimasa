from datetime import timedelta

from django.utils import timezone

from pipeline.models import Artifact, Job, StageExecution
from pipeline.orchestrator import transition_job


def _build_placeholder_tts(translation_payload: dict) -> dict:
    segments = translation_payload.get("segments", [])
    voiced_segments = []
    for segment in segments:
        voiced_segments.append(
            {
                "start": segment.get("start", 0.0),
                "end": segment.get("end", 0.0),
                "speaker": segment.get("speaker", "spk_1"),
                "text": segment.get("translated_text", ""),
                "audio_uri": "placeholder://tts-segment",
            }
        )

    return {
        "target_language": translation_payload.get("target_language", "unknown"),
        "segments": voiced_segments,
        "generated_at": timezone.now().isoformat(),
    }


def run_tts_stage(job: Job, *, idempotency_key: str) -> dict:
    existing_done = job.transition_events.filter(idempotency_key=idempotency_key, to_state=Job.Status.TTS_DONE).first()
    if existing_done:
        synth_artifact = job.artifacts.filter(artifact_type=Artifact.ArtifactType.SYNTH_VOICE_V1).order_by("-created_at").first()
        return {
            "idempotent_replay": True,
            "stage_execution_id": "",
            "artifact_id": str(synth_artifact.id) if synth_artifact else "",
        }

    translation_artifact = (
        job.artifacts.filter(artifact_type=Artifact.ArtifactType.TRANSLATION_V1).order_by("-created_at").first()
    )
    if not translation_artifact:
        raise ValueError("TTS stage requires TRANSLATION_V1 artifact")

    stage_execution = StageExecution.objects.create(
        job=job,
        stage_name=StageExecution.StageName.TTS,
        status=StageExecution.Status.RUNNING,
        started_at=timezone.now(),
        attempt=1,
    )

    tts_payload = _build_placeholder_tts(translation_artifact.metadata or {})
    synth_artifact = Artifact.objects.create(
        job=job,
        stage_execution=stage_execution,
        artifact_type=Artifact.ArtifactType.SYNTH_VOICE_V1,
        uri=f"artifact://tts/{job.id}/{stage_execution.id}",
        checksum=f"placeholder-tts:{stage_execution.id}",
        version="v1",
        metadata=tts_payload,
    )

    stage_execution.status = StageExecution.Status.SUCCESS
    stage_execution.ended_at = timezone.now() + timedelta(milliseconds=1)
    stage_execution.save(update_fields=["status", "ended_at"])

    transition_result = transition_job(
        job=job,
        to_state=Job.Status.TTS_DONE,
        idempotency_key=idempotency_key,
        trace_id=job.trace_id,
        reason_code="TTS_STAGE_COMPLETED",
    )

    return {
        "idempotent_replay": transition_result.idempotent_replay,
        "stage_execution_id": str(stage_execution.id),
        "artifact_id": str(synth_artifact.id),
    }
