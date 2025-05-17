from django.db.models import Choices


class MessageResponseType(Choices):
    REQUEST = 'request'
    RESPONSE = 'response'
    LOADING_RESPONSE = 'loading_response'
