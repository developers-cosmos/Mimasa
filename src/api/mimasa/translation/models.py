#!/usr/bin/env python3
import asyncio
import secrets
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import models
from django.utils import timezone

from src.common.libraries import Logger, Video
from src.translation.translation import Translation


class MimasaModel(models.Model):
    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("fr", "French"),
        ("de", "German"),
        ("hi", "Hindi"),
    )

    STATUS_CHOICES = (
        ("CREATED", "Created"),
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILURE", "Failure"),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="translations",
        null=True,
        blank=True,
    )
    video = models.FileField(upload_to="videos/", default="", blank=True, null=True)
    input_language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, default="en")
    output_language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, default="en")
    task_status = models.CharField(max_length=100, choices=STATUS_CHOICES, default="CREATED")
    task_id = models.CharField(max_length=100, default="unknown")

    output_video_filename = models.CharField(max_length=1000, default="output_videos/")
    output_video = models.FileField(upload_to="output_videos/", null=True, blank=True, max_length=200)

    translated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Translation for video {self.video.name} from {self.input_language} to {self.output_language}"

    def _attach_output_video(self, output_video_filename: str):
        output_file = Path(output_video_filename)
        if output_file.exists() and output_file.is_file():
            with output_file.open("rb") as file_obj:
                self.output_video.save(output_file.name, File(file_obj), save=False)

    def translate(self):
        """Perform both audio and video translations and persist output metadata."""
        main_logger = Logger("MAIN")
        main_logger.add_file_handler("main.log")
        main_logger.info("Initializing Mimasa Application...")
        main_logger.info(
            "Translation for video %s from %s to %s",
            self.video.path,
            self.input_language,
            self.output_language,
        )

        if not self.video:
            raise ValueError("No input video has been provided")

        video = Video(file_path=self.video.path, language=self.input_language)
        translation_unit = Translation(video=video, output_language=self.output_language, input_language=self.input_language)

        main_logger.info("Mimasa Application initialized successfully")
        main_logger.info("Translation started...")

        asyncio.run(translation_unit.translate())
        output_video_filename = translation_unit.get_output_video()

        if output_video_filename:
            self.output_video_filename = output_video_filename
            self._attach_output_video(output_video_filename)
            self.translated_at = timezone.now()
            self.save(update_fields=["output_video_filename", "output_video", "translated_at", "updated_at"])

        main_logger.info("Translation finished successfully")
        return output_video_filename


class TranslationNotification(models.Model):
    """Stores translation completion notifications for users."""

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="translation_notifications",
        null=True,
        blank=True,
    )
    translation = models.ForeignKey(MimasaModel, on_delete=models.CASCADE, related_name="notifications")
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    download_token = models.CharField(max_length=64, default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)
