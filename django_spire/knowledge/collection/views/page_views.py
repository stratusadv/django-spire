from django.contrib.auth.decorators import login_required

from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.collection.models import Collection


@login_required()
def list_view(request):
    collections = Collection.objects.all()

    return portal_views.list_view(
        request,
        model=Collection,
        context_data={
            'collections': collections
        },
        template='django_spire/knowledge/collection/page/list_page.html'
    )
