# ML Lead

## Role
Owns ASR/MT/TTS model strategy, evaluation standards, and quality gates.

## Responsibilities
- Select and benchmark candidate model stacks for Phase A languages.
- Define quality metrics and thresholds (transcription, translation, naturalness).
- Provide model packaging/versioning strategy.
- Set fallback behavior when model confidence is low.

## Inputs Needed
- Target language/business requirements from Product Lead.
- Runtime constraints from MLOps & SRE Engineer.
- Contract format from System Architect.

## Outputs Produced
- Model shortlist and baseline results.
- Quality threshold definitions for QA policy.
- Inference requirements and resource sizing.

## Immediate Next Steps
1. Build benchmark set for initial 3-4 languages.
2. Publish quality scorecard template.
3. Deliver model I/O adapters matching stage contracts.

## Handover To
**Workflow Orchestration Engineer** and **Backend Platform Engineer**

## Handover Package
- Model endpoints and request/response schema.
- Confidence score semantics.
- Resource profile for deployment.
