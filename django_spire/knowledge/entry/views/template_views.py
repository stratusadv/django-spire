from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.template.response import TemplateResponse

from django_spire.knowledge.entry.models import Entry


@login_required()
def file_list_view(request: WSGIRequest) -> TemplateResponse:
    return TemplateResponse(
        request,
        context={
            'files_json': Entry.services.tool.get_files_to_convert_json(),
        },
        template='django_spire/knowledge/entry/file/page/list_page.html'
    )
