from test_project.app.celery.seeding.seeder import CeleryStalkSeeder


celery_stalk_seeder = CeleryStalkSeeder()

celery_stalk_seeder.seed_database(count=50)
