from django.contrib.auth.decorators import login_required

from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.collection.models import Collection


@login_required()
def collection_list_view(request):
    collections = Collection.objects.all()

    return portal_views.list_view(
        request=request,
        context_data={
            'collections': collections
        },
        model=Collection,
        template='django_spire/knowledge/collection/page/collection_list_page.html'
    )