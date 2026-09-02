from __future__ import annotations

from django.template import Context, Template

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.visual.models import VisualRegion
from django_spire.metric.visual.tests.factories import (
    create_test_domain,
    create_test_statistic,
    create_test_statistic_group,
    create_test_visual,
)

TAG_KEY = 'home:dashboard:hero'


class RenderVisualRegionTagTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        domain = create_test_domain()
        group = create_test_statistic_group(domain=domain)
        self.statistic = create_test_statistic(group=group)
        self.request = self.client.get('/').wsgi_request

    def _render(self) -> str:
        template_string = (
            "{% load django_spire_metric_region %}{% render_visual_region '" + TAG_KEY + "' %}"
        )
        template = Template(template_string)
        return template.render(Context({'request': self.request}))

    def test_unassigned_renders_placeholder(self):
        assert VisualRegion.objects.filter(key=TAG_KEY).count() == 0

        content = self._render()

        assert 'Unassigned' in content
        assert TAG_KEY in content

    def test_assigned_renders_visual(self):
        visual = create_test_visual(statistic=self.statistic)
        VisualRegion.objects.create(key=TAG_KEY, visual=visual)

        content = self._render()

        assert visual.name in content
        assert 'Unassigned' not in content

    def test_title_overrides_visual_name(self):
        visual = create_test_visual(statistic=self.statistic)
        VisualRegion.objects.create(key=TAG_KEY, visual=visual, title='Hero Metric')

        content = self._render()

        assert 'Hero Metric' in content
        assert visual.name not in content

    def test_live_chart_renders(self):
        visual = create_test_visual(statistic=self.statistic, kind='line', with_conditions=False)
        VisualRegion.objects.create(key=TAG_KEY, visual=visual, is_live_updated=True)

        content = self._render()

        assert visual.name in content

    def test_static_chart_renders_without_glue(self):
        visual = create_test_visual(statistic=self.statistic, kind='line', with_conditions=False)
        VisualRegion.objects.create(key=TAG_KEY, visual=visual, is_live_updated=False)

        content = self._render()

        assert visual.name in content
