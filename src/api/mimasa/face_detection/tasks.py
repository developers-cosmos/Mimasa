from mimasa.celery import app

from .services import face_detection_service


@app.task
def run_face_detection(video_filepath: str, destination: str, async_enabled: bool, async_type: str, detector_type: str):
    try:
        result = face_detection_service(video_filepath, destination, async_enabled, async_type, detector_type)
        if "error" in result:
            e = result["error"]
            exc_type = result["exc_type"]
            run_face_detection.update_state(state="FAILURE", meta={"exc_type": exc_type, "exc_message": str(e)})
        else:
            run_face_detection.update_state(
                state="SUCCESS",
                meta={"video_filename": result["video_filename"]},
            )
    except Exception as e:
        run_face_detection.update_state(state="FAILURE", meta={"exc_type": type(e).__name__, "exc_message": str(e)})
