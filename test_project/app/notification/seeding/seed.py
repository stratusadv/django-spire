from test_project.app.notification.seeding.seeder import AppNotificationSeeder, NotificationSeeder


notification_seeder = NotificationSeeder(count=60)

notification_seeder.seed_database()


app_notification_seeder = AppNotificationSeeder(count=60)

app_notification_seeder.seed_database()
