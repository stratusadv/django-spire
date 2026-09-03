from decimal import Decimal

# All helper functions need to be loaded as lazily as possible to prevent Django startup errors.

class Spire:
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
