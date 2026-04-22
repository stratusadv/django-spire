from test_project.apps.queryset_filtering.seeding.seeder import TaskModelSeeder, TaskUserModelSeeder

TaskModelSeeder.seed_database(1000)
TaskUserModelSeeder.seed_database(1000)
