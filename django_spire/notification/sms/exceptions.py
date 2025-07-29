from django_spire.exceptions import DjangoSpireException


class SmsNotificationException(DjangoSpireException):
    pass


class SmsTemporaryMediaException(SmsNotificationException):
    pass


class TwilioException(Exception):
    pass


class TwilioAPIConcurrentException(TwilioException):
    pass
