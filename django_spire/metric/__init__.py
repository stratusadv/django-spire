from __future__ import annotations

__all__ = (
    'BuildSummary',
    'DomainSpec',
    'Metric',
    'StatisticGroupSpec',
    'StatisticSpec',
    'SubDomainSpec',
    'Target',
    'discover_metric_registries',
)


def __getattr__(name: str) -> object:
    if name in __all__:
        from django_spire.metric import metric  # noqa: PLC0415

        return getattr(metric, name)

    message = f'module {__name__!r} has no attribute {name!r}'
    raise AttributeError(message)
