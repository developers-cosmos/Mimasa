from .services import audio_separation_service
from mimasa.celery import app


@app.task
def run_audio_separation(audio_filepath, destination_folder):
    try:
        result = audio_separation_service(audio_filepath=audio_filepath, destination=destination_folder)
        if "error" in result:
            e = result["error"]
            exc_type = result["exc_type"]
            run_audio_separation.update_state(state="FAILURE", meta={"exc_type": exc_type, "exc_message": str(e)})
        else:
            run_audio_separation.update_state(
                state="SUCCESS",
                meta={"music_filename": result["music_filename"], "speech_filename": result["speech_filename"]},
            )
    except Exception as e:
        run_audio_separation.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
