from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from typing_extensions import Any
from django_spire.core.context_processors import django_spire as django_spire_context_processor


def test_project(_: WSGIRequest) -> dict[str, list[dict[str, str]]]:
    return {
        'test_project_apps': [
            {'heading': 'Django Spire'},
            {'title': 'Ai Management', 'icon': 'bi bi-robot', 'url': reverse('ai:home')},
            {'title': 'Ai Chat', 'icon': 'bi bi-chat-heart', 'url': reverse('ai:chat:home')},
            {'title': 'Comment', 'icon': 'bi bi-chat-text', 'url': reverse('comment:home')},
            {'title': 'Help Desk', 'icon': 'bi bi-headset', 'url': reverse('help_desk:home')},
            {'title': 'History', 'icon': 'bi bi-clock-history', 'url': reverse('history:home')},
            {'title': 'Home', 'icon': 'bi bi-house-door', 'url': reverse('home:page:home')},
            {'title': 'Notification', 'icon': 'bi bi-bell', 'url': reverse('notification:page:home')},
            {'title': 'Wizard', 'icon': 'bi bi-magic', 'url': reverse('wizard:home')},
            {'heading': 'Examples'},
            {'title': 'Component', 'icon': 'bi bi-puzzle', 'url': reverse('component:home')},
            {'title': 'Tabular', 'icon': 'bi bi-table', 'url': reverse('tabular:home')},
        ]
    }


def django_spire(request: WSGIRequest) -> dict[str, Any]:
    context_data = django_spire_context_processor(request)
    context_data['app_bootstrap_icon']['other'] = 'testy_test_icon_string'

    return context_data