from django.core.management import CommandError


class AppExistsError(CommandError):
    pass