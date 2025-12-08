from __future__ import annotations

from django.db import connection, models


class DummyModel(models.Model):
    name = models.CharField(max_length=255, default='')

    class Meta:
        app_label = 'django_spire_core'
        db_table = 'django_spire_core_dummymodel'

    def __str__(self) -> str:
        return 'dummy'

    @classmethod
    def create_table(cls) -> None:
        with connection.cursor() as cursor:
            query = '''
                CREATE TABLE IF NOT EXISTS django_spire_core_dummymodel (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) DEFAULT ''
                )
            '''

            cursor.execute(query)

    @classmethod
    def drop_table(cls) -> None:
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE IF EXISTS django_spire_core_dummymodel')


class DummyModelMixin:
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        DummyModel.create_table()

    @classmethod
    def tearDownClass(cls) -> None:
        DummyModel.drop_table()
        super().tearDownClass()
