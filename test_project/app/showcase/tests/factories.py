from __future__ import annotations

from typing import Any

from test_project.app.showcase.models import ShowcaseCategory, ShowcaseTag, WidgetShowcase


def create_test_showcase_category(name: str = 'Test Category') -> ShowcaseCategory:
    return ShowcaseCategory.objects.create(name=name)


def create_test_showcase_tag(name: str = 'Test Tag') -> ShowcaseTag:
    return ShowcaseTag.objects.create(name=name)


def create_test_widget_showcase(**kwargs: Any) -> WidgetShowcase:
    return WidgetShowcase.objects.create(**kwargs)
