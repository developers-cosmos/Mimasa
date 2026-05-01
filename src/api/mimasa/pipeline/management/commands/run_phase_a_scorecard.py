import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from pipeline.qa_scorecard import build_quality_scorecard


class Command(BaseCommand):
    help = "Generate WI-015 quality scorecard and pass/fail recommendation"

    def add_arguments(self, parser):
        parser.add_argument("--out", type=str, default="", help="Optional output JSON path")

    def handle(self, *args, **options):
        payload = build_quality_scorecard()
        payload["generated_at"] = timezone.now().isoformat()

        if options["out"]:
            out_path = Path(options["out"])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Quality scorecard written to {out_path}"))
        else:
            self.stdout.write(json.dumps(payload, indent=2))

        if payload["recommendation"] == "FAIL":
            self.stdout.write(self.style.WARNING("Phase A quality recommendation is FAIL"))
