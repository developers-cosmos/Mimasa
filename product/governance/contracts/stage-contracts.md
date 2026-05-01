# WI-001 — Phase A Stage Contract Specification

**Owner Role:** System Architect  
**Status:** Completed  
**Related Work Item:** WI-001 (Finalize stage contracts and state machine)

## 1) Contract Principles

1. Every stage has explicit input/output schemas.
2. All outputs are immutable artifacts with version metadata.
3. Errors are normalized (`error_code`, `error_message`, `retryable`).
4. Every stage call includes correlation metadata (`job_id`, `trace_id`, `stage_execution_id`).

## 2) Shared Envelope

## 2.1 StageInputEnvelope

```json
{
  "job_id": "string",
  "stage_execution_id": "string",
  "trace_id": "string",
  "input_artifact_ids": ["string"],
  "config": {
    "runtime_profile": "fast_preview|balanced|high_quality",
    "language_pair": "en->hi"
  }
}
```

## 2.2 StageOutputEnvelope

```json
{
  "job_id": "string",
  "stage_execution_id": "string",
  "trace_id": "string",
  "status": "SUCCESS|FAILED",
  "output_artifacts": [
    {
      "artifact_id": "string",
      "artifact_type": "string",
      "uri": "s3://...",
      "checksum": "sha256:...",
      "metadata": {}
    }
  ],
  "quality": {
    "confidence": 0.0,
    "signals": {}
  },
  "error": {
    "error_code": "string",
    "error_message": "string",
    "retryable": true
  }
}
```

## 3) Stage Contracts

## 3.1 PREPROCESSING

**Input artifacts:** `SOURCE_VIDEO`  
**Output artifacts:**
- `NORMALIZED_VIDEO`
- `EXTRACTED_AUDIO`

**Primary checks:** codec normalization, frame rate, loudness baseline.

## 3.2 ASR

**Input artifacts:** `EXTRACTED_AUDIO`  
**Output artifacts:**
- `TRANSCRIPT_V1` (timecoded text)
- `SPEAKER_SEGMENTS_V1`

**Primary checks:** transcript completeness and diarization confidence.

## 3.3 MT

**Input artifacts:** `TRANSCRIPT_V1`  
**Output artifacts:**
- `TRANSLATION_V1`

**Primary checks:** language validity and segment alignment consistency.

## 3.4 TTS

**Input artifacts:** `TRANSLATION_V1`, optional `SPEAKER_PROFILE`  
**Output artifacts:**
- `SYNTH_VOICE_V1` (segment-aligned generated speech)

**Primary checks:** duration drift within configured tolerance.

## 3.5 COMPOSITING

**Input artifacts:** `NORMALIZED_VIDEO`, `SYNTH_VOICE_V1`, optional `MUSIC_BED`  
**Output artifacts:**
- `LOCALIZED_VIDEO_V1`
- `DELIVERY_AUDIO_V1`

**Primary checks:** mux validity and A/V sync threshold.

## 3.6 QA_EVAL

**Input artifacts:** `LOCALIZED_VIDEO_V1`, `TRANSCRIPT_V1`, `TRANSLATION_V1`  
**Output artifacts:**
- `QUALITY_REPORT_V1`

**Primary checks:** acceptance policy verdict with explainable reasons.

## 4) Error Code Convention

- `PREP_*` preprocessing errors
- `ASR_*` transcription/diarization errors
- `MT_*` translation errors
- `TTS_*` synthesis errors
- `COMP_*` compositing/render errors
- `QA_*` quality gate errors
- `SYS_*` infra/runtime errors

## 5) Versioning Rules

- Contract changes require ADR + version increment.
- Backward-incompatible change => new major contract version (`v2`).
- Existing jobs remain pinned to the contract version they started with.

## 6) Acceptance Criteria for WI-001

1. All stage owners implement against this contract.
2. Workflow executor rejects payloads that violate envelope schema.
3. DB artifact registry supports `artifact_type`, `checksum`, `uri`, `version`.
4. QA policy consumes standardized quality signals from stage outputs.
