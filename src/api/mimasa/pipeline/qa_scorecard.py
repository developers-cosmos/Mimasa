from dataclasses import dataclass, asdict

from .qa_acceptance import evaluate_phase_a_acceptance


@dataclass(frozen=True)
class ScorecardGrade:
    key: str
    value: float
    threshold: float
    grade: str


def _grade(value: float, threshold: float) -> str:
    if threshold <= 0:
        return "N/A"
    ratio = value / threshold
    if ratio >= 1.15:
        return "A"
    if ratio >= 1.0:
        return "B"
    if ratio >= 0.85:
        return "C"
    return "F"


def build_quality_scorecard():
    acceptance = evaluate_phase_a_acceptance()
    grades = []
    for check in acceptance["checks"]:
        grades.append(
            ScorecardGrade(
                key=check["key"],
                value=float(check["value"]),
                threshold=float(check["threshold"]),
                grade=_grade(float(check["value"]), float(check["threshold"])),
            )
        )

    fail_count = sum(1 for check in acceptance["checks"] if not check["passed"])
    recommendation = "PASS" if fail_count == 0 else "FAIL"

    return {
        "recommendation": recommendation,
        "failed_checks": fail_count,
        "scorecard": [asdict(item) for item in grades],
        "acceptance": acceptance,
    }
