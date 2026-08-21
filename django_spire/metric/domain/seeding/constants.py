DOMAIN_SEEDS = [
    {
        'name': 'Sales',
        'description': (
            'The Sales domain tracks revenue generation, deal progression, and account '
            'performance across the organization.'
        ),
        'sub_domain_description': (
            'Sales sub domains cover leads, opportunities, quotes, and revenue reporting.'
        ),
    },
    {
        'name': 'Marketing',
        'description': (
            'The Marketing domain measures campaign effectiveness, brand reach, and demand '
            'generation across channels.'
        ),
        'sub_domain_description': (
            'Marketing sub domains include campaigns, website traffic, social media, and email '
            'engagement.'
        ),
    },
    {
        'name': 'Finance',
        'description': (
            'The Finance domain monitors profitability, cash flow, and budget performance across '
            'the organization.'
        ),
        'sub_domain_description': (
            'Finance sub domains cover revenue, expenses, accounts receivable, and budget variance.'
        ),
    },
    {
        'name': 'Human Resources',
        'description': (
            'The Human Resources domain tracks workforce metrics, hiring, and employee retention.'
        ),
        'sub_domain_description': (
            'Human Resources sub domains include headcount, hiring, attendance, and turnover.'
        ),
    },
    {
        'name': 'Operations',
        'description': (
            'The Operations domain measures production efficiency, quality, and supply chain '
            'performance.'
        ),
        'sub_domain_description': (
            'Operations sub domains cover production, inventory, quality, and logistics.'
        ),
    },
    {
        'name': 'Information Technology',
        'description': (
            'The Information Technology domain monitors infrastructure uptime, service delivery, '
            'and technology spend.'
        ),
        'sub_domain_description': (
            'Information Technology sub domains include infrastructure, applications, support '
            'tickets, and security incidents.'
        ),
    },
    {
        'name': 'Customer Service',
        'description': (
            'The Customer Service domain measures support performance, customer satisfaction, and '
            'resolution efficiency.'
        ),
        'sub_domain_description': (
            'Customer Service sub domains cover tickets, satisfaction, response time, and '
            'escalations.'
        ),
    },
]

GROUP_SEEDS = [
    {
        'name': 'Pipeline Performance',
        'description': 'Tracks lead flow and deal progression across the sales pipeline.',
    },
    {
        'name': 'Website Performance',
        'description': 'Measures visitor engagement and interaction across the website.',
    },
    {
        'name': 'Financial Health',
        'description': 'Monitors revenue, invoicing, and cash performance.',
    },
    {'name': 'Workforce', 'description': 'Tracks headcount, hiring, and team growth.'},
    {
        'name': 'Support Operations',
        'description': 'Measures ticket throughput and operational resolution performance.',
    },
]


STATISTIC_SEEDS = [
    'New Leads',
    'Clicks',
    'Revenue',
    'Headcount',
    'Tickets Resolved',
    'Closed Deals',
    'Page Views',
    'Invoices Paid',
    'New Hires',
    'Production Units',
]


SUB_DOMAIN_KEYS = [
    '11111111-2222-4333-8444-555555555501',
    '11111111-2222-4333-8444-555555555502',
    '11111111-2222-4333-8444-555555555503',
    '11111111-2222-4333-8444-555555555504',
    '11111111-2222-4333-8444-555555555505',
    '11111111-2222-4333-8444-555555555506',
    '11111111-2222-4333-8444-555555555507',
    '11111111-2222-4333-8444-555555555508',
    '11111111-2222-4333-8444-555555555509',
    '11111111-2222-4333-8444-55555555550A',
    '11111111-2222-4333-8444-55555555550B',
    '11111111-2222-4333-8444-55555555550C',
    '11111111-2222-4333-8444-55555555550D',
    '11111111-2222-4333-8444-55555555550E',
    '11111111-2222-4333-8444-55555555550F',
    '11111111-2222-4333-8444-555555555510',
    '11111111-2222-4333-8444-555555555511',
    '11111111-2222-4333-8444-555555555512',
    '11111111-2222-4333-8444-555555555513',
    '11111111-2222-4333-8444-555555555514',
    '11111111-2222-4333-8444-555555555515',
    '11111111-2222-4333-8444-555555555516',
    '11111111-2222-4333-8444-555555555517',
    '11111111-2222-4333-8444-555555555518',
]


STATISTIC_KEYS = [
    '22222222-3333-4444-8555-666666666601',
    '22222222-3333-4444-8555-666666666602',
    '22222222-3333-4444-8555-666666666603',
    '22222222-3333-4444-8555-666666666604',
    '22222222-3333-4444-8555-666666666605',
    '22222222-3333-4444-8555-666666666606',
    '22222222-3333-4444-8555-666666666607',
    '22222222-3333-4444-8555-666666666608',
    '22222222-3333-4444-8555-666666666609',
    '22222222-3333-4444-8555-66666666660A',
]


SUBDOMAIN_SEEDS = [
    {
        'name': 'Leads',
        'description': (
            'Tracks potential customers and their progression through the sales pipeline.'
        ),
    },
    {
        'name': 'Opportunities',
        'description': 'Monitors open deals, win rates, and the value of the sales pipeline.',
    },
    {
        'name': 'Quotes',
        'description': 'Tracks quote creation, approval status, and conversion to closed deals.',
    },
    {
        'name': 'Revenue',
        'description': 'Tracks total income, recurring revenue, and revenue growth over time.',
    },
    {
        'name': 'Campaigns',
        'description': 'Measures marketing campaign reach, engagement, and conversion performance.',
    },
    {
        'name': 'Website Traffic',
        'description': 'Tracks website visits, sessions, and audience engagement.',
    },
    {
        'name': 'Social Media',
        'description': 'Measures social media followers, engagement, and campaign performance.',
    },
    {
        'name': 'Invoices',
        'description': 'Monitors invoice issuance, payment status, and outstanding balances.',
    },
    {
        'name': 'Headcount',
        'description': 'Tracks employee count, hiring, and departures across the organization.',
    },
    {
        'name': 'Attendance',
        'description': 'Monitors employee attendance, absenteeism, and on-time rates.',
    },
    {
        'name': 'Production',
        'description': 'Measures manufacturing output, throughput, and production efficiency.',
    },
    {
        'name': 'Tickets',
        'description': 'Monitors support and service tickets by status, priority, and resolution.',
    },
]
