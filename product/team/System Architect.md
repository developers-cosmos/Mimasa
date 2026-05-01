# System Architect

## Role
Converts product goals into implementable architecture and technical contracts.

## Responsibilities
- Define canonical pipeline architecture and service boundaries.
- Author stage contracts (inputs/outputs/errors/idempotency).
- Decide core tech choices and ADRs.
- Enforce design consistency across API, workflow, and ML services.

## Inputs Needed
- Product Lead’s acceptance criteria.
- ML feasibility constraints from ML Lead.
- Operational constraints from MLOps & SRE Engineer.

## Outputs Produced
- Approved architecture diagrams and ADR set.
- Stage contract specs and state machine definitions.
- Integration plan for backend/workflow/ML teams.

## Immediate Next Steps
1. Finalize ADR-001..ADR-005 (orchestration, contracts, storage, observability, fallback policy).
2. Publish stage-level interface contract docs.
3. Run architecture sign-off with all role owners.

## Handover To
**Backend Platform Engineer** and **Workflow Orchestration Engineer**

## Handover Package
- Signed architecture docs.
- Stage execution state model.
- Interface contract test checklist.
