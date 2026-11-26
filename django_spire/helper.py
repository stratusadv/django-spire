from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

# All helper functions need to be loaded as lazily as possible to prevent Django startup errors.


class _SpireMeta(type):
    def __getattr__(cls, name: str) -> Any:
        if name in ('Form', 'ModelForm'):
            from django_spire.core import forms as spire_forms

            mapping = {
                'Form': spire_forms.SpireForm,
                'ModelForm': spire_forms.SpireModelForm,
            }
            return mapping[name]

        message = f"type object '{cls.__name__}' has no attribute '{name}'"
        raise AttributeError(message)


class Spire(metaclass=_SpireMeta):
    if TYPE_CHECKING:
        from django_spire.core.forms import SpireForm as Form
        from django_spire.core.forms import SpireModelForm as ModelForm

    class Metric:
        class Statistic:
            @staticmethod
            def record(
                    statistic_key: str,
                    sub_domain_key: str,
                    reference: str,
                    value: float | str | Decimal = 1,
            ) -> None:
                from django_spire.metric.domain.statistic.models import Statistic

                Statistic.services.record(statistic_key, sub_domain_key, reference, value)

            @staticmethod
            def remote_record(
                    statistic_key: str,
                    sub_domain_key: str,
                    reference: str,
                    value: float | str | Decimal = 1,
            ) -> dict | None:
                from django_spire.metric.domain.statistic.models import Statistic

                Statistic.services.remote_record(statistic_key, sub_domain_key, reference, value)
