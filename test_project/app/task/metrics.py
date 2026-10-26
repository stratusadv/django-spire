from django_spire.metric.metric import Metric


class TaskMetric(Metric):
    domains = [
        Metric.Domain(
            key='tasks',
            name='Tasks',
            description='Task creation and completion metrics for the task app.',
            sub_domain_name='Sources',
            subdomains=(
                Metric.SubDomain(key='manual', name='Manual', description='Tasks created directly in the UI.'),
                Metric.SubDomain(
                    key='imported', name='Imported', description='Tasks created via the API or bulk import.'
                ),
            ),
            statistic_groups=(
                Metric.StatisticGroup(
                    key='lifecycle',
                    name='Lifecycle',
                    description='Task lifecycle events.',
                    statistics=(
                        Metric.Statistic('created', name='Tasks created'),
                        Metric.Statistic('completed', name='Tasks completed'),
                        Metric.Statistic('cancelled', name='Tasks cancelled'),
                    ),
                ),
                Metric.StatisticGroup(
                    key='throughput',
                    name='Throughput',
                    description='Completion rates and effort estimates.',
                    statistics=(
                        Metric.Statistic('completion-rate', name='Completion rate', value_type='percentage'),
                        Metric.Statistic('estimated-hours', name='Estimated hours', value_type='number'),
                    ),
                ),
            ),
        )
    ]
