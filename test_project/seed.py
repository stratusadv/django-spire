import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django_spire.auth.user.tests.factories import create_super_user

create_super_user()

print('Seeding Users')
from django_spire.auth.seeding.seed import *

print('Seeding Api Data...')
from django_spire.api.seeding.seed import *

print('Seeding Celery Stalks...')
from test_project.app.celery.seeding.seed import *

print('Seeding Help Desk Data...')
from test_project.app.help_desk.seeding.seed import *

print('Seeding Query Set Filtering Models')
from test_project.app.task.seeding.seed import *

# print('Seeding Knowledge Data...')
# from django_spire.knowledge.seeding.seed import *

# print('Seeding AI Context Data...')
# from django_spire.ai.context.seeding.seed import *

print('Seeding Comment Examples...')
from test_project.app.comment.seeding.seed import *

print('Seeding Notification...')
from test_project.app.notification.seeding.seed import *

print('Seeding Task...')
from test_project.app.task.seeding.seed import *

print('Seeding Domain & Sub Domain...')
from django_spire.metric.domain.seeding.seed import *

print('Seeding Ordering...')
from test_project.app.ordering.seeding.seed import *
