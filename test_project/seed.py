import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django_spire.auth.user.tests.factories import create_super_user

create_super_user()

print('Seeding Users')
from django_spire.auth.seeding.seed import * # noqa

print('Seeding Api Data...')
from django_spire.api.seeding.seed import * # noqa

print('Seeding Help Desk Data...')
from test_project.app.help_desk.seeding.seed import * # noqa

print('Seeding Query Set Filtering Models')
from test_project.app.queryset_filtering.seeding.seed import * # noqa

# print('Seeding Knowledge Data...')
# from django_spire.knowledge.seeding.seed import * # noqa

# print('Seeding AI Context Data...')
# from django_spire.ai.context.seeding.seed import * # noqa

print('Seeding Infinite Scrolling...')
from test_project.app.infinite_scrolling.seeding.seed import * # noqa

print('Seeding Lazy Tabs...')
from test_project.app.lazy_tabs.seeding.seed import * # noqa

print('Seeding Comment Examples...')
from test_project.app.comment.seeding.seed import * # noqa

print('Seeding Notification...')
from test_project.app.notification.seeding.seed import * # noqa
