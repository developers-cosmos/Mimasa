# Phase A Team Plan (Owner: Product Lead)

## Mission for Phase A

Deliver the **audio-first localization MVP** from `product/strategy/implementation-plan.md` and `product/strategy/architecture.md`:

1. upload video,
2. run ASR -> MT -> TTS -> compositing,
3. generate downloadable localized output,
4. enforce quality gates + human review,
5. ship a reliable and observable pipeline.

## Team Members (Named by Role)

1. Product Lead
2. System Architect
3. ML Lead
4. Backend Platform Engineer
5. Workflow Orchestration Engineer
6. Frontend Review Engineer
7. MLOps & SRE Engineer
8. QA & Annotation Lead

## Phase A Delivery Ownership

- **Product Lead**: scope, priorities, acceptance criteria, release decisions.
- **System Architect**: architecture decisions, interface contracts, technical governance.
- **ML Lead**: ASR/MT/TTS model strategy and quality thresholds.
- **Backend Platform Engineer**: APIs, data model, job metadata, artifact lifecycle.
- **Workflow Orchestration Engineer**: DAG/state machine, retries, idempotency.
- **Frontend Review Engineer**: review UI and operator workflows.
- **MLOps & SRE Engineer**: deployment, observability, cost/latency SLOs.
- **QA & Annotation Lead**: quality framework, test sets, acceptance reports.

## Phase A Milestones (8-week cadence)

### Weeks 1-2: Contracts + Foundations
- Finalize stage contracts and state machine.
- Establish base schemas and artifact conventions.
- Build dev/staging environments and telemetry baseline.

### Weeks 3-4: Pipeline Vertical Slice
- Deliver end-to-end happy path on sample dataset.
- Produce first localized outputs and baseline quality report.

### Weeks 5-6: Review + Reliability
- Add human review queue and correction workflow.
- Add retries, dead-letter handling, and operational runbooks.

### Weeks 7-8: Hardening + Release
- Run acceptance tests across target languages/scenarios.
- Publish Phase A readiness report and go/no-go decision.

## Handoff Chain (Critical Path)

1. Product Lead -> System Architect
2. System Architect -> Backend Platform Engineer + Workflow Orchestration Engineer
3. ML Lead -> Workflow Orchestration Engineer + Backend Platform Engineer
4. Backend Platform Engineer -> Frontend Review Engineer
5. Workflow Orchestration Engineer -> MLOps & SRE Engineer
6. QA & Annotation Lead -> Product Lead (acceptance recommendation)

## Definition of Done for Phase A

- End-to-end ASR/MT/TTS/compositor pipeline operational.
- Job state machine and artifact traceability complete.
- Reviewer UI usable for corrections and approvals.
- SLO dashboard live (success rate, latency, cost/min).
- Product Lead sign-off with QA recommendation.

## Working Agreements

- Daily 15-min sync.
- Twice-weekly architecture/design reviews.
- Weekly demo with measurable progress against milestones.
- Every handoff must include: artifacts, checklist, known risks, rollback plan.
