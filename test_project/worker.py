import os
import robit
from django.core.wsgi import get_wsgi_application


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    'test_project.postgres_settings'
)

os.environ.setdefault(
    "DANDY_SETTINGS_MODULE",
    'test_project.dandy_settings'
)

application = get_wsgi_application()

robit.set_timezone('America/Edmonton')
robit.set_database_logging(True)
robit.set_controls(True)

from django_spire.knowledge.entry.models import Entry
from django_spire.notification import automations as notification_automations


wo = robit.Worker(
    name='Django Spire',
    web_server=True,
    web_server_address=os.getenv('ROBIT_WEB_SERVER_ADDRESS', '127.0.0.1'),
    web_server_port=8080,
    key=os.getenv('ROBIT_WEB_SERVER_KEY', 'dec650f8-919c-4124-9f2f-320f6725c4c3'),
)


wo.add_group('Notifications')

wo.add_job(
    name="Process Ready Notifications",
    method=notification_automations.process_notifications,
    group='Notifications',
    cron='0 0 * * 6'
)

wo.add_group('Knowledge Base')

wo.add_job(
    name="Convert Files to Model Objects",
    method=Entry.services.automation.convert_files_to_model_objects,
    group='Knowledge Base',
    cron='*/5 * * * * *'
)


if __name__ == '__main__':
    wo.start()
