from __future__ import annotations

from test_project.app.notification.seeding.seeder import NotificationSeeder, AppNotificationSeeder


NotificationSeeder.seed_app_notification(count=10)
AppNotificationSeeder.seed_database(count=10)
