# Mimasa Target Architecture (Production-Grade)

## 1) Architecture Principles

1. **Pipeline-first**: model stages are explicit services with contracts.
2. **Artifact-driven**: each stage writes immutable versioned outputs.
3. **Quality-gated**: no output delivered without policy checks.
4. **Fallback-safe**: low-confidence visual sync degrades gracefully to audio-first output.
5. **Observability-native**: tracing/metrics are first-class, not optional.

---

## 2) High-Level System Components

## 2.1 Control Plane

- **API Gateway / BFF** (FastAPI):
  - authentication/authorization,
  - project and job APIs,
  - signed artifact URLs,
  - webhook management.

- **Workflow Orchestrator** (Temporal preferred; Celery transitional):
  - DAG execution,
  - retries/timeouts,
  - compensation/recovery,
  - status propagation.

- **Metadata Store** (PostgreSQL):
  - jobs, stages, speakers, transcripts, translations, outputs, quality reports.

- **Object Storage** (S3-compatible):
  - raw uploads,
  - per-stage artifacts,
  - final rendered outputs.

## 2.2 Data/Inference Plane

- `preprocess-service`
- `asr-diarization-service`
- `translation-service`
- `tts-service`
- `timing-alignment-service`
- `lipsync-service`
- `audio-mix-service`
- `video-compositor-service`
- `quality-eval-service`

Each service is independently deployable and versioned.

## 2.3 Human Review Plane

- **Review Console** (web app):
  - transcript correction,
  - translation editing,
  - confidence visualization,
  - approve/reject decisions.

- **Admin Console**:
  - ops dashboards,
  - failed job diagnostics,
  - policy controls.

---

## 3) Reference Runtime Flow

1. User uploads source video.
2. Ingestion stores source asset and creates Job.
3. Preprocess normalizes media (frame rate, codecs, loudness).
4. ASR+diarization outputs timecoded segments + speaker mapping.
5. Translation service produces target text per segment.
6. TTS generates speaker-conditioned target speech.
7. Timing alignment adjusts synthesized speech to segment durations.
8. Lip-sync service renders visually aligned segments (if confidence threshold passes).
9. Audio mix combines translated voice with preserved ambience/music.
10. Video compositor muxes output streams and renders master artifact.
11. Quality evaluator scores objective metrics and policy checks.
12. If pass => deliver signed URL + webhook; if fail => review queue.

---

## 4) Data Model (Core Tables / Entities)

- `projects`
- `assets`
- `jobs`
- `stage_executions`
- `speakers`
- `segments`
- `transcript_versions`
- `translation_versions`
- `audio_renders`
- `video_renders`
- `quality_reports`
- `review_decisions`
- `webhook_deliveries`

### 4.1 StageExecution Contract

Fields:
- `job_id`, `stage_name`, `status`, `attempt`, `started_at`, `ended_at`
- `input_artifact_ids[]`, `output_artifact_ids[]`
- `model_name`, `model_version`, `runtime_profile`
- `error_code`, `error_message`

This contract is mandatory for auditability and reproducibility.

---

## 5) API Surface (Representative)

- `POST /v1/projects`
- `POST /v1/projects/{id}/assets:upload`
- `POST /v1/jobs`
- `GET /v1/jobs/{id}`
- `GET /v1/jobs/{id}/stages`
- `GET /v1/jobs/{id}/artifacts`
- `POST /v1/jobs/{id}/retry`
- `POST /v1/reviews/{id}/approve`
- `POST /v1/reviews/{id}/reject`
- `POST /v1/webhooks`

---

## 6) Recommended Tech Stack

## 6.1 Services

- Python 3.12+ for AI and backend services.
- FastAPI for service endpoints.
- Pydantic for contracts.

## 6.2 Workflow / Queue

- Temporal (preferred) for orchestration.
- Redis/Kafka as supporting infra where needed.
- Celery only as migration bridge if already deeply embedded.

## 6.3 Storage

- PostgreSQL 16+
- S3-compatible object store
- Redis cache

## 6.4 ML Runtime

- PyTorch inference containers
- FFmpeg for media processing
- ONNX/TensorRT optional optimization tracks

## 6.5 Frontend

- Next.js / React + TypeScript
- authenticated review and operations dashboard

## 6.6 Infra

- Kubernetes + autoscaling GPU node pools
- Terraform/IaC
- GitHub Actions + environment promotion pipelines

---

## 7) Security & Compliance Architecture

- OAuth2/OIDC for identity
- RBAC/ABAC for project + artifact access
- Signed URLs (short TTL)
- Encryption in transit and at rest
- Audit events for every review and delivery action
- Data retention/deletion policy engine

---

## 8) Reliability Architecture

- Idempotency keys on job creation and stage reruns
- Dead letter queues and replay tools
- Circuit breakers around model services
- Backpressure and concurrency quotas
- SLO dashboards:
  - job success rate,
  - P95 pipeline latency,
  - cost per minute,
  - QA pass rate.

---

## 9) Performance Strategy

- Batch inference where quality allows.
- Segment parallelization with ordering constraints.
- Cache reusable intermediates (transcripts/embeddings).
- Tiered runtime profiles:
  - `fast_preview`
  - `balanced`
  - `high_quality`

C++23 optimization is allowed only for identified bottlenecks with evidence.

---

## 10) Migration from Current Prototype

1. Freeze current prototype branch as baseline.
2. Introduce new control-plane schema + APIs behind versioned namespace (`/v1`).
3. Wrap current processing modules as transitional stage services.
4. Replace in-model orchestration with workflow engine execution.
5. Add evaluator + review loop before delivery.
6. Incrementally swap prototype ML modules with production-grade services.

---

## 11) ADRs (Architecture Decision Records) to Create Immediately

1. Primary orchestration engine (Temporal vs Celery).
2. Artifact contract format (Pydantic JSON vs protobuf).
3. Lip-sync fallback policy and confidence thresholds.
4. Multi-tenant isolation model.
5. Observability schema and correlation ID strategy.

---

## 12) Target End-State

A resilient localization platform that can produce multilingual outputs with controlled quality and predictable operations, where lip-sync is a confidence-governed stage rather than a brittle always-on assumption.
