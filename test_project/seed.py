import os

from django.core.wsgi import get_wsgi_application

from django_spire.contrib.seeding import Seeder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django_spire.auth.user.tests.factories import create_super_user # noqa

create_super_user()

from django_spire.auth.seeding.seed import * # noqa

from django_spire.api.seeding.seed import * # noqa

from test_project.app.celery.seeding.seed import * # noqa

from test_project.app.help_desk.seeding.seed import * # noqa

# print('Seeding Knowledge Data...')
# from django_spire.knowledge.seeding.seed import * # noqa

# print('Seeding AI Context Data...')
# from django_spire.ai.context.seeding.seed import * # noqa

from test_project.app.comment.seeding.seed import * # noqa

from test_project.app.notification.seeding.seed import * # noqa

from test_project.app.task.seeding.seed import * # noqa

from django_spire.metric.domain.seeding.seed import * # noqa

from test_project.app.ordering.seeding.seed import * # noqa

from test_project.app.rest.seeding.seed import * # noqa

Seeder.print_meta_overview()