import base64

from django.contrib.auth import authenticate, login
from django.http.response import HttpResponse


def allow_basic_auth(persist_login=False):
    def decorator_wrapper(view_func):
        def view_wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)

            auth_header_parts = request.META.get('HTTP_AUTHORIZATION', '').split(' ')

            if auth_header_parts[0].lower() == 'basic':
                username, password = (
                    base64.b64decode(auth_header_parts[1])
                    .decode('utf-8')
                    .split(':')
                )

                user = authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    request.user = user
                    if persist_login:
                        login(request, user)

                    return view_func(request, *args, **kwargs)

            return HttpResponse(status=401)

        return view_wrapper

    return decorator_wrapper