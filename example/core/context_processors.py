from __future__ import annotations

from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse


def example(request: WSGIRequest) -> dict[str, list[dict[str, str]]]:
    return {
        'example_apps': [
            {'heading': 'Django Spire'},
            {'title': 'Ai Management', 'icon': 'bi bi-robot', 'url': reverse('ai:home')},
            {'title': 'Ai Chat', 'icon': 'bi bi-chat-heart', 'url': reverse('ai:chat:home')},
            {'title': 'Breadcrumb', 'icon': 'bi bi-list-nested', 'url': reverse('breadcrumb:home')},
            {'title': 'Comment', 'icon': 'bi bi-chat-text', 'url': reverse('comment:home')},
            {'title': 'File', 'icon': 'bi bi-file-earmark', 'url': reverse('file:home')},
            {'title': 'Form', 'icon': 'bi bi-ui-checks', 'url': reverse('form:home')},
            {'title': 'Gamification', 'icon': 'bi bi-award', 'url': reverse('gamification:home')},
            {'title': 'Help', 'icon': 'bi bi-question-circle', 'url': reverse('help:home')},
            {'title': 'History', 'icon': 'bi bi-clock-history', 'url': reverse('history:home')},
            {'title': 'Home', 'icon': 'bi bi-house-door', 'url': reverse('home:page:home')},
            {'title': 'Modal', 'icon': 'bi bi-window', 'url': reverse('modal:home')},
            {'title': 'Notification', 'icon': 'bi bi-bell', 'url': reverse('notification:page:home')},
            {'title': 'Options', 'icon': 'bi bi-gear', 'url': reverse('options:home')},
            {'title': 'Pagination', 'icon': 'bi bi-arrow-bar-right', 'url': reverse('pagination:home')},
            {'title': 'Permission', 'icon': 'bi bi-lock', 'url': reverse('permission:home')},
            {'title': 'Search', 'icon': 'bi bi-search', 'url': reverse('search:home')},
            {'title': 'Speech to Text', 'icon': 'bi-chat-left-text', 'url': reverse('speech_to_text:home')},
            {'title': 'User Account', 'icon': 'bi bi-person', 'url': reverse('user_account:home')},
            {'title': 'User Account: Profile', 'icon': 'bi bi-person-circle', 'url': reverse('user_account:home')},
            {'title': 'Wizard', 'icon': 'bi bi-magic', 'url': reverse('wizard:home')},
            {'heading': 'Examples'},
            {'title': 'Test Model', 'icon': 'bi bi-database', 'url': reverse('test_model:home')},
            {'title': 'Component', 'icon': 'bi bi-puzzle', 'url': reverse('component:home')},
            {'title': 'Tabular', 'icon': 'bi bi-table', 'url': reverse('tabular:home')},
        ]
    }
