from django.http import JsonResponse

from django_spire.contrib.responses.enums import ResponseTypeChoices


def json_response(type: str, message: str, **kwargs) -> JsonResponse:
    response_choices = [choice.value for choice in ResponseTypeChoices]
    if type not in response_choices:
        valid = ', '.join(response_choices)
        raise ValueError(f'{type} is not a valid option for ResponseTypeChoices: [{valid}]')

    return JsonResponse({
        'type': type,
        'message': message,
        **kwargs,
    })