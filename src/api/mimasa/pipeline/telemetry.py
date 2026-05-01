import contextvars
import logging
import uuid

request_id_ctx = contextvars.ContextVar("request_id", default="")


def set_request_id(request_id: str | None = None) -> str:
    value = request_id or str(uuid.uuid4())
    request_id_ctx.set(value)
    return value


def get_request_id() -> str:
    return request_id_ctx.get()


def log_event(event_name: str, **kwargs):
    payload = {
        "event": event_name,
        "request_id": get_request_id(),
        **kwargs,
    }
    logging.getLogger("mimasa.telemetry").info(payload)
