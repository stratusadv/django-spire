from __future__ import annotations

from django.urls import reverse


def get_app_context_data() -> list[dict[str, str]]:
    app_context_list = [
        {'heading': 'Django Spire'},
        {'title': 'Ai Management', 'icon_class': 'bi bi-robot', 'url': reverse('ai:home')},
        {'title': 'Authentication', 'icon_class': 'bi bi-shield-lock', 'url': reverse('authentication:home')},
        {'title': 'Authentication: MFA', 'icon_class': 'bi bi-shield-lock-fill', 'url': reverse('authentication:mfa:home')},
        {'title': 'Breadcrumb', 'icon_class': 'bi bi-list-nested', 'url': reverse('breadcrumb:home')},
        {'title': 'Comment', 'icon_class': 'bi bi-chat-text', 'url': reverse('comment:home')},
        {'title': 'File', 'icon_class': 'bi bi-file-earmark', 'url': reverse('file:home')},
        {'title': 'Form', 'icon_class': 'bi bi-ui-checks', 'url': reverse('form:home')},
        {'title': 'Gamification', 'icon_class': 'bi bi-award', 'url': reverse('gamification:home')},
        {'title': 'Help', 'icon_class': 'bi bi-question-circle', 'url': reverse('help:home')},
        {'title': 'History', 'icon_class': 'bi bi-clock-history', 'url': reverse('history:home')},
        {'title': 'Home', 'icon_class': 'bi bi-house-door', 'url': reverse('home:home')},
        {'title': 'Maintenance', 'icon_class': 'bi bi-tools', 'url': reverse('maintenance:home')},
        {'title': 'Modal', 'icon_class': 'bi bi-window', 'url': reverse('modal:home')},
        {'title': 'Notification', 'icon_class': 'bi bi-bell', 'url': reverse('notification:page:home')},
        {'title': 'Options', 'icon_class': 'bi bi-gear', 'url': reverse('options:home')},
        {'title': 'Pagination', 'icon_class': 'bi bi-arrow-bar-right', 'url': reverse('pagination:home')},
        {'title': 'Permission', 'icon_class': 'bi bi-lock', 'url': reverse('permission:home')},
        {'title': 'Search', 'icon_class': 'bi bi-search', 'url': reverse('search:home')},
        {'title': 'Speech to Text', 'icon_class': 'bi-chat-left-text', 'url': reverse('speech_to_text:home')},
        {'title': 'User Account', 'icon_class': 'bi bi-person', 'url': reverse('user_account:home')},
        {'title': 'User Account: Profile', 'icon_class': 'bi bi-person-circle', 'url': reverse('user_account:home')},
        {'title': 'Wizard', 'icon_class': 'bi bi-magic', 'url': reverse('wizard:home')},

        {'heading': 'Examples'},
        {'title': 'Test Model', 'icon_class': 'bi bi-database', 'url': reverse('test_model:home')},
        {'title': 'Component', 'icon_class': 'bi bi-puzzle', 'url': reverse('component:home')},
        {'title': 'Cookbook', 'icon_class': 'bi bi-book', 'url': reverse('cookbook:list')},
        {'title': 'Tabular', 'icon_class': 'bi bi-table', 'url': reverse('tabular:home')},

    ]

    return app_context_list
