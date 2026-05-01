# Phase A Execution Board (Product Lead Command)

## Objective
Complete Phase A (Audio-first localization MVP) by executing staged work items across the team with strict handoffs and acceptance gates.

## Phase A Exit Criteria (Must all pass)
1. Upload -> ASR -> MT -> TTS -> Compositing pipeline produces downloadable output.
2. Job/state tracking and stage artifacts are persisted and auditable.
3. Reviewer UI supports correction + approve/reject flow.
4. Observability dashboard shows success rate, P95 latency, and cost/min.
5. QA sign-off and Product Lead release approval are documented.

---

## Sprint Plan (4 x 2-week sprints)

## Sprint 1: Contracts + Skeleton

### Work Items
- WI-001: Finalize stage contracts and state machine
- WI-002: Create API/data model skeleton (`jobs`, `stage_executions`, `artifacts`)
- WI-003: Establish orchestration skeleton with idempotent transitions
- WI-004: Stand up telemetry baseline in staging

### Owners
- System Architect (WI-001)
- Backend Platform Engineer (WI-002)
- Workflow Orchestration Engineer (WI-003)
- MLOps & SRE Engineer (WI-004)

### Gate
- Architecture + contract sign-off document produced.

---

## Sprint 2: Vertical Slice

### Work Items
- WI-005: ASR stage integration
- WI-006: MT stage integration
- WI-007: TTS stage integration
- WI-008: Audio compositing + muxing stage integration
- WI-009: End-to-end run on sample dataset with artifacts

### Owners
- ML Lead (WI-005/6/7)
- Workflow Orchestration Engineer (WI-008/9)
- Backend Platform Engineer (artifact persistence)

### Gate
- First E2E output generated for sample dataset with trace IDs.

---

## Sprint 3: Review + Reliability

### Work Items
- WI-010: Reviewer UI (correction + approval)
- WI-011: Retry/dead-letter and replay controls
- WI-012: Signed output delivery + webhook callback
- WI-013: Operational runbooks and alerting

### Owners
- Frontend Review Engineer (WI-010)
- Workflow Orchestration Engineer (WI-011)
- Backend Platform Engineer (WI-012)
- MLOps & SRE Engineer (WI-013)

### Gate
- Failed job replay demo and review workflow demo completed.

---

## Sprint 4: Hardening + Release

### Work Items
- WI-014: QA acceptance matrix execution
- WI-015: Quality scorecards and pass/fail report
- WI-016: SLO validation under staged load
- WI-017: Release readiness review and go/no-go

### Owners
- QA & Annotation Lead (WI-014/15)
- MLOps & SRE Engineer (WI-016)
- Product Lead (WI-017)

### Gate
- QA and Product Lead dual sign-off.

---

## Handoff Rules (Mandatory)

Every handoff must include:
1. What was built (artifacts, links, commit refs)
2. Known limitations
3. Test evidence
4. Rollback/mitigation note
5. Explicit next-owner tasks

No task is "done" without handoff package.

---

## Tracking Template

Use this ticket format for each WI:
- ID:
- Owner:
- Dependencies:
- Deliverables:
- Acceptance Test:
- Handoff To:
- Status:

---

## Product Lead Enforcement Rules

- Scope changes after Sprint 1 require Product Lead + System Architect approval.
- Any missed gate triggers immediate replan (same day).
- Quality gates cannot be waived for launch.

## WI-001 Completion Note

- Status: ✅ Completed by **System Architect**
- Outputs:
  - `product/governance/contracts/state-machine.md`
  - `product/governance/contracts/stage-contracts.md`
  - `product/governance/adrs/ADR-001-state-machine-and-stage-contracts.md`
- Next Handover: Backend Platform Engineer + Workflow Orchestration Engineer

## WI-002 Completion Note

- Status: ✅ Completed by **Backend Platform Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/models.py`
  - `src/api/mimasa/pipeline/serializers.py`
  - `src/api/mimasa/pipeline/views.py`
  - `src/api/mimasa/pipeline/urls.py`
  - `src/api/mimasa/pipeline/admin.py`
  - `src/api/mimasa/mimasa/urls.py` (`/api/v1/jobs`, `/api/v1/jobs/<id>/stages`, `/api/v1/jobs/<id>/artifacts`)
- Next Handover: Frontend Review Engineer

## WI-003 Completion Note

- Status: ✅ Completed by **Workflow Orchestration Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/orchestrator.py`
  - `src/api/mimasa/pipeline/models.py` (`JobTransitionEvent` + idempotency constraint)
  - `src/api/mimasa/pipeline/views.py` (`POST /api/v1/jobs/<id>/transitions`)
  - `src/api/mimasa/pipeline/urls.py` (transition routes)
- Guarantees:
  - legal transition validation via canonical transition map
  - idempotent replay for repeated idempotency keys
- Next Handover: MLOps & SRE Engineer

## WI-004 Completion Note

- Status: ✅ Completed by **MLOps & SRE Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/middleware.py` (request-id propagation)
  - `src/api/mimasa/pipeline/telemetry.py` (structured telemetry logger)
  - `src/api/mimasa/pipeline/telemetry_views.py` (`GET /api/v1/telemetry/summary/`)
  - `src/api/mimasa/mimasa/settings.py` (baseline telemetry logging config)
- Guarantees:
  - every API response includes `X-Request-ID`
  - transition events emit structured telemetry logs
  - staging summary endpoint exposes baseline counts for jobs/stages/transitions
- Next Handover: Sprint 2 owners (ML Lead + Workflow Orchestration Engineer)

## Sprint 1 Review Adjustments

- Sprint 1 gate passed with WI-001..WI-004 complete.
- Sprint 2 must include quality-baseline tasks in addition to vertical slice work:
  - commit migrations for `pipeline` models
  - add unit/integration tests for orchestration + APIs
  - define auth guardrails for `/api/v1/*`
  - publish telemetry KPI dashboard spec
- Review artifact: `product/team/sprint-1-review.md`

## WI-005 Completion Note

- Status: ✅ Completed by **ML Lead**
- Outputs:
  - `src/api/mimasa/pipeline/stages/asr.py` (ASR stage integration skeleton)
  - `src/api/mimasa/pipeline/views.py` (`POST /api/v1/jobs/<id>/run-asr/`)
  - `src/api/mimasa/pipeline/models.py` (speaker segments artifact type)
- Guarantees:
  - ASR run requires `EXTRACTED_AUDIO` artifact
  - transition to `ASR_DONE` uses idempotent orchestration path
  - transcript + speaker-segment artifacts are persisted
- Next Handover: Workflow Orchestration Engineer

## WI-006 Completion Note

- Status: ✅ Completed by **ML Lead**
- Outputs:
  - `src/api/mimasa/pipeline/stages/mt.py` (MT stage integration skeleton)
  - `src/api/mimasa/pipeline/views.py` (`POST /api/v1/jobs/<id>/run-mt/`)
  - `src/api/mimasa/pipeline/serializers.py` (`MTStageRunRequestSerializer`)
- Guarantees:
  - MT run requires `TRANSCRIPT_V1` artifact
  - translation artifacts are persisted as `TRANSLATION_V1`
  - transition to `MT_DONE` uses idempotent orchestration path
- Next Handover: Workflow Orchestration Engineer

## WI-007 Completion Note

- Status: ✅ Completed by **ML Lead**
- Outputs:
  - `src/api/mimasa/pipeline/stages/tts.py` (TTS stage integration skeleton)
  - `src/api/mimasa/pipeline/views.py` (`POST /api/v1/jobs/<id>/run-tts/`)
  - `src/api/mimasa/pipeline/serializers.py` (`TTSStageRunRequestSerializer`)
- Guarantees:
  - TTS run requires `TRANSLATION_V1` artifact
  - synthesized voice artifacts are persisted as `SYNTH_VOICE_V1`
  - transition to `TTS_DONE` uses idempotent orchestration path
- Next Handover: Workflow Orchestration Engineer

## WI-008 Completion Note

- Status: ✅ Completed by **Workflow Orchestration Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/stages/compositing.py` (compositing + muxing skeleton)
  - `src/api/mimasa/pipeline/views.py` (`POST /api/v1/jobs/<id>/run-compositing/`)
  - `src/api/mimasa/pipeline/serializers.py` (`CompositingStageRunRequestSerializer`)
- Guarantees:
  - compositing requires synthesized voice + normalized/source video artifacts
  - localized video and delivery audio artifacts are persisted
  - transition to `RENDERED` uses idempotent orchestration path
- Next Handover: Backend Platform Engineer

## WI-009 Completion Note

- Status: ✅ Completed by **Workflow Orchestration Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/stages/vertical_slice.py` (Sprint 2 vertical slice runner)
  - `src/api/mimasa/pipeline/views.py` (`POST /api/v1/jobs/<id>/run-vertical-slice/`)
  - `src/api/mimasa/pipeline/serializers.py` (`VerticalSliceRunRequestSerializer`)
- Guarantees:
  - bootstraps preprocessing artifacts for sample runs
  - executes ASR -> MT -> TTS -> Compositing in one orchestration call
  - returns artifact references for end-to-end demo output
- Next Handover: Frontend Review Engineer

## Sprint 2 Review Adjustments

- Sprint 2 delivered WI-005..WI-009 functional vertical slice.
- Sprint 3 must prioritize hardening prerequisites before reliability stories:
  - commit and validate model migrations
  - add automated pipeline test suite in CI
  - enforce auth/RBAC for `/api/v1/*` pipeline endpoints
  - add stage-level telemetry KPIs (duration/error/replay)
- Review artifact: `product/team/sprint-2-review.md`

## WI-010 Completion Note

- Status: ✅ Completed by **Frontend Review Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/review_views.py` (review dashboard + decision APIs)
  - `src/api/mimasa/pipeline/templates/pipeline/review_dashboard.html`
  - `src/api/mimasa/pipeline/templates/pipeline/review_job.html`
  - `src/api/mimasa/pipeline/models.py` (`ReviewDecision` audit model)
- Guarantees:
  - reviewer UI can inspect artifacts and submit approve/reject decisions
  - review decisions are persisted and auditable
  - job status transitions to QA_PASSED/QA_FAILED via idempotent transition path
- Next Handover: Workflow Orchestration Engineer


## WI-010 Refinement (this commit)

- Added persisted review corrections (`ReviewCorrection`) for transcript/translation segments.
- Added authenticated corrections API: `GET/POST /api/v1/jobs/<id>/review-corrections/`.
- Strengthened reviewer endpoints/UI to require authenticated access.
- Updated review job UI with correction capture and correction history in addition to approve/reject decisions.
- Added initial `pipeline` migrations package for model bootstrap.


## WI-011 Completion Note

- Status: ✅ Completed by **Workflow Orchestration Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/retry_controls.py` (retry/dead-letter/replay services)
  - `src/api/mimasa/pipeline/views.py` (`/retry`, `/replay`, `/dead-letters` endpoints + failure capture)
  - `src/api/mimasa/pipeline/models.py` (`DeadLetterEvent`)
  - `src/api/mimasa/pipeline/orchestrator.py` (FAILED_FATAL replay transition allowances)
  - `src/api/mimasa/pipeline/migrations/0002_deadletterevent.py`
- Guarantees:
  - stage failures create auditable dead-letter events with retry metadata
  - operator can retry latest open dead-letter or replay a specific dead-letter event
  - repeated stage failures escalate to `FAILED_FATAL` after max attempts
- Next Handover: Backend Platform Engineer (WI-012)


## WI-012 Completion Note

- Status: ✅ Completed by **Backend Platform Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/delivery.py` (signed delivery creation, token validation, webhook dispatch)
  - `src/api/mimasa/pipeline/views.py` (`/deliver`, `/deliveries`, tokenized `/download` endpoints)
  - `src/api/mimasa/pipeline/models.py` (`DeliveryRecord`)
  - `src/api/mimasa/pipeline/serializers.py` (delivery request/response serializers)
  - `src/api/mimasa/pipeline/migrations/0003_deliveryrecord.py`
- Guarantees:
  - localized output delivery links are tokenized with expiration
  - delivery lifecycle transitions through `DELIVERING` to `DELIVERED`
  - webhook callbacks are emitted with delivery payload and status tracking
- Next Handover: MLOps & SRE Engineer (WI-013)


## WI-013 Completion Note

- Status: ✅ Completed by **MLOps & SRE Engineer**
- Outputs:
  - `src/api/mimasa/pipeline/alerting.py` (SLO checks and trigger evaluation)
  - `src/api/mimasa/pipeline/alerting_views.py` (`GET /api/v1/telemetry/alerts/`)
  - `src/api/mimasa/mimasa/settings.py` (alert threshold env config)
  - `product/operations/incident-runbook.md`
  - `product/operations/alert-policy.md`
- Guarantees:
  - alert checks evaluate failure rate, stage P95 latency, dead-letter backlog, and webhook failure rate
  - threshold values are environment configurable
  - runbook and escalation path are documented for sprint operations
- Next Handover: QA & Annotation Lead (WI-014)


## WI-013 Refinement (this commit)

- Added persisted alert lifecycle tracking (`AlertEvent`) with OPEN/RESOLVED states.
- Added `check_pipeline_alerts` management command for scheduled alert evaluation + sync.
- Added alert events API endpoint: `GET /api/v1/telemetry/alert-events/`.
- Added alerting tests in `src/api/mimasa/pipeline/tests.py` for triggering, persistence sync, and alerts endpoint behavior.


## Sprint 3 Review Adjustments

- Sprint 3 delivered WI-010..WI-013, including review/replay/delivery/alerting foundations.
- Sprint 4 must enforce release hardening prerequisites before go/no-go stories:
  - enforce auth/RBAC across all pipeline endpoints
  - execute full CI/staging test suite with migrations applied
  - wire alert escalations to human on-call channel (not dashboard-only)
  - validate delivery token expiry/revocation and webhook failure/retry behaviors
- Review artifact: `product/team/sprint-3-review.md`


## WI-014 Completion Note

- Status: ✅ Completed by **QA & Annotation Lead**
- Outputs:
  - `product/qa/phase-a-acceptance-matrix.md`
  - `product/qa/weekly-qa-report-sprint4-week1.md`
  - `src/api/mimasa/pipeline/qa_acceptance.py` (automated acceptance checks)
  - `src/api/mimasa/pipeline/management/commands/run_phase_a_acceptance.py`
  - `src/api/mimasa/pipeline/tests.py` (acceptance report tests)
- Guarantees:
  - acceptance matrix defined across language/scenario/quality dimensions
  - objective KPI checks can be executed and exported as JSON report
  - Sprint 4 QA reporting template established for WI-015 scorecards
- Next Handover: QA & Annotation Lead (WI-015 quality scorecards)


## WI-015 Completion Note

- Status: ✅ Completed by **QA & Annotation Lead**
- Outputs:
  - `product/qa/wi-015-quality-scorecards.md`
  - `src/api/mimasa/pipeline/qa_scorecard.py`
  - `src/api/mimasa/pipeline/management/commands/run_phase_a_scorecard.py`
- Guarantees:
  - acceptance KPIs are transformed into graded scorecards
  - deterministic PASS/FAIL recommendation is generated
- Next Handover: MLOps & SRE Engineer (WI-016)


## WI-016 Completion Note

- Status: ✅ Completed by **MLOps & SRE Engineer**
- Outputs:
  - `product/operations/wi-016-slo-validation.md`
  - `src/api/mimasa/pipeline/slo_validation.py`
  - `src/api/mimasa/pipeline/management/commands/validate_phase_a_slos.py`
- Guarantees:
  - SLO validation produces explicit violation lists
  - pass/fail status is computed from threshold violations
- Next Handover: Product Lead (WI-017)


## WI-017 Completion Note

- Status: ✅ Completed by **Product Lead**
- Outputs:
  - `product/operations/wi-017-release-readiness.md`
  - `src/api/mimasa/pipeline/release_readiness.py`
  - `src/api/mimasa/pipeline/management/commands/release_readiness_phase_a.py`
- Guarantees:
  - release readiness decision is deterministic (`GO`/`NO_GO`)
  - blockers are explicitly listed for remediation tracking
- Next Handover: Phase A closeout review
