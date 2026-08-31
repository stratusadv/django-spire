VISUAL_SEEDS = [
    {
        'name': 'Site Sessions',
        'description': 'Tracks daily sessions across the site.',
        'kind': 'line',
        'statistic': 'Page Views',
    },
    {
        'name': 'Page Views per Minute',
        'description': 'Monitors real-time page view velocity.',
        'kind': 'gauge',
        'statistic': 'Page Views',
    },
    {
        'name': 'Conversion Rate',
        'description': 'Measures the share of sessions that convert to purchases.',
        'kind': 'gauge',
        'statistic': 'Conversion Rate',
    },
    {
        'name': 'New Customers',
        'description': 'Counts customers acquired per week.',
        'kind': 'bar',
        'statistic': 'New Leads',
    },
    {
        'name': 'Average Order Value',
        'description': 'Tracks the average spend per order over time.',
        'kind': 'line',
        'statistic': 'Revenue',
    },
    {
        'name': 'Cart Abandonment Rate',
        'description': 'Measures started carts that end without a purchase.',
        'kind': 'indicator',
        'statistic': 'Clicks',
    },
    {
        'name': 'Customer Satisfaction Score',
        'description': 'Averages survey scores since the last review cycle.',
        'kind': 'indicator',
        'statistic': 'Tickets Resolved',
    },
    {
        'name': 'Support Ticket Volume',
        'description': 'Splits open support tickets by category.',
        'kind': 'pie',
        'statistic': 'Tickets Resolved',
    },
    {
        'name': 'Revenue by Channel',
        'description': 'Breaks monthly revenue down by sales channel.',
        'kind': 'pie',
        'statistic': 'Revenue',
    },
    {
        'name': 'Gross Margin',
        'description': 'Tracks gross margin as a percentage of revenue.',
        'kind': 'area',
        'statistic': 'Gross Margin',
    },
]

VISUAL_REGION_SEEDS = [
    {
        'key': 'home:dashboard:hero',
        'title': '',
        'visual_name': 'Site Sessions',
        'is_live_updated': False,
    },
    {
        'key': 'home:dashboard:conversion',
        'title': 'Conversion Rate',
        'visual_name': 'Conversion Rate',
        'is_live_updated': True,
    },
]
