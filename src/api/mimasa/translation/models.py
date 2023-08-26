#!/usr/bin/env python3
import asyncio
from django.db import models
from django.core.files import File

from src.common.libraries import Logger, Video
from src.translation.translation import Translation


class MimasaModel(models.Model):
    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("fr", "French"),
        ("de", "German"),
        ("hi", "Hindi"),
    )

    id = models.AutoField(primary_key=True)
    video = models.FileField(upload_to="videos/", default="", blank=True, null=True)
    input_language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, default=("en", "English"))
    output_language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, default=("en", "English"))
    task_status = models.CharField(max_length=100, default="CREATED")
    task_id = models.CharField(max_length=100, default="unknown")

    # output_video_filename = models.FileField(upload_to="output_videos/", default="", blank=True, null=True)
    output_video_filename = models.CharField(max_length=1000, default="output_videos/")
    output_video = models.FileField(upload_to="output_videos/", null=True, blank=True, max_length=200)

    def __str__(self):
        return f"Translation for video {self.video.name} from {self.input_language} to {self.output_language}"

    def translate(self):
        """Method for performing both audio and video translations"""

        main_logger = Logger("MAIN")
        main_logger.add_file_handler("main.log")
        main_logger.info("Initializing Mimasa Application...")
        main_logger.info(
            f"Translation for video {self.video.path} from {self.input_language} to {self.output_language}"
        )
        try:
            video = Video(file_path=self.video.path, language=self.input_language)
            translation_unit = Translation(
                video=video, output_language=self.output_language, input_language=self.input_language
            )
            main_logger.info("Mimasa Application initialized successfully")

            main_logger.info("Translation started...")
            asyncio.run(translation_unit.translate())
            # await translation_unit.translate()
            output_video_filename = translation_unit.get_output_video()
            if output_video_filename:
                self.output_video_filename = output_video_filename
                # TODO: upload output video correctly
                # filename = output_video_filename.split('\\')[-1]
                # print(filename)
                # self.output_video.save(filename, File(open(output_video_filename, 'rb')))
                self.save()
            main_logger.info("Translation finished successfully")
        except:
            main_logger.critical("Translation failed. Shutting down Mimasa application!!")
            raise
