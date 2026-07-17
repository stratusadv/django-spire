from test_project.app.rest.seeding.seeder import PirateModelSeeder


pirate_model_seeder = PirateModelSeeder(count=50)

pirate_model_seeder.seed_database()
