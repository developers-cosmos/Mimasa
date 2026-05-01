from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from .models import DeadLetterEvent, Job, StageExecution
from .orchestrator import InvalidTransitionError, transition_job
from .stages.asr import run_asr_stage
from .stages.compositing import run_compositing_stage
from .stages.mt import run_mt_stage
from .stages.tts import run_tts_stage

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (30, 120, 600)


@dataclass(frozen=True)
class StageControl:
    stage_name: str
    running_state: str
    run_callable: callable


STAGE_CONTROLS = {
    StageExecution.StageName.ASR: StageControl(
        stage_name=StageExecution.StageName.ASR,
        running_state=Job.Status.ASR_RUNNING,
        run_callable=lambda job, key: run_asr_stage(job, idempotency_key=key, language=job.source_language),
    ),
    StageExecution.StageName.MT: StageControl(
        stage_name=StageExecution.StageName.MT,
        running_state=Job.Status.MT_RUNNING,
        run_callable=lambda job, key: run_mt_stage(job, idempotency_key=key, target_language=job.target_language),
    ),
    StageExecution.StageName.TTS: StageControl(
        stage_name=StageExecution.StageName.TTS,
        running_state=Job.Status.TTS_RUNNING,
        run_callable=lambda job, key: run_tts_stage(job, idempotency_key=key),
    ),
    StageExecution.StageName.COMPOSITING: StageControl(
        stage_name=StageExecution.StageName.COMPOSITING,
        running_state=Job.Status.COMPOSITING_RUNNING,
        run_callable=lambda job, key: run_compositing_stage(job, idempotency_key=key),
    ),
}


@transaction.atomic
def record_stage_failure(
    *,
    job: Job,
    stage_name: str,
    error_message: str,
    error_code: str = "STAGE_EXECUTION_ERROR",
    failure_idempotency_key: str,
) -> DeadLetterEvent:
    failed_attempt = StageExecution.objects.filter(job=job, stage_name=stage_name).count() + 1
    should_fatal = failed_attempt >= MAX_ATTEMPTS
    retry_after = BACKOFF_SECONDS[min(failed_attempt - 1, len(BACKOFF_SECONDS) - 1)]

    dead_letter = DeadLetterEvent.objects.create(
        job=job,
        stage_name=stage_name,
        failed_attempt=failed_attempt,
        max_attempts=MAX_ATTEMPTS,
        error_code=error_code,
        error_message=error_message,
        retry_after_seconds=0 if should_fatal else retry_after,
        payload={"job_status": job.status, "failed_attempt": failed_attempt, "error_code": error_code},
    )

    if should_fatal:
        transition_job(
            job=job,
            to_state=Job.Status.FAILED_FATAL,
            idempotency_key=f"{failure_idempotency_key}:fatal",
            trace_id=job.trace_id,
            reason_code=f"{stage_name}_MAX_RETRIES_EXHAUSTED",
        )

    return dead_letter


def _resolve_stage_control(stage_name: str) -> StageControl:
    try:
        return STAGE_CONTROLS[stage_name]
    except KeyError as exc:
        raise ValueError(f"Stage {stage_name} is not retry-enabled") from exc


@transaction.atomic
def replay_dead_letter(*, job: Job, dead_letter: DeadLetterEvent, idempotency_key: str) -> dict:
    if dead_letter.status != DeadLetterEvent.Status.OPEN:
        raise ValueError("Dead-letter event is not open")

    control = _resolve_stage_control(dead_letter.stage_name)

    if job.status != control.running_state:
        transition_job(
            job=job,
            to_state=control.running_state,
            idempotency_key=f"{idempotency_key}:resume",
            trace_id=job.trace_id,
            reason_code=f"REPLAY_{dead_letter.stage_name}",
        )

    dead_letter.status = DeadLetterEvent.Status.REPLAYED
    dead_letter.replayed_at = timezone.now()
    dead_letter.save(update_fields=["status", "replayed_at"])

    run_result = control.run_callable(job, idempotency_key)
    return {
        "dead_letter_id": str(dead_letter.id),
        "stage_name": dead_letter.stage_name,
        "run_result": run_result,
    }


def retry_latest_failed_stage(*, job: Job, idempotency_key: str, stage_name: str | None = None) -> dict:
    queryset = job.dead_letters.filter(status=DeadLetterEvent.Status.OPEN)
    if stage_name:
        queryset = queryset.filter(stage_name=stage_name)

    dead_letter = queryset.order_by("-created_at").first()
    if not dead_letter:
        raise ValueError("No open dead-letter events available for retry")

    return replay_dead_letter(job=job, dead_letter=dead_letter, idempotency_key=idempotency_key)
