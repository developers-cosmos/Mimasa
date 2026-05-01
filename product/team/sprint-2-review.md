# Sprint 2 Review — Phase A (Vertical Slice)

**Sprint Window:** 2 weeks  
**Review Owner:** Product Lead  
**Date:** 2026-04-26

## 1) Sprint Goal

Deliver a runnable vertical slice for Phase A:
- WI-005: ASR stage integration
- WI-006: MT stage integration
- WI-007: TTS stage integration
- WI-008: Compositing stage integration
- WI-009: End-to-end run using sample artifact flow

## 2) Outcome Summary

### Completed
- ✅ WI-005 completed (ASR skeleton + transcript/speaker artifacts)
- ✅ WI-006 completed (MT skeleton + translation artifacts)
- ✅ WI-007 completed (TTS skeleton + synth voice artifacts)
- ✅ WI-008 completed (compositing skeleton + localized output artifacts)
- ✅ WI-009 completed (single-call vertical slice orchestration path)

### Exit Status
- **Sprint 2 Gate:** Partially met
- **Phase A Overall:** Functionally on track, operationally under-prepared for release hardening

## 3) Demo Evidence (What was shown)

1. Stage-specific endpoints for ASR/MT/TTS/Compositing are available under `/api/v1/jobs/<id>/run-*`.
2. Vertical slice endpoint `/api/v1/jobs/<id>/run-vertical-slice/` executes staged chain and returns final artifact references.
3. Artifact graph now covers source/normalized/extracted/transcript/translation/synth/delivery/localized output placeholders.

## 4) What Went Well

- Stage contracts from Sprint 1 were successfully consumed by Sprint 2 stage skeletons.
- Idempotent transition mechanics prevented duplicate transition records for repeated keys.
- Team handoff discipline improved via WI completion notes.

## 5) What Did Not Go Well / Gaps

1. **Still no automated tests** for stage endpoints and vertical slice behavior.
2. **No committed migrations** despite multiple model additions.
3. **Placeholder implementations** are still non-production ML stubs.
4. **Security posture is incomplete** (`AllowAny` endpoints remain for pipeline).
5. **No retry/dead-letter operational simulation** for stage failures.

## 6) Must-Fix Action Items Before Sprint 3 Reliability Goals

### A. Engineering Baseline
- Add model migrations for `pipeline` and `translation` changes.
- Add automated test suites:
  - transition legality + idempotency,
  - stage endpoint input validation,
  - vertical slice happy-path and replay behavior.

### B. Reliability Baseline
- Add explicit stage failure simulation tests and replay scenarios.
- Add stage-level retry policy docs and implementation checklist.
- Add dead-letter strategy and manual replay commands.

### C. Security Baseline
- Add authentication + RBAC policy for `/api/v1/pipeline` endpoints.
- Define service-account model for orchestrator calls.

### D. Observability Baseline
- Extend telemetry beyond counts:
  - stage duration metrics,
  - stage error rates,
  - idempotent replay counts,
  - p95 pipeline latency.

## 7) Plan Adjustments

### Original Sprint 3 Focus
- Review + Reliability hardening.

### Adjusted Sprint 3 Focus
- Keep Review + Reliability scope, but enforce a strict prerequisite track:
  1. migrations merged,
  2. minimal test harness in CI,
  3. auth guardrails in place,
  4. stage-level observability KPIs published.

Rationale: without these controls, Sprint 3 changes will increase tech debt and reduce confidence for Phase A sign-off.

## 8) Updated Sprint 3 Entry Criteria

Sprint 3 starts only when:
1. migration set is merged and validated,
2. CI runs pipeline test suite,
3. pipeline endpoint auth policy is active,
4. telemetry dashboard includes stage-level latency/error metrics.

## 9) Risks to Monitor

- Contract drift between placeholder stage output and future real model output.
- Rising complexity from stage orchestration without failure automation.
- Integration debt if frontend/review workflows build on unauthenticated APIs.

## 10) Product Lead Decision

**Decision:** Proceed to Sprint 3 with corrective baseline tasks as hard requirements.

No “production-ready” claim until migrations/tests/security/observability prerequisites are complete.
