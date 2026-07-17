from __future__ import annotations


from django_spire.auth.seeding.seeder import UserSeeder


user_seeder = UserSeeder(count=20)

user_seeder.seed_database()
