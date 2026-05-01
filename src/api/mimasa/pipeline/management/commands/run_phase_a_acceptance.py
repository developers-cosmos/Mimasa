import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from pipeline.qa_acceptance import evaluate_phase_a_acceptance


class Command(BaseCommand):
    help = "Execute WI-014 Phase A acceptance matrix checks and output report"

    def add_arguments(self, parser):
        parser.add_argument("--out", type=str, default="", help="Optional output JSON path")

    def handle(self, *args, **options):
        report = evaluate_phase_a_acceptance()
        report["generated_at"] = timezone.now().isoformat()

        if options["out"]:
            out_path = Path(options["out"])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Acceptance report written to {out_path}"))
        else:
            self.stdout.write(json.dumps(report, indent=2))

        if not report["summary"]["all_passed"]:
            self.stdout.write(self.style.WARNING("Phase A acceptance checks did not fully pass"))
