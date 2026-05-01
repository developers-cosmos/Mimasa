# Workflow Orchestration Engineer

## Role
Implements and operates the end-to-end workflow execution engine.

## Responsibilities
- Build job DAG/state machine execution.
- Implement retries, idempotency, timeouts, and dead-letter behavior.
- Coordinate stage dependencies and parallelism constraints.
- Publish stage-level events and status updates.

## Inputs Needed
- State machine and contracts from System Architect.
- Stage executors from ML Lead/backend services.
- Runtime limits from MLOps & SRE Engineer.

## Outputs Produced
- Reliable orchestrated pipeline for Phase A.
- Replay and resume capabilities for failed jobs.
- Workflow telemetry and event streams.

## Immediate Next Steps
1. Implement CREATED->DELIVERED lifecycle with explicit transitions.
2. Add idempotency keys and deterministic retry policy.
3. Build failure simulation tests for stage recovery.

## Handover To
**MLOps & SRE Engineer**

## Handover Package
- Workflow deployment topology.
- Retry/dead-letter policies.
- Operational playbook for incident response.
