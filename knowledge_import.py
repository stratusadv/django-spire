from django.core.wsgi import get_wsgi_application

get_wsgi_application()

from django_spire.knowledge.entry.models import Entry

Entry.services.automation.convert_files_to_model_objects()