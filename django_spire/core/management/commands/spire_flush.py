from __future__ import annotations

import contextlib

from importlib import import_module

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.core.management.sql import emit_post_migrate_signal, sql_flush
from django.db import DEFAULT_DB_ALIAS, connections
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    help = (
        "Removes ALL DATA from the database, including data added during "
        'migrations. Does not achieve a "fresh install" state.'
    )

    stealth_options = ("reset_sequences", "inhibit_post_migrate")

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            choices=tuple(connections),
            help='Nominates a database to flush. Defaults to the "default" database.',
        )

    def handle(self, **options) -> None:
        database = options["database"]
        connection = connections[database]
        verbosity = options["verbosity"]
        allow_cascade = True

        # The following are stealth options used by Django's internals.
        reset_sequences = options.get("reset_sequences", True)
        inhibit_post_migrate = options.get("inhibit_post_migrate", False)

        self.style = no_style()

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_config in apps.get_app_configs():
            with contextlib.suppress(ImportError):
                import_module(".management", app_config.name)

        sql_list = sql_flush(
            self.style,
            connection,
            reset_sequences=reset_sequences,
            allow_cascade=allow_cascade,
        )

        try:
            connection.ops.execute_sql_flush(sql_list)
        except Exception as exc:
            db_name = connection.settings_dict['NAME']

            message = (
                f"Database {db_name} couldn't be flushed."
                f" Possible reasons:\n"
                f"  * The database isn't running or isn't"
                f" configured correctly.\n"
                f"  * At least one of the expected database"
                f" tables doesn't exist.\n"
                f"  * The SQL was invalid.\n"
                f"Hint: Look at the output of"
                f" 'django-admin sqlflush'. "
                f"That's the SQL this command wasn't"
                f" able to run."
            )

            raise CommandError(message) from exc

        # Empty sql_list may signify an empty database and post_migrate
        # would then crash.
        if sql_list and not inhibit_post_migrate:
            # Emit the post migrate signal. This allows individual
            # applications to respond as if the database had been migrated
            # from scratch.
            emit_post_migrate_signal(verbosity, False, database)

        db_name = connection.settings_dict['NAME']
        self.stdout.write(f'Database "{db_name}" flushed successfully.')
