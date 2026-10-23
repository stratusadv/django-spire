from __future__ import annotations

from django.core.management.base import BaseCommand
from django.core.management.base import CommandParser
from django.utils.timezone import now as django_now

from django_spire.celery.models import CelerySchedulerTask, CeleryTaskSweep
from django_spire.celery.scheduler import _load_entries
from django_spire.celery.sweep import _DEFAULT_SWEEP_KEY
from django_spire.conf import settings as spire_settings


class Command(BaseCommand):
    help = (
        'Reports whether the embedded Celery web-process threads are alive, judging each '
        'component by the freshness of its claim row. STALE means the thread has not '
        'claimed recently (dead, or never started). With --fail, exits 1 when anything '
        'is STALE.'
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--max-age',
            type=float,
            default=0,
            help=(
                'Extra staleness grace in seconds, on top of twice the component interval '
                '(or tick) (default: 0).'
            ),
        )
        parser.add_argument(
            '--fail', action='store_true', help='Exit with status 1 when any component is STALE.'
        )

    def handle(self, *args, **options) -> None:  # noqa: ARG002
        max_age = float(options['max_age'])
        stale = self._check_sweep(max_age) or self._check_scheduler(max_age)

        if options['fail'] and stale:
            raise SystemExit(1)

    def _check_sweep(self, max_age: float) -> bool:
        if not spire_settings.DJANGO_SPIRE_CELERY_SWEEP_ENABLED:
            self.stdout.write('sweep: SKIPPED (sweep is not enabled)')
            return False

        interval_seconds = float(spire_settings.DJANGO_SPIRE_CELERY_SWEEP_INTERVAL_SECONDS or 30)
        grace_seconds = max(2 * interval_seconds, max_age)

        row = CeleryTaskSweep.objects.filter(key=_DEFAULT_SWEEP_KEY).first()
        if row is None:
            self.stdout.write('sweep: STALE (no claim row; the sweep thread has never ticked)')
            return True

        age_seconds = (django_now() - row.last_swept_datetime).total_seconds()
        if age_seconds > grace_seconds:
            self.stdout.write(
                f'sweep: STALE (last swept {age_seconds:.0f}s ago, grace {grace_seconds:.0f}s)'
            )
            return True

        self.stdout.write(
            f'sweep: OK (last swept {age_seconds:.0f}s ago, grace {grace_seconds:.0f}s)'
        )
        return False

    def _check_scheduler(self, max_age: float) -> bool:
        if (
            not spire_settings.DJANGO_SPIRE_CELERY_SCHEDULER_ENABLED
            or not spire_settings.DJANGO_SPIRE_CELERY_SCHEDULER_CLASSES
        ):
            self.stdout.write('scheduler: SKIPPED (scheduler is not enabled)')
            return False

        entries = _load_entries()
        if not entries:
            self.stdout.write('scheduler: SKIPPED (no registered scheduler entries)')
            return False

        tick_seconds = float(spire_settings.DJANGO_SPIRE_CELERY_SCHEDULER_TICK_SECONDS or 30)
        grace_seconds = max(2 * tick_seconds, max_age)
        moment = django_now()
        stale = False

        for entry in entries:
            row = CelerySchedulerTask.objects.filter(schedule_key=entry.schedule_key).first()
            if row is None:
                self.stdout.write(f'scheduler: STALE ({entry.schedule_key}: no claim row)')
                stale = True
                continue

            next_slot = row.last_sent_datetime + entry.crontab_schedule.remaining_estimate(
                row.last_sent_datetime
            )
            missed_by = (moment - next_slot).total_seconds()
            if missed_by > grace_seconds:
                self.stdout.write(
                    f'scheduler: STALE ({entry.schedule_key}: slot {next_slot:%Y-%m-%d %H:%M:%S} '
                    f'missed by {missed_by:.0f}s, grace {grace_seconds:.0f}s)'
                )
                stale = True
            else:
                self.stdout.write(
                    f'scheduler: OK ({entry.schedule_key}: next slot {next_slot:%Y-%m-%d %H:%M:%S})'
                )

        return stale
