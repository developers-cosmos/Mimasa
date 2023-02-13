from .models import AudioSeparationModel
from .services import audio_separation_service
from mimasa.celery import app
from src.common.libraries import Audio
from rest_framework.response import Response


@app.task
def run_audio_separation(pk):
    try:
        separator_instance = AudioSeparationModel.objects.get(id=pk)
        audio = Audio(separator_instance.audio_filepath)
        result = audio_separation_service(audio=audio, destination=separator_instance.destination_folder)
        if isinstance(result, Response):
            separator_instance.task_status = "FAILURE"
            separator_instance.save()
            e = result.data["error"]
            run_audio_separation.update_state(
                state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)}
            )
        else:
            music_filename, speech_filename = result
            separator_instance.music_filename = music_filename
            separator_instance.speech_filename = speech_filename
            separator_instance.task_status = "SUCCESS"
            separator_instance.save()
            run_audio_separation.update_state(
                state="SUCCESS", meta={"music_filename": music_filename, "speech_filename": speech_filename}
            )
    except Exception as e:
        separator_instance.task_status = "FAILURE"
        separator_instance.save()
        run_audio_separation.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
        raise  # TODO: check if we need to raise an exception here
