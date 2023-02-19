from rest_framework import serializers


class FaceDetectionSerializer(serializers.Serializer):
    video_filepath = serializers.CharField()
    destination_folder = serializers.CharField()
    run_in_background = serializers.BooleanField(default=False)
    async_enabled = serializers.BooleanField(default=False)
    async_type = serializers.ChoiceField(
        choices=[
            ("AsyncTaskFaceDetector", "AsyncTaskFaceDetector"),
            ("ConcurrentFuturesFaceDetector", "ConcurrentFuturesFaceDetector"),
            ("AsyncIOAndCPUFaceDetector", "AsyncIOAndCPUFaceDetector"),
        ],
        default="AsyncTaskFaceDetector",
        required=False,
    )
    detector_type = serializers.ChoiceField(
        choices=[
            ("ViolaJones", "ViolaJones"),
            ("MTCNN", "MTCNN"),
            ("SSD", "SSD"),
            ("YOLO", "YOLO"),
            ("RetinaFace", "RetinaFace"),
        ],
        default="MTCNN",
    )

    def validate(self, data):
        if data.get("async_enabled", False) and not data.get("async_type"):
            raise serializers.ValidationError("The 'async_type' field is required when 'async_enabled' is True.")

        if data["detector_type"] != "MTCNN":
            raise serializers.ValidationError("The selected face detector is not implemented.")

        if data.get("run_in_background", False) and data["async_type"] != "AsyncTaskFaceDetector":
            raise serializers.ValidationError(
                "The selected async_type is currently not supported to run in background."
            )
        return data


class TaskIdSerializer(serializers.Serializer):
    task_id = serializers.CharField()
