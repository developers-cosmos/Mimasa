# Mimasa Workshop Research: Business Problem, Product Direction, and Technical Strategy

## 1) Executive Summary

Mimasa’s stated goal is highly ambitious: **translate spoken language in a source video into a target language while preserving speaker identity, timing, facial expression, and lip synchronization**. That is not a single-model feature; it is a **multi-stage media intelligence platform** requiring robust orchestration, quality gates, and explicit trade-offs between quality, latency, and cost.

The current codebase demonstrates useful prototypes (face detection, audio separation, task execution, and basic Django workflow), but it does **not yet solve** the core business outcome end-to-end.

This research proposes:

1. A clear product definition and scope for what “success” means.
2. A reference architecture that can actually deliver business value in phases.
3. A practical tech stack (replace/supplement current prototype stack where necessary).
4. An implementation roadmap with measurable quality/latency/cost targets.

---

## 2) Business Problem Definition

### 2.1 Problem Statement

Creators, educators, media teams, and enterprises need to localize video content into multiple languages **without re-recording everything manually**. Existing subtitle-only localization is often insufficient for engagement and accessibility. The desired value is:

- native-language spoken output,
- natural timing,
- believable mouth movement and expression continuity,
- rapid turnaround,
- scalable multi-language processing.

### 2.2 Outcome Definition (What users actually buy)

Users are not buying “models” — they are buying:

- Faster localization cycle time,
- Lower per-minute localization cost,
- Higher viewer retention and trust in dubbed content,
- Operational reliability (predictable runs, retries, auditability).

### 2.3 Primary User Segments

1. **Content creators / agencies**: want quick turn-around and easy UX.
2. **EdTech / corporate training teams**: need quality and compliance.
3. **Media localization teams**: need batch throughput and review workflows.
4. **Enterprise internal comms**: need security, governance, and on-prem options.

### 2.4 Success Metrics (Business + Technical)

- **Turnaround time**: minutes of wall-clock per minute of source video.
- **Localization cost**: compute + human review minutes per localized minute.
- **Quality acceptance rate**: % videos accepted with no manual fix.
- **A/V sync quality**: lip-sync offset and subjective MOS.
- **Reliability**: job success rate, retry rate, MTTR.

---

## 3) What the Current Repository Solves vs. Doesn’t Solve

## 3.1 What Exists Today (strengths)

- Modular components for:
  - face detection,
  - audio extraction/separation,
  - async task orchestration prototypes,
  - Django/Celery integration.
- A basic web/API workflow around upload, task status, and download.
- Initial production-hardening direction (env-driven settings, async workers).

## 3.2 Core Gaps (blocking business value)

1. **No true speech translation pipeline**
   - No robust ASR → MT → TTS production chain integrated with time alignment.
2. **No high-fidelity lip-sync / facial reenactment stage**
   - Face detection rectangles are not equivalent to mouth reanimation.
3. **No quality control layer**
   - Missing objective gating and human-in-the-loop review tooling.
4. **No media timeline orchestration**
   - Need segment-level timecodes, speaker turns, voice identity mapping.
5. **No hardened MLOps lifecycle**
   - Model registry, versioning, drift monitoring, A/B quality evaluation.
6. **No enterprise-grade data/security controls**
   - PII handling, retention policy, and content governance not formalized.

### 3.3 Product Reality Check

Today’s implementation is best classified as a **foundation prototype**. It is not yet a production solution for “translated voice + synced lips + retained expressions.”

---

## 4) System Design for the Real Problem

## 4.1 Required End-to-End Pipeline

1. **Ingestion**
   - Upload video/audio, detect format, normalize codecs.
2. **Diarization + ASR**
   - Detect speakers and generate timestamped transcript segments.
3. **Translation + Adaptation**
   - Translate text with context retention, optionally style-aware rewrites.
4. **Voice Synthesis (TTS / voice conversion)**
   - Generate target-language speech preserving speaker identity constraints.
5. **Timing Alignment**
   - Stretch/compress generated speech to match shot timing boundaries.
6. **Lip-Sync / Facial Reenactment**
   - Conditioned generation to match target audio visemes and facial dynamics.
7. **Compositing + Rendering**
   - Combine synthesized speech with original music/ambience.
8. **Quality Evaluation**
   - Automated checks + optional human review queue.
9. **Delivery**
   - Signed URLs, webhooks, audit logs, and downloadable artifacts.

## 4.2 Domain Model

- Project
- Asset (source media)
- Job
- Segment (timecoded unit)
- SpeakerProfile
- TranscriptVersion
- TranslationVersion
- AudioRender
- VideoRender
- QualityReport
- ReviewDecision

This gives traceability and version control for each stage.

## 4.3 Orchestration Strategy

Use a DAG-style pipeline (task graph), not ad-hoc calls.

- Celery can work for background tasks, but complex pipelines benefit from workflow engines (e.g., Temporal/Prefect/Argo) to provide:
  - deterministic retries,
  - step-level observability,
  - compensation semantics,
  - long-running workflow state.

---

## 5) Technology Stack Recommendations

## 5.1 Backend / API Layer

- Keep Django for admin/review workflows OR shift to FastAPI for high-throughput API layer.
- For this project:
  - **FastAPI** for media job APIs,
  - **Django admin** (optional) for internal moderation/review.

## 5.2 Queue + Workflow

- Short term: Celery + Redis (already partially present).
- Medium/long term: Temporal (or Argo/Prefect) for robust workflow orchestration.

## 5.3 Data Stores

- PostgreSQL: system-of-record metadata.
- Object store (S3-compatible): raw/processed media artifacts.
- Redis: queue/cache.
- Optional vector store for translation memory / glossary retrieval.

## 5.4 Media + ML Runtime

- FFmpeg for deterministic media transforms.
- PyTorch-based inference services, containerized with GPU support.
- Model serving per stage (ASR, MT, TTS, lip-sync), ideally isolated microservices.

## 5.5 Observability

- OpenTelemetry traces across pipeline stages.
- Prometheus + Grafana metrics dashboards.
- Structured logs (JSON) + centralized log aggregation.

## 5.6 Security & Compliance

- Signed URLs + short-lived access tokens.
- Encryption at rest/in transit.
- Data retention policy and delete workflows.
- Tenant isolation if B2B multi-tenant.

---

## 6) Product Strategy: Phase-by-Phase Delivery

## Phase 0: Foundation Hardening (2–4 weeks)

- Standardize data model for jobs/stages/artifacts.
- Introduce deterministic media preprocessing.
- Build job state machine + consistent retry semantics.
- Add metrics and tracing from day 1.

**Exit criteria:** Reliable ingestion and repeatable stage outputs.

## Phase 1: “Pragmatic Localization MVP” (4–8 weeks)

- ASR + MT + TTS output with good subtitle/audio alignment.
- Original video preserved (no facial reenactment yet).
- Human review UI for transcript and translated text fixes.

**Exit criteria:** Business value via scalable dubbed audio + subtitles.

## Phase 2: Visual Sync Beta (8–16 weeks)

- Introduce lip-sync stage for frontal clear-face shots.
- Add shot-level fallback policy where lip-sync confidence is low.
- Per-language quality baseline and automatic rejection thresholds.

**Exit criteria:** measurable improvement in perceived sync quality.

## Phase 3: Production-Grade Multi-Speaker (ongoing)

- Speaker identity preservation, glossary/brand voice controls.
- Enterprise features: SSO, audit, tenant controls, quota/billing.
- Continuous model quality monitoring and A/B testing.

**Exit criteria:** enterprise adoption readiness.

---

## 7) Architecture Blueprint (Target)

- **API Gateway**: auth, rate limits, project/job APIs.
- **Job Orchestrator**: manages DAG transitions.
- **Stage Workers**:
  - media normalize worker,
  - ASR/diarization worker,
  - MT worker,
  - TTS worker,
  - lip-sync worker,
  - compositor worker,
  - QA scorer worker.
- **Storage**:
  - object storage for media,
  - postgres for metadata,
  - redis for queue/cache.
- **Review Console**:
  - transcript correction,
  - translation override,
  - final approval.

---

## 8) Non-Functional Requirements (Must-Haves)

1. **Scalability**: batch and burst support.
2. **Reliability**: idempotent tasks; crash-safe resume.
3. **Traceability**: reproducible outputs with model/version stamps.
4. **Latency controls**: SLA tiers (fast vs high-quality).
5. **Cost controls**: per-stage budgeting and fallback profiles.
6. **Quality governance**: automatic confidence and manual override.

---

## 9) Risk Analysis

### Technical Risks

- Lip-sync quality degrades on profile views, occlusion, low light.
- Target language prosody differs from source timing.
- Multi-speaker overlap and crosstalk break diarization.

### Product Risks

- Overpromising fully “perfect” realism too early.
- High infra cost before PMF if no staged rollout.

### Mitigations

- Define explicit supported scenarios for each release.
- Add confidence-based fallback (subtitle/audio-only when needed).
- Keep human review options for low-confidence segments.

---

## 10) Recommended “Bring-Up” Tech Stack

## Control Plane

- FastAPI (public API), Django Admin (internal ops), PostgreSQL, Redis, S3.

## Workflow

- Celery now; migrate to Temporal as complexity grows.

## Media/ML

- FFmpeg pipelines, PyTorch inference services in separate GPU-enabled containers.

## Infrastructure

- Kubernetes (or ECS) for autoscaling workers.
- CI/CD with model + service version pinning.

## DevEx

- Monorepo with service boundaries.
- Typed contracts for stage artifacts.
- Smoke tests on short sample clips in CI.

---

## 11) Suggested Immediate Next Actions for This Repository

1. Create a **formal pipeline spec** (`pipeline.yaml`) with stage contracts.
2. Introduce a **Job + StageExecution** schema and explicit state machine.
3. Replace direct in-model pipeline execution with orchestrated workers.
4. Implement a first true MVP path: **ASR + MT + TTS + composite**, even without lip-sync.
5. Add evaluation harness:
   - timing drift,
   - intelligibility score proxy,
   - manual review queue.
6. Build a demo dataset and deterministic benchmark scripts.

---

## 12) Definition of “Core Business Problem Solved”

Mimasa should be considered to have solved the core problem when:

1. A user uploads video and target language,
2. Receives translated output with acceptable speech naturalness,
3. Lip-sync quality meets agreed thresholds on supported scenarios,
4. System processes reliably at defined SLA/cost,
5. Quality is measurable, auditable, and improvable over time.

Until these conditions are met, changes should be framed as infrastructure/prototype progress, not end-state completion.

---

## 13) Final Recommendation

Do **not** attempt to jump directly to full “perfect multilingual lip-synced translation” in one sprint. Build a staged product:

- First monetize reliable localized audio + subtitles,
- Then layer visual sync on top with confidence-based fallback,
- Keep human-in-the-loop quality controls,
- Instrument everything for evidence-driven iteration.

This path is the highest-probability route to real business value.
