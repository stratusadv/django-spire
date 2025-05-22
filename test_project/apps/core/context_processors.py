from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse


def test_project(request: WSGIRequest) -> dict[str, list[dict[str, str]]]:
    return {
        'test_project_apps': [
            {'heading': 'Django Spire'},
            {'title': 'Ai Management', 'icon': 'bi bi-robot', 'url': reverse('ai:home')},
            {'title': 'Ai Chat', 'icon': 'bi bi-chat-heart', 'url': reverse('ai:chat:home')},
            {'title': 'Comment', 'icon': 'bi bi-chat-text', 'url': reverse('comment:home')},
            {'title': 'History', 'icon': 'bi bi-clock-history', 'url': reverse('history:home')},
            {'title': 'Home', 'icon': 'bi bi-house-door', 'url': reverse('home:page:home')},
            {'title': 'Notification', 'icon': 'bi bi-bell', 'url': reverse('notification:page:list')},
            {'title': 'Wizard', 'icon': 'bi bi-magic', 'url': reverse('wizard:home')},
            {'heading': 'Examples'},
            {'title': 'Component', 'icon': 'bi bi-puzzle', 'url': reverse('component:home')},
            {'title': 'Tabular', 'icon': 'bi bi-table', 'url': reverse('tabular:home')},
        ]
    }
