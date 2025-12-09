from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings

from django_spire.contrib.performance.decorators import performance_timer


class TestPerformanceTimer(TestCase):
    @override_settings(DEBUG=True)
    def test_calls_function_when_debug_true(self) -> None:
        @performance_timer
        def sample_func() -> str:
            return 'result'

        result = sample_func()

        assert result == 'result'

    @override_settings(DEBUG=False)
    def test_calls_function_when_debug_false(self) -> None:
        @performance_timer
        def sample_func() -> str:
            return 'result'

        result = sample_func()

        assert result == 'result'

    @override_settings(DEBUG=True)
    def test_logs_warning_when_debug_true(self) -> None:
        @performance_timer
        def sample_func() -> str:
            return 'result'

        with patch('django_spire.contrib.performance.decorators.logging.warning') as mock_warning:
            sample_func()

            mock_warning.assert_called_once()

    @override_settings(DEBUG=False)
    def test_no_logging_when_debug_false(self) -> None:
        @performance_timer
        def sample_func() -> str:
            return 'result'

        with patch('django_spire.contrib.performance.decorators.logging.warning') as mock_warning:
            sample_func()

            mock_warning.assert_not_called()

    @override_settings(DEBUG=True)
    def test_log_message_contains_runtime(self) -> None:
        @performance_timer
        def sample_func() -> str:
            return 'result'

        with patch('django_spire.contrib.performance.decorators.logging.warning') as mock_warning:
            sample_func()

            log_message = mock_warning.call_args[0][0]

            assert 'seconds runtime' in log_message

    @override_settings(DEBUG=True)
    def test_log_message_contains_function_name(self) -> None:
        @performance_timer
        def sample_func() -> str:
            return 'result'

        with patch('django_spire.contrib.performance.decorators.logging.warning') as mock_warning:
            sample_func()

            log_message = mock_warning.call_args[0][0]

            assert 'sample_func' in log_message

    @override_settings(DEBUG=True)
    def test_passes_args_to_function(self) -> None:
        @performance_timer
        def sample_func(a: int, b: int) -> int:
            return a + b

        result = sample_func(2, 3)

        assert result == 5

    @override_settings(DEBUG=True)
    def test_passes_kwargs_to_function(self) -> None:
        @performance_timer
        def sample_func(a: int, b: int = 10) -> int:
            return a + b

        result = sample_func(5, b=20)

        assert result == 25

    @override_settings(DEBUG=True)
    def test_returns_none_when_function_returns_none(self) -> None:
        @performance_timer
        def sample_func() -> None:
            pass

        result = sample_func()

        assert result is None
