from django.http import HttpRequest


class FakeRemoteUserMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if not request.META.get("REMOTE_USER"):
            request.META['REMOTE_USER'] = "EXAMPLE\\administrator"
        return self.get_response(request)
