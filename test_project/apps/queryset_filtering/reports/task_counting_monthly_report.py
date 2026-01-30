import random
from datetime import date, datetime
from time import sleep

from django_spire.metric.report import BaseReport

NAMES = ['tom', 'jerry', 'sally', 'bob', 'alice']


class TaskCountingMonthlyReport(BaseReport):
    title: str = 'Task Counting Monthly Report'
    description = 'A broken down list of all the tasks completed monthly by user.'

    @staticmethod
    def person_choices():
        return (
            (i, name) for i, name in enumerate(NAMES)
        )

    def other_people_choices(self):
        return self.person_choices()

    def run(
            self,
            start_date: date = BaseReport.helper.start_of_last_month,
            end_datetime: datetime = BaseReport.helper.end_of_current_year,
            task_limit: int = 100,
            quality_limit: float = 20.0,
            show_puppets: bool = True,
            person: int = 0,
            other_people: list[int] = [0],
    ):
        sleep(1.0) # Simulate loading!

        self.add_column(f'People', sub_title=str(end_datetime))
        self.add_column('Type', type=self.ColumnType.CHOICE)
        self.add_column('Quality', type=self.ColumnType.PERCENT)
        self.add_column('Tasks', type=self.ColumnType.NUMBER)
        self.add_column('Hours', type=self.ColumnType.NUMBER_1)
        self.add_column('Days', type=self.ColumnType.NUMBER_2)
        self.add_column('Weeks', type=self.ColumnType.NUMBER_3)
        self.add_column('Value', type=self.ColumnType.DOLLAR)

        types = ['bug', 'feature', 'enhancement', 'documentation']

        self.add_divider_row('Main Tasks', description=f'This section shows the main task! {person=} and {other_people=}')

        for _ in range(1, 60):
            self.add_row([
                random.choice(NAMES),
                random.choice(types),
                random.randint(0, 100),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(100_000, 1_999_999),
            ], cell_sub_values=[
                start_date,
                None,
                None,
                None,
                None,
                None,
                None,
                'Tacos',
            ])

        self.add_divider_row('Internal Tasks', page_break=True)

        for _ in range(1, 20):
            self.add_row([
                random.choice(NAMES),
                random.choice(types),
                random.randint(0, 100),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(100_000, 1_999_999),
            ],
                border_top=True, border_bottom=True,
            )

        self.add_divider_row('Extra Tasks', page_break=True)

        for _ in range(1, 20):
            self.add_row([
                random.choice(NAMES),
                random.choice(types),
                random.randint(0, 100),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(100_000, 1_999_999),
            ])

        self.add_footer_row([
            'Totals:',
            '-',
            random.randint(30, 60),
            random.randint(30, 70),
            random.randint(30, 70),
            random.randint(30, 70),
            random.randint(30, 70),
            random.randint(5_000_000, 9_999_999),
        ])

        self.add_blank_row()
        self.add_blank_row(text='This some extra information on how tasks are evaluated and make sure to take time to read this and be amazed!!!')
        self.add_blank_row()

