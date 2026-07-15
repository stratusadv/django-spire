from test_project.app.task.seeding.seeder import (
    TaskModelSeeder,
    TaskUserModelSeeder,
    SubTaskModelSeeder,
)

TaskModelSeeder.seed_database(200)
SubTaskModelSeeder.seed_database(1000)
TaskUserModelSeeder.seed_database(4000)
