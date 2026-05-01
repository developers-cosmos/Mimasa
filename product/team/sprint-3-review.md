# Sprint 3 Review — Phase A (Review + Reliability)

**Sprint Window:** 2 weeks  
**Review Owner:** Product Lead  
**Date:** 2026-04-27

## 1) Sprint Goal

Deliver the human review and reliability controls required before Sprint 4 release hardening:
- WI-010: reviewer correction + approval workflow
- WI-011: retry/dead-letter and replay controls
- WI-012: signed output delivery + webhook callback
- WI-013: operational runbooks and alerting

## 2) Outcome Summary

### Completed
- ✅ WI-010 completed (review correction persistence + review approval flow)
- ✅ WI-011 completed (dead-letter tracking + retry/replay APIs)
- ✅ WI-012 completed (signed delivery links + webhook callback tracking)
- ✅ WI-013 completed (telemetry alert checks + incident runbook + alert policy)

### Exit Status
- **Sprint 3 Gate:** Met with constraints
- **Phase A Overall:** Ready to enter Sprint 4 hardening, but still not release-ready

## 3) Demo Evidence (What was shown)

1. Reviewer workflow now supports correction capture and decision auditing.
2. Failed stages generate dead-letter entries and can be retried/replayed by operators.
3. Delivery flow now issues tokenized/expiring download links and attempts webhook callbacks.
4. Telemetry alert checks are available via `/api/v1/telemetry/alerts/` with persisted alert-event support.

## 4) What Went Well

- Sprint 3 directly addressed reliability debt from Sprint 2 review.
- API surface now reflects realistic operator workflows (review, replay, delivery, alert checks).
- Operational artifacts (runbook + alert policy) now exist with clear ownership and escalation paths.

## 5) What Did Not Go Well / Gaps

1. **Auth/RBAC still inconsistent**: several pipeline APIs remain `AllowAny` and need hard enforcement by role.
2. **Runtime verification gap**: full Django test execution is blocked in this environment; tests were added but not validated in CI/staging from this workspace.
3. **Alert transport is incomplete**: alerts are computed/persisted, but paging integration (PagerDuty/Slack/Email) is not yet wired.
4. **Model stages are placeholders**: business-critical quality still depends on replacing skeleton stage logic with real model-backed inference services.

## 6) Must-Fix Action Items Before Sprint 4 Exit

### A. Release Safety
- Enforce auth/RBAC for all pipeline endpoints (`reviewer`, `operator`, `service`).
- Add endpoint-level permission tests and negative authorization tests.

### B. Quality Assurance
- Execute full test suite in CI/staging with migrations applied.
- Add integration tests for:
  - review->rework loop,
  - dead-letter retry/replay,
  - delivery token expiry and webhook error handling,
  - alert persistence open/resolved lifecycle.

### C. Operational Hardening
- Add outbound notifier integration for critical alerts.
- Publish SLO dashboard links with threshold ownership and escalation mapping.

### D. Delivery Confidence
- Add signed URL key-rotation policy and explicit token revocation workflow.
- Add webhook retry backoff policy and dead-letter queue for callback failures.

## 7) Plan Adjustments

### Original Sprint 4 Focus
- QA matrix, quality scorecards, SLO validation, release readiness.

### Adjusted Sprint 4 Focus
- Keep original scope, but add hard entry controls:
  1. auth/RBAC enforcement merged,
  2. CI green on pipeline test suite,
  3. alert notifier integration in place,
  4. delivery security policy documented and validated.

Rationale: Sprint 3 delivered operational primitives; Sprint 4 must prove production readiness, not add new platform features.

## 8) Updated Sprint 4 Entry Criteria

Sprint 4 starts only when:
1. permission policy is active on all pipeline endpoints,
2. migrations apply cleanly in staging and CI tests pass,
3. alert escalations route to human on-call channel,
4. delivery token expiry and webhook failure behaviors are tested.

## 9) Risks to Monitor

- Security risk if permissive endpoints remain exposed.
- Reliability risk if alerting stays dashboard-only without escalation transport.
- Quality risk if model placeholders are mistaken for production behavior in demos.

## 10) Product Lead Decision

**Decision:** Proceed to Sprint 4 with strict hardening gates.  
No launch recommendation until Sprint 4 QA + SLO + security criteria are evidenced.
