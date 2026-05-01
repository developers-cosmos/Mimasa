from dataclasses import dataclass

from django.db import transaction

from .models import Job, JobTransitionEvent
from .telemetry import log_event


@dataclass
class TransitionResult:
    event: JobTransitionEvent
    idempotent_replay: bool


class InvalidTransitionError(ValueError):
    pass


ALLOWED_TRANSITIONS = {
    Job.Status.CREATED: {Job.Status.PREPROCESSING, Job.Status.CANCELLED},
    Job.Status.PREPROCESSING: {Job.Status.ASR_RUNNING, Job.Status.FAILED_FATAL},
    Job.Status.ASR_RUNNING: {Job.Status.ASR_DONE, Job.Status.FAILED_FATAL},
    Job.Status.ASR_DONE: {Job.Status.MT_RUNNING},
    Job.Status.MT_RUNNING: {Job.Status.MT_DONE, Job.Status.FAILED_FATAL},
    Job.Status.MT_DONE: {Job.Status.TTS_RUNNING},
    Job.Status.TTS_RUNNING: {Job.Status.TTS_DONE, Job.Status.FAILED_FATAL},
    Job.Status.TTS_DONE: {Job.Status.COMPOSITING_RUNNING},
    Job.Status.COMPOSITING_RUNNING: {Job.Status.RENDERED, Job.Status.FAILED_FATAL},
    Job.Status.RENDERED: {Job.Status.QA_PENDING},
    Job.Status.QA_PENDING: {Job.Status.QA_PASSED, Job.Status.QA_FAILED},
    Job.Status.QA_PASSED: {Job.Status.DELIVERING},
    Job.Status.DELIVERING: {Job.Status.DELIVERED, Job.Status.FAILED_FATAL},
    Job.Status.QA_FAILED: {Job.Status.MT_RUNNING, Job.Status.TTS_RUNNING, Job.Status.COMPOSITING_RUNNING},
    Job.Status.DELIVERED: set(),
    Job.Status.FAILED_FATAL: {
        Job.Status.CANCELLED,
        Job.Status.ASR_RUNNING,
        Job.Status.MT_RUNNING,
        Job.Status.TTS_RUNNING,
        Job.Status.COMPOSITING_RUNNING,
        Job.Status.DELIVERING,
    },
    Job.Status.CANCELLED: set(),
}


@transaction.atomic
def transition_job(
    *,
    job: Job,
    to_state: str,
    idempotency_key: str,
    trace_id: str = "",
    reason_code: str = "",
) -> TransitionResult:
    existing = JobTransitionEvent.objects.select_for_update().filter(job=job, idempotency_key=idempotency_key).first()
    if existing:
        log_event("job.transition.replay", job_id=str(job.id), to_state=existing.to_state, idempotency_key=idempotency_key)
        return TransitionResult(event=existing, idempotent_replay=True)

    allowed_next = ALLOWED_TRANSITIONS.get(job.status, set())
    if to_state not in allowed_next:
        raise InvalidTransitionError(f"Transition {job.status} -> {to_state} is not allowed")

    from_state = job.status
    job.status = to_state
    if trace_id and not job.trace_id:
        job.trace_id = trace_id
    job.save(update_fields=["status", "trace_id", "updated_at"])

    log_event("job.transition.accepted", job_id=str(job.id), from_state=from_state, to_state=to_state, idempotency_key=idempotency_key)

    event = JobTransitionEvent.objects.create(
        job=job,
        from_state=from_state,
        to_state=to_state,
        idempotency_key=idempotency_key,
        trace_id=trace_id,
        reason_code=reason_code,
    )
    return TransitionResult(event=event, idempotent_replay=False)
