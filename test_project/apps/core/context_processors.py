from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from typing_extensions import Any
from django_spire.core.context_processors import django_spire as django_spire_default


# Demonstrating how to override the default django spire context processor data
def django_spire(request: WSGIRequest) -> dict[str, Any]:
    context_data = django_spire_default(request)
    context_data['app_bootstrap_icon']['help_desk'] = 'bi bi-headset'

    return context_data


def test_project(request: WSGIRequest) -> dict[str, list[dict[str, str]]]:
    spire_context_data = django_spire(request)

    return {
        'test_project_apps': [
            {'heading': 'Django Spire'},
            {'title': 'Ai Management', 'icon': 'bi bi-robot', 'url': reverse('ai:home')},
            {'title': 'Ai Chat', 'icon': 'bi bi-chat-heart', 'url': reverse('ai:chat:home')},
            {'title': 'Comment', 'icon': 'bi bi-chat-text', 'url': reverse('comment:home')},
            {'title': 'Help Desk', 'icon': spire_context_data['app_bootstrap_icon']['help_desk'], 'url': reverse('help_desk:home')},
            {'title': 'History', 'icon': 'bi bi-clock-history', 'url': reverse('history:home')},
            {'title': 'Home', 'icon': 'bi bi-house-door', 'url': reverse('home:page:home')},
            {'title': 'Knowledge', 'icon': 'bi bi-journal-bookmark', 'url': reverse('django_spire:knowledge:collection:page:list')},
            {'title': 'Notification', 'icon': 'bi bi-bell', 'url': reverse('notification:page:list')},
            {'title': 'Test Model', 'icon': 'bi bi-flask', 'url': reverse('test_model:detail')},
            {'title': 'Wizard', 'icon': 'bi bi-magic', 'url': reverse('wizard:home')},
            {'heading': 'Examples'},
            {'title': 'Tabular', 'icon': 'bi bi-table', 'url': reverse('tabular:home')},
        ]
    }
