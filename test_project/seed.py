import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django_spire.auth.user.tests.factories import create_super_user

create_super_user()

print('Seeding Users')
from django_spire.auth.seeding.seed import *

print('Seeding Help Desk Data...')
from test_project.apps.help_desk.seeding.seed import *

print('Seeding Query Set Filtering Models')
from test_project.apps.queryset_filtering.seeding.seed import *

# print('Seeding Knowledge Data...')
# from django_spire.knowledge.seeding.seed import *

# print('Seeding AI Context Data...')
# from django_spire.ai.context.seeding.seed import *

print('Seeding Infinite Scrolling...')
from test_project.apps.infinite_scrolling.seeding.seed import *
