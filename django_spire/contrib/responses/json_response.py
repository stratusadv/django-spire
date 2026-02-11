from django.http import JsonResponse

from django_spire.contrib.responses.enums import ResponseTypeChoices


def error_json_response(message: str | None = None, **kwargs) -> JsonResponse:
    return json_response(type=ResponseTypeChoices.ERROR, message=message, **kwargs)


def info_json_response(message: str | None = None, **kwargs) -> JsonResponse:
    return json_response(type=ResponseTypeChoices.INFO, message=message, **kwargs)


def json_response(type: ResponseTypeChoices, message: str | None = None, **kwargs) -> JsonResponse:
    response_choices = [choice.value for choice in ResponseTypeChoices]
    if type not in response_choices:
        valid = ', '.join(response_choices)
        raise ValueError(f'{type} is not a valid option for ResponseTypeChoices: [{valid}]')

    return_data = {
        'type': type.value,
        **kwargs,
    }

    if message is not None:
        return_data.update({'message': message})

    return JsonResponse(return_data)


def success_json_response(message: str | None = None, **kwargs) -> JsonResponse:
    return json_response(type=ResponseTypeChoices.SUCCESS, message=message, **kwargs)


def warning_json_response(message: str | None = None, **kwargs) -> JsonResponse:
    return json_response(type=ResponseTypeChoices.WARNING, message=message, **kwargs)