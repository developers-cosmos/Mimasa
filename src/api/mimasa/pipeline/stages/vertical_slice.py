from django.utils import timezone

from pipeline.models import Artifact, Job
from pipeline.orchestrator import transition_job
from pipeline.stages.asr import run_asr_stage
from pipeline.stages.compositing import run_compositing_stage
from pipeline.stages.mt import run_mt_stage
from pipeline.stages.tts import run_tts_stage


def _ensure_preprocessing_artifacts(job: Job, source_video_uri: str) -> dict:
    source_video = job.artifacts.filter(artifact_type=Artifact.ArtifactType.SOURCE_VIDEO).order_by("-created_at").first()
    if not source_video:
        source_video = Artifact.objects.create(
            job=job,
            stage_execution=None,
            artifact_type=Artifact.ArtifactType.SOURCE_VIDEO,
            uri=source_video_uri,
            checksum=f"placeholder-source:{job.id}",
            version="v1",
            metadata={"created_at": timezone.now().isoformat()},
        )

    normalized = (
        job.artifacts.filter(artifact_type=Artifact.ArtifactType.NORMALIZED_VIDEO).order_by("-created_at").first()
    )
    if not normalized:
        normalized = Artifact.objects.create(
            job=job,
            stage_execution=None,
            artifact_type=Artifact.ArtifactType.NORMALIZED_VIDEO,
            uri=f"artifact://normalized-video/{job.id}",
            checksum=f"placeholder-normalized:{job.id}",
            version="v1",
            metadata={"source_artifact_id": str(source_video.id)},
        )

    extracted_audio = (
        job.artifacts.filter(artifact_type=Artifact.ArtifactType.EXTRACTED_AUDIO).order_by("-created_at").first()
    )
    if not extracted_audio:
        extracted_audio = Artifact.objects.create(
            job=job,
            stage_execution=None,
            artifact_type=Artifact.ArtifactType.EXTRACTED_AUDIO,
            uri=f"artifact://extracted-audio/{job.id}",
            checksum=f"placeholder-audio:{job.id}",
            version="v1",
            metadata={"source_artifact_id": str(source_video.id)},
        )

    return {
        "source_video_artifact_id": str(source_video.id),
        "normalized_video_artifact_id": str(normalized.id),
        "extracted_audio_artifact_id": str(extracted_audio.id),
    }


def run_vertical_slice(job: Job, *, idempotency_key: str, source_video_uri: str, target_language: str) -> dict:
    if job.status == Job.Status.CREATED:
        transition_job(job=job, to_state=Job.Status.PREPROCESSING, idempotency_key=f"{idempotency_key}:prep")

    prep_artifacts = _ensure_preprocessing_artifacts(job, source_video_uri)

    if job.status == Job.Status.PREPROCESSING:
        transition_job(job=job, to_state=Job.Status.ASR_RUNNING, idempotency_key=f"{idempotency_key}:asr:start")

    asr_result = run_asr_stage(job, idempotency_key=f"{idempotency_key}:asr", language=job.source_language)

    if job.status == Job.Status.ASR_DONE:
        transition_job(job=job, to_state=Job.Status.MT_RUNNING, idempotency_key=f"{idempotency_key}:mt:start")

    mt_result = run_mt_stage(job, idempotency_key=f"{idempotency_key}:mt", target_language=target_language)

    if job.status == Job.Status.MT_DONE:
        transition_job(job=job, to_state=Job.Status.TTS_RUNNING, idempotency_key=f"{idempotency_key}:tts:start")

    tts_result = run_tts_stage(job, idempotency_key=f"{idempotency_key}:tts")

    if job.status == Job.Status.TTS_DONE:
        transition_job(job=job, to_state=Job.Status.COMPOSITING_RUNNING, idempotency_key=f"{idempotency_key}:comp:start")

    compositing_result = run_compositing_stage(job, idempotency_key=f"{idempotency_key}:comp")

    localized_video = (
        job.artifacts.filter(artifact_type=Artifact.ArtifactType.LOCALIZED_VIDEO_V1).order_by("-created_at").first()
    )

    return {
        "job_id": str(job.id),
        "final_status": job.status,
        "preprocessing": prep_artifacts,
        "asr": asr_result,
        "mt": mt_result,
        "tts": tts_result,
        "compositing": compositing_result,
        "localized_video_artifact_id": str(localized_video.id) if localized_video else "",
    }
