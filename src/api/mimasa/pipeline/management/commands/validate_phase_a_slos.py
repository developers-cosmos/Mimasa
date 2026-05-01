import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from pipeline.slo_validation import validate_phase_a_slos


class Command(BaseCommand):
    help = "Execute WI-016 SLO validation for Phase A"

    def add_arguments(self, parser):
        parser.add_argument("--out", type=str, default="", help="Optional output JSON path")

    def handle(self, *args, **options):
        payload = validate_phase_a_slos()
        payload["generated_at"] = timezone.now().isoformat()

        if options["out"]:
            out_path = Path(options["out"])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"SLO validation report written to {out_path}"))
        else:
            self.stdout.write(json.dumps(payload, indent=2))

        if not payload["passed"]:
            self.stdout.write(self.style.WARNING("Phase A SLO validation failed"))
