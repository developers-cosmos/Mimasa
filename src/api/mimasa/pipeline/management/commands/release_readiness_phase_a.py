import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from pipeline.release_readiness import build_release_readiness_report


class Command(BaseCommand):
    help = "Generate WI-017 release readiness go/no-go report for Phase A"

    def add_arguments(self, parser):
        parser.add_argument("--out", type=str, default="", help="Optional output JSON path")

    def handle(self, *args, **options):
        payload = build_release_readiness_report()
        payload["generated_at"] = timezone.now().isoformat()

        if options["out"]:
            out_path = Path(options["out"])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Release readiness report written to {out_path}"))
        else:
            self.stdout.write(json.dumps(payload, indent=2))

        if payload["go_no_go"] != "GO":
            self.stdout.write(self.style.WARNING("Phase A release decision is NO_GO"))
