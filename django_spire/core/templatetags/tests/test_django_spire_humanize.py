from __future__ import annotations

import unittest

from django.template import Context, Template

from django_spire.core.templatetags.django_spire_humanize import (
    humanize_duration,
    humanize_duration_compact,
    humanize_duration_simple,
)


class TestHumanizeDurationSimple(unittest.TestCase):
    def test_zero_amount_returns_na(self) -> None:
        result = humanize_duration_simple(0)
        assert result == 'N/A'

    def test_none_amount_returns_na(self) -> None:
        result = humanize_duration_simple(None)  # type: ignore[arg-type]
        assert result == 'N/A'

    def test_positive_amount_with_default_unit(self) -> None:
        result = humanize_duration_simple(5)
        assert result == '5 seconds'

    def test_positive_singular_unit(self) -> None:
        result = humanize_duration_simple(1)
        assert result == '1 second'

    def test_different_start_unit(self) -> None:
        result = humanize_duration_simple(3, start_unit='minute')
        assert result == '3 minutes'

    def test_invalid_unit_returns_na(self) -> None:
        result = humanize_duration_simple(10, start_unit='invalid')
        assert result == 'N/A'

    def test_negative_amount(self) -> None:
        result = humanize_duration_simple(-5)
        assert result == '-5 seconds'

    def test_hour_unit(self) -> None:
        result = humanize_duration_simple(2, start_unit='hour')
        assert result == '2 hours'

    def test_day_unit(self) -> None:
        result = humanize_duration_simple(1, start_unit='day')
        assert result == '1 day'


class TestHumanizeDuration(unittest.TestCase):
    def test_full_duration(self) -> None:
        result = humanize_duration(3661)
        assert '1 hour' in result
        assert '1 minute' in result
        assert '1 second' in result

    def test_short_form(self) -> None:
        result = humanize_duration(3661, is_short_form=True)
        assert '1h' in result
        assert '1m' in result
        assert '1s' in result

    def test_min_unit(self) -> None:
        result = humanize_duration(3661, min_unit='minute')
        assert '1 hour' in result
        assert '1 minute' in result
        assert '1 second' not in result

    def test_included_units(self) -> None:
        result = humanize_duration(90061, included_units=['day', 'hour'])
        assert '1 day' in result
        assert '1 hour' in result

    def test_zero_amount(self) -> None:
        result = humanize_duration(0)
        assert result == 'Unknown'

    def test_different_start_unit(self) -> None:
        result = humanize_duration(1.5, start_unit='day', included_units=['hour'])
        assert '36 hours' in result

    def test_year_duration(self) -> None:
        result = humanize_duration(31536001)
        assert '1 year' in result


class TestHumanizeDurationCompact(unittest.TestCase):
    def test_compact_format(self) -> None:
        result = humanize_duration_compact(3661)
        assert '1h' in result
        assert '1m' in result
        assert '1s' in result

    def test_compact_with_min_unit(self) -> None:
        result = humanize_duration_compact(3661, min_unit='minute')
        assert '1h' in result
        assert '1m' in result
        assert '1s' not in result

    def test_compact_included_units(self) -> None:
        result = humanize_duration_compact(90061, included_units=['day', 'hour'])
        assert '1d' in result
        assert '1h' in result

    def test_zero_amount(self) -> None:
        result = humanize_duration_compact(0)
        assert result == 'Unknown'


class TestHumanizeDurationTemplateRendering(unittest.TestCase):
    def test_render_humanize_duration_simple(self) -> None:
        template_code = """
            {% load django_spire_humanize %}

            {{ seconds | humanize_duration_simple }}
        """

        tmpl = Template(template_code)
        context = Context({'seconds': 5})
        rendered = tmpl.render(context)

        assert '5 seconds' in rendered

    def test_render_humanize_duration_simple_with_unit(self) -> None:
        template_code = """
            {% load django_spire_humanize %}

            {{ minutes | humanize_duration_simple:"minute" }}
        """

        tmpl = Template(template_code)
        context = Context({'minutes': 3})
        rendered = tmpl.render(context)

        assert '3 minutes' in rendered

    def test_render_humanize_duration(self) -> None:
        template_code = """
            {% load django_spire_humanize %}

            {{ seconds | humanize_duration }}
        """

        tmpl = Template(template_code)
        context = Context({'seconds': 3661})
        rendered = tmpl.render(context)

        assert 'hour' in rendered or '1h' in rendered

    def test_render_humanize_duration_compact(self) -> None:
        template_code = """
            {% load django_spire_humanize %}

            {{ seconds | humanize_duration_compact }}
        """

        tmpl = Template(template_code)
        context = Context({'seconds': 3661})
        rendered = tmpl.render(context)

        assert '1h' in rendered
