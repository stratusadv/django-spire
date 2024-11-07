from __future__ import annotations

from django.urls import reverse


def get_app_context_data() -> list[dict[str, str]]:
    return [
        # Django Spire
        {'title': 'Authentication', 'icon_class': 'bi bi-shield-lock', 'url': '#'},
        {'title': 'Authentication: MFA', 'icon_class': 'bi bi-shield-lock-fill', 'url': '#'},
        {'title': 'Breadcrumb', 'icon_class': 'bi bi-list-nested', 'url': '#'},
        {'title': 'Comment', 'icon_class': 'bi bi-chat-text', 'url': '#'},

        {'title': 'File', 'icon_class': 'bi bi-file-earmark', 'url': '#'},
        {'title': 'Form', 'icon_class': 'bi bi-ui-checks', 'url': '#'},
        {'title': 'Gamification', 'icon_class': 'bi bi-award', 'url': '#'},
        {'title': 'Help', 'icon_class': 'bi bi-question-circle', 'url': '#'},

        {'title': 'History', 'icon_class': 'bi bi-clock-history', 'url': '#'},
        {'title': 'Home', 'icon_class': 'bi bi-house-door', 'url': '#'},
        {'title': 'Maintenance', 'icon_class': 'bi bi-tools', 'url': '#'},
        {'title': 'Modal', 'icon_class': 'bi bi-window', 'url': reverse('modal:home')},

        {'title': 'Notification', 'icon_class': 'bi bi-bell', 'url': '#'},
        {'title': 'Options', 'icon_class': 'bi bi-gear', 'url': '#'},
        {'title': 'Pagination', 'icon_class': 'bi bi-arrow-bar-right', 'url': '#'},
        {'title': 'Permission', 'icon_class': 'bi bi-lock', 'url': '#'},

        {'title': 'Search', 'icon_class': 'bi bi-search', 'url': '#'},
        {'title': 'User Account', 'icon_class': 'bi bi-person', 'url': '#'},
        {'title': 'User Account: Profile', 'icon_class': 'bi bi-person-circle', 'url': '#'},

        # Example
        {'title': 'Test Model', 'icon_class': 'bi bi-database', 'url': reverse('test_model')},
        {'title': 'Component', 'icon_class': 'bi bi-puzzle', 'url': reverse('component:home')},
        {'title': 'Cookbook', 'icon_class': 'bi bi-book', 'url': reverse('cookbook:list')},
    ]
