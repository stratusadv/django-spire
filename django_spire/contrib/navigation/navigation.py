from __future__ import annotations

from django.urls import reverse

from django_spire.conf import settings
from django_spire.contrib.navigation.breadcrumbs import Breadcrumbs
from django_spire.contrib.navigation.tools import form_action_name
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django.db.models import Model


class Navigation:
    def __init__(self) -> None:
        self.page_title: str | None = None
        self.help_template: str | None = None
        self.icon_class: str | None = None
        self.home_url: str | None = settings.DJANGO_SPIRE_NAVIGATION_HOME_URL
        self.breadcrumbs: Breadcrumbs = Breadcrumbs()

    @property
    def home_href(self) -> str | None:
        if self.home_url:
            return reverse(viewname=self.home_url)

        return None

    def set_page_title_from_model_plural_name(self, model: type[Model] | Model) -> None:
        self.page_title = str(model._meta.verbose_name_plural.title())

    def set_page_title_from_model_name(self, model: type[Model] | Model) -> None:
        self.page_title = str(model._meta.verbose_name.title())

    def set_page_title_to_form_action_from_model_instance(self, model: Model) -> None:
        self.page_title = (
            f'{form_action_name(has_pk=model.pk is not None)} {model._meta.verbose_name.title()}'
        )

    def as_context(self) -> dict[str, Any]:
        return {
            'django_spire_navigation': {
                'page_title': self.page_title,
                'home_href': self.home_href,
                'icon_class': self.icon_class,
                'help_template': self.help_template,
                **self.breadcrumbs.as_context(),
            }
        }
