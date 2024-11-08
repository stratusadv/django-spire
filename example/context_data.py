from __future__ import annotations

from django.urls import reverse


def get_app_context_data() -> list[dict[str, str]]:
    return [
        # Django Spire
        {'title': 'Authentication', 'icon_class': 'bi bi-shield-lock', 'url': reverse('authentication:list')},
        {'title': 'Authentication: MFA', 'icon_class': 'bi bi-shield-lock-fill', 'url': reverse('authentication:mfa:list')},
        {'title': 'Breadcrumb', 'icon_class': 'bi bi-list-nested', 'url': reverse('breadcrumb:list')},
        {'title': 'Comment', 'icon_class': 'bi bi-chat-text', 'url': reverse('comment:list')},

        {'title': 'File', 'icon_class': 'bi bi-file-earmark', 'url': reverse('file:list')},
        {'title': 'Form', 'icon_class': 'bi bi-ui-checks', 'url': reverse('form:list')},
        {'title': 'Gamification', 'icon_class': 'bi bi-award', 'url': reverse('gamification:list')},
        {'title': 'Help', 'icon_class': 'bi bi-question-circle', 'url': reverse('help:list')},

        {'title': 'History', 'icon_class': 'bi bi-clock-history', 'url': reverse('history:list')},
        {'title': 'Home', 'icon_class': 'bi bi-house-door', 'url': reverse('home:list')},
        {'title': 'Maintenance', 'icon_class': 'bi bi-tools', 'url': reverse('maintenance:list')},
        {'title': 'Modal', 'icon_class': 'bi bi-window', 'url': reverse('modal:home')},

        {'title': 'Notification', 'icon_class': 'bi bi-bell', 'url': reverse('notification:list')},
        {'title': 'Options', 'icon_class': 'bi bi-gear', 'url': reverse('options:list')},
        {'title': 'Pagination', 'icon_class': 'bi bi-arrow-bar-right', 'url': reverse('pagination:list')},
        {'title': 'Permission', 'icon_class': 'bi bi-lock', 'url': reverse('permission:list')},

        {'title': 'Search', 'icon_class': 'bi bi-search', 'url': reverse('search:list')},
        {'title': 'User Account', 'icon_class': 'bi bi-person', 'url': reverse('user_account:list')},
        {'title': 'User Account: Profile', 'icon_class': 'bi bi-person-circle', 'url': reverse('user_account:profile:list')},

        # Example
        {'title': 'Test Model', 'icon_class': 'bi bi-database', 'url': reverse('test_model')},
        {'title': 'Component', 'icon_class': 'bi bi-puzzle', 'url': reverse('component:home')},
        {'title': 'Cookbook', 'icon_class': 'bi bi-book', 'url': reverse('cookbook:list')},
    ]
