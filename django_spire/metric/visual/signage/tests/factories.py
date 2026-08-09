from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.metric.visual.presentation.tests.factories import (
    create_test_presentation,
    create_test_section,
    create_test_slide,
)
from django_spire.metric.visual.signage.models import Signage, SignagePresentation

if TYPE_CHECKING:
    from django_spire.metric.visual.presentation.models import Presentation


def create_test_signage(
    name: str = 'test_signage', description: str = 'signage description'
) -> Signage:
    return Signage.objects.create(name=name, description=description)


def create_test_link(
    signage: Signage, presentation: Presentation | None = None, order: int = 0
) -> SignagePresentation:
    presentation = presentation or create_test_presentation(name=f'presentation_{order}')
    return SignagePresentation.objects.create(
        signage=signage, presentation=presentation, order=order
    )


def create_test_signage_links(signage: Signage, count: int = 3) -> list[SignagePresentation]:
    links = []

    for order in range(count):
        presentation = create_test_presentation(name=f'presentation_{order}')
        slide = create_test_slide(presentation)
        create_test_section(slide, row=1, col=order + 1)
        links.append(create_test_link(signage, presentation=presentation, order=order))

    return links
