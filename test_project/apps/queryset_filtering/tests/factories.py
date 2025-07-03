from test_project.apps.queryset_filtering.seeding.seeder import TaskModelSeeder


def create_test_task():
    return TaskModelSeeder.seed_database(1)[0]
