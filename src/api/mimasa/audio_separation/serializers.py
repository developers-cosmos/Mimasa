from rest_framework import serializers


class AudioSeparationSerializer(serializers.Serializer):
    # run_in_background = serializers.BooleanField(default=False)

    # class Meta:
    #     model = AudioSeparationModel
    #     fields = '__all__'

    audio_filepath = serializers.CharField()
    destination_folder = serializers.CharField()
    run_in_background = serializers.BooleanField(default=False)


class TaskIdSerializer(serializers.Serializer):
    task_id = serializers.CharField()
