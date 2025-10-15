from django.db.models import Count, Q
from test_project.apps.queryset_filtering.models import Task, TaskUser


def tabular_context_data(page=1, page_size=5, search='', sort_column='name', sort_direction='asc'):
    offset = (page - 1) * page_size

    tasks = Task.objects.select_related()

    if search:
        tasks = tasks.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    tasks = tasks.annotate(user_count=Count('user'))

    sort_mapping = {
        'name': 'name',
        'status': 'status',
        'quantity': 'user_count',
        'cost': 'id',
        'date': 'created_datetime',
    }

    sort_field = sort_mapping.get(sort_column, 'created_datetime')
    order_by = f"{'-' if sort_direction == 'desc' else ''}{sort_field}"

    tasks = tasks.order_by(order_by)

    total_count = tasks.count()
    tasks = tasks[offset:offset + page_size]

    rows = []
    for task in tasks:
        task_users = task.users.select_related('user').all()

        row = {
            'data': {
                'uuid': str(task.id),
                'quantity': task_users.count(),
                'cost': float(task.id * 100),
                'price': float(task.id * 150),
                'date': task.created_datetime.date(),
                'name': task.name,
                'status': task.get_status_display(),
                'description': task.description[:50] + '...' if len(task.description) > 50 else task.description,
            },
            'child_rows': []
        }

        if task_users.exists():
            for task_user in task_users:
                child_row = {
                    'child_data': {
                        'uuid': f"task-{task.id}-user-{task_user.user.id}",
                        'quantity': 1,
                        'cost': float(50 + task.id),
                        'price': float(75 + task.id),
                        'date': task_user.created_datetime.date(),
                        'user_name': task_user.user.get_full_name() or task_user.user.username,
                        'role': task_user.get_role_display(),
                    }
                }
                row['child_rows'].append(child_row)

        rows.append(row)

    has_next = offset + page_size < total_count

    return {
        'rows': rows,
        'has_next': has_next,
        'total_count': total_count,
    }
