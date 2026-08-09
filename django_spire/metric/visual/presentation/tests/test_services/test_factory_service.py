from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.presentation.models import Presentation, Slide, SlideSection


class PresentationFactoryServiceTestCase(BaseTestCase):
    def test_factory_services_exposed(self):
        presentation = Presentation.objects.create(name='p')
        slide = Slide.objects.create(presentation=presentation, name='s')

        assert presentation.services.factory is not None
        assert slide.services.factory is not None
        assert SlideSection.objects.create(slide=slide, row=1, col=1).services.factory is not None
