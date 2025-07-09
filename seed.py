from django.core.wsgi import get_wsgi_application
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.postgres_settings')
os.environ.setdefault('DANDY_SETTINGS_MODULE', 'test_project.dandy_settings')

application = get_wsgi_application()

from django_spire.auth.user.tests.factories import create_super_user

create_super_user()

print('Seeding Users')
from django_spire.auth.seeding.seed import *

print('Seeding Help Desk Data...')
from test_project.apps.help_desk.seed import *

print('Seeing Query Set Filtering Models')
from test_project.apps.queryset_filtering.seeding.seed import *