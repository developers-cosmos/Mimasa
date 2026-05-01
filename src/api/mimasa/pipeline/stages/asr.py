from datetime import timedelta

from django.utils import timezone

from pipeline.models import Artifact, Job, StageExecution
from pipeline.orchestrator import transition_job


def _build_placeholder_transcript(audio_uri: str, language: str) -> dict:
    return {
        "language": language,
        "source_audio": audio_uri,
        "segments": [
            {
                "start": 0.0,
                "end": 3.0,
                "speaker": "spk_1",
                "text": "placeholder transcript - replace with real ASR engine",
            }
        ],
        "generated_at": timezone.now().isoformat(),
    }


def run_asr_stage(job: Job, *, idempotency_key: str, language: str = "en") -> dict:
    """Run ASR stage integration skeleton and transition job to ASR_DONE."""
    existing_done = job.transition_events.filter(idempotency_key=idempotency_key, to_state=Job.Status.ASR_DONE).first()
    if existing_done:
        transcript = (
            job.artifacts.filter(artifact_type=Artifact.ArtifactType.TRANSCRIPT_V1).order_by("-created_at").first()
        )
        return {
            "idempotent_replay": True,
            "stage_execution_id": "",
            "artifact_id": str(transcript.id) if transcript else "",
        }

    audio_artifact = job.artifacts.filter(artifact_type=Artifact.ArtifactType.EXTRACTED_AUDIO).order_by("-created_at").first()
    if not audio_artifact:
        raise ValueError("ASR stage requires EXTRACTED_AUDIO artifact")

    stage_execution = StageExecution.objects.create(
        job=job,
        stage_name=StageExecution.StageName.ASR,
        status=StageExecution.Status.RUNNING,
        started_at=timezone.now(),
        attempt=1,
    )

    transcript_payload = _build_placeholder_transcript(audio_uri=audio_artifact.uri, language=language)
    transcript_artifact = Artifact.objects.create(
        job=job,
        stage_execution=stage_execution,
        artifact_type=Artifact.ArtifactType.TRANSCRIPT_V1,
        uri=f"artifact://transcript/{job.id}/{stage_execution.id}",
        checksum=f"placeholder:{stage_execution.id}",
        version="v1",
        metadata=transcript_payload,
    )

    speaker_artifact = Artifact.objects.create(
        job=job,
        stage_execution=stage_execution,
        artifact_type=Artifact.ArtifactType.SPEAKER_SEGMENTS_V1,
        uri=f"artifact://speaker-segments/{job.id}/{stage_execution.id}",
        checksum=f"placeholder-speaker:{stage_execution.id}",
        version="v1",
        metadata={"speakers": ["spk_1"], "segments": transcript_payload["segments"]},
    )

    stage_execution.status = StageExecution.Status.SUCCESS
    stage_execution.ended_at = timezone.now() + timedelta(milliseconds=1)
    stage_execution.save(update_fields=["status", "ended_at"])

    transition_result = transition_job(
        job=job,
        to_state=Job.Status.ASR_DONE,
        idempotency_key=idempotency_key,
        trace_id=job.trace_id,
        reason_code="ASR_STAGE_COMPLETED",
    )

    return {
        "idempotent_replay": transition_result.idempotent_replay,
        "stage_execution_id": str(stage_execution.id),
        "artifact_id": str(transcript_artifact.id),
        "speaker_artifact_id": str(speaker_artifact.id),
    }
