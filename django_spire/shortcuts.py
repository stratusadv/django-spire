from django.urls import path, include

from django_spire.constants import BASE_URL_NAME


def django_spire_urls() -> list:
    return [
        path(
            f'{BASE_URL_NAME}/',
            include('django_spire.urls', namespace=BASE_URL_NAME),
        )
    ]

