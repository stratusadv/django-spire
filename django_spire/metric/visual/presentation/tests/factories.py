from __future__ import annotations

from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)


def create_test_presentation(
    name: str = 'test_presentation', description: str = 'presentation description'
) -> Presentation:
    return Presentation.objects.create(name=name, description=description)


def create_test_slide(
    presentation: Presentation, name: str = 'test_slide', order: int = 0
) -> Slide:
    return Slide.objects.create(presentation=presentation, name=name, order=order)


def create_test_section(
    slide: Slide, row: int = 1, col: int = 1, with_visual: bool = True
) -> SlideSection:
    visual = None

    if with_visual:
        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        statistic = create_test_statistic(group=group)
        visual = create_test_visual(statistic=statistic, name=f'test_visual_{row}_{col}')

    return SlideSection.objects.create(slide=slide, visual=visual, row=row, col=col)
