# WI-001 — Phase A State Machine Specification

**Owner Role:** System Architect  
**Status:** Completed  
**Related Work Item:** WI-001 (Finalize stage contracts and state machine)

## 1) Purpose

Define a deterministic, auditable job lifecycle for Phase A (audio-first localization) so every team can build against one source of truth.

## 2) State Model

```text
CREATED
  -> PREPROCESSING
  -> PREPROCESSING_FAILED (retryable)

PREPROCESSING
  -> ASR_RUNNING
  -> FAILED_FATAL

ASR_RUNNING
  -> ASR_DONE
  -> ASR_FAILED (retryable)

ASR_DONE
  -> MT_RUNNING

MT_RUNNING
  -> MT_DONE
  -> MT_FAILED (retryable)

MT_DONE
  -> TTS_RUNNING

TTS_RUNNING
  -> TTS_DONE
  -> TTS_FAILED (retryable)

TTS_DONE
  -> COMPOSITING_RUNNING

COMPOSITING_RUNNING
  -> RENDERED
  -> COMPOSITING_FAILED (retryable)

RENDERED
  -> QA_PENDING

QA_PENDING
  -> QA_PASSED
  -> QA_FAILED

QA_PASSED
  -> DELIVERING

DELIVERING
  -> DELIVERED
  -> DELIVERY_FAILED (retryable)

QA_FAILED
  -> REWORK_REQUIRED

REWORK_REQUIRED
  -> MT_RUNNING | TTS_RUNNING | COMPOSITING_RUNNING (based on reviewer choice)

FAILED_FATAL
  -> CANCELLED (operator)
```

## 3) Terminal States

- `DELIVERED`
- `CANCELLED`
- `FAILED_FATAL`

## 4) Retry Semantics

Retryable states:
- `PREPROCESSING_FAILED`, `ASR_FAILED`, `MT_FAILED`, `TTS_FAILED`, `COMPOSITING_FAILED`, `DELIVERY_FAILED`

Policy:
- max attempts per stage: 3
- exponential backoff: 30s, 2m, 10m
- on final failure:
  - if stage is critical and no fallback available -> `FAILED_FATAL`
  - if fallback path exists and policy allows -> proceed to fallback stage

## 5) Idempotency Rules

- `job_id + stage_name + attempt` uniquely identifies an execution attempt.
- Re-running the same attempt must not create duplicate artifacts.
- Stage outputs are immutable and versioned.

## 6) Event Contract (Minimum)

Each transition emits:
- `event_id`
- `job_id`
- `from_state`
- `to_state`
- `timestamp`
- `trace_id`
- `actor_type` (`system`, `reviewer`, `operator`)
- `reason_code` (optional)

## 7) Ownership by State

- System-managed: `CREATED` -> `QA_PENDING`
- Reviewer-managed: `QA_PENDING` -> `QA_PASSED` / `QA_FAILED`
- Operator-managed: cancellation/retry overrides

## 8) Acceptance Criteria for WI-001

1. All teams reference this state model in implementation tickets.
2. No custom ad-hoc states are introduced without ADR.
3. API and DB schemas map exactly to these states.
4. Retry and rework paths are explicitly supported.
