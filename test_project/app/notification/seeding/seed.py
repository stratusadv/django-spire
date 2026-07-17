from test_project.app.notification.seeding.seeder import NotificationSeeder, AppNotificationSeeder


notification_seeder = NotificationSeeder(count=10)

notification_seeder.seed_database()


app_notification_seeder = AppNotificationSeeder(count=10)

app_notification_seeder.seed_database()
