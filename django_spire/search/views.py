from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.template.response import TemplateResponse

from django_spire.core.redirect.generic_redirect import reverse_generic_relation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def search_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    if 'query' in request.GET:
        search_query = request.GET['query']
        search_item_list = []
        model_info_dict = [
            {
                'app_label': '',
                'model_name': '',
                'query_set': []
            }
        ]

        for model in model_info_dict:
            for item in model['query_set']:
                item_name = item

                if 'model_identifier' in model:
                    model_name = model['model_identifier']
                else:
                    model_name = model['model_name']

                search_item_list.append({
                    'name': item_name,
                    'model_name': model_name,
                    'url': reverse_generic_relation(item)
                })

        context_data['search_query'] = search_query
        context_data['search_item_list'] = search_item_list

    return TemplateResponse(request, 'spire/page/full_search_page.html', context_data)
