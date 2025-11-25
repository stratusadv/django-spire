from __future__ import annotations

import json

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.template.response import TemplateResponse

from test_project.apps.ordering import models


if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('apps.view_appsordering')
def demo_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'ducks': json.dumps([{
                'name': duck.name,
                'id': duck.id,
                'color': duck.color
            }
            for duck in models.Duck.objects.all().order_by('order')
        ])
    }

    return TemplateResponse(
        request,
        context=context_data,
        template='ordering/page/demo_page.html'
    )
