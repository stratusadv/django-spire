import random
from time import sleep

from django_spire.metric.report import BaseReport, helper


class TaskCountingMonthlyReport(BaseReport):
    title: str = 'Task Counting Monthly Report'
    description = 'A broken down list of all the tasks completed monthly by user.'

    def people_choices(self):
        return (
            (1, 'tom'),
            (2, 'jerry'),
            (3, 'sally'),
            (4, 'bob'),
            (5, 'alice'),
        )

    def run(
            self,
            start_date: str = helper.today.date().isoformat(),
            task_limit: int = 100,
            quality_limit: float = 20.0,
            show_puppets: bool = True,
            people: int = 0,
    ):
        sleep(1.0) # Simulate loading!

        self.add_column(f'People', sub_title=start_date)
        self.add_column('Type', type=self.ColumnType.CHOICE)
        self.add_column('Quality', type=self.ColumnType.PERCENT)
        self.add_column('Tasks', type=self.ColumnType.NUMBER)
        self.add_column('Hours', type=self.ColumnType.DECIMAL_1)
        self.add_column('Days', type=self.ColumnType.DECIMAL_2)
        self.add_column('Weeks', type=self.ColumnType.DECIMAL_3)
        self.add_column('Value', type=self.ColumnType.DOLLAR)

        types = ['bug', 'feature', 'enhancement', 'documentation']
        names = ['tom', 'jerry', 'sally', 'bob', 'alice']

        self.add_divider_row('Main Tasks', description='This section shows the main tasks')

        for _ in range(1, 60):
            self.add_row([
                random.choice(names),
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

        self.add_blank_row()
        self.add_divider_row('Internal Tasks', page_break=True)

        for _ in range(1, 20):
            self.add_row([
                random.choice(names),
                random.choice(types),
                random.randint(0, 100),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(100_000, 1_999_999),
            ])

        self.add_blank_row()
        self.add_divider_row('Extra Tasks', page_break=True)

        for _ in range(1, 20):
            self.add_row([
                random.choice(names),
                random.choice(types),
                random.randint(0, 100),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(10, 99),
                random.randint(100_000, 1_999_999),
            ])

        self.add_blank_row()
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

