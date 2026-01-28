import calendar
from datetime import datetime, timedelta

from django.utils.timezone import now


class Helper:
    @property
    def thirty_days_ago(self) -> datetime:
        return self.today - timedelta(days=30)

    @property
    def sixty_days_ago(self) -> datetime:
        return self.today - timedelta(days=60)

    @property
    def ninety_days_ago(self) -> datetime:
        return self.today - timedelta(days=90)

    @property
    def today(self) -> datetime:
        return now()

    @property
    def tomorrow(self) -> datetime:
        return self.today + timedelta(days=1)

    @property
    def yesterday(self) -> datetime:
        return self.today - timedelta(days=1)

    @property
    def start_of_current_week(self) -> datetime:
        return self.today - timedelta(days=self.today.weekday())

    @property
    def end_of_current_week(self) -> datetime:
        return self.start_of_week + timedelta(days=6)

    @property
    def start_of_last_week(self) -> datetime:
        return self.start_of_week - timedelta(days=6)

    @property
    def end_of_last_week(self) -> datetime:
        return self.end_of_week - timedelta(days=6)

    @property
    def start_of_current_month(self) -> datetime:
        return self.today.replace(day=1)

    @property
    def end_of_current_month(self) -> datetime:
        _, last_day = calendar.monthrange(self.today.year, self.today.month)
        return self.today.replace(day=last_day)

    @property
    def start_of_last_month(self) -> datetime:
        return self._add_months(self.today, -1).replace(day=1)

    @property
    def end_of_last_month(self) -> datetime:
        last_month = self._add_months(self.today, -1)
        _, last_day = calendar.monthrange(last_month.year, last_month.month)

        return last_month.replace(day=last_day)

    @property
    def start_of_current_year(self) -> datetime:
        return self.today.replace(month=1, day=1)

    @property
    def end_of_current_year(self) -> datetime:
        return self.today.replace(month=12, day=31)

    @property
    def start_of_last_year(self) -> datetime:
        return self.today.replace(year=self.today.year - 1, month=1, day=1)

    @property
    def end_of_last_year(self) -> datetime:
        return self.today.replace(year=self.today.year - 1, month=12, day=31)

    @staticmethod
    def _add_months(datetime_, months):
        month = datetime_.month - 1 + months
        year = datetime_.year + month // 12
        month = month % 12 + 1

        day = min(datetime_.day, calendar.monthrange(year, month)[1])

        return datetime_.replace(year=year, month=month, day=day)