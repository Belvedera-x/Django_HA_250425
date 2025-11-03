from django.http import HttpResponse, HttpRequest


def home_page(request: HttpRequest):
    return HttpResponse(
        f"<h1>Hello from our first endpoint!!!</h1>"
    )

def name_page(request: HttpRequest, user_name):
    return HttpResponse(
        f"<h1>Hello {user_name}!!!</h1>"
    )

