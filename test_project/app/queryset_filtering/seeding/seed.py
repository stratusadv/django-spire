from test_project.app.queryset_filtering.seeding.seeder import TaskModelSeeder, TaskUserModelSeeder

TaskModelSeeder.seed_database(1000)
TaskUserModelSeeder.seed_database(1000)
