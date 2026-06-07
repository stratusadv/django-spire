from test_project.app.task.seeding.seeder import TaskModelSeeder, TaskUserModelSeeder

TaskModelSeeder.seed_database(1000)
TaskUserModelSeeder.seed_database(1000)
