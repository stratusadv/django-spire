from typing import Callable

from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse


def bearer_token_auth_required(token: str) -> Callable[[Callable], Callable]:
    def decorator_wrapper(view_func: Callable) -> Callable:
        def view_wrapper(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)

            auth_header_parts = request.META.get('HTTP_AUTHORIZATION', '').split(' ')

            if auth_header_parts[0].lower() == 'bearer':
                if auth_header_parts[1] == token:
                    return view_func(request, *args, **kwargs)

            return HttpResponse(status=401)

        return view_wrapper

    return decorator_wrapper