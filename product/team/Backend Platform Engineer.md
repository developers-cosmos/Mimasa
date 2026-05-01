# Backend Platform Engineer

## Role
Builds control-plane APIs, metadata persistence, and artifact lifecycle plumbing.

## Responsibilities
- Implement project/job/stage/artifact APIs.
- Implement persistent schema for jobs, stages, outputs, and quality reports.
- Manage signed URL generation and access controls.
- Ensure auditability and traceability for each job.

## Inputs Needed
- Contracts/state model from System Architect.
- Model I/O definitions from ML Lead.
- Deployment standards from MLOps & SRE Engineer.

## Outputs Produced
- Versioned API endpoints.
- Reliable metadata store integration.
- Artifact index and secure retrieval APIs.

## Immediate Next Steps
1. Implement `/v1/jobs`, `/v1/stages`, `/v1/artifacts` core APIs.
2. Add schema migrations for stage execution tracking.
3. Integrate signed URL delivery flow.

## Handover To
**Frontend Review Engineer**

## Handover Package
- API specs + examples.
- Auth model and permissions matrix.
- Error handling and retry semantics for UI integration.
