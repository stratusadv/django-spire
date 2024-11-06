from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Remove all migration(s) and delete SQLite database.'

    def handle(self, *_args, **_kwargs) -> None:
        is_migration_removed = self.remove_migration()

        if is_migration_removed:
            message = self.style.SUCCESS('The migration file(s) removed.')
            self.stdout.write(message)
        else:
            message = self.style.SUCCESS('The migration file(s) removed.')
            self.stdout.write(message)

        is_database_removed = self.remove_sqlite_database()

        if is_database_removed:
            message = self.style.SUCCESS('The test database was removed.')
            self.stdout.write(message)
        else:
            message = self.style.SUCCESS('The test database was removed.')
            self.stdout.write(message)

    def remove_migration(self) -> bool:
        found = False

        for app in settings.INSTALLED_APPS:
            path = settings.BASE_DIR / app.replace('.', '/') / 'migrations'

            if path.exists():
                for file in path.glob('*.py'):
                    if file.name == '__init__.py':
                        continue

                    file.unlink()
                    found = True

        return found

    def remove_sqlite_database(self) -> bool:
        path = settings.DATABASES.get('default')

        if not path:
            return False

        name = path.get('NAME')

        if name is None:
            return False

        path = settings.BASE_DIR / name

        if path.exists() and path.is_file():
            path.unlink()
            return True

        return False
