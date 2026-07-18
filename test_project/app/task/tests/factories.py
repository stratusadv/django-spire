from __future__ import annotations

from typing import Any, TYPE_CHECKING

from test_project.app.task.seeding.seeder import TaskModelSeeder

if TYPE_CHECKING:
    from test_project.app.task.models import Task


def create_test_task(**kwargs: Any) -> Task:
    seeder = TaskModelSeeder(count=1, verbose=False)
    seeder.seed()

    for field, value in kwargs.items():
        seeder.seeds[0][field] = value

    return seeder.seed_database()[0]
