from .telemetry import set_request_id


class RequestContextMiddleware:
    """Adds a request id into request context and response headers."""

    header_name = "HTTP_X_REQUEST_ID"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inbound_request_id = request.META.get(self.header_name)
        request_id = set_request_id(inbound_request_id)
        request.request_id = request_id

        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
