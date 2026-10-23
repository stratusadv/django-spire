from django_spire.metric import Metric


class StoreMetric(Metric):
    domains = [
        Metric.Domain(
            key='store',
            name='Store',
            description='Storefront sales and fulfillment metrics.',
            sub_domain_name='Channels',
            subdomains=[
                Metric.SubDomain(key='web', name='Web', description='Online storefront.'),
                Metric.SubDomain(key='retail', name='Retail', description='Physical stores.'),
            ],
            statistic_groups=[
                Metric.StatisticGroup(
                    key='orders',
                    name='Orders',
                    description='Order lifecycle metrics.',
                    statistics=[
                        Metric.Statistic('created', name='Orders created'),
                        Metric.Statistic('revenue', name='Order revenue', value_type='currency'),
                    ],
                )
            ],
        )
    ]
