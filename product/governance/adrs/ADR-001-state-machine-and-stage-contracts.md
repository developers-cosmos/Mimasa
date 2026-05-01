# ADR-001: Adopt Canonical State Machine and Stage Contracts for Phase A

- **Status:** Accepted
- **Date:** 2026-04-26
- **Owner Role:** System Architect
- **Related WI:** WI-001

## Context

Phase A requires multiple teams to implement interconnected capabilities. Without a canonical lifecycle and contract standard, teams will produce incompatible interfaces and non-deterministic behavior.

## Decision

1. Adopt `product/governance/contracts/state-machine.md` as the only valid Phase A lifecycle model.
2. Adopt `product/governance/contracts/stage-contracts.md` as the required stage interface standard.
3. Any deviation requires a new ADR and Product Lead + System Architect approval.

## Consequences

### Positive
- Predictable cross-team integration.
- Strong auditability and traceability.
- Faster onboarding and lower coordination overhead.

### Negative
- Upfront design discipline required before coding.
- Contract migrations require governance.

## Follow-up Actions

- Backend Platform Engineer: map DB/API schema to contract envelopes.
- Workflow Orchestration Engineer: enforce transition legality.
- ML Lead: adapt model services to stage contracts.
