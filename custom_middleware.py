from django.utils.deprecation import MiddlewareMixin


# class CustomMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         ...
#
#     def process_response(self, request, response):
#         ...


class CustomMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ...

        response = self.get_response(request)
        ...