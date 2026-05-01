# Mimasa Implementation Plan (System-Level)

## 0) Decision Framing

Based on `product/strategy/research.md`, Mimasa is fundamentally a **multistage AI media platform** (ASR + translation + TTS + lip-sync + compositing + quality governance), not a single application feature.

### Language Decision (C++23 vs alternatives)

- **C++23 should NOT be the primary stack** for the full product.
- Why:
  1. Modern speech/translation/lip-sync ecosystem and model tooling are Python-first.
  2. MLOps workflows, model serving libraries, and research iteration speed are much better in Python.
  3. Product delivery risk increases significantly if core ML orchestration is forced into C++.

**Where C++23 is appropriate**:
- Optional performance-critical media kernels (custom FFmpeg filters, realtime codec modules, specific CPU/GPU accelerators).

**Primary recommendation**:
- Python for ML + orchestration services,
- TypeScript for frontend,
- SQL + object storage for system of record/artifacts.

---

## 1) Product Scope & Release Strategy

## 1.1 Problem We Are Solving

Deliver localized video with:
1. translated speech,
2. acceptable timing and naturalness,
3. visual plausibility (lip-sync) where confidence is high,
4. predictable cost, latency, and reliability.

## 1.2 Phased Product Targets

### Phase A — Monetizable MVP (Audio-first localization)

- Upload video
- ASR + MT + TTS
- Mix translated speech with original ambience/music
- Produce translated video with optional subtitles
- Human review queue for transcript/translation edits

**Outcome**: immediate business value without full visual reenactment risk.

### Phase B — Visual Sync Beta

- Add shot/segment-level lip-sync stage
- Confidence gating and fallback to audio-only on low confidence
- Support clear frontal speaking shots first

### Phase C — Production Scale + Enterprise

- Multi-speaker consistency
- Custom glossary/brand voice controls
- Tenant controls, SSO, governance, billing, SLA

---

## 2) Delivery Plan (90/180/365)

## 2.1 First 90 Days

1. **Platform foundations**
   - Unified domain schema for jobs/stages/artifacts
   - Deterministic media preprocessing contracts
   - Async workflow engine with idempotency/retries

2. **Core AI pipeline v1**
   - ASR + diarization
   - MT with glossary hooks
   - TTS with timing alignment
   - audio compositing + muxing

3. **Operational baseline**
   - observability (logs/metrics/traces)
   - signed URL artifact delivery
   - basic review UI and approval workflow

4. **Evaluation harness**
   - stage-level quality scores
   - latency and cost per minute telemetry

### 2.2 180 Days

- Segment-level lip-sync integration
- Confidence thresholds + policy routing
- Active learning loop from reviewer corrections
- Batch scheduling and workload QoS profiles

### 2.3 365 Days

- Enterprise controls (SSO, audit, tenant isolation)
- Multi-region architecture
- Continuous model governance and A/B framework
- Cost optimization with tiered inference paths

---

## 3) Workstream Plan

## Workstream 1: Product & Quality Governance

- Define acceptance thresholds:
  - transcript quality,
  - translation adequacy/fluency,
  - voice naturalness,
  - lip-sync quality,
  - end-to-end acceptance rate.
- Build reviewer workflow and final approval states.

## Workstream 2: Workflow and Data Platform

- Implement explicit state machine:
  - CREATED -> PREPROCESSING -> ASR_DONE -> MT_DONE -> TTS_DONE -> SYNC_DONE -> RENDERED -> QA_PASSED/FAILED -> DELIVERED
- Persist stage artifacts and provenance metadata.

## Workstream 3: AI Inference Services

- Isolate each major model stage as service boundary:
  - asr-service
  - translation-service
  - tts-service
  - lipsync-service
  - compositor-service

## Workstream 4: API + UX

- Project/job APIs with webhook callbacks.
- Review console for transcript and translation edits.
- Delivery dashboard with downloadable/signed artifacts.

## Workstream 5: SRE + Security

- Trace every stage with correlation IDs.
- Policy-based retention/deletion.
- Signed URLs and least-privilege runtime identities.

---

## 4) Backlog Prioritization (Must/Should/Could)

## Must
- Job + StageExecution data model
- Reliable orchestration and retries
- ASR/MT/TTS/compositor happy path
- Artifact versioning and immutable storage
- Quality scoring + review approval state

## Should
- Glossary and terminology controls
- Multi-speaker diarization improvements
- Webhook integrations

## Could
- Real-time streaming mode
- On-device privacy-preserving edge execution
- C++23 optimized modules for specific performance hotspots

---

## 5) Team Topology

- 1 Product lead (localization domain)
- 1 Tech lead/architect
- 2-3 ML engineers
- 2 backend/platform engineers
- 1 frontend engineer
- 1 SRE/DevOps
- 1 QA/annotation operations lead

---

## 6) Risks and Mitigations

1. **Model quality variance by language**
   - Mitigation: language-by-language launch matrix and thresholds.
2. **High GPU cost**
   - Mitigation: tiered inference profiles, caching, batching.
3. **Lip-sync failures**
   - Mitigation: confidence-based fallback to audio-only output.
4. **Complexity drift**
   - Mitigation: strict stage contracts and architecture review cadence.

---

## 7) Exit Criteria by Phase

### Phase A exit
- >95% pipeline completion success
- clear cost/minute and latency baseline
- human approval workflow operational

### Phase B exit
- measurable lip-sync quality gain on supported shot types
- low-confidence fallback policy preventing bad outputs

### Phase C exit
- enterprise readiness checklist complete
- SLO attainment and operational maturity established

---

## 8) What We Will Not Do (Now)

- We will not rewrite the whole platform in C++23.
- We will not promise universal perfect lip-sync in all scenes from day one.
- We will not deploy without observability + quality governance.

---

## 9) Immediate Next Actions (2 weeks)

1. Create canonical schema and state machine docs.
2. Define stage artifact contracts (`jsonschema`/protobuf).
3. Implement minimal workflow runner with idempotency keys.
4. Build ASR->MT->TTS->compositor E2E on fixed sample dataset.
5. Set quality gate dashboard and review queue MVP.
