from test_project.apps.queryset_filtering.models import Task

from django.db.models import Count, F, FloatField, Q, Value
from django.db.models.functions import Cast


def tabular_context_data(page=1, page_size=5, search='', sort_column='name', sort_direction='asc'):
    offset = (page - 1) * page_size

    tasks = Task.objects.select_related()

    if search:
        tasks = tasks.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    tasks = tasks.annotate(
        user_count=Count('user'),
        calculated_cost=Cast(F('id') * Value(100), FloatField()),
        calculated_price=Cast(F('id') * Value(150), FloatField())
    )

    sort_mapping = {
        'name': 'name',
        'status': 'status',
        'quantity': 'user_count',
        'cost': 'calculated_cost',
        'date': 'created_datetime',
    }

    sort_field = sort_mapping.get(sort_column, 'created_datetime')
    order_by = f"{'-' if sort_direction == 'desc' else ''}{sort_field}"

    tasks = tasks.order_by(order_by)

    total_count = tasks.count()
    tasks = tasks[offset:offset + page_size]

    has_next = offset + page_size < total_count

    return {
        'tasks': tasks,
        'has_next': has_next,
        'total_count': total_count,
    }
