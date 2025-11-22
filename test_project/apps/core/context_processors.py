from __future__ import annotations

from typing import Any, TYPE_CHECKING

from django.urls import reverse
from django_spire.core.context_processors import django_spire as django_spire_default

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


# Demonstrating how to override the default django spire context processor data
def django_spire(request: WSGIRequest) -> dict[str, Any]:
    return django_spire_default(request)


def test_project(request: WSGIRequest) -> dict[str, list[dict[str, str]]]:
    _ = django_spire(request)

    return {
        'test_project_apps': [
            {'heading': 'Django Spire'},
            {'title': 'Ai Home', 'icon': 'bi bi-robot', 'url': reverse('ai:home')},
            {'title': 'Ai Chat', 'icon': 'bi bi-chat-heart', 'url': reverse('django_spire:ai:chat:page:home')},
            {'title': 'Comment', 'icon': 'bi bi-chat-text', 'url': reverse('comment:home')},
            {'title': 'Help Desk', 'icon': 'bi bi-headset', 'url': reverse('help_desk:home')},
            {'title': 'History', 'icon': 'bi bi-clock-history', 'url': reverse('history:home')},
            {'title': 'Home', 'icon': 'bi bi-house-door', 'url': reverse('home:page:home')},
            {'title': 'Ordering', 'icon': 'bi bi-list-ol', 'url': reverse('ordering:page:demo')},
            {'title': 'Knowledge', 'icon': 'bi bi-journal-bookmark', 'url': reverse('django_spire:knowledge:page:home')},
            {'title': 'Notification', 'icon': 'bi bi-bell', 'url': reverse('notification:page:list')},
            {'title': 'Theme', 'icon': 'bi bi-brush', 'url': reverse('django_spire:theme:page:dashboard')},
            {'title': 'QuerySet Filtering', 'icon': 'bi bi-filter', 'url': reverse('queryset_filtering:page:list')},
            {'title': 'Wizard', 'icon': 'bi bi-magic', 'url': reverse('wizard:home')},
            {'heading': 'Examples'},
            {'title': 'Tabular', 'icon': 'bi bi-table', 'url': reverse('tabular:page:list')},
        ]
    }
