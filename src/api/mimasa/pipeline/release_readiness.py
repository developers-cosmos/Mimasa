from pipeline.qa_scorecard import build_quality_scorecard
from pipeline.slo_validation import validate_phase_a_slos


def build_release_readiness_report():
    quality = build_quality_scorecard()
    slo = validate_phase_a_slos()

    blockers = []
    if quality["recommendation"] != "PASS":
        blockers.append("Quality scorecard recommendation is FAIL")
    if not slo["passed"]:
        blockers.append("SLO validation has active violations")

    return {
        "go_no_go": "GO" if not blockers else "NO_GO",
        "blockers": blockers,
        "quality": quality,
        "slo": slo,
    }
