from __future__ import annotations

from test_project.app.task.seeding.seeder import (
    SubTaskModelSeeder,
    SubSubTaskModelSeeder,
    TaskModelSeeder,
    TaskUserModelSeeder,
)


task_model_seeder = TaskModelSeeder(count=20)

task_model_seeder.seed_database()


sub_task_model_seeder = SubTaskModelSeeder(count=100)

sub_task_model_seeder.seed_database()


sub_sub_task_model_seeder = SubSubTaskModelSeeder(count=100)

sub_sub_task_model_seeder.seed_database()


task_user_model_seeder = TaskUserModelSeeder(count=400)

task_user_model_seeder.seed_database()
